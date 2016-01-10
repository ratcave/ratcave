Tutorial 3: Using Cubemapping to Render a CAVE VR System
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. warning:: This Tutorial is currently out of date.

CAVE VR relies on position updates from head trackers to render a virtual scene from the subject's perspective in virtual space, then to warp a video projection so that to the viewer the virtual scene appears to be geometrically correct  We use a cubemapping approach to do just that:
  - :py:class:`.Mesh` objects are placed into the virtual :py:class:`.Scene` object as in the previous two tutorials. However, this :py:class:`.Scene` is placed in the :py:attr:`.Window.virtual_scene` attribute, instead of the :py:attr:`.Window.active_scene` attribute.
  - The screen itself, being the thing that is actually projected by the display, is placed in as the :py:meth:`.Window.active_scene`.  This :py:class:`.Scene` contains 3D-Modeled version of the the projected surface as a :py:class:`.Mesh` object, and its :py:meth:`.Mesh.cubemap` attribute is set to True. The *Active Scene's* :py:class:`.Camera` is then set to be in the same position, rotation, and other properties as the projector itself.  Getting accurate measurements of your projection surface and projector can be challenging, so ratCAVE comes with a few console scripts to give you an idea of how this can be made to work (and, if you're from the Sirota lab at LMU, you can even use these scripts to automatically calibrate them both!).  Future versions will include a more general approach for different setups.
  - Each frame, the subject's position is taken from a tracker (for Motive/Optitrack users, we've included a :py:class:`.Optitrack` class for easily getting NatNet data, but any interface will work for this.) and set to the *Virtual Scene's* camera position.  Simply calling the :py:meth:`.Window.draw()` and :py:meth:`.Window.flip()` methods as usual will take care of the rest!

Create the Virtual Scene
------------------------

Let's say that our virtual scene contains a sphere and a Monkey head::

    from ratcave import graphics

    # Make Meshes for the virtual scene
    obj_reader = graphics.WavefrontReader(graphics.resources.obj_primitives)
    monkey = obj_reader.get_mesh('Monkey', centered=True)
    sphere = obj_reader.get_mesh('Sphere', centered=True)

    # Put inside a Scene
    virtual_scene = graphics.Scene([monkey, sphere])

Create the Projected Scene
--------------------------

