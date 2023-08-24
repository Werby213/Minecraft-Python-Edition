from camera import Camera
from settings import *

class AgentCamera(Camera):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.update()
    
    def update(self):
        self.position = self.agent.position + glm.vec3(0, AGENT_HEIGHT * 0.8, 0)
        self.yaw = self.agent.rotation.x
        self.pitch = self.agent.rotation.y
        super().update()