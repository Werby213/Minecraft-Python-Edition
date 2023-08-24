from rl.agent import Agent
from settings import *
import moderngl as mgl
import pygame as pg
import sys
from shader_program import ShaderProgram
from environment import Environment
from player import Player
from textures import Textures
import logging
import os

from utils import generate_caption
from terrain_gen.terrain_gen_flat import TerrainGenFlat
from terrain_gen.terrain_gen_perlin import TerrainGenPerlin

class VoxelEngine:
    def initialize_pygame(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, MAJOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, MINOR_VER)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, DEPTH_SIZE)
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, NUM_SAMPLES)

        pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.ctx = mgl.create_context()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0
        self.time = 0

        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

        self.is_running = True

    def on_init_new(self, terrain_gen, filename):
        self.initialize_pygame()
        self.textures = Textures(self)
        self.player = Player(self, glm.vec3(CENTER_XZ, 17, CENTER_XZ), glm.vec2(-90, -45))
        self.shader_program = ShaderProgram(self)
        self.env = Environment(filename)
        self.env.on_init_new(self, terrain_gen)
    
    def on_init_load(self, voxels, player, filename, spawn_agents=False):
        self.initialize_pygame()
        self.textures = Textures(self)
        self.player = Player(self, glm.vec3(player[:3]), player[3:])
        self.shader_program = ShaderProgram(self)
        self.env = Environment(filename)

        self.env.on_init_load(self, voxels, spawn_agents)

    def update(self):
        self.player.update()
        self.shader_program.update()

        self.delta_time = self.clock.tick()
        self.env.update(self.delta_time)

        self.time = pg.time.get_ticks() * 0.001
        pg.display.set_caption(generate_caption(self.clock, self.player, self.env))

    def render(self):
        self.ctx.clear(color=BG_COLOR)
        self.env.render()
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.is_running = False
            self.player.handle_event(event=event)

    def run(self):
        first_freeze = False # TODO remove this
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
            if self.env.agent_handler.frozen and not first_freeze:
                self.env.agent_handler.unfreeze()
                first_freeze = True
        pg.quit()
        sys.exit()

    def save_env(self):
        # create the folder "saves" if it doesn't exist
        if not os.path.exists("saves"):
            os.makedirs("saves")
        # create the folder "envs" if it doesn't exist
        path_0 = os.path.join("saves", self.env.filename)
        if not os.path.exists(path_0):
            os.makedirs(path_0)
        path = os.path.join(path_0, "voxels.npy")
        np.save(path, app.env.world.voxels)
        path = os.path.join(path_0, "player.npy")
        np.save(path, [app.player.position.x, app.player.position.y, app.player.position.z, app.player.yaw, app.player.pitch])

    def load_env(self, file_name):
        # load the environment voxels from a file
        # create the folder "saves" if it doesn't exist
        if not os.path.exists("saves"):
            os.makedirs("saves")
        path = os.path.join("saves", file_name, "voxels.npy")
        voxels = np.load(path)
        path = os.path.join("saves", file_name, "player.npy")
        player = np.load(path)
        return voxels, player

def display_menu(title, options, default=1):
    def get_user_choice(min_c, max_c):
        while True:
            choice = input(f"Enter your choice ({min_c}-{max_c}): ")
            if choice.isdigit() and min_c <= int(choice) <= max_c:
                return int(choice)
            elif choice == "":
                return default
            else:
                print(f"Invalid choice. Please enter a number between {min_c} and {max_c}")

    print("\n" + "=" * 20)
    print(f"{title}:")
    for i in range(len(options)):
        print(f"{i+1}. {options[i]}{' - default' * (default == i + 1)}")
    return get_user_choice(1, len(options))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = VoxelEngine()
    mode = display_menu("Select mode", ["Environement Editing", "Agent Training", "Trained Agent Viewing"])
    
    if not os.path.exists("saves"):
        os.makedirs("saves")
    saved_worlds = [f for f in os.listdir("saves") if os.path.isdir(os.path.join("saves", f))]
    
    if mode == 1:
        generate_or_load = display_menu("New or load env", ["New", "Load"])
        if generate_or_load == 1:
            env_size = display_menu("Select env size", ["Small", "Medium", "Large"])
            env_type = display_menu("Select env type", ["Flat", "Perlin Noise"])
            spawn_trees = 2 - display_menu("Spawn trees?", ["Yes", "No"])
            spawn_caves = 2 - display_menu("Spawn caves?", ["Yes", "No"])

            generator = None
            if env_type == 1:
                ground_type = display_menu("Select ground type", ["Sand", "Grass", "Dirt", "Stone", "Snow", "Leaves", "Wood"])
                generator = TerrainGenFlat(env_size, spawn_trees, spawn_caves, ground_type)
            elif env_type == 2:
                generator = TerrainGenPerlin(env_size, spawn_trees, spawn_caves)
            app.on_init_new(generator, input("Enter the name of the environement: "))
        elif generate_or_load == 2:
            selected_world = display_menu("Select environement", saved_worlds)
            loaded_world_name = saved_worlds[selected_world - 1]
            voxels, player = app.load_env(loaded_world_name)
            app.on_init_load(voxels, player, loaded_world_name)
    elif mode == 2:
        selected_world = display_menu("Select environement", saved_worlds)
        loaded_world_name = saved_worlds[selected_world - 1]
        voxels, player = app.load_env(loaded_world_name)

        app.on_init_load(voxels, player, loaded_world_name, True)
    elif mode == 3:
        selected_world = display_menu("Select environement", saved_worlds)
        pass

    app.run()