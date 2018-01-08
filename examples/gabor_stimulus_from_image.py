import pyglet
import ratcave as rc
from copy import deepcopy, copy


# Create window and OpenGL context (always must come first!)
window = pyglet.window.Window()

# Load Meshes and put into a Scene
obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)
torus = obj_reader.get_mesh('Plane', position=(0, 0, -2))
torus.uniforms['flat_shading'] = True
torus.uniforms['diffuse'] = 1., 1., 1.
torus.textures.append(rc.Texture.from_image('gabor-50-50.png'))
torus.rotation.z = 90
torus.position.x = -1

torus2 = obj_reader.get_mesh('Plane', position=(0, 0, -2))
torus2.uniforms['flat_shading'] = True
torus2.uniforms['diffuse'] = 1., 1., 1.
torus2.textures.append(rc.Texture.from_image('gabor-50-50.png'))
torus2.rotation.z = 0
torus2.position.x = 1
torus2.scale.x = 2

scene = rc.Scene(meshes=[torus, torus2], bgColor=(.47, .47, .47))
scene.camera.projection.fov_y = 80


# Draw Function
@window.event
def on_draw():
    with rc.default_shader:
        scene.draw()


# Pyglet's event loop run function
pyglet.app.run()