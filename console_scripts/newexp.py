__author__ = 'Nick DG'

import sys
import os
from os import path

if __name__ == '__main__':


    # Create Base directory
    script_arg_pos = sys.argv.index('newexp.py')
    assert len(sys.argv) > script_arg_pos + 2, "newexp needs an experiment directory name to continue"

    base_name = sys.argv[script_arg_pos + 1]
    assert path.exists(base_name) == False, "directory {0} already exists, please select another name.".format(base_name)

    os.mkdir(base_name)
    os.chdir(base_name)

    # Create Subdirectories and fill them with essential default materials
    """ Base Directory """
    # Create File for all experiment information, to be parsed into a dictionary later on.
    metadata_file = open("metadata.txt", "wb")
    metadata_file.write("Experiment Name: {base_name}\nExperimenters: Nick DG\nDate Created:\nExperiment Description: \n".format(base_name))
    metadata_file.close()

    """ Resources """
    os.mkdir('Resources')  # For meshes and textures
    # TODO: Copy primitives.blend, .obj, and .mtl by default into resources.  Will help with prototyping.

    """ Exp Data """
    os.mkdir('Exp Data') # For Event Logs, Optitrack data
    os.mkdir(path.join('Exp Data', 'Event Logs'))
    os.mkdir(path.join('Exp Data', 'Tracker Data'))
    # TODO: Configure Motive to redirect to this directory.

    """ Exp Design """
    os.mkdir('Exp Design') # For PlanFile, History File,

    """ Subjects """
    os.mkdir('Subjects')  # For all subject-related data files


    # Create Main Experiment Script Skeleton.  This is very helpful for tutorials and such!

    expfile = open(base_name+".py", "wb")  # Create new default python script

    script = """
    import collections
    from os import path
    from psychopy import core, event, gui, sound
    from hippoVR.graphics import *
    from hippoVR.devices import optitrack, propixx


    # Set Experiment Metadata (Important at the very least for file names)
    metadata = collections.OrderedDict()
    metadata['Experiment'] = "{base_name}"  # Use only filename-safe characters
    metadata['Experimenter'] = 'NickDG'  #   Use only filename-safe characters


    # Connect to tracker
    propixx.start_frame_sync_signal()  # Optional. Used to sync Propixx projector frames with Optitrack.
    tracker = optitrack.Optitrack("10.153.170.85")  # Connect to Optitrack tracking system.


    # Load Arena (if none yet, use the arena_scaner.py file to generate it into the Resources subdirectory)
    arena_reader = Wavefront(path.join('Resources', 'Arena.obj'))
    arena = arena_reader.get_mesh('Arena')


    # Load all meshes needed for the experiment (Use Wavefront class to get Mesh objects from .obj files)
    subject = Empty()  # Create subject (rat, mouse, gerbil, etc) as Empty by default, but can give them a Mesh.


    # Insert meshes into Scenes (will need two Scenes, typically, for VR: a real scene and a virtual scene)
    scene = Scene(arena)
    scene.camera = projector
    scene.camera.position = projector_position  # Make sure these were also properly calibrated.
    scene.light.position = projector_position

    virtual_scene = Scene()  # Put all VR objects into this scene!


    # Insert scenes into a Window
    window = PsychWindow(scene)
    window.set_virtual_scene(virtual_scene, subject, arena)  # Always view virtual scene from rat's perspective, and project onto the arena)




    """.format(base_name=base_name)


