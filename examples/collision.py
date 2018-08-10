import pyglet
import ratcave as rc
import numpy as np

np.set_printoptions(suppress=True, precision=4)

window = pyglet.window.Window()

cube = rc.Mesh.from_primitive('Cube')
cube.position.z = -3
cube.scale.xyz = .3, .3, .3
# cube.visible = False

cube.collider = rc.ColliderCylinder(visible=True, ignore_axis=1)


sphere = rc.Mesh.from_primitive('Sphere', position=(0.99, 0, 0))
sphere.scale.xyz = 1.00, 1, 2
sphere.parent = cube
sphere.collider = rc.ColliderSphere(visible=True, position=(0, 0, 0))


tt = 0.
def update(dt):
    global tt
    tt += dt
    sphere.position.x = np.sin(3. * tt) * 3
    sphere.rotation.y += 25 * dt
    cube.rotation.y += 60 * dt
    sphere.uniforms['diffuse'] = (0., 1., 0.) if sphere.collider.collides_with(cube) else (0., 0., 1.)
    cube.uniforms['diffuse'] = (0., 1., 0.) if cube.collider.collides_with(sphere) else (0., 0., 1.)
    print(sphere.position.xyz)
    # print(sphere.collider.collides_with(cube), cube.collider.collides_with(sphere))

pyglet.clock.schedule(update)


@window.event
def on_draw():
    window.clear()
    with rc.default_shader, rc.default_states, rc.default_camera:
        for mesh in cube:
            mesh.draw()


pyglet.app.run()