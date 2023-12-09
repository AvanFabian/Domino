from OpenGL.GL import *
from OpenGL.GLU import *

WIDTH, HEIGHT = 1400, 800
TableXSize = 1400
TableYSize = 800

# create 3D cube
vertices = (
    (1, 1, 1),  # 0
    (-1, 1, 1),  # 1
    (-1, -1, 1),  # 2
    (1, -1, 1),  # 3
    (1, 1, -1),  # 4
    (-1, 1, -1),  # 5
    (-1, -1, -1),  # 6
    (1, -1, -1),  # 7
)

surfaces = (
    (0, 1, 2, 3),  # surface 0
    (4, 5, 6, 7),  # surface 1
    (0, 3, 7, 4),  # surface 2
    (1, 2, 6, 5),  # surface 3
    (0, 1, 5, 4),  # surface 4
    (3, 2, 6, 7),  # surface 5
)

normals = [
    (0, 0, -1),  # surface 0
    (0, 0, 1),  # surface 1
    (-1, 0, 0),  # surface 2
    (1, 0, 0),  # surface 3
    (0, -1, 0),  # surface 4
    (0, 1, 0)  # surface 5
]

colors = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 1, 0),
    (1, 0, 1),
    (0, 1, 1)
)

uv_coords = (
    (1, 1),  # 0
    (0, 1),  # 1
    (0, 0),  # 2
    (1, 0),  # 3
    (1, 1),  # 4
    (0, 1),  # 5
    (0, 0),  # 6
    (1, 0),  # 7
)

def cube():
    glBegin(GL_QUADS)
    for i_surface, surface in enumerate(surfaces):
        # print(f"surface: {surface}")
        glNormal3fv(normals[i_surface])
        for vertex in surface:
            # print(f"vertex: {vertex}")
            glTexCoord2fv(uv_coords[vertex])
            glVertex3fv(vertices[vertex])
    glEnd()