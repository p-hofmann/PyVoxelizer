#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='PyVoxelizer',
    version='0.0.1',
    description='A python converter of 3D model into voxels',
    author='Peter Hofmann',
    author_email='',
    url='',
    packages=find_packages(exclude=('unittest', '__pycache__')),
    )
