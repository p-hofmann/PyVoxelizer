__author__ = 'Peter Hofmann'

import unittest
import os
from voxlib.voxelize import voxelize


class PerimeterTest(unittest.TestCase):
    input_file_paths = [
        "./input/cube_corner.stl",
        # "./input/Dragon_2.5.stl",
        # "./input/Scaffold.obj"
    ]

    def test_voxelize(self):
        for file_path in self.input_file_paths:
            print(os.path.basename(file_path))
            triangles = set(voxelize(file_path, 10))
            self.assertGreaterEqual(len(triangles), 2)
        # print(x, y, z)
