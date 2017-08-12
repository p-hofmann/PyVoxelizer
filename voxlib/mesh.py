import numpy as np

# functions are loosly based


def get_scale_and_shift(mesh, resolution):
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


def scale_and_shift_triangle(triangle, scale, shift):
    """

    @type triangle: ((float, float, float), (float, float, float), (float, float, float))
    @type scale: float
    @type shift: list[float

    @rtype: list[(float, float, float)] | None
    """
    shifted_triangle = []
    for point in triangle:
        new_point = np.array([.0, .0, .0])
        for i in range(3):
            new_point[i] = (point[i] + shift[i]) * scale
        shifted_triangle.append(new_point)
    del triangle
    return shifted_triangle
