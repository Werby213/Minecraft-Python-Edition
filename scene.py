from settings import *
import moderngl as mgl
from world import World
from world_objects.voxel_marker import VoxelMarker
from world_objects.water import Water
from world_objects.clouds import Clouds
from agent import Agent


class Scene:
    def __init__(self, app):
        self.app = app
        self.world = World(self.app)
        self.voxel_marker = VoxelMarker(self.world.voxel_handler)
        self.water = Water(app)
        self.clouds = Clouds(app)
        
        # Agents
        self.agents = []
        for _ in range(1):
            self.agents.append(Agent(self.world.voxel_handler, PLAYER_POS + glm.vec3(0, 50, -10), glm.vec2(0, 0)))

    def update(self, dt):
        self.world.update()

        for agent in self.agents:
            agent.update(dt)

        self.voxel_marker.update()
        self.clouds.update()

    def render(self):
        # chunks rendering
        self.world.render()

        # agents rendering
        for agent in self.agents:
            agent.render()

        # rendering without cull face
        self.app.ctx.disable(mgl.CULL_FACE)
        self.clouds.render()
        self.water.render()
        self.app.ctx.enable(mgl.CULL_FACE)

        # voxel selection
        self.voxel_marker.render()
