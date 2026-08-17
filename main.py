import pygame, sys, random, math

pygame.init()
pygame.font.init()
pygame.mixer.init()
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1) 

icon = pygame.image.load("assets/icon.png")
pygame.display.set_caption("Philooxy's Phishing")
pygame.display.set_icon(icon)
pygame.mixer.init()
clock = pygame.time.Clock()
arial = pygame.font.SysFont('arial', 20)
ut = pygame.font.Font('assets/font.ttf', 20)


# flags
FLAG1 = True #bobber falling animation at start of fishing
FLAG2 = False #music only starts once on fishing area
FLAG3 = False #reeling in animation
FLAG4 = False #music only starts once on title screen

area = 0
offsetX, offsetY = 0, 0

bobberSpeed = 2
bobberFall = 0
bobberReel = 0
fish = False
fishpos = (0,0)
fishScared = 0
fishCaught = False
waterOffset = 0
cloudOffset = -730
cloudOffset2 = -680
fishCount = 0
fishes = []
linePos = (150, 100)
isClicking = False
fishesHeld = 0

#upgrade related variables
reelTime = 70 #how long it takes for you to reel in the fishes
maxFishes = 1 #how much fishes you can hold at a time
fishSpawnCap = 3 #how many fishes can spawn

#settings variables
volume = 1 #volume
fishSFX = True#if you want the annoying fish sound that plays every time a fish spawns

class button():
    def __init__(self, rect, newarea, image):
        self.clicked = False
        self.image = pygame.image.load(image)
        self.rect2 = rect
        self.newarea = newarea

    def update(self):
        global isClicking, area
        mousepos = pygame.mouse.get_pos()
        if self.rect2[0] < mousepos[0] < (self.rect2[0] + self.rect2[2]) and self.rect2[1] < mousepos[1] < (self.rect2[1] + self.rect2[3]):
            self.rect = pygame.Rect((self.rect2[0]-(self.rect2[2]*0.1), self.rect2[1]-(self.rect2[3]*0.1), self.rect2[2]*1.2, self.rect2[3]*1.2))
            self.image = pygame.transform.scale(self.image, (self.rect2[2]*1.2, self.rect2[3]*1.2))
            if pygame.mouse.get_pressed()[0] == False and isClicking == True:
                isClicking = False
            if pygame.mouse.get_pressed()[0]:
                if isClicking == False:
                    area = self.newarea
                isClicking = True
        else:
            self.rect = pygame.Rect(self.rect2)
        screen.blit(self.image, self.rect)

class fishy():
    def __init__(self):
        global fishes, fishingrect, fishingrect2

        #print("You know what that means")

        self.pos = (random.randint(-200, 200), random.randint(20, 200))
        self.type = type
        self.dir = random.randint(1, 2)
        self.caught = False
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], 32, 32)
        self.scared = 0
        self.speed = random.random()+0.5
        self.speed2 = self.speed

        self.imagepath = f'assets/fish{random.randint(1,1)}.png'
        self.image = pygame.image.load(self.imagepath) 
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        fishes.append(self)

    def update(self):
        global moving, offsetX, offsetY, fishCount, FLAG1, FLAG3, fishes, fishesHeld

        self.speed = self.speed2

        self.image = pygame.image.load(self.imagepath)
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.pos[0] < -180:
            self.dir = 1
        elif self.pos [0] > 180:
            self.dir = 2

        if self.rect.colliderect(fishingrect2) and moving == True:
            self.scared = 30
        if self.scared > 0:
            self.speed = 3*self.speed2
            
            if self.caught == False:
                if self.pos[0] > offsetX:
                    self.dir = 1
                elif self.pos[0] < offsetX:
                    self.dir = 2

            self.scared -= 1

        if self.dir == 2:
            self.pos = (self.pos[0]-1*self.speed, self.pos[1])
        else:
            self.pos = (self.pos[0]+1*self.speed, self.pos[1])

        if self.rect.colliderect(fishingrect) and self.caught == False and fishesHeld < maxFishes:
            self.caught = True
            fishesHeld += 1

        if self.caught == True:
            self.pos = (offsetX, offsetY+24)
            if offsetY <= 0 and offsetX < -40:
                #self.caught = False
                #fishes.remove(self)
                FLAG3 = True
        
        if self.pos[0] > 320 or self.pos[0] < -320 or (self.pos[1] > 200 and self.caught == False):
            fishes.remove(self)

        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], 32, 32)

        screen.blit(self.image, self.rect)



