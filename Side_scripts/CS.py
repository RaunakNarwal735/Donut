import moderngl
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from pyrr import Matrix44

# Initialize Pygame with OpenGL context
pygame.init()
screen = pygame.display.set_mode((1280, 720), DOUBLEBUF | OPENGL)
clock = pygame.time.Clock()

# Create ModernGL context
ctx = moderngl.create_context()
ctx.enable(moderngl.DEPTH_TEST)

# Vertex shader
vertex_shader = """
#version 330
in vec3 in_position;
uniform mat4 mvp;
void main() {
    gl_Position = mvp * vec4(in_position, 1.0);
}
"""

# Fragment shader
fragment_shader = """
#version 330
out vec4 fragColor;
uniform vec3 color;
void main() {
    fragColor = vec4(color, 1.0);
}
"""

# Compile shaders
prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
mvp_uniform = prog['mvp']
color_uniform = prog['color']

# Define axes lines and grid as vertex arrays
axes_vertices = np.array([
    # X axis
    -5, 0, 0,   5, 0, 0,
    # Y axis
    0, -5, 0,   0, 5, 0,
    # Z axis
    0, 0, -5,   0, 0, 5,
], dtype='f4')

axes_vbo = ctx.buffer(axes_vertices.tobytes())
axes_vao = ctx.simple_vertex_array(prog, axes_vbo, 'in_position')

# Grid plane (XZ plane example)
grid_lines = []
grid_size = 5
for i in range(-grid_size, grid_size + 1):
    grid_lines += [i, 0, -grid_size, i, 0, grid_size]  # Vertical lines
    grid_lines += [-grid_size, 0, i, grid_size, 0, i]  # Horizontal lines
grid_vertices = np.array(grid_lines, dtype='f4')
grid_vbo = ctx.buffer(grid_vertices.tobytes())
grid_vao = ctx.simple_vertex_array(prog, grid_vbo, 'in_position')

# Projection matrix
proj = Matrix44.perspective_projection(45.0, 1280 / 720, 0.1, 100.0)

# Camera setup
camera_pos = np.array([10.0, 10.0, 10.0])
target = np.array([0.0, 0.0, 0.0])
view = Matrix44.look_at(camera_pos, target, [0.0, 1.0, 0.0])

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    ctx.clear(0.05, 0.05, 0.05)

    mvp = proj * view
    mvp_uniform.write(mvp.astype('f4').tobytes())

    # Draw axes
    color_uniform.value = (1.0, 1.0, 1.0)
    axes_vao.render(moderngl.LINES)

    # Draw grid
    color_uniform.value = (0.8, 0.8, 0.8)
    grid_vao.render(moderngl.LINES)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()