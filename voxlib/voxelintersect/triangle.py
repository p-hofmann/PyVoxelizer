import sys
import os
import numpy as np
from ctypes import cdll, Structure, c_float


class Point3(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float)
        ]


class Triangle3(Structure):
    _fields_ = [
        ("v1", Point3),
        ("v2", Point3),
        ("v3", Point3)
        ]


triangle_lib = None
script_dir = os.path.dirname(os.path.realpath(__file__))
try:
    if sys.platform.startswith('linux') and sys.maxsize == 9223372036854775807:
        file_path_library = os.path.join(script_dir, 'triangleCube_linux64.so')
        if os.path.exists(file_path_library):
            triangle_lib = cdll.LoadLibrary(file_path_library)
    elif sys.platform.startswith("win") and sys.maxsize == 2147483647:
        file_path_library = os.path.join(script_dir, 'triangleCube_win32.so')
        if os.path.exists(file_path_library):
            triangle_lib = cdll.LoadLibrary(file_path_library)
except OSError:
    triangle_lib = None


"""
    Code conversion into python from:
    'https://github.com/erich666/GraphicsGems/blob/master/gemsiii/triangleCube.c'
"""

INSIDE = 0
OUTSIDE = 1
EPS = 1e-5
# EPS = 0.0
# print(EPS)


def cross_product(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        -a[0] * b[2] + a[2] * b[0],
        a[0] * b[1] - a[1] * b[0])


def sign3(point):
    sign_code = 0

    if point[0] < EPS:
        sign_code |= 4
    if point[0] > -EPS:
        sign_code |= 32

    if point[1] < EPS:
        sign_code |= 2
    if point[1] > -EPS:
        sign_code |= 16

    if point[2] < EPS:
        sign_code |= 1
    if point[2] > -EPS:
        sign_code |= 8

    return sign_code


def lerp(alpha, a, b):
    return a + alpha * (b - a)


class Triangle(object):
    """

    @type v1: numpy.ndarray
    @type v2: numpy.ndarray
    @type v3: numpy.ndarray
    """

    def __init__(self):
        """

        """
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0

    def set(self, vertex_1, vertex_2, vertex_3):
        """

        @type vertex_1: numpy.ndarray
        @type vertex_2: numpy.ndarray
        @type vertex_3: numpy.ndarray
        """
        self.v1 = vertex_1
        self.v2 = vertex_2
        self.v3 = vertex_3

    def min(self, index):
        if self.v1[index] < self.v2[index] and self.v1[index] < self.v3[index]:
            return self.v1[index]
        elif self.v2[index] < self.v3[index]:
            return self.v2[index]
        else:
            return self.v3[index]

    def max(self, index):
        if self.v1[index] > self.v2[index] and self.v1[index] > self.v3[index]:
            return self.v1[index]
        elif self.v2[index] > self.v3[index]:
            return self.v2[index]
        else:
            return self.v3[index]


def vertexes_to_c_triangle(vertex_1, vertex_2, vertex_3):
    return Triangle3(
        Point3(vertex_1[0], vertex_1[1], vertex_1[2]),
        Point3(vertex_2[0], vertex_2[1], vertex_2[2]),
        Point3(vertex_3[0], vertex_3[1], vertex_3[2])
        )


def face_plane(point):
    """
    Which of the six face-plane(s) is point P outside of?

    @type point: numpy.ndarray | (float, float, float)
    """
    face_plane_code = 0
    if point[0] >= .5:
        face_plane_code |= 0x01
    if point[0] < -.5:
        face_plane_code |= 0x02
    if point[1] >= .5:
        face_plane_code |= 0x04
    if point[1] < -.5:
        face_plane_code |= 0x08
    if point[2] >= .5:
        face_plane_code |= 0x10
    if point[2] < -.5:
        face_plane_code |= 0x20
    return face_plane_code


