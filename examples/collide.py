import pyglet
from pyglet.window import key#, MouseCursor
from pyglet.window import mouse
import ratcave as rc
import numpy as np

# Create Window
window = pyglet.window.Window(800, 600)
keys = key.KeyStateHandler()
window.push_handlers(keys)
window.set_mouse_visible(True)

def update(dt):
    pass
pyglet.clock.schedule(update)

# Insert filename into WavefrontReader.
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)

# Create Meshes
monkey = obj_reader.get_mesh("Monkey", scale=2, position=(0, 0, -6))

scale = np.linalg.norm(monkey.vertices[:, :3], axis=1).max()

sphere = obj_reader.get_mesh("Sphere",  position=(0, 0, -6), scale=scale)
sphere.draw_mode = sphere.points
# monkey.add_child(sphere)


# Create Collision Sphere
col_sphere = rc.SphereCollisionChecker(mesh=monkey, visible=True)

# Create Scene
scene = rc.Scene(meshes=[monkey, sphere], bgColor=(0,0,0))
scene.camera.projection.z_far = 20

def move_camera(dt):
    speed = 3
    if keys[key.LEFT]:
        sphere.position.y -= speed * dt
    if keys[key.RIGHT]:
        sphere.position.y += speed * dt
pyglet.clock.schedule(move_camera)

@window.event
def on_mouse_press(x, y, button, modifiers):
    if button == mouse.LEFT:
        # adjust coordinates
        x = (x-400)/100
        y = (y-300)/100
        collide = col_sphere.collides_with(xyz=(x,y,-6))

        if collide:
            # change color on collision
            monkey.uniforms['diffuse'][0] = np.random.randint(1, high = 5)
            monkey.uniforms['diffuse'][1] = np.random.randint(1, high = 5)
        print('The left mouse button was pressed.', collide)

@window.event
def on_draw():
    # sphere.rotation.y += 0.5
    with rc.default_shader:
        scene.draw()

pyglet.app.run()
