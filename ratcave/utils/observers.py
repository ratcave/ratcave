
class Observable(object):

    def __init__(self, **kwargs):
        super(Observable, self).__init__(**kwargs)
        self._observers = set()
        self.notify_observers()

    def register_observer(self, observer):
        if not isinstance(observer, Observer):
            raise TypeError()
        self._observers.add(observer)

    def unregister_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.notify()


class IterObservable(Observable):
    """Observable that auto-notifies observers if indexed assignment is performed on it."""

    def __setitem__(self, key, value):
        self.notify_observers()


class Observer(object):

    def __init__(self, **kwargs):
        super(Observer, self).__init__(**kwargs)
        self._requires_update = True

    def notify(self):
        """Flags Observer to perform update() at proper time."""
        self._requires_update = True

    def on_change(self):
        """Callback for if change  detected. Meant to be overridable by subclasses."""
        pass

    def update(self):
        """Check if any updates happened. If not, return early.  Else, perform callback and reset update flag."""
        assert not hasattr(super, 'update')
        if not self._requires_update:
            return
        else:
            self.on_change()
            self._requires_update = False


class AutoRegisterObserver(Observer):
    # Auto-checks if new attributes are Observable. If so, registers self with them and notifies a change.

    def __setattr__(self, key, value):
        super(AutoRegisterObserver, self).__setattr__(key, value)
        if isinstance(value, Observable):
            value.register_observer(self)


class SetterObserver(Observer):

    _observables = []

    def __setattr__(self, key, value):
        """Automatically notifies self whenever an attribute is set, essentially
        turning all attributes into Observables."""
        super(SetterObserver, self).__setattr__(key, value)
        if key in self._observables:
            self.notify()