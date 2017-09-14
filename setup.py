from setuptools import setup, find_packages, Extension
try:
    import numpy
except ImportError:
    print("Numpy must be installed before running setup.py.")
    response = input("Attempt to automatically install numpy using pip? (y/n)")
    if 'y' in response.lower():
        import subprocess
        subprocess.run(["pip", "install", "numpy"])
        import numpy
    else:
        raise ImportError("Numpy required before installation.")


setup(name='ratcave',
      version='0.6',
      url='https://www.github.com/neuroneuro15/ratcave',
      description='3D Graphics Engine for CAVE VR setups',
      author='Nicholas A. Del Grosso',
      author_email='delgrosso.nick@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['docs']),
      include_package_data=True,
      package_data={'': ['../assets/*.'+el for el in ['png', 'obj', 'mtl']] +
                        ['../shaders/*'+el for el in ['vert', 'frag']]
                    },
      install_requires=['pyglet', 'numpy', 'wavefront_reader', 'future', 'six'],
      ext_modules=[Extension('_transformations', sources=['third_party/transformations.c'], include_dirs=[numpy.get_include()])],
      test_suite='tests',
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

