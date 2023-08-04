import pygame as pg
import numpy as np
from settings import *
from meshes.agent_mesh import AgentMesh
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

        # perspective stream
        self.stream = np.zeros((STREAM_SIZE, STREAM_SIZE, 3), dtype=np.uint8)

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
        dx, dy, dz = self.get_motion_vector()
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
        x, y, z = self.collide((x + dx, y + dy, z + dz))
        self.position = glm.vec3(x, y, z)

        drx, drz = self.get_rotation_vector()
        rotation_speed = dt * AGENT_ROTAION_SPEED
        self.rotation = glm.vec2(self.rotation[0] + drx * rotation_speed, self.rotation[1] + drz * rotation_speed)

    def set_uniform(self):
        self.mesh.program['m_model'].write(self.get_model_matrix())

    def get_model_matrix(self):
        m_model = glm.translate(glm.mat4(), glm.vec3(self.position))
        m_model = glm.rotate(m_model, self.rotation.x, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rotation.y, glm.vec3(1, 0, 0))
        
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

    def get_rotation_vector(self):
        dx, dy = self.rotation_speed
        x, y = self.rotation
        nx, ny = x + dx, y + dy
        ny = max(-90, min(90, y))
        return (nx - x, ny - y)
    
    def get_block_position(self, position):
        """ Accepts `position` of arbitrary precision and returns the block
        containing that position.

        Parameters
        ----------
        position : tuple of len 3

        Returns
        -------
        block_position : tuple of ints of len 3

        """
        x, y, z = position
        x, y, z = (np.rint(x), np.rint(y), np.rint(z))
        return (x, y, z)

    
    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.

        """
        if any(self.strafe):
            x, _ = self.rotation
            s = math.degrees(math.atan2(*self.strafe))
            x_angle = math.radians(x + s)
            dy = 0.0
            dx = math.cos(x_angle)
            dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)
    
    def collide(self, new_position):
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.05
        p = list(new_position)
        np = self.get_block_position(new_position)
        for face in FACES:  # check all surrounding blocks
            for i in range(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in range(math.ceil(AGENT_HEIGHT)):  # check each height
                    op = list(np)
                    op[1] += dy
                    op[i] += face[i]
                    voxel_id, _, _, _ = self.handler.get_voxel_id(glm.ivec3(op))
                    if not voxel_id:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break
        return tuple(p)

    # def update_stream(self, stream):
    #     self.stream = stream
    
    # def mutate(self):
    #     self.processor.mutate()
    
    # def get_sight_vector(self):
    #     """ Returns the current line of sight vector indicating the direction
    #     the player is looking.

    #     """
    #     x, y = self.rotation
    #     # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
    #     # is 1 when looking ahead parallel to the ground and 0 when looking
    #     # straight up or down.
    #     m = math.cos(math.radians(y))
    #     # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
    #     # looking straight up.
    #     dy = math.sin(math.radians(y))
    #     dx = math.cos(math.radians(x - 90)) * m
    #     dz = math.sin(math.radians(x - 90)) * m
    #     return (dx, dy, dz)