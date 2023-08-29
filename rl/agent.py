import pygame as pg
from rl.agent_camera import AgentCamera
from settings import *
from meshes.agent_mesh import AgentMesh
from utils import *
# from processor import Processor

class Agent():
    # yaw, pitch
    def __init__(self, voxel_handler, position, rotation):
        self.app = voxel_handler.app
        self.handler = voxel_handler
        self.position = glm.vec3(position)
        self.rotation = glm.vec2(rotation)
        self.jumping = False

        self.mesh = AgentMesh(self.app)

        # Velocity in the y (upward) direction.
        self.dy = 0

        self.strafe = glm.vec2(0)
        self.rotation_speed = glm.vec2(0)

        self.camera = AgentCamera(self)

        # perspective stream
        self.stream = np.zeros((*STREAM_ASPECT, 3), dtype=np.uint8)

        # self.processor = Processor(STREAM_SIZE)

    # def tick(self, model):
    #     """ Called every tick to update the agent's state. """
    #     prediction = self.processor.predict(self.stream)

    #     # first two values are x, z movement
    #     dx, dz, rx, rz, jump, place, destroy = prediction[0]
    #     if dx >= 0.5:
    #         self.strafe = (1, self.strafe[1])
    #     elif dx < 0.5:
    #         self.strafe = (-1, self.strafe[1])
        
    #     if dz >= 0.5:
    #         self.strafe = (self.strafe[0], 1)
    #     elif dz < 0.5:
    #         self.strafe = (self.strafe[0], -1)
        
    #     if rx >= 0.5:
    #         self.rotation_speed = (0, -1)
    #     elif rx < 0.5:
    #         self.rotation_speed = (0, 1)

    #     if rz >= 0.5:
    #         self.rotation_speed = (-1, 0)
    #     elif rz < 0.5:
    #         self.rotation_speed = (1, 0)

    #     if jump >= 0.5:
    #         self.jump()
        
    #     if place >= 0.5:
    #         self.place_block(model)

    #     if destroy >= 0.5:
    #         self.destroy_block(model)

    def update(self, dt):
        # inputs from pygame keyboard
        keys = pg.key.get_pressed()
        self.strafe = glm.vec2(0)
        self.rotation_speed = glm.vec2(0)
        if keys[pg.K_UP]:
            self.strafe = (1, self.strafe[1])
        if keys[pg.K_DOWN]:
            self.strafe = (-1, self.strafe[1])
        if keys[pg.K_LEFT]:
            self.strafe = (self.strafe[0], 1)
        if keys[pg.K_RIGHT]:
            self.strafe = (self.strafe[0], -1)
        if keys[pg.K_l]:
            self.rotation_speed = (-1, 0)
        if keys[pg.K_m]:
            self.rotation_speed = (1, 0)
        if keys[pg.K_o]:
            self.rotation_speed = (0, -1)
        if keys[pg.K_p]:
            self.rotation_speed = (0, 1)

        # Check if the right shift key was just pressed
        if keys[pg.K_RSHIFT] and not self.jump_key_pressed:
            self.jump()
            self.jump_key_pressed = True

        # Check if the right shift key was released
        if not keys[pg.K_RSHIFT]:
            self.jump_key_pressed = False

        # walking
        speed = AGENT_WALKING_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = get_motion_vector(self.strafe, self.rotation)
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity

        # Update your vertical speed: if you are falling, speed up until you
        # hit terminal velocity; if you are jumping, slow down until you
        # start falling.
        self.dy -= dt * AGENT_GRAVITY
        self.dy = max(self.dy, -AGENT_TERMINAL_VELOCITY)
        dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = x - AGENT_WIDTH / 2, y, z - AGENT_WIDTH / 2
        x, y, z = self.collide((x + dx, y + dy, z + dz))
        x, y, z = x + AGENT_WIDTH / 2, y, z + AGENT_WIDTH / 2
        self.position = glm.vec3(x, y, z)

        drx, drz = get_rotation_vector(self.rotation, self.rotation_speed)
        rotation_speed = dt * AGENT_ROTATION_SPEED
        self.rotation = glm.vec2(self.rotation[0] + drx * rotation_speed, self.rotation[1] + drz * rotation_speed)

        self.camera.update()
        self.stream = self.app.get_stream(self)

    def set_uniform(self):
        self.mesh.program['m_model'].write(self.get_model_matrix())

    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), glm.vec3(self.position))
        
        # rotate around center y axis
        m_model = glm.rotate(m_model, glm.radians(-self.rotation[0]), glm.vec3(0, 1, 0))
        m_model = glm.translate(m_model, glm.vec3(-AGENT_WIDTH / 2, 0, -AGENT_WIDTH / 2))
        
        return m_model
    
    def render(self):
        self.set_uniform()
        self.mesh.render()

    def move(self, direction):
        """ Moves the player by the given amount. """
        self.strafe = direction
    
    def rotate(self, rotation):
        """ Rotates the player by the given amount. """
        self.rotation = rotation
    
    # def place_block(self, model):
    #     vector = self.get_sight_vector()
    #     _, previous = model.hit_test(self.position, vector)
    #     if previous:
    #         model.add_block(previous, self.block)

    # def destroy_block(self, model):
    #     vector = self.get_sight_vector()
    #     block, _ = model.hit_test(self.position, vector)
    #     if block:
    #         texture = model.world[block]
    #         if texture != STONE:
    #             model.remove_block(block)

    def jump(self):
        """ Called when the user presses the jump key. """
        if self.dy == 0:
            self.dy = AGENT_JUMP_SPEED
            self.jump_key_pressed = True
    
    # stuck along vertical walls problem
    def collide(self, new_position):
        agent_aabb = [list(new_position), [new_position[0] + AGENT_WIDTH, new_position[1] + AGENT_HEIGHT, new_position[2] + AGENT_WIDTH]]

        player_position = (int(new_position[0]), int(new_position[1]), int(new_position[2]))
        for dx in range(-1, 2):  # check the surrounding blocks in x dimension
            for dz in range(-1, 2):  # check the surrounding blocks in z dimension
                for dy in range(AGENT_HEIGHT + 1):  # check each height
                    block_position = player_position[0] + dx, player_position[1] + dy, player_position[2] + dz
                    block_aabb = (block_position, (block_position[0] + 1, block_position[1] + 1, block_position[2] + 1))

                    if self.aabb_collision(agent_aabb, block_aabb):
                        voxel_id, _, _, _ = self.handler.get_voxel_id(glm.ivec3(block_position))
                        if not voxel_id:
                            continue

                        penetration = [0, 0, 0]
                        for i in range(3):
                            penetration[i] = min(abs(agent_aabb[1][i] - block_aabb[0][i]), abs(block_aabb[1][i] - agent_aabb[0][i]))

                        min_axis = penetration.index(min(penetration))
                        overlap_a = agent_aabb[1][min_axis] - block_aabb[0][min_axis]
                        overlap_b = block_aabb[1][min_axis] - agent_aabb[0][min_axis]

                        if overlap_a < overlap_b:
                            agent_aabb[0][min_axis] -= penetration[min_axis]
                            agent_aabb[1][min_axis] -= penetration[min_axis]
                        else:
                            agent_aabb[0][min_axis] += penetration[min_axis]
                            agent_aabb[1][min_axis] += penetration[min_axis]

                        # If the collision was with the ground (y-axis), stop falling
                        if min_axis == 1:
                            self.dy = 0
        return tuple(agent_aabb[0])

    def aabb_collision(self, a, b):
        return (a[0][0] < b[1][0] and a[1][0] > b[0][0] and
                a[0][1] < b[1][1] and a[1][1] > b[0][1] and
                a[0][2] < b[1][2] and a[1][2] > b[0][2])
    
    # def mutate(self):
    #     self.processor.mutate()