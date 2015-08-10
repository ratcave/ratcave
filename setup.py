__author__ = 'ratcave'

from setuptools import setup, find_packages

setup(name='ratcave',
      version='0.8',
      description='3D Graphics Engine for CAVE VR setups',
      author='Nicholas A. Del Grosso',
      author_email='delgrosso@bio.lmu.de',
      packages=find_packages(),
      include_package_data=True,
      package_data={'': ['graphics/assets/*.'+el for el in ['png', 'obj', 'mtl']] +
                        ['graphics/shaders/*'+el for el in ['vert', 'frag']]
                    },
      install_requires=['pyglet', 'numpy', 'psychopy', 'appdirs'],
      scripts=['ratcave/console_scripts/arena_scanner.py',
               'ratcave/console_scripts/newexp.py',
               'ratcave/console_scripts/opti_projector_calibration.py',
               'ratcave/console_scripts/opti_projector_rotation_calib.py'
                ]
      )

