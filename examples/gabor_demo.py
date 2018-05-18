import pyglet
import ratcave as rc


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
 }
 """

shader = rc.Shader(vert=vert_shader, frag=frag_shader)
plane = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh('Plane')#gen_fullscreen_quad()
plane.scale.xyz = .2
plane.position.xyz = 0, 0, -1
plane.uniforms['theta'] = 0.
plane.uniforms['width'] = .01

window = pyglet.window.Window(fullscreen=True)

scene = rc.Scene(meshes=[plane], bgColor=(.5, .5, .5), camera=rc.Camera(projection=rc.OrthoProjection()))

# Draw Function
@window.event
def on_draw():
    with shader:
        scene.draw()


def update(dt):
    plane.uniforms['theta'] += dt * 7.
pyglet.clock.schedule(update)


# Pyglet's event loop run function
pyglet.app.run()