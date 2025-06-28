from typing import Self

from panda3d.core import (
    GeomNode,
    GeomVertexFormat,
    NodePath,
    Vec3,
)
from pydantic.color import Color

from .base import DynMeshBase
from .mesh_generation import generate_mesh


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
        if self.settings.floating_point_precision is None:
            return number

        return round(number, self.settings.floating_point_precision)

    def __eq__(self, other):
        """
        Check if two DynMeshes contains the same data
        """

        if len(self.vertices) != len(other.vertices):
            return False

        for i, (x, y, z) in enumerate(self.vertices):
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

    def move_vectors(self, vec: Vec3):
        self.vertices = [x + vec for x in self.vertices]

    def generate_panda_3d_mesh(
        name: str = "surface", vertex_format: GeomVertexFormat | None = None
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
