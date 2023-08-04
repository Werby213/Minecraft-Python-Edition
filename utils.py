import numpy as np
import math

def round_position(position):
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

def get_rotation_vector(rotation, rotation_speed):
    dx, dy = rotation_speed
    x, y = rotation
    nx, ny = x + dx, y + dy
    ny = max(-90, min(90, y))
    return (nx - x, ny - y)
    
def get_motion_vector(strafe, rotation):
    """ Returns the current motion vector indicating the velocity of the
    player.

    Returns
    -------
    vector : tuple of len 3
        Tuple containing the velocity in x, y, and z respectively.

    """
    if any(strafe):
        x, _ = rotation
        s = math.degrees(math.atan2(*strafe))
        x_angle = math.radians(x + s)
        dy = 0.0
        dx = math.cos(x_angle)
        dz = math.sin(x_angle)
    else:
        dy = 0.0
        dx = 0.0
        dz = 0.0
    return (dx, dy, dz)