import pyglet
import ratcave as rc
import math

reader = rc.WavefrontReader(rc.resources.obj_primitives)

torus = reader.get_mesh('Torus', position=(0, 0.0, -1))
monkey = reader.get_mesh('MonkeySmooth', position=(1, 0, -1))
monkey.orientation0 = 0, 0, -1
monkey.look_at(*torus.position.xyz)

scene = rc.Scene(meshes=[torus, monkey])
cam = scene.camera
cam.position.z = 1
# cam.rotation.x = -45

shader = rc.Shader.from_file(*rc.resources.genShader)

win = pyglet.window.Window()

@win.event
def on_draw():
    with shader:
        scene.draw()

tt = 0.
def update(dt):
    global tt
    tt += dt

    cam.position.y = math.sin(tt) * 2
    cam.look_at(*monkey.position.xyz)
    print(cam.orientation)
pyglet.clock.schedule(update)
pyglet.app.run()