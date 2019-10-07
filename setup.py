import os
import codecs
import subprocess
import py_common_util
from setuptools import setup, find_packages
from distutils.command.install import install as _install

with open("README.md") as f:
    readme = f.read()


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_install_requires():
    with open('requirements.txt', 'r') as f:
        res = f.readlines()
    res = list(map(lambda s: s.replace('\n', ''), res))
    return res


class install(_install):
    def run(self):
        subprocess.call(["make", "clean", "-C", "src/hello"])
        subprocess.call(["make", "all", "-C", "src/hello"])
        _install.run(self)

setup(
    name='py-common-util',
    version=py_common_util.__version__,
    description="",
    long_description=readme,
    install_requires=read_install_requires(),
    setup_requires=['setuptools>=41.2.0', 'wheel>=0.33.6'],
    author='tony',
    author_email='',
    license='BSD',
    url='',
    keywords='python common util',
    classifiers=['Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'License :: OSI Approved :: BSD License'],
    packages=find_packages(),
    package_data={'': ["foo.so"]},
    cmdclass={'install': install},
)

# it can also be built from the repository as follows.
# 1. $git clone https://github.com/perfmjs/py-common-util
# 2. $python setup.py bdist_wheel
# 3. $pip install dist/*.whl
# 4. $pip show -f hello