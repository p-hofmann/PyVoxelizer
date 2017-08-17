import argparse
import sys
import numpy as np

from meshlib.meshreader import MeshReader
from .boundarybox import BoundaryBox
from .common.progressbar import print_progress_bar
from .voxelintersect.triangle import Triangle, t_c_intersection, INSIDE, vertexes_to_c_triangle, triangle_lib


class Voxelizer(object):

    n_range = {-1, 0, 1}

    @staticmethod
    def _get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3):
        """

        @type vertex_1: numpy.ndarray
        @type vertex_2: numpy.ndarray
        @type vertex_3: numpy.ndarray

        @rtype: list[(int, int, int)]
        """
        c_lib = triangle_lib
        result_positions = []
        tmp_triangle = None
        searched = set()
        stack = set()

        seed = (int(vertex_1[0]), int(vertex_1[1]), int(vertex_1[2]))
        for x in Voxelizer.n_range:
            for y in Voxelizer.n_range:
                for z in Voxelizer.n_range:
                    neighbour = (seed[0] + x, seed[1] + y, seed[2] + z)
                    if neighbour not in searched:
                        stack.add(neighbour)

        tmp = np.array([0.0, 0.0, 0.0])
        tmp_vertex_1 = np.array([0.0, 0.0, 0.0])
        tmp_vertex_2 = np.array([0.0, 0.0, 0.0])
        tmp_vertex_3 = np.array([0.0, 0.0, 0.0])
        if not c_lib:
            tmp_triangle = Triangle()
            tmp_triangle.set(tmp_vertex_1, tmp_vertex_2, tmp_vertex_3)
        while len(stack) > 0:
            position = stack.pop()
            searched.add(position)
            tmp[0] = 0.5 + position[0]
            tmp[1] = 0.5 + position[1]
            tmp[2] = 0.5 + position[2]

            # move raster to origin, test assumed triangle in relation to origin
            np.subtract(vertex_1, tmp, tmp_vertex_1)
            np.subtract(vertex_2, tmp, tmp_vertex_2)
            np.subtract(vertex_3, tmp, tmp_vertex_3)

            try:
                if c_lib:
                    is_inside = c_lib.t_c_intersection(
                        vertexes_to_c_triangle(tmp_vertex_1, tmp_vertex_2, tmp_vertex_3)) == INSIDE
                else:
                    is_inside = t_c_intersection(tmp_triangle) == INSIDE
            except Exception:
                c_lib = None
                tmp_triangle = Triangle()
                tmp_triangle.set(tmp_vertex_1, tmp_vertex_2, tmp_vertex_3)
                is_inside = t_c_intersection(tmp_triangle) == INSIDE

            if is_inside:
                result_positions.append(position)

                neighbours = set()
                if tmp_vertex_2[0] < 0:
                    neighbours.add((position[0] - 1, position[1], position[2]))
                    if tmp_vertex_3[0] > 0:
                        neighbours.add((position[0] + 1, position[1], position[2]))
                else:
                    neighbours.add((position[0] + 1, position[1], position[2]))
                    if tmp_vertex_3[0] < 0:
                        neighbours.add((position[0] - 1, position[1], position[2]))

                if tmp_vertex_2[1] < 0:
                    neighbours.add((position[0], position[1] - 1, position[2]))
                    if tmp_vertex_3[1] > 0:
                        neighbours.add((position[0], position[1] + 1, position[2]))
                else:
                    neighbours.add((position[0], position[1] + 1, position[2]))
                    if tmp_vertex_3[1] < 0:
                        neighbours.add((position[0], position[1] - 1, position[2]))

                if tmp_vertex_2[2] < 0:
                    neighbours.add((position[0], position[1], position[2] - 1))
                    if tmp_vertex_3[2] > 0:
                        neighbours.add((position[0], position[1], position[2] + 1))
                else:
                    neighbours.add((position[0], position[1], position[2] + 1))
                    if tmp_vertex_3[2] < 0:
                        neighbours.add((position[0], position[1], position[2] - 1))

                for neighbour in neighbours:
                    if neighbour not in searched:
                        stack.add(neighbour)
        del searched, stack
        return result_positions

    @staticmethod
    def _get_scale_and_shift(mesh, resolution):
        """

        @type mesh: list[((float, float, float), (float, float, float), (float, float, float))]
        @type resolution: int
        @rtype: (float, list[float], int)
        """
        triangle_count = 0
        mins = list(mesh[0][0])
        maxs = list(mesh[0][0])
        for triangle in mesh:
            triangle_count += 1
            for index, point in enumerate(triangle):
                if point[index] < mins[index]:
                    mins[index] = point[index]
                if point[index] > maxs[index]:
                    maxs[index] = point[index]
        shift = [-minimum for minimum in mins]
        scale = float(resolution - 1) / (max(maxs[0] - mins[0], maxs[1] - mins[1], maxs[2] - mins[2]))
        return scale, shift, triangle_count

    @staticmethod
    def _shift_and_scale_triangle(triangle, scale, shift):
        """
        move mesh to origin and then scale it to fit resolution

        @type triangle: ((float, float, float), (float, float, float), (float, float, float))
        @type scale: float
        @type shift: list[float

        @rtype: list[np.ndarray]
        """
        shifted_triangle = []
        for point in triangle:
            new_point = np.array(
                [
                    (point[0] + shift[0]) * scale,
                    (point[1] + shift[1]) * scale,
                    (point[2] + shift[2]) * scale
                 ])
            shifted_triangle.append(new_point)
        del triangle
        return shifted_triangle

    @staticmethod
    def voxelize(file_path, resolution, color_list=None, progress_bar=None):
        """

        @type file_path: str
        @type resolution: int
        @type color_list: list[(float, float, float, float)]
        @type progress_bar: any
        """
        if not progress_bar:
            progress_bar = print_progress_bar

        # read triangle positions from file
        mesh_reader = MeshReader()
        if file_path.endswith('.zip'):
            mesh_reader.read_archive(file_path)
        else:
            mesh_reader.read(file_path)
        if not mesh_reader.has_triangular_facets():
            raise NotImplementedError("Unsupported polygonal face elements. Only triangular facets supported.")
        list_of_triangles = list(mesh_reader.get_facets())

        # move mesh to origin and then scale it to fit resolution
        scale, shift, triangle_count = Voxelizer._get_scale_and_shift(list_of_triangles, resolution)
        for index, triangle in enumerate(list_of_triangles):
            # if index == 118:
            #     print(triangle, scale, shift)
            #     return
            list_of_triangles[index] = Voxelizer._shift_and_scale_triangle(triangle, scale, shift)

        # find voxels for each facet
        progress_counter = 0
        dict_voxels = {}
        bounding_box = BoundaryBox()
        for index, (vertex_1, vertex_2, vertex_3) in enumerate(list_of_triangles):
            progress_counter += 1
            progress_bar(progress_counter, triangle_count, prefix="Voxelize: ")
            bounding_box.from_vertexes(vertex_1, vertex_2, vertex_3)
            dict_voxels[index] = Voxelizer._get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3)

            # center = (
            #     int((vertex_1[0] + vertex_2[0] + vertex_3[0]) / 3.),
            #     int((vertex_1[1] + vertex_2[1] + vertex_3[1]) / 3.),
            #     int((vertex_1[2] + vertex_2[2] + vertex_3[2]) / 3.)
            #     )
            # assert center in dict_voxels[index], index

        # get textures if available
        dict_colors = None
        if color_list is not None:
            if None in color_list:
                color_list.remove(None)
            from .voxelpainter import VoxelPainter
            dict_colors = VoxelPainter.paint_voxels(mesh_reader, list_of_triangles, dict_voxels, color_list, progress_bar)

        # output one position at a time
        center = bounding_box.get_center()
        for key, voxels in dict_voxels.items():
            for index, (x, y, z) in enumerate(voxels):
                if dict_colors is not None:
                    try:
                        yield (x - center[0], y - center[1], z - center[2]), dict_colors[key][index]
                    except (KeyError, TypeError):
                        yield (x - center[0], y - center[1], z - center[2]), None
                else:
                    yield (x - center[0], y - center[1], z - center[2])

if __name__ == '__main__':
    # parse cli args
    parser = argparse.ArgumentParser(description='stl/obj file to voxels converter')
    parser.add_argument('input')
    parser.add_argument('resolution', type=int)
    args = parser.parse_args()
    for pos_x, pos_y, pos_z in Voxelizer.voxelize(args.input, args.resolution):
        sys.stdout.write("{}\t{}\t{}\n".format(pos_x, pos_y, pos_z))
