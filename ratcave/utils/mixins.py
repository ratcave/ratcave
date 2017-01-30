

class NameLabelMixin(object):

    def __init__(self, name=None, **kwargs):
        super(NameLabelMixin, self).__init__(**kwargs)
        self.name = str(name) if name else 'Unnamed{}'.format(self.__class__.__name__)



