import sys
import heapq
import random
from pathlib import Path

# Xác định đường dẫn tới thư mục 'src'
# Cấu trúc: submissions/CoreAI/agent.py -> tiến lên 3 cấp để ra thư mục gốc -> vào src
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from environment import Move
from agent_interface import PacmanAgent as BasePacmanAgent
from agent_interface import GhostAgent as BaseGhostAgent
import numpy as np

class Utils:
    @staticmethod
    def get_valid_neighbors(pos, map_state):
        """
        Trả về danh sách các (tọa độ, Move) hợp lệ (ô = 0).
        """
        neighbors = []

        directions = {
            Move.UP: (-1, 0),
            Move.DOWN: (1, 0),
            Move.LEFT: (0, -1),
            Move.RIGHT: (0, 1)
        }

        h, w = map_state.shape

        for move, (dr, dc) in directions.items():
            nr, nc = pos[0] + dr, pos[1] + dc

            # Check boundary + traversable
            if 0 <= nr < h and 0 <= nc < w and map_state[nr, nc] == 0:
                neighbors.append(((nr, nc), move))

        return neighbors

    @staticmethod
    def manhattan_dist(p1, p2):
        """Khoảng cách Manhattan."""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    @staticmethod
    def translate_pos_to_move(current_pos, next_pos):
        """Convert position delta -> Move."""
        dr = next_pos[0] - current_pos[0]
        dc = next_pos[1] - current_pos[1]

        if dr == -1 and dc == 0:
            return Move.UP
        elif dr == 1 and dc == 0:
            return Move.DOWN
        elif dr == 0 and dc == -1:
            return Move.LEFT
        elif dr == 0 and dc == 1:
            return Move.RIGHT
        else:
            # Không phải neighbor hợp lệ → báo lỗi sớm
            raise ValueError(f"Invalid move from {current_pos} to {next_pos}")

    @staticmethod
    def is_same_direction(move1, move2):
        """
        Kiểm tra 2 move có cùng hướng (dùng cho seeker speed=2).
        """
        if move1 == Move.STAY or move2 == Move.STAY:
            return False
        return move1 == move2

class Seeker:
    def a_star(self, start, target, map_state):
        """Thuật toán A* tìm đường ngắn nhất."""
        frontier = []
        heapq.heappush(frontier, (0, start, []))
        visited = {start: 0}

        while frontier:
            _, current, path = heapq.heappop(frontier)
            if current == target:
                return path

            for neighbor, move in Utils.get_valid_neighbors(current, map_state):
                new_cost = len(path) + 1
                if neighbor not in visited or new_cost < visited[neighbor]:
                    visited[neighbor] = new_cost
                    priority = new_cost + Utils.manhattan_dist(neighbor, target)
                    heapq.heappush(frontier, (priority, neighbor, path + [move]))
        return []

    def compute_seeker_move(self, path, pacman_speed):
        """Quyết định đi 1 hay 2 bước dựa trên đường đi thẳng."""
        if not path:
            return Move.STAY, 1

        first_move = path[0]
        if len(path) >= 2 and pacman_speed >= 2:
            if path[1] == first_move: # Đi thẳng 2 ô [cite: 68]
                return first_move, 2

        return first_move, 1

"""
Hider (Ghost) Agent 
"""

from collections import deque
from environment import Move
import numpy as np


