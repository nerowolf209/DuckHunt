import pygame
import math

#### Completed 
# 
# , https://www.freecodecamp.org/news/create-a-arcade-style-shooting/ ####

file = open('PyGame\highScore.txt','r')
read_file = file.readlines()
file.close()


pygame.init()
#set frames per second
fps = 60
#setup for timer
timer = pygame.time.Clock()
#setup for font used
font = pygame.font.Font('freesansbold.ttf',32)
bigFont = pygame.font.Font('freesansbold.ttf',48)
#Setup for size of screen
WIDTH = 900
HEIGHT = 800
#setting up screen
screen = pygame.display.set_mode([WIDTH,HEIGHT])

#list for bag grounds
bgs = []
#list for the banners
banners = []
#list of gun colors
guns = []
#list of taget images
levelTargets = [[],[],[]]
#list for menu
menuImg = pygame.image.load(f'PyGame\\assets\menus\mainMenu.png')
gameOverImg = pygame.image.load(f'PyGame\\assets\menus\gameOver.png')
pauseMenuImg = pygame.image.load(f'PyGame\\assets\menus\pause.png')
#dictionary to determine how many targets per level
targets = { 
            1: [10,5,3],
            2: [12,8,5],
            3: [15,12,8,3]
            }
#Target values
oneCoords = [[],[],[]]
twoCoords = [[],[],[]]
threeCoords = [[],[],[],[]]
# lvl 0 is the menu's
level = 0
menu = True
pause = False
gameOver = False

#score card
points = 0
totalShot = 0
ammo = 5
timePlayed = 0
timeRemaining = 0
counter = 1

#Menu Score
bestFreePlay = 0
bestAmmoPlay = 0
bestTimed = 0

#Best scores after read file
bestFreePlay = int(read_file[0])
bestAmmoPlay = int(read_file[1])
bestTimed = int(read_file[2])

# 0 = freeplay, 1 = accuracy, 2 = timed
mode = 0
#has shot?
shot = False
#rewriting highscores
writeValue = False
#isClicked
clicked = False
#reinitialize the targets
newCoords = True

#initalize sounds in the game
pygame.mixer.init()
pygame.mixer.music.load('PyGame\\assets\sounds\\bg_music.mp3')
plateSound = pygame.mixer.Sound('PyGame\\assets\sounds\\Broken plates.wav')
plateSound.set_volume(.3)
birdSound = pygame.mixer.Sound('PyGame\\assets\sounds\\Drill Gear.mp3')
birdSound.set_volume(.3)
fartSound = pygame.mixer.Sound('PyGame\\assets\sounds\\Fart Toot.wav')
fartSound.set_volume(.3)
laserGun = pygame.mixer.Sound('PyGame\\assets\sounds\\Laser Gun.wav')
laserGun.set_volume(.4)
pygame.mixer.music.play()


#adding in the list of images being used

for i in range(1,4):
    bgs.append(pygame.image.load(f'PyGame\\assets\\bgs\{i}.png'))
    banners.append(pygame.image.load(f'PyGame\\assets\\banners\{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'PyGame\\assets\\guns\{i}.png'),(100,100)))
    if i<3:
        for count in range(1,4):
            levelTargets[i-1].append(pygame.transform.scale(pygame.image.load(f'PyGame\\assets\\targets\\{i}\{count}.png'),(120 - (count * 18), 80 - (count * 12))))
    else:
        for count in range(1,5):
            levelTargets[i-1].append(pygame.transform.scale(pygame.image.load(f'PyGame\\assets\\targets\\{i}\{count}.png'),(120 - (count * 18), 80 - (count * 12))))


def drawScore():
    pointsText = font.render(f'Points: {points}', True, 'black')
    screen.blit(pointsText,(320,660))
    shotsText = font.render(f'Total shots: {totalShot}', True, 'black')
    screen.blit(shotsText,(320,686))
    timeText = font.render(f'Time played: {timePlayed}', True, 'black')
    screen.blit(timeText,(320,713))
    if mode == 0:
        modeText =font.render(f'Freeplay!', True, 'black')
    if mode == 1:
        modeText =font.render(f'Ammo remaining: {ammo}', True, 'black')
    if mode == 2:
        modeText =font.render(f'Time remaining: {timeRemaining}', True, 'black')
    screen.blit(modeText,(320,741))
    pass

def drawGun():
    #Getting the position of the mouse
    mouse_pos = pygame.mouse.get_pos()
    #Setting the position of the gun on the screen
    gun_point = (WIDTH/2, HEIGHT - 200)
    #Creating a list for the gun colors
    lasers = ['red','purple','green']
    #creating a list to capture the mouse_press location
    clicks = pygame.mouse.get_pressed()
    # calculating the slop of the gun when tracking the mouse ( rise over run ) the if statement protects if the mouse click is directly above the gun ( as that would equal 0)
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1])/(mouse_pos[0] - gun_point[0])
    else:
        # gives us a angle straight up
        slope = -10000
    # this creates the statement in radions ( invers tan, geomatry bleh )
    angle = math.atan(slope)
    # this converts to degrees for pygame.rotate.transform requires degrees
    rotation = math.degrees(angle)
    if mouse_pos[0] < WIDTH/2:
        # setting the game to display the gun and allowing it to be mirrored ( flipped ) when moving left to right depending on angle, True indicates X position, False is Y Position
        gun = pygame.transform.flip(guns[level - 1],True,False)
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH/2 - 90, HEIGHT - 250 ))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
    else:
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun,270 - rotation), (WIDTH/2 - 30, HEIGHT - 250 ))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)

