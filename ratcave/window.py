from __future__ import absolute_import


import pyglet.gl as gl

from .utils import gl as ugl



fbos = {'shadow': ugl.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=5, color=False, depth=True),
        'vrshadow': ugl.create_fbo(gl.GL_TEXTURE_2D, texture_size, texture_size, texture_slot=6, color=False, depth=True),
        'cube': ugl.create_fbo(gl.GL_TEXTURE_CUBE_MAP, texture_size*2, texture_size*2, texture_slot=0, color=True, depth=True, grayscale=self.grayscale),
        'antialias': ugl.create_fbo(gl.GL_TEXTURE_2D, aa_texture_size, aa_texture_size, texture_slot=0, color=True, depth=True, grayscale=self.grayscale)
        }