def bevel_2d(point):
    """

    Which of the twelve edge plane(s) is point P outside of?
    """
    edge_plane_code = 0
    if point[0] + point[1] >= 1.0:
        edge_plane_code |= 0x001
    if point[0] - point[1] >= 1.0:
        edge_plane_code |= 0x002
    if -point[0] + point[1] > 1.0:
        edge_plane_code |= 0x004
    if -point[0] - point[1] > 1.0:
        edge_plane_code |= 0x008

    if point[0] + point[2] >= 1.0:
        edge_plane_code |= 0x010
    if point[0] - point[2] >= 1.0:
        edge_plane_code |= 0x020
    if -point[0] + point[2] > 1.0:
        edge_plane_code |= 0x040
    if -point[0] - point[2] > 1.0:
        edge_plane_code |= 0x080

    if point[1] + point[2] >= 1.0:
        edge_plane_code |= 0x100
    if point[1] - point[2] >= 1.0:
        edge_plane_code |= 0x200
    if -point[1] + point[2] > 1.0:
        edge_plane_code |= 0x400
    if -point[1] - point[2] > 1.0:
        edge_plane_code |= 0x800
    return edge_plane_code


def bevel_3d(point):
    """
    Which of the eight corner plane(s) is point P outside of?
    """
    corner_plane_code = 0
    if (point[0] + point[1] + point[2]) >= 1.5:
        corner_plane_code |= 0x01
    if (point[0] + point[1] - point[2]) >= 1.5:
        corner_plane_code |= 0x02
    if (point[0] - point[1] + point[2]) >= 1.5:
        corner_plane_code |= 0x04
    if (point[0] - point[1] - point[2]) >= 1.5:
        corner_plane_code |= 0x08
    if (-point[0] + point[1] + point[2]) > 1.5:
        corner_plane_code |= 0x10
    if (-point[0] + point[1] - point[2]) > 1.5:
        corner_plane_code |= 0x20
    if (-point[0] - point[1] + point[2]) > 1.5:
        corner_plane_code |= 0x40
    if (-point[0] - point[1] - point[2]) > 1.5:
        corner_plane_code |= 0x80
    return corner_plane_code


def check_point(point_a, point_b, alpha, mask):
    """
    Test the point "alpha" of the way from P1 to P2
    See if it is on a face of the cube
    Consider only faces in "mask"
    """
    plane_point_x = lerp(alpha, point_a[0], point_b[0])
    plane_point_y = lerp(alpha, point_a[1], point_b[1])
    plane_point_z = lerp(alpha, point_a[2], point_b[2])

    plane_point = (plane_point_x, plane_point_y, plane_point_z)
    return face_plane(plane_point) & mask


def check_line(point_a, point_b, outcode_diff):
    """
    /* Compute intersection of P1 --> P2 line segment with face planes */
    /* Then test intersection point to see if it is on cube face       */
    /* Consider only face planes in "outcode_diff"                     */
    /* Note: Zero bits in "outcode_diff" means face line is outside of */
    """
    if (0x01 & outcode_diff) != 0:
        if check_point(point_a, point_b, (0.5 - point_a[0])/(point_b[0] - point_a[0]), 0x3e) == INSIDE:
            return INSIDE
    if (0x02 & outcode_diff) != 0:
        if check_point(point_a, point_b, (-0.5 - point_a[0])/(point_b[0] - point_a[0]), 0x3d) == INSIDE:
            return INSIDE
    if (0x04 & outcode_diff) != 0:
        if check_point(point_a, point_b, (0.5 - point_a[1])/(point_b[1] - point_a[1]), 0x3b) == INSIDE:
            return INSIDE
    if (0x08 & outcode_diff) != 0:
        if check_point(point_a, point_b, (-0.5 - point_a[1])/(point_b[1] - point_a[1]), 0x37) == INSIDE:
            return INSIDE
    if (0x10 & outcode_diff) != 0:
        if check_point(point_a, point_b, (0.5 - point_a[2])/(point_b[2] - point_a[2]), 0x2f) == INSIDE:
            return INSIDE
    if (0x20 & outcode_diff) != 0:
        if check_point(point_a, point_b, (-0.5 - point_a[2])/(point_b[2] - point_a[2]), 0x1f) == INSIDE:
            return INSIDE
    return OUTSIDE


