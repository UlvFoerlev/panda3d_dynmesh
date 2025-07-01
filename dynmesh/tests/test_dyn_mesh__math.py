import numpy as np
import pytest
from panda3d.core import Point3, Vec3

from dynmesh.math import rotate_point, rotation_matrix


@pytest.mark.parametrize(
    argnames=["axis", "theta", "result_matrix"],
    argvalues=[
        (Vec3(1, 0, 0), 0, np.identity(3)),
        (Vec3(0, 0, 0), 1.2, np.identity(3)),
        (
            Vec3(1, 0, 0),
            1.2,
            np.array(
                [
                    [1.0000000, 0.0000000, 0.0000000],
                    [0.0000000, 0.36235771, -0.9320391],
                    [0.0000000, 0.9320391, 0.36235771],
                ]
            ),
        ),
        (
            Vec3(1, 3, 2),
            2.1,
            np.array(
                [
                    [
                        [-0.3973571, -0.1389378, 0.9070852],
                        [0.7838718, 0.4625550, 0.4142316],
                        [-0.4771292, 0.8756365, -0.0748901],
                    ]
                ]
            ),
        ),
        (
            Vec3(0, 0, 1),
            90 * np.pi / 180,
            np.array(
                [
                    [
                        [0.0, -1.0, 0.0],
                        [1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ]
                ]
            ),
        ),
    ],
)
def test_rotate_matrix(axis: Vec3, theta: float, result_matrix: np.ndarray):
    m = rotation_matrix(axis=axis, theta=theta)

    assert np.all(np.isclose(m, result_matrix, 0.01, 0.01))


@pytest.mark.parametrize(
    argnames=["point", "rotation_matrix", "pivot", "expected_result"],
    argvalues=[
        (
            Point3(1, 0, 0),
            [
                [-1.0000000, 0.0000000, 0.0000000],
                [0.0000000, -1.0000000, 0.0000000],
                [0.0000000, 0.0000000, 1.0000000],
            ],
            Point3(0, 0, 0),
            Point3(-1, 0, 0),
        ),
        (
            Point3(1, 0, 0),
            [
                [-1.0000000, 0.0000000, 0.0000000],
                [0.0000000, -1.0000000, 0.0000000],
                [0.0000000, 0.0000000, 1.0000000],
            ],
            Point3(0.5, 0, 0),
            Point3(0, 0, 0),
        ),
    ],
)
def test_rotate_point(
    point: Point3, rotation_matrix: np.ndarray, pivot: Point3, expected_result: Point3
):
    new_point = rotate_point(point=point, rotation_matrix=rotation_matrix, pivot=pivot)

    assert new_point == expected_result
