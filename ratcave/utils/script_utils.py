__author__ = 'ratcave'
import numpy as np
from . import orienting




def correct_orientation_motivepy(rb, n_attempts=3):
    import motive
    """Reset the orientation to account for between-session arena shifts"""
    for attempt in range(n_attempts):
            rb.reset_orientation()
            motive.update()
    additional_rotation = orienting.rotate_to_var(np.array(rb.point_cloud_markers))
    return additional_rotation


def correct_orientation_natnet(rb, n_attempts=3):
    """Assumes the orientation is reset already (need MotivePy to do it automatically) to account for between-session arena shifts"""
    print(("Warning: Assuming that the orientation has been reset to 0,0,0 for the {} rigid body".format(rb.name)))
    additional_rotation = orienting.rotate_to_var(np.array([m.position for m in rb.markers]))
    return additional_rotation


def update_world_position_motivepy(meshes, arena_rb, additional_rot_y_rotation):
    """# Update the positions of everything, based on the MotivePy data of the arena rigid body"""
    for mesh in meshes:
        mesh.world.position = arena_rb.location
        mesh.world.rotation = arena_rb.rotation_global
        mesh.world.rot_y += additional_rot_y_rotation
    return


def update_world_position_natnet(meshes, arena_rb, additional_rot_y_rotation):
    """# Update the positions of everything, based on the MotivePy data of the arena rigid body"""
    for mesh in meshes:
        mesh.world.position = arena_rb.position
        mesh.world.rotation = arena_rb.rotation
        mesh.world.rot_y += additional_rot_y_rotation
    return