def point_triangle_intersection(p, t):
    """
    Test if 3D point is inside 3D triangle

    @type p: list[float]
    @type t: Triangle
    """
    # /* First, a quick bounding-box test:                               */
    # /* If P is outside triangle bbox, there cannot be an intersection. */

    # add/sub EPS as buffer to avoid an floating point issue

    if p[0] > t.max(0) + EPS:
        return OUTSIDE
    if p[1] > t.max(1) + EPS:
        return OUTSIDE
    if p[2] > t.max(2) + EPS:
        return OUTSIDE
    if p[0] < t.min(0) - EPS:
        return OUTSIDE
    if p[1] < t.min(1) - EPS:
        return OUTSIDE
    if p[2] < t.min(2) - EPS:
        return OUTSIDE

    # /* For each triangle side, make a vector out of it by subtracting vertexes; */
    # /* make another vector from one vertex to point P.                          */
    # /* The crossproduct of these two vectors is orthogonal to both and the      */
    # /* signs of its X,Y,Z components indicate whether P was to the inside or    */
    # /* to the outside of this triangle side.                                    */

    vect12 = np.subtract(t.v1, t.v2)
    vect1h = np.subtract(t.v1, p)
    cross12_1p = cross_product(vect12, vect1h)
    sign12 = sign3(cross12_1p)  # /* Extract X,Y,Z signs as 0..7 or 0...63 integer */

    vect23 = np.subtract(t.v2, t.v3)
    vect2h = np.subtract(t.v2, p)
    cross23_2p = cross_product(vect23, vect2h)
    sign23 = sign3(cross23_2p)

    vect31 = np.subtract(t.v3, t.v1)
    vect3h = np.subtract(t.v3, p)
    cross31_3p = cross_product(vect31, vect3h)
    sign31 = sign3(cross31_3p)

    # /* If all three cross product vectors agree in their component signs,  */
    # /* then the point must be inside all three.                            */
    # /* P cannot be OUTSIDE all three sides simultaneously.                 */

    if (sign12 & sign23 & sign31) == 0:
        return OUTSIDE
    return INSIDE


