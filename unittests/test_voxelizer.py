__author__ = 'Peter Hofmann'

import unittest
from voxlib.voxelize import voxelize


class PerimeterTest(unittest.TestCase):
    input_ascii = "./cube_corner.stl"
    input_binary = "./Dragon_2.5.stl"

    def test_voxelize(self):
        triangles = set(voxelize(self.input_ascii, 8))
        self.assertGreaterEqual(len(triangles), 2)
        # print(x, y, z)
