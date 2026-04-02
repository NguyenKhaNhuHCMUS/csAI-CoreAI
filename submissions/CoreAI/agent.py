import sys
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


class MyCoreAgent:
    def __init__(self, role):
        self.role = role
        self.last_move = Move.STAY  # hỗ trợ seeker sau này

    def solve(self, map_state, my_pos, enemy_pos):
        """
        Wrapper trung gian. Người viết Seeker/Hider sẽ sửa logic tại đây.
        """

        # Defensive: tránh crash nếu input lỗi
        if map_state is None or my_pos is None:
            return Move.STAY

        neighbors = Utils.get_valid_neighbors(my_pos, map_state)

        if not neighbors:
            return Move.STAY

        # Tạm thời: chọn random để tránh predictable
        import random
        next_pos, move = random.choice(neighbors)

        self.last_move = move

        return move


class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_system = MyCoreAgent(role="seeker")

    def step(self, map_state, my_position, enemy_position, step_number):
        result = self.my_system.solve(map_state, my_position, enemy_position)

        # Cho phép trả (move, steps) hoặc move
        return result


class GhostAgent(BaseGhostAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.my_system = MyCoreAgent(role="hider")

    def step(self, map_state, my_position, enemy_position, step_number):
        return self.my_system.solve(map_state, my_position, enemy_position)