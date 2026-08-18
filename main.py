import pygame, sys, random, math, time

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
ut_s = pygame.font.Font('assets/font.ttf', 15)
ut_xs = pygame.font.Font('assets/font.ttf', 12)


# flags
bobberFallAnim = False #bobber falling animation at start of fishing
fishingMusic = False #music only starts once on fishing area
reelAnim = False #reeling in animation
menuMusic = False #music only starts once on title screen
startTransitionY = 0 #transition between menu and start
#startTransitionY2 = 100

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
fishCaughtArray = []
balance = 0

#upgrade related variables
reelTime = 60 #how long it takes for you to reel in the fishes
maxFishes = 3 #how much fishes you can hold at a time
fishSpawnCap = 5 #how many fishes can spawn
upgrade = False

#settings variables
volume = 1 #volume
fishSFX = False#if you want the annoying fish sound that plays every time a fish spawns

class button():
    def __init__(self, rect, newarea, image):
        global startTransitionY
        self.clicked = False
        self.image = pygame.image.load(image)
        self.rect2 = rect
        self.newarea = newarea

    def update(self, rect):
        global isClicking, area, startTransitionY

        self.rect2 = rect

        self.image = pygame.transform.scale(self.image, (self.rect2[2], self.rect2[3]))
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
        self.scared = 0
        self.speed = random.random()+0.5
        self.speed2 = self.speed

        self.imagepath = f'assets/fish{random.randint(1,1)}.png'
        self.image = pygame.image.load(self.imagepath) 
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], self.rect[2], self.rect[3])

        self.rotate = random.randint(0,4)*90

        fishes.append(self)

    def update(self):
        global moving, offsetX, offsetY, fishCount, bobberFallAnim, reelAnim, fishes, fishesHeld, maxFishes, fishCaughtArray

        self.speed = self.speed2

        self.image = pygame.image.load(self.imagepath)
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.caught == True:
            self.image = pygame.transform.rotate(self.image, self.rotate)
            #self.rect = self.image.get_rect()
            #self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], self.rect[2], self.rect[3])

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
            fishesHeld += 1
            self.caught = True
            fishCaughtArray.append(self)


        if self.caught == True:
            self.pos = (offsetX, offsetY+24+11)
            if offsetY <= 0 and offsetX < -20 and bobberFallAnim == False:
                #self.caught = False
                #fishes.remove(self)
                reelAnim = True
        
        if self.pos[0] > 320 or self.pos[0] < -320 or (self.pos[1] > 200 and self.caught == False):
            fishes.remove(self)

        self.rect[0], self.rect[1] = WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1]

        #pygame.draw.rect(screen, (255, 0, 0), self.rect)

        screen.blit(self.image, self.rect)

#basic upgrade item
class shopItem():
    def __init__(self, name, desc, image, rect, cost, increment, cap):
        #global isClicking
        self.image = pygame.image.load(image)
        self.imagepath = image
        self.rect2 = pygame.Rect(rect)
        self.cost = cost
        self.increment = increment
        self.name = name
        self.desc = desc
        self.cap = cap
        self.isClicking = False
        self.upgrade = False
        self.capCheck = True
        self.capCheck2 = True

    def update(self, var):
        global balance
        
        self.image = pygame.transform.scale(self.image, (self.rect2[2], self.rect2[3]))
        mousepos = pygame.mouse.get_pos()
        if self.rect2[0] < mousepos[0] < (self.rect2[0] + self.rect2[2]) and self.rect2[1] < mousepos[1] < (self.rect2[1] + self.rect2[3]):
            self.rect = self.rect2.inflate(self.rect2[2]*0.2, self.rect2[3]*0.2)
            self.image = pygame.transform.scale(self.image, (self.rect2[2]*1.2, self.rect2[3]*1.2))
            
            self.upgrade = False
            if pygame.mouse.get_pressed()[0] == False and self.isClicking == True:
                self.isClicking = False
            if pygame.mouse.get_pressed()[0]:
                if self.isClicking == False:
                    if self.increment > 0:
                        self.capCheck = (var+self.increment < self.cap)
                    elif self.increment < 0:
                        self.capCheck = (var+self.increment > self.cap)

                    if self.capCheck:
                        self.upgrade = True
                    self.isClicking = True

            desc1 = ut_xs.render(self.desc, False, (0,0,0))
            desc1Rect = desc1.get_rect()
            desc1Rect.center = (self.rect2.center[0], self.rect2.center[1] + self.rect2[3]/2 + 10 + 20)
            screen.blit(desc1, desc1Rect)

            if self.capCheck:
                if self.increment > 0:
                    self.capCheck2 = var+self.increment > self.cap
                elif self.increment < 0:
                    self.capCheck2 = var+self.increment < self.cap

                if self.capCheck2:
                    var2 = self.cap
                else:
                    var2 = var+self.increment
                desc2Text = f'{var} -> {var2}'
            else:
                desc2Text = f'MAX ({self.cap})'

            cost = ut_xs.render(f'Cost: $0', False, (0,0,0))
            costRect = cost.get_rect()
            costRect.center = (self.rect2.center[0], self.rect2.center[1] + self.rect2[3]/2 + desc1Rect[3]/2 + 20 + 16)
            screen.blit(cost, costRect)

            desc2 = ut_xs.render(desc2Text, False, (0,0,0))
            desc2Rect = desc2.get_rect()
            desc2Rect.center = (self.rect2.center[0], self.rect2.center[1] + self.rect2[3]/2 + desc1Rect[3]/2 + 20 + 30)
            screen.blit(desc2, desc2Rect)
        else:
            self.rect = pygame.Rect(self.rect2)

        name = ut_s.render(self.name, False, (0,0,0))
        nameRect = name.get_rect()
        nameRect.center = (self.rect.center[0], self.rect.bottom + 10)
        screen.blit(name, nameRect)

        screen.blit(self.image, (self.rect[0], self.rect[1]))

        return self.upgrade

