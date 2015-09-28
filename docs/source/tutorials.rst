

Tutorials
=========

Example 1: Displaying a 3D Object
+++++++++++++++++++++++++++++++++

This tutorial will show the process of displaying a 3D object onscreen. This will be done in four steps:
  - We'll open a file containing 3D objects--a Wavefront .obj file containing basic 3D primitives that comes with ratCAVE (although you can use any .obj file outputted by 3D modeling software), 
  - We then retrieve a Mesh object from the file. Mesh objects contain all information about the object, including its position (inside its Local and World attributes), color (inside its Material attribute), and even the vertex data itself (inside its Data attribute).
  - We'll put the Mesh inside a Scene object, which is a container class that holds all meshes visible at one time, a Camera object, and a Light source object. Multiple Scenes can be created, even ones that contain the same Meshes, and rendering one vs another one is as simple as changing which Scene is the active one inside the Window.
  - Finally, we'll put the Scene inside a Window object, and render it by calling its draw() and flip() methods.



Reading a Wavefront .obj file
-----------------------------

Wavefront files can be exported from Blender, and they usually come in pairs-- a .obj file contianing the spatial vertex data for each mesh, and a .mtl file containing the coloring data for each mesh.  In ratCAVE, .obj files are summarized in the MeshData class and .mtl files are summarized in the Material class.  Mesh classes wrap both of these, plus containing a bit of extra functionality for dealing with these meshes as a whole (like moving the whole thing around, rotating it, or giving it certain image textures, things like that.).  Custom MeshData and Material objects can be created, but often it is just easier to import them together in Wavefront files as Meshes.  This is the purpose of the **WavefrontReader** class.  We've included some files with primitive shapes with ratCAVE, whose paths you can find in the **graphics.resources** module, to get you started::

  from ratcave import graphics

  # Insert filename into WavefrontReader.
  obj_filename = graphics.resources.obj_primitives
  obj_reader = graphics.WavefrontReader(obj_filename)

  # Check which meshes can be found inside the Wavefront file, and extract it into a Mesh object for rendering.
  print(obj_reader.mesh_names)
  >>> ['Torus', 'Sphere', 'Monkey', 'Cube']


Creating a Mesh from the WavefrontReader and Positioning it
-----------------------------------------------------------

The same keywords used for instantiating a Mesh can be used inside the WavefrontReader.get_mesh() method.  An important keyword is **centered**--if you leave it False (it is False by default), then the Mesh will appear wherever it was in the original file, which cana be found in its local.position attribute.  This is useful when you've pre-arranged the locations of everything in a 3D modelling program, but if you'd like to explicitly set its postiion, it can be a bit confusing.  So, we set its starting position to 0,0,0 by calling centered=True.  Then, we set local.position to a locatio in front of the camera::

  monkey = obj_reader.get_mesh("Monkey")
  monkey.local.position = 0, 0, -2 


Creating a Scene
----------------

Many Meshes can be put into a Scene.  For this exmple, we have just one, but we still need to put it in as a list.::

  scene = graphics.Scene([monkey])


Creating a Window and Rendering the Scene
-----------------------------------------

Now, we put Scene into a Window.  Currently, ratCAVE only uses Windows subclassed from PsychoPy, and many attributes used for PsychoPy Windows will work here.  We'll delve more into this in future tutorials, along with a few gotchas, but for now, let's just put the Scene into the Window and draw it.  Notice that this always takes two steps--draw(), which does all the heavy rendering on the GPU, and flip(), which actually sends the final image to the display.  These are separated to allow the user finer control of performance.  We'll import PsychoPy's getKeys() function as well, so that the script can be cleanly exited by pressing the 'escape' key on the keyboard. The Window then will be explicitly closed by calling the Window.close() method.  ::

  window = graphics.Window(scene)

  from psychopy import events

  while 'escape' not in events.getKeys():
      window.draw()
      window.flip()

  window.close()


Summary
-------

That's it!  Here's the final script, in one place.  This script wll be modified in the next tutorial to animate the scene.::

  from ratcave import graphics
  from psychopy import events

  # Insert filename into WavefrontReader.
  obj_filename = graphics.resources.obj_primitives
  obj_reader = graphics.WavefrontReader(obj_filename)

  # Create Mesh
  monkey = obj_reader.get_mesh("Monkey")
  monkey.local.position = 0, 0, -2

  # Create Scene
  scene = graphics.Scene([monkey])

  # Create Window
  window = graphics.Window(scene)

  while 'escape' not in events.getKeys():
      window.draw()
      window.flip()

  window.close()



