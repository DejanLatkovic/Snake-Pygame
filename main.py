# Wormy (web-friendly pygame-ce / pygbag build)
# Original idea by Al Sweigart. This version refactored for web.
import os, sys, random
import pygame
from pygame.locals import *

# Hide the pygame support prompt
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Detect pygbag/browser
RUNNING_IN_BROWSER = (sys.platform == "emscripten") or (os.environ.get("PYGBAG") == "1")

# ---------------------- Config ----------------------
FPS = 15
WINDOWWIDTH  = 800   # fits pygbag's default canvas well
WINDOWHEIGHT = 600
CELLSIZE = 20
assert WINDOWWIDTH  % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH  = WINDOWWIDTH  // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# Colors
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BROWN     = (150,  75,   0)

DARKBLUE   = (  0,   0, 139)
DARKPINK   = (231,  84, 128)
DARKYELLOW = (155, 135,  12)
DARKPURPLE = ( 48,  25,  52)
BLUE       = (  0,   0, 255)
PINK       = (255, 192, 203)
YELLOW     = (250, 253,  15)
PURPLE     = (106,  13, 173)
GOLD       = (255, 215,   0)

BGCOLOR = BLACK

# Directions
UP = 'up'; DOWN = 'down'; LEFT = 'left'; RIGHT = 'right'

HEAD = 0  # index of the worm's head

# Globals filled in main()
FPSCLOCK = None
DISPLAYSURF = None
BASICFONT = None

# ----------------------------------------------------
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    # Init minimal subsystems explicitly (web-friendly)
    pygame.display.init()
    pygame.font.init()
    # Disable audio to avoid browser "user gesture" blockers
    try:
        pygame.mixer.quit()
    except Exception:
        pass

    FPSCLOCK = pygame.time.Clock()

    # SCALED plays nice with browser canvas
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED)
    pygame.display.set_caption("Wormy")

    BASICFONT = pygame.font.Font(None, 24)

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Random start point
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [
        {'x': startx,     'y': starty},
        {'x': startx - 1, 'y': starty},
        {'x': startx - 2, 'y': starty}
    ]
    direction = RIGHT

    # First apple
    apple = getRandomLocation()

    # Barriers (“poop”) and golden apple
    gold = {'x': -2, 'y': -1}        # off-screen sentinel
    poop = [{'x': -1, 'y': -1}]      # off-screen sentinel
    gold_ready_flag = 0

    while True:  # main loop
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key in (K_LEFT,  K_a)) and direction != RIGHT:
                    direction = LEFT
                elif (event.key in (K_RIGHT, K_d)) and direction != LEFT:
                    direction = RIGHT
                elif (event.key in (K_UP,    K_w)) and direction != DOWN:
                    direction = UP
                elif (event.key in (K_DOWN,  K_s)) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # Wall collision
        if (wormCoords[HEAD]['x'] < 0 or wormCoords[HEAD]['x'] >= CELLWIDTH or
            wormCoords[HEAD]['y'] < 0 or wormCoords[HEAD]['y'] >= CELLHEIGHT):
            return  # game over

        # Self collision
        for body in wormCoords[1:]:
            if body['x'] == wormCoords[HEAD]['x'] and body['y'] == wormCoords[HEAD]['y']:
                return

        # If we just ate an apple, drop a poop where the tail was
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            poop.append(wormCoords[-1])

        # Hit a poop? game over
        for item in poop:
            if wormCoords[HEAD]['x'] == item['x'] and wormCoords[HEAD]['y'] == item['y']:
                return

        # Golden apple appears once poop list reaches 10 tiles
        if len(poop) >= 10 and gold_ready_flag == 0:
            gold_ready_flag = 1
            gold = getRandomLocation()

        # Eat golden apple: clear poop, hide gold
        if wormCoords[HEAD]['x'] == gold['x'] and wormCoords[HEAD]['y'] == gold['y']:
            gold = {'x': -1, 'y': -1}
            poop = [{'x': -2, 'y': -1}]
            gold_ready_flag = 0

        # Regular apple eating & respawn (avoid overlap with poop/gold)
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            apple = getRandomLocation()
            # Ensure apple and gold don't land on poop or each other
            safe = False
            while not safe:
                safe = True
                for item in poop:
                    if item == apple:
                        apple = getRandomLocation()
                        safe = False
                        break
                if gold == apple:
                    apple = getRandomLocation()
                    safe = False
        else:
            # Move forward by removing tail unless we just ate
            del wormCoords[-1]

        # Move the worm by adding a new head
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'],     'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'],     'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        else:  # RIGHT
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)

        # Draw
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawgoldapple(gold)  # golden apple (off-screen if not active)
        for item in poop:
            drawPoop(item)
        drawScore(len(wormCoords) - 3)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


