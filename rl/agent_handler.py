from rl.agent import Agent

class AgentHandler:
    def __init__(self, voxel_handler, policy):
        self.app = voxel_handler.app
        self.handler = voxel_handler
        self.policy = policy
        self.agents = []
        self.frozen = False

    def update(self, dt):
        if self.frozen:
            return
        for agent in self.agents:
            agent.update(dt)

    def render(self):
        for agent in self.agents:
            agent.render()

    def spawn_agents(self, count, position, rotation):
        for _ in range(count):
            self.agents.append(Agent(self.handler, self.policy, position, rotation))

    def freeze(self):
        self.frozen = True
    
    def unfreeze(self):
        self.frozen = False
    
    def kill_all_agents(self):
        self.agents.clear()
    
    def start_training(self):
        self.freeze()
        self.kill_all_agents()
        self.spawn_agents(1, (0, 0, 0), (0, 0))
    
    def step_training(self):
        self.freeze()
        weights = self.agents[0].processor.mutate()
        self.kill_all_agents()

        self.spawn_agents(1, (0, 0, 0), (0, 0))
        self.agents[0].processor.set_weights(weights)