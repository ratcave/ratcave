import pyglet
import ratcave as rc
import time
import math

vert_shader = """
 #version 330

 layout(location = 0) in vec3 vertexPosition;
 uniform mat4 projection_matrix, view_matrix, model_matrix;
 out vec4 vVertex;

 void main()
 {
     vVertex = model_matrix * vec4(vertexPosition, 1.0);
     gl_Position = projection_matrix * view_matrix * vVertex;
 }
 """

frag_shader = """
 #version 330
 out vec4 final_color;
 uniform vec3 diffuse;
 void main()
 {
     final_color = vec4(diffuse, 1.);
 }
 """

shader = rc.Shader(vert=vert_shader, frag=frag_shader)

# Create window and OpenGL context (always must come first!)
window = pyglet.window.Window()

# Load Meshes and put into a Scene
obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)
torus = obj_reader.get_mesh('Torus', position=(0, 0, -2))
torus.uniforms['diffuse'] = [.5, .0, .8]

scene = rc.Scene(meshes=[torus])

# Constantly-Running mesh rotation, for fun
def update(dt):
    torus.rotation.y += 20. * dt
pyglet.clock.schedule(update)


def update_color(dt):
    torus.uniforms['diffuse'][0] = 0.5 * math.sin(time.clock() * 10) + .5
pyglet.clock.schedule(update_color)


# Draw Function
@window.event
def on_draw():
    with shader:
        scene.draw()


# Pyglet's event loop run function
pyglet.app.run()