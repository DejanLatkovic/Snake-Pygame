# import os, sys, random, pygame
# from pygame.locals import *

# # ---- constants ----
# FPS = 15
# WINDOWWIDTH, WINDOWHEIGHT = 1000, 800
# CELLSIZE = 20
# CELLWIDTH  = WINDOWWIDTH  // CELLSIZE
# CELLHEIGHT = WINDOWHEIGHT // CELLSIZE

# WHITE=(255,255,255); BLACK=(0,0,0); RED=(255,0,0)
# GREEN=(0,255,0); DARKGREEN=(0,155,0); DARKGRAY=(40,40,40)
# BROWN=(150,75,0); GOLD=(255,215,0)
# BGCOLOR = BLACK

# UP='up'; DOWN='down'; LEFT='left'; RIGHT='right'
# HEAD = 0

# # globals pygame needs
# FPSCLOCK = None
# DISPLAYSURF = None
# BASICFONT = None

# def log(msg):  # prints to pygbag overlay + DevTools console
#     print(msg); sys.stdout.flush()

# def init_pygame():
#     global FPSCLOCK, DISPLAYSURF, BASICFONT
#     pygame.init()  # safe on web
#     # keep it simple: no vsync flag
#     DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.SCALED)
#     pygame.display.set_caption('Wormy (web)')
#     BASICFONT = pygame.font.Font(None, 24)
#     FPSCLOCK = pygame.time.Clock()    # <- the one that was missing in some edits
#     log("pygame initialized")

# def drawGrid():
#     for x in range(0, WINDOWWIDTH, CELLSIZE):
#         pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
#     for y in range(0, WINDOWHEIGHT, CELLSIZE):
#         pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

# def drawWorm(worm):
#     for seg in worm:
#         x = seg['x'] * CELLSIZE
#         y = seg['y'] * CELLSIZE
#         pygame.draw.rect(DISPLAYSURF, DARKGREEN, (x, y, CELLSIZE, CELLSIZE))
#         pygame.draw.rect(DISPLAYSURF, GREEN, (x+4, y+4, CELLSIZE-8, CELLSIZE-8))

# def drawApple(coord):
#     x = coord['x'] * CELLSIZE
#     y = coord['y'] * CELLSIZE
#     pygame.draw.rect(DISPLAYSURF, RED, (x, y, CELLSIZE, CELLSIZE))

# def drawPoop(coord):
#     x = coord['x'] * CELLSIZE
#     y = coord['y'] * CELLSIZE
#     pygame.draw.rect(DISPLAYSURF, BROWN, (x, y, CELLSIZE, CELLSIZE))

# def drawgoldapple(coord):
#     x = coord['x'] * CELLSIZE
#     y = coord['y'] * CELLSIZE
#     pygame.draw.rect(DISPLAYSURF, GOLD, (x, y, CELLSIZE, CELLSIZE))

# def drawScore(score):
#     surf = BASICFONT.render(f"Score: {score}", True, WHITE)
#     rect = surf.get_rect()
#     rect.topleft = (WINDOWWIDTH - 140, 10)
#     DISPLAYSURF.blit(surf, rect)

# def getRandomLocation():
#     return {'x': random.randint(0, CELLWIDTH-1), 'y': random.randint(0, CELLHEIGHT-1)}

# def wait_for_start():
#     # accept click or any key
#     while True:
#         for e in pygame.event.get():
#             if e.type == QUIT:
#                 pygame.quit(); raise SystemExit
#             if e.type in (KEYDOWN, KEYUP):
#                 if getattr(e, "key", None) == K_ESCAPE:
#                     pygame.quit(); raise SystemExit
#                 log("start: key"); return
#             if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
#                 log("start: mouse"); return
#         pygame.time.wait(10)

# def showStartScreen():
#     titleFont  = pygame.font.Font(None, 100)
#     titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
#     titleSurf2 = titleFont.render('Wormy!', True, GREEN)

#     DISPLAYSURF.fill((127,127,127))
#     # button-like text:
#     msg = pygame.font.Font(None, 72).render("Ready to start !", True, (30,40,255))
#     msg_rect = msg.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))
#     pad_rect = msg_rect.inflate(600, 40)
#     pygame.draw.rect(DISPLAYSURF, (30,30,30), pad_rect, 6)
#     pygame.draw.rect(DISPLAYSURF, (0,230,0), pad_rect)
#     DISPLAYSURF.blit(msg, msg_rect)
#     pygame.display.update()

#     wait_for_start()
#     log("leaving start screen")

# def runGame():
#     log("game loop BEGIN")
#     startx = random.randint(5, CELLWIDTH - 6)
#     starty = random.randint(5, CELLHEIGHT - 6)
#     worm = [{'x': startx, 'y': starty},
#             {'x': startx-1, 'y': starty},
#             {'x': startx-2, 'y': starty}]
#     direction = RIGHT

