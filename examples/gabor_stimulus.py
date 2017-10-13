import pyglet
import ratcave as rc
import time
import math

vert_shader = """
 #version 330

 layout(location = 0) in vec3 vertexPosition;
 layout(location = 2) in vec2 uvTexturePosition;
 uniform mat4 projection_matrix, view_matrix, model_matrix;
 out vec2 texCoord;


 void main()
 {
     gl_Position = projection_matrix * view_matrix * model_matrix * vec4(vertexPosition.xyz,  1.0);
     texCoord = uvTexturePosition;
 }
 """

frag_shader = """
 #version 330
 in vec2 texCoord;
 out vec4 final_color;
 uniform vec3 diffuse;
 float brightness;
 uniform float width;

 float pi = 3.14159;
 float mean = 0.5;
 float std = .1;
 uniform float theta;

 void main()
 {
    brightness = sin(texCoord.x / width + theta) / 2.; // Sine wave
    brightness *= exp(-.5 * pow(texCoord.x - mean, 2) / pow(std, 2)); // x-gaussian
    brightness *= exp(-.5 * pow(texCoord.y - mean, 2) / pow(std, 2)); // y-gaussian
    brightness += .5;  // Add grey value
    final_color = vec4(vec3(brightness), 1.) ;
    //final_color = vec4(texCoord, 0., 1.);
 }
 """

shader = rc.Shader(vert=vert_shader, frag=frag_shader)

# Create window and OpenGL context (always must come first!)


# Load Meshes and put into a Scene
plane = rc.gen_fullscreen_quad()
plane.scale.x = .5
plane.position.x = -.5
plane.uniforms['theta'] = 0.
plane.uniforms['width'] = .04

plane2 = rc.gen_fullscreen_quad()
plane2.scale.x = .5
plane2.position.x = .5
plane2.uniforms['theta'] = 0.
plane2.uniforms['width'] = .01

window = pyglet.window.Window(fullscreen=True)

scene = rc.Scene(meshes=[plane, plane2], bgColor=(.5, .5, .5))
scene.gl_states = scene.gl_states[:-1]
# scene.camera.projection = rc.OrthoProjection()
scene.camera.projection.fov_y = 140.
scene.camera.projection.match_aspect_to_viewport()# = window.width / window.height
# rc.PerspectiveProjection.match_aspect_to_viewport()


# Draw Function
@window.event
def on_draw():
    with shader:
        scene.draw()


def update(dt):
    plane.uniforms['theta'] += dt * 7.
    plane2.rotation.z += dt * 50.


pyglet.clock.schedule(update)


# Pyglet's event loop run function
pyglet.app.run()