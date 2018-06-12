from setuptools import setup, find_packages, Extension
try:
    import numpy
except ImportError:
    raise ImportError("numpy not found.  Please install numpy (e.g. 'pip install numpy') before installing ratcave.")


setup(name='ratcave',
      version='0.8.0',
      url='https://www.github.com/neuroneuro15/ratcave',
      description='3D Graphics Engine for Scientific, Video Game, and VR Applications.',
      author='Nicholas A. Del Grosso',
      author_email='delgrosso.nick@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['docs']),
      include_package_data=True,
      package_data={'': ['../assets/*.'+el for el in ['png', 'obj', 'mtl']] +
                        ['../shaders/*/*'+el for el in ['vert', 'frag']]
                    },
      install_requires=['pyglet', 'numpy', 'wavefront_reader', 'future', 'six'],
      ext_modules=[Extension('_transformations', sources=['third_party/transformations.c'], include_dirs=[numpy.get_include()])],
      setup_requires=['numpy', 'pytest-runner'],
      tests_require = ['pytest'],
      keywords='graphics 3D pyglet psychopy python virtual reality VR',
      classifiers=[
          "Topic :: Multimedia :: Graphics :: 3D Rendering",
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Intended Audience :: Science/Research",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
      ],
      )

