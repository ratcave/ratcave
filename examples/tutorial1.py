import pyglet
import ratcave as rc

# Create Window
window = pyglet.window.Window()

# Insert filename into WavefrontReader.
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)

# Create Mesh
monkey = obj_reader.get_mesh("Monkey")
monkey.position.xyz = 0, 0, -2

@window.event
def on_draw():
    with rc.default_shader, rc.default_states, rc.default_camera:
        monkey.draw()


pyglet.app.run()