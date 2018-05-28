from __future__ import print_function
import unittest
from ratcave.utils import Observable, Observer, AutoRegisterObserver, IterObservable
import numpy as np


np.set_printoptions(suppress=True, precision=2)

class TestObserver(unittest.TestCase):
    """
    Run tests from main project folder.
    """


    def test_observer_receives_observable_signals(self):

        obs = Observer()
        obs2 = Observer()
        able = Observable()
        able.register_observer(obs)

        self.assertIn(obs, able._observers)
        self.assertNotIn(obs2, able._observers)

    def test_observer_executes_when_notified_and_updated(self):

        class DummyObserver(Observer):
            def on_change(self):
                self.test_value += 1

        obs = DummyObserver()
        obs.test_value = 1

        obs2 = DummyObserver()
        obs2.test_value = 1

        self.assertEqual(obs.test_value, 1)
        obs.notify()
        obs.update()
        self.assertEqual(obs.test_value, 2)
        obs.notify()
        obs.update()
        self.assertEqual(obs.test_value, 3)
        self.assertEqual(obs2.test_value, 1)


        able = Observable()
        able.register_observer(obs)
        obs.update()
        self.assertEqual(obs.test_value, 4)

        able.notify_observers()
        obs.update()
        obs2.update()
        self.assertEqual(obs.test_value, 5)
        self.assertEqual(obs2.test_value, 1)

    def test_observer_executes_when_notified(self):

        class DummyObserver(Observer):
            def on_change(self):
                self.test_value += 1

        obs = DummyObserver()
        obs.test_value = 1

        obs2 = DummyObserver()
        obs2.test_value = 1

        self.assertEqual(obs.test_value, 1)
        obs.notify()
        self.assertEqual(obs.test_value, 1)
        obs.notify()
        obs.update()
        self.assertEqual(obs.test_value, 2)
        self.assertEqual(obs2.test_value, 1)

        self.assertEqual(obs.test_value, 2)
        obs.update()
        self.assertEqual(obs.test_value, 2)


        able = Observable()
        able.register_observer(obs)
        self.assertEqual(obs.test_value, 2)

        able.notify_observers()
        self.assertEqual(obs.test_value, 2)
        self.assertEqual(obs2.test_value, 1)


    def test_observer_executes_for_every_single_notification(self):
        class DummyObserver(Observer):
            def on_change(self):
                self.test_value += 1

        obs = DummyObserver()
        obs.test_value = 0

        ables = [Observable() for el in range(5)]
        for idx, able in enumerate(ables):
            able.register_observer(obs)
            obs.update()
            self.assertEqual(obs.test_value, idx + 1)

        for idx, able in enumerate(ables):
            able.notify_observers()
            obs.update()
            self.assertEqual(obs.test_value, idx + len(ables) + 1)

    def test_observable_keeps_no_duplicates(self):
        obs = Observer()
        able = Observable()
        self.assertEqual(len(able._observers), 0)
        able.register_observer(obs)
        obs.update()
        self.assertEqual(len(able._observers), 1)
        able.register_observer(obs)
        obs.update()
        self.assertEqual(len(able._observers), 1)
        able.register_observer(Observer())
        obs.update()
        self.assertEqual(len(able._observers), 2)

        able.unregister_observer(obs)
        obs.update()
        self.assertEqual(len(able._observers), 1)

    def test_autoregistration(self):
        obs = Observer()
        able = Observable()
        self.assertEqual(len(able._observers), 0)
        obs.attr1 = able
        self.assertEqual(len(able._observers), 0)

        autoobs = AutoRegisterObserver()
        autoobs.attr1 = able
        self.assertEqual(len(able._observers), 1)
        autoobs.attr1 = able
        self.assertEqual(len(able._observers), 1)
        autoobs.attr2 = able
        self.assertEqual(len(able._observers), 1)
