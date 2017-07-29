__author__ = 'Peter Hofmann'

import argparse
import sys
import math

import numpy as np

from .common.progressbar import print_progress_bar
from voxlib.meshreader.meshreader import MeshReader
from .voxelintersect.triangle import Triangle, t_c_intersection, INSIDE, vertexes_to_c_triangle, triangle_lib
from .mesh import calculate_scale_and_shift, scale_and_shift_triangle


class BoundaryBox(object):
    """
    @type minimum: list[int]
    @type maximum: list[int]
    """

    minimum = None
    maximum = None

    def get_center(self):
        assert self.minimum, "BoundaryBox not initialized"
        return [
            int((self.maximum[0] + self.minimum[0])/2),
            int((self.maximum[1] + self.minimum[1])/2),
            int((self.maximum[2] + self.minimum[2])/2)
            ]

    def from_triangle(self, triangle):
        """
        @type triangle: Triangle
        """
        self.minimum[0] = math.floor(triangle.min(0))
        self.minimum[1] = math.floor(triangle.min(1))
        self.minimum[2] = math.floor(triangle.min(2))

        self.maximum[0] = math.ceil(triangle.max(0))
        self.maximum[1] = math.ceil(triangle.max(1))
        self.maximum[2] = math.ceil(triangle.max(2))

    def from_vertexes(self, vertex_1, vertex_2, vertex_3):
        """
        @type vertex_1: (float, float, float)
        @type vertex_2: (float, float, float)
        @type vertex_3: (float, float, float)
        """
        if self.minimum is None:
            self.minimum = [0, 0, 0]
            self.maximum = [0, 0, 0]

            self.minimum[0] = math.floor(min([vertex_1[0], vertex_2[0], vertex_3[0]]))
            self.minimum[1] = math.floor(min([vertex_1[1], vertex_2[1], vertex_3[1]]))
            self.minimum[2] = math.floor(min([vertex_1[2], vertex_2[2], vertex_3[2]]))

            self.maximum[0] = math.ceil(max([vertex_1[0], vertex_2[0], vertex_3[0]]))
            self.maximum[1] = math.ceil(max([vertex_1[1], vertex_2[1], vertex_3[1]]))
            self.maximum[2] = math.ceil(max([vertex_1[2], vertex_2[2], vertex_3[2]]))
        else:
            self.minimum[0] = math.floor(min([vertex_1[0], vertex_2[0], vertex_3[0], self.minimum[0]]))
            self.minimum[1] = math.floor(min([vertex_1[1], vertex_2[1], vertex_3[1], self.minimum[1]]))
            self.minimum[2] = math.floor(min([vertex_1[2], vertex_2[2], vertex_3[2], self.minimum[2]]))

            self.maximum[0] = math.ceil(max([vertex_1[0], vertex_2[0], vertex_3[0], self.maximum[0]]))
            self.maximum[1] = math.ceil(max([vertex_1[1], vertex_2[1], vertex_3[1], self.maximum[1]]))
            self.maximum[2] = math.ceil(max([vertex_1[2], vertex_2[2], vertex_3[2], self.maximum[2]]))


# @staticmethod
def get_neighbours(position):
    range_p = [-1, 0, 1]
    for x in range_p:
        for y in range_p:
            for z in range_p:
                # if abs(x) + abs(y) + abs(z) > 2:
                #     continue
                position_tmp = (position[0] + x, position[1] + y, position[2] + z)
                # if position_tmp == position:
                #     continue
                yield position_tmp


range_p = [-1, 0, 1]


def get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3):
    """

    @type vertex_1: numpy.ndarray
    @type vertex_2: numpy.ndarray
    @type vertex_3: numpy.ndarray

    @rtype: list[(int, int, int)]
    """
    result_positions = []
    range_p = [-1, 0, 1]
    tmp_triangle = None
    seed = int(vertex_1[0]), int(vertex_1[1]), int(vertex_1[2])
    searched = set()
    stack = set()
    stack.add(seed)
    tmp = np.array([0.0, 0.0, 0.0])
    tmp_vertex_1 = np.array([0.0, 0.0, 0.0])
    tmp_vertex_2 = np.array([0.0, 0.0, 0.0])
    tmp_vertex_3 = np.array([0.0, 0.0, 0.0])
    if not triangle_lib:
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
        if triangle_lib:
            is_inside = triangle_lib.t_c_intersection(
                vertexes_to_c_triangle(tmp_vertex_1, tmp_vertex_2, tmp_vertex_3)) == INSIDE
        else:
            is_inside = t_c_intersection(tmp_triangle) == INSIDE
        if is_inside:
            result_positions.append(position)
            # neighbours = list(get_neighbours(position))
            for x in range_p:
                for y in range_p:
                    for z in range_p:
                        neighbour = (position[0] + x, position[1] + y, position[2] + z)
                        if neighbour not in searched:
                            stack.add(neighbour)
    del searched, stack
    return result_positions


