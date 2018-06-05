import pyglet
from pyglet.window import key
import ratcave as rc

# Create Window
window = pyglet.window.Window(resizable=True)
keys = key.KeyStateHandler()
window.push_handlers(keys)


def update(dt):
    pass
pyglet.clock.schedule(update)

# Insert filename into WavefrontReader.
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)

# Create Meshes
sun = obj_reader.get_mesh("Sphere", name='sun')
merkury = obj_reader.get_mesh("Sphere", scale =.1, name='merkury')
venus   = obj_reader.get_mesh("Sphere", scale =.2, name='venus')
earth   = obj_reader.get_mesh("Sphere", scale =.2, name='earth')
mars    = obj_reader.get_mesh("Sphere", scale =.2, name='mars')
jupyter = obj_reader.get_mesh("Sphere", scale =.4, name='jupyter')
moon = obj_reader.get_mesh("Sphere", scale =.5, name='moon')

# Create Empty Entities
empty_merkury = rc.EmptyEntity(name='sun_merkury')
empty_venus   = rc.EmptyEntity(name='sun_venus')
empty_earth   = rc.EmptyEntity(name='sun_earth')
empty_mars    = rc.EmptyEntity(name='sun_mars')
empty_jupyter = rc.EmptyEntity(name='sun_jupyter')

# Define Relationships
sun.add_children(empty_merkury, empty_earth, empty_venus, empty_mars, empty_jupyter)

empty_merkury.add_child(merkury)
empty_venus.add_child(venus)
empty_earth.add_child(earth)
empty_mars.add_child(mars)
empty_jupyter.add_child(jupyter)

earth.add_child(moon)

# Define Relative Positions
sun.rotation.x = 50
sun.position.xyz = 0, 0, -12

merkury.position.z += 1
venus.position.z += 2
earth.position.z += 3
mars.position.z += 4
jupyter.position.z += 5

moon.position.z += 1

# Add Texture
sun.textures.append(rc.Texture.from_image(rc.resources.img_colorgrid))

# Create Scene
scene = rc.Scene(meshes=sun, bgColor=(0,0,0))
scene.camera.projection.z_far = 20


@window.event
def on_draw():
    sun.rotation.y += 0.5
    earth.rotation.y += 0.5
    empty_merkury.rotation.y += 2
    empty_venus.rotation.y += 1.5
    empty_earth.rotation.y += 1
    empty_mars.rotation.y += 0.75
    empty_jupyter.rotation.y += 0.5

    with rc.default_shader:
        scene.draw()

pyglet.app.run()
