__author__ = 'Peter Hofmann'

import argparse
import sys
import math

import numpy as np

from .common.progressbar import print_progress_bar
from voxlib.meshreader.meshreader import MeshReader
from .voxelintersect.triangle import t_c_intersection, INSIDE, Triangle
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


def get_intersecting_voxels_brute_force(vertex_1, vertex_2, vertex_3):
    """

    @type vertex_1: (float, float, float)
    @type vertex_2: (float, float, float)
    @type vertex_3: (float, float, float)

    @rtype:
    """
    boundary_box = BoundaryBox()
    boundary_box.from_vertexes(vertex_1, vertex_2, vertex_3)

    tmp = np.array([0.0, 0.0, 0.0])
    tmp_triangle = Triangle()
    for x in range(boundary_box.minimum[0], boundary_box.maximum[0]+1):
        tmp[0] = 0.5 + x
        for y in range(boundary_box.minimum[1], boundary_box.maximum[1]+1):
            tmp[1] = 0.5 + y
            for z in range(boundary_box.minimum[2], boundary_box.maximum[2]+1):
                tmp[2] = 0.5 + z
                tmp_triangle.set(
                    np.subtract(vertex_1, tmp),
                    np.subtract(vertex_2, tmp),
                    np.subtract(vertex_3, tmp))
                if t_c_intersection(tmp_triangle) == 0:
                    yield x, y, z


# @staticmethod
def get_neighbours(position):
    range_p = [-1, 0, 1]
    for x in range_p:
        for y in range_p:
            for z in range_p:
                taxi_dist = abs(x) + abs(y) + abs(z)
                position_tmp = (position[0] + x, position[1] + y, position[2] + z)
                if position_tmp == position:
                    continue
                yield taxi_dist, position_tmp


def get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3):
    """

    @type vertex_1: (float, float, float)
    @type vertex_2: (float, float, float)
    @type vertex_3: (float, float, float)

    @rtype:
    """
    # boundary_box = BoundaryBox()
    # boundary_box.from_vertexes(vertex_1, vertex_2, vertex_3)
    seed = int(round(vertex_1[0] - 0.5)), int(round(vertex_1[1] - 0.5)), int(round(vertex_1[2] - 0.5))
    searched = set()
    stack = set()
    stack.add(seed)
    tmp = np.array([0.0, 0.0, 0.0])
    tmp_triangle = Triangle()
    while len(stack) > 0:
        position = stack.pop()
        searched.add(position)
        tmp[0] = 0.5 + position[0]
        tmp[1] = 0.5 + position[1]
        tmp[2] = 0.5 + position[2]
        tmp_triangle.set(
            np.subtract(vertex_1, tmp),
            np.subtract(vertex_2, tmp),
            np.subtract(vertex_3, tmp))
        is_inside = t_c_intersection(tmp_triangle) == INSIDE
        if is_inside:
            for taxi_dist, neighbour in get_neighbours(position):
                if neighbour not in searched:
                    stack.add(neighbour)
            yield position
    del searched, stack


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
        for (x, y, z) in get_intersecting_voxels_depth_first(vertex_1, vertex_2, vertex_3):
            voxels.add((x, y, z))
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
