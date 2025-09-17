# Minimal, web-ready pygame demo; no audio; works in pygbag bundle.
import asyncio, os, pygame

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

WIDTH, HEIGHT = 1000, 800
FPS = 60
BLACK = (0, 0, 0)
GREEN = (0, 220, 0)

async def wait_for_any_input(screen, clock, font):
    text = font.render("Ready to start !", True, (40, 40, 255))
    pad = 22
    box = pygame.Surface((text.get_width()+pad*2, text.get_height()+pad))
    box.fill(GREEN); pygame.draw.rect(box, BLACK, box.get_rect(), 8)
    box.blit(text, (pad, (box.get_height()-text.get_height())//2))
    rect = box.get_rect(center=(WIDTH//2, HEIGHT//2))
    while True:
        screen.fill((24,24,24)); screen.blit(box, rect); pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: raise SystemExit
            if e.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                return
        clock.tick(FPS); await asyncio.sleep(0)

async def game(screen, clock):
    # just move a square to prove it renders
    x, y, vx, vy = 100, 100, 4, 3
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: raise SystemExit
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q):
                return
        x += vx; y += vy
        if x<0 or x>WIDTH-60: vx = -vx
        if y<0 or y>HEIGHT-60: vy = -vy
        screen.fill(BLACK)
        pygame.draw.rect(screen, GREEN, (x, y, 60, 60))
        pygame.display.flip()
        clock.tick(FPS); await asyncio.sleep(0)

async def main_async():
    pygame.display.init(); pygame.font.init()
    try: pygame.mixer.quit()   # make sure audio is fully disabled
    except Exception: pass
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Pygame Web Test")
    clock = pygame.time.Clock(); font = pygame.font.Font(None, 64)
    while True:
        await wait_for_any_input(screen, clock, font)
        await game(screen, clock)

def main():
    try: asyncio.run(main_async())
    except SystemExit: pass

if __name__ == "__main__":
    main()
