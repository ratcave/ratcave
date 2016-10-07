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
      package_data={'': ['assets/*.'+el for el in ['png', 'obj', 'mtl']] +
                        ['shaders/*'+el for el in ['vert', 'frag']]
                    },
      install_requires=['pyglet', 'numpy'],
      scripts=['console_scripts/newexp.py',
               'console_scripts/test_ratcave.py'
                ],
      ext_modules=[Extension('_transformations', sources=['c_sources/transformations.c'], include_dirs=[numpy.get_include()])],
      test_suite='tests',
      classifiers=[
          "Topic :: Multimedia :: Graphics :: 3D Rendering",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
      ],
      )

