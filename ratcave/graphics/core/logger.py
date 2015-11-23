__author__ = 'nicholas'

import datetime
import json
from json import encoder
encoder.FLOAT_REPR = lambda o: "{0:.4f}".format(o)#lambda o: format(o, '.4f')
from . import mixins
import time

physical_keys = mixins.Physical().__dict__.keys()
def encode_phys(obj):
    """Only grabs the data that is expected to change frame to frame"""
    try:
        d = obj.__dict__
        dd = {key: d[key] for key in d if key in ['camera', 'local', 'world']}
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

    def __init__(self, fname, window, exp_name, student_name, subj_name, sess_name, buffer_len=240):

        self.filename = fname

        today = datetime.datetime.today()
        self.metadata = {'Experiment': exp_name,
                         'Experimenter': student_name,
                         'Subject': subj_name,
                         'Session': sess_name,
                         'Date': today.date().isoformat(),
                         'Time': today.time().isoformat()}

        self.f = None  # Will be flie
        self.win_dict = {'active_scene': window.active_scene}
        self.lines_buffer = []
        self.buffer_len = buffer_len
        self.timestamp_start = time.time()

        if window.virtual_scene:
            self.win_dict.update({'virtual_scene': window.virtual_scene})


    def __enter__(self):

        # Return the file for writing the Physical, frame-by-frame, log:
        self.f = open(self.filename+'.json', 'w')

        # Write the experiment metdadata
        self.f.write('{"session": ')
        json.dump(self.metadata, self.f)

        # Describe the scene
        self.f.write(', "objects": ')
        json.dump(self.win_dict, self.f, default=encode_obj, sort_keys=True)

        # Fake-Create the Data Side (if crashes during experiment, will just need to write onto the end.
        self.f.write(', "data": [')

        # Return self for context manager
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove trailing comma, close array, and close file
        self.f.seek(-1, 1)
        self.f.truncate()
        self.f.write(']}')
        self.f.close()

    def write(self, note=None):

        self.win_dict['time'] = time.time() - self.timestamp_start
        self.win_dict['note'] = note
        self.lines_buffer.append(json.dumps(self.win_dict, default=encode_phys, sort_keys=True))

        if len(self.lines_buffer) > self.buffer_len:
            self.f.write(','.join(self.lines_buffer))
            self.f.write(',')
            self.lines_buffer = []

        # Write only the data
        # data = json.loads(json.dumps(self.win_dict, self.f, default=encode_phys, sort_keys=True))
        # for scene_dict in ['active_scene']:
        #
        #     #data[scene_dict]['light'] = [data[scene_dict]['light'][key] for key in physical_keys]
        #     data[scene_dict]['camera'] = [data[scene_dict]['camera'][key] for key in physical_keys]
        #     for meshkey in data[scene_dict]['meshes']:
        #         for phys in ['local', 'world']:
        #             data[scene_dict]['meshes'][meshkey][phys] = [data[scene_dict]['meshes'][meshkey][phys][key] for key in physical_keys]
        # json.dump(data, self.f, sort_keys=True)#


        # self.f.write(',')

