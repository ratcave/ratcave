Tutorial 2: Animating a Scene with Multiple Meshes, and using Multiple Scenes
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This tutorial will build on the previous one by adding some more interesting elements.  We'll allow the user to switch between two different :py:class:`.Scene` objects by pressing a key, and have multiple meshes in each scene that move.

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

