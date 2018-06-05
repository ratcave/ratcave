import ratcave as rc
from ratcave import Mesh, Scene, WavefrontReader, resources
import pyglet
import pytest
import os


@pytest.fixture
def reader():
    return WavefrontReader(resources.obj_primitives)


def test_drawing_no_error(reader):
    cube = reader.get_mesh('Cube')
    torus = reader.get_mesh('Torus')
    scene = Scene(meshes=[cube, torus])
    window = pyglet.window.Window()
    if not 'APPVEYOR' in os.environ:
        with rc.default_shader:
            scene.draw()
    window.close()
