from ratcave import Camera, CameraGroup, PerspectiveProjection, OrthoProjection
import pytest
import numpy as np
import pyglet


def test_camera_physical_attributes():
    cam = Camera()
    assert np.isclose(cam.position.xyz, (0, 0, 0)).all()
    assert np.isclose(cam.rotation.xyz, (0, 0, 0)).all()

    cam.position.x = 1
    assert np.isclose(cam.position.xyz, (1, 0, 0)).all()
    assert np.all(cam.view_matrix[:3, -1] == tuple(-el for el in cam.position.xyz))
    assert np.all(cam.model_matrix[:3, -1] == cam.position.xyz)

    cam.rotation.y = 30
    assert np.isclose(cam.rotation.xyz, (0, 30, 0)).all()
    assert cam.rotation.y == 30


def test_perspective_projection_updates():
    proj = PerspectiveProjection()
    assert np.isclose(proj.projection_matrix[2, 2], (proj.z_far + proj.z_near) / (proj.z_near - proj.z_far))
    assert np.isclose(proj.projection_matrix[0, 0], 1. / np.tan(np.radians(proj.fov_y / 2.)) / proj.aspect)
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


def test_projection_matrix_updates_when_assigning_new_projection():
    cam = Camera()
    assert (cam.projection_matrix == cam.projection.projection_matrix).all()

    old_projmat = cam.projection_matrix.copy()
    cam.projection = OrthoProjection()
    assert (cam.projection_matrix == cam.projection.projection_matrix).all()
    assert not (cam.projection_matrix == old_projmat).all()
    assert not (cam.projection.projection_matrix == old_projmat).all()

    cam.projection = PerspectiveProjection()
    assert (cam.projection_matrix == old_projmat).all()


def test_cameragroup_contains_two_cameras():
    cam = CameraGroup()
    assert hasattr(cam, "cam_right") and hasattr(cam, "cam_left")


def test_cameras_are_cameragroup_childrens():
    cam = CameraGroup()
    assert cam.cam_right in cam.children
    assert cam.cam_left in cam.children


def test_cameras_have_correct_distance():
    dist = 10
    cam = CameraGroup(distance=dist)
    assert cam.distance == dist
    assert (cam.cam_right.position.x - cam.cam_left.position.x) == cam.distance

    cam.distance = 20
    assert (cam.cam_right.position.x - cam.cam_left.position.x) == cam.distance


def test_projection_instance_is_shared_between_cameragroup_and_its_children():
    cam = CameraGroup()
    assert (cam.projection == cam.cam_right.projection) and (cam.projection == cam.cam_left.projection)

    cam.projection = OrthoProjection()
    assert isinstance(cam.projection, OrthoProjection)
    assert (cam.projection == cam.cam_right.projection) and (cam.projection == cam.cam_left.projection)    


def test_look_at_updates_for_children():
    dist = 2.
    cam = CameraGroup(distance=dist)
    point = np.array([0, 0, 0, 1]).reshape(-1, 1)
    point[2] = -1 #np.random.randint(1, 6)

    angle = np.arctan(point[2]/(cam.distance/2))[0]
    cam.cam_right.rotation.y = -np.rad2deg(angle)
    cam.cam_left.rotation.y = np.rad2deg(angle)
    point_view_mat_left = np.dot(cam.cam_left.view_matrix, point)
    point_view_mat_right = np.dot(cam.cam_right.view_matrix, point)
    assert (point_view_mat_left == point_view_mat_right).all()

    cam2 = CameraGroup(distance=dist, look_at=point[:3])
    point_view_mat_left2 = np.dot(cam2.cam_left.view_matrix, point)
    point_view_mat_right2 = np.dot(cam2.cam_right.view_matrix, point)
    assert (point_view_mat_left == point_view_mat_left2).all() and (point_view_mat_right == point_view_mat_right2).all()


def test_viewport():
    win = pyglet.window.Window(width=500, height=550)
    assert win.width == 500
    assert win.height == 550
    proj = PerspectiveProjection()
    viewport = proj.viewport
    assert viewport.width == win.width
    assert viewport.height == win.height
    win.close()


def test_projection_shift():
    for _ in range(50):
        x, y = np.random.uniform(-5, 5, size=2)
        proj = PerspectiveProjection(x_shift=x, y_shift=y)
        smat = proj._get_shift_matrix()
        assert np.isclose(smat[0, 2], x)
        assert np.isclose(smat[1, 2], y)

        proj = PerspectiveProjection()
        old_pmat = proj.projection_matrix.copy()
        proj.x_shift = x
        proj.y_shift = y
        smat = proj._get_shift_matrix()
        assert np.isclose(smat[0, 2], x)
        assert np.isclose(smat[1, 2], y)
        assert not np.isclose(old_pmat, proj.projection_matrix).all()

        cam = Camera()
        old_pmat = cam.projection_matrix.copy()
        assert np.isclose(old_pmat, cam.projection.projection_matrix).all()
        assert np.isclose(old_pmat, cam.projection_matrix).all()
        cam.projection.x_shift = x
        cam.projection.y_shift = y
        assert not np.isclose(old_pmat, cam.projection_matrix).all()

        proj = PerspectiveProjection(x_shift=x)
        cam = Camera(projection=proj)
        old_pmat = cam.projection_matrix.copy()
        assert np.isclose(old_pmat, cam.projection.projection_matrix).all()
        assert np.isclose(old_pmat, cam.projection_matrix).all()
        assert np.isclose(old_pmat, cam.uniforms['projection_matrix']).all()
        cam.projection.y_shift = y
        assert not np.isclose(old_pmat, cam.projection_matrix).all()
        assert not np.isclose(old_pmat, cam.uniforms['projection_matrix']).all()


        proj = PerspectiveProjection()
        old_smat = proj._get_shift_matrix()
        proj.fov_y = 10.
        assert np.isclose(old_smat, proj._get_shift_matrix()).all()



