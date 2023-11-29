from camera import Camera
from settings import *

class AgentCamera(Camera):
    def __init__(self, agent):
        super().__init__(glm.vec3(0), glm.vec2(0))
        self.agent = agent
        self.update()
    
    def get_coordinates(self):
        return self.agent.position + glm.vec3(0, AGENT_HEIGHT * 0.8, 0), self.agent.rotation.x + 90, self.agent.rotation.y
    
    def update(self):
        delta_time = None
        is_moving = None
        on_ground = None
        velocity = None

        self.position, self.yaw, self.pitch = self.get_coordinates()
        self.yaw = glm.radians(self.yaw)
        self.pitch = glm.radians(self.pitch)

        super().update(delta_time, is_moving, on_ground, velocity)