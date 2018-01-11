from ratcave import resources, WavefrontReader, default_shader
import pytest
import numpy as np
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
