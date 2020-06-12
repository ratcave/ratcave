from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext


class build_ext(_build_ext):
    def finalize_options(self):
        """
        only import numpy when it is actually needed for building an extension. By then, it should already be installed.
        From https://stackoverflow.com/questions/19919905/how-to-bootstrap-numpy-installation-in-setup-py
        """
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())



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
      install_requires=['pyglet<2.0', 'numpy', 'wavefront_reader', 'future', 'six'],
      cmdclass={'build_ext':build_ext},
      ext_modules=[Extension('_transformations', sources=['third_party/transformations.c'])],#, include_dirs=[numpy.get_include()])],
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

