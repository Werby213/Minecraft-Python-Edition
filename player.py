import pygame as pg
from camera import Camera
from settings import *


class Player(Camera):
    def __init__(self, app, position, rotation):
        self.app = app
        self.velocity = glm.vec3(0, 0, 0)
        super().__init__(position, rotation)

    def update(self):
        self.keyboard_control()
        self.mouse_control()
        self.position += self.velocity * self.app.delta_time
        super().update()

    def handle_event(self, event):
        # adding and removing voxels with clicks
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.env.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_e:
                self.app.save_env()

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()

        input_vel = int(key_state[pg.K_d]) * self.right
        input_vel -= int(key_state[pg.K_q]) * self.right
        input_vel += int(key_state[pg.K_z]) * self.forward
        input_vel -= int(key_state[pg.K_s]) * self.forward

        if glm.length(input_vel) > 0:
            input_vel = glm.normalize(glm.vec3(input_vel.x, 0, input_vel.z)) * PLAYER_SPEED

        y_vel = (int(key_state[pg.K_SPACE]) - int(key_state[pg.K_LSHIFT])) * PLAYER_SPEED

        self.velocity = input_vel + glm.vec3(0, y_vel, 0)