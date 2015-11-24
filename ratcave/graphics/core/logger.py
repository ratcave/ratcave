__author__ = 'nicholas'

import datetime
import json
from json import encoder
encoder.FLOAT_REPR = lambda x: "{0:.4f}".format(x).rstrip('0').rstrip('.')
from . import mixins
import time
import os
import Image
import base64
from pyglet import image

physical_keys = sorted(key for key in mixins.Physical().__dict__.keys() if '_' not in key[0])
def encode_phys(obj):
    """Only grabs the data that is expected to change frame to frame"""
    try:
        d = obj.__dict__
        dd = {}
        for key in d:
            if key in ['camera', 'local', 'world']:
                temp_d = d[key].__dict__
                dd.update({key: [temp_d[n] for n in physical_keys if n in temp_d]})
        if 'meshes' in d:
            dd.update({'meshes': {mesh.data.name: mesh for mesh in d['meshes'] if mesh.visible}})
        return dd
    except:
        return

def encode_obj(obj):
    """Handles json obj and numpy array encoding."""
    if isinstance(obj, image.Texture):
        img = obj.get_texture().get_image_data()
        im = Image.frombytes(img.format, (img.width, img.height), img.data).resize((32, 32), Image.ANTIALIAS)
        return {'shape': im.size,'format': img.format, 'data': base64.b64encode(im.tobytes()), 'encoding': 'Base64'}
    try:
        d = obj.__dict__.copy()
        if 'meshes' in d:
            d['meshes'] = {mesh.data.name: mesh for mesh in d['meshes']}
        return d #obj.__dict__
    except AttributeError:
        try:
            return obj.tolist()
        except AttributeError:
            return obj



class Logger(object):

    def __init__(self, window, exp_name, log_directory=os.path.join('.', 'logs'), metadata_dict={}, buffer_len=240):

        today = datetime.datetime.today()

        # File specifics
        self.f = None  # Will be the file handle, when opened with a context manager
        self.filename = exp_name + today.strftime('_%Y-%m-%d_%H-%M-%S') + '.json'
        self.filedir = log_directory

        # Create Header Data
        self.metadata = metadata_dict
        self.metadata.update({'Date': today.date().isoformat(), 'Time': today.time().isoformat()})

        # Cache/Buffer parameters
        self.lines_buffer = []
        self.buffer_len = buffer_len
        self.timestamp_start = time.time()

        # Data pre-organization
        self.win_dict = {'active_scene': window.active_scene}
        if window.virtual_scene:
            self.win_dict.update({'virtual_scene': window.virtual_scene})


    def __enter__(self):

        # Return the file for writing the Physical, frame-by-frame, log:
        if not os.path.exists(self.filedir):
            os.mkdir(self.filedir)
        self.f = open(os.path.join(self.filedir, self.filename), 'w')

        # Write the experiment metdadata
        self.f.write('{"session": ')
        json.dump(self.metadata, self.f)

        # Describe the scene
        self.f.write(', "objects": ')
        json.dump(self.win_dict, self.f, default=encode_obj, sort_keys=True)

        # Fake-Create the Data Side (if crashes during experiment, will just need to write onto the end.
        self.f.write(', "log": {"columns": %s, "data": [' % json.dumps(physical_keys))

        # Return self for context manager
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove trailing comma, close array, and close file
        self.f.seek(-1, 1)
        self.f.truncate()
        self.f.write(']}}')
        self.f.close()

    def write(self, note=None):

        self.win_dict['time'] = time.time() - self.timestamp_start
        self.win_dict['note'] = note
        self.lines_buffer.append(json.dumps(self.win_dict, default=encode_phys, sort_keys=True))

        if len(self.lines_buffer) > self.buffer_len:
            self.f.write(','.join(self.lines_buffer) + ',')
            self.lines_buffer = []

