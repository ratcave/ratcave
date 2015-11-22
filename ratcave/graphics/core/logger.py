__author__ = 'nicholas'

import datetime
import json
from . import mixins

physical_keys = mixins.Physical().__dict__
def encode_phys(obj):
    """Only grabs the data that is expected to change frame to frame"""
    try:
        d = obj.__dict__
        dd = {key: d[key] for key in d if key in ['light', 'camera', 'local', 'world']}
        dd.update({key: d[key] for key in d if key in physical_keys})
        if 'meshes' in d:
            dd.update({'meshes': {mesh.data.name: mesh for mesh in d['meshes']}})
        if 'visible' in d:
            dd['visible'] = d['visible']
        return dd
    except:
        return

def encode_obj(obj):
    """Handles json obj and numpy array encoding."""
    try:
        return obj.__dict__
    except AttributeError:
        try:
            return obj.tolist()
        except AttributeError:
            return str(obj)




class Logger(object):

    def __init__(self, fname, window, exp_name, student_name, subj_name, sess_name, indent=2):

        self.filename = fname

        today = datetime.datetime.today()
        self.metadata = {'Experiment': exp_name,
                         'Experimenter': student_name,
                         'Subject': subj_name,
                         'Session': sess_name,
                         'Date': today.date().isoformat(),
                         'Time': today.time().isoformat()}

        self.f = None  # Will be flie
        self.indent = indent
        self.win_dict = {'active_scene': window.active_scene}
        if window.virtual_scene:
            self.win_dict.update({'virtual_scene': window.virtual_scene})


    def __enter__(self):
        # Write the header, first, in its own file.
        with open(self.filename+'_header.json', 'w') as f:
            json.dump(self.metadata, f, indent=self.indent)
            json.dump(self.win_dict, f, default=encode_obj, indent=self.indent, sort_keys=True)

        #Return the file for writing the Physical, frame-by-frame, log:
        self.f = open(self.filename+'_tracker.json', 'w')
        self.f.write('[')
        # json.dump(self.metadata, self.f, indent=self.indent)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove trailing comma, and close array
        self.f.seek(-1, 1)
        self.f.truncate()
        self.f.write(']')
        self.f.close()

    def write(self):
        today = datetime.datetime.today
        self.win_dict['time'] = today().time().isoformat()
        json.dump(self.win_dict, self.f, default=encode_phys, indent=self.indent, sort_keys=True)
        self.f.write(',')


