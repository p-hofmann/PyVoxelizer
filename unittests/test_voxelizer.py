import unittest
import os
from voxlib.voxelize import voxelize, get_intersecting_voxels_depth_first, scale_and_shift_triangle


class PerimeterTest(unittest.TestCase):
    input_file_paths = [
        "./input/cube.stl",
        "./input/cube_diagonals.stl",
        "./input/cube_diagonals_axis.stl",
        # "./input/Dragon_2_5.stl",
        # "./input/Scaffold.obj"
    ]

    def test_cube(self):
        file_path = self.input_file_paths[0]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(voxelize(file_path, resolution))
        print(len(voxels))
        self.assertEqual(len(voxels), 602)

    def test_diagonals(self):
        file_path = self.input_file_paths[1]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(voxelize(file_path, resolution))
        print(len(voxels))
        self.assertEqual(len(voxels), 890)

    def test_diagonals_axis(self):
        file_path = self.input_file_paths[2]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(voxelize(file_path, resolution))
        print(len(voxels))
        self.assertEqual(len(voxels), 730)

    def test_get_intersecting_voxels_depth_first(self):
        scale = 0.2171953325381205
        shift = [103.419, 65.4, 68.2169]
        triangle = ((-39.3653, 8.43406, 86.9206), (-66.9773, -5.08748, 86.9206), (-39.3653, -8.43406, 86.9206))
        (vertex_1, vertex_2, vertex_3) = scale_and_shift_triangle(triangle, scale, shift)
        new_set = get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3)
        center = (
            int((vertex_1[0] + vertex_2[0] + vertex_3[0]) / 3.),
            int((vertex_1[1] + vertex_2[1] + vertex_3[1]) / 3.),
            int((vertex_1[2] + vertex_2[2] + vertex_3[2]) / 3.)
            )
        self.assertTrue(center in new_set, center)


if __name__ == '__main__':
    unittest.main()
