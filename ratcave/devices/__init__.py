__author__ = 'ratcave'


import optitrack
from optitrack import Optitrack, NatDataSocket, NatCommSocket

# Optional Imports
try:
    import propixx_utils
except ImportError:
    print("Warning: propixx_utils module not imported, as pypixxlib not found.")
