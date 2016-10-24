Tutorial 4: Using Cubemapping to Render a CAVE VR System
++++++++++++++++++++++++++++++++++++++++++++++++++++++++


CAVE VR relies on position updates from head trackers to render a virtual scene from the subject's perspective in virtual space, then to warp a video projection so that to the viewer the virtual scene appears to be geometrically correct  We use a cubemapping approach to do just that:
  - Two different :py:class:`.Scene` objects are used:
    - a virtual Scene, which contains the virtual environment to be cubemapped which is rendered from the subject's perspective (meaning, the camera goes where the subject is)
    - a "real" Scene, which contains just the model (also a :py:class:`.Mesh`) of the screen on which the VR is being projected, seen from the perspective of teh video projector.

While this is difficult to show without having an actual tracking system, we'll illustrate this effect and the code needed to run it by making an animation:

.. warning:: This tutorial assumes knowledge gained from the previous tutorials.  If you are just getting started, it's recommended to start from Tutorial 1!

Import Pyglet and Ratcave, and Start the Window and OpenGL Context
------------------------------------------------------------------

At the beginning of the script::

    import pyglet
    import ratcave as rc

    window = pyglet.window.Window(resizable=True)

At the end of the script::

    pyglet.app.run()

Create the Virtual Scene
------------------------

Let's say that our virtual scene contains a red sphere and a cyan cube::

    obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)
    sphere = obj_reader.get_mesh("Sphere", position=(0, 0, 2), scale=0.2)
    sphere.uniforms['diffuse'] = 1, 0, 0

    cube = obj_reader.get_mesh("Cube", position=(0, 0, 0), scale=0.2)
    cube.uniforms['diffuse'] = 1, 1, 0

    # Put inside a Scene
    virtual_scene = rc.Scene(meshes=[sphere, cube])

Note that we have one object at the origin (0, 0, 0).  Since our light is also at 0,0,0 by default, this may affect how things appear.  Let's move the scene's light::

    virtual_scene.light.position = 0, 3, -1

Create the Projected Scene
--------------------------

