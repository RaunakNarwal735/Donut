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
    x_offset = columns / 2
    y_offset = rows / 2

    A, B = 0, 0
    theta_spacing = 2
    phi_spacing = 2
    R1, R2 = 1.1, 2.5

    zoom_factor = 1.5
    spin_speed = 5.0
    freeze = False
    ascii_mode = True
    theme_index = 2  # Studio Render as default
    light_directions = [[0, 1, -1], [1, 1, -1], [0, -1, -1], [1, 0, -1]]
    light_dir_index = 0

    CHARACTERS = list("RAM")
    font = pygame.font.SysFont('Consolas', 14, bold=True)

    # THEMES: Each theme has 2 palettes (Base + Accent)
    themes = [
        # Plasma Pink (magenta + light blue)
        [[(210, 50, 180), (255, 150, 200), (180, 100, 250)],
         [(120, 200, 255), (180, 240, 255), (100, 200, 255)]],

        # Metallic (realistic shiny metal + golden lines)
        [[(80, 80, 80), (180, 180, 180), (255, 255, 255)],
         [(220, 180, 50), (255, 215, 0), (255, 255, 255)]],

        # Studio Render (blender-like neutral)
        [[(60, 60, 70), (150, 150, 160), (240, 240, 250)],
         [(30, 30, 40), (180, 180, 200), (255, 255, 255)]],

        # Crystal (merged Amethyst + Emerald + Green Crystal)
        [[(220, 180, 50),(80, 220, 120),(180, 120, 220), (200, 255, 240), (100, 180, 255)],
         [(255, 215, 0),(240, 180, 250),(220, 255, 255),(255, 255, 255),(255, 250, 200)]],


        # Solar Ember (orange + deep red)
        [[(120, 30, 10), (200, 100, 50), (255, 200, 100)],
         [(180, 30, 30), (255, 70, 70), (255, 120, 80)]],

        # Aqua Radiance (cyan + blue tones)
        [[(20, 50, 80), (50, 180, 200), (180, 250, 255)],
         [(80, 120, 200), (120, 200, 255), (220, 255, 255)]],
    ]

    theme_names = [
        "Plasma Pink",
        "Metallic",
        "Studio Render",
        "Crystal",
        "Solar Ember",
        "Aqua Radiance"
    ]

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Multicolored Donut Visualizer")

    def normalize(v):
        l = math.sqrt(sum(i*i for i in v))
        return [i / l for i in v]

    def dot(a, b):
        return sum(i * j for i, j in zip(a, b))

    def lerp_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

    run = True
    display_panel_open = False

    while run:
        screen.fill((10, 10, 10))

        palette1, palette2 = themes[theme_index]
        light = light_directions[light_dir_index]

        pygame.draw.rect(screen, (0, 0, 0), (0, 0, 260, HEIGHT))
        ui_texts = [
            "Display (D)  [Toggle]",
            "ESC: EXIT"
        ]

        if display_panel_open:
            ui_texts += [
                f"THEME (T): {theme_names[theme_index]}",
                f"SPEED (UP/DOWN): {spin_speed:.2f}",
                f"ZOOM (Z/X): {zoom_factor:.2f}",
                f"RESET (R)",
                f"LIGHT (L): {light_directions[light_dir_index]}",
                f"ASCII (A): {'ON' if ascii_mode else 'OFF'}",
                f"FREEZE (F): {'ON' if freeze else 'OFF'}"
            ]

        y_offset_ui = 20
        for text in ui_texts:
            rendered = font.render(text, True, (200, 200, 200))
            screen.blit(rendered, (20, y_offset_ui))
            y_offset_ui += 25

        zbuffer = [0.0] * (rows * columns)
        colorbuffer = [(0, 0, 0)] * (rows * columns)
        charbuffer = [' '] * (rows * columns)

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

                nx, ny, nz = cost * cosp, cost * sinp, sint
                norm = normalize([nx, ny, nz])
                lum = max(0, min(1, dot(norm, normalize(light))))

                blend_factor = (math.sin(phi) + 1) / 2
                shadow_color = lerp_color(palette1[0], palette2[0], blend_factor)
                mid_color = lerp_color(palette1[1], palette2[1], blend_factor)
                highlight_color = lerp_color(palette1[2], palette2[2], blend_factor)

                if 0 <= xp < columns and 0 <= yp < rows and ooz > zbuffer[idx]:
                    zbuffer[idx] = ooz
                    base = lerp_color(shadow_color, mid_color, lum) if lum < 0.5 else lerp_color(mid_color, highlight_color, (lum - 0.5) * 2)
                    depth_shade = 0.8 + 0.7 * ooz
                    shaded = tuple(min(255, int(c * depth_shade)) for c in base)
                    colorbuffer[idx] = shaded
                    charbuffer[idx] = random.choice(CHARACTERS)

        x_pos = y_pos = 0
        for i in range(rows * columns):
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

        if not freeze:
            A += 0.02 * spin_speed
            B += 0.01 * spin_speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    display_panel_open = not display_panel_open

                if display_panel_open:
                    if event.key == pygame.K_t:
                        theme_index = (theme_index + 1) % len(themes)
                    if event.key == pygame.K_UP:
                        spin_speed += 0.2
                    if event.key == pygame.K_DOWN:
                        spin_speed = max(spin_speed - 0.2, 0)
                    if event.key == pygame.K_r:
                        theme_index = 2
                        spin_speed = 5.0
                        zoom_factor = 1.5
                        freeze = False
                    if event.key == pygame.K_z:
                        zoom_factor += 0.1
                    if event.key == pygame.K_x:
                        zoom_factor = max(0.1, zoom_factor - 0.1)
                    if event.key == pygame.K_a:
                        ascii_mode = not ascii_mode
                    if event.key == pygame.K_l:
                        light_dir_index = (light_dir_index + 1) % len(light_directions)
                    if event.key == pygame.K_f:
                        freeze = not freeze

if __name__ == "__main__":
    run_donut()
