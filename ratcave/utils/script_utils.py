__author__ = 'ratcave'
import numpy as np
from .. import graphics


def motive_camera_vislight_configure():
    import motive
    for cam in motive.get_cams():

            # All cameras should have frame rate changed.
            cam.frame_rate = 30

            if 'Prime 13' in cam.name:
                cam.set_settings(videotype=0, exposure=33000, threshold=80, intensity=0)  #check if 480 corresponds to these thousands described in motive
                cam.image_gain = 8  # 8 is the maximum image gain setting
                cam.set_filter_switch(False)
            else:
                cam.set_settings(0, cam.exposure, cam.threshold, cam.intensity)


def correct_orientation(rb, n_attempts=3):
    import motive
    import orienting
    """Reset the orientation to account for between-session arena shifts"""
    for attempt in range(n_attempts):
            rb.reset_orientation()
            motive.update()
    additional_rotation = orienting.rotate_to_var(np.array(rb.point_cloud_markers))
    return additional_rotation


def get_arena_from(file_name=graphics.resources.obj_arena, cubemap=True):
    """Just returns the arena mesh from a .obj file."""
    reader = graphics.WavefrontReader(file_name)
    arena = reader.get_mesh('Arena', lighting=True, centered=False)
    arena.cubemap = cubemap
    return arena

def update_world_position(meshes, arena_rb, additional_rotation=0.):
    """# Update the positions of everything, based on the MotivePy data of the arena rigid body"""
    for mesh in meshes:
        mesh.world.position = arena_rb.location
        mesh.world.rotation = arena_rb.rotation_global
        mesh.world.rot_y += additional_rotation
    return