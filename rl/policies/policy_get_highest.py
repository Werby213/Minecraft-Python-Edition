from rl.policies.policy import Policy
import numpy as np
import glm

class PolicyGetHighest(Policy):
    def __init__(self):
        pass
    
    def get_reward(self, agent, world) -> int:
        target_block = glm.vec2(68, 71)
        distance_from_target = glm.distance(glm.vec2(agent.position.x, agent.position.z), target_block)
        return int(agent.position.y * 2) * 5.0 - min(1.0 / distance_from_target, 100.0)
    
    def get_description(self):
        return "Get to the highest point on the map."