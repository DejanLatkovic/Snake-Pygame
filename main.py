import sys, time, platform
import pygame

# ---- minimal init (works in browser & desktop) ----
pygame.display.init()
pygame.font.init()

W, H = 960, 540
screen = pygame.display.set_mode((W, H), pygame.SCALED)  # browser-friendly
clock = pygame.time.Clock()
font_big  = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 28)

t0 = time.time()
x, y = 100, 100
vx, vy = 3, 2

def draw_hud():
    lines = [
        "SMOKE TEST — If you see this, render & events are OK",
        f"Python: {platform.python_version()}    pygame: {pygame.version.ver}",
        "Keys: arrows move box, ESC quits (desktop); click/tap does nothing here",
    ]
    yy = 10
    for line in lines:
        surf = font_small.render(line, True, (230, 230, 230))
        screen.blit(surf, (10, yy))
        yy += 26

def main():
    global x, y, vx, vy
    running = True
    while running:
        # ---- events ----
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                # (ESC won’t exit in the browser; that’s OK)
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  x -= 5
        if keys[pygame.K_RIGHT]: x += 5
        if keys[pygame.K_UP]:    y -= 5
        if keys[pygame.K_DOWN]:  y += 5

        # ---- simple animation ----
        x += vx
        y += vy
        if x < 0 or x > W - 80: vx = -vx
        if y < 0 or y > H - 80: vy = -vy

        # ---- draw ----
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (40, 40, 40), (0, 0, W, 70))
        draw_hud()
        pygame.draw.rect(screen, (5, 200, 90), (x, y, 80, 80))

        # FPS in corner
        fps = font_small.render(f"{int(clock.get_fps())} FPS", True, (220, 220, 220))
        screen.blit(fps, (W-100, 10))

        pygame.display.flip()
        clock.tick(60)

    # graceful quit (no-op in browser)
    try:
        pygame.quit()
    except Exception:
        pass

if __name__ == "__main__":
    main()
