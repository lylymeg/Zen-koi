import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zen Koi Pond & Water Ripples Simulator")
clock = pygame.time.Clock()

# Couleurs (Thème Bassin Nocturne & Zen)
POND_BG = (12, 24, 38)
WATER_DEEP = (16, 32, 48)
RIPPLE_COLOR = (75, 145, 195)
LILY_GREEN = (48, 128, 86)
LILY_HIGHLIGHT = (72, 168, 114)
LOTUS_PINK = (255, 165, 200)
FOOD_COLOR = (245, 195, 110)
TEXT_COLOR = (240, 246, 255)
GRAY = (130, 148, 172)

KOI_PALETTES = [
    {"body": (250, 248, 245), "spots": (240, 85, 55)},    # Kohaku (Blanc & Rouge-Orange)
    {"body": (245, 135, 45), "spots": (248, 246, 240)},   # Orenji (Orange & Blanc)
    {"body": (250, 210, 75), "spots": (235, 95, 65)},     # Yamabuki (Or & Corail)
    {"body": (242, 242, 248), "spots": (45, 50, 65)},     # Shiro Utsuri (Blanc & Encre)
]

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

class Ripple:
    def __init__(self, x, y, max_radius=95):
        self.x = float(x)
        self.y = float(y)
        self.radius = 4.0
        self.max_radius = max_radius
        self.alpha = 180

    def update(self):
        self.radius += 1.4
        progress = self.radius / self.max_radius
        self.alpha = max(0, int(180 * (1.0 - progress)))

    def draw(self, surface):
        if self.alpha <= 4:
            return
        r = int(self.radius)
        surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*RIPPLE_COLOR, self.alpha), (r + 2, r + 2), r, 2)
        surface.blit(surf, (int(self.x) - r - 2, int(self.y) - r - 2))

class FoodPellet:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.bob_phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.bob_phase += 0.08
        self.x += math.cos(self.bob_phase * 0.5) * 0.15
        self.y += math.sin(self.bob_phase * 0.5) * 0.15

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surface, FOOD_COLOR, (ix, iy), 4)
        pygame.draw.circle(surface, (255, 235, 180), (ix - 1, iy - 1), 2)

class LilyPad:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = random.randint(24, 38)
        self.has_flower = random.random() < 0.45
        self.notch_angle = random.uniform(0, math.pi * 2)
        self.drift_phase = random.uniform(0, math.pi * 2)

    def update(self):
        self.drift_phase += 0.02
        self.x += math.sin(self.drift_phase) * 0.08
        self.y += math.cos(self.drift_phase * 0.8) * 0.08

    def draw(self, surface):
        ix, iy = int(self.x), int(self.y)
        # Feuille de nénuphar
        pygame.draw.circle(surface, LILY_GREEN, (ix, iy), self.radius)
        pygame.draw.circle(surface, LILY_HIGHLIGHT, (ix - 3, iy - 3), self.radius - 5)

        # Encoche caractéristique de la feuille
        nx = ix + math.cos(self.notch_angle) * (self.radius + 2)
        ny = iy + math.sin(self.notch_angle) * (self.radius + 2)
        n1x = ix + math.cos(self.notch_angle - 0.25) * (self.radius + 2)
        n1y = iy + math.sin(self.notch_angle - 0.25) * (self.radius + 2)
        n2x = ix + math.cos(self.notch_angle + 0.25) * (self.radius + 2)
        n2y = iy + math.sin(self.notch_angle + 0.25) * (self.radius + 2)
        pygame.draw.polygon(surface, POND_BG, [(ix, iy), (n1x, n1y), (nx, ny), (n2x, n2y)])

        # Fleur de lotus rose optionnelle
        if self.has_flower:
            for i in range(6):
                ang = i * (math.pi / 3)
                px = ix + math.cos(ang) * 7
                py = iy + math.sin(ang) * 7
                pygame.draw.circle(surface, LOTUS_PINK, (int(px), int(py)), 5)
            pygame.draw.circle(surface, (255, 225, 110), (ix, iy), 4)

