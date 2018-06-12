import unittest
from ratcave import resources, WavefrontReader, Mesh
import pytest
import numpy as np
import pickle
from tempfile import NamedTemporaryFile
import sys

np.random.seed(100)

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
    assert np.isclose(cube2.model_matrix, cube.model_matrix).all()
    assert np.isclose(cube2.normal_matrix, cube.normal_matrix).all()
    assert np.isclose(cube2.view_matrix, cube.view_matrix).all()
    cube2.rotation.x = 22.5
    assert not np.all(np.isclose(cube2.rotation.xyz, cube.rotation.xyz))
    assert np.all(cube.position.xyz == cube2.position.xyz)
    assert cube2.visible == cube.visible

    assert not np.isclose(cube2.model_matrix, cube.model_matrix).all()
    assert not np.isclose(cube2.normal_matrix, cube.normal_matrix).all()
    assert not np.isclose(cube2.view_matrix, cube.view_matrix).all()



def test_mesh_can_draw():
    print('testing the draw process..')
    mesh = cube()
    assert not mesh.vbos
    assert not mesh.vao

#     with pytest.raises(UnboundLocalError):
#         mesh.draw()

#     with default_shader:
#         mesh.draw()

#     assert mesh.vao
#     assert mesh.vbos
#     assert len(mesh.vbos) == 3  # vertices, texcoords, and normals




if sys.platform == 'linux':
    def test_mesh_is_picklable():
        for _ in range(2):
            phys = cube()
            phys.position.xyz =np.random.uniform(-5, 5, 3)
            phys.rotation.xyz = np.random.uniform(-5, 5, 3)
            phys.scale.xyz = np.random.uniform(1, 5, 3)

            with NamedTemporaryFile('wb', delete=False) as f:
                phys.to_pickle(f.name)
            with open(f.name, 'rb') as f:
                phys2 = Mesh.from_pickle(f.name)
            assert phys.position.xyz == phys2.position.xyz
            assert phys.rotation.xyz == phys2.rotation.xyz
            assert phys.scale.xyz == phys2.scale.xyz
            assert np.isclose(phys.model_matrix[:3, -1], phys2.model_matrix[:3, -1]).all()

            phys.position.xyz = 5, 5, 5
            assert not np.isclose(phys.position.xyz, phys2.position.xyz).all()
            assert not np.isclose(phys.model_matrix[:3, -1], phys2.model_matrix[:3, -1]).all()
            assert np.isclose(phys.model_matrix, phys.uniforms['model_matrix']).all()
            assert np.isclose(phys.normal_matrix, phys.uniforms['normal_matrix']).all()

            phys2.position.xyz = 5, 5, 5
            assert np.isclose(phys.position.xyz, phys2.position.xyz).all()
            assert np.isclose(phys2.position.xyz, phys2.model_matrix[:3, -1]).all()

            assert np.isclose(phys2.model_matrix, phys2.uniforms['model_matrix']).all()
            assert np.isclose(phys2.normal_matrix, phys2.uniforms['normal_matrix']).all()
            assert np.isclose(phys.normal_matrix, phys2.normal_matrix).all()
            assert np.isclose(phys.view_matrix, phys2.view_matrix).all()

            assert np.isclose(phys.model_matrix[:3, -1], phys2.model_matrix[:3, -1]).all()


            phys2.position.xyz = 10, 10, 10
            assert np.isclose(phys2.position.xyz, phys2.uniforms['model_matrix'][:3, -1]).all()

            assert np.isclose(phys.vertices, phys2.vertices).all()
            assert np.isclose(phys.normals, phys2.normals).all()
            assert np.isclose(phys.texcoords, phys2.texcoords).all()