from rl.policies.policy import Policy
import numpy as np

class PolicyGetHighest(Policy):
    def __init__(self):
        pass
    
    def get_reward(self, agent, world) -> int:
        return int(agent.position.y * 2)
    
    def get_description(self):
        return "Get to the highest point on the map."