class Hider:
    """
    Ghost (Hider) Agent - Trốn càng lâu càng tốt
    Strategy: Di chuyển đến ô xa nhất so với Seek agent
    """
    
    def __init__(self):
        self.dead_ends = set()      # Lưu các ô ngõ cụt
        self.map_analyzed = False   # Đã phân tích map chưa
    
    def bfs_from_seeker(self, my_pos, enemy_pos, map_state):
        """
        Chạy BFS từ vị trí của Seeker (enemy_pos) để tính khoảng cách
        đến tất cả các ô có thể đi được.
        
        Args:
            my_pos: Vị trí hiện tại của Hider (không dùng trực tiếp ở đây)
            enemy_pos: Vị trí của Seeker (Pacman)
            map_state: Bản đồ 21x21
            
        Returns:
            dict: {position: distance_from_seeker}
        """
        if enemy_pos is None:
            return {}
        
        height, width = map_state.shape
        distances = {}
        queue = deque()
        
        # Bắt đầu từ vị trí của Seeker
        queue.append((enemy_pos[0], enemy_pos[1], 0))
        visited = set()
        visited.add(enemy_pos)
        
        while queue:
            row, col, dist = queue.popleft()
            distances[(row, col)] = dist
            
            # Thử 4 hướng
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                new_pos = (nr, nc)
                
                # Kiểm tra trong bounds và không phải tường
                if 0 <= nr < height and 0 <= nc < width:
                    if map_state[nr, nc] == 0 and new_pos not in visited:
                        visited.add(new_pos)
                        queue.append((nr, nc, dist + 1))
        
        return distances
    
    def identify_dead_ends(self, map_state):
        """
        Xác định các ô ngõ cụt (chỉ có 1 lối ra).
        Nên gọi 1 lần duy nhất khi khởi tạo.
        
        Returns:
            set: Các ô là ngõ cụt
        """
        height, width = map_state.shape
        dead_ends = set()
        
        for i in range(height):
            for j in range(width):
                if map_state[i, j] == 0:  # Ô có thể đi được
                    # Đếm số lượng ô lân cận có thể đi
                    neighbor_count = 0
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ni, nj = i + dr, j + dc
                        if 0 <= ni < height and 0 <= nj < width:
                            if map_state[ni, nj] == 0:
                                neighbor_count += 1
                    
                    # Ngõ cụt: chỉ có 1 lối ra (hoặc 0 nếu bị kẹt)
                    if neighbor_count <= 1:
                        dead_ends.add((i, j))
        
        return dead_ends
    
    def evaluate_safety(self, pos, enemy_pos, distances_from_seeker):
        """
        Đánh giá độ an toàn của một ô.
        Càng xa Seeker càng tốt, và không phải ngõ cụt.
        
        Args:
            pos: Ô cần đánh giá
            enemy_pos: Vị trí Seeker (có thể None)
            distances_from_seeker: Kết quả từ bfs_from_seeker()
            
        Returns:
            float: Điểm an toàn (càng cao càng an toàn)
        """
        if enemy_pos is None:
            # Không biết Seeker ở đâu → ưu tiên ô có nhiều lối thoát
            if pos in self.dead_ends:
                return -100  # Tránh ngõ cụt
            return 0  # Trung tính
        
        # Yếu tố 1: Khoảng cách đến Seeker (càng xa càng tốt)
        distance = distances_from_seeker.get(pos, 0)
        distance_score = distance
        
        # Yếu tố 2: Tránh ngõ cụt
        dead_end_penalty = -100 if pos in self.dead_ends else 0
        
        return distance_score + dead_end_penalty
    
    def get_hider_action(self, map_state, my_position, enemy_position, step_number):
        """
        Hàm chính của Hider: quyết định nước đi.
        
        Args:
            map_state: Bản đồ 21x21 (0=đường, 1=tường, -1=chưa thấy)
            my_position: Vị trí hiện tại của Hider
            enemy_position: Vị trí của Seeker (hoặc None nếu không thấy)
            step_number: Số bước hiện tại
            
        Returns:
            Move: UP/DOWN/LEFT/RIGHT/STAY
        """
        # Phân tích map 1 lần duy nhất
        if not self.map_analyzed:
            self.dead_ends = self.identify_dead_ends(map_state)
            self.map_analyzed = True
        
        # BFS từ vị trí Seeker để tính khoảng cách
        distances = self.bfs_from_seeker(my_position, enemy_position, map_state)
        
        # Tìm các ô lân cận hợp lệ
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row = my_position[0] + dr
            new_col = my_position[1] + dc
            new_pos = (new_row, new_col)
            
            if 0 <= new_row < 21 and 0 <= new_col < 21:
                if map_state[new_row, new_col] == 0:
                    neighbors.append((new_pos, dr, dc))
        
        # Nếu không có ô nào để đi, đứng yên
        if not neighbors:
            return Move.STAY
        
        # Đánh giá từng ô lân cận và chọn ô an toàn nhất
        best_score = -float('inf')
        best_move = Move.STAY
        
        for new_pos, dr, dc in neighbors:
            score = self.evaluate_safety(new_pos, enemy_position, distances)
            if score > best_score:
                best_score = score
                # Chuyển delta thành Move
                if dr == -1 and dc == 0:
                    best_move = Move.UP
                elif dr == 1 and dc == 0:
                    best_move = Move.DOWN
                elif dr == 0 and dc == -1:
                    best_move = Move.LEFT
                elif dr == 0 and dc == 1:
                    best_move = Move.RIGHT
        
        return best_move
    
class MyCoreAgent:
    def __init__(self, role, pacman_speed=1): 
        self.role = role
        self.pacman_speed = pacman_speed 
        self.seeker_logic = Seeker()
        self.last_known_enemy_pos = None
        self.hider_logic = Hider()

    def solve(self, map_state, my_pos, enemy_pos, step_number):
        """
        Wrapper trung gian. Người viết Seeker/Hider sẽ sửa logic tại đây.
        """

        # Defensive: tránh crash nếu input lỗi
        if map_state is None or my_pos is None:
            return Move.STAY, 1

        if self.role == "seeker":
            # 1. Cập nhật bộ nhớ vị trí
            if enemy_pos is not None:
                self.last_known_enemy_pos = enemy_pos

            target = enemy_pos or self.last_known_enemy_pos

            # 2. Chạy logic A*
            if target:
                path = self.seeker_logic.a_star(my_pos, target, map_state)
                return self.seeker_logic.compute_seeker_move(path, self.pacman_speed)

            # 3. Nếu hoàn toàn không thấy đối phương, đi random (tạm thời)
            neighbors = Utils.get_valid_neighbors(my_pos, map_state)
            return (random.choice(neighbors)[1], 1) if neighbors else (Move.STAY, 1)

        else: # Vai trò Hider (Giữ nguyên logic random của thành viên kia)
            return self.hider_logic.get_hider_action(map_state, my_pos, enemy_pos, step_number)


class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        speed = kwargs.get("pacman_speed", 1)
        self.my_system = MyCoreAgent(role="seeker", pacman_speed=speed)

    def step(self, map_state, my_position, enemy_position, step_number):
        result = self.my_system.solve(map_state, my_position, enemy_position, step_number)

        # Cho phép trả (move, steps) hoặc move
        return result


class GhostAgent(BaseGhostAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_system = MyCoreAgent(role="hider")

    def step(self, map_state, my_position, enemy_position, step_number):
        return self.my_system.solve(map_state, my_position, enemy_position, step_number)
    