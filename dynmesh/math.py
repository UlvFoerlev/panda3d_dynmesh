from numpy import cross, eye, dot, ndarray, identity
from scipy.linalg import expm, norm
from panda3d.core import Vec3, Point3


def rotation_matrix(axis: Vec3, theta: float) -> ndarray:
    """
    Create a rotation matrix from axis and rotation theta.
    Returns identity matrix if axis is a zero vector or if rotation is zero.

    Keyword arguments:
    axis -- 3D axis (Vec3)
    theta -- rotation in radians (float)

    Returns:
    rotation matrix (ndarray)

    """
    if axis.length() == 0 or theta == 0:
        return identity(3)

    return expm(cross(eye(3), axis / norm(axis) * theta))


def rotate_point(
    point: Point3, rotation_matrix: ndarray, pivot: Point3 | None = None
) -> Point3:
    """
    Use rotation matrix to rotate a point around in 3D Space.

    Keyword arguments:
    point -- 3D point in space (Point3)
    rotation_matrix -- Numpy rotation.
        (NDarray) (see 'rotation_matrix' above)
    pivot -- pivot point to rotate around, defaults to Vec3(0, 0, 0)

    Returns:
    rotated point (Point3)
    """

    pivot = pivot or Point3(0, 0, 0)

    return Point3(*dot(rotation_matrix, point - pivot) + pivot)  # type: ignore