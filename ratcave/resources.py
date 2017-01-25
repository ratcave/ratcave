
from os import path
from .shader import Shader

"""
Here are some sample obj files for prototyping your app!
"""

# This is an easy way to get the filepaths of some oft-used resources for displaying simple scenes.

resource_path = path.join(path.split(__file__)[0], '..', 'assets')

# Images
img_uvgrid = path.join(resource_path,'uvgrid.png')
img_colorgrid = path.join(resource_path, 'colorgrid.png')
img_white = path.join(resource_path, 'white.png')

# Meshes
obj_primitives = path.join(resource_path, 'primitives.obj')
obj_grid3D = path.join(resource_path, 'grid3D.obj')


# Shaders
shader_path = path.join(path.split(__file__)[0], '..', 'shaders')

# General, Normal Shader
genShader = Shader(open(path.join(shader_path, 'combShader.vert')).read(),
                   open(path.join(shader_path, 'combShader.frag')).read())

shadowShader = Shader(open(path.join(shader_path, 'shadowShader.vert')).read(),
                      open(path.join(shader_path, 'shadowShader.frag')).read())

deferredShader = Shader(open(path.join(shader_path, 'basicDeferred.vert')).read(),
                  open(path.join(shader_path, 'basicDeferred.frag')).read())