#upgrade types

class hookUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, increment, cap)
        self.cap = cap

    def update(self):
        global maxFishes
        self.increment = self.shopItem.increment
        upgrade1 = self.shopItem.update(maxFishes)
        if upgrade1 == True:
            maxFishes += self.increment
        if maxFishes > self.cap:
            maxFishes = self.cap


class spawnCapUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, increment, cap):
        #shopItem.__init__(self, name, desc, image, rect, cost, increment, cap)
        self.shopItem = shopItem(name, desc, image, rect, cost, increment, cap)
        self.cap = cap

    def update(self):
        global fishSpawnCap
        self.increment = self.shopItem.increment
        upgrade2 = self.shopItem.update(fishSpawnCap)
        if upgrade2 == True:
            fishSpawnCap += self.increment
        if fishSpawnCap > self.cap:
            fishSpawnCap = self.cap


class reelTimeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, increment, cap)
        self.cap = cap

    def update(self):
        global reelTime
        self.increment = self.shopItem.increment
        upgrade3 = self.shopItem.update(reelTime)
        if upgrade3 == True:
            reelTime += self.increment
        if reelTime < self.cap:
            reelTime = self.cap

#upgrades
hookupgrade = hookUpgrade("Hook upgrade", "Increase how much fish you can hold", "assets/hookupgrade.png", (WIDTH/4 - 16, 2*HEIGHT/3, 32, 32), 10, 5, 50)
spawncapupgrade = spawnCapUpgrade("Max fish upgrade", "Increase how much fish spawn at a time", "assets/maxfishupgrade.png", (2*WIDTH/4 - 16, 2*HEIGHT/3, 32, 32), 50, 1, 20)
reeltimeupgrade = reelTimeUpgrade("Reel time upgrade", "Decrease the time to reel in fish", "assets/reelupgrade.png", (3*WIDTH/4 - 16, 2*HEIGHT/3, 32, 32), 20, -10, 10)

#buttons
startbutton = button((WIDTH/2 - 50, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40), 1, "assets/fishbutton.png")
shopbutton = button((WIDTH/2 - 50, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40), 2, "assets/shopbutton.png")
#settingsbutton = button((WIDTH/2 - 50, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40), 3, "assets/settingsbutton.png")
exitbutton = button((WIDTH/2 - 50, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40), -1, "assets/exitbutton.png")
homebutton_area1 = button((20, 20, 100, 40), 0, "assets/homebutton.png")
homebutton_area2 = button((20, 20, 100, 40), 0, "assets/homebutton.png")

#images
cloudsImage2 = pygame.image.load("assets/clouds2-outline.png")
cloudsImage = pygame.image.load("assets/clouds1-outline.png")
waterImage = pygame.image.load("assets/water.png")
waterImage2 = pygame.image.load("assets/water.png")
dockImage = pygame.image.load("assets/dock.png")
fisherImage_normal = pygame.image.load("assets/fisher.png")
fisherImage_pull = pygame.image.load("assets/fisherpull.png")
dockImage2 = pygame.image.load("assets/dock.png")
dockImage2 = pygame.transform.flip(dockImage2, True, False)
bobberImage = pygame.image.load("assets/bobber.png")
fisherImage = fisherImage_normal
titleImage = pygame.image.load("assets/title.png")

