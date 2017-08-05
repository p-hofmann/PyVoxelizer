#!/usr/bin/env python

from setuptools import setup, find_packages
from voxlib import __version__ as version, __author__ as author

setup(
    name='voxlib',
    version=version,
    description='A python converter of 3D model into voxels',
    author=author,
    author_email='',
    url='',
    packages=find_packages(exclude=('unittest', '__pycache__')),
    )