def t_c_intersection(triangle):
    """
    /**********************************************/
    /* This is the main algorithm procedure.      */
    /* Triangle t is compared with a unit cube,   */
    /* centered on the origin.                    */
    /* It returns INSIDE (0) or OUTSIDE(1) if t   */
    /* intersects or does not intersect the cube. */
    /**********************************************/

    @type triangle: Triangle
    """

    # long v1_test,v2_test,v3_test;
    # float d,denom;
    # Point3 vect12,vect13,norm;
    # Point3 hitpp,hitpn,hitnp,hitnn;

    # /* First compare all three vertexes with all six face-planes */
    # /* If any vertex is inside the cube, return immediately!     */

    v1_test = face_plane(triangle.v1)
    v2_test = face_plane(triangle.v2)
    v3_test = face_plane(triangle.v3)
    if v1_test == INSIDE:
        return INSIDE
    if v2_test == INSIDE:
        return INSIDE
    if v3_test == INSIDE:
        return INSIDE

    # /* If all three vertexes were outside of one or more face-planes, */
    # /* return immediately with a trivial rejection!                   */

    if (v1_test & v2_test & v3_test) != INSIDE:
        return OUTSIDE

    # /* Now do the same trivial rejection test for the 12 edge planes */

    v1_test |= bevel_2d(triangle.v1) << 8
    v2_test |= bevel_2d(triangle.v2) << 8
    v3_test |= bevel_2d(triangle.v3) << 8
    if (v1_test & v2_test & v3_test) != INSIDE:
        return OUTSIDE

    # /* Now do the same trivial rejection test for the 8 corner planes */

    v1_test |= bevel_3d(triangle.v1) << 24
    v2_test |= bevel_3d(triangle.v2) << 24
    v3_test |= bevel_3d(triangle.v3) << 24
    if (v1_test & v2_test & v3_test) != INSIDE:
        return OUTSIDE

    # /* If vertex 1 and 2, as a pair, cannot be trivially rejected */
    # /* by the above tests, then see if the v1-->v2 triangle edge  */
    # /* intersects the cube.  Do the same for v1-->v3 and v2-->v3. */
    # /* Pass to the intersection algorithm the "OR" of the outcode */
    # /* bits, so that only those cube faces which are spanned by   */
    # /* each triangle edge need be tested.                         */

    if (v1_test & v2_test) == 0:
        if check_line(triangle.v1, triangle.v2, v1_test | v2_test) == INSIDE:
            return INSIDE
    if (v1_test & v3_test) == 0:
        if check_line(triangle.v1, triangle.v3, v1_test | v3_test) == INSIDE:
            return INSIDE
    if (v2_test & v3_test) == 0:
        if check_line(triangle.v2, triangle.v3, v2_test | v3_test) == INSIDE:
            return INSIDE

    # /* By now, we know that the triangle is not off to any side,     */
    # /* and that its sides do not penetrate the cube.  We must now    */
    # /* test for the cube intersecting the interior of the triangle.  */
    # /* We do this by looking for intersections between the cube      */
    # /* diagonals and the triangle...first finding the intersection   */
    # /* of the four diagonals with the plane of the triangle, and     */
    # /* then if that intersection is inside the cube, pursuing        */
    # /* whether the intersection point is inside the triangle itself. */

    # /* To find plane of the triangle, first perform crossproduct on  */
    # /* two triangle side vectors to compute the normal vector.       */

    vect12 = np.subtract(triangle.v1, triangle.v2)
    vect13 = np.subtract(triangle.v1, triangle.v3)
    norm = cross_product(vect12, vect13)

    # /* The normal vector "norm" X,Y,Z components are the coefficients */
    # /* of the triangles AX + BY + CZ + D = 0 plane equation.  If we   */
    # /* solve the plane equation for X=Y=Z (a diagonal), we get        */
    # /* -D/(A+B+C) as a metric of the distance from cube center to the */
    # /* diagonal/plane intersection.  If this is between -0.5 and 0.5, */
    # /* the intersection is inside the cube.  If so, we continue by    */
    # /* doing a point/triangle intersection.                           */
    # /* Do this for all four diagonals.                                */

    d = norm[0] * triangle.v1[0] + norm[1] * triangle.v1[1] + norm[2] * triangle.v1[2]

    # /* if one of the diagonals is parallel to the plane, the other will intersect the plane */
    denom = norm[0] + norm[1] + norm[2]
    hitpp = [0.0, 0.0, 0.0]
    if abs(denom) > EPS:
        # /* skip parallel diagonals to the plane; division by 0 can occur */
        hitpp[0] = hitpp[1] = hitpp[2] = d / denom
        if abs(hitpp[0]) <= 0.5:
            if point_triangle_intersection(hitpp, triangle) == INSIDE:
                return INSIDE

    denom = norm[0] + norm[1] - norm[2]
    hitpn = [0.0, 0.0, 0.0]
    if abs(denom) > EPS:
        hitpn[0] = hitpn[1] = d / denom
        hitpn[2] = -hitpn[0]
        if abs(hitpn[0]) <= 0.5:
            if point_triangle_intersection(hitpn, triangle) == INSIDE:
                return INSIDE

    denom = norm[0] - norm[1] + norm[2]
    hitnp = [0.0, 0.0, 0.0]
    if abs(denom) > EPS:
        hitnp[0] = hitnp[2] = d / denom
        hitnp[1] = -hitnp[0]
        if abs(hitnp[0]) <= 0.5:
            if point_triangle_intersection(hitnp, triangle) == INSIDE:
                return INSIDE

    denom = norm[0] - norm[1] - norm[2]
    hitnn = [0.0, 0.0, 0.0]
    if abs(denom) > EPS:
        hitnn[0] = d / denom
        hitnn[1] = hitnn[2] = -hitnn[0]
        if abs(hitnn[0]) <= 0.5:
            if point_triangle_intersection(hitnn, triangle) == INSIDE:
                return INSIDE

    # /* No edge touched the cube; no cube diagonal touched the triangle. */
    # /* We're done...there was no intersection.                          */

    return OUTSIDE
