"""This is the devices package __init__.py docstring.

.. todo:: Fix the sphinx autodocs (or the way imports are handled), so the devices are properly documented, okay?
"""

__author__ = 'ratcave'

from .trackers.optitrack import Optitrack, NatDataSocket, NatCommSocket

# Optional Imports
try:
    from .displays import propixx_utils
except ImportError:
    print("Warning: propixx_utils module not imported, as pypixxlib not found.")

try:
    from .reward.ttl import USB_TTL
except ImportError:
    print("Warning: USB_TTL device not imported.")


__all__ = ['Optitrack', 'NatDataSocket', 'NatCommSocket', 'USB_TTL', 'propixx_utils']
