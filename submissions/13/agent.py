import sys
import os
import numpy as np
import random

# Thiết lập đường dẫn để đảm bảo import được AgentInterface
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
    """
    CLASS UTILS - Bộ công cụ hỗ trợ tính toán tọa độ, tầm nhìn và khoảng cách.
    Được thiết kế để dùng chung cho cả Pacman và Ghost.
    """
    MAP_SIZE = 21
    VISION_RANGE = 5

    @staticmethod
    def is_within_bounds(pos):
        """Kiểm tra tọa độ (x, y) có nằm trong map 21x21 không."""
        x, y = pos
        return 0 <= x < Utils.MAP_SIZE and 0 <= y < Utils.MAP_SIZE

    @staticmethod
    def get_manhattan_dist(p1, p2):
        """Tính khoảng cách Manhattan giữa 2 điểm (x, y)."""
        if p1 is None or p2 is None: return float('inf')
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    @staticmethod
    def get_next_pos(pos, action, steps=1):
        """Tính tọa độ tiếp theo dựa trên hướng Move và số bước."""
        x, y = pos
        if action == Move.UP: return (x, y - 1 * steps)
        if action == Move.DOWN: return (x, y + 1 * steps)
        if action == Move.LEFT: return (x - 1 * steps, y)
        if action == Move.RIGHT: return (x + 1 * steps, y)
        return (x, y) # STAY

    @staticmethod
    def is_wall(pos, map_state):
        """Kiểm tra vị trí (x, y) có phải là tường (1) không."""
        x, y = pos
        if not Utils.is_within_bounds(pos): return True
        return map_state[y][x] == 1

    @staticmethod
    def get_vision_ray(pos, move, map_state):
        """
        Dự đoán tầm nhìn theo 1 hướng nhất định.
        Trả về danh sách các ô nhìn thấy được (tối đa 5 ô).
        Dừng lại khi gặp tường.
        """
        visible_coords = []
        for i in range(1, Utils.VISION_RANGE + 1):
            next_p = Utils.get_next_pos(pos, move, i)
            if not Utils.is_within_bounds(next_p): break
            visible_coords.append(next_p)
            if Utils.is_wall(next_p, map_state): break
        return visible_coords


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