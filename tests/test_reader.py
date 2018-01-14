from ratcave import Mesh, Scene, WavefrontReader, resources
import pytest


@pytest.fixture
def reader():
    return WavefrontReader(resources.obj_primitives)


def test_reader_returns_mesh(reader):
    cube = reader.get_mesh('Cube')
    assert isinstance(cube, Mesh)



