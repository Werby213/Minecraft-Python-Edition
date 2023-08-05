from settings import *
import moderngl as mgl
import pygame as pg
import sys
from shader_program import ShaderProgram
from environment import Environment
from player import Player
from textures import Textures
import logging

from utils import generate_caption

class VoxelEngine:
    def __init__(self):
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

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)

        self.is_running = True
        self.on_init()

    def on_init(self):
        self.textures = Textures(self)
        self.player = Player(self)
        self.shader_program = ShaderProgram(self)
        self.env = Environment(self)

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
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()
        pg.quit()
        sys.exit()

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

    mode = display_menu("Select mode", ["Environement Editing", "Agent Training", "Trained Agent Viewing"])
    if mode == 1:
        generate_or_load = display_menu("New or load env", ["New", "Load"])
        if generate_or_load == 1:
            env_size = display_menu("Select env size", ["Small", "Medium", "Large"])
            env_type = display_menu("Select env type", ["Flat", "Perlin Noise"])
            spawn_trees = display_menu("Spawn trees?", ["Yes", "No"])
            spawn_caves = display_menu("Spawn caves?", ["Yes", "No"])
            spawn_water = display_menu("Spawn water?", ["Yes", "No"])

            if env_type == 1:
                ground_type = display_menu("Select ground type", ["Grass", "Dirt", "Stone", "Sand", "Snow"])
                pass
            elif env_type == 2:
                pass
        elif generate_or_load == 2:
            selected_world = display_menu("Select environement", ["Env 1", "Env 2", "Env 3"])
            pass
    elif mode == 2:
        selected_world = display_menu("Select environement", ["Env 1", "Env 2", "Env 3"])
        pass
    elif mode == 3:
        selected_world = display_menu("Select environement", ["Env 1", "Env 2", "Env 3"])
        pass

    app = VoxelEngine()
    app.run()
