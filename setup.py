#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Voxelizer',
    version='0.0.1',
    description='Voxelizer, turning 3D model into voxels',
    author='Peter Hofmann',
    author_email='',
    url='',
    packages=find_packages(exclude=('unittest', '__pycache__')),
    )
