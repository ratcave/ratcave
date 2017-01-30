from .observers import Observable

class NameLabelMixin(object):

    def __init__(self, name=None, **kwargs):
        super(NameLabelMixin, self).__init__(**kwargs)
        self.name = str(name) if name else 'Unnamed{}'.format(self.__class__.__name__)


class ObservableVisibleMixin(Observable):

    def __init__(self, visible=True, **kwargs):
        super(ObservableVisibleMixin, self).__init__(**kwargs)
        self._visible = visible

    @property
    def visible(self):
        """Whether Mesh is drawn or not."""
        return self._visible

    @visible.setter
    def visible(self, value):
        val = bool(value)
        if val != self._visible:
            self._visible = bool(value)
            self.notify_observers()