Tutorial 2: Animating a Scene with Multiple Meshes, and using Multiple Scenes
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This tutorial will build on the previous one by adding some more interesting elements.  We'll allow the user to switch between two different scenes by pressing a key, and have multiple meshes in each scenethat move.

Scenes Hold Lists of Meshes
---------------------------

Let's insert a couple Meshes from our obj_reader WavefrontReader object into a couple different scenes.  We'll even create a second Monkey object and display it as a wireframe.::

  # Create Meshes from WavefrontReader
  monkey = obj_reader.get_mesh("Monkey", centered=True, position=(0, 0, -1.5))
  cube = obj_reader.get_mesh("Cube", centered=True, position=(1, 0, -1.5), scale=.2)
  torus = obj_reader.get_mesh("Torus", centered=True, position=(-1, 0, -1.5), scale=.2)
  wire_monkey = obj_reader.get_mesh("Monkey", centered=True, drawstyle='lines', position=(0, 0, -2)

  # Create Scenes with Meshes.  
  scene1 = graphics.Scene([monkey, cube])
  scene2 = graphics.Scene([wire_monkey, torus])

Moving a Mesh
-------------

Now, we'll animate the Meshes by changing their position and rotation attributes. Note that these are found in both the local and world attributes, and it's very important to understand which is which.  But for now, let's just say that the easiest thing to do is to leave the world position and rotation at (0,0,0) and only modify the local attribute, to get the most intuitive results::

  from psychopy import events
  import math

  window = graphics.Window(Scene)

  theta = 0
  while True:
      keys_pressed = events.getKeys()  # getKeys() will empty list each time it returns, so save it to reference it multiple times.
      if 'escape' in keys_pressed:
          window.close()
          break


      # Animate
      aa += .05
      monkey.local.position = math.sin(aa), 0, -2
      cube.local.rotation = (aa * 3), 0, 0

      # Draw
      window.draw()
      window.flip()

 
Modifying Scene's Background Color
----------------------------------

Scenes also have a background color, saved as an RGB array in the Scene.bgColor attribute::

  scene1.bgColor = 1, 0, 0
  scene2.bgColor = 0, 1, 1
      
Changing the Active Scene
-------------------------

The Scene being rendered in the Window is found in the Window.active_scene attribute.  To change what is being drawn, simply assign a different Scene object to Window.active_scene::

    if 'left' in keys_pressed:
       window.active_scene = scene1
    elif 'right' in keys_pressed:
       window.active_scene = scene2
 
Let's also modify which object is being moved based on the Meshes listed in Scene.meshes::

  window.active_scene.meshes[0].local.position = math.sin(aa), 0, -2
  window.active_scene.meshes[1].local.rotation = (aa  * 3), 0, 0


Summary
-------

Here's the full code from Tutorial 2::

  from ratcave import graphics
  from psychopy import events
  import math

  # Insert filename into WavefrontReader.
  obj_filename = graphics.resources.obj_primitives
  obj_reader = graphics.WavefrontReader(obj_filename)
  
  # Create Meshes from WavefrontReader
  monkey = obj_reader.get_mesh("Monkey", centered=True, position=(0, 0, -1.5))
  cube = obj_reader.get_mesh("Cube", centered=True, position=(1, 0, -1.5), scale=.2)
  torus = obj_reader.get_mesh("Torus", centered=True, position=(-1, 0, -1.5), scale=.2)
  wire_monkey = obj_reader.get_mesh("Monkey", centered=True, drawstyle='lines', position=(0, 0, -2)

  # Create Scenes with Meshes.  
  scene1 = graphics.Scene([monkey, cube])
  scene2 = graphics.Scene([wire_monkey, torus])
  window = graphics.Window(Scene)

  # Main Loop
  theta = 0
  while True:

      keys_pressed = events.getKeys()  # getKeys() will empty list each time it returns, so save it to reference it multiple times.

      # End program and close window if escape key is pressed.
      if 'escape' in keys_pressed:
          window.close()
          break

      #  Switch active scene if left or right arrow keys are pressed.
      if 'left' in keys_pressed:
          window.active_scene = scene1
      elif 'right' in keys_pressed:
          window.active_scene = scene2
      
      
      # Animate
      aa += .05
      window.active_scene.meshes[0].local.position = math.sin(aa), 0, -2
      window.active_scene.meshes[1].local.rotation = (aa  * 3), 0, 0

      # Draw
      window.draw()
      window.flip()


