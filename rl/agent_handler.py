from rl.agent import Agent

class AgentHandler:
    def __init__(self, voxel_handler):
        self.app = voxel_handler.app
        self.handler = voxel_handler
        self.agents = []

    def update(self, dt):
        for agent in self.agents:
            agent.update(dt)

    def render(self):
        for agent in self.agents:
            agent.render()

    def spawn_agents(self, count, position, rotation):
        for _ in range(count):
            self.agents.append(Agent(self.handler, position, rotation))
    
    def kill_all_agents(self):
        self.agents.clear()