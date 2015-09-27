

Tutorials
=========

Example 1: Displaying a 3D Object
+++++++++++++++++++++++++++++++++

This tutorial will show the process of displaying a 3D object onscreen. This will be done in four steps:
  - We'll open a file containing 3D objects--a Wavefront .obj file containing basic 3D primitives that comes with ratCAVE (although you can use any .obj file outputted by 3D modeling software), 
  - We then retrieve a Mesh object from the file. Mesh objects contain all information about the object, including its position (inside its Local and World attributes), color (inside its Material attribute), and even the vertex data itself (inside its Data attribute).
  - We'll put the Mesh inside a Scene object, which is a container class that holds all meshes visible at one time, a Camera object, and a Light source object. Multiple Scenes can be created, even ones that contain the same Meshes, and rendering one vs another one is as simple as changing which Scene is the active one inside the Window.
  - Finally, we'll put the Scene inside a Window object, and render it by calling its draw() and flip() methods.


