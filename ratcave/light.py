from .camera import Camera

class Light(Camera):

    def __init__(self, *args, **kwargs):
        """Light class."""
        super(Light, self).__init__(*args, **kwargs)