class KoiFish:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(1.4, 2.1)
        self.palette = random.choice(KOI_PALETTES)
        self.size = random.uniform(0.9, 1.25)
        self.swim_phase = random.uniform(0, math.pi * 2)
        self.turn_timer = random.randint(40, 120)
        self.target_angle = self.angle
        # Positions relatives des taches colorées sur le dos
        self.spots = [
            (random.uniform(-6, 8), random.uniform(-3, 3), random.uniform(4, 7))
            for _ in range(3)
        ]

    def update(self, pellets, ripples):
        self.swim_phase += 0.16 * (self.speed / 1.6)

        # Chercher un granulé proche
        target_pellet = None
        if pellets:
            closest = min(pellets, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))
            if math.hypot(closest.x - self.x, closest.y - self.y) < 260:
                target_pellet = closest

        if target_pellet:
            self.target_angle = math.atan2(target_pellet.y - self.y, target_pellet.x - self.x)
        else:
            self.turn_timer -= 1
            if self.turn_timer <= 0:
                self.turn_timer = random.randint(50, 140)
                self.target_angle += random.uniform(-1.1, 1.1)

        # Éviter doucement les bords de l'écran et le HUD
        margin = 65
        if self.x < margin:
            self.target_angle = 0.0
        elif self.x > WIDTH - margin:
            self.target_angle = math.pi
        if self.y < 110:
            self.target_angle = math.pi / 2
        elif self.y > HEIGHT - margin:
            self.target_angle = -math.pi / 2

        # Rotation progressive vers l'angle cible
        diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        self.angle += diff * 0.05

        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Manger le granulé si atteint
        if target_pellet and math.hypot(target_pellet.x - self.x, target_pellet.y - self.y) < 16:
            pellets.remove(target_pellet)
            ripples.append(Ripple(self.x, self.y, max_radius=55))

    def draw(self, surface):
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        perp_x = -sin_a
        perp_y = cos_a

        # Nageoires pectorales
        fin_wave = math.sin(self.swim_phase) * 3
        for side in (-1, 1):
            fx = self.x + cos_a * 4 + perp_x * side * (9 * self.size)
            fy = self.y + sin_a * 4 + perp_y * side * (9 * self.size) + fin_wave * 0.3
            pygame.draw.circle(surface, self.palette["body"], (int(fx), int(fy)), int(5 * self.size))

        # Corps segmenté pour un effet d'ondulation naturel
        segments = [
            (12, 8.5),   # Tête
            (4, 9.5),    # Avant-corps
            (-5, 8.0),   # Milieu
            (-13, 5.5),  # Arrière
            (-20, 3.2),  # Base de la queue
        ]

        for idx, (offset, rad) in enumerate(segments):
            wiggle = math.sin(self.swim_phase - idx * 0.55) * (idx * 1.4)
            sx = self.x + cos_a * (offset * self.size) + perp_x * wiggle
            sy = self.y + sin_a * (offset * self.size) + perp_y * wiggle
            pygame.draw.circle(surface, self.palette["body"], (int(sx), int(sy)), max(2, int(rad * self.size)))

        # Nageoire caudale (queue ondulante)
        tail_wiggle = math.sin(self.swim_phase - 2.6) * 7.5
        tx = self.x - cos_a * (28 * self.size) + perp_x * tail_wiggle
        ty = self.y - sin_a * (28 * self.size) + perp_y * tail_wiggle
        base_x = self.x - cos_a * (20 * self.size) + perp_x * (tail_wiggle * 0.6)
        base_y = self.y - sin_a * (20 * self.size) + perp_y * (tail_wiggle * 0.6)
        pygame.draw.polygon(surface, self.palette["body"], [
            (int(base_x), int(base_y)),
            (int(tx + perp_x * 6), int(ty + perp_y * 6)),
            (int(tx - perp_x * 6), int(ty - perp_y * 6))
        ])

        # Taches colorées sur le dos
        for sp_off, sp_side, sp_rad in self.spots:
            wiggle = math.sin(self.swim_phase - 0.8) * 1.5
            px = self.x + cos_a * (sp_off * self.size) + perp_x * (sp_side * self.size + wiggle)
            py = self.y + sin_a * (sp_off * self.size) + perp_y * (sp_side * self.size + wiggle)
            pygame.draw.circle(surface, self.palette["spots"], (int(px), int(py)), max(2, int(sp_rad * self.size)))

        # Petits yeux
        for side in (-1, 1):
            ex = self.x + cos_a * (14 * self.size) + perp_x * side * (4.5 * self.size)
            ey = self.y + sin_a * (14 * self.size) + perp_y * side * (4.5 * self.size)
            pygame.draw.circle(surface, (20, 24, 32), (int(ex), int(ey)), 2)

