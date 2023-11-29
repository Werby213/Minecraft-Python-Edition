import glm
from settings import *
from frustum import Frustum
import time
class Camera:
    def __init__(self, position, rotation):
        yaw, pitch = rotation
        self.position = glm.vec3(position)
        self.yaw = yaw
        self.pitch = pitch
        self.yaw_sway = 0.0
        self.pitch_sway = 0.0

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.m_view = glm.mat4()

        self.frustum = Frustum(self)

    def update(self, delta_time, is_moving, on_ground, velocity):
        self.update_vectors()
        self.update_sway(delta_time, is_moving, on_ground, velocity)
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

    def update_sway(self, delta_time, is_moving, on_ground, velocity):
        sway_speed = 1
        sway_amplitude = 1
        current_time = time.time()

        if is_moving:
            if on_ground == False:
                sway_speed *= glm.length(velocity)
                self.yaw_sway = glm.sin(current_time * sway_speed) * sway_amplitude
                self.pitch_sway = glm.cos(current_time * sway_speed) * sway_amplitude

                self.yaw += self.yaw_sway * delta_time
                self.pitch += self.pitch_sway * delta_time




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
