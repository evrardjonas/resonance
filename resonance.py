import pygame, sys, math

pygame.init()

# ---------- Physique ----------
V_SON = 343.0  # m/s

def frequences_resonance(L, type_tube, n_max=8):
    freqs = []
    for n in range(1, n_max + 1):
        if type_tube in ("ouvert-ouvert", "ferme-ferme"):
            f = n * V_SON / (2 * L)
        else:  # ouvert-ferme
            f = (2 * n - 1) * V_SON / (4 * L)
        freqs.append(f)
    return freqs

# ---------- Écran ----------
W, H = 900, 620
ecran = pygame.display.set_mode((W, H))
pygame.display.set_caption("Résonance dans un tube")
horloge = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)
font_petit = pygame.font.SysFont("arial", 17)

# ---------- Niveau ----------
L = 0.60                     # longueur du tube (m)
TYPE = "ouvert-ouvert"       # ou "ouvert-ferme"
F_MIN, F_MAX = 0.0, 1500.0
FREQ_INIT = 150.0
PAS = 3.0                    # Hz par frame quand on maintient la flèche
LARGEUR = 6.0                # largeur du pic de résonance (Hz)

resonances = frequences_resonance(L, TYPE)
freq = FREQ_INIT

tube_x0, tube_x1 = 100, 800
tube_y, tube_h = 320, 90

def amplitude_pour(f):
    """Lorentzienne : 1 au pic, décroît vite autour."""
    a = 0.0
    for fr in resonances:
        a = max(a, 1.0 / (1.0 + ((f - fr) / LARGEUR) ** 2))
    return a

def harmonique_proche(f):
    best, best_d = 0, 1e9
    for i, fr in enumerate(resonances):
        d = abs(f - fr)
        if d < best_d:
            best, best_d = i, d
    return best, best_d

# ---------- Boucle ----------
running = True
while running:
    horloge.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    touches = pygame.key.get_pressed()
    if touches[pygame.K_LEFT]:
        freq -= PAS
    if touches[pygame.K_RIGHT]:
        freq += PAS
    freq = max(F_MIN, min(F_MAX, freq))

    amp = amplitude_pour(freq)
    n_idx, dist = harmonique_proche(freq)
    n_harm = n_idx + 1

    ecran.fill((18, 18, 28))

    # --- Infos ---
    ecran.blit(font.render(f"Fréquence : {freq:6.1f} Hz", True, (240, 240, 240)), (30, 25))
    ecran.blit(font_petit.render(f"L = {L} m   |   tube {TYPE}", True, (170, 170, 200)), (30, 60))

    # --- Liste des résonances ---
    for i, fr in enumerate(resonances):
        y = 100 + i * 24
        proche = abs(freq - fr) < LARGEUR
        col = (120, 255, 130) if proche else (110, 110, 135)
        ecran.blit(font_petit.render(f"n={i+1}   f = {fr:7.1f} Hz", True, col), (30, y))

    # --- Tube ---
    pygame.draw.rect(ecran, (70, 70, 95), (tube_x0, tube_y, tube_x1 - tube_x0, tube_h), 2)

    # --- Onde stationnaire (déplacement) ---
    points = []
    N = 240
    for i in range(N + 1):
        x = i / N
        px = tube_x0 + x * (tube_x1 - tube_x0)
        if TYPE == "ouvert-ferme":
            y = math.cos((2 * n_harm - 1) * math.pi * x / 2)
        else:
            y = math.cos(n_harm * math.pi * x)
        py = tube_y + tube_h / 2 - y * amp * (tube_h / 2 - 4)
        points.append((px, py))
    pygame.draw.lines(ecran, (80, 220, 255), False, points, 2)

    # --- Barre d'amplitude ---
    ecran.blit(font_petit.render("Amplitude", True, (220, 220, 220)), (100, 445))
    pygame.draw.rect(ecran, (50, 50, 70), (100, 470, 700, 30))
    pygame.draw.rect(ecran, (255, 120, 80), (100, 470, int(700 * amp), 30))

    if amp > 0.85:
        ecran.blit(font.render("RÉSONANCE !", True, (255, 220, 80)), (370, 530))

    pygame.display.flip()

pygame.quit()