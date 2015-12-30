__author__ = 'ratcave'

from setuptools import setup, find_packages, Extension
import numpy



setup(name='ratcave',
      version='0.5',
      description='3D Graphics Engine for CAVE VR setups',
      author='Nicholas A. Del Grosso',
      author_email='delgrosso@bio.lmu.de',
      packages=find_packages(),
      include_package_data=True,
      package_data={'': ['graphics/assets/*.'+el for el in ['png', 'obj', 'mtl']] +
                        ['graphics/shaders/*'+el for el in ['vert', 'frag']] +
                        ['arduino_programs/s*']
                    },
      install_requires=['pyglet', 'numpy', 'psychopy', 'appdirs', 'sklearn'],
      scripts=['ratcave/console_scripts/arena_scanner.py',
               'ratcave/console_scripts/newexp.py',
               'ratcave/console_scripts/opti_projector_calibration.py',
               'ratcave/console_scripts/opti_projector_rotation_calib.py',
               'ratcave/console_scripts/test_ratcave.py'
                ],
      ext_modules=[Extension('ratcave.graphics._transformations', sources=['ratcave/c_sources/transformations.c'], include_dirs=[numpy.get_include()])]
      )

