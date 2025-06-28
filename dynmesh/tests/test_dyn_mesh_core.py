from dynmesh.core import DynMeshCore
import pytest
from typing import Collection
from panda3d.core import Point3, Vec3, Point2
from pydantic_core import PydanticSerializationError
from pydantic import ValidationError
from pydantic.color import Color


def test_dyn_mesh__empty():
    dyn_mesh = DynMeshCore()

    geometry, node = dyn_mesh.generate_mesh(name="test_mesh")

    assert geometry
    assert node


@pytest.mark.parametrize(argnames="vertices", argvalues=[((1, 1, 1)), ([3, 2, 1])])
def test_dyn_mesh__type_serilization__vertices(vertices):
    dyn_mesh = DynMeshCore(vertices=[vertices])

    assert isinstance(dyn_mesh.vertices[0], Point3)

    dyn_mesh_dict = dyn_mesh.model_dump()
    assert isinstance(dyn_mesh_dict["vertices"][0], Point3)

    try:
        dyn_mesh.model_dump_json()
    except PydanticSerializationError:
        assert False
    else:
        assert True


@pytest.mark.parametrize(argnames="normals", argvalues=[((1, 1, 1)), ([3, 2, 1])])
def test_dyn_mesh__type_serilization__normals(normals):
    dyn_mesh = DynMeshCore(normals=[normals])

    assert isinstance(dyn_mesh.normals[0], Vec3)
    assert dyn_mesh.normals[0].normalize() is True

    dyn_mesh_dict = dyn_mesh.model_dump()
    assert isinstance(dyn_mesh_dict["normals"][0], Vec3)

    try:
        dyn_mesh.model_dump_json()
    except PydanticSerializationError:
        assert False
    else:
        assert True


def test_dyn_mesh__type_serilization__normals__zero_vector():
    with pytest.raises(ValidationError):
        DynMeshCore(normals=[(0, 0, 0)])


@pytest.mark.parametrize(
    argnames="uvs", argvalues=[((0, 1)), ([0, 0]), ([0.5, 0.5]), ((1, 1))]
)
def test_dyn_mesh__type_serilization__uvs(uvs):
    dyn_mesh = DynMeshCore(uvs=[uvs])

    assert isinstance(dyn_mesh.uvs[0], Point2)

    dyn_mesh_dict = dyn_mesh.model_dump()
    assert isinstance(dyn_mesh_dict["uvs"][0], Point2)

    try:
        dyn_mesh.model_dump_json()
    except PydanticSerializationError:
        assert False
    else:
        assert True


@pytest.mark.parametrize(
    argnames="uv", argvalues=[((-1, 0)), ([0, -1]), ([2, 0]), ((0, 2))]
)
def test_dyn_mesh__type_serilization__uvs__outside_bounds(uv):
    with pytest.raises(ValidationError):
        DynMeshCore(uvs=[uv])


@pytest.mark.parametrize(
    argnames=["color_input", "color_output"],
    argvalues=[((255, 255, 255, 1), (255, 255, 255, 1))],
)
def test_dyn_mesh__type_serilization__color(color_input, color_output: Color):
    dyn_mesh = DynMeshCore(colors=[color_input])

    color_result = dyn_mesh.colors[0]
    assert isinstance(color_result, Color)

    color_result_tuple = color_result.as_rgb_tuple()
    if len(color_result_tuple) == 3:
        color_result_tuple = (*color_result_tuple, 1)

    assert color_result_tuple == color_output

    dyn_mesh_dict = dyn_mesh.model_dump()
    assert isinstance(dyn_mesh_dict["colors"][0], Color)

    try:
        dyn_mesh.model_dump_json()
    except PydanticSerializationError:
        assert False
    else:
        assert True
