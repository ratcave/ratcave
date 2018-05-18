import pyglet
import ratcave as rc


# Create Window
window = pyglet.window.Window()

def update(dt):
    pass
    # monkey.rotation.y += 15 * dt
pyglet.clock.schedule(update)

# Insert filename into WavefrontReader.
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)

# Create Mesh
monkey = obj_reader.get_mesh("Monkey", scale=.7)
monkey.position.xyz = 0, 0, -3
monkey.uniforms['diffuse'] = 0., 0., 1.
monkey.uniforms['spec_weight'] = 300.

torus = obj_reader.get_mesh("Torus")
torus.position.xyz = 0, 0, -3
torus.rotation.x = 20
torus.uniforms['diffuse'] = 1., 0., 0.
torus.uniforms['spec_weight'] = 300.


# Create Scene
scene = rc.Scene(meshes=[monkey, torus])



@window.event
def on_draw():
    with rc.default_shader:
        scene.draw()

pyglet.app.run()