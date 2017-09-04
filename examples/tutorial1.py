import pyglet
import fruitloop as fruit



# Create Window
window = pyglet.window.Window()


def update(dt):
    pass


pyglet.clock.schedule(update)

# Insert filename into WavefrontReader.
obj_filename = fruit.resources.obj_primitives
obj_reader = fruit.WavefrontReader(obj_filename)

# Create Mesh
monkey = obj_reader.get_mesh("Monkey")
monkey.position.xyz = 0, 0, -2

# Create Scene
scene = fruit.Scene(meshes=[monkey])

shader = fruit.Shader.from_file(*fruit.resources.genShader)
@window.event
def on_draw():
    with shader:
        scene.draw()



pyglet.app.run()