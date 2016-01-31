__author__ = 'nicholas'

from .camera import Camera
from .mixins import Color, Physical

class Light(Camera):

    def __init__(self, *args, **kwargs):
        super(Light, self).__init__(*args, **kwargs)