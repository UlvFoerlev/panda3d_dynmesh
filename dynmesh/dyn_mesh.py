from typing import Self

from panda3d.core import GeomNode, GeomVertexFormat, NodePath, Vec3, Point3, Vec2D, Vec2
from pydantic.color import Color
from pydantic import conint
from scipy.spatial.transform import Rotation

from .base import DynMeshBase
from .mesh_generation import generate_mesh
from .math import rotate_point, rotation_matrix
import numpy as np

class DynMesh(DynMeshBase):
    def merge(self, other: Self) -> None:
        if not other or not other.vertices:
            return

        original = len(self.vertices)
        self.vertices += other.vertices
        self.normals += other.normals
        self.uvs += other.uvs

        new_triangles = [
            (original + i0, original + i1, original + i2)
            for (i0, i1, i2) in other.triangles
        ]
        self.triangles += new_triangles

    def _round(self, number: float):
        return round(number, 4)
        
        # if self.settings.floating_point_precision is None:
        #     return number

        # return round(number, self.settings.floating_point_precision)

    def __eq__(self, other):
        """
        Check if two DynMeshes contains the same data
        """

        if len(self.vertices) != len(other.vertices):
            return False

        for i, p in enumerate(self.vertices):
            ox, oy, oz = other.vertices[i]

            if self._round(x) != self._round(ox):
                return False

            if self._round(y) != self._round(oy):
                return False

            if self._round(z) != self._round(oz):
                return False

        if len(self.normals) != len(other.normals):
            return False

        for i, (x, y, z) in enumerate(self.normals):
            ox, oy, oz = other.normals[i]

            if self._round(x) != self._round(ox):
                return False

            if self._round(y) != self._round(oy):
                return False

            if self._round(z) != self._round(oz):
                return False

        return (
            self.triangles == other.triangles
            and self.uvs == other.uvs
            and self.normals == other.normals
        )

    def move(self, vec: Vec3):
        self.vertices = [x + vec for x in self.vertices]

    def rotate(
        self, radians: float, axis: Vec3 | None = None, pivot: Point3 | None = None
    ):
        axis = axis or Vec3(0, 0, 0)
        pivot = pivot or Point3(0, 0, 0)

        m = rotation_matrix(axis=axis, theta=radians)

        self.vertices = [rotate_point(x, m, pivot) for x in self.vertices]

    def generate_panda_3d_mesh(
        self, name: str = "surface", vertex_format: GeomVertexFormat | None = None
    ) -> tuple[GeomNode, NodePath]:
        """
        Generate Panda3D Mesh based on DynMesh data.
        """

        return generate_mesh(
            vertex_format=vertex_format,
            name=name,
            vertices=self.vertices,
            triangles=self.triangles,
            normals=self.normals,
            uvs=self.uvs,
            colors=self.colors,
        )

    def add_plane(
        self,
        position: Point3 | None = None,
        rotation: Vec3 | None = None,
        x_vertices: conint(ge=2) = 2,  # type: ignore
        y_vertices: conint(ge=2) = 2,  # type: ignore
        size: Vec2 | None = None,
        two_sided: bool = False,
    ) -> None:
        size = size or Vec2(1.0, 1.0)
        position = position or Point3(0, 0, 0)
        rotation = rotation or Vec3(0, 0, 0)
