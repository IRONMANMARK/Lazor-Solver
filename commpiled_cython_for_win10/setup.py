from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# define the name for the c package and the source python file for the c package convert from
ext_modules = [Extension("hello", ["project.pyx"])]

# set up detail for the build
setup(
    name='Hello world app',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules
)