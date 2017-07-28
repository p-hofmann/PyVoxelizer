def calculate_scale_and_shift(mesh, resolution):
    """

    @type mesh: collections.Iterable[(float, float, float), (float, float, float), (float, float, float)]
    @type resolution: int
    @rtype: (float, list[float], int)
    """
    triangle_count = 0
    mins = None
    maxs = None
    # allPoints = [item for sublist in mesh for item in sublist]
    for triangle in mesh:
        triangle_count += 1
        if mins is None:
            mins = list(triangle[0])
            maxs = list(triangle[0])
        for index, point in enumerate(triangle):
            if point[index] < mins[index]:
                mins[index] = point[index]
            if point[index] > maxs[index]:
                maxs[index] = point[index]
    shift = [-minimum for minimum in mins]
    scale = float(resolution - 1) / (max(maxs[0] - mins[0], maxs[1] - mins[1]))
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
        new_point = [0, 0, 0]
        for i in range(3):
            new_point[i] = (point[i] + shift[i]) * scale
        shifted_triangle.append(tuple(new_point))
    del triangle
    if not contains_duplicates(shifted_triangle):
        return shifted_triangle
    return None


def contains_duplicates(list_of_points):
    return len(set(list_of_points)) != len(list_of_points)
