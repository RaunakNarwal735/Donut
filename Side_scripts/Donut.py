import pygame
import math
import colorsys

def run_donut():
    pygame.init()
    # Screen settings
    WIDTH, HEIGHT = 1280, 720
    x_separator, y_separator = 3, 6  # smaller = finer detail
    columns = WIDTH // x_separator
    rows = HEIGHT // y_separator
    screen_size = rows * columns
    x_offset = columns / 2
    y_offset = rows / 2
    # Rotation angles
    A, B = 0, 0
    # Geometry & resolution
    theta_spacing = 2  # angular steps
    phi_spacing = 2
    R1, R2 = 1.1, 2.5  # donut tube radius and center radius
    # Lighting direction
    light = [0, 1, -1]
    # Color gradients (metallic)
    SHADOW_COLOR = (30, 40, 80)      # deep blue
    MID_COLOR = (180, 180, 200)      # silver/gray
    HIGHLIGHT_COLOR = (220, 240, 255) # bluish-white
    def normalize(v):
        l = math.sqrt(sum(i*i for i in v))
        return [i / l for i in v]
    def dot(a, b):
        return sum(i * j for i, j in zip(a, b))
    def lerp_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Detailed Spinning Donut")
    run = True
    hue = 0
    while run:
        screen.fill((0, 0, 0))
        zbuffer = [0.0] * screen_size
        colorbuffer = [(0, 0, 0)] * screen_size
        for theta_deg in range(0, 360, theta_spacing):
            theta = math.radians(theta_deg)
            cost, sint = math.cos(theta), math.sin(theta)
            for phi_deg in range(0, 360, phi_spacing):
                phi = math.radians(phi_deg)
                cosp, sinp = math.cos(phi), math.sin(phi)
                # Donut surface coordinates before rotation
                circlex = R2 + R1 * cost
                circley = R1 * sint
                # Apply rotation around X and Z
                x = circlex * (math.cos(B) * cosp + math.sin(A) * math.sin(B) * sinp) - circley * math.cos(A) * math.sin(B)
                y = circlex * (math.sin(B) * cosp - math.sin(A) * math.cos(B) * sinp) + circley * math.cos(A) * math.cos(B)
                z = 5 + circlex * math.cos(A) * sinp + circley * math.sin(A)
                ooz = 1 / z
                xp = int(x_offset + 80 * ooz * x)
                yp = int(y_offset + 40 * ooz * y)
                idx = xp + columns * yp
                # Compute normal for lighting
                nx = cost * cosp
                ny = cost * sinp
                nz = sint
                norm = normalize([nx, ny, nz])
                lum = dot(norm, normalize(light))
                lum = max(0, min(1, lum))
                if 0 <= xp < columns and 0 <= yp < rows and ooz > zbuffer[idx]:
                    zbuffer[idx] = ooz
                    if lum < 0.5:
                        base = lerp_color(SHADOW_COLOR, MID_COLOR, lum * 2)
                    else:
                        base = lerp_color(MID_COLOR, HIGHLIGHT_COLOR, (lum - 0.5) * 2)
                    depth_shade = 0.7 + 0.6 * ooz
                    shaded = tuple(int(min(255, c * depth_shade)) for c in base)
                    # Shift hue for dynamic color
                    r, g, b = [c / 255 for c in shaded]
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    h = (h + hue) % 1.0
                    final_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))
                    colorbuffer[idx] = (final_color[0], final_color[1], final_color[2])
        # Draw the donut using small circles for smoothness
        x_pos = y_pos = 0
        radius = min(x_separator, y_separator) // 2
        for i in range(screen_size):
            if colorbuffer[i] != (0, 0, 0):
                center = (x_pos + x_separator // 2, y_pos + y_separator // 2)
                pygame.draw.circle(screen, colorbuffer[i], center, radius)
            if (i + 1) % columns == 0:
                x_pos = 0
                y_pos += y_separator
            else:
                x_pos += x_separator
        pygame.display.flip()
        A += 0.37
        B += 0.15
        hue += 0.006
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False

if __name__ == "__main__":
    run_donut()
