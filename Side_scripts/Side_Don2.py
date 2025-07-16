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

# Zoom state
zoom_level = 0  # 0, 1, 2, 3 (cycles back to 0)
zoom_scales = [1.0, 1.5, 2.0, 2.5]  # Zoom multipliers

# Spinning R text state
r_rotation_angle = 0.0

# Cartesian plane state
active_planes = set()  # Can contain 'X', 'Y', 'Z', 'XY', 'XZ', 'YZ'

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
    zoom_scale = zoom_scales[zoom_level]
    xp = int(x_offset + 80 * ooz * px * zoom_scale)
    yp = int(y_offset + 40 * ooz * py * zoom_scale)
    return xp, yp, ooz

def rotate_surface(surface, angle, center):
    """Rotate a surface around its center"""
    rotated = pygame.transform.rotate(surface, math.degrees(angle))
    new_rect = rotated.get_rect(center=center)
    return rotated, new_rect

def draw_cartesian_planes(screen, A, B, C, zoom_level):
    """Draw cartesian coordinate planes"""
    if not active_planes:
        return
    
    zoom_scale = zoom_scales[zoom_level]
    plane_size = 4.0  # Size of the plane in 3D space
    grid_density = 0.2  # Spacing between grid lines
    
    # Define plane colors with transparency
    plane_colors = {
        'X': (255, 100, 100, 80),   # Red for YZ plane (X=0)
        'Y': (100, 255, 100, 80),   # Green for XZ plane (Y=0)
        'Z': (100, 100, 255, 80),   # Blue for XY plane (Z=0)
        'XY': (255, 255, 100, 60),  # Yellow for XY plane
        'XZ': (255, 100, 255, 60),  # Magenta for XZ plane
        'YZ': (100, 255, 255, 60),  # Cyan for YZ plane
    }
    
    # Create a surface for planes with alpha
    plane_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    for plane_name in active_planes:
        color = plane_colors[plane_name]
        
        # Draw grid lines for each plane
        for i in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1):
            line_pos = i * grid_density
            
            if plane_name == 'X':  # YZ plane (X = 0)
                # Draw lines parallel to Y axis
                points = []
                for z in [j * grid_density for j in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1)]:
                    x, y, z_3d = 0, line_pos, z
                    # Apply rotations
                    x_rot = x * math.cos(C) - y * math.sin(C)
                    y_rot = x * math.sin(C) + y * math.cos(C)
                    x, y = x_rot, y_rot
                    
                    x_final = x * math.cos(B) - z_3d * math.sin(B)
                    z_final = x * math.sin(B) + z_3d * math.cos(B)
                    x = x_final
                    
                    y_final = y * math.cos(A) - z_final * math.sin(A)
                    z_final = y * math.sin(A) + z_final * math.cos(A)
                    y = y_final
                    
                    xp, yp, _ = project_point(x, y, z_final)
                    if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                        points.append((xp, yp))
                
                if len(points) > 1:
                    pygame.draw.lines(plane_surface, color[:3], False, points, 1)
                
                # Draw lines parallel to Z axis
                points = []
                for y in [j * grid_density for j in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1)]:
                    x, y_3d, z = 0, y, line_pos
                    # Apply rotations
                    x_rot = x * math.cos(C) - y_3d * math.sin(C)
                    y_rot = x * math.sin(C) + y_3d * math.cos(C)
                    x, y_3d = x_rot, y_rot
                    
                    x_final = x * math.cos(B) - z * math.sin(B)
                    z_final = x * math.sin(B) + z * math.cos(B)
                    x = x_final
                    
                    y_final = y_3d * math.cos(A) - z_final * math.sin(A)
                    z_final = y_3d * math.sin(A) + z_final * math.cos(A)
                    y_3d = y_final
                    
                    xp, yp, _ = project_point(x, y_3d, z_final)
                    if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                        points.append((xp, yp))
                
                if len(points) > 1:
                    pygame.draw.lines(plane_surface, color[:3], False, points, 1)
            
            elif plane_name == 'Y':  # XZ plane (Y = 0)
                # Draw lines parallel to X axis
                points = []
                for z in [j * grid_density for j in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1)]:
                    x, y, z_3d = line_pos, 0, z
                    # Apply rotations
                    x_rot = x * math.cos(C) - y * math.sin(C)
                    y_rot = x * math.sin(C) + y * math.cos(C)
                    x, y = x_rot, y_rot
                    
                    x_final = x * math.cos(B) - z_3d * math.sin(B)
                    z_final = x * math.sin(B) + z_3d * math.cos(B)
                    x = x_final
                    
                    y_final = y * math.cos(A) - z_final * math.sin(A)
                    z_final = y * math.sin(A) + z_final * math.cos(A)
                    y = y_final
                    
                    xp, yp, _ = project_point(x, y, z_final)
                    if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                        points.append((xp, yp))
                
                if len(points) > 1:
                    pygame.draw.lines(plane_surface, color[:3], False, points, 1)
                
                # Draw lines parallel to Z axis
                points = []
                for x in [j * grid_density for j in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1)]:
                    x_3d, y, z = x, 0, line_pos
                    # Apply rotations
                    x_rot = x_3d * math.cos(C) - y * math.sin(C)
                    y_rot = x_3d * math.sin(C) + y * math.cos(C)
                    x_3d, y = x_rot, y_rot
                    
                    x_final = x_3d * math.cos(B) - z * math.sin(B)
                    z_final = x_3d * math.sin(B) + z * math.cos(B)
                    x_3d = x_final
                    
                    y_final = y * math.cos(A) - z_final * math.sin(A)
                    z_final = y * math.sin(A) + z_final * math.cos(A)
                    y = y_final
                    
                    xp, yp, _ = project_point(x_3d, y, z_final)
                    if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                        points.append((xp, yp))
                
                if len(points) > 1:
                    pygame.draw.lines(plane_surface, color[:3], False, points, 1)
            
            elif plane_name == 'Z':  # XY plane (Z = 0)
                # Draw lines parallel to X axis
                points = []
                for y in [j * grid_density for j in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1)]:
                    x, y_3d, z = line_pos, y, 0
                    # Apply rotations
                    x_rot = x * math.cos(C) - y_3d * math.sin(C)
                    y_rot = x * math.sin(C) + y_3d * math.cos(C)
                    x, y_3d = x_rot, y_rot
                    
                    x_final = x * math.cos(B) - z * math.sin(B)
                    z_final = x * math.sin(B) + z * math.cos(B)
                    x = x_final
                    
                    y_final = y_3d * math.cos(A) - z_final * math.sin(A)
                    z_final = y_3d * math.sin(A) + z_final * math.cos(A)
                    y_3d = y_final
                    
                    xp, yp, _ = project_point(x, y_3d, z_final)
                    if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                        points.append((xp, yp))
                
                if len(points) > 1:
                    pygame.draw.lines(plane_surface, color[:3], False, points, 1)
                
                # Draw lines parallel to Y axis
                points = []
                for x in [j * grid_density for j in range(int(-plane_size / grid_density), int(plane_size / grid_density) + 1)]:
                    x_3d, y, z = x, line_pos, 0
                    # Apply rotations
                    x_rot = x_3d * math.cos(C) - y * math.sin(C)
                    y_rot = x_3d * math.sin(C) + y * math.cos(C)
                    x_3d, y = x_rot, y_rot
                    
                    x_final = x_3d * math.cos(B) - z * math.sin(B)
                    z_final = x_3d * math.sin(B) + z * math.cos(B)
                    x_3d = x_final
                    
                    y_final = y * math.cos(A) - z_final * math.sin(A)
                    z_final = y * math.sin(A) + z_final * math.cos(A)
                    y = y_final
                    
                    xp, yp, _ = project_point(x_3d, y, z_final)
                    if 0 <= xp < WIDTH and 0 <= yp < HEIGHT:
                        points.append((xp, yp))
                
                if len(points) > 1:
                    pygame.draw.lines(plane_surface, color[:3], False, points, 1)
    
    # Blit the plane surface to the main screen
    screen.blit(plane_surface, (0, 0))

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
        # Spin the R text when auto-rotate is on
        r_rotation_angle += 0.08  # Adjust speed as needed

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
    
    # Draw cartesian planes
    draw_cartesian_planes(screen, A, B, C, zoom_level)

    axes_display = ''.join(sorted(a.lower() for a in active_axes)) or "none"
    axis_text = font.render(f"Axes: {axes_display}", True, (255, 255, 255))
    zoom_text = font.render(f"Zoom: {zoom_scales[zoom_level]:.1f}x", True, (255, 255, 255))
    
    # Display active planes
    planes_display = ', '.join(sorted(active_planes)) if active_planes else "none"
    planes_text = font.render(f"Planes: {planes_display}", True, (255, 255, 255))

    # Create the Auto Rotate text with spinning R
    if auto_rotate:
        # Create separate text surfaces for "Auto " and "otate: ON"
        auto_text = font.render("Auto ", True, (255, 255, 255))
        otate_text = font.render("otate: ON", True, (255, 255, 255))
        
        # Create the spinning R
        r_text = font.render("R", True, (255, 100, 100))  # Red color for emphasis
        r_rotated, r_rect = rotate_surface(r_text, r_rotation_angle, (0, 0))
        
        # Position everything
        auto_width = auto_text.get_width()
        r_width = r_text.get_width()
        
        # Blit the text components
        screen.blit(auto_text, (10, 35))
        
        # Position the spinning R after "Auto "
        r_center = (10 + auto_width + r_width // 2, 35 + r_text.get_height() // 2)
        r_rect.center = r_center
        screen.blit(r_rotated, r_rect)
        
        # Position "otate: ON" after the spinning R
        otate_x = 10 + auto_width + r_width
        screen.blit(otate_text, (otate_x, 35))
    else:
        # Normal static text when not rotating
        rotate_text = font.render("Auto Rotate: OFF", True, (255, 255, 255))
        screen.blit(rotate_text, (10, 35))

    help_lines = [
        "Help",
        "Auto Rotate: press R",
        "Reset Position: press E",
        "Transparency Toggle: press T",
        "Zoom: press 7",
        "For X-axis: press X",
        "For Y-axis: press Y",
        "For Z-axis: press Z",
        "Planes: 1(X), 2(Y), 3(Z)",
        "Combined: 12(XY), 13(XZ), 23(YZ)",
    ]

    screen.blit(axis_text, (10, 10))
    screen.blit(zoom_text, (10, 60))
    screen.blit(planes_text, (10, 85))
    for i, line in enumerate(help_lines):
        text = font.render(line, True, (180, 180, 180))
        screen.blit(text, (10, 110 + i * 25))

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
                # Reset R rotation when toggling
                if not auto_rotate:
                    r_rotation_angle = 0.0
            elif event.key == pygame.K_e:
                A, B, C = 0.0, 0.0, 0.0
            elif event.key == pygame.K_t:
                transparent_mode = not transparent_mode
            elif event.key == pygame.K_7:
                zoom_level = (zoom_level + 1) % 4  # Cycle through 0, 1, 2, 3
            elif event.key == pygame.K_x:
                active_axes ^= {'X'}
            elif event.key == pygame.K_y:
                active_axes ^= {'Y'}
            elif event.key == pygame.K_z:
                active_axes ^= {'Z'}
            # Cartesian plane controls
            elif event.key == pygame.K_1:
                active_planes ^= {'X'}
            elif event.key == pygame.K_2:
                active_planes ^= {'Y'}
            elif event.key == pygame.K_3:
                active_planes ^= {'Z'}
            elif event.key == pygame.K_4:  # For combined planes
                keys = pygame.key.get_pressed()
                if keys[pygame.K_1]:  # 1+4 = 14, but we'll use simpler logic
                    pass
                elif keys[pygame.K_2]:  # 2+4 = 24
                    pass
                elif keys[pygame.K_3]:  # 3+4 = 34
                    pass
            # Handle number combinations for combined planes
            keys = pygame.key.get_pressed()
            if keys[pygame.K_1] and keys[pygame.K_2]:
                if event.key in [pygame.K_1, pygame.K_2]:
                    active_planes ^= {'XY'}
            elif keys[pygame.K_1] and keys[pygame.K_3]:
                if event.key in [pygame.K_1, pygame.K_3]:
                    active_planes ^= {'XZ'}
            elif keys[pygame.K_2] and keys[pygame.K_3]:
                if event.key in [pygame.K_2, pygame.K_3]:
                    active_planes ^= {'YZ'}