# Wormy (a Nibbles clone) — pygame-web friendly version

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"   # hide pygame banner on desktop

import random
import pygame
from pygame.locals import *

# ---- Config -----------------------------------------------------------------
FPS = 15
WINDOWWIDTH  = 1000
WINDOWHEIGHT = 800
CELLSIZE     = 20
assert WINDOWWIDTH  % CELLSIZE == 0
assert WINDOWHEIGHT % CELLSIZE == 0
CELLWIDTH  = WINDOWWIDTH  // CELLSIZE
CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# colors
WHITE=(255,255,255); BLACK=(0,0,0); RED=(255,0,0)
GREEN=(0,255,0); DARKGREEN=(0,155,0); DARKGRAY=(40,40,40); BROWN=(150,75,0)
DARKBLUE=(0,0,139); DARKPINK=(231,84,128); DARKYELLOW=(155,135,12)
DARKPURPLE=(48,25,52); BLUE=(0,0,255); PINK=(255,192,203)
YELLOW=(250,253,15); PURPLE=(106,13,173); GOLD=(255,215,0)
BGCOLOR = BLACK

UP, DOWN, LEFT, RIGHT = "up", "down", "left", "right"
HEAD = 0

# detect touch constants exist (always true on pygame 2, but harmless)
HAS_TOUCH = hasattr(pygame, "FINGERDOWN")

# ---- Boot / main loop -------------------------------------------------------
def main():
    # pygame-web works best if we keep things simple
    pygame.init()
    # shut off audio completely so the browser doesn't require a user gesture
    try:
        pygame.mixer.quit()
    except Exception:
        pass

    global DISPLAYSURF, BASICFONT, FPSCLOCK
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED)
    pygame.display.set_caption("Wormy")
    BASICFONT = pygame.font.Font(None, 18)
    FPSCLOCK  = pygame.time.Clock()

    print("[wormy] boot ok")
    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

# ---- Game -------------------------------------------------------------------
def runGame():
    startx = random.randint(5, CELLWIDTH  - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx, 'y': starty},
                  {'x': startx-1, 'y': starty},
                  {'x': startx-2, 'y': starty}]
    direction = RIGHT

    apple = getRandomLocation()
    gold  = {'x': -2, 'y': -1}        # hidden off-screen until spawned
    poop  = [{'x': -1, 'y': -1}]
    count_g = 0

    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            elif e.type == KEYDOWN:
                if (e.key in (K_LEFT,  K_a)) and direction != RIGHT: direction = LEFT
                elif (e.key in (K_RIGHT, K_d)) and direction != LEFT: direction = RIGHT
                elif (e.key in (K_UP,    K_w)) and direction != DOWN:  direction = UP
                elif (e.key in (K_DOWN,  K_s)) and direction != UP:    direction = DOWN
                elif e.key == K_ESCAPE: terminate()

        # hit wall?
        hx, hy = wormCoords[HEAD]['x'], wormCoords[HEAD]['y']
        if hx < 0 or hx >= CELLWIDTH or hy < 0 or hy >= CELLHEIGHT:
            return
        # hit itself?
        for wb in wormCoords[1:]:
            if wb['x'] == hx and wb['y'] == hy:
                return

        # drop poop when eating apple (barrier)
        if hx == apple['x'] and hy == apple['y']:
            poop.append(wormCoords[-1])

        # hit poop?
        for item in poop:
            if hx == item['x'] and hy == item['y']:
                return

        # golden apple after 10 poop
        if len(poop) >= 10 and count_g == 0:
            count_g = 1
            gold = getRandomLocation()

        if hx == gold['x'] and hy == gold['y']:
            gold = {'x': -1, 'y': -1}
            poop = [{'x': -2, 'y': -1}]
            count_g = 0

        # eat apple?
        if hx == apple['x'] and hy == apple['y']:
            apple = getRandomLocation()
            # keep apples/gold off poop
            safe = False
            while not safe:
                safe = True
                for item in poop:
                    if item == apple:
                        apple = getRandomLocation(); safe = False; break
                    if item == gold:
                        gold = getRandomLocation(); safe = False; break
        else:
            del wormCoords[-1]  # move by popping tail

        # advance head
        if direction == UP:    newHead = {'x': hx,     'y': hy-1}
        if direction == DOWN:  newHead = {'x': hx,     'y': hy+1}
        if direction == LEFT:  newHead = {'x': hx-1,   'y': hy}
        if direction == RIGHT: newHead = {'x': hx+1,   'y': hy}
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
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

