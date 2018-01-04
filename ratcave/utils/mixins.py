import pickle

class NameLabelMixin(object):

    def __init__(self, name=None, **kwargs):
        super(NameLabelMixin, self).__init__(**kwargs)
        self.name = str(name) if name else 'Unnamed{}'.format(self.__class__.__name__)


class PickleableMixin:

    @classmethod
    def from_pickle(cls, fname):
        with open(fname) as f:
            obj = pickle.load(f)
            if not issubclass(obj.__class__, cls):
                raise TypeError("Unpickled object was of type {}; Expected a {}".format(obj.__class__.__name__, cls.__name__))
        if hasattr(obj, 'reset_uniforms'):
            obj.reset_uniforms()
        return obj

    def to_pickle(self, fname):
        with open(fname, 'w') as f:
            pickle.dump(self, f)