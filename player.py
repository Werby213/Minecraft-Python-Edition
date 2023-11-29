#player.py
import pygame as pg
import pygame.time

from utils import *
from camera import Camera
from settings import *


class Player(Camera):
    def __init__(self, app, position, rotation):
        self.app = app
        self.velocity = glm.vec3(0, 0, 0)
        self.flying_mode = False
        self.y_vel = 0
        self.is_moving = True
        self.input_vel = 0
        self.space_pressed = False
        self.double_space_pressed = False
        self.space_press_time = 0

        self.w_pressed = False
        self.w_press_time = 0

        self.strafe = glm.vec2(0)
        self.rotation = glm.vec2(rotation)

        super().__init__(position, rotation)
        self.position.x = self.position.z = CENTER_XZ
        self.position.y = CENTER_Y

    def update(self):
        self.keyboard_control()
        self.mouse_control()

        self.velocity += glm.vec3(0, self.y_vel, 0)
        self.position += self.velocity * self.app.delta_time * 1000
        self.damping = 0
        self.is_moving = glm.length(self.velocity) > 0

        self.handle_collisions(self.position)

        super().update(self.app.delta_time, self.is_moving, self.is_on_ground, self.velocity)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.env.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_e:
                self.app.save_env()
            if event.key == pg.K_c:
                self.app.switch_camera()
            if event.key == pg.K_SPACE:
                current_time = pg.time.get_ticks()

                if self.space_pressed:
                    if current_time - self.space_press_time <= 300:
                        self.double_space_pressed = True
                        self.flying_mode = not self.flying_mode
                        self.space_pressed = False
                    else:
                        self.double_space_pressed = False

                self.space_press_time = current_time
                self.space_pressed = True

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()

        if key_state[pg.K_F8]:
            self.position = glm.vec3(float(CENTER_XZ), float(CENTER_Y), float(CENTER_XZ))
            return

        # Calculate acceleration based on input
        forward_input = int(key_state[pg.K_w]) - int(key_state[pg.K_s])
        strafe_input = int(key_state[pg.K_d]) - int(key_state[pg.K_a])

        # Calculate input acceleration in world space
        acceleration = (
                forward_input * self.forward + strafe_input * self.right
        )

        if glm.length(acceleration) > 0:
            acceleration = glm.normalize(acceleration) * PLAYER_ACCELERATION

        # Apply self.damping to simulate inertia
        if self.is_on_ground():
            self.damping = PLAYER_DAMPING_GROUND
        else:
            if self.flying_mode:
                self.damping = PLAYER_DAMPING_AIR
            else:
                self.damping = 15

        self.velocity += (acceleration - self.damping * self.velocity) * self.app.delta_time

        if self.flying_mode:
            if self.is_on_ground():
                self.y_vel = 0
            else:
                self.y_vel = max(0, int(key_state[pg.K_SPACE]) * PLAYER_SPEED)
        else:
            if int(key_state[pg.K_SPACE]) and self.is_on_ground():
                self.y_vel = PLAYER_JUMP_SPEED
            else:
                if self.is_on_ground():
                    self.y_vel = 0
                else:
                    self.y_vel -= PLAYER_GRAVITY * 1000 * self.app.delta_time

        self.velocity.y = self.y_vel

    def is_on_ground(self):
        player_position = (int(self.position.x), int(self.position.y), int(self.position.z))
        for dy in range(1, AGENT_HEIGHT + 1):
            block_position = player_position[0], player_position[1] - dy, player_position[2]
            voxel_id, _, _, _ = self.app.env.world.voxel_handler.get_voxel_id(glm.ivec3(block_position))
            if voxel_id:
                return True
        return False
    def handle_collisions(self, new_position):
        player_aabb = self.get_player_aabb()

        player_position = (int(new_position[0]), int(new_position[1]), int(new_position[2]))
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                for dy in range(-1, 2):
                    block_position = player_position[0] + dx, player_position[1] + dy, player_position[2] + dz
                    block_aabb = (
                        [block_position[0], block_position[1], block_position[2]],
                        [block_position[0] + 1, block_position[1] + 1, block_position[2] + 1]
                    )

                    if self.aabb_collision(player_aabb, block_aabb):
                        voxel_id, _, _, _ = self.app.env.world.voxel_handler.get_voxel_id(glm.ivec3(block_position))
                        if not voxel_id:
                            continue

                        penetration = [0, 0, 0]
                        for i in range(3):
                            penetration[i] = min(abs(player_aabb[1][i] - block_aabb[0][i]),
                                                 abs(block_aabb[1][i] - player_aabb[0][i]))

                        min_axis = penetration.index(min(penetration))
                        overlap_a = player_aabb[1][min_axis] - block_aabb[0][min_axis]
                        overlap_b = block_aabb[1][min_axis] - player_aabb[0][min_axis]

                        if overlap_a < overlap_b:
                            new_position[min_axis] -= penetration[min_axis]
                        else:
                            new_position[min_axis] += penetration[min_axis]

                        if min_axis == 1:
                            self.y_vel = 0

        return new_position

    def get_player_aabb(self):
        half_width = PLAYER_WIDTH / 2
        half_height = PLAYER_HEIGHT / 2
        bottom_y = self.position.y - half_height - 1  # shift down by 1 block
        top_y = self.position.y + half_height - 1

        player_aabb = [
            [self.position.x - half_width, bottom_y, self.position.z - half_width],
            [self.position.x + half_width, top_y, self.position.z + half_width]
        ]
        return player_aabb
    def aabb_collision(self, a, b):
        return (a[0][0] < b[1][0] and a[1][0] > b[0][0] and
                a[0][1] < b[1][1] and a[1][1] > b[0][1] and
                a[0][2] < b[1][2] and a[1][2] > b[0][2])