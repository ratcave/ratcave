
class Observable(object):

    def __init__(self, **kwargs):
        super(Observable, self).__init__(**kwargs)
        self.observers = set()
        self.notify_observers()

    def notify_observers(self):
        for observer in self.observers:
            observer.notify(self)


class IterObservable(Observable):
    """Observable that auto-notifies observers if indexed assignment is performed on it."""

    def __setitem__(self, key, value):
        # super(IterObservable, self).__setitem__(key, value)
        assert not hasattr(super, '__setitem__')
        self.notify_observers()


class Observer(object):

    def __init__(self, **kwargs):
        super(Observer, self).__init__(**kwargs)
        self._changed_observables = []

    def notify(self, observable):
        """
        Increment the update counter.
        This allows the timing and frequency of change detection and action to be independently controlled.
        """
        self._changed_observables.append(observable)

    def on_change(self):
        """Callback for if change  detected.  Meant to be overridable by subclasses."""
        pass

    def update(self):
        """Check if any updates happened. If not, return early.  Else, perform callback and continue to end of method."""
        assert not hasattr(super, 'update')
        if not self._changed_observables:
            return
        else:
            self.on_change()
            self._changed_observables = []



class AutoRegisterObserver(Observer):
    # Auto-checks if new attributes are Observable. If so, registers self with them and notifies a change.

    def __setattr__(self, key, value):
        super(AutoRegisterObserver, self).__setattr__(key, value)
        if isinstance(value, Observable):
            value.observers.add(self)
            self.notify(value)