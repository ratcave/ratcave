import pyglet
import ratcave as rc

# Create Window
window = pyglet.window.Window(resizable=True)

def update(dt):
    pass
pyglet.clock.schedule(update)

# Insert filename into WavefrontReader.
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)

# Create Meshes
sun = obj_reader.get_mesh("Sphere")
merkury = obj_reader.get_mesh("Sphere", scale =.1)
venus   = obj_reader.get_mesh("Sphere", scale =.2)
earth   = obj_reader.get_mesh("Sphere", scale =.2)
mars    = obj_reader.get_mesh("Sphere", scale =.2)
jupyter = obj_reader.get_mesh("Sphere", scale =.4)
moon = obj_reader.get_mesh("Sphere", scale =.5)

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
sun.rotation.x = 90
sun.position.xyz = 0, 0, -12

merkury.position.z += 1
venus.position.z += 2
earth.position.z += 3
mars.position.z += 4
jupyter.position.z += 5

moon.position.z += 1

# Create Scene
scene = rc.Scene(meshes=sun)

@window.event
def on_draw():
    with rc.default_shader:
        sun.rotation.y += 0.5
        empty_merkury.rotation.y += 2
        empty_venus.rotation.y += 1.5
        empty_earth.rotation.y += 1
        empty_mars.rotation.y += 0.75
        empty_jupyter.rotation.y += 0.5

        earth.rotation.y += 0.5

        empty_merkury.update()
        empty_venus.update()
        empty_earth.update()
        empty_mars.update()
        empty_jupyter.update()

        merkury.update()
        venus.update()
        earth.update()
        mars.update()
        jupyter.update()
        moon.update()

        scene.draw()

pyglet.app.run()
