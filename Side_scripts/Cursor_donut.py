import pygame
import math
import colorsys

pygame.init()

# Screen and grid setup
WIDTH, HEIGHT = 1280, 720
x_separator, y_separator = 3, 6
columns = WIDTH // x_separator
rows = HEIGHT // y_separator
screen_size = rows * columns
x_offset = columns / 2
y_offset = rows / 2
font = pygame.font.Font("NK57 Monospace Cd Bd.otf", 20)

# Torus configuration
R1, R2 = 1.1, 2.5
theta_spacing = 2
phi_spacing = 2
light = [0, 1, -1]

# Rotation angles
A, B, C = 0.0, 0.0, 0.0

# Rotation state
active_axes = set()
auto_rotate = False
dragging = False
last_mouse_pos = None
sensitivity = 0.01
hue = 0
transparent_mode = False

# Colors
SHADOW_COLOR = (30, 40, 80)
MID_COLOR = (180, 180, 200)
HIGHLIGHT_COLOR = (220, 240, 255)

# Utility functions
def normalize(v):
    l = math.sqrt(sum(i * i for i in v))
    return [i / l for i in v] if l != 0 else v

def dot(a, b):
    return sum(i * j for i, j in zip(a, b))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def project_point(px, py, pz):
    z = pz + 5
    ooz = 1 / z
    xp = int(x_offset + 80 * ooz * px)
    yp = int(y_offset + 40 * ooz * py)
    return xp, yp, ooz

# Init screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Donut with Axis/Plane Control")
clock = pygame.time.Clock()
run = True

while run:
    screen.fill((0, 0, 0))
    zbuffer = [0.0] * screen_size
    colorbuffer = [(0, 0, 0, 0)] * screen_size

    if dragging and last_mouse_pos:
        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - last_mouse_pos[0], my - last_mouse_pos[1]
        last_mouse_pos = (mx, my)
        if 'X' in active_axes: A += dy * sensitivity
        if 'Y' in active_axes: B += dx * sensitivity
        if 'Z' in active_axes: C += dx * sensitivity

    if auto_rotate:
        if 'X' in active_axes: A += 0.3
        if 'Y' in active_axes: B += 0.3
        if 'Z' in active_axes: C += 0.3

    for theta_deg in range(0, 360, theta_spacing):
        theta = math.radians(theta_deg)
        cost, sint = math.cos(theta), math.sin(theta)
        for phi_deg in range(0, 360, phi_spacing):
            phi = math.radians(phi_deg)
            cosp, sinp = math.cos(phi), math.sin(phi)
            circlex = R2 + R1 * cost
            circley = R1 * sint
            x = circlex * (math.cos(B) * cosp + math.sin(A) * math.sin(B) * sinp) - circley * math.cos(A) * math.sin(B)
            y = circlex * (math.sin(B) * cosp - math.sin(A) * math.cos(B) * sinp) + circley * math.cos(A) * math.cos(B)
            z = circlex * math.cos(A) * sinp + circley * math.sin(A)
            x_rot = x * math.cos(C) - y * math.sin(C)
            y_rot = x * math.sin(C) + y * math.cos(C)
            x, y = x_rot, y_rot
            xp, yp, ooz = project_point(x, y, z)
            idx = xp + columns * yp
            if 0 <= xp < columns and 0 <= yp < rows:
                nx = cost * cosp
                ny = cost * sinp
                nz = sint
                norm = normalize([nx, ny, nz])
                lum = dot(norm, normalize(light))
                lum = max(0, min(1, lum))
                if ooz > zbuffer[idx]:
                    zbuffer[idx] = ooz
                    base = lerp_color(SHADOW_COLOR, MID_COLOR, lum * 2) if lum < 0.5 else lerp_color(MID_COLOR, HIGHLIGHT_COLOR, (lum - 0.5) * 2)
                    shade = 0.7 + 0.6 * ooz
                    shaded = tuple(min(255, int(c * shade)) for c in base)
                    r, g, b = [c / 255 for c in shaded]
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    h = (h + hue) % 1.0
                    final_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))
                    alpha = 100 if transparent_mode else 255
                    colorbuffer[idx] = (*final_color, alpha)

    donut_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    x_pos = y_pos = 0
    radius = min(x_separator, y_separator) // 2
    for i in range(screen_size):
        if colorbuffer[i][3] > 0:
            center = (x_pos + x_separator // 2, y_pos + y_separator // 2)
            pygame.draw.circle(donut_surface, colorbuffer[i], center, radius)
        if (i + 1) % columns == 0:
            x_pos = 0
            y_pos += y_separator
        else:
            x_pos += x_separator

    screen.blit(donut_surface, (0, 0))

    axes_display = ''.join(sorted(a.lower() for a in active_axes)) or "none"
    axis_text = font.render(f"Axes: {axes_display}", True, (255, 255, 255))
    rotate_text = font.render(f"Auto Rotate: {'ON' if auto_rotate else 'OFF'}", True, (255, 255, 255))

    help_lines = [
        "Help",
        "Auto Rotate: press R",
        "Reset Position: press E",
        "Transparency Toggle: press T",
        "For X-axis: press X",
        "For Y-axis: press Y",
        "For Z-axis: press Z",
    ]

    screen.blit(axis_text, (10, 10))
    screen.blit(rotate_text, (10, 35))
    for i, line in enumerate(help_lines):
        text = font.render(line, True, (180, 180, 180))
        screen.blit(text, (10, 70 + i * 25))

    pygame.display.flip()
    hue += 0.004
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
            last_mouse_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
            last_mouse_pos = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                auto_rotate = not auto_rotate
            elif event.key == pygame.K_e:
                A, B, C = 0.0, 0.0, 0.0
            elif event.key == pygame.K_t:
                transparent_mode = not transparent_mode
            elif event.key == pygame.K_x:
                active_axes ^= {'X'}
            elif event.key == pygame.K_y:
                active_axes ^= {'Y'}
            elif event.key == pygame.K_z:
                active_axes ^= {'Z'}
