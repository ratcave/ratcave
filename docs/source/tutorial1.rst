Tutorial 1: Displaying a 3D Object
++++++++++++++++++++++++++++++++++

This tutorial will show the process of displaying a 3D object onscreen. This will be done in four steps:
  - We'll open a file containing 3D objects--a Wavefront .obj file containing basic 3D primitives that comes with ratCAVE (although you can use any .obj file outputted by 3D modeling software), using the :py:class:`.WavefrontReader` class.
  - We then retrieve a :py:class:`.Mesh` object from the file. Mesh objects contain all information about the object, including its position (inside its Local and World attributes, which are :py:class:`.Physical` objects), color (inside its Material attribute, which are of the :py:class:`.Material` class), and even the vertex data itself (inside its Data attribute, which is a :py:class:`.MeshData` object).
  - We'll put the Mesh inside a :py:class:`.Scene` object, which is a container class that holds :py:class:`.Mesh` objects, a :py:class:`.Camera` object, and a :py:class:`.Light` object, along with an RGB background color. Multiple Scenes can be created, even ones that contain the same Meshes, and rendering one vs another one is as simple as changing which Scene is the active one inside the :py:class:`.Window`.
  - Finally, we'll put the Scene inside a :py:class:`.Window` object, and render it by calling its :py:meth:`.Window.draw` and :py:meth:`.Window.flip`  methods.



Reading a Wavefront .obj file
-----------------------------

Wavefront files can be exported from Blender, and they usually come in pairs-- a .obj file contianing the spatial vertex data for each mesh, and a .mtl file containing the coloring data for each mesh.  In ratCAVE, .obj files are summarized in the :py:class:`.MeshData` class and .mtl files are summarized in the :py:class:`.Material` class.  :py:class:`Mesh` classes wrap both of these, plus containing a bit of extra functionality for dealing with these meshes as a whole (like moving the whole thing around, rotating it, or giving it certain image textures, things like that.).  Custom :py:class:`.MeshData` and :py:class:`.Material` objects can be created, but often it is just easier to import them together in Wavefront files as :py:class:`.Mesh` objects.  This is the purpose of the :py:class:`.WavefrontReader` class.  We've included some files with primitive shapes with ratCAVE, whose paths you can find under :py:attr:`.graphics.resources`, to get you started::


  import ratcave as rc

  # Insert filename into WavefrontReader.
  obj_filename = rc.resources.obj_primitives
  obj_reader = rc.WavefrontReader(obj_filename)

  # Check which meshes can be found inside the Wavefront file, and extract it into a Mesh object for rendering.
  print(obj_reader.mesh_names)
  >>> ['Torus', 'Sphere', 'Monkey', 'Cube']


Creating a Mesh from the WavefrontReader and Positioning it
-----------------------------------------------------------

The same keywords used for instantiating a Mesh can be used inside the :py:meth:`.WavefrontReader.get_mesh` method.  An important keyword is **centered**--if you leave it False (it is False by default), then the Mesh will appear wherever it was in the original file, which cana be found in its local.position attribute.  This is useful when you've pre-arranged the locations of everything in a 3D modelling program, but if you'd like to explicitly set its position, it can be a bit confusing.  So, we set its starting position to 0,0,0 by calling centered=True.  Then, we set local.position to a location in front of the camera::

  monkey = obj_reader.get_mesh("Monkey")
  monkey.local.position = 0, 0, -2 


Creating a Scene
----------------

To be rendered onscreen, you must first put :py:class:`.Mesh` objects  can be put into a :py:class:`.Scene`.  This may seem a bit too much when you have only one Mesh, but it allows for many advanced features.  For this exmple, we have just one, but we still need to put it in as a list.::

  scene = rc.Scene([monkey])


Creating a Window and Rendering the Scene
-----------------------------------------

Now, we put :py:class:`.Scene` into a :py:class:`.Window`.  Currently, ratCAVE only uses Windows subclassed from PsychoPy, and many attributes used for PsychoPy Windows will work here.  We'll delve more into this in future tutorials, along with a few gotchas, but for now, let's just put the :py:class:`.Scene` into the :py:class:`.Window` and draw it.  Notice that this always takes two steps--:py:meth:`.Window.draw()`, which does all the heavy rendering on the GPU, and :py:meth:`.Window.flip`, which actually sends the final image to the display.  These are separated to allow the user finer control of performance.  We'll import PsychoPy's getKeys() function as well, so that the script can be cleanly exited by pressing the 'escape' key on the keyboard. The :py:class:`.Window` then will be explicitly closed by calling the :py:meth:`.Window.close` method.  ::

  window = rc.Window(scene)

  from psychopy import events

  while 'escape' not in events.getKeys():
      window.draw()
      window.flip()

  window.close()


Summary
-------

That's it!  Here's the final script, in one place.  This script wll be modified in the next tutorial to animate the scene.::

  import ratcave as rc
  from psychopy import events

  # Insert filename into WavefrontReader.
  obj_filename = rc.resources.obj_primitives
  obj_reader = rc.WavefrontReader(obj_filename)

  # Create Mesh
  monkey = obj_reader.get_mesh("Monkey")
  monkey.local.position = 0, 0, -2

  # Create Scene
  scene = rc.Scene([monkey])

  # Create Window
  window = rc.Window(scene)

  while 'escape' not in events.getKeys():
      window.draw()
      window.flip()

  window.close()

