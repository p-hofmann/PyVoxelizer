import math


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
            int((self.maximum[0] + self.minimum[0])/2.0),
            int((self.maximum[1] + self.minimum[1])/2.0),
            int((self.maximum[2] + self.minimum[2])/2.0)
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
