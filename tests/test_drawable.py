import ratcave as rc
from ratcave import Mesh, Scene, WavefrontReader, resources
import pyglet
import pytest


@pytest.fixture
def reader():
    return WavefrontReader(resources.obj_primitives)


def test_drawing_no_error(reader):
    cube = reader.get_mesh('Cube')
    torus = reader.get_mesh('Torus')
    scene = Scene(meshes=[cube, torus])
    window = pyglet.window.Window()
    with rc.default_shader:
        scene.draw()
    window.close()