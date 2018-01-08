import pyglet
import ratcave as rc
import math, time


window = pyglet.window.Window(resizable=True)

# Assemble the Virtual Scene
obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)
sphere = obj_reader.get_mesh("Sphere", position=(0, 0, 2), scale=0.2)
sphere.uniforms['diffuse'] = 1, 0, 0

cube = obj_reader.get_mesh("Cube", position=(0, 0, 0), scale=0.2)
cube.uniforms['diffuse'] = 1, 1, 0

# virtual_scene = rc.Scene(meshes=[sphere, cube], bgColor=(0., 0., 1.))
virtual_scene = rc.Scene(meshes=[cube, sphere], bgColor=(0., 0., 1.))
virtual_scene.light.position.xyz = 0, 3, -1


cube_camera = rc.Camera(projection=rc.PerspectiveProjection(fov_y=90, aspect=1.))
virtual_scene.camera = cube_camera

# Assemble the Projected Scene
monkey = obj_reader.get_mesh("Monkey", position=(0, 0, -1), scale=0.8)
screen = obj_reader.get_mesh("Plane", position=(0, 0, 1), rotation=(1.5, 180, 0))

projected_scene = rc.Scene(meshes=[monkey, screen, sphere, cube], bgColor=(1., .5, 1.))
projected_scene.light.position = virtual_scene.light.position
projected_scene.camera = rc.Camera(position=(0, 4, 0), rotation=(-90, 0, 0))
projected_scene.camera.projection.z_far = 6

# Create Framebuffer and Textures
cube_texture = rc.texture.TextureCube(width=1024, height=1024)  # this is the actual cube texture
cube_fbo = rc.FBO(texture=cube_texture)
screen.textures.append(cube_texture)



clock = 0.
def update(dt):
    global clock
    clock += dt
    monkey.position.x = math.sin(1.3 * clock)
    virtual_scene.camera.position.xyz = monkey.position.xyz
    screen.uniforms['playerPos'] = virtual_scene.camera.position.xyz
pyglet.clock.schedule(update)


@window.event
def on_draw():
    with rc.default_shader:
        with cube_fbo as fbo:
            virtual_scene.draw360_to_texture(fbo.texture)
        projected_scene.draw()


pyglet.app.run()