#     apple = getRandomLocation()
#     gold  = {'x': -2, 'y': -1}
#     poop  = [{'x': -1, 'y': -1}]
#     count_g = 0

#     while True:
#         for e in pygame.event.get():
#             if e.type == QUIT:
#                 pygame.quit(); raise SystemExit
#             if e.type == KEYDOWN:
#                 if (e.key in (K_LEFT, K_a)) and direction != RIGHT:  direction = LEFT
#                 elif (e.key in (K_RIGHT, K_d)) and direction != LEFT: direction = RIGHT
#                 elif (e.key in (K_UP, K_w)) and direction != DOWN:    direction = UP
#                 elif (e.key in (K_DOWN, K_s)) and direction != UP:    direction = DOWN
#                 elif e.key == K_ESCAPE:
#                     pygame.quit(); raise SystemExit

#         # borders or self
#         if (worm[HEAD]['x'] < 0 or worm[HEAD]['x'] >= CELLWIDTH or
#             worm[HEAD]['y'] < 0 or worm[HEAD]['y'] >= CELLHEIGHT):
#             log("hit wall -> game over"); return
#         for body in worm[1:]:
#             if body['x'] == worm[HEAD]['x'] and body['y'] == worm[HEAD]['y']:
#                 log("hit self -> game over"); return

#         # poop barrier when eating apple
#         if worm[HEAD]['x'] == apple['x'] and worm[HEAD]['y'] == apple['y']:
#             poop.append(worm[-1])

#         for item in poop:
#             if worm[HEAD]['x'] == item['x'] and worm[HEAD]['y'] == item['y']:
#                 log("hit poop -> game over"); return

#         if len(poop) >= 10 and count_g == 0:
#             count_g = 1
#             gold = getRandomLocation()

#         if worm[HEAD]['x'] == gold['x'] and worm[HEAD]['y'] == gold['y']:
#             gold = {'x': -1, 'y': -1}
#             poop = [{'x': -2, 'y': -1}]
#             count_g = 0

#         # eat / move
#         if worm[HEAD]['x'] == apple['x'] and worm[HEAD]['y'] == apple['y']:
#             apple = getRandomLocation()
#             safe = False
#             while not safe:
#                 safe = True
#                 for item in poop + [gold]:
#                     if item['x'] == apple['x'] and item['y'] == apple['y']:
#                         apple = getRandomLocation(); safe = False; break
#         else:
#             del worm[-1]

#         # advance head
#         if direction == UP:    new = {'x': worm[HEAD]['x'],     'y': worm[HEAD]['y']-1}
#         if direction == DOWN:  new = {'x': worm[HEAD]['x'],     'y': worm[HEAD]['y']+1}
#         if direction == LEFT:  new = {'x': worm[HEAD]['x']-1,   'y': worm[HEAD]['y']}
#         if direction == RIGHT: new = {'x': worm[HEAD]['x']+1,   'y': worm[HEAD]['y']}
#         worm.insert(0, new)

#         # draw
#         DISPLAYSURF.fill(BGCOLOR)
#         drawGrid(); drawWorm(worm); drawApple(apple); drawgoldapple(gold)
#         for item in poop: drawPoop(item)
#         drawScore(len(worm)-3)
#         pygame.display.update()
#         FPSCLOCK.tick(FPS)

# def showGameOverScreen():
#     f = pygame.font.Font(None, 150)
#     s1 = f.render('Game', True, WHITE)
#     s2 = f.render('Over', True, WHITE)
#     r1 = s1.get_rect(midtop=(WINDOWWIDTH//2, 10))
#     r2 = s2.get_rect(midtop=(WINDOWWIDTH//2, r1.height + 35))
#     DISPLAYSURF.blit(s1, r1); DISPLAYSURF.blit(s2, r2)
#     pygame.display.update()
#     pygame.time.wait(500)
#     # wait for any key or click
#     while True:
#         e = pygame.event.wait()
#         if e.type in (KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP):
#             pygame.event.get(); return
#         if e.type == QUIT:
#             pygame.quit(); raise SystemExit

# def main():
#     try:
#         init_pygame()
#         showStartScreen()
#         while True:
#             runGame()
#             showGameOverScreen()
#     except SystemExit:
#         raise
#     except Exception as ex:
#         # make sure we see any crash reason
#         log(f"ERROR: {ex!r}")
# #         pygame.quit()
# #         raise

# if __name__ == '__main__':
#     main()

# main.py — pygame-web smoke test
import asyncio, pygame

WIDTH, HEIGHT = 1000, 800

async def main():
    pygame.display.init()
    pygame.font.init()
    # SCALED helps on web; no audio init at all
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption("pygbag smoke test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    t = 0
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False

        t += 1
        # simple animation + FPS text
        screen.fill(((t // 2) % 255, 40, 90))
        txt = font.render(f"Ticks: {t}  FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        screen.blit(txt, (20, 20))
        pygame.display.flip()
        clock.tick(60)
        # CRUCIAL on web: yield each frame
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
