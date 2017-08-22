import os
import math
import numpy as np

from meshlib.mtlreader import MtlReader


class VoxelPainter(object):

    transparent = (0, 0, 0, 0)

    @staticmethod
    def get_palette(color_list):
        """

        @param color_list: list[(int, int, int)]
        @return: palette_image
        """
        from PIL import Image
        palette_image= Image.new("P", (1, 1))
        number_of_colors = len(color_list)
        array_of_colors = tuple([value for rgb in color_list for value in rgb])
        palette_image.putpalette(array_of_colors + (0, 0, 0) * (256 - number_of_colors))
        return palette_image

    @staticmethod
    def get_image(file_path, palette):
        """

        @type file_path: str
        @param palette: PIL.Image
        @return: image
        """
        from PIL import Image, ImageFilter
        image_material_texture = Image.open(file_path)
        if image_material_texture.mode != "RGB":
            image_material_texture = image_material_texture.convert('RGB')
        size = 3
        # max_rank = size * size - 1
        for _ in range(5):
            image_material_texture = image_material_texture.quantize(palette=palette).convert('RGB')
            image_material_texture = image_material_texture.filter(ImageFilter.MedianFilter(size=size))
        image_material_texture = image_material_texture.quantize(palette=palette).convert('RGB')
        return image_material_texture

    @staticmethod
    def paint_voxels(mesh_reader, list_of_triangles, dict_voxels, color_list, progress_bar):
        palette = VoxelPainter.get_palette(color_list)
        unknown_material = None
        dict_colors = {}
        image_material_texture = None
        pixel_map = None
        triangle_count = len(list_of_triangles)
        directory_textures = mesh_reader.get_directory_textures()
        if not directory_textures:
            # No available textures
            raise RuntimeError("No available textures")
        mtl_reader = MtlReader()
        file_path_material_library_current = None
        file_path_material_current = None
        progress_counter = 0
        for texture_triangle, material_name, file_path_material_library in mesh_reader.get_texture_facets():
            progress_counter += 1
            dict_colors[progress_counter-1] = None
            progress_bar(progress_counter, triangle_count, prefix="Voxelize: ")
            if material_name is None:
                # facet without material assigned
                continue
            if not file_path_material_library or not os.path.exists(file_path_material_library):
                file_path_material_library = mesh_reader.get_file_path()
            if file_path_material_library_current != file_path_material_library:
                file_path_material_library_current = file_path_material_library
                success_failure = mtl_reader.read(file_path_material_library_current, directory_textures)
                if not mtl_reader.validate_textures():
                    # texture paths are invalid
                    raise RuntimeError("Texture file paths could not be confirmed.")
                if success_failure and success_failure[1] > 1:
                    # library reconstruction failed
                    raise RuntimeError("Library reconstruction failed")
            material = mtl_reader.get_material(material_name)
            if material is None and "EXPORT" in material_name:
                material_name = material_name.split("EXPORT")[0]
                material = mtl_reader.get_material(material_name)
            if not material:
                # unknown file path or material
                if unknown_material != material_name:
                    print("No material: '{}'".format(material_name))
                    unknown_material = material_name
                continue
            material_texture = material.get_texture()
            if not material_texture:
                # unknown file path or material
                print("No texture: '{}'".format(material_name))
                continue
            if not material_texture.file_path:
                # unknown file path or material
                if unknown_material != material_name:
                    print("Missing texture file path: '{}'".format(material_name))
                    unknown_material = material_name
                continue
            if file_path_material_current != material_texture.file_path:
                file_path_material_current = material_texture.file_path
                image_material_texture = VoxelPainter.get_image(material_texture.file_path, palette)
                pixel_map = image_material_texture.load()

            dict_colors[progress_counter-1] = VoxelPainter.paint_triangle(
                list_of_triangles[progress_counter-1], texture_triangle, dict_voxels[progress_counter-1],
                material, image_material_texture.size, pixel_map)
        return dict_colors

    @staticmethod
    def magnitude(point):
        return math.sqrt(
            math.pow(point[0], 2) +
            math.pow(point[1], 2) +
            math.pow(point[2], 2))

    @staticmethod
    def point_distance(point_1, point_2):
        return math.sqrt(
            math.pow(point_1[0] - point_2[0], 2) +
            math.pow(point_1[1] - point_2[1], 2) +
            math.pow(point_1[2] - point_2[2], 2))

    @staticmethod
    def color_distance(color_1, color_2):
        return math.sqrt(
            math.pow(color_1[0] - color_2[0], 2) +
            math.pow(color_1[1] - color_2[1], 2) +
            math.pow(color_1[2] - color_2[2], 2) +
            math.pow(color_1[3] - color_2[3], 2)
            )

    @staticmethod
    def paint_triangle(triangle, texture_triangle, list_of_voxels, material, size, pixel_map):
        # todo: stretch and move origin with 'material_texture'

        list_of_rgb = []
        xy_position = [0.0, 0.0]
        for voxel in list_of_voxels:
            u, v = VoxelPainter.position_to_uv(triangle, voxel, texture_triangle)
            if not VoxelPainter.point_in_triangle([u, v], texture_triangle):
                list_of_rgb.append(VoxelPainter.transparent)
                continue
            xy_position[0] = int(math.floor((u % 1) * (size[0]-1)))
            xy_position[1] = int(math.floor((1-(v % 1)) * (size[1]-1)))
            # print(xy_position, size)
            pixel_color = pixel_map[xy_position[0], xy_position[1]]
            # print(xy_position, pixel_color)
            if material.d == 1:
                voxel_color = pixel_color + (255,)
            else:
                voxel_color = pixel_color + (127,)
            list_of_rgb.append(voxel_color)
            # print(xy_position, pixel_color, voxel_color)
        return list_of_rgb

    @staticmethod
    def position_to_uv(triangle, point_f, texture_triangle):
        """
        http://answers.unity3d.com/questions/383804/calculate-uv-coordinates-of-3d-point-on-plane-of-m.html

        @type triangle: ((float, float, float), (float, float, float), (float, float, float))
        @type point_f: (int, int, int)
        @type texture_triangle: ((float, float), (float, float), (float, float))
        """
        p1, p2, p3 = triangle
        uv1, uv2, uv3 = texture_triangle
        # // calculate vectors from point f to vertices p1, p2 and p3:
        f1 = np.subtract(p1, point_f)
        f2 = np.subtract(p2, point_f)
        f3 = np.subtract(p3, point_f)
        # // calculate the areas (parameters order is essential in this case):
        va = np.cross(np.subtract(p1, p2), np.subtract(p1, p3))
        va1 = np.cross(f2, f3)
        va2 = np.cross(f3, f1)
        va3 = np.cross(f1, f2)
        a = VoxelPainter.magnitude(va)
        # // calculate barycentric coordinates with sign:
        a1 = VoxelPainter.magnitude(va1)/a * np.sign(np.dot(va, va1))
        a2 = VoxelPainter.magnitude(va2)/a * np.sign(np.dot(va, va2))
        a3 = VoxelPainter.magnitude(va3)/a * np.sign(np.dot(va, va3))
        # // find the uv corresponding to point f (uv1/uv2/uv3 are associated to p1/p2/p3):
        uv = np.array(uv1) * a1 + np.array(uv2) * a2 + np.array(uv3) * a3
        return uv

    @staticmethod
    def point_same_side(point, p2, a, b):
        """

        @type point: np.ndarray
        @type p2: np.ndarray
        @type a: np.ndarray
        @type b: np.ndarray
        @rtype: bool
        """
        v1 = np.cross(b - a, point - a)
        v2 = np.cross(b - a, p2 - a)
        if np.dot(v1, v2) >= -0.5:
            return True
        return False

    @staticmethod
    def point_in_triangle(point, triangle):
        """

        @type point: list[float]
        @type triangle:
        @rtype: bool
        """
        p = np.array(list(point))
        a = np.array(list(triangle[0]))
        b = np.array(list(triangle[1]))
        c = np.array(list(triangle[2]))
        if VoxelPainter.point_same_side(
                p, a, b, c) and VoxelPainter.point_same_side(
                p, b, a, c) and VoxelPainter.point_same_side(
                p, c, a, b):
            return True
        return False
