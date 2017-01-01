
class Observable(object):

    def __init__(self, **kwargs):
        super(Observable, self).__init__(**kwargs)
        self.observers = set()

    def ping_observers(self):
        for observer in self.observers:
            observer.ping()


class IterObservable(Observable):
    """Observable that auto-pings observers if indexed assignment is performed on it."""

    def __setitem__(self, key, value):
        # super(IterObservable, self).__setitem__(key, value)
        assert not hasattr(super, '__setitem__')
        self.ping_observers()


class Observer(object):

    def __init__(self, **kwargs):
        super(Observer, self).__init__(**kwargs)
        self._change_counter = 0

    def ping(self):
        """
        Increment the update counter.
        This allows the timing and frequency of change detection and action to be independently controlled.
        """
        self._change_counter += 1

    def on_change(self):
        """Callback for if change  detected.  Meant to be overridable by subclasses."""
        pass

    def update(self):
        """Check if any updates happened. If not, return.  Else, reset update counter and continue to end of method."""
        assert not hasattr(super, 'update')
        if self._change_counter == 0:
            return
        else:
            self._change_counter = 0
            self.on_change()


class AutoRegisterObserver(Observer):
    # Auto-checks if new attributes are Observable. If so, registers self with them and pings a change.

    def __setattr__(self, key, value):
        super(AutoRegisterObserver, self).__setattr__(key, value)
        if isinstance(value, Observable):
            value.observers.add(self)
            self.ping()