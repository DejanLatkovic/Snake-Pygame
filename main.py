import os, random, sys, pygame
from pygame.locals import *

# ---- no audio on web ----
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

FPS = 15
WINDOWWIDTH, WINDOWHEIGHT = 1000, 800
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0
assert WINDOWHEIGHT % CELLSIZE == 0
CELLWIDTH, CELLHEIGHT = WINDOWWIDTH // CELLSIZE, WINDOWHEIGHT // CELLSIZE

WHITE=(255,255,255); BLACK=(0,0,0); RED=(255,0,0)
GREEN=(0,255,0); DARKGREEN=(0,155,0); DARKGRAY=(40,40,40)
BROWN=(150,75,0); GOLD=(255,215,0)
DARKBLUE=(0,0,139); BLUE=(0,0,255)
DARKPINK=(231,84,128); PINK=(255,192,203)
DARKYELLOW=(155,135,12); YELLOW=(250,253,15)
DARKPURPLE=(48,25,52); PURPLE=(106,13,173)

UP, DOWN, LEFT, RIGHT = "up","down","left","right"
HEAD = 0

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    pygame.display.init()
    pygame.font.init()
    # scaled = resizes nicely in the canvas
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED)
    pygame.display.set_caption("Wormy")
    BASICFONT = pygame.font.Font(None, 18)
    FPSCLOCK = pygame.time.Clock()
    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

def runGame():
    startx = random.randint(5, CELLWIDTH-6)
    starty = random.randint(5, CELLHEIGHT-6)
    wormCoords = [{'x':startx,'y':starty},{'x':startx-1,'y':starty},{'x':startx-2,'y':starty}]
    direction = RIGHT
    apple = getRandomLocation()

    gold = {'x': -2, 'y': -1}
    poop = [{'x': -1, 'y': -1}]
    count_g = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key in (K_LEFT,K_a)) and direction!=RIGHT:  direction = LEFT
                elif (event.key in (K_RIGHT,K_d)) and direction!=LEFT: direction = RIGHT
                elif (event.key in (K_UP,K_w)) and direction!=DOWN:     direction = UP
                elif (event.key in (K_DOWN,K_s)) and direction!=UP:     direction = DOWN
                elif event.key == K_ESCAPE: terminate()

        if (wormCoords[HEAD]['x'] in (-1, CELLWIDTH) or
            wormCoords[HEAD]['y'] in (-1, CELLHEIGHT)):
            return
        for body in wormCoords[1:]:
            if body['x']==wormCoords[HEAD]['x'] and body['y']==wormCoords[HEAD]['y']:
                return

        if wormCoords[HEAD]==apple:
            poop.append(wormCoords[-1])
            apple = getRandomSafeLocation(poop, gold)
        else:
            del wormCoords[-1]

        if any(wormCoords[HEAD]==p for p in poop):
            return

        if len(poop) >= 10 and count_g == 0:
            count_g = 1
            gold = getRandomSafeLocation(poop, None)

        if wormCoords[HEAD]==gold:
            gold = {'x':-1,'y':-1}
            poop = [{'x':-2,'y':-1}]
            count_g = 0

        if direction == UP:    newHead={'x':wormCoords[HEAD]['x'],   'y':wormCoords[HEAD]['y']-1}
        if direction == DOWN:  newHead={'x':wormCoords[HEAD]['x'],   'y':wormCoords[HEAD]['y']+1}
        if direction == LEFT:  newHead={'x':wormCoords[HEAD]['x']-1, 'y':wormCoords[HEAD]['y']}
        if direction == RIGHT: newHead={'x':wormCoords[HEAD]['x']+1, 'y':wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)

        DISPLAYSURF.fill(BLACK)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        drawgoldapple(gold)
        for p in poop: drawPoop(p)
        drawScore(len(wormCoords)-3)
        pygame.display.flip()
        FPSCLOCK.tick(FPS)

def getRandomLocation():
    return {'x': random.randint(0,CELLWIDTH-1), 'y': random.randint(0,CELLHEIGHT-1)}

def getRandomSafeLocation(poop, gold):
    while True:
        loc = getRandomLocation()
        if poop and any(loc==p for p in poop): continue
        if gold and loc==gold: continue
        return loc

