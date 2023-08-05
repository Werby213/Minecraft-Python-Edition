from terrain_gen.terrain_gen import TerrainGen
from noise import noise2, noise3
from random import random
from settings import *
import math
from numba import njit

class TerrainGenFlat(TerrainGen):

    def __init__(self, env_size, spawn_trees, spawn_caves, ground_type):
        super().__init__(env_size, spawn_trees, spawn_caves)
        self.ground_type = ground_type

    # flat terrain
    def get_height(self, x, z):
        return 15

    def set_voxel_id(self, voxels, x, y, z, wx, wy, wz, world_height):
        voxel_id = self.ground_type

        if wy < world_height - 1 and self.spawn_caves:
            # create caves
            if (noise3(wx * 0.09, wy * 0.09, wz * 0.09) > 0 and
                    noise2(wx * 0.1, wz * 0.1) * 3 + 3 < wy < world_height - 10):
                voxel_id = 0

        # setting ID
        voxels[TerrainGen.get_index(x, y, z)] = voxel_id

        # place tree
        if wy < DIRT_LVL and self.spawn_trees:
            TerrainGen.place_tree(voxels, x, y, z, voxel_id, True, 0.0005)