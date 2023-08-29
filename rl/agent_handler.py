from rl.agent import Agent

class AgentHandler:
    def __init__(self, voxel_handler):
        self.app = voxel_handler.app
        self.handler = voxel_handler
        self.agents = []
        self.frozen = False

    def update(self, dt):
        if self.frozen:
            return
        for agent in self.agents:
            agent.update(dt)
            # set camera to agent
            self.app.set_camera(agent.camera)
            self.app.get_stream()

    def render(self):
        for agent in self.agents:
            agent.render()

    def spawn_agents(self, count, position, rotation):
        for _ in range(count):
            self.agents.append(Agent(self.handler, position, rotation))

    def freeze(self):
        self.frozen = True
    
    def unfreeze(self):
        self.frozen = False
    
    def kill_all_agents(self):
        self.agents.clear()