def moveLevel(coords):
    if level == 1 or level == 2:
        maxValue = 3
    else:
        maxValue = 4
    
    for i in range(maxValue):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            #this resets all the targets to the right after moving off screen to the left
            #the else statement increases the speed based on the tier of target
            if my_coords[0] < -100:
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2**(i*.75), my_coords[1])
    return coords

def drawLevel(coords):
    #sets up to prep hit boxes for the images
    if level == 1 or level == 2:
        target_rects = [[],[],[]]
    else:
        target_rects = [[],[],[],[]]
    #creating the rectangle hit box
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]),
                                                    (60 - i * 12, 60 - i * 12)))
            screen.blit(levelTargets[level - 1][i], coords[i][j])
    return target_rects

def checkShot(targets, coords):
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + 10 * (i**2)
                # TODO add sounds for enemy hit
                if level == 1:
                    birdSound.play()
                elif level == 2:
                    plateSound.play()
                else:
                    laserGun.play()


    return coords

def drawGameOver():
    global menu,clicked,level,newCoords,gameOver,run,points,timePlayed,mode,pause
    screen.blit(gameOverImg, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    if mode == 0:
        displayedScrore = timePlayed
    else:
        displayedScrore = points
    screen.blit(bigFont.render(f'{displayedScrore}',True,'black'),(630,590))
    menuButton = pygame.rect.Rect((475,660),(250,100))
    exitButton = pygame.rect.Rect((175,660),(250,100))
    if menuButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        gameOver = False
        pause = False
        menu = True
        newCoords = True
    if exitButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        run = False

def drawPause():
    global pause,menu,clicked,level,resumeLevel,newCoords
    screen.blit(pauseMenuImg, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    menuButton = pygame.rect.Rect((475,660),(250,100))
    resumeButton = pygame.rect.Rect((175,660),(250,100))
    if menuButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        menu = True
        newCoords = True
        pygame.mixer.music.play()
    if resumeButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        pause = False
        level = resumeLevel

def drawMenu():
    global gameOver,pause,mode,level,menu, timePlayed, totalShot, points, ammo, timeRemaining, bestAmmoPlay,bestFreePlay,bestTimed,writeValue,clicked,newCoords
    gameOver = False
    pause = False
    screen.blit(menuImg, (0,0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    freeplayButton = pygame.rect.Rect((175,525),(250,100))
    screen.blit(font.render(f'{bestFreePlay}',True,'black'),(340,583))
    accuracyButton = pygame.rect.Rect((475,525),(250,100))
    screen.blit(font.render(f'{bestAmmoPlay}',True,'black'),(650,583))
    timedButton = pygame.rect.Rect((175,660),(250,100))
    screen.blit(font.render(f'{bestTimed}',True,'black'),(350,713))
    resetButton = pygame.rect.Rect((475,660),(250,100))
    if freeplayButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        clicked = True
        menu = False
        newCoords = True
        timePlayed = 0
        totalShot = 0 
        points = 0
    if accuracyButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        clicked = True
        menu = False
        newCoords = True
        timePlayed = 0
        ammo = 81
        totalShot = 0 
        points = 0
    if timedButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        clicked = True
        menu = False
        newCoords = True
        timeRemaining = 30
        timePlayed = 0
        totalShot = 0 
        points = 0
    if resetButton.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        bestFreePlay = 0
        bestAmmoPlay = 0
        bestTimed = 0
        writeValue = True

# Game event
run = True

while run:
    #sets the screen frame rate
    timer.tick(fps)
    #sets the time counter
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            timePlayed += 1
            if mode == 2:
                timeRemaining -= 1
    
    if newCoords:
        #initialize target starting positions
        oneCoords = [[],[],[]]
        twoCoords = [[],[],[]]
        threeCoords = [[],[],[],[]]
        for i in range(3):
            my_list = targets[1]
            for j in range(my_list[i]):
                oneCoords[i].append((WIDTH//(my_list[i]) * j, 300- (i * 150) + 30 * (j%2)))
        for i in range(3):
            my_list = targets[2]
            for j in range(my_list[i]):
                twoCoords[i].append((WIDTH//(my_list[i]) * j, 300- (i * 150) + 30 * (j%2)))
        for i in range(4):
            my_list = targets[3]
            for j in range(my_list[i]):
                threeCoords[i].append((WIDTH//(my_list[i]) * j, 300- (i * 100) + 30 * (j%2)))
        newCoords = False


    #Sets the screen fill color
    screen.fill('black')
    #sets the background of the screen (image to load, screen position)
    screen.blit(bgs[level - 1],(0,0))
    #sets the banner on the bottom of the screen (image to load, screen positoin - 200 ( which is the image size ))
    screen.blit(banners[level - 1],(0,HEIGHT - 200))

    if menu:
        level = 0
        drawMenu()
    if gameOver:
        level = 0
        drawGameOver()
    if pause:
        level = 0
        drawPause()

    #Draws the enemies on the screen
    if level == 1:
        targetBoxes = drawLevel(oneCoords)
        oneCoords = moveLevel(oneCoords)
        if shot:
            oneCoords = checkShot(targetBoxes,oneCoords)
            shot = False
    elif level == 2:
        targetBoxes = drawLevel(twoCoords)
        twoCoords = moveLevel(twoCoords)
        if shot:
            twoCoords = checkShot(targetBoxes,twoCoords)
            shot = False
    elif level == 3:
        targetBoxes = drawLevel(threeCoords)
        threeCoords = moveLevel(threeCoords)
        if shot:
            twoCoords = checkShot(targetBoxes,threeCoords)
            shot = False

    #Draws the gun on the screen
    if level > 0:
        drawGun()
        drawScore()



    # Creates an event to exist the game (pygame.QUIT is the close button)
    for event in pygame.event.get():
        #exit game
        if event.type == pygame.QUIT:
            run = False
        #check mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mousePostition = pygame.mouse.get_pos()
            if (0 < mousePostition[0] < WIDTH) and (0 < mousePostition[1] < HEIGHT - 200):
                shot = True
                totalShot += 1
                if mode == 1:
                    ammo -= 1
            #pause
            if (670 < mousePostition[0] < 860) and (660 < mousePostition[1] < 715):
                resumeLevel = level
                pause = True
                clicked = True
            #restart
            if (670 < mousePostition[0] < 860) and (715 < mousePostition[1] < 760):
                resumeLevel = level
                menu = True
                clicked = True
                newCoords = True
                pygame.mixer.music.play()

        #check mouse up
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False
            


    if level > 0:
        if targetBoxes == [[],[],[]] and level < 3:
            level += 1
        if (level == 3 and targetBoxes == [[],[],[],[]]) or (mode == 1 and ammo == 0) or (mode == 2 and timeRemaining == 0):
            newCoords = True
            pygame.mixer.music.play()
            if mode == 0:
                if timePlayed < bestFreePlay or bestFreePlay == 0:
                    bestFreePlay = timePlayed
                    writeValue = True
            if mode == 1:
                if points > bestAmmoPlay:
                    bestAmmoPlay = points
                    writeValue = True
            if mode == 2:
                if points > bestTimed:
                    bestTimed = points
                    writeValue = True
            gameOver = True
    
    if writeValue:
        file = open('PyGame\highScore.txt','w')
        file.write(f'{bestFreePlay}\n{bestAmmoPlay}\n{bestTimed}')
        file.close()
        writeValue = False

    # tells pygame to display everything we have asked it to display. 
    pygame.display.flip()

# exits pygame
pygame.quit()

