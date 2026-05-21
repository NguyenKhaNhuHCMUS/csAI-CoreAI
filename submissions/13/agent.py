import sys
import os
import numpy as np
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(parent_dir, 'src')
sys.path.append(parent_dir)
sys.path.append(src_dir)

try:
    from agent_interface import PacmanAgent as PacmanBase, GhostAgent as GhostBase, Move
except ImportError:
    from src.agent_interface import PacmanAgent as PacmanBase, GhostAgent as GhostBase, Move


class Utils:
    MAP_SIZE = 21
    VISION_RANGE = 5

    # Định nghĩa các hướng di chuyển để dễ quản lý
    DIRECTIONS = [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]

    @staticmethod
    def is_within_bounds(pos):
        """Kiểm tra vị trí có nằm trong bản đồ không"""
        x, y = pos
        return 0 <= x < Utils.MAP_SIZE and 0 <= y < Utils.MAP_SIZE

    @staticmethod
    def manhattan_dist(p1, p2):
        """Tính khoảng cách Manhattan giữa 2 điểm"""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    @staticmethod
    def apply_move(pos, move, steps=1):
        """Tính vị trí mới sau khi đi theo một hướng với số bước nhất định"""
        x, y = pos
        if move == Move.UP:
            return (x, y - steps)
        elif move == Move.DOWN:
            return (x, y + steps)
        elif move == Move.LEFT:
            return (x - steps, y)
        elif move == Move.RIGHT:
            return (x + steps, y)
        return (x, y)  # Trường hợp STAY hoặc không xác định

    @staticmethod
    def translate_pos_to_move(current_pos, next_pos):
        """Chuyển tọa độ ô kế tiếp thành hướng di chuyển (Move Enum)"""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]

        if dx > 0: return Move.RIGHT
        if dx < 0: return Move.LEFT
        if dy > 0: return Move.DOWN
        if dy < 0: return Move.UP
        return Move.STAY

    @staticmethod
    def is_walkable(pos, map_state, allow_unknown=False):
        """Kiểm tra một ô có thể đi vào được không (không phải tường)"""
        if not Utils.is_within_bounds(pos):
            return False

        x, y = pos
        cell_value = map_state[y][x]

        if cell_value == 1:  # Là tường
            return False
        if cell_value == -1:  # Vùng chưa biết
            return allow_unknown
        return True  # cell_value == 0 (đường trống đã thấy)

    @staticmethod
    def get_valid_neighbors(pos, map_state):
        """Lấy danh sách các vị trí lân cận có thể đi được (4 hướng)"""
        neighbors = []
        for move in Utils.DIRECTIONS:
            next_p = Utils.apply_move(pos, move)
            if Utils.is_walkable(next_p, map_state):
                neighbors.append(next_p)
        return neighbors

    @staticmethod
    def is_straight_path_clear(start_pos, move, steps, map_state):
        """Kiểm tra đường đi thẳng (1 hoặc 2 ô) có bị chặn bởi tường không"""
        for s in range(1, steps + 1):
            check_pos = Utils.apply_move(start_pos, move, s)
            if not Utils.is_walkable(check_pos, map_state):
                return False
        return True

    @staticmethod
    def is_same_direction(move1, move2):
        """Kiểm tra hai hướng di chuyển có cùng hướng không"""
        return move1 == move2

    @staticmethod
    def get_escape_count(pos, map_state):
        """Đếm số lối thoát (ô có thể đi) xung quanh một ô"""
        return len(Utils.get_valid_neighbors(pos, map_state))


class PacmanAgent(PacmanBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def step(self, map_state, my_position, enemy_position, step_number):
        """
            ...
        """


class GhostAgent(GhostBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def step(self, map_state, my_position, enemy_position, step_number):
        """
            ...
        """