def displayscreen(area):
    global FLAG1, FLAG2, FLAG3, FLAG4, offsetX, offsetY, bobberSpeed, bobberFall, bobberReel, exponent, fish, fishpos, fishFlip, fishScared, fishCaught, waterOffset, fishCount, fishingrect, fishingrect2, moving, fishes, cloudOffset, cloudOffset2, xmove_temp, ymove_temp, reelTime, linePos, fishesHeld, fishSpawnCap

    pressed_keys = pygame.key.get_pressed()

    if area == -1:
        sys.exit()

    elif area == 0:

        FLAG1 = True
        FLAG3 = False
        bobberFall = 0
        bobberReel = 0
        fish = False
        offsetX = 0
        offsetY = 0
        fishesHeld

        for i in fishes:
            fishes.remove(i)

        FLAG2 = False

        if FLAG4 == False:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/hotel2.mp3")
            pygame.mixer.music.play(loops=-1, fade_ms=1000)
            FLAG4 = True

        startbutton = button((WIDTH/2 - 50, HEIGHT/2 + 40, 100, 40), 1, "assets/fishbutton.png")
        startbutton.update()

        #shopbutton = button((WIDTH/2 - 50, HEIGHT/2 + 90, 100, 40), 1, "assets/fishbutton.png")
        #shopbutton.update()

        #settingsbutton = button((WIDTH/2 - 50, HEIGHT/2 + 140, 100, 40), 1, "assets/fishbutton.png")
        #settingsbutton.update()

        exitbutton = button((WIDTH/2 - 50, HEIGHT/2 + 190, 100, 40), -1, "assets/exitbutton.png")
        exitbutton.update()

        #fishingrect = pygame.Rect((WIDTH - 120, 20, 100, 40))
        #pygame.draw.rect(screen, (255, 0, 0), fishingrect)
    elif area == 1:

        FLAG4 = False

        if FLAG2 == False:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/paradise.mp3")
            pygame.mixer.music.play(loops=-1, fade_ms=1000)
            FLAG2 = True

        if FLAG3 == True:
            linePos = (140, 90)
            if bobberReel == 0:
                xmove_temp = ((WIDTH/2+offsetX)-140)/reelTime
                ymove_temp = ((HEIGHT/2+offsetY)-120)/reelTime
                bobberReel = 1
            if bobberReel < reelTime+1:
                offsetX -= xmove_temp
                offsetY -= ymove_temp
                bobberReel += 1
            if bobberReel == reelTime+1:
                FLAG3 = False
                FLAG1 = True
                bobberFall = 0
                bobberReel = 0
                for i in fishes:
                    if i.caught == True:
                        fishes.remove(i)
                        i.caught == False
                        fishCount += 1
                fishesHeld = 0
                linePos = (150, 100)

        moving = False
        if FLAG1 == True:
            moving = True
            if bobberFall < 1:
                offsetX = -100
                exponent = 10
                offsetY = -200
            if bobberFall <= 100:
                offsetX += 1
                exponent += 0.05
                offsetY = 100*math.sin(exponent)-55
                bobberFall += 1
            else:
                offsetY = 0
                FLAG1 = False


        if FLAG1 == False and FLAG3 == False:
            if pressed_keys[pygame.K_LEFT] and offsetX > -200:
                moving = True
                offsetX -= 1*bobberSpeed
            if pressed_keys[pygame.K_RIGHT] and offsetX < 200:
                moving = True
                offsetX += 1*bobberSpeed
            if pressed_keys[pygame.K_UP] and offsetY > 0:
                moving = True
                offsetY -= 1*bobberSpeed
            if pressed_keys[pygame.K_DOWN] and offsetY < 200:
                moving = True
                offsetY += 1*bobberSpeed

            if pressed_keys[pygame.K_LEFT] and pressed_keys[pygame.K_RIGHT]:
                moving = False
            if pressed_keys[pygame.K_UP] and pressed_keys[pygame.K_DOWN]:
                moving = False
        
        fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + offsetY, 32, 32)
        fishingrect2 = pygame.Rect(WIDTH/2 - 48 + offsetX, HEIGHT/2 - 48 + offsetY, 96, 96)

        #lags the game a bit
        skyImage = pygame.image.load("assets/sky.png")
        screen.blit(skyImage, (0,-230))

        #cloud offsets
        #clouds1: 730
        #clouds2: 680

        cloudsImage2 = pygame.image.load("assets/clouds2-outline.png")
        screen.blit(cloudsImage2, (cloudOffset2,25))

        cloudOffset2 += 0.5
        if cloudOffset2 > 0:
            cloudOffset2 = -680

        cloudsImage = pygame.image.load("assets/clouds1-outline.png")
        screen.blit(cloudsImage, (cloudOffset,-20))

        cloudOffset += 1
        if cloudOffset > 0:
            cloudOffset = -730

        homebutton = button((20, 20, 100, 40), 0, "assets/homebutton.png")
        homebutton.update()

        waterImage = pygame.image.load("assets/water.png")
        screen.blit(waterImage, (-100-70*math.sin(waterOffset),0))

        waterImage2 = pygame.image.load("assets/water.png")
        screen.blit(waterImage2, (-100+100*math.sin(waterOffset),0))

        waterOffset += 0.01

        #fishSpeed = 0.5

        if len(fishes) < fishSpawnCap:
            r = random.randint(1, 100)
            if r == 33:
                ykwtm = pygame.mixer.Sound("assets/fish.mp3")
                ykwtm.play()
                fish = fishy()

        for i in fishes:
            i.update()

        """
                fish = True
                fishScared = 0
                fishpos = (random.randint(-200, 200), random.randint(20, 200))
                fishRect = pygame.Rect(WIDTH/2 - 16 + fishpos[0], HEIGHT/2 - 16 + fishpos[1], 32, 32)
                if fishingrect.colliderect(fishRect):
                    fish = False
                fishFlip = random.randint(1, 2)

        else:
            fishImage = pygame.image.load("assets/icon.png")
            if fishFlip == 2:
                fishImage = pygame.transform.flip(fishImage, True, False)
            
            fishRect = pygame.Rect(WIDTH/2 - 16 + fishpos[0], HEIGHT/2 - 16 + fishpos[1], 32, 32)

            
            if fishpos[0] < -180:
                fishFlip = 1
            elif fishpos [0] > 180:
                fishFlip = 2

            if fishingrect2.colliderect(fishRect) and moving == True:
                fishScared = 30
            if fishScared > 0:
                fishSpeed = 3
                
                if fishpos[0] > offsetX:
                    fishFlip = 1
                elif fishpos[0] < offsetX:
                    fishFlip = 2

                #if fishpos[1] > offsetY and fishpos[1] > 20:
                #    print("fishup")
                #    fishpos = (fishpos[0], fishpos[1] + 1*fishSpeed)
                #elif fishpos[1] < offsetY:
                #    fishpos = (fishpos[0], fishpos[1] - 1*fishSpeed)

                fishScared -= 1

            if fishFlip == 2:
                fishpos = (fishpos[0]-1*fishSpeed, fishpos[1])
            else:
                fishpos = (fishpos[0]+1*fishSpeed, fishpos[1])

            if fishingrect.colliderect(fishRect):
                fishCaught = True

            if fishCaught == True:
                fishpos = (offsetX, offsetY+24)
                if offsetY == 0 and offsetX < -20:
                    fishCaught = False
                    fish = False
                    fishCount += 1
                    FLAG1 = True
                    bobberFall = 0
            
            if fishpos[0] > 320 or fishpos[0] < -320 or (fishpos[1] > 200 and fishCaught == False):
                fish = False

            screen.blit(fishImage, fishRect)
        """

        dockImage = pygame.image.load("assets/dock.png")
        screen.blit(dockImage, (0, -100))

        fisherImage = pygame.image.load("assets/fisher.png")
        if FLAG3 == True:
            fisherImage = pygame.image.load("assets/fisherpull.png")
        screen.blit(fisherImage, (0, -100))

        dockImage2 = pygame.image.load("assets/dock.png")
        dockImage2 = pygame.transform.flip(dockImage2, True, False)
        screen.blit(dockImage2, (WIDTH - 158, -100))

        pygame.draw.line(screen, (0,0,0), linePos, (WIDTH/2 + offsetX, HEIGHT/2 + offsetY - 16), width=2)

        #pygame.draw.rect(screen, (0,255,0), fishingrect2)
        #pygame.draw.rect(screen, (255,0,0), fishingrect)

        bobberImage = pygame.image.load("assets/bobber.png")
        screen.blit(bobberImage, fishingrect)


        fishCounter = ut.render(f'Fish Caught: {fishCount}', False, (0,0,0))
        fishCounterRect = fishCounter.get_rect()
        fishCounterRect.topright = (WIDTH - 20, 20)
        screen.blit(fishCounter, fishCounterRect)

        fishesHelder = ut.render(f'Fish Held: {fishesHeld}/{maxFishes}', False, (0,0,0))
        fishesHelderRect = fishesHelder.get_rect()
        fishesHelderRect.bottomright = (WIDTH - 20, HEIGHT - 20)
        screen.blit(fishesHelder, fishesHelderRect)
        

def update():
    global area
    pressed_keys = pygame.key.get_pressed()

    clock.tick(60)

    if pressed_keys[pygame.K_F11]:
        pygame.display.toggle_fullscreen()

    if pressed_keys[pygame.K_a]:
        print(area)

    pygame.display.flip()

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill((255,255,255)) 

    displayscreen(area)

    update()