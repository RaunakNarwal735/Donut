import pygame
import DonW
import os

# Settings
WIDTH, HEIGHT = 1280, 720
LEFT_PANEL_WIDTH = 400
BG_COLOR = (20, 22, 30)
PANEL_COLOR = (30, 32, 40, 220)
SEARCH_BAR_COLOR = (40, 44, 60)
SEARCH_BAR_ACTIVE = (60, 70, 100)
TEXT_COLOR = (220, 240, 255)
OPTION_COLOR = (80, 120, 200)
OPTION_HOVER = (120, 180, 255)

FONT_PATH = os.path.join(os.path.dirname(__file__), "NK57 Monospace Cd Bd.otf")
FONT_SIZE = 28
SMALL_FONT_SIZE = 20

# Donut rendering parameters (simplified for background)
DONUT_XSEP, DONUT_YSEP = 6, 12
DONUT_R1, DONUT_R2 = 1.1, 2.5
DONUT_THETA_SPACING = 4
DONUT_PHI_SPACING = 4

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Symmetry Visualizer")
font = pygame.font.Font(FONT_PATH, FONT_SIZE)
small_font = pygame.font.Font(FONT_PATH, SMALL_FONT_SIZE)

# Donut background state
A, B = 0.0, 0.0
hue = 0

def draw_donut_bg(surface):
    global A, B, hue
    cols = WIDTH // DONUT_XSEP
    rows = HEIGHT // DONUT_YSEP
    x_offset = cols / 2
    y_offset = rows / 2
    zbuffer = [0.0] * (cols * rows)
    colorbuffer = [(0, 0, 0)] * (cols * rows)
    SHADOW_COLOR = (30, 40, 80)
    MID_COLOR = (180, 180, 200)
    HIGHLIGHT_COLOR = (220, 240, 255)
    light = [0, 1, -1]
    import math, colorsys
    def normalize(v):
        l = math.sqrt(sum(i*i for i in v))
        return [i / l for i in v] if l != 0 else v
    def dot(a, b):
        return sum(i * j for i, j in zip(a, b))
    def lerp_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    for theta_deg in range(0, 360, DONUT_THETA_SPACING):
        theta = math.radians(theta_deg)
        cost, sint = math.cos(theta), math.sin(theta)
        for phi_deg in range(0, 360, DONUT_PHI_SPACING):
            phi = math.radians(phi_deg)
            cosp, sinp = math.cos(phi), math.sin(phi)
            circlex = DONUT_R2 + DONUT_R1 * cost
            circley = DONUT_R1 * sint
            x = circlex * cosp
            y = circley
            z = circlex * sinp
            # Simple rotation for background
            x_rot = x * math.cos(B) - z * math.sin(B)
            z_rot = x * math.sin(B) + z * math.cos(B)
            y_rot = y * math.cos(A) - z_rot * math.sin(A)
            z_final = y * math.sin(A) + z_rot * math.cos(A)
            x, y, z = x_rot, y_rot, z_final
            z += 8
            ooz = 1 / z
            xp = int(x_offset + 80 * ooz * x)
            yp = int(y_offset + 40 * ooz * y)
            idx = xp + cols * yp
            if 0 <= xp < cols and 0 <= yp < rows:
                nx = cost * cosp
                ny = cost * sinp
                nz = sint
                norm = normalize([nx, ny, nz])
                lum = dot(norm, normalize(light))
                lum = max(0, min(1, lum))
                if ooz > zbuffer[idx]:
                    zbuffer[idx] = ooz
                    if lum < 0.5:
                        base = lerp_color(SHADOW_COLOR, MID_COLOR, lum * 2)
                    else:
                        base = lerp_color(MID_COLOR, HIGHLIGHT_COLOR, (lum - 0.5) * 2)
                    depth_shade = 0.7 + 0.6 * ooz
                    shaded = tuple(int(min(255, c * depth_shade)) for c in base)
                    r, g, b = [c / 255 for c in shaded]
                    h, s, v = colorsys.rgb_to_hsv(r, g, b)
                    h = (h + hue) % 1.0
                    final_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))
                    # Ensure final_color is always a tuple of 3 elements
                    if len(final_color) == 3:
                        colorbuffer[idx] = (final_color[0], final_color[1], final_color[2])
                    else:
                        colorbuffer[idx] = (0, 0, 0)
    donut_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    x_pos = y_pos = 0
    radius = min(DONUT_XSEP, DONUT_YSEP) // 2
    for i in range(cols * rows):
        if colorbuffer[i] != (0, 0, 0):
            center = (x_pos + DONUT_XSEP // 2, y_pos + DONUT_YSEP // 2)
            pygame.draw.circle(donut_surface, colorbuffer[i], center, radius)
        if (i + 1) % cols == 0:
            x_pos = 0
            y_pos += DONUT_YSEP
        else:
            x_pos += DONUT_XSEP
    surface.blit(donut_surface, (0, 0))
    # Animate
    A += 0.025
    B += 0.012
    hue += 0.002

# UI state
search_text = ""
search_active = False
option_rect = None

clock = pygame.time.Clock()

def main():
    global search_text, search_active, option_rect
    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_donut_bg(screen)
        # Draw left panel
        panel = pygame.Surface((LEFT_PANEL_WIDTH, HEIGHT), pygame.SRCALPHA)
        panel.fill(PANEL_COLOR)
        screen.blit(panel, (0, 0))
        # Draw search bar
        bar_rect = pygame.Rect(40, 60, LEFT_PANEL_WIDTH - 80, 48)
        bar_color = SEARCH_BAR_ACTIVE if search_active else SEARCH_BAR_COLOR
        pygame.draw.rect(screen, bar_color, bar_rect, border_radius=10)
        prompt = font.render("Which shape to visualize?", True, TEXT_COLOR)
        screen.blit(prompt, (40, 20))
        # Draw search text
        text_surf = font.render(search_text, True, TEXT_COLOR)
        screen.blit(text_surf, (bar_rect.x + 10, bar_rect.y + 8))
        # Draw option for DonW
        show_option = "donw" in search_text.lower() or search_text.strip() == "" or "don" in search_text.lower()
        if show_option:
            opt_rect = pygame.Rect(40, 130, LEFT_PANEL_WIDTH - 80, 44)
            mouse_pos = pygame.mouse.get_pos()
            hovered = opt_rect.collidepoint(mouse_pos)
            color = OPTION_HOVER if hovered else OPTION_COLOR
            pygame.draw.rect(screen, color, opt_rect, border_radius=8)
            opt_label = font.render("DonW", True, (255, 255, 255))
            screen.blit(opt_label, (opt_rect.x + 16, opt_rect.y + 6))
            option_rect = opt_rect
        else:
            option_rect = None
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bar_rect.collidepoint(event.pos):
                    search_active = True
                else:
                    search_active = False
                if option_rect and option_rect.collidepoint(event.pos):
                    pygame.quit()
                    DonW.run_donut()
                    return
            elif event.type == pygame.KEYDOWN and search_active:
                if event.key == pygame.K_BACKSPACE:
                    search_text = search_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if option_rect:
                        pygame.quit()
                        DonW.run_donut()
                        return
                elif event.key == pygame.K_ESCAPE:
                    search_active = False
                else:
                    if len(search_text) < 20 and event.unicode.isprintable():
                        search_text += event.unicode
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main() 