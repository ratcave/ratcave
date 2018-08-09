import pyglet
import ratcave as rc
import numpy as np

np.set_printoptions(suppress=True, precision=4)

window = pyglet.window.Window()

cube = rc.Mesh.from_primitive('Cube')
cube.position.z = -3
cube.scale.xyz = .5
# cube.visible = False

collider = rc.ColliderSphere(visible=True, position=(0, 0, -.2))
collider.parent = cube

sphere = rc.Mesh.from_primitive('Sphere', position=(1.01, 0, 0))
sphere.scale.xyz = 1.00, 1, 1
sphere.parent = cube
sphere.collider = rc.ColliderSphere(visible=True, position=(0, 0, 0))



def update(dt):
    cube.rotation.y += 60 * dt
    print(np.subtract(cube.position_global, sphere.position_global),
          sphere.collider.collides_with(cube)
          )

pyglet.clock.schedule(update)


@window.event
def on_draw():
    window.clear()
    with rc.default_shader, rc.default_states, rc.default_camera:
        for mesh in cube:
            mesh.draw()


pyglet.app.run()