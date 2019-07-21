from setuptools import setup, find_packages
import codecs
import os
import py_common_util

with open("README.md") as f:
    readme = f.read()


def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_install_requires():
    with open('requirements.txt', 'r') as f:
        res = f.readlines()
    res = list(map(lambda s: s.replace('\n', ''), res))
    return res

setup(
    name='py-common-util',
    version=py_common_util.__version__,
    description="",
    long_description=readme,
    install_requires=read_install_requires(),
    setup_requires=['setuptools>=41.0.1', 'wheel>=0.33.4'],
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
    package_data={'': ['*.csv']},
)