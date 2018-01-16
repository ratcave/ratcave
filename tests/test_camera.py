from ratcave import Camera, PerspectiveProjection, OrthoProjection
import pytest
import numpy as np
import pyglet


def test_camera_physical_attributes():
    cam = Camera()
    assert cam.position.xyz == (0, 0, 0)
    assert cam.rotation.xyz == (0, 0, 0)

    cam.position.x = 1
    assert cam.position.xyz == (1, 0, 0)
    assert np.all(cam.view_matrix[:3, -1] == tuple(-el for el in cam.position.xyz))
    assert np.all(cam.model_matrix[:3, -1] == cam.position.xyz)


    cam.rotation.y = 30
    assert cam.rotation.xyz == (0, 30, 0)
    assert cam.rotation.y == 30


def test_perspective_projection_updates():
    proj = PerspectiveProjection()
    assert np.isclose(proj.projection_matrix[2, 2], (proj.z_far + proj.z_near) / (proj.z_near - proj.z_far))
    assert np.isclose(proj.projection_matrix[0, 0], 1./np.tan(np.radians(proj.fov_y / 2.)) / proj.aspect)
    proj.z_far = 30
    assert np.isclose(proj.projection_matrix[2, 2], (proj.z_far + proj.z_near) / (proj.z_near - proj.z_far))
    assert np.isclose(proj.projection_matrix[0, 0], 1. / np.tan(np.radians(proj.fov_y / 2.)) / proj.aspect)
    proj.aspect = .1
    assert np.isclose(proj.projection_matrix[0, 0], 1. / np.tan(np.radians(proj.fov_y / 2.)) / proj.aspect)
    proj.fov_y = 25
    assert np.isclose(proj.projection_matrix[0, 0], 1. / np.tan(np.radians(proj.fov_y / 2.)) / proj.aspect)

    with pytest.raises(ValueError):
        proj.z_far = -10

    with pytest.raises(ValueError):
        proj.z_near = 100

    with pytest.raises(ValueError):
        proj.z_near = -20


    with pytest.raises(ValueError):
        p2 = PerspectiveProjection()
        p2.z_near = .1
        p2.z_far = .01

    with pytest.raises(ValueError):
        PerspectiveProjection(z_far=-.1)


    with pytest.raises(ValueError):
        proj.fov_y = -10


def test_default_projection_is_perspective():
    cam = Camera()
    assert isinstance(cam.projection, PerspectiveProjection)


def test_camera_has_all_uniforms():
    cam = Camera()
    for name in ['projection_matrix', 'model_matrix', 'view_matrix', 'camera_position']:
        assert name in cam.uniforms


def test_projection_attributes_change_cameras_projection_matrix_uniform():
    cam = Camera()
    for proj in [(), PerspectiveProjection(), PerspectiveProjection()]:
        if isinstance(proj, int):
            cam, proj = Camera(name='Early'), PerspectiveProjection()
            cam.projection = proj
        elif proj:
            cam = Camera(projection=proj)
        old_projmat = cam.projection_matrix.copy()
        old_pm_uni = cam.uniforms['projection_matrix'].copy()
        assert np.all(old_projmat == old_pm_uni)
        cam.projection.aspect = np.random.random()
        assert np.any(cam.projection_matrix != old_projmat)
        assert np.any(cam.uniforms['projection_matrix'] != old_pm_uni)
        assert np.all(cam.projection_matrix == cam.uniforms['projection_matrix'])
        assert np.all(cam.projection.projection_matrix == cam.projection_matrix)
        assert np.all(cam.uniforms['projection_matrix'] == cam.projection.projection_matrix)


def test_viewport():
    win = pyglet.window.Window(width=500, height=550)
    assert win.width == 500
    assert win.height == 550
    proj = PerspectiveProjection()
    viewport = proj.viewport
    assert viewport.width == win.width
    assert viewport.height == win.height
    win.close()