The Projected Scene is what is actually sent to the display.  It will contain the projector as a :py:class:`.Camera` object, and the shape of the projected surface (for example, the rodent's arena floor and walls) as a :py:class:`.Mesh` object with the :py:attr:`.Mesh.cubemap` flag set to True.::

    # Import Arena shape as a Mesh
    arena_reader = graphics.WavefrontReader('MyArenaFile.obj')
    arena = arena_reader.get_mesh('Arena')
    arena.cubemap = True

    # Make a camera with the same intrinsic and extrinsic properties of the projector
    projector = graphics.Camera(fov_y=60., x_shift=0.1, position=(0, 1., 0.), rotation=(-90, 0, 0))

    # Put inside a Scene
    active_scene = graphics.Scene(meshes=[arena], camera=projector)

If you have run the arena scanner and/or the projector calibration console scripts, then the data for these is already saved in the resources file, so you can do this step alternatively in the following way::

    # Import Arena shape as a Mesh
    arena_reader = graphics.WavefrontReader(graphics.resources.obj_arena)
    arena = arena_reader.get_mesh('Arena')
    arena.cubemap = True

    # Make a camera with the same intrinsic and extrinsic properties of the projector
    projector = graphics.projector

    # Put inside a Scene
    active_scene = grahpics.Scene(meshes=[arena], camera=projector)

Put the Scenes into a Window
----------------------------

The Window will correctly handle the data so long as it knows which scene should be processed in which way::

    # Create Window
    window = graphics.Window(active_scene=active_scene, virtual_scene=virtual_scene)


Tracking The Subject / Player
-----------------------------

Finally, you need to tell ratCAVE from which perspective the virtual scene should be drawn from! This perpsective is the virtual scene's camera.  In this tutorial, we'll use our :py:class:`.Optitrack` object to get the player's position, but any method you wish can be used to assign an x,y,z position to the virtual scene's :py:attr:`.Scene.camera.position` attribute::

    from ratcave.devices import Optitrack

    # Connect to the motion tracker and get the player's position as an object
    tracker = Optitrack()
    player_tracked = tracker.rigid_bodies['Player']

    # Assign a variable to the virtual scene camera, for convenience
    player_camera = virtual_scene.camera

    # Put the camera position in the same location as the camera position
    player_camera.position = player_tracked.position

.. note:: The rotation angle of the virtual camera doesn't matter, as the cubemapping approach renders the scene 360-degrees around the player.

Display Loop
------------

Now, we simply display!  We'll add another check to for if the user presses the escape key to exit, for convenience::

    from psychopy.events import getKeys

    while 'escape' not in getKeys():

        # Update the virtual camera's position to the player's perspective in real-time
        player_camera.position = player_tracked.position

        # Render the Scenes and push to the display
        window.draw()
        window.flip()


Setting your virtual meshes in Arena-Coordinates
------------------------------------------------

While the above steps are enough for getting a picture, it defines all positions in your tracker's space.  But what if the arena itself shifts, or rotates?  Then all of your careful alignment would be lost--virtual objects placed inside the arena could be positioned outside the arena!

.. note:: This problem does not affect the Mesh's apparant shape, however--all geometric warping will continue to be correct.  

To solve this, we can set each virtual Mesh's :py:attr:`.Mesh.global.position` and :py:attr:`.Mesh.global.rotation` properties to match the position of the Arena!  When this happens, everything will be centered on the arena, and their :py:attr:`.Mesh.local.position` and :py:attr:`.Mesh.local.rotatoin` properties can be used to reposition them as normal.  Doing this thus moves your positioning from *Absolute Coordinates* to *Relative Coordinates*.  No more problems!

Here's how you can do that in real-time, allowing even a constantly-moving arena to stay updated::

    # Set virtual meshes to relative coordinate system.
    for mesh in active_scene.meshes:
        mesh.world.position = arena.local.position
        mesh.world.rotation = arena.local.rotation


Getting Rotation-Invariant Tracking Coordinates
-----------------------------------------------

When a new object is being tracked, the position of the object is fairly easy to ascertain, but its rotation is not; as a result, many trackers will define any new object as starting with zero rotation, and simply tracking from there.  But what if you want to track an object that you need to redefine?  Rescanning the object helps this problem, as does saving the original tracking data for future use, but if something is lost or changed then everything--arena body defining, arena scanning, and experiment positioning-- would need to be redone.  

To help with this problem, ratCAVE tracker objects have a :py:attr:`.Tracker.rotation_pca_y` attribute that defines an object's rotation in terms of the addition of the tracker server's stated rotation and the angle between its default vector and the vector of maximum variance, along the direction of its highest variance.  This way, the rotation is totally defined by the marker configuration itself (how we tend to think of the object's rotation) instead of its rotation when first defined.  

.. todo:: Need to better explain the :py:attr:`.Tracker.rotation_pca_y` concept in the future.

Further, the arena_scanner.py console script can automatically rotate the arena vertices so that these two rotations match.  So, when using files generated by this scanner, the rotation_pca_y information must be used instead of the rotation data::

    arena_tracked = tracker.rigid_bodies['Arena']
    arena.local.position = arena_tracked.position
    arena.local.rotation = arena_tracked.rotation_pca_y

Summary
-------

Here's the final code::
    
    # Imports    
    from ratcave import graphics
    from ratcave.devices import Optitrack
    from psychopy.events import getKeys

    # Make Meshes for the virtual scene
    obj_reader = graphics.WavefrontReader(graphics.resources.obj_primitives)
    monkey = obj_reader.get_mesh('Monkey', centered=True)
    sphere = obj_reader.get_mesh('Sphere', centered=True)

    virtual_scene = graphics.Scene([monkey, sphere])

    # Import Arena shape as a Mesh
    arena_reader = graphics.WavefrontReader(graphics.resources.obj_arena)
    arena = arena_reader.get_mesh('Arena')
    arena.cubemap = True

    # Make a camera with the same intrinsic and extrinsic properties of the projector
    projector = graphics.projector

    # Put inside a Scene
    active_scene = graphics.Scene(meshes=[arena], camera=projector)

    # Connect to the motion tracker and get the player's position as an object
    tracker = Optitrack()
    player_tracked = tracker.rigid_bodies['Player']
    player_camera = virtual_scene.camera

    arena_tracked = tracker.rigid_bodies['Arena']

    # Main Draw Loop
    while 'escape' not in getKeys():

        # Update the virtual camera's position to the player's perspective in real-time
        player_camera.position = player_tracked.position

        # Position virtual meshes relative to the arena.
        arena.local.position = arena_tracked.position
        arena.local.rotation = arena_tracked.rotation_pca_y
        
        for mesh in active_scene.meshes:
            mesh.world.position = arena.local.position
            mesh.world.rotation = arena.local.rotation

        # Render the Scenes and push to the display
        window.draw()

That's it!  We're still not at a release verision, and we'll be adding more features in the future to make this process even easier, so that your coding efforts can be focused on what matters--your experiments!
