import unittest
import os
from voxlib.voxelize import Voxelizer


class PerimeterTest(unittest.TestCase):
    input_file_paths = [
        "./input/cube.stl",
        "./input/cube_diagonals.stl",
        "./input/cube_diagonals_axis.stl",
        os.path.join(".", "input", "test_obj", "test.obj"),
        # "./input/Dragon_2_5.stl",
        # "./input/Scaffold.obj"
    ]

    def test_obj_texture(self):
        rgba_color_map_armor = {
            None                   :  63,  # glass
            (0   , 0   , 0   , 1.0): 603,  # black
            (0.9 , 0.9 , 0.9 , 1.0): 608,  # white
            (0.5 , 0   , 0.5 , 1.0): 613,  # purple
            (0   , 0.1 , 0.75, 1.0): 618,  # blue
            (0   , 0.75, 0   , 1.0): 623,  # green
            (0.9 , 0.9 , 0   , 1.0): 628,  # yellow
            (0.9 , 0.5 , 0   , 1.0): 633,  # orange
            (0.75, 0   , 0   , 1.0): 638,  # red
            (0.9 , 0.75, 0.5 , 1.0): 643,  # brown
            (0   , 0.6 , 0.6 , 1.0): 878,  # teal
            (0.9 , 0   , 0.9 , 1.0): 912,  # pink / fuchsia

            (0   , 0   , 0   , 0.75): 593,  # black
            (0.25, 0.25, 0.25, 0.75): 828,  # dark grey
            (0.5 , 0.5 , 0.5 , 0.5): 598,  # grey
            (1.0 , 1.0 , 1.0 , 0.5): 507,  # white
            (0.5 , 0   , 0.5 , 0.5): 537,  # purple
            (0   , 0   , 0.5 , 0.5): 532,  # blue
            (0   , 0.5 , 0   , 0.5): 527,  # green
            (1.0 , 1.0 , 0   , 0.5): 522,  # yellow
            (1.0 , 0.5 , 0   , 0.5): 517,  # orange
            (0.5 , 0   , 0   , 0.5): 512,  # red
            (1.0 , 0.75, 0.5 , 0.5): 690,  # brown
            (0   , 0.5 , 0.5 , 0.5): 883,  # teal
            (1.0 , 0   , 1.0 , 0.5): 917,  # pink / fuchsia
            }
        file_path = self.input_file_paths[3]
        print(os.path.basename(file_path))
        resolution = 100
        voxels = []
        colors = []
        for position, color in Voxelizer.voxelize(file_path, resolution, color_list=list(rgba_color_map_armor.keys())):
            voxels.append(position)
            colors.append(color)
        print(len(voxels))

    def test_cube(self):
        file_path = self.input_file_paths[0]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(list(Voxelizer.voxelize(file_path, resolution)))
        print(len(voxels))
        self.assertEqual(len(voxels), 602)

    def test_diagonals(self):
        file_path = self.input_file_paths[1]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(list(Voxelizer.voxelize(file_path, resolution)))
        print(len(voxels))
        self.assertTrue(len(voxels) in [874, 890])

    def test_diagonals_axis(self):
        file_path = self.input_file_paths[2]
        print(os.path.basename(file_path))
        resolution = 11
        voxels = set(list(Voxelizer.voxelize(file_path, resolution)))
        print(len(voxels))
        self.assertEqual(len(voxels), 730)

    def test_test(self):
        file_path = "./input/vaygr-mobile-refinery.zip"
        print(os.path.basename(file_path))
        resolution = 512
        voxels = set(list(Voxelizer.voxelize(file_path, resolution)))

    def test_get_intersecting_voxels_depth_first(self):
        scale = 0.2171953325381205
        shift = [103.419, 65.4, 68.2169]
        triangle = ((-39.3653, 8.43406, 86.9206), (-66.9773, -5.08748, 86.9206), (-39.3653, -8.43406, 86.9206))
        (vertex_1, vertex_2, vertex_3) = Voxelizer._shift_and_scale_triangle(triangle, scale, shift)
        new_set = Voxelizer._get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3)
        center = (
            int((vertex_1[0] + vertex_2[0] + vertex_3[0]) / 3.),
            int((vertex_1[1] + vertex_2[1] + vertex_3[1]) / 3.),
            int((vertex_1[2] + vertex_2[2] + vertex_3[2]) / 3.)
            )
        self.assertTrue(center in new_set, center)

        scale = 5.710692304657724
        shift = [41.61392, 13.89282, 43.15285]
        triangle = ((5.16002, -1.27574, -37.65369), (7.913, -3.8991, -32.88319), (5.16002, -3.8991, -32.88319))
        (vertex_1, vertex_2, vertex_3) = Voxelizer._shift_and_scale_triangle(triangle, scale, shift)
        new_set = Voxelizer._get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3)
        center = (
            int((vertex_1[0] + vertex_2[0] + vertex_3[0]) / 3.),
            int((vertex_1[1] + vertex_2[1] + vertex_3[1]) / 3.),
            int((vertex_1[2] + vertex_2[2] + vertex_3[2]) / 3.)
            )
        self.assertTrue(center in new_set, center)

        triangle = ((1.08379, 15.04493, 2.03954), (-1.08379, 15.04493, 2.03954), (-2.74327, 8.26107, 12.26688))
        (vertex_1, vertex_2, vertex_3) = Voxelizer._shift_and_scale_triangle(triangle, scale, shift)
        new_set = Voxelizer._get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3)
        center = (
            int((vertex_1[0] + vertex_2[0] + vertex_3[0]) / 3.),
            int((vertex_1[1] + vertex_2[1] + vertex_3[1]) / 3.),
            int((vertex_1[2] + vertex_2[2] + vertex_3[2]) / 3.)
            )
        self.assertTrue(center in new_set, center)
        # [], [], []
        triangle = ((18.60192, 4.88039, -26.33656), (18.60192, 4.88039, -32.88319), (28.1828, 4.8804, -26.34663))
        (vertex_1, vertex_2, vertex_3) = Voxelizer._shift_and_scale_triangle(triangle, scale, shift)
        new_set = Voxelizer._get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3)
        center = (
            int((vertex_1[0] + vertex_2[0] + vertex_3[0]) / 3.),
            int((vertex_1[1] + vertex_2[1] + vertex_3[1]) / 3.),
            int((vertex_1[2] + vertex_2[2] + vertex_3[2]) / 3.)
            )
        self.assertTrue(center in new_set, center)

if __name__ == '__main__':
    unittest.main()
