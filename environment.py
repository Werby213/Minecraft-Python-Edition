from settings import *
import moderngl as mgl
from world import World
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds

from rl.agent_handler import AgentHandler
from rl.agent import Agent

import logging

class Environment:
    def __init__(self, filename):
        self.filename = filename

    def on_init_new(self, app, terrain_gen):
        logging.info("Initializing scene...")
        self.app = app
        logging.info("Initializing world...")
        self.world = World()
        self.world.on_init_new(self.app, terrain_gen)
        self.on_init(app)
    
    def on_init_load(self, app, voxels, spawn_agents=False, policy=None):
        logging.info("Initializing scene...")
        self.app = app
        logging.info("Initializing world...")
        self.world = World()
        self.world.on_init_load(self.app, voxels)
        self.on_init(app, spawn_agents, policy)

    def on_init(self, app, spawn_agents=False, policy=None):
        logging.info("Initializing voxel marker...")
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        logging.info("Initializing water...")
        self.water = Water(app)
        logging.info("Initializing clouds...")
        self.clouds = Clouds(app)
        self.spawn_agents = spawn_agents
        
        if spawn_agents:
            logging.info("Initializing agents...")
            # Agents
            # find the agent spawn block in the world
            agent_spawn_block = None
            agent_spawn_block_pos = glm.vec3(CENTER_XZ, 15, CENTER_XZ) # TODO find a better way to do this
            agent_spawn_rotation = glm.vec2(90, 0)
            self.agent_handler = AgentHandler(self.world.voxel_handler, policy, agent_spawn_block_pos, agent_spawn_rotation)
            self.agent_handler.start_training()

    def update(self, dt):
        self.world.update()
        self.voxel_marker.update()
        self.clouds.update()
        if self.spawn_agents:
            self.agent_handler.update(dt)

    def render(self, renderAgents):
        # chunks rendering
        self.world.render()

        # rendering without cull face
        self.app.ctx.disable(mgl.CULL_FACE)
        self.clouds.render()
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        # voxel selection
        self.voxel_marker.render()

        # agents rendering
        if self.spawn_agents or renderAgents:
            self.agent_handler.render()