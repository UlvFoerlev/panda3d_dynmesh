from panda3d.core import (
    Vec3,
    Point3,
    Point2,
)
from pydantic import BaseModel, ConfigDict
from typing import Iterable, Collection
from pydantic import field_serializer, field_validator
from pydantic.color import Color


class DynMeshBase(BaseModel):
    """
    Base class
    Type validation.
    """

    vertices: list[Point3] = []
    triangles: list[tuple[int, int, int]] = []
    normals: list[Vec3] = []
    uvs: list[Point2] = []
    colors: list[Color] = []

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
            color: Collection[float | int] | Color | str
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
                    return Color(color) # type: ignore

                if isinstance(color[0], float):
                    r, g, b = [int(x) * 255 for x in color[0:3]]
                    a = float(color[3]) if len(color) == 4 else 1.0
                    return Color((r, g, b, a))

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
