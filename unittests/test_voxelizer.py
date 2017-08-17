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
            (  0,   0,   0): {255: 603, 127: 593, 0:  63},  # black
            (255, 255, 255): {255: 608, 127: 507},  # white
            (127,   0, 127): {255: 613, 127: 537},  # purple
            (  0,   0, 192): {255: 618, 127: 532},  # blue
            (  0, 192,   0): {255: 623, 127: 527},  # green
            (255, 255,   0): {255: 628, 127: 522},  # yellow
            (255, 127,   0): {255: 633, 127: 517},  # orange
            (192,   0,   0): {255: 638, 127: 512},  # red
            (255, 192, 127): {255: 643, 127: 690},  # brown
            (  0, 127, 127): {255: 878, 127: 883},  # teal
            (255,   0, 255): {255: 912, 127: 917},  # pink / fuchsia

            ( 64,  64,  64): {255: 828, 127: 828},  # dark grey
            (127, 127, 127): {255: 598, 127: 598},  # grey
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

    # def test_test(self):
    #     file_path = "./input/vaygr-mobile-refinery.zip"
    #     print(os.path.basename(file_path))
    #     resolution = 512
    #     voxels = set(list(Voxelizer.voxelize(file_path, resolution)))

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