def get_intersecting_voxels_depth_first_mod(vertex_1, vertex_2, vertex_3):
    """

    @type vertex_1: numpy.ndarray
    @type vertex_2: numpy.ndarray
    @type vertex_3: numpy.ndarray

    @rtype: list[(int, int, int)]
    """
    result_positions = []
    tmp_triangle = None
    searched = set()
    stack = set()

    seed = int(vertex_1[0]), int(vertex_1[1]), int(vertex_1[2])
    stack.add(seed)

    tmp = np.array([0.0, 0.0, 0.0])
    tmp_vertex_1 = np.array([0.0, 0.0, 0.0])
    tmp_vertex_2 = np.array([0.0, 0.0, 0.0])
    tmp_vertex_3 = np.array([0.0, 0.0, 0.0])
    if not triangle_lib:
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
        if triangle_lib:
            is_inside = triangle_lib.t_c_intersection(
                vertexes_to_c_triangle(tmp_vertex_1, tmp_vertex_2, tmp_vertex_3)) == INSIDE
        else:
            is_inside = t_c_intersection(tmp_triangle) == INSIDE
        if is_inside:
            result_positions.append(position)

            neighbours = set()
            if position[0] > vertex_2[0]:
                neighbours.add((position[0] - 1, position[1], position[2]))
                if position[0] < vertex_3[0]:
                    neighbours.add((position[0] + 1, position[1], position[2]))
            else:
                neighbours.add((position[0] + 1, position[1], position[2]))
                if position[0] > vertex_3[0]:
                    neighbours.add((position[0] - 1, position[1], position[2]))

            if position[1] > vertex_2[1]:
                neighbours.add((position[0], position[1] - 1, position[2]))
                if position[1] < vertex_3[1]:
                    neighbours.add((position[0], position[1] + 1, position[2]))
            else:
                neighbours.add((position[0], position[1] + 1, position[2]))
                if position[1] > vertex_3[1]:
                    neighbours.add((position[0], position[1] - 1, position[2]))

            if position[2] > vertex_2[2]:
                neighbours.add((position[0], position[1], position[2] - 1))
                if position[2] < vertex_3[2]:
                    neighbours.add((position[0], position[1], position[2] + 1))
            else:
                neighbours.add((position[0], position[1], position[2] + 1))
                if position[2] > vertex_3[2]:
                    neighbours.add((position[0], position[1], position[2] - 1))

            for neighbour in neighbours:
                if neighbour not in searched:
                    stack.add(neighbour)
    del searched, stack
    return result_positions


def voxelize(file_path, resolution):
    mesh_reader = MeshReader()
    mesh_reader.read(file_path)
    if not mesh_reader.has_triangular_facets():
        raise NotImplementedError("Unsupported polygonal face elements. Only triangular facets supported.")

    list_of_triangles = list(mesh_reader.get_facets())
    scale, shift, triangle_count = calculate_scale_and_shift(list_of_triangles, resolution)
    progress_counter = 0
    voxels = set()
    bounding_box = BoundaryBox()
    for triangle in list_of_triangles:
        progress_counter += 1
        print_progress_bar(progress_counter, triangle_count, prefix="Voxelize: ")

        (vertex_1, vertex_2, vertex_3) = scale_and_shift_triangle(triangle, scale, shift)
        bounding_box.from_vertexes(vertex_1, vertex_2, vertex_3)
        voxels.update(get_intersecting_voxels_depth_first_mod(vertex_1, vertex_2, vertex_3))
    center = bounding_box.get_center()
    while len(voxels) > 0:
        (x, y, z) = voxels.pop()
        yield x-center[0], z-center[2], -1 * (y-center[1])


if __name__ == '__main__':
    # parse cli args
    parser = argparse.ArgumentParser(description='STL file to voxels converter')
    parser.add_argument('input')
    parser.add_argument('resolution', type=int)
    args = parser.parse_args()
    for x, y, z in voxelize(args.input, args.resolution):
        sys.stdout.write("{}\t{}\t{}\n".format(x, y, z))