def drawPressKeyMsg():
    surf = BASICFONT.render("Click or press any key to play.", True, DARKGRAY)
    rect = surf.get_rect()
    rect.topleft = (WINDOWWIDTH-260, WINDOWHEIGHT-30)
    DISPLAYSURF.blit(surf, rect)

def showStartScreen():
    titleFont = pygame.font.Font(None, 100)
    t1 = titleFont.render("Wormy!", True, WHITE, DARKGREEN)
    t2 = titleFont.render("Wormy!", True, GREEN)
    deg1 = deg2 = 0
    while True:
        DISPLAYSURF.fill(BLACK)
        r1 = pygame.transform.rotate(t1, deg1)
        r2 = pygame.transform.rotate(t2, deg2)
        DISPLAYSURF.blit(r1, r1.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2)))
        DISPLAYSURF.blit(r2, r2.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2)))
        drawPressKeyMsg()
        pygame.display.flip()
        if wait_for_start(): return
        deg1 += 3; deg2 += 7
        FPSCLOCK.tick(FPS)

def wait_for_start():
    for e in pygame.event.get():
        if e.type == QUIT: terminate()
        if e.type in (KEYDOWN, KEYUP):
            if getattr(e,"key",None) == K_ESCAPE: terminate()
            return True
        if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP) or hasattr(pygame,"FINGERDOWN") and e.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            return True
    pygame.time.wait(10)
    return False

def showGameOverScreen():
    f = pygame.font.Font(None, 150)
    g = f.render("Game", True, WHITE)
    o = f.render("Over", True, WHITE)
    gr, orc = g.get_rect(), o.get_rect()
    gr.midtop = (WINDOWWIDTH//2, 10)
    orc.midtop = (WINDOWWIDTH//2, gr.height + 35)
    DISPLAYSURF.blit(g, gr); DISPLAYSURF.blit(o, orc)
    drawPressKeyMsg()
    pygame.display.flip()
    pygame.time.wait(500)
    while True:
        k = checkForKeyPress()
        if k: return

def checkForKeyPress():
    for e in pygame.event.get():
        if e.type == QUIT: terminate()
        if e.type in (KEYDOWN, KEYUP):
            if getattr(e,"key",None) == K_ESCAPE: terminate()
            return True
        if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP) or hasattr(pygame,"FINGERDOWN") and e.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            return True
    return None

def drawScore(score):
    surf = BASICFONT.render(f"Score: {score}", True, WHITE)
    rect = surf.get_rect()
    rect.topleft = (WINDOWWIDTH-120, 10)
    DISPLAYSURF.blit(surf, rect)

def drawWorm(wormCoords):
    colours = [(DARKBLUE,BLUE),(DARKPINK,PINK),(DARKYELLOW,YELLOW),(DARKPURPLE,PURPLE),(DARKGREEN,GREEN)]
    for c in wormCoords:
        outer, inner = random.choice(colours)
        x, y = c['x']*CELLSIZE, c['y']*CELLSIZE
        pygame.draw.rect(DISPLAYSURF, outer, (x,y,CELLSIZE,CELLSIZE))
        pygame.draw.rect(DISPLAYSURF, inner, (x+4,y+4,CELLSIZE-8,CELLSIZE-8))

def drawApple(c):
    x,y = c['x']*CELLSIZE, c['y']*CELLSIZE
    pygame.draw.rect(DISPLAYSURF, RED, (x,y,CELLSIZE,CELLSIZE))

def drawPoop(c):
    x,y = c['x']*CELLSIZE, c['y']*CELLSIZE
    pygame.draw.rect(DISPLAYSURF, BROWN, (x,y,CELLSIZE,CELLSIZE))

def drawgoldapple(c):
    x,y = c['x']*CELLSIZE, c['y']*CELLSIZE
    pygame.draw.rect(DISPLAYSURF, GOLD, (x,y,CELLSIZE,CELLSIZE))

def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x,0), (x,WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0,y), (WINDOWWIDTH,y))

def terminate():
    try: pygame.quit()
    finally: sys.exit()

if __name__ == "__main__":
    main()
