import os
from ctypes import cdll
import pathlib


def wrap_bar():
    _path = os.path.join(*(os.path.split(__file__)[:-1]))
    base_path = str(pathlib.Path(__file__).cwd())
    print("===" + base_path + ", " + str(pathlib.Path(__file__)))
    foo = cdll.LoadLibrary(str(pathlib.Path(__file__).with_name('mysum*.so')))
    return foo.bar()


def call_mysum():
    import ctypes
    import numpy
    import glob

    # find the shared library, the path depends on the platform and Python version
    basedir = os.path.abspath(os.path.dirname(__file__))
    libpath = os.path.join(basedir, 'foo*.so')
    print(f"libpath={libpath}, glob.glob(libpath)={glob.glob(libpath)}")
    libfile = glob.glob(libpath)[0]

    # 1. open the shared library
    mylib = ctypes.CDLL(libfile)

    # 2. tell Python the argument and result types of function mysum
    mylib.calc_mysum.restype = ctypes.c_longlong
    mylib.calc_mysum.argtypes = [ctypes.c_int,
                            numpy.ctypeslib.ndpointer(dtype=numpy.int32)]

    array = numpy.arange(0, 100000000, 1, numpy.int32)

    # 3. call function mysum
    array_sum = mylib.calc_mysum(len(array), array)

    print('sum of array: {}'.format(array_sum))


if __name__ == '__main__':
    call_mysum()
