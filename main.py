# minimal, web-ready pygame program (async-friendly for pygbag)
# works locally and on GitHub Pages (via pygbag)
import os, sys, asyncio, random
import pygame

# hide the pygame support prompt
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

WIDTH, HEIGHT = 1000, 800
FPS = 60
GRID = 20

BLACK = (0, 0, 0)
DARK = (24, 24, 24)
DGRAY = (40, 40, 40)
WHITE = (255, 255, 255)
GREEN = (0, 220, 0)
RED = (255, 70, 70)

# small helpers ----------------------------------------------------------------
def draw_grid(surf):
    for x in range(0, WIDTH, GRID):
        pygame.draw.line(surf, DGRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID):
        pygame.draw.line(surf, DGRAY, (0, y), (WIDTH, y))

def grid_random():
    return {
        "x": random.randint(0, (WIDTH // GRID) - 1),
        "y": random.randint(0, (HEIGHT // GRID) - 1),
    }

def center_rect(w, h):
    r = pygame.Rect(0, 0, w, h)
    r.center = (WIDTH // 2, HEIGHT // 2)
    return r

# start screen ------------------------------------------------------------------
async def start_screen(screen, clock, font):
    text = font.render("Ready to start !", True, (40, 40, 255))
    pad = 22
    box = pygame.Surface((text.get_width() + pad*2, text.get_height() + pad))
    box.fill(GREEN)
    pygame.draw.rect(box, BLACK, box.get_rect(), 8)
    box.blit(text, (pad, (box.get_height()-text.get_height())//2))

    rect = center_rect(box.get_width(), box.get_height())

    while True:
        screen.fill(DARK)
        screen.blit(box, rect)
        pygame.display.flip()

        # normal event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit
            if e.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                return

        clock.tick(FPS)
        # important on web: give control back to browser
        await asyncio.sleep(0)

# game loop ---------------------------------------------------------------------
async def game_loop(screen, clock, font):
    # tiny snake-like demo: arrow/WASD to move, eat red squares
    direction = (1, 0)  # start moving right
    snake = [{"x": 10, "y": 10}, {"x": 9, "y": 10}, {"x": 8, "y": 10}]
    food = grid_random()
    score = 0

    def draw_cell(c, color):
        r = pygame.Rect(c["x"]*GRID, c["y"]*GRID, GRID, GRID)
        pygame.draw.rect(screen, color, r)
        pygame.draw.rect(screen, BLACK, r, 1)

    while True:
        # events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    return  # back to start screen
                elif e.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    direction = (-1, 0)
                elif e.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    direction = (1, 0)
                elif e.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    direction = (0, -1)
                elif e.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    direction = (0, 1)

        # move
        head = {"x": snake[0]["x"] + direction[0], "y": snake[0]["y"] + direction[1]}

        # wrap around edges so we don't immediately "lose"
        head["x"] %= (WIDTH // GRID)
        head["y"] %= (HEIGHT // GRID)

        # collision with self -> reset to start screen
        if any(seg["x"] == head["x"] and seg["y"] == head["y"] for seg in snake):
            return

        snake.insert(0, head)

        # eat?
        if head["x"] == food["x"] and head["y"] == food["y"]:
            score += 1
            food = grid_random()
        else:
            snake.pop()

        # draw
        screen.fill(BLACK)
        draw_grid(screen)
        draw_cell(food, RED)
        for seg in snake:
            draw_cell(seg, GREEN)

        s = font.render(f"Score: {score}", True, WHITE)
        screen.blit(s, (WIDTH - s.get_width() - 16, 12))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)

# entrypoint --------------------------------------------------------------------
async def main_async():
    # init minimal subsystems
    pygame.display.init()
    pygame.font.init()
    try:
        # make sure no mixer runs (browser gesture gate)
        pygame.mixer.quit()
    except Exception:
        pass

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption("Wormy (web-ready)")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 60)

    # outer loop: start screen -> game -> start screen...
    while True:
        await start_screen(screen, clock, font)
        await game_loop(screen, clock, font)

def main():
    # Run async entry so pygbag can yield back to the browser cleanly
    try:
        asyncio.run(main_async())
    except SystemExit:
        pass

if __name__ == "__main__":
    main()