# ---------------------- UI helpers ----------------------
def drawPressKeyMsg():
    msg = 'Click / tap or press any key to play.'
    pressKeySurf = BASICFONT.render(msg, True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (20, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def wait_for_start():
    """Return after any click/tap/key (Esc still quits)."""
    # Handle touch on mobile if available
    HAS_TOUCH = hasattr(pygame, "FINGERDOWN")
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            if e.type in (KEYDOWN, KEYUP):
                if getattr(e, "key", None) == K_ESCAPE:
                    terminate()
                return
            if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                return
            if HAS_TOUCH and e.type in (pygame.FINGERDOWN, pygame.FINGERUP):
                return
        pygame.time.wait(10)


def showStartScreen():
    titleFont = pygame.font.Font(None, 96)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)
    degrees1 = 0
    degrees2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        r1 = pygame.transform.rotate(titleSurf1, degrees1)
        r2 = pygame.transform.rotate(titleSurf2, degrees2)
        DISPLAYSURF.blit(r1, r1.get_rect(center=(WINDOWWIDTH // 2, WINDOWHEIGHT // 2)))
        DISPLAYSURF.blit(r2, r2.get_rect(center=(WINDOWWIDTH // 2, WINDOWHEIGHT // 2)))
        drawPressKeyMsg()
        pygame.display.update()

        # spin titles
        degrees1 = (degrees1 + 3) % 360
        degrees2 = (degrees2 + 7) % 360
        FPSCLOCK.tick(FPS)

        # leave when we get user input
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            if e.type in (KEYDOWN, KEYUP):
                if getattr(e, "key", None) == K_ESCAPE:
                    terminate()
                pygame.event.get()  # clear any leftovers
                return
            if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                pygame.event.get()
                return


def terminate():
    try:
        pygame.quit()
    except Exception:
        pass
    raise SystemExit


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1),
            'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font(None, 120)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH // 2, 10)
    overRect.midtop = (WINDOWWIDTH // 2, gameRect.height + 35)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(400)

    # Wait for user to continue
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            if e.type in (KEYDOWN, KEYUP):
                if getattr(e, "key", None) == K_ESCAPE:
                    terminate()
                pygame.event.get()
                return
            if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                pygame.event.get()
                return
        FPSCLOCK.tick(30)


def drawScore(score):
    scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topright = (WINDOWWIDTH - 10, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    colours_outer = [DARKBLUE, DARKPINK, DARKYELLOW, DARKPURPLE, DARKGREEN]
    for coord in wormCoords:
        choice_outer = random.choice(colours_outer)
        if choice_outer == DARKBLUE:   choice_inner = BLUE
        elif choice_outer == DARKPINK: choice_inner = PINK
        elif choice_outer == DARKYELLOW: choice_inner = YELLOW
        elif choice_outer == DARKPURPLE: choice_inner = PURPLE
        else: choice_inner = GREEN

        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        outer = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        inner = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, choice_outer, outer)
        pygame.draw.rect(DISPLAYSURF, choice_inner, inner)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, RED, pygame.Rect(x, y, CELLSIZE, CELLSIZE))


def drawPoop(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, BROWN, pygame.Rect(x, y, CELLSIZE, CELLSIZE))


def drawgoldapple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, GOLD, pygame.Rect(x, y, CELLSIZE, CELLSIZE))


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


# Launch in both desktop and web (pygbag renames to site.py)
if __name__ == "__main__" or RUNNING_IN_BROWSER:
    main()
