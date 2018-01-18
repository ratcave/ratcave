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
monkey = obj_reader.get_mesh("Monkey")
monkey.position.xyz = 0, 0, -3
monkey.textures.append(rc.Texture.from_image('../assets/wood.jpg'))

# Create Scene
scene = rc.Scene(meshes=[monkey])

@window.event
def on_draw():
    with rc.default_shader:
        scene.draw()

pyglet.app.run()