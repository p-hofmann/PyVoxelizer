__author__ = 'Peter Hofmann'

import unittest
import os
from voxlib.voxelize import voxelize


class PerimeterTest(unittest.TestCase):
    input_file_paths = [
        "./input/cube.stl",
        "./input/cube_diagonals.stl",
        "./input/cube_diagonals_axis.stl",
        # "./input/Dragon_2.5.stl",
        # "./input/Scaffold.obj"
    ]

    def test_cube(self):
        file_path = self.input_file_paths[0]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(voxelize(file_path, resolution))
        self.assertEqual(len(voxels), 602)
        print(len(voxels))

    def test_diagonals(self):
        file_path = self.input_file_paths[1]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(voxelize(file_path, resolution))
        # self.assertEqual(len(voxels), 602)
        print(len(voxels))

    def test_diagonals_axis(self):
        file_path = self.input_file_paths[2]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(voxelize(file_path, resolution))
        # self.assertEqual(len(voxels), 602)
        print(len(voxels))

