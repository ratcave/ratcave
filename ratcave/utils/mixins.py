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


class BindingContextMixin(object):
    """Mixin that calls self.bind() and self.unbind() when used in a context manager."""

    def __enter__(self):
        self.bind()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unbind()


class BindTargetMixin(object):
    """Mixin that speifices a bind() and unbind() interface by taking advantage of the OpenGL bind format:
    bind: bindfun(target, id)
    unbind: bindfun(target, 0)
    """

    bindfun = None
    _bound = None

    def bind(self):
        self.bindfun(self.target, self.id)
        self.__class__._bound = self

    @classmethod
    def unbind(cls):
        cls.bindfun(cls.target, 0)
        cls._bound = None


class BindNoTargetMixin(BindTargetMixin):
    """Same as BindTargetMixin, but for bind functions that don't have a specified target."""

    _bound = None

    def bind(self):
        self.bindfun(self.id)
        self.__class__._bound = self

    @classmethod
    def unbind(cls):
        cls.bindfun(0)
        cls._bound = None
