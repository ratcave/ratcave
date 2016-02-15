from __future__ import absolute_import
from os import path

import pyglet.gl as gl

from .utils.shader import Shader
from .utils import gl as ugl
from . import mesh

"""
Here are some sample obj files for prototyping your app!
"""

# This is an easy way to get the filepaths of some oft-used resources for displaying simple scenes.

resource_path = path.join(path.split(__file__)[0],'assets')

# Images
img_uvgrid = path.join(resource_path,'uvgrid.png')
img_colorgrid = path.join(resource_path, 'colorgrid.png')

# Meshes
obj_primitives = path.join(resource_path, 'primitives.obj')
obj_grid3D = path.join(resource_path, 'grid3D.obj')


# Shaders
shader_path = path.join(path.split(__file__)[0], 'shaders')

# General, Normal Shader
genShader = Shader(open(path.join(shader_path, 'combShader.vert')).read(),
                   open(path.join(shader_path, 'combShader.frag')).read())

shadowShader = Shader(open(path.join(shader_path, 'shadowShader.vert')).read(),
                      open(path.join(shader_path, 'shadowShader.frag')).read())

aaShader = Shader(open(path.join(shader_path, 'antialiasShader.vert')).read(),
                  open(path.join(shader_path, 'antialiasShader.frag')).read())


# FBOS
texture_size = 1024
aa_texture_size = 1024

# shadowFBO = ugl.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=5,
#                            color=False, depth=True)
#
# vrShadowFBO = ugl.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=6,
#                              color=False, depth=True)
#
# cubeFBO = ugl.create_fbo(gl.GL_TEXTURE_CUBE_MAP, texture_size*2, texture_size*2, texture_slot=0,
#                          color=True, depth=True, grayscale=False)
#
# antialiasFBO = ugl.create_fbo(gl.GL_TEXTURE_2D, aa_texture_size, aa_texture_size, texture_slot=0,
#                               color=True, depth=True, grayscale=False)


# Meshes
fullscreen_quad_data = mesh.MeshData([-1, -1, 0, -1, 1, 0, 1, 1, 0,
                                 -1, -1, 0,  1, 1, 0, 1, -1, 0],
                                [0, 1, 2, 0, 2, 3],
                                normals=[0, 0, -1]*6,
                                # NEED NORMALS TO RENDER PROPERLY NOW!!
                                texture_uv=[0, 0, 0, 1, 1, 1,
                                            0, 0, 1, 1, 1, 0])
fullscreen_quad = mesh.Mesh(fullscreen_quad_data)
fullscreen_quad.update_matrices()