# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *
HAS_TOUCH = hasattr(pygame, "FINGERDOWN")

FPS = 15
WINDOWWIDTH = 1000
WINDOWHEIGHT = 800
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
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

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.display.init()
    pygame.font.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font(None, 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()

audio_inited = False
def init_sound_if_possible():
    """Try to initialize audio after a user gesture. Ignore failures."""
    global audio_inited
    if audio_inited:
        return
    try:
        # This only works after a click/tap/key in the browser
        pygame.mixer.init()
        audio_inited = True
    except Exception:
        # On web, this can still fail; don’t crash the game
        pass


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()
    #DL - Dec 3 2021 -
    #AS - Dec 5 2021 -
    #Storing the first coordinates in a list
    gold = {'x': -2, 'y': -1}
    poop = [{'x': -1, 'y': -1}]
    count_g = 0
   
    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over
        
        
        
        #DL - Dec 3 2021 -
        
        #Poop/barrier code
        
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            poop.append(wormCoords[-1])
        
        #AS - Dec 5 2021 modified - 
        #Check if worm has hit barrier/poop
        #Adding a for loop to store the location of loop. 
        for item in poop:
            if wormCoords[HEAD]['x'] == item['x'] and wormCoords[HEAD]['y'] == item['y']:
                return # game over
       
        #DL For the golden apple -  Jan 19 2022 -
        
        if len(poop) >= 10 and count_g == 0:
            count_g = 1
            gold = getRandomLocation() 
        
        if wormCoords[HEAD]['x'] == gold['x'] and wormCoords[HEAD]['y'] == gold['y']:
            gold = {'x': -1, 'y': -1}
            poop = [{'x': -2, 'y': -1}] 
            count_g = 0
        
        
        
        
        
        # check if worm has eaten an apply
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation() # set a new apple somewhere
            
            #DL - Dec 3 2021
            #AS - Dec 5 2021
            #DL - Dec 6 2021
            '''
            This command ensures that the apple cannot spawn where the barrier is. It checks every location 
            of barrier and makes sure the apple does not spawn where a barrier is
            '''
            safe = False
            while safe == False:
                counter = 0
                counter_need = len(poop)
                for item in poop:
                    counter += 1
                    if item == apple:
                        apple = getRandomLocation()
                        counter = 0
                    if item == gold:
                        gold = getRandomLocation()
                        counter = 0                             
                    if counter == counter_need:
                        safe = True
                    
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        #DL - Jan 19 2022 -
        '''
        Draws the golden apple first at negative cords to not show on screen but to still exist and shall apear every 20 poop
        '''
        drawgoldapple(gold)
        #DL - Dec 3 2021 - AS Dec 4 2021
        #adding a loop to show each item in a list created to save the coordinates of the last location of newly created loop
        for item in poop:
            drawPoop(item)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
#Function to press a key 
def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Click or press any key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 260, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

#Function that containts a boolean to check for any key presses from user
def wait_for_start():
    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                terminate()

            if e.type in (KEYDOWN, KEYUP):
                if getattr(e, "key", None) == K_ESCAPE:
                    terminate()
                init_sound_if_possible()   # <-- add
                return

            if e.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, FINGERDOWN, FINGERUP):
                init_sound_if_possible()   # <-- add
                return

        pygame.time.wait(10)


def checkForKeyPress():
    """Used on Game Over screen; accept key, click, or tap."""
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            terminate()

        if e.type in (pygame.KEYDOWN, pygame.KEYUP):
            if getattr(e, "key", None) == pygame.K_ESCAPE:
                terminate()
            return e.key or True

        if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            return True

        if HAS_TOUCH and e.type in (pygame.FINGERDOWN, pygame.FINGERUP):
            return True

    return None

#Function showing the start screen and any visual details
def showStartScreen():
    titleFont  = pygame.font.Font(None, 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)
    degrees1 = degrees2 = 0

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        r1 = pygame.transform.rotate(titleSurf1, degrees1)
        r2 = pygame.transform.rotate(titleSurf2, degrees2)
        DISPLAYSURF.blit(r1, r1.get_rect(center=(WINDOWWIDTH//2,  WINDOWHEIGHT//2)))
        DISPLAYSURF.blit(r2, r2.get_rect(center=(WINDOWWIDTH//2,  WINDOWHEIGHT//2)))
        drawPressKeyMsg()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        # Wait here until we get a click or a key, then leave the start screen.
        wait_for_start()
        pygame.event.get()  # clear any leftovers
        return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame

#Function to terminate the program..
def terminate():
    try:        
        pygame.quit()
    except Exception:
        pass
    raise SystemExit
#This small function sets random location to spawn the poop or the apple
def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

#This is the game over function that appears every time the player hits any kind of barriers
def showGameOverScreen():
    gameOverFont = pygame.font.Font(None, 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf  = gameOverFont.render('Over', True, WHITE)
    gameRect  = gameSurf.get_rect()
    overRect  = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH // 2, 10)
    overRect.midtop = (WINDOWWIDTH // 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()  # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
#This function interprets the score on the right top side of the grid 
def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

#AS and DL - Dec 4 2021 -
"""This function implements the idea to add different color cells for the snake and to make each cell have a darker colored part on the 
outside and lighter color on the inside of each cell which makes it looks like a Christmas Tree"""
#Personal comment from Alikhan: Divide idea from Dejan about gradient visualization! I only thought of making the snake change color but not in such detail.
def drawWorm(wormCoords):
    '''
    DARKBLUE   =(  0,   0, 139)
    DARKPINK   =(231,  84, 128)
    DARKYELLOW =(155, 135,  12)
    DARKPURPLE =( 48,  25,  52)
    BLUE       =(  0,   0, 255)
    PINK       =(255, 192, 203)
    YELLOW     =(250, 253,  15)
    PURPLE     =(106,  13, 173)   
    '''
    colour = [DARKBLUE, DARKPINK, DARKYELLOW, DARKPURPLE, DARKGREEN]
    for coord in wormCoords:
        choice_outer= random.choice(colour)
        if choice_outer == DARKBLUE:
            choice_inner = BLUE
        elif choice_outer == DARKPINK:
            choice_inner = PINK
        elif choice_outer == DARKYELLOW:
            choice_inner = YELLOW
        elif choice_outer == DARKPURPLE:
            choice_inner = PURPLE
        elif choice_outer == DARKGREEN:
            choice_inner = GREEN
        
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, choice_outer, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, choice_inner, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


#DL - Dec 3 2021 -
def drawPoop(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    poopRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, BROWN, poopRect)
    
#DL - Jan 19 2022 -
def drawgoldapple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    goldRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, GOLD, goldRect)
    
    
def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))

'''
#LJ - Dec 5 2021 -

pygame.init()
screen = pygame.display.set_mode((128, 128))
clock = pygame.time.Clock()

counter, text = 10, '10'.rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)

while True:
    for e in pygame.event.get():
        if e.type == pygame.USEREVENT: 
            counter -= 1
            text = str(counter).rjust(3) if counter > 0 else 'boom!'
        if e.type == pygame.QUIT: break
    else:
        screen.fill((255, 255, 255))
        screen.blit(font.render(text, True, (0, 0, 0)), (32, 48))
        pygame.display.flip()
        clock.tick(60)
        continue
    break
'''

if __name__ == '__main__':
    main()