The Projected Scene is what is actually sent to the display.  It will contain the screen (or rodent arena, if you're in a rodent neuroscience lab like us!).  Here, let's just use a flat plane to be used as our screen, and use a monkey to show where the subject is looking from (note: the subject isn't necessary for actual VR, it's just used here for illustration of the cubemapping approach).  ::

    monkey = obj_reader.get_mesh("Monkey", position=(0, 0, -1), scale=0.8)
    screen = obj_reader.get_mesh("Plane", position=(0, 0, 1), rotation=(1.5, 180, 0))

    projected_scene = rc.Scene(meshes=[monkey, screen], bgColor=(1., 1., 1.))
    projected_scene.light.position = virtual_scene.light.position

To ensure that the cubemapped texture appears on the screen, the :py:func:`Mesh.cubemap` flag needs to be set to True::

    screen.cubemap = True

Setting Your Cameras
--------------------

A Camera used for Cubemapping
=============================

Cubemapping involves rendering an image from six different angles: up, down, left, right, forward, and backward, and stitching each of these six images onto the faces of a cube (for more info, see http://www.nvidia.com/object/cube_map_ogl_tutorial.html).
For this algorithm to work, then, two of the :py:class:`.Camera`'s properties must be customized:

  - :py:func:`.Camera.aspect`: The camera's image must be square (meaning it's width-to-height aspect ratio must be 1.0)
  - :py:func:`.Camera.fov_y`: The camera must be able to see 90-degrees, so that the sides all match up.

Altering the camera to be useful for cubemapping is straightforward::

    cube_camera = rc.Camera(fov_y=90, aspect=1.)
    virtual_scene.camera = cube_camera

The Projector Camera
====================

In order to do CAVE VR, the camera you use to render the screen must exactly match not only the position and rotation of your video projector relative to the screen, but also the lens characteristics as well.
This requires some calibration and measuring on your part, which will differ based on your setup and hardware.  Since this is just a demo, let's just arbitrarily place the camera above the scene, looking down::

    projected_scene.camera = rc.Camera(position=(0, 4, 0), rotation=(-90, 0, 0), z_far=6)

The aspect of the camera should, ideally, match that of the window.  Let's do that here, using Pyglet's on_resize event handler so that it will happen automatically, even when the screen is resized::

    @window.event
    def on_resize(width, height):
        projected_scene.camera.aspect = width / float(height)


Create the OpenGL FrameBuffer and Cube Texture
----------------------------------------------

So far, we've always rendered our Scenes straight to the monitor.  However, we can also render to a texture!  This lets us do all kinds of image postprocessing effects, but here we'll just use it to update a cube texture, so the screen always has the latest VR image::

    cube_texture = rc.texture.TextureCube()  # this is the actual cube texture
    cube_fbo = rc.FBO(cube_texture)

All that's left is to apply the texture the screen::

    screen.texture = cube_texture

.. warning:: The built-in shader that comes with ratCAVE requires the subject's position to be sent to it throught the **playerPos** uniform.  This may be remedied in future releases, or can be changed in your own custom shaders.  To do this, use: screen.uniforms['playerPos'] = virtual_scene.camera.position

Move the Subject
----------------

Let's have the Monkey move left-to-right, just to illustrate what cubemapping does::

    import math, time
    def update(dt):
        monkey.x = math.sin(.3 * time.clock())
        virtual_scene.camera.position = monkey.position
        screen.uniforms['playerPos'] = virtual_scene.camera.position
    pyglet.clock.schedule(update)

.. note:: The uniforms currently don't update automatically, and should be explicitly changed.



Draw the Scenes
---------------

All that's left is for the scenes to be drawn. The virtual_scene should be drawn to the :py:Class:`.FBO`, and the projected_scene to the window.  To perform the rotations correctly and in the right order, a convenient :py:func:`Scene.draw360_to_texture` method has been supplied::

  @window.event
  def on_draw():
    with cube_fbo:
        virtual_scene.draw360_to_texture(cube_texture)
    projected_scene.draw()


Summary
-------

Here's the full code::

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

    virtual_scene = rc.Scene(meshes=[sphere, cube])
    virtual_scene.light.position = 0, 3, -1

    cube_camera = rc.Camera(fov_y=90, aspect=1.)
    virtual_scene.camera = cube_camera

    # Assemble the Projected Scene
    monkey = obj_reader.get_mesh("Monkey", position=(0, 0, -1), scale=0.8)
    screen = obj_reader.get_mesh("Plane", position=(0, 0, 1), rotation=(1.5, 180, 0))
    screen.cubemap = True

    projected_scene = rc.Scene(meshes=[monkey, screen, sphere, cube], bgColor=(1., 1., 1.))
    projected_scene.light.position = virtual_scene.light.position
    projected_scene.camera = rc.Camera(position=(0, 4, 0), rotation=(-90, 0, 0), z_far=6)

    # Create Framebuffer and Textures
    cube_texture = rc.texture.TextureCube()  # this is the actual cube texture
    cube_fbo = rc.FBO(cube_texture)
    screen.texture = cube_texture


    @window.event
    def on_resize(width, height):
        projected_scene.camera.aspect = width / float(height)


    def update(dt):
        monkey.x = math.sin(.3 * time.clock())
        virtual_scene.camera.position = monkey.position
        screen.uniforms['playerPos'] = virtual_scene.camera.position
    pyglet.clock.schedule(update)


    @window.event
    def on_draw():
        with cube_fbo:
            virtual_scene.draw360_to_texture(cube_texture)
        projected_scene.draw()


    pyglet.app.run()


PsychoPy Version
----------------

Here's the same scenario, done in PsychoPy::

    from psychopy import visual, event
    import ratcave as rc
    import math, time


    window = visual.Window()

    # Assemble the Virtual Scene
    obj_reader = rc.WavefrontReader(rc.resources.obj_primitives)
    sphere = obj_reader.get_mesh("Sphere", position=(0, 0, 2), scale=0.2)
    sphere.uniforms['diffuse'] = 1, 0, 0

    cube = obj_reader.get_mesh("Cube", position=(0, 0, 0), scale=0.2)
    cube.uniforms['diffuse'] = 1, 1, 0

    virtual_scene = rc.Scene(meshes=[sphere, cube])
    virtual_scene.light.position = 0, 3, -1

    cube_camera = rc.Camera(fov_y=90, aspect=1.)
    virtual_scene.camera = cube_camera

    # Assemble the Projected Scene
    monkey = obj_reader.get_mesh("Monkey", position=(0, 0, -1), scale=0.8)
    screen = obj_reader.get_mesh("Plane", position=(0, 0, 1), rotation=(1.5, 180, 0))
    screen.cubemap = True

    projected_scene = rc.Scene(meshes=[monkey, screen, sphere, cube], bgColor=(1., 1., 1.))
    projected_scene.light.position = virtual_scene.light.position
    projected_scene.camera = rc.Camera(position=(0, 4, 0), rotation=(-90, 0, 0), z_far=6)

    # Create Framebuffer and Textures
    cube_texture = rc.texture.TextureCube()  # this is the actual cube texture
    cube_fbo = rc.FBO(cube_texture)
    screen.texture = cube_texture

    # Main Loop
    while True:

        if 'escape' in event.getKeys():
            window.close()
            break

        monkey.x = math.sin(.3 * time.clock())
        virtual_scene.camera.position = monkey.position
        screen.uniforms['playerPos'] = virtual_scene.camera.position

        with cube_fbo:
            virtual_scene.draw360_to_texture(cube_texture)
        projected_scene.draw()
        window.flip()