# Initialisation
koi_list = [
    KoiFish(random.uniform(150, WIDTH - 150), random.uniform(150, HEIGHT - 120))
    for _ in range(6)
]
lily_pads = [
    LilyPad(180, 190),
    LilyPad(WIDTH - 190, 220),
    LilyPad(240, HEIGHT - 140),
    LilyPad(WIDTH - 230, HEIGHT - 150)
]
ripples = []
pellets = []

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mouse_pos[1] > 80:
                # Clic gauche : Créer une onde sur l'eau et déposer un granulé
                ripples.append(Ripple(mouse_pos[0], mouse_pos[1], max_radius=110))
                pellets.append(FoodPellet(mouse_pos[0], mouse_pos[1]))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_k:
                if len(koi_list) < 12:
                    koi_list.append(KoiFish(random.uniform(150, WIDTH - 150), random.uniform(150, HEIGHT - 120)))
            elif event.key == pygame.K_l:
                if len(lily_pads) < 10:
                    lily_pads.append(LilyPad(random.uniform(120, WIDTH - 120), random.uniform(140, HEIGHT - 100)))
            elif event.key == pygame.K_r:
                koi_list = [KoiFish(random.uniform(150, WIDTH - 150), random.uniform(150, HEIGHT - 120)) for _ in range(6)]
                pellets = []
                ripples = []

    # Ondes spontanées légères
    if random.random() < 0.02:
        ripples.append(Ripple(random.uniform(80, WIDTH - 80), random.uniform(110, HEIGHT - 80), max_radius=65))

    # Mises à jour
    for r in ripples[:]:
        r.update()
        if r.radius >= r.max_radius:
            ripples.remove(r)

    for p in pellets:
        p.update()

    for pad in lily_pads:
        pad.update()

    for koi in koi_list:
        koi.update(pellets, ripples)

    # --- RENDU GRAPHIQUE ---
    screen.fill(POND_BG)

    # Reflet doux au centre du bassin
    pygame.draw.ellipse(screen, WATER_DEEP, (80, 105, WIDTH - 160, HEIGHT - 150))

    # Ondes sur l'eau
    for r in ripples:
        r.draw(screen)

    # Carpes Koï
    for koi in koi_list:
        koi.draw(screen)

    # Granulés flottants
    for p in pellets:
        p.draw(screen)

    # Nénuphars et fleurs de lotus (en surface)
    for pad in lily_pads:
        pad.draw(screen)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("ZEN KOI POND — BASSIN APAISANT & ONDES D'EAU", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Carpes Koï : {len(koi_list)} | Nénuphars : {len(lily_pads)} | Granulés : {len(pellets)}", True, (115, 205, 245))
    screen.blit(stats_txt, (40, 42))

    inst_txt = font_small.render("CLIC GAUCHE : Onde & Nourrir | K : Ajouter une Koï | L : Nénuphar | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 40, 42))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()