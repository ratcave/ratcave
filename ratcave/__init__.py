__author__ = 'ratcave'

import graphics
import devices
import utils

# Check for Data Directory.  If not made, then
def __data_dir_check():
    """Checks that the data directory exists, and creates it if not.  Data directory location is platform-specific."""
    import appdirs
    import os

    data_dir = appdirs.user_data_dir('ratCAVE')
    if not os.path.exists(data_dir):
        print("Data Directory not found--creating new data directory at {0}".format(data_dir))
        os.makedirs(data_dir)

    return data_dir

data_dir = __data_dir_check()

