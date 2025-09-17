# Wormy (a Nibbles clone) — web-friendly version for pygbag + desktop
# Based on Al Sweigart's original. Tweaked for browser input/audio + fonts.

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"  # hide pygame banner

import random
import pygame
from pygame.locals import *

# --------------------------- Config ---------------------------

FPS = 15
WINDOWWIDTH  = 1000
WINDOWHEIGHT = 800
CELLSIZE     = 20

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

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # index of the worm's head

HAS_TOUCH = hasattr(pygame, "FINGERDOWN")

# --------------------------- App bootstrap ---------------------------

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    # Init only what we need; audio gets initialized (if at all) after a user gesture.
    pygame.display.init()
    pygame.font.init()

    # Make sure mixer isn't holding up browser autoplay policies
    try:
        pygame.mixer.quit()
    except Exception:
        pass

    # Create the window (SCALED plays nice with browser canvas)
    try:
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED, vsync=1)
    except TypeError:  # older pygame without vsync kw
        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED)

    FPSCLOCK  = pygame.time.Clock()            # <-- required; drives the game loop
    BASICFONT = pygame.font.Font(None, 18)     # use default font (works on web)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

_audio_inited = False
def init_sound_if_possible():
    """Try to init audio after a click/tap/key. Ignore failures (browser may still block)."""
    global _audio_inited
    if _audio_inited:
        return
    try:
        pygame.mixer.init()
        _audio_inited = True
    except Exception:
        pass

# --------------------------- Game loops ---------------------------

def runGame():
    # Random start point + 3-segment worm
    startx = random.randint(5, CELLWIDTH  - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Food + extras
    apple = getRandomLocation()
    gold  = {'x': -2, 'y': -1}          # offscreen until triggered
    poop  = [{'x': -1, 'y': -1}]        # list of barriers
    count_g = 0

    while True:  # main game loop
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

        # hit walls?
        hx, hy = wormCoords[HEAD]['x'], wormCoords[HEAD]['y']
        if hx == -1 or hx == CELLWIDTH or hy == -1 or hy == CELLHEIGHT:
            return  # game over

        # hit itself?
        for body in wormCoords[1:]:
            if body['x'] == hx and body['y'] == hy:
                return

        # leave poop where last segment was when eating an apple
        if hx == apple['x'] and hy == apple['y']:
            poop.append(wormCoords[-1])

        # hit poop?
        for item in poop:
            if hx == item['x'] and hy == item['y']:
                return

        # spawn golden apple after enough poop
        if len(poop) >= 10 and count_g == 0:
            count_g = 1
            gold = getRandomLocation()

        # eat golden apple: clear poop + reset
        if hx == gold['x'] and hy == gold['y']:
            gold    = {'x': -1, 'y': -1}
            poop    = [{'x': -2, 'y': -1}]
            count_g = 0

        # normal apple eaten?
        if hx == apple['x'] and hy == apple['y']:
            # grow: don't remove tail this tick
            apple = getRandomLocation()

            # avoid spawning on poop or gold
            safe = False
            while not safe:
                safe = True
                for item in poop:
                    if item == apple:
                        apple = getRandomLocation()
                        safe = False
                        break
                if apple == gold:
                    gold = getRandomLocation()
                    safe = False
        else:
            del wormCoords[-1]  # move forward by dropping tail

        # move head
        if direction == UP:
            newHead = {'x': hx,     'y': hy - 1}
        elif direction == DOWN:
            newHead = {'x': hx,     'y': hy + 1}
        elif direction == LEFT:
            newHead = {'x': hx - 1, 'y': hy}
        else:  # RIGHT
            newHead = {'x': hx + 1, 'y': hy}

        wormCoords.insert(0, newHead)

        # draw
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawgoldapple(gold)
        for item in poop:
            drawPoop(item)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

# --------------------------- UI helpers ---------------------------

def drawPressKeyMsg():
    msg = 'Click or press any key to play.'
    pressKeySurf = BASICFONT.render(msg, True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 260, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

def wait_for_start():
    """Block here until a key, click, or tap occurs (Esc still quits)."""
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()

            if e.type in (KEYDOWN, KEYUP):
                if getattr(e, "key", None) == K_ESCAPE:
                    terminate()
                init_sound_if_possible()
                return

            if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                init_sound_if_possible()
                return

            if HAS_TOUCH and e.type in (FINGERDOWN, FINGERUP):
                init_sound_if_possible()
                return

        pygame.time.wait(10)

def checkForKeyPress():
    """Used on Game Over screen; accept key, click, or tap."""
    for e in pygame.event.get():
        if e.type == QUIT:
            terminate()
        if e.type in (KEYDOWN, KEYUP):
            if getattr(e, "key", None) == K_ESCAPE:
                terminate()
            return True
        if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
            return True
        if HAS_TOUCH and e.type in (FINGERDOWN, FINGERUP):
            return True
    return None

def showStartScreen():
    titleFont  = pygame.font.Font(None, 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)
    degrees1 = degrees2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        r1 = pygame.transform.rotate(titleSurf1, degrees1)
        r2 = pygame.transform.rotate(titleSurf2, degrees2)
        DISPLAYSURF.blit(r1, r1.get_rect(center=(WINDOWWIDTH // 2, WINDOWHEIGHT // 2)))
        DISPLAYSURF.blit(r2, r2.get_rect(center=(WINDOWWIDTH // 2, WINDOWHEIGHT // 2)))
        drawPressKeyMsg()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        wait_for_start()
        pygame.event.get()  # clear leftovers so gameplay starts clean
        return

def terminate():
    try:
        pygame.quit()
    finally:
        raise SystemExit

# --------------------------- Drawing ---------------------------

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1),
            'y': random.randint(0, CELLHEIGHT - 1)}

def showGameOverScreen():
    gameOverFont = pygame.font.Font(None, 150)
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
    pygame.time.wait(500)
    pygame.event.get()  # flush

    while True:
        if checkForKeyPress():
            pygame.event.get()
            return

def drawScore(score):
    scoreSurf = BASICFONT.render(f'Score: {score}', True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def drawWorm(wormCoords):
    colours_outer = [DARKBLUE, DARKPINK, DARKYELLOW, DARKPURPLE, DARKGREEN]
    for coord in wormCoords:
        choice_outer = random.choice(colours_outer)
        if   choice_outer == DARKBLUE:   choice_inner = BLUE
        elif choice_outer == DARKPINK:   choice_inner = PINK
        elif choice_outer == DARKYELLOW: choice_inner = YELLOW
        elif choice_outer == DARKPURPLE: choice_inner = PURPLE
        else:                            choice_inner = GREEN

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

# --------------------------- Entrypoint ---------------------------

if __name__ == '__main__':
    main()

