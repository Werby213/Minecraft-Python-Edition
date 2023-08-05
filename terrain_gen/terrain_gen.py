from noise import noise2, noise3
from random import random
import settings as sg
from numba import njit

class TerrainGen:

    def __init__(self, env_size, spawn_trees, spawn_caves):
        self.world_size = 3 if env_size == 1 else 6 if env_size == 2 else 12
        self.spawn_trees = spawn_trees
        self.spawn_caves = spawn_caves

    def get_height(self, x, z):
        pass

    @staticmethod
    def get_index(x, y, z):
        return x + sg.CHUNK_SIZE * z + sg.CHUNK_AREA * y

    def set_voxel_id(self, voxels, x, y, z, wx, wy, wz, world_height):
        pass

    @staticmethod
    def place_tree(voxels, x, y, z, voxel_id, ignore_below=False, over_tree_prob=-1):
        rnd = random()
        if (voxel_id != sg.GRASS and not ignore_below) or (rnd > sg.TREE_PROBABILITY or (over_tree_prob >= 0 and rnd > over_tree_prob)):
            return None
        if y + sg.TREE_HEIGHT >= sg.CHUNK_SIZE:
            return None
        if x - sg.TREE_H_WIDTH < 0 or x + sg.TREE_H_WIDTH >= sg.CHUNK_SIZE:
            return None
        if z - sg.TREE_H_WIDTH < 0 or z + sg.TREE_H_WIDTH >= sg.CHUNK_SIZE:
            return None

        # dirt under the tree
        voxels[TerrainGen.get_index(x, y, z)] = sg.DIRT

        # leaves
        m = 0
        for n, iy in enumerate(range(sg.TREE_H_HEIGHT, sg.TREE_HEIGHT - 1)):
            k = iy % 2
            rng = int(random() * 2)
            for ix in range(-sg.TREE_H_WIDTH + m, sg.TREE_H_WIDTH - m * rng):
                for iz in range(-sg.TREE_H_WIDTH + m * rng, sg.TREE_H_WIDTH - m):
                    if (ix + iz) % 4:
                        voxels[TerrainGen.get_index(x + ix + k, y + iy, z + iz + k)] = sg.LEAVES
            m += 1 if n > 0 else 3 if n > 1 else 0

        # tree trunk
        for iy in range(1, sg.TREE_HEIGHT - 2):
            voxels[TerrainGen.get_index(x, y + iy, z)] = sg.WOOD

        # top
        voxels[TerrainGen.get_index(x, y + sg.TREE_HEIGHT - 2, z)] = sg.LEAVES