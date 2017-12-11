import pyglet.gl as gl


def draw_vr_anaglyph(cube_fbo, vr_scene, active_scene, eye_poses=(.01, -.01)):
    """
    Experimental anaglyph drawing function for VR system with red/blue glasses, used in Sirota lab.
    (note: assumes shader uses playerPos like ratcave's default shader.)
    """
    color_masks = [(True, False, False, True), (False, True, True, True)]
    cam = vr_scene.camera
    orig_cam_position = cam.position.xyz

    for color_mask, eye_pos in zip(color_masks, eye_poses):
        gl.glColorMask(*color_mask)
        cam.position.xyz = cam.model_matrix.dot([eye_pos, 0., 0., 1.])[:3]  # inter_eye_distance / 2.
        cam.uniforms['playerPos'] = cam.position.xyz
        with cube_fbo as fbo:
            vr_scene.draw360_to_texture(fbo.texture)
        cam.position.xyz = orig_cam_position
        active_scene.draw()
