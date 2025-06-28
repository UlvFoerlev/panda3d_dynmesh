from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    NodePath,
)
from pydantic.color import Color
from panda3d.core import (
    Vec3,
    Point3,
    Point2,
)


def generate_mesh(
    vertices: list[Point3],
    triangles: list[tuple[int, int, int]],
    normals: list[Vec3],
    uvs: list[Point2],
    colors: list[Color],
    name: str,
    vertex_format: GeomVertexFormat,
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
    tris_prim.reserve_num_vertices(len(vertices))

    geometry = Geom(vertex_data)

    def _normal_write(vertex_index):
        if not vertex_format.has_column("normal"):
            return

        if vertex_format not in {}:
            return

        normal = normals[vertex_index]
        normal_writer.add_data3(normal)

    def _color_write(vertex_index: int):
        if not vertex_format.has_column("color"):
            return

        if not colors or len(colors) < vertex_index:
            color = (1.0, 1.0, 1.0, 1.0)

        color: Color = colors[vertex_index].as_rgb_tuple()
        if len(color) == 3:
            color = (*color, 1)

        color_writer.add_data4(tuple(float(x / 255) for x in color))  # type: ignore

    def _uv_write(vertex_index: int):
        if not vertex_format.has_column("texcoord"):
            return

        uv = uvs[vertex_index]
        uv_writer.add_data2(uv)

    def _generate_mesh_by_vertices():
        """
        num vertices > num triangles
        """

        for i, (x, y, z) in enumerate(vertices):
            if i < len(triangles):
                tris_prim.add_vertices(*triangles[i])

            position_writer.add_data3((x, y, z))
            _color_write(vertex_index=i)
            _uv_write(vertex_index=i)
            _normal_write(vertex_index=i)

    def _generate_mesh_by_triangles():
        """
        num triangles > num vertices
        """

        for i, face in enumerate(triangles):
            tris_prim.add_vertices(*face)

            if i < len(vertices):
                x, y, z = tuple(vertices[i])

                position_writer.add_data3((x, y, z))
                _color_write(vertex_index=i)
                _uv_write(vertex_index=i)
                _normal_write(vertex_index=i)

    if len(vertices) >= len(triangles):
        _generate_mesh_by_vertices()
    else:
        _generate_mesh_by_triangles()

    geometry.add_primitive(tris_prim)

    geometry_node = GeomNode(name=name)
    geometry_node.add_geom(geometry)

    node_path = NodePath(geometry_node)

    return geometry_node, node_path
