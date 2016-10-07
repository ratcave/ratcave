.. ratCAVE documentation master file, created by
   sphinx-quickstart on Tue Sep  8 18:58:17 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ratCAVE's documentation!
===================================


ratCAVE is a Python package for displaying 3D Graphics.
It was inspired by a Virtual Reality CAVE Setup for rodents in a neuroscience lab in Munich, Germany, and was meant
to make the creation of 3D experiments simple and accessible.

ratCAVE has since evolved into a standalone wrapper for modern OpenGL constructs, like programmable shaders,
environment mapping, and deferred rendering.  Because it wraps these OpenGL features directly, it also works with all
popular python OpenGL graphics engines, including Pyglet, PsychoPy, and PyGame.

Finally, ratCAVE is written to reduce boilerplate code, in order to make writing simple 3D environments easy.  It does this using
many python features, including dictionary-like uniform assignment and context managers to bind OpenGL objects.

Features
========

Easy Installation
+++++++++++++++++
ratCAVE supports both Python 2 and Python 3, and can be installed via pip!::

   pip install ratcave

Supplied 3D Primitives
++++++++++++++++++++++

`Blender 3D's <https://www.blender.org/>`_ built-in primitives (Cone, Sphere, Cube, etc) come packaged with ratCAVE, making it easier to get started and prototype your 3D application.
A reader object for Blender's .obj Wavefront files is also included.

.. image:: _static/primitives.png

Supplied 3D Shaders
+++++++++++++++++++

ratCAVE is "batteries-included": You get diffuse shading, specular reflections, shadows, and even FXAA antialiasing in the
packaged shaders. These shaders are open-source and free to be edited and improved!

.. image:: _static/shading_example.png


Pythonic Interface
++++++++++++++++++

FrameBuffer Context Managers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Normally, the OpenGL code to bind a framebuffer involves the following::


    glGetIntegerv(GL_VIEWPORT, old_viewport_size)
    glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, fbo_id)  # Rendering off-screen
    glViewport(0, 0, texture_width, texture_height)
    << Draw Scene Here >>
    glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
    glViewport(old_viewport_size)

In ratCAVE, this is a simple context manager::

    with fbo:
       scene.draw()


Shader Uniforms
~~~~~~~~~~~~~~~

OpenGL Shader Uniform creation and setting is also wrapped in a pythonic way::

    sphere.uniforms['diffuse_color'] = [1., 0., 0.]  # RGB values



System Requirements
-------------------
At the moment, ratCAVE's shaders require OpenGL 3.3, though this is planned to change in future releases.  If you'd like to use
ratCAVE and don't have a graphics driver that supports OpenGL 3.3, however, you can already load your own shaders and it will
work fine.




Table of Contents:
++++++++++++++++++

.. toctree::
   :maxdepth: 2

   introduction
   tutorials
   ratcave

* :ref:`genindex`