#sounds
ykwtm = pygame.mixer.Sound("assets/fish.mp3")

#music
mus_menu = pygame.mixer.Sound("assets/hotel2.mp3")
mus_fishing = pygame.mixer.Sound("assets/paradise.mp3")

def displayscreen(area):
    global bobberFallAnim, fishingMusic, reelAnim, menuMusic, startTransitionY, offsetX, offsetY, bobberSpeed, bobberFall, bobberReel, exponent, fish, fishpos, fishFlip, fishScared, fishCaught, waterOffset, fishCount, fishingrect, fishingrect2, moving, fishes, cloudOffset, cloudOffset2, xmove_temp, ymove_temp, reelTime, linePos, fishesHeld, fishSpawnCap, fishCaughtArray, fishesHeld, balance, fisherImage, fishSFX, bobberPos

    pressed_keys = pygame.key.get_pressed()

    if area == -1:
        sys.exit()

    elif area == 0:

        bobberFallAnim = True
        reelAnim = False
        bobberFall = 0
        bobberReel = 0
        fish = False
        offsetX = 0
        offsetY = 0
        fishesHeld = 0
#        startTransitionY = 100

        for i in fishes:
            fishes.remove(i)

        fishingMusic = False

        if menuMusic == False:
            pygame.mixer.stop()
            mus_menu.play(loops=-1)
            menuMusic = True

        """
        screen.fill((0,175,229))

        screen.blit(cloudsImage2, (cloudOffset2,40))

        cloudOffset2 += 0.25
        if cloudOffset2 > 0:
            cloudOffset2 = -680

        screen.blit(cloudsImage, (cloudOffset,0))

        cloudOffset += 0.5
        if cloudOffset > 0:
            cloudOffset = -730

        screen.blit(waterImage, (-100-70*math.sin(waterOffset),50))

        screen.blit(waterImage2, (-100+100*math.sin(waterOffset),100))

        waterOffset += 0.01
        """

        screen.fill((0,175,229))

        screen.blit(cloudsImage2, (cloudOffset2,25+3*startTransitionY/20))

        cloudOffset2 += 0.25
        if cloudOffset2 > 0:
            cloudOffset2 = -680

        screen.blit(cloudsImage, (cloudOffset, -20+startTransitionY/5))

        cloudOffset += 0.5
        if cloudOffset > 0:
            cloudOffset = -730

        screen.blit(waterImage, (-100-70*math.sin(waterOffset),startTransitionY/2))

        screen.blit(waterImage2, (-100+100*math.sin(waterOffset),startTransitionY))

        waterOffset += 0.01

        screen.blit(dockImage, (0, startTransitionY*6-100))

        #screen.blit(fisherImage, (0, startTransitionY*6-100))

        screen.blit(dockImage2, (WIDTH - 158, startTransitionY*6-100))

        #screen.blit(bobberImage, (136, 100+startTransitionY*6))

        screen.blit(titleImage, (100, 50-700+startTransitionY*7))

        if startTransitionY < 100:
            startTransitionY += 1

        startbutton.update((WIDTH/2 - 50, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
        shopbutton.update((WIDTH/2 - 50, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
        #settingsbutton.update((WIDTH/2 - 50, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
        exitbutton.update((WIDTH/2 - 50, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))

    elif area == 1:

        menuMusic = False

        if fishingMusic == False:
            pygame.mixer.stop()
            mus_fishing.play(loops=-1)
            fishingMusic = True

        if reelAnim == True and startTransitionY == -1:
            tempReelTime = reelTime*(fishesHeld+0)/2
            linePos = (140, 91)
            if bobberReel == 0:
                #offsetX, offsetY = -40, 0
                xmove_temp = ((WIDTH/2+offsetX)-142)/tempReelTime
                ymove_temp = ((HEIGHT/2+offsetY)-102)/tempReelTime
                bobberReel = 1
            if bobberReel < tempReelTime+1:
                offsetX -= xmove_temp
                offsetY -= ymove_temp
                bobberReel += 1
            if bobberReel == tempReelTime+1:
                bobberFall = 0
                bobberReel = 0
                while len(fishCaughtArray) > 0:
                    for i in fishes:
                        if i.caught == True:
                            fishes.remove(i)
                            fishCaughtArray.remove(i)
                            i.caught == False
                            fishCount += 1
                            fishesHeld -= 1
                linePos = (150, 100)
                reelAnim = False
                bobberFallAnim = True

        moving = False
        if bobberFallAnim == True and startTransitionY == -1:
            moving = True
            if bobberFall < 1:
                offsetX = -169
                exponent = 10
                offsetY = -129
            if bobberFall <= 97:
                offsetX += 1
                exponent += 0.05
                offsetY = 100*math.sin(exponent)-70
                bobberFall += 1
            else:
                offsetY = 0
                bobberFallAnim = False


        if bobberFallAnim == False and reelAnim == False and startTransitionY == -1:
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
        
        fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + 16 + offsetY, 32, 32)
        fishingrect2 = pygame.Rect(WIDTH/2 - 48 + offsetX, HEIGHT/2 - 48 + 16 + offsetY, 96, 96)

        if startTransitionY > -1:

            screen.fill((0,175,229))

            screen.blit(cloudsImage2, (cloudOffset2,25+3*startTransitionY/20))

            cloudOffset2 += 0.25
            if cloudOffset2 > 0:
                cloudOffset2 = -680

            screen.blit(cloudsImage, (cloudOffset, -20+startTransitionY/5))

            cloudOffset += 0.5
            if cloudOffset > 0:
                cloudOffset = -730

            screen.blit(waterImage, (-100-70*math.sin(waterOffset),startTransitionY/2))

            screen.blit(waterImage2, (-100+100*math.sin(waterOffset),startTransitionY))

            waterOffset += 0.01

            screen.blit(dockImage, (0, startTransitionY*6-100))

            screen.blit(fisherImage, (0, startTransitionY*6-100))

            screen.blit(dockImage2, (WIDTH - 158, startTransitionY*6-100))

            screen.blit(bobberImage, (136, 100+startTransitionY*6))

            startbutton.update((WIDTH/2 - 50, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
            shopbutton.update((WIDTH/2 - 50, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
            #settingsbutton.update((WIDTH/2 - 50, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
            exitbutton.update((WIDTH/2 - 50, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))

            screen.blit(titleImage, (100, 50-700+startTransitionY*7))

            startTransitionY -= 1

        elif startTransitionY == -1:

            screen.fill((0,175,229))

            #cloud offsets
            #clouds1: 730
            #clouds2: 680

            screen.blit(cloudsImage2, (cloudOffset2,25))

            cloudOffset2 += 0.25
            if cloudOffset2 > 0:
                cloudOffset2 = -680

            screen.blit(cloudsImage, (cloudOffset,-20))

            cloudOffset += 0.5
            if cloudOffset > 0:
                cloudOffset = -730

            homebutton_area1.update((20, 20, 100, 40))

            screen.blit(waterImage, (-100-70*math.sin(waterOffset),0))

            screen.blit(waterImage2, (-100+100*math.sin(waterOffset),0))

            waterOffset += 0.01

            if len(fishes) < fishSpawnCap + fishesHeld:
                r = random.randint(1, 100)
                if r == 33:
                    if fishSFX == True:
                        ykwtm.play()
                    fish = fishy()

            for i in fishes:
                i.update()

            screen.blit(dockImage, (0, -100))

            fisherImage = fisherImage_normal
            if reelAnim == True:
                fisherImage = fisherImage_pull

            screen.blit(fisherImage, (0, -100))

            screen.blit(dockImage2, (WIDTH - 158, -100))

            pygame.draw.line(screen, (0,0,0), linePos, (WIDTH/2 + offsetX-1, HEIGHT/2 + offsetY - 11), width=2)

            #pygame.draw.rect(screen, (0,255,0), fishingrect2)
            #pygame.draw.rect(screen, (255,0,0), fishingrect)

            screen.blit(bobberImage, (fishingrect[0], fishingrect[1]-11))

            #bobberPos = (offsetX+16, offsetY-11)

        fishCounter = ut.render(f'Fish Caught: {fishCount}', False, (0,0,0))
        fishCounterRect = fishCounter.get_rect()
        fishCounterRect.topright = (WIDTH - 20, 20)
        screen.blit(fishCounter, fishCounterRect)

        fishesHelder = ut.render(f'Fish Held: {fishesHeld}/{maxFishes}', False, (0,0,0))
        fishesHelderRect = fishesHelder.get_rect()
        fishesHelderRect.bottomright = (WIDTH - 20, HEIGHT - 20)
        screen.blit(fishesHelder, fishesHelderRect)

    elif area == 2:

        hookupgrade.update()
        spawncapupgrade.update()
        reeltimeupgrade.update()

        homebutton_area1.update((20, 20, 100, 40))
        

def update():
    pressed_keys = pygame.key.get_pressed()

    clock.tick(60)

    if pressed_keys[pygame.K_F11]:
        pygame.display.toggle_fullscreen()

    pygame.display.flip()

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill((255,255,255)) 

    displayscreen(area)

    update()