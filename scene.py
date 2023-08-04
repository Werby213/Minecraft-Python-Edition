from settings import *
import moderngl as mgl
from world import World
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds
from agent import Agent
import logging

class Scene:
    def __init__(self, app):
        logging.info("Initializing scene...")
        self.app = app
        logging.info("Initializing world...")
        self.world = World(self.app)
        logging.info("Initializing voxel marker...")
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        logging.info("Initializing water...")
        self.water = Water(app)
        logging.info("Initializing clouds...")
        self.clouds = Clouds(app)
        
        logging.info("Initializing agents...")
        # Agents
        self.agents = []
        for _ in range(1):
            self.agents.append(Agent(self.world.voxel_handler, PLAYER_POS + glm.vec3(0, 500, -10), glm.vec2(0, 0)))

    def update(self, dt):
        self.world.update()

        for agent in self.agents:
            agent.update(dt)

        self.voxel_marker.update()
        self.clouds.update()

    def render(self):
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
        for agent in self.agents:
            agent.render()