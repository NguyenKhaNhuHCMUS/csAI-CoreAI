"""
A simple working agent for testing
"""
import sys
import time
from pathlib import Path

src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent_interface import PacmanAgent as BasePacmanAgent, GhostAgent as BaseGhostAgent, Move
import random


class PacmanAgent(BasePacmanAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def step(self, observation, my_position, enemy_position, current_step):
        return random.choice([Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT])


class GhostAgent(BaseGhostAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def step(self, observation, my_position, enemy_position, current_step):
        return random.choice([Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT])
