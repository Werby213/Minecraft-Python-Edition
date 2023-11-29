from noise import noise2, noise3
from random import random
from settings import *
import math
import logging
from numba import njit
from terrain_gen.terrain_gen import TerrainGen

class TerrainGenPerlin(TerrainGen):
    @staticmethod
    def get_height(x, z):
        # island mask
        island = 1 / (pow(0.0025 * math.hypot(x - CENTER_XZ, z - CENTER_XZ), 20) + 0.0001)
        island = min(island, 1)

        # amplitude
        a1 = CENTER_Y
        a2, a4, a8 = a1 * 0.5, a1 * 0.25, a1 * 0.125

        # frequency
        f1 = 0.005
        f2, f4, f8 = f1 * 2, f1 * 4, f1 * 8

        if noise2(0.1 * x, 0.1 * z) < 0:
            a1 /= 1.07

        height = 0
        height += noise2(x * f1, z * f1) * a1 + a1
        height += noise2(x * f2, z * f2) * a2 - a2
        height += noise2(x * f4, z * f4) * a4 + a4
        height += noise2(x * f8, z * f8) * a8 - a8

        height = max(height,  noise2(x * f8, z * f8) + 2)
        height *= island

        return int(height)

    @staticmethod
    def get_index(x, y, z):
        return x + CHUNK_SIZE * z + CHUNK_AREA * y

    @staticmethod
    def set_voxel_id(voxels, x, y, z, wx, wy, wz, world_height):
        voxel_id = 0

        if wy < world_height - 1:
            # create caves
            if (noise3(wx * 0.09, wy * 0.09, wz * 0.09) > 0 and
                    noise2(wx * 0.1, wz * 0.1) * 3 + 3 < wy < world_height - 10):
                voxel_id = 0

            else:
                voxel_id = STONE
        else:
            rng = int(7 * random())
            ry = wy - rng
            if SNOW_LVL <= ry < world_height:
                voxel_id = SNOW

            elif STONE_LVL <= ry < SNOW_LVL:
                voxel_id = STONE

            elif DIRT_LVL <= ry < STONE_LVL:
                voxel_id = DIRT

            elif GRASS_LVL <= ry < DIRT_LVL:
                voxel_id = GRASS

            else:
                voxel_id = SAND

        # setting ID
        voxels[TerrainGen.get_index(x, y, z)] = voxel_id

        # place tree
        if wy < DIRT_LVL:
            TerrainGen.place_tree(voxels, x, y, z, voxel_id)