import unittest
from ratcave import resources, WavefrontReader, default_shader
import pytest
import numpy as np


class TestMesh(unittest.TestCase):
    """
    Run tests from main project folder.
    """

    def setUp(self):
        self.reader = WavefrontReader(resources.obj_primitives)

        self.mesh = self.reader.get_mesh("Cube")

    def tearDown(self):
        pass

    def test_position_update_to_modelmatrix(self):

        for pos in [(4,5, 6), (5, 4, 1)]:
            mesh = self.reader.get_mesh("Cube", position=pos)
            self.assertTrue(np.isclose(mesh.position.xyz, pos).all())
            self.assertTrue(np.isclose(mesh.uniforms['model_matrix'][:3, 3], pos).all())

        for pos in [(4,5, 6), (5, 4, 1)]:
            mesh = self.mesh
            mesh.position.xyz = pos
            self.assertTrue(np.isclose(mesh.position.xyz, pos).all())
            self.assertTrue(np.isclose(mesh.uniforms['model_matrix'][:3, 3], pos).all())


    def test_position_update(self):

        mesh = self.mesh
        for pos in [(4,5, 6), (5, 4, 1)]:
            mesh.position.x, mesh.position.y, mesh.position.z = pos
            self.assertTrue(np.isclose(mesh.position.xyz, pos).all())

    def test_rotation_update(self):

        mesh = self.mesh
        for rot in [(4, 5, 6), (5, 4, 1)]:
            mesh.rotation.x, mesh.rotation.y, mesh.rotation.z = rot
            self.assertTrue(np.isclose(mesh.rotation.xyz, rot).all())

    def test_scale_update(self):

        mesh = self.mesh
        for rot in [(4, 5, 6), (5, 4, 1)]:
            mesh.scale.x, mesh.scale.y, mesh.scale.z = rot
            self.assertTrue(np.isclose(mesh.scale.xyz, rot).all())

        for rot in [4, 5]:
            mesh.scale.xyz = rot
            self.assertTrue(np.isclose(mesh.scale.xyz, (rot, rot, rot)).all())


@pytest.fixture()
def cube():
    reader = WavefrontReader(resources.obj_primitives)
    return reader.get_mesh("Cube")


def test_mesh_has_all_uniforms(cube):
    for name in ['model_matrix', 'normal_matrix']:
        assert name in cube.uniforms


def test_mesh_vertices_are_correct(cube):
    assert cube.vertices.shape[1] == 3
    assert cube.texcoords.shape[1] == 2
    assert cube.normals.shape[1] == 3


def test_mesh_is_visible_by_default(cube):
    assert cube.visible == True


def test_mesh_copying_works(cube):
    cube2 = cube.copy()
    assert np.all(np.isclose(cube2.vertices, cube.vertices))
    assert np.all(np.isclose(cube2.normals, cube.normals))
    assert np.all(np.isclose(cube2.texcoords, cube.texcoords))
    assert np.all(np.isclose(cube2.rotation.xyz, cube.rotation.xyz))
    cube2.rotation.x = 22.5
    assert not np.all(np.isclose(cube2.rotation.xyz, cube.rotation.xyz))
    assert np.all(cube.position.xyz == cube2.position.xyz)
    assert cube2.visible == cube.visible


def test_mesh_can_draw():
    print('testing the draw process..')
    mesh = cube()
    assert not mesh.vbos
    assert not mesh.vao

    with pytest.raises(UnboundLocalError):
        mesh.draw()

    with default_shader:
        mesh.draw()

    assert mesh.vao
    assert mesh.vbos
    assert len(mesh.vbos) == 3  # vertices, texcoords, and normals
