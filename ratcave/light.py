from .physical import PhysicalNodeComposite

class Light(PhysicalNodeComposite):

    def __init__(self, *args, **kwargs):
        """Light class."""
        super(Light, self).__init__(*args, **kwargs)