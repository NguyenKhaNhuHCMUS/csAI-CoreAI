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

class MyCoreAgent:
    def __init__(self, role, pacman_speed=1): 
        self.role = role
        self.pacman_speed = pacman_speed 
        self.seeker_logic = Seeker()
        self.last_known_enemy_pos = None

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
            neighbors = Utils.get_valid_neighbors(my_pos, map_state)
            if not neighbors: return Move.STAY
            _, move = random.choice(neighbors)
            return move


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
    