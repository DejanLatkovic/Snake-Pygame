# Wormy (web-friendly)
import os, random, pygame, sys
from pygame.locals import *

# turn off the pygame “Hello” line
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

FPS         = 15
WINDOWWIDTH = 1000
WINDOWHEIGHT= 800
CELLSIZE    = 20
CELLWIDTH   = WINDOWWIDTH // CELLSIZE
CELLHEIGHT  = WINDOWHEIGHT // CELLSIZE

WHITE=(255,255,255); BLACK=(0,0,0); RED=(255,0,0)
GREEN=(0,255,0); DARKGREEN=(0,155,0); DARKGRAY=(40,40,40)
BROWN=(150,75,0); GOLD=(255,215,0)
BGCOLOR=BLACK
UP,DOWN,LEFT,RIGHT='up','down','left','right'
HEAD=0

def main():
    global DISPLAYSURF, BASICFONT, FPSCLOCK

    # Init only what we need; mixer intentionally off for web
    pygame.display.init()
    pygame.font.init()
    try:
        pygame.mixer.quit()  # make sure audio is really off
    except Exception:
        pass

    # >>> THIS WAS MISSING <<<
    FPSCLOCK = pygame.time.Clock()

    # Scaled canvas works well in browsers
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED)
    BASICFONT = pygame.font.Font(None, 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

def runGame():
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx, 'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    apple = getRandomLocation()
    gold  = {'x': -2, 'y': -1}
    poop  = [{'x': -1, 'y': -1}]
    count_g = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key in (K_LEFT, K_a)) and direction != RIGHT: direction = LEFT
                elif (event.key in (K_RIGHT, K_d)) and direction != LEFT: direction = RIGHT
                elif (event.key in (K_UP, K_w)) and direction != DOWN: direction = UP
                elif (event.key in (K_DOWN, K_s)) and direction != UP: direction = DOWN
                elif event.key == K_ESCAPE: terminate()

        # edge / self collision
        hx, hy = wormCoords[HEAD]['x'], wormCoords[HEAD]['y']
        if hx < 0 or hx >= CELLWIDTH or hy < 0 or hy >= CELLHEIGHT: return
        for body in wormCoords[1:]:
            if body['x'] == hx and body['y'] == hy: return

        # eat apple => drop poop at tail
        if hx == apple['x'] and hy == apple['y']:
            poop.append(wormCoords[-1])

        # hit poop => game over
        for p in poop:
            if hx == p['x'] and hy == p['y']: return

        # golden apple appears after 10 poop
        if len(poop) >= 10 and count_g == 0:
            count_g = 1
            gold = getRandomLocation()
        if hx == gold['x'] and hy == gold['y']:
            gold = {'x': -1, 'y': -1}
            poop = [{'x': -2, 'y': -1}]
            count_g = 0

        # handle apple/gold spawn safety, else move (drop tail)
        if hx == apple['x'] and hy == apple['y']:
            apple = getRandomLocation()
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
            del wormCoords[-1]

        # move head
        if direction == UP:    newHead={'x': hx,     'y': hy-1}
        elif direction == DOWN:newHead={'x': hx,     'y': hy+1}
        elif direction == LEFT:newHead={'x': hx-1,   'y': hy}
        else:                  newHead={'x': hx+1,   'y': hy}
        wormCoords.insert(0, newHead)

        # draw
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid(); drawWorm(wormCoords); drawApple(apple); drawgoldapple(gold)
        for item in poop: drawPoop(item)
        drawScore(len(wormCoords)-3)
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    surf = BASICFONT.render('Click or press any key to play.', True, DARKGRAY)
    rect = surf.get_rect()
    rect.topleft = (WINDOWWIDTH - 260, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(surf, rect)

def wait_for_start():
    while True:
        for e in pygame.event.get():
            if e.type == QUIT: terminate()
            if e.type in (KEYDOWN, KEYUP):
                if getattr(e, "key", None) == K_ESCAPE: terminate()
                return
            if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
                return
        pygame.time.wait(10)

def showStartScreen():
    titleFont = pygame.font.Font(None, 100)
    t1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    t2 = titleFont.render('Wormy!', True, GREEN)
    deg1 = deg2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        r1 = pygame.transform.rotate(t1, deg1); DISPLAYSURF.blit(r1, r1.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2)))
        r2 = pygame.transform.rotate(t2, deg2); DISPLAYSURF.blit(r2, r2.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2)))
        drawPressKeyMsg()
        pygame.display.flip()

        wait_for_start()
        pygame.event.get()
        return

def terminate():
    try: pygame.quit()
    except Exception: pass
    raise SystemExit

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH-1), 'y': random.randint(0, CELLHEIGHT-1)}

def showGameOverScreen():
    font = pygame.font.Font(None, 150)
    g = font.render('Game', True, WHITE); o = font.render('Over', True, WHITE)
    gr = g.get_rect(); or_ = o.get_rect()
    gr.midtop = (WINDOWWIDTH//2, 10)
    or_.midtop = (WINDOWWIDTH//2, gr.height + 35)
    DISPLAYSURF.blit(g, gr); DISPLAYSURF.blit(o, or_)
    drawPressKeyMsg(); pygame.display.flip()
    pygame.time.wait(500)
    while True:
        if checkForKeyPress():
            pygame.event.get()
            return

def checkForKeyPress():
    for e in pygame.event.get():
        if e.type == QUIT: terminate()
        if e.type in (KEYDOWN, KEYUP):
            if getattr(e, "key", None) == K_ESCAPE: terminate()
            return True
        if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
            return True
    return None

def drawScore(score):
    s = BASICFONT.render(f'Score: {score}', True, WHITE)
    r = s.get_rect(); r.topleft = (WINDOWWIDTH-120, 10)
    DISPLAYSURF.blit(s, r)

def drawWorm(coords):
    colours = [(0,0,139),(231,84,128),(155,135,12),(48,25,52),(0,155,0)]
    for c in coords:
        x, y = c['x']*CELLSIZE, c['y']*CELLSIZE
        outer = random.choice(colours)
        inner = (0,0,255) if outer==(0,0,139) else (255,192,203) if outer==(231,84,128) else (250,253,15) if outer==(155,135,12) else (106,13,173) if outer==(48,25,52) else (0,255,0)
        pygame.draw.rect(DISPLAYSURF, outer, pygame.Rect(x,y,CELLSIZE,CELLSIZE))
        pygame.draw.rect(DISPLAYSURF, inner, pygame.Rect(x+4,y+4,CELLSIZE-8,CELLSIZE-8))

def drawApple(c):
    pygame.draw.rect(DISPLAYSURF, RED, pygame.Rect(c['x']*CELLSIZE, c['y']*CELLSIZE, CELLSIZE, CELLSIZE))

def drawPoop(c):
    pygame.draw.rect(DISPLAYSURF, BROWN, pygame.Rect(c['x']*CELLSIZE, c['y']*CELLSIZE, CELLSIZE, CELLSIZE))

def drawgoldapple(c):
    pygame.draw.rect(DISPLAYSURF, GOLD, pygame.Rect(c['x']*CELLSIZE, c['y']*CELLSIZE, CELLSIZE, CELLSIZE))

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

if __name__ == '__main__':
    main()

