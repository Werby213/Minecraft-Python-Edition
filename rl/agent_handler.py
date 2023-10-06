from rl.agent import Agent
import logging
import matplotlib.pyplot as plt

class AgentHandler:
    def __init__(self, voxel_handler, policy, start_position, start_rotation):
        self.app = voxel_handler.app
        self.handler = voxel_handler
        self.policy = policy
        self.start_position = start_position
        self.start_rotation = start_rotation
        self.agents = []
        self.frozen = False
        self.step_cooldown = 5.0
        self.step_count = 0
        self.agent_count = 1
        self.history = []

    def update(self, dt):
        if self.frozen:
            return
        
        self.step_cooldown -= dt
        if self.step_cooldown <= 0:
            if self.step_count > 0:
                self.register_step()
            self.step_training()
            self.step_cooldown = 5.0
            self.step_count += 1

        for agent in self.agents:
            agent.update(dt)

    def render(self):
        for agent in self.agents:
            agent.render()

    def spawn_agents(self, count, position, rotation):
        # maybe spawn them at random places or on a specific block
        for _ in range(count):
            self.agents.append(Agent(self.handler, self.policy, position, rotation))

    def freeze(self):
        self.frozen = True
    
    def unfreeze(self):
        self.frozen = False

    def register_step(self):
        max_agent = max(self.agents, key=lambda agent: agent.reward)
        self.history.append((max_agent))
    
    def kill_all_agents(self):
        self.agents.clear()
    
    def start_training(self):
        logging.info("Start training")
        self.freeze()
        self.kill_all_agents()
        self.spawn_agents(self.agent_count, self.start_position, self.start_rotation)
    
    def step_training(self):
        weights = None
        if len(self.history) == 0:
            logging.info(f"Step training {self.step_count}")
        else:
            logging.info(f"Step training {self.step_count} (max reward: {self.history[-1].reward})")
            current_max_agent = max(self.agents, key=lambda agent: agent.reward)
            best_agent_yet = max(self.history, key=lambda agent: agent.reward)
            if current_max_agent.reward < best_agent_yet.reward:
                logging.info(f"Reverting to best agent yet: {best_agent_yet.reward} from step {self.history.index(best_agent_yet)}")
                weights = best_agent_yet.processor.get_weights()
            else:
                weights = current_max_agent.processor.get_weights()
        self.freeze()
        self.kill_all_agents()
        self.spawn_agents(self.agent_count, self.start_position, self.start_rotation)
        if weights:
            for agent in self.agents:
                agent.processor.set_weights(weights)
                agent.processor.mutate()
        self.unfreeze()
    
    def plot_history(self):
        plt.plot([agent.reward for agent in self.history])
        plt.show()
    
    def save_best_model(self, ):
        best_agent = max(self.history, key=lambda agent: agent.reward)
        model = best_agent.processor.model
        model.save("rl/best_model.h5")