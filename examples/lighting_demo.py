import pyglet
import ratcave as rc
from itertools import cycle
import math

# Create Window
window = pyglet.window.Window()
fbo_shadow = rc.FBO(texture=rc.DepthTexture(width=2048, height=2048))



cam = rc.default_camera
cam.tt = 0.
def update(dt):
    # for mesh in [monkey, monkey2, monkey3]:
    #     mesh.rotation.y += 120. * dt
    cam.tt += dt
    cam.position.x = math.sin(cam.tt * 1.5)
pyglet.clock.schedule(update)

# Insert filename into WavefrontReader.
obj_filename = rc.resources.obj_primitives
obj_reader = rc.WavefrontReader(obj_filename)

plane = obj_reader.get_mesh('Plane')
plane.position.xyz = 0, 0, -5
plane.rotation.x = 0
plane.scale.xyz = 8
plane.uniforms['spec_weight'] = 0
plane.uniforms['flat_shading'] = False
plane.uniforms['diffuse'] = .8, .8, .6

plane.textures.append(fbo_shadow.texture)

# Create Mesh
print(rc.Mesh.__mro__)
monkey = obj_reader.get_mesh("Monkey", position=(0, 0, -3), name='flat')
monkey.uniforms['flat_shading'] = True
monkey.uniforms['diffuse'] = (.55,) * 3

monkey2 = obj_reader.get_mesh("Monkey", position=(0, 0, -3), name='diffuse')
monkey2.uniforms['flat_shading'] = False
monkey2.uniforms['spec_weight'] = 0

monkey3 = obj_reader.get_mesh("Monkey", position=(0, 0, -3), name='specular')
monkey3.uniforms['flat_shading'] = False
monkey3.uniforms['spec_weight'] = 30

monkey4 = obj_reader.get_mesh("Monkey", position=(0, 0, -3), name='specular')
monkey4.uniforms['flat_shading'] = False
monkey4.uniforms['spec_weight'] = 30

meshes = cycle([monkey, monkey2, monkey3, monkey4, rc.EmptyEntity()])
mesh = [next(meshes)]


def change_mesh(dt):
    mesh[0] = next(meshes)
pyglet.clock.schedule_interval(change_mesh, 4)


@window.event
def on_draw():
    rc.clear_color(*plane.uniforms['diffuse'])
    if mesh[0] == monkey4:
        with rc.default_shader, fbo_shadow, rc.default_light, cam, rc.default_states:
            window.clear()
            mesh[0].draw()

    with rc.default_shader, rc.default_states, cam:

        mesh[0].draw()
        print(mesh[0].name)
        plane.textures = [fbo_shadow.texture] if mesh[0] == monkey4 else []
        plane.draw()
pyglet.app.run()