from os.path import split, join
from ctypes import byref
from utils import *
import __mixins as mixins
from __camera import Camera
from __shader import Shader
from __mesh import fullscreen_quad



shader_path = join(split(__file__)[0], 'shaders')

def create_opengl_object(gl_gen_function):
    """Returns int pointing to an OpenGL texture"""
    texture_id = gl.GLuint(1)
    gl_gen_function(1, byref(texture_id))  # Create Empty Texture
    return texture_id.value  # Use handle for rest


def create_fbo(texture_type, width, height, texture_slot=0, color=True, depth=True, grayscale=False):

    assert color or depth, "at least one of the two data types, color or depth, must be set to True."

    # Make a texture and bind it.
    gl.glActiveTexture(gl.GL_TEXTURE0 + texture_slot)
    texture = create_opengl_object(gl.glGenTextures)  # Create a general texture
    gl.glBindTexture(texture_type, texture)  # Bind it.

    # Apply texture settings for interpolation behavior (Required)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameterf(texture_type, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    if texture_type == gl.GL_TEXTURE_CUBE_MAP:
        gl.glTexParameterf(texture_type, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    # Generate empty texture(s)
    color_type = gl.GL_R8 if grayscale else gl.GL_RGBA
    internal_format = gl.GL_DEPTH_COMPONENT if depth and not color else color_type

    color_type = gl.GL_RED if grayscale else gl.GL_RGBA
    pixel_format = gl.GL_DEPTH_COMPONENT if depth and not color else color_type

    if texture_type == gl.GL_TEXTURE_2D:
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal_format, width, height, 0,
                pixel_format, gl.GL_UNSIGNED_BYTE, 0)
    elif texture_type == gl.GL_TEXTURE_CUBE_MAP:
        # Generate blank textures, one for each cube face.
        for face in range(0, 6):
            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face, 0, internal_format,
                            width, height, 0, pixel_format, gl.GL_UNSIGNED_BYTE, 0)

    # Create FBO and bind it.
    fbo = create_opengl_object(gl.glGenFramebuffersEXT)
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, fbo)

    # Set Draw and Read locations for the FBO (mostly, turn off if not doing any color stuff)
    if depth and not color:
        gl.glDrawBuffer(gl.GL_NONE)  # No color in this buffer
        gl.glReadBuffer(gl.GL_NONE)

    # Bind texture to FBO.
    attachment_point = gl.GL_DEPTH_ATTACHMENT_EXT if depth and not color else gl.GL_COLOR_ATTACHMENT0_EXT
    attached_texture2D_type = gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X if texture_type==gl.GL_TEXTURE_CUBE_MAP else gl.GL_TEXTURE_2D
    gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, attachment_point, attached_texture2D_type, texture, 0)

    # create a render buffer as our temporary depth buffer, bind it, and attach it to the fbo
    if color and depth:
        renderbuffer = create_opengl_object(gl.glGenRenderbuffersEXT)
        gl.glBindRenderbufferEXT(gl.GL_RENDERBUFFER_EXT, renderbuffer)
        gl.glRenderbufferStorageEXT(gl.GL_RENDERBUFFER_EXT, gl.GL_DEPTH_COMPONENT24, width, height)
        gl.glFramebufferRenderbufferEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_DEPTH_ATTACHMENT_EXT, gl.GL_RENDERBUFFER_EXT,
                                        renderbuffer)

    # check FBO status (warning appears for debugging)
    FBOstatus = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
    if FBOstatus != gl.GL_FRAMEBUFFER_COMPLETE_EXT:
        raise BufferError("GL_FRAMEBUFFER_COMPLETE failed, CANNOT use FBO.\n{0}\n".format(FBOstatus))

    #Unbind FBO and return it and its texture
    gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)

    return fbo, texture


class Scene:
    """Returns a Scene object.  Scenes manage rendering of Meshes, Lights, and Cameras."""

    # Class Variables
    cubemap_camera_rotation_order = list(enumerate([[180, 90, 0], [180, -90, 0], [90, 0, 0], [-90, 0, 0], [180, 0, 0], [0, 0, 180]]))
    player = None
    grayscale = False

    # General, Normal Shader
    genShader = Shader(open(join(shader_path, 'combShader.vert')).read(),
                    open(join(shader_path, 'combShader.frag')).read())

    # CubeMapping Shader
    _cubeFboID, _cubeTexture = None, None
    __cubeCamera = Camera(fov_y=90., aspect=1.)  # camera for cubemapping

    # Shadows
    _shadowFboID = None
    __shadowCamera = Camera(fov_y=60., aspect=1.)  # camera for shadows
    shadowShader = Shader(open(join(shader_path, 'shadowShader.vert')).read(),
                        open(join(shader_path, 'shadowShader.frag')).read())

    _aaFboID, _aaTexture = None, None
    aaShader = Shader(open(join(shader_path, 'antialiasShader.vert')).read(),
                        open(join(shader_path, 'antialiasShader.frag')).read())

    # Viewport measurements
    _viewport = [0, 0, 1280, 720] # None  # TODO: Find out how to properly set a default viewport

    # Lights
    light = mixins.Physical()

    def __init__(self, *meshes):
        """Initialize the Scene object using Meshes as input../s"""

        self.camera = Camera()  # create a default Camera object
        self.bgColor = (0.0, 0.0, 0.0)

        # Initialize List of all Meshes to draw
        self.meshes = list(meshes)

    def render_shadow(self):

        if not Scene._shadowFboID:
            Scene._shadowFboID, Scene._shadowTexture = create_fbo(gl.GL_TEXTURE_2D, 2048, 2048, texture_slot=5, color=False, depth=True)  # Pyglet interferes with fbo creation if done too early.

        # render to Frame Buffer Object (FBO) (depth values only)
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, Scene._shadowFboID)  # Rendering off-screen

        ###### Setup Matrices to look from Light Position ###########
        gl.glViewport(0, 0, 2048, 2048)
        Scene.__shadowCamera.rotation = self.camera.rotation
        Scene.__shadowCamera.position = Scene.light.position
        ###################################

        # Render Scene
        self._draw(Scene.__shadowCamera, Scene.shadowShader)

        # Reset Render settings to normal and unbind FBO
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)
        gl.glViewport(*Scene._viewport)

    def render_to_cubemap(self):
        """
        Renders the scene, 360 degrees around a camera, to a mesh "toMesh" from the perspective of "fromObject".
        Currently, window width and height must also be supplied.
        """
        if not Scene._cubeFboID:
            Scene._cubeFboID, Scene._cubeTexture = create_fbo(gl.GL_TEXTURE_CUBE_MAP, 2048, 2048, texture_slot=0, color=True, depth=True, grayscale=Scene.grayscale)

        # Bind to Cubemap Framebuffer to render directly to the cubemap texture.
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, Scene._cubeFboID)

        # Assign new camera position for 360-degree shot
        # (this must be pre-set to a square 90-degree camera)
        Scene.__cubeCamera.position = Scene.player.position
        gl.glViewport(0, 0, 2048, 2048)  # Change viewport to square texture, as big as possible.

        # Render to Each Face of Cubemap texture, rotating the camera in the correct direction before each shot.
        for face, rotation in Scene.cubemap_camera_rotation_order:  # Created as class variable for performance reasons.
            Scene.__cubeCamera.rotation = rotation
            gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT,
                                         gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + face,
                                         Scene._cubeTexture,  0)  # Select face of cube texture to render to.
            self._draw(Scene.__cubeCamera, Scene.genShader)  # Render

        # Restore previous camera position and lens settings
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)  # Unbind cubemap Framebuffer (so rendering to screen can be done)
        gl.glViewport(*Scene._viewport)  # Reset Viewport

    def render_to_antialias(self):

        if not Scene._aaFboID:
            Scene._aaFboID, Scene._aaTexture = create_fbo(gl.GL_TEXTURE_2D, 1280, 720, texture_slot=0, color=True, depth=True, grayscale=Scene.grayscale)

        # Bind to Cubemap Framebuffer to render directly to the cubemap texture.
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, Scene._aaFboID)
        self._draw(self.camera, Scene.genShader)
        gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, 0)  # Unbind cubemap Framebuffer (so rendering to screen can be done)

        # Render Scene onto a fullscreen quad, after antialiasing.
        gl.glViewport(*Scene._viewport)  # Reset Viewport
        self._render_to_fullscreen_quad(Scene.aaShader, Scene._aaTexture)

    def resize(self, width, height):
        """Call when resizing window, inputting new window width and height."""
        Scene._viewport = [0, 0, width, height]
        gl.glViewport(*Scene._viewport)  # resizes viewport to fill screen.
        self.camera.aspect = width / float(height)  # Rescale aspect ratio

    def draw(self):
        """General draw method."""
        self._draw(self.camera, Scene.genShader)

    def _render_to_fullscreen_quad(self, shader, texture):
        """Fairly general method, to be converted to more general deferred shading rendering method."""
        gl.glClearColor(self.bgColor[0], self.bgColor[1], self.bgColor[2], 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        shader.bind()
        shader.uniformf('frameBufSize', *Scene._viewport[2:])
        shader.uniformi('image_texture', 0)
        shader.uniformi('grayscale', int(Scene.grayscale))
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        fullscreen_quad.render()
        shader.unbind()
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    def _draw(self, camera, shader):
        """Draws the scene. Call this method in your Window's Draw Loop."""

        # Enable 3D OpenGL
        gl.glEnable(gl.GL_DEPTH_TEST)
        #gl.glEnable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP)
        gl.glEnable(gl.GL_TEXTURE_2D)

        # Clear and Refresh Screen
        gl.glClearColor(self.bgColor[0], self.bgColor[1], self.bgColor[2], 1.)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Bind Shader
        shader.bind()

        # Send Uniforms that are constant across meshes.
        shader.uniform_matrixf('view_matrix', camera._view_matrix)
        shader.uniform_matrixf('projection_matrix', camera._projection_matrix)
        shader.uniformf('light_position', *Scene.light.position)
        shader.uniformf('camera_position', *camera.position)

        shader.uniformi('hasShadow', int(Scene._shadowFboID is not False))
        shader.uniformi('ShadowMap', 5)
        shader.uniform_matrixf('shadow_projection_matrix', Scene.__shadowCamera._projection_matrix)
        shader.uniform_matrixf('shadow_view_matrix', Scene.__shadowCamera._view_matrix)

        shader.uniformi('grayscale', int(Scene.grayscale))

        # Draw each visible mesh in the scene.
        for mesh in self.meshes:

            if mesh.visible:

                # Send Model and Normal Matrix to shader.
                shader.uniform_matrixf('model_matrix_global', mesh.world._model_matrix)
                shader.uniform_matrixf('model_matrix_local', mesh.local._model_matrix)
                shader.uniform_matrixf('normal_matrix_global', mesh.world._normal_matrix)
                shader.uniform_matrixf('normal_matrix_local', mesh.local._normal_matrix)


                if shader == Scene.genShader:
                    # Change Material to Mesh's
                    shader.uniformf('ambient', *mesh.material.ambient.rgb)
                    shader.uniformf('diffuse', *mesh.material.diffuse.rgb)
                    shader.uniformf('spec_color', *mesh.material.spec_color.rgb)
                    shader.uniformf('spec_weight', mesh.material.spec_weight)
                    shader.uniformf('opacity', mesh.material.diffuse.a)
                    shader.uniformi('hasLighting', mesh.lighting)

                    # Bind Cubemap if mesh is to be rendered with the cubemap.
                    shader.uniformi('hasCubeMap', int(bool(mesh.cubemap)))
                    if mesh.cubemap:
                        shader.uniformf('playerPos', *vec(Scene.player.position))
                        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, Scene._cubeTexture)  # No ActiveTexture needed, because only one Cubemap.

                    # Bind Textures and apply Material
                    shader.uniformi('hasTexture', int(bool(mesh.texture)))
                    if mesh.texture:
                        gl.glActiveTexture(gl.GL_TEXTURE2)
                        gl.glBindTexture(gl.GL_TEXTURE_2D, mesh.texture.id)
                        shader.uniformi('ImageTextureMap', 2)
                        gl.glActiveTexture(gl.GL_TEXTURE0)

                # Draw the Mesh
                mesh.render()  # Bind VAO.

        # Unbind Shader
        shader.unbind()