import pygame
import math
import colorsys
import random

def run_donut():
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    x_separator, y_separator = 2, 4
    columns = WIDTH // x_separator
    rows = HEIGHT // y_separator
    screen_size = rows * columns
    x_offset = columns / 2
    y_offset = rows / 2

    # Initialize state variables
    A, B = 0, 0
    theta_spacing = 2
    phi_spacing = 2
    R1, R2 = 1.1, 2.5
    zoom_factor = 1.0
    spin_speed = 1.0
    hue_rotation_enabled = False
    ascii_mode = True
    theme_index = 0
    light_directions = [[0, 1, -1], [1, 1, -1], [0, -1, -1], [1, 0, -1]]
    light_dir_index = 0

    CHARACTERS = list("RAUNAK")
    font = pygame.font.SysFont('Consolas', 14, bold=True)

    themes = [
        # Metallic Theme
        [(210, 50, 180), (180, 210, 220), (155, 150, 100)],
        # Rendered Theme
        [(50, 60, 70), (120, 150, 160), (220, 230, 240)],
        # Normal Theme
        [(50, 50, 50), (180, 180, 180), (255, 255, 255)],
    ]

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Donut with UI")

    def normalize(v):
        l = math.sqrt(sum(i*i for i in v))
        return [i / l for i in v]

    def dot(a, b):
        return sum(i * j for i, j in zip(a, b))

    def lerp_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    run = True
    hue = 0

    while run:
        screen.fill((10, 10, 10))

        SHADOW_COLOR, MID_COLOR, HIGHLIGHT_COLOR = themes[theme_index]
        light = light_directions[light_dir_index]

        # UI Panel
        pygame.draw.rect(screen, (20, 20, 30), (0, 0, 260, HEIGHT))
        ui_texts = [
            f"THEME (T): {['Metallic', 'Rendered', 'Normal'][theme_index]}",
            f"HUE (H): {'ON' if hue_rotation_enabled else 'OFF'}",
            f"SPEED (UP/DOWN): {spin_speed:.2f}",
            f"DETAIL (D): {theta_spacing}",
            f"ZOOM (Z): {zoom_factor:.2f}",
            f"RESET (R)",
            f"LIGHT (L): {light_directions[light_dir_index]}",
            f"ASCII (A): {'ON' if ascii_mode else 'OFF'}",
            f"ESC: EXIT"
        ]
        y_offset_ui = 20
        for text in ui_texts:
            rendered = font.render(text, True, (200, 200, 200))
            screen.blit(rendered, (20, y_offset_ui))
            y_offset_ui += 25

        zbuffer = [0.0] * screen_size
        colorbuffer = [(0, 0, 0)] * screen_size
        charbuffer = [' '] * screen_size

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
                z = 5 + circlex * math.cos(A) * sinp + circley * math.sin(A)
                ooz = 1 / z
                xp = int(x_offset + zoom_factor * 80 * ooz * x)
                yp = int(y_offset + zoom_factor * 40 * ooz * y)
                idx = xp + columns * yp

                nx = cost * cosp
                ny = cost * sinp
                nz = sint
                norm = normalize([nx, ny, nz])
                lum = dot(norm, normalize(light))
                lum = max(0, min(1, lum))

                if 0 <= xp < columns and 0 <= yp < rows and ooz > zbuffer[idx]:
                    zbuffer[idx] = ooz
                    base = lerp_color(SHADOW_COLOR, MID_COLOR, lum) if lum < 0.5 else lerp_color(MID_COLOR, HIGHLIGHT_COLOR, (lum - 0.5) * 2)
                    depth_shade = 0.8 + 0.7 * ooz
                    shaded = tuple(min(255, int(c * depth_shade)) for c in base)
                    r, g, b = [c / 255 for c in shaded]
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    if hue_rotation_enabled:
                        h = (h + hue) % 1.0
                    final_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))

                    colorbuffer[idx] = final_color
                    charbuffer[idx] = random.choice(CHARACTERS)

        x_pos = y_pos = 0
        for i in range(screen_size):
            if colorbuffer[i] != (0, 0, 0):
                color = colorbuffer[i]
                if ascii_mode:
                    char = charbuffer[i]
                    text_surface = font.render(char, True, color)
                    center = (x_pos + x_separator // 2, y_pos + y_separator // 2)
                    screen.blit(text_surface, center)
                else:
                    center = (x_pos + x_separator // 2, y_pos + y_separator // 2)
                    pygame.draw.circle(screen, color, center, 1)
            if (i + 1) % columns == 0:
                x_pos = 0
                y_pos += y_separator
            else:
                x_pos += x_separator

        pygame.display.flip()
        A += 0.02 * spin_speed
        B += 0.01 * spin_speed
        hue += 0.005 if hue_rotation_enabled else 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    theme_index = (theme_index + 1) % len(themes)
                if event.key == pygame.K_h:
                    hue_rotation_enabled = not hue_rotation_enabled
                if event.key == pygame.K_UP:
                    spin_speed = min(spin_speed + 0.1, 5.0)
                if event.key == pygame.K_DOWN:
                    spin_speed = max(spin_speed - 0.1, 0.1)
                if event.key == pygame.K_d:
                    theta_spacing = max(1, theta_spacing - 1)
                    phi_spacing = max(1, phi_spacing - 1)
                if event.key == pygame.K_r:
                    theme_index = 0
                    spin_speed = 1.0
                    theta_spacing, phi_spacing = 2, 2
                    zoom_factor = 1.0
                    hue_rotation_enabled = False
                if event.key == pygame.K_z:
                    zoom_factor = 1.5 if zoom_factor == 1.0 else 1.0
                if event.key == pygame.K_a:
                    ascii_mode = not ascii_mode
                if event.key == pygame.K_l:
                    light_dir_index = (light_dir_index + 1) % len(light_directions)

if __name__ == "__main__":
    run_donut()