# ---- UI screens -------------------------------------------------------------
def showStartScreen():
    titleFont = pygame.font.Font(None, 100)
    title1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    title2 = titleFont.render('Wormy!', True, GREEN)
    d1 = d2 = 0

    print("[wormy] start screen")
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: terminate()
                return
            if e.type in (MOUSEBUTTONDOWN,) or (HAS_TOUCH and e.type == FINGERDOWN):
                return

        DISPLAYSURF.fill(BGCOLOR)
        r1 = pygame.transform.rotate(title1, d1)
        r2 = pygame.transform.rotate(title2, d2)
        DISPLAYSURF.blit(r1, r1.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2)))
        DISPLAYSURF.blit(r2, r2.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2)))
        drawPressKeyMsg()
        pygame.display.flip()
        d1 = (d1 + 3) % 360
        d2 = (d2 + 7) % 360
        FPSCLOCK.tick(FPS)

def showGameOverScreen():
    gameOverFont = pygame.font.Font(None, 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect(midtop=(WINDOWWIDTH // 2, 10))
    overRect = overSurf.get_rect(midtop=(WINDOWWIDTH // 2, gameRect.height + 35))

    print("[wormy] game over")
    while True:
        for e in pygame.event.get():
            if e.type == QUIT: terminate()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: terminate()
                return
            if e.type in (MOUSEBUTTONDOWN,) or (HAS_TOUCH and e.type == FINGERDOWN):
                return

        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(gameSurf, gameRect)
        DISPLAYSURF.blit(overSurf, overRect)
        drawPressKeyMsg()
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

# ---- Helpers ----------------------------------------------------------------
def terminate():
    try:
        pygame.quit()
    finally:
        raise SystemExit

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH-1), 'y': random.randint(0, CELLHEIGHT-1)}

def drawPressKeyMsg():
    surf = BASICFONT.render('Click or press any key to play.', True, DARKGRAY)
    rect = surf.get_rect()
    rect.topleft = (WINDOWWIDTH - 260, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(surf, rect)

def drawScore(score):
    surf = BASICFONT.render(f'Score: {score}', True, WHITE)
    rect = surf.get_rect(topleft=(WINDOWWIDTH - 120, 10))
    DISPLAYSURF.blit(surf, rect)

def drawWorm(wormCoords):
    palette = [DARKBLUE, DARKPINK, DARKYELLOW, DARKPURPLE, DARKGREEN]
    for c in wormCoords:
        outer = random.choice(palette)
        inner = {DARKBLUE: BLUE, DARKPINK: PINK, DARKYELLOW: YELLOW,
                 DARKPURPLE: PURPLE, DARKGREEN: GREEN}[outer]
        x, y = c['x'] * CELLSIZE, c['y'] * CELLSIZE
        pygame.draw.rect(DISPLAYSURF, outer, pygame.Rect(x, y, CELLSIZE, CELLSIZE))
        pygame.draw.rect(DISPLAYSURF, inner, pygame.Rect(x+4, y+4, CELLSIZE-8, CELLSIZE-8))

def drawApple(coord):
    x, y = coord['x'] * CELLSIZE, coord['y'] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, RED, pygame.Rect(x, y, CELLSIZE, CELLSIZE))

def drawPoop(coord):
    x, y = coord['x'] * CELLSIZE, coord['y'] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, BROWN, pygame.Rect(x, y, CELLSIZE, CELLSIZE))

def drawgoldapple(coord):
    x, y = coord['x'] * CELLSIZE, coord['y'] * CELLSIZE
    pygame.draw.rect(DISPLAYSURF, GOLD, pygame.Rect(x, y, CELLSIZE, CELLSIZE))

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

# ---- Entrypoint -------------------------------------------------------------
if __name__ == "__main__":
    main()
