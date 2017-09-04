
class Observable(object):

    def __init__(self, **kwargs):
        super(Observable, self).__init__(**kwargs)
        self._observers = set()
        self.notify_observers()

    def register_observer(self, observer):
        if not issubclass(observer.__class__, Observer):
            raise TypeError()
        self._observers.add(observer)
        observer.notify(self)

    def unregister_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.notify(self)


class IterObservable(Observable):
    """Observable that auto-notifies observers if indexed assignment is performed on it."""

    def __setitem__(self, key, value):
        self.notify_observers()


class Observer(object):

    def __init__(self, **kwargs):
        super(Observer, self).__init__(**kwargs)
        self._requires_update = True
        self._changed_observables = []

    def notify(self, observable):
        """Flags Observer to perform update() at proper time."""
        self._requires_update = True
        self._changed_observables.append(observable)

    def on_change(self):
        """Callback for if change  detected. Meant to be overridable by subclasses."""
        pass

    def update(self):
        """Check if any updates happened. If not, return False.  Else, perform callback and reset update flag, and return True."""
        assert not hasattr(super, 'update')
        if not self._requires_update:
            return False
        else:
            self.on_change()
            self._requires_update = False
            self._changed_observables = []
            return True


class AutoRegisterObserver(Observer):
    # Auto-checks if new attributes are Observable. If so, registers self with them and notifies a change.

    def __setattr__(self, key, value):
        super(AutoRegisterObserver, self).__setattr__(key, value)
        if issubclass(value.__class__, Observable):
            value.register_observer(self)