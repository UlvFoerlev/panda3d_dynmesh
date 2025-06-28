from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
    Vec3,
    Point3,
    Point2,
)
from pydantic import BaseModel, ConfigDict
from typing import Self, Iterable, Collection
from pydantic import model_validator, field_serializer, field_validator
from .settings import DynMeshSettings
from pydantic.color import Color


class DynMeshCore(BaseModel):
    vertices: list[Point3] = []
    triangles: list[tuple[int, int, int]] = []
    normals: list[Vec3] = []
    uvs: list[Point2] = []
    colors: list[Color] = []

    settings: DynMeshSettings = DynMeshSettings(floating_point_precision=2)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("vertices", mode="before")
    @classmethod
    def type_coerse_vertices(cls, vertices: Iterable[Collection[float | int]]):
        return [Point3(x, y, z) for (x, y, z) in vertices]

    @field_serializer("vertices", when_used="json")
    def serialize_vertices_json(self, vertices: Iterable[Collection[float | int]]):
        return [[x, y, z] for (x, y, z) in vertices]

    @field_validator("normals", mode="before")
    @classmethod
    def type_coerse_normals(cls, normals: Iterable[Collection[float | int]]):
        def _normalize(vec: Vec3, i: int):
            if vec.length() == 0:
                raise ValueError(f"Zero Vector at position {i} cannot be normalized.")

            if vec.length() == 1:
                return vec

            return vec.normalized()

        return [_normalize(Vec3(x, y, z), i) for i, (x, y, z) in enumerate(normals)]

    @field_serializer("normals", when_used="json")
    def serialize_normals_json(self, normals: Iterable[Collection[float | int]]):
        return [[x, y, z] for (x, y, z) in normals]

    @field_validator("uvs", mode="before")
    @classmethod
    def type_coerse_uvs(cls, uvs: Iterable[Collection[float | int]]):
        def _validate_uv(uv: Point2) -> Point2:
            if not (0 <= uv.x <= 1):
                raise ValueError(f"Both coordinates of {uv} must be between 0 and 1.")

            if not (0 <= uv.y <= 1):
                raise ValueError(f"Both coordinates of {uv} must be between 0 and 1.")

            return uv

        return [_validate_uv(Point2(x, y)) for (x, y) in uvs]

    @field_serializer("uvs", when_used="json")
    def serialize_uvs_json(self, uvs: Iterable[Collection[float | int]]):
        return [[x, y] for (x, y) in uvs]

    @field_validator("colors", mode="before")
    @classmethod
    def type_coerse_colors(
        cls, colors: Iterable[Collection[float | int] | Color | str]
    ):
        def _decode_color(
            color: Color
            | tuple[int, int, int]
            | tuple[float, float, float]
            | list[int]
            | list[float],
        ):
            if isinstance(color, Color):
                return color

            if isinstance(color, str):
                return Color(color)

            if isinstance(color, tuple | list):
                if not (3 <= len(color) <= 4):
                    raise ValueError(
                        "Color must have either 3 or 4 elements. (R, G, B) or (R, G, B, A)."
                    )
                if isinstance(color[0], int):
                    return Color(color)

                if isinstance(color[0], float):
                    r, g, b = [int(x) * 255 for x in color[0:3]]
                    a = color[3] if len(color) == 4 else 1
                    return Color([r, g, b, a])

            raise TypeError(
                f"Could not recognice color '{color}' of type '{type(color)}'."
            )

        return [_decode_color(color) for color in colors]

    @field_serializer("colors", when_used="json")
    def serialize_colors_json(self, colors: Iterable[Collection[float | int]]):
        def _color(color) -> tuple[int, int, int, float]:
            c = color.as_rgb_tuple()
            a = c[3] if len(c) == 4 else 1.0
            r, g, b, *_ = c

            return (r, g, b, a)

        return [_color(color) for color in colors]

    def generate_mesh(
        self, name: str = "surface", vertex_format: GeomVertexFormat | None = None
    ) -> tuple[GeomNode, NodePath]:
        """
        Generates Panda3D Mesh from Data
        """
        vertex_format = vertex_format or GeomVertexFormat.get_v3n3c4t2()
        vertex_data = GeomVertexData("surface", vertex_format, Geom.UH_static)
        position_writer = GeomVertexWriter(vertex_data, "vertex")
        normal_writer = GeomVertexWriter(vertex_data, "normal")
        color_writer = GeomVertexWriter(vertex_data, "color")
        uv_writer = GeomVertexWriter(vertex_data, "texcoord")

        tris_prim = GeomTriangles(Geom.UH_static)
        tris_prim.reserve_num_vertices(len(self.vertices))

        geometry = Geom(vertex_data)

        def _normal_write(vertex_index):
            if not vertex_format.has_column("normal"):
                return

            if vertex_format not in {}:
                return

            normal = self.normals[vertex_index]
            normal_writer.add_data3(normal)

        def _color_write(vertex_index: int):
            if not vertex_format.has_column("color"):
                return

            if not self.colors or len(self.colors) < vertex_index:
                color = (1.0, 1.0, 1.0, 1.0)

            color: Color = self.colors[vertex_index].as_rgb_tuple()
            if len(color) == 3:
                color = (*color, 1)

            color_writer.add_data4(tuple(float(x / 255) for x in color))  # type: ignore

        def _uv_write(vertex_index: int):
            if not vertex_format.has_column("texcoord"):
                return

            uv = self.uvs[vertex_index]
            uv_writer.add_data2(uv)

        def _generate_mesh_by_vertices():
            """
            num vertices > num triangles
            """

            for i, (x, y, z) in enumerate(self.vertices):
                if i < len(self.triangles):
                    tris_prim.add_vertices(*self.triangles[i])

                position_writer.add_data3((x, y, z))
                _color_write(vertex_index=i)
                _uv_write(vertex_index=i)
                _normal_write(vertex_index=i)

        def _generate_mesh_by_triangles():
            """
            num triangles > num vertices
            """

            for i, face in enumerate(self.triangles):
                tris_prim.add_vertices(*face)

                if i < len(self.vertices):
                    x, y, z = tuple(self.vertices[i])

                    position_writer.add_data3((x, y, z))
                    _color_write(vertex_index=i)
                    _uv_write(vertex_index=i)
                    _normal_write(vertex_index=i)

        if len(self.vertices) >= len(self.triangles):
            _generate_mesh_by_vertices()
        else:
            _generate_mesh_by_triangles()

        geometry.add_primitive(tris_prim)

        geometry_node = GeomNode(name=name)
        geometry_node.add_geom(geometry)

        node_path = NodePath(geometry_node)

        return geometry_node, node_path

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

    # @model_validator(mode="before")
    # @classmethod
    # def _mesh_validator(cls, data: dict[str, Any]) -> dict[str, Any]:
    #     """
    #     Helper converting sets and lists of data to the appropiate data structues,
    #     such as vectors and points
    #     """

    #     if "vertices" in data and isinstance(data["vertices"][0], tuple | list):  # type: ignore
    #         data["vertices"] = [Point3(x, y, z) for (x, y, z) in data["vertices"]]  # type: ignore

    #     if "normals" in data and isinstance(data["normals"][0], tuple | list):  # type: ignore
    #         data["normals"] = [Vec3(x, y, z) for (x, y, z) in data["normals"]]  # type: ignore

    #     if "uvs" in data and isinstance(data["uvs"][0], tuple | list):
    #         data["uvs"] = [Point2(x, y) for (x, y) in data["uvs"]]

    #     return data  # type: ignore

    def _round(self, number: float):
        if self.settings.floating_point_precision is None:
            return number

        return round(number, self.settings.floating_point_precision)

    def __eq__(self, other):
        """
        Floating point errors in vertices, makes identical meshes stored different locations in memory unequal.
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

    def move_by_vector(self, vec: Vec3):
        self.vertices = [x + vec for x in self.vertices]
