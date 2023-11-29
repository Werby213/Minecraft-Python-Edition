import glm
from settings import *
from frustum import Frustum
import time
from random import uniform
class Camera:
    def __init__(self, position, rotation):
        yaw, pitch = rotation
        self.position = glm.vec3(position)
        self.position.y -=1
        self.yaw = yaw
        self.pitch = pitch
        self.yaw_sway = 0.0
        self.pitch_sway = 0.0
        self.sway_timer = 0.0
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.m_view = glm.mat4()

        self.frustum = Frustum(self)

    def update(self, delta_time, is_moving, on_ground, velocity):
        self.update_vectors()
        self.camera_sway(delta_time, is_moving, on_ground, velocity)
        self.update_view_matrix()

    def update_view_matrix(self):
        self.m_view = glm.lookAt(
            self.position,
            self.position + self.forward,
            self.up
        )

    def update_vectors(self):
        self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self.forward.y = glm.sin(self.pitch)
        self.forward.z = glm.sin(self.yaw) * glm.cos(self.pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def camera_sway(self, delta_time, is_moving, on_ground, velocity):
        if not on_ground:
            return

        # Sway magnitude and frequency
        sway_magnitude = 0.002
        sway_frequency = 7.0
        # Velocity influence on sway
        velocity_influence = 50

        self.sway_timer += delta_time * sway_frequency

        sway_offset_x = sway_magnitude * glm.sin(self.sway_timer)
        sway_offset_y = sway_magnitude * glm.sin(2 * self.sway_timer)

        sway_offset_x *= velocity.x * velocity_influence
        sway_offset_y *= velocity.z * velocity_influence

        sway_right = glm.normalize(self.right + sway_offset_x * self.up)
        sway_up = glm.normalize(self.up + sway_offset_y * self.right)

        self.right = sway_right
        self.up = sway_up



    def rotate_pitch(self, delta_y):
        self.pitch -= delta_y
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)

    def rotate_yaw(self, delta_x):
        self.yaw += delta_x

    def move_left(self, velocity):
        self.position -= self.right * velocity

    def move_right(self, velocity):
        self.position += self.right * velocity

    def move_up(self, velocity):
        self.position += self.up * velocity

    def move_down(self, velocity):
        self.position -= self.up * velocity

    def move_forward(self, velocity):
        self.position += self.forward * velocity

    def move_back(self, velocity):
        self.position -= self.forward * velocity
