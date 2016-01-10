.. ratCAVE documentation master file, created by
   sphinx-quickstart on Tue Sep  8 18:58:17 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ratCAVE's documentation!
===================================


ratCAVE is a Python package for displaying 3D Graphics.  It was inspired by a project meant for displaying a Virtual Reality CAVE Setup for rodents, and was meant as a lightweight alternative to Panda3D.  ratCAVE uses the lightweight OpenGL wrapping provided by Pyglet and advanced OpenGL 3.3+ Features to get a relatively high-performance graphics in an easy-to-use, Pythonic interface.  Currently, only Pyglet and PsychoPy are wrapped as backends, but ratCAVE classes are meant to be "subclass-friendly" and should be easily added to the backend graphics engine of your choice.

Additionally, as Virtual Reality in psychology labs is our original primary targeted user group, this project also has a devices submodule that provides interfaces to NaturalPoints Optitrack NatNet optical tracking system and some USB devices not currently supported in PsychoPy.  These are temporary fixtures, though, for developer convenience (i.e. laziness) as future versions of ratCAVE will focus on increasing graphics performance and the Optitrack class will go into its own Python package.  

Table of Contents:
++++++++++++++++++

.. toctree::
   :maxdepth: 2

   introduction
   tutorials
   ratcave

* :ref:`genindex`

