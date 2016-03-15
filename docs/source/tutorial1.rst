Tutorial 1: Displaying a 3D Object
++++++++++++++++++++++++++++++++++

This tutorial will show the process of displaying a 3D object onscreen. This will be done in four steps:
  - We'll open a file containing 3D objects--a Wavefront .obj file containing basic 3D primitives that comes with ratCAVE (although you can use any .obj file outputted by 3D modeling software), using the :py:class:`.WavefrontReader` class.
  - We then retrieve a :py:class:`.Mesh` object from the file. Mesh objects contain all information about the object, including its position (inside its Local and World attributes, which are :py:class:`.Physical` objects), color (inside its Material attribute, which are of the :py:class:`.Material` class), and even the vertex data itself (inside its Data attribute, which is a :py:class:`.MeshData` object).
  - We'll put the Mesh inside a :py:class:`.Scene` object, which is a container class that holds :py:class:`.Mesh` objects, a :py:class:`.Camera` object, and a :py:class:`.Light` object, along with an RGB background color. Multiple Scenes can be created, even ones that contain the same Meshes, and rendering one vs another one is as simple as changing which Scene is the active one inside the :py:class:`.Window`.
  - Finally, we'll put the Scene inside a :py:class:`.Window` object, and render it by calling its :py:meth:`.Window.draw` and :py:meth:`.Window.flip`  methods.


Starting an OpenGL Context
--------------------------

ratCAVE depends on their already being an OpenGL context set up before loading objects.  This can be done by any OpenGL manager (Pyglet and PsychoPy are useful, but PyGame and Qt OpenGL windows should work fine as well).
So, before doing anything in ratCAVE, a window must first be created.  In these tutorials, I'll show it with Pyglet::

  import pyglet
  import ratcave as rc

  window = pyglet.window.Window()


Reading a Wavefront .obj file
-----------------------------

Wavefront files can be exported from Blender, and they usually come in pairs-- a .obj file contianing the spatial vertex data for each mesh, and a .mtl file containing the coloring data for each mesh.  In ratCAVE, .obj files are summarized in the :py:class:`.MeshData` class and .mtl files are summarized in the :py:class:`.Material` class.  :py:class:`Mesh` classes wrap both of these, plus containing a bit of extra functionality for dealing with these meshes as a whole (like moving the whole thing around, rotating it, or giving it certain image textures, things like that.).  Custom :py:class:`.MeshData` and :py:class:`.Material` objects can be created, but often it is just easier to import them together in Wavefront files as :py:class:`.Mesh` objects.  This is the purpose of the :py:class:`.WavefrontReader` class.  We've included some files with primitive shapes with ratCAVE, whose paths you can find under :py:attr:`.graphics.resources`, to get you started::

  # Insert filename into WavefrontReader.
  obj_filename = rc.resources.obj_primitives
  obj_reader = rc.WavefrontReader(obj_filename)

  # Check which meshes can be found inside the Wavefront file, and extract it into a Mesh object for rendering.
  print(obj_reader.mesh_names)
  >>> ['Torus', 'Sphere', 'Monkey', 'Cube']


Creating a Mesh from the WavefrontReader and Positioning it
-----------------------------------------------------------

The same keywords used for instantiating a Mesh can be used inside the :py:meth:`.WavefrontReader.get_mesh` method.  By default, the mesh will have its position in the same location as in its .obj file, but this can be easilty changed.  Because the camera is in the -z directoin by default, let's set it in front of the camera::

  monkey = obj_reader.get_mesh("Monkey")
  monkey.position = 0, 0, -2

Creating a Scene
----------------

To be rendered onscreen, you must first put :py:class:`.Mesh` objects  can be put into a :py:class:`.Scene`.  This may seem a bit too much when you have only one Mesh, but it allows for many advanced features.  For this exmple, we have just one, but we still need to put it in as a list.::

  scene = rc.Scene(meshes=[monkey])


Drawing the Scene
-----------------------------------------

To draw the scene, simply call the Scene.draw() method in the context manager's draw loop and start the loop::

  @window.event
  def on_draw():
     scene.draw()

  pyglet.app.run()

Summary
-------

That's it!  Here's the final script, in one place.  This script wll be modified in the next tutorial to animate the scene.::

  import pyglet
  import ratcave as rc

  # Create Window
  window = pyglet.window.Window()

  # Insert filename into WavefrontReader.
  obj_filename = rc.resources.obj_primitives
  obj_reader = rc.WavefrontReader(obj_filename)

  # Create Mesh
  monkey = obj_reader.get_mesh("Monkey")
  monkey.position = 0, 0, -2

  # Create Scene
  scene = rc.Scene(meshes=[monkey])

  @window.event
  def on_draw():
    scene.draw()

  pyglet.app.run()


Version using PsychoPy
----------------------

Alternatively, you can see the same example using a PsychoPy window::



  import ratcave as rc
  from psychopy import visual, events

  # Create Window
  window = visual.Window()

  # Insert filename into WavefrontReader.
  obj_filename = rc.resources.obj_primitives
  obj_reader = rc.WavefrontReader(obj_filename)

  # Create Mesh
  monkey = obj_reader.get_mesh("Monkey")
  monkey.position = 0, 0, -2

  # Create Scene
  scene = rc.Scene([monkey])

  while 'escape' not in events.getKeys():
      scene.draw()
      window.flip()

  window.close()

