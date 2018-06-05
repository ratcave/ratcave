from ratcave import resources, WavefrontReader, EmptyEntity
import pytest
import numpy as np
@pytest.fixture()
def cube():
    reader = WavefrontReader(resources.obj_primitives)
    return reader.get_mesh("Cube")


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


def test_dynamic_mode_reflects_array_writability():
    reader = WavefrontReader(resources.obj_primitives)
    cube = reader.get_mesh("Cube", dynamic=True)
    old_vert = cube.vertices[0, 0]
    cube.vertices[:] += 1.
    assert cube.vertices[0, 0] == old_vert + 1
    assert cube.dynamic
    cube.dynamic = False
    assert not cube.dynamic
    with pytest.raises(ValueError):
        cube.vertices[:] += 1.
    cube.dynamic = True
    cube.vertices[:] += 1.
    assert cube.vertices[0][0] == old_vert + 2


def test_wavefront_objects_get_name():
    reader = WavefrontReader(resources.obj_primitives)
    cube = reader.get_mesh('Cube', name='CoolCube')
    assert hasattr(cube, 'name')
    assert cube.name == 'CoolCube'

def test_empty_entity_gets_name():
    obj = EmptyEntity(name='DummyObj')
    assert hasattr(obj, 'name')
    assert obj.name == 'DummyObj'
