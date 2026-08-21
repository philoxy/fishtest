import pygame, sys, random, math, time, datetime, json

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
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

# flags
bobberFallAnim = False #bobber falling animation at start of fishing
fishingMusic = False #music only starts once on fishing area
reelAnim = False #reeling in animation
menuMusic = False #music only starts once on title screen

#not flags
startTransitionY = 0 #transition between menu and start
startTransitionX = 100 #same thing but horizontal
sunMove = 0

area = 0
offsetX, offsetY = -169, -129

bobberSpeed = 2
bobberFall = 0
bobberReel = 0
waterOffset = 0
cloudOffset = -730
cloudOffset2 = -680
fishCount = 0
fishes = []
linePos = (150, 101)
isClicking = False
#fishesHeld = []
fishCaughtArray = []
#balance = 0
easingY = 0
easingX = 0
bobberPos = (136, 100)
hovering = False
fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + 16 + offsetY, 32, 32)
sunsetCheck = False
sunriseCheck = False

with open('save.philooxy', 'r') as f:
    lines = f.readlines()
    fishesHeld = json.loads(lines[0])
    balance = int(lines[1])
    reelTime = int(lines[2])
    maxFishes = int(lines[3])
    fishSpawnCap = int(lines[4])
    fishScaredRange = int(lines[5])
    catchTimer = int(lines[6])
    fishCount = len(fishesHeld)


#upgrade related variables
#reelTime = 60 #how long it takes for you to reel in the fishes
#maxFishes = 3 #how much fishes you can hold at a time
#fishSpawnCap = 5 #how many fishes can spawn
#fishScaredRange = 48 #how close you can get to a fish without it getting scared
#catchTimer = 70 #how long you can hold a fish before it escapes 
upgrade = False

#settings variables
volume = 1 #volume
fishSFX = False#if you want the annoying fish sound that plays every time a fish spawns
lowGraphicsMode = False

#stupid
wideMode = False

class button():
    def __init__(self, rect, newarea, image):
        global startTransitionY
        self.clicked = False
        self.image = pygame.image.load(image)
        self.rect2 = pygame.Rect(rect)
        self.newarea = newarea
        self.rect = self.rect2

    def update(self, rect):
        global isClicking, area, startTransitionY, startTransitionX, hovering

        self.image = pygame.transform.scale(self.image, (self.rect2[2], self.rect2[3]))
        if self.rect.collidepoint(pygame.mouse.get_pos()) and (startTransitionY == 100 or startTransitionY == 0) and (startTransitionX == 100 or startTransitionX == 0):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            hovering = True
            self.rect = pygame.Rect((self.rect2[0]-(self.rect2[2]*0.1), self.rect2[1]-(self.rect2[3]*0.1), self.rect2[2]*1.2, self.rect2[3]*1.2))
            self.image = pygame.transform.scale(self.image, (self.rect2[2]*1.2, self.rect2[3]*1.2))
            if pygame.mouse.get_pressed()[0] == False and isClicking == True:
                isClicking = False
            if pygame.mouse.get_pressed()[0]:
                if isClicking == False:
                    area = self.newarea
                isClicking = True
        else:
            self.rect2 = pygame.Rect(rect)
            self.rect = self.rect2
        screen.blit(self.image, self.rect)

class fishy():
    def __init__(self):
        global fishes, fishingrect, fishingrect2

        #print("You know what that means")

        self.pos = (random.randint(-200, 200), random.randint(20, 200))
        self.type = random.randint(1,5)
        if self.type == 3:
            self.type = 2
        else:
            self.type = 1
        self.dir = random.randint(1, 2)
        self.caught = False
        self.scared = 0
        self.speed = random.random()+0.5*self.type
        self.speed2 = self.speed
        self.anim = 0
        self.catchTimer = -31
        if self.type == 1:
            self.catchTime = 50
        if self.type == 2:
            self.catchTime = 25

        self.imagepath = f'assets/fish{self.type}'
        self.image = pygame.image.load(f'{self.imagepath}_0.png')
        if self.dir == 2:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1], self.rect[2], self.rect[3])

        self.rotate = random.randint(0,4)*90

        fishes.append(self)

    def update(self):
        global moving, offsetX, offsetY, fishCount, bobberFallAnim, reelAnim, fishes, fishesHeld, maxFishes, fishCaughtArray, catchTimer

        self.image = pygame.image.load(f'{self.imagepath}_{int((self.anim*self.speed/10)%2)}.png')

        self.speed = self.speed2

        self.anim += 1
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

        if self.catchTimer > -30:
            self.catchTimer -= 1


        if self.rect.colliderect(fishingrect2) and (moving == True or self.caught == True):
            self.scared = 30
        if self.scared > 0:
            self.speed = 3*self.speed2

            if self.caught == False:
                if self.pos[0] > offsetX:
                    self.dir = 1
                elif self.pos[0] < offsetX:
                    self.dir = 2

            self.scared -= 1

        if reelAnim == False:
            if -30 < self.catchTimer <= 0:
                self.caught = False

            if self.catchTimer == 0:
                #fishesHeld.remove(self.type)
                fishCaughtArray.remove(self)
                self.pos = (self.pos[0], self.pos[1]+(16+-64*random.randint(0,1)))
                if self.pos[1] < 20:
                    self.pos = (self.pos[0], 20)

        if self.dir == 2:
            self.pos = (self.pos[0]-1*self.speed, self.pos[1])
        else:
            self.pos = (self.pos[0]+1*self.speed, self.pos[1])

        if self.rect.colliderect(fishingrect) and self.caught == False and len(fishCaughtArray) < maxFishes:
            if not(-30 < self.catchTimer <= 0):
                self.caught = True
                #fishesHeld.append(self.type)
                self.catchTimer = catchTimer + self.catchTime
                fishCaughtArray.append(self)


        if self.caught == True:
            self.pos = (offsetX, offsetY+24+11)
            if offsetY <= 0 and offsetX < -20 and bobberFallAnim == False:
                #self.caught = False
                #fishes.remove(self)
                reelAnim = True

        if self.pos[0] > 320 or self.pos[0] < -320 or ((self.pos[1] > 200) and self.caught == False) or 0 < startTransitionY < 100:
            fishes.remove(self)

        self.rect[0], self.rect[1] = WIDTH/2 - 16 + self.pos[0], HEIGHT/2 - 16 + self.pos[1]

        #pygame.draw.rect(screen, (255, 0, 0), self.rect)

        screen.blit(self.image, self.rect)

#basic upgrade item
class shopItem():
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        #global isClicking
        self.image = pygame.image.load(image)
        self.imagepath = image
        self.rect2 = pygame.Rect(rect)
        self.rect = self.rect2
        self.cost = cost
        self.cost2 = cost
        self.costIncrement = costIncrement
        self.increment = increment
        self.name = name
        self.desc = desc
        self.cap = cap
        self.isClicking = False
        self.upgrade = False
        self.capCheck = True
        self.capCheck2 = True
        self.bought = 0

    def update(self, var, rect):
        global balance, hovering, startTransitionY, startTransitionX

        self.rect2 = pygame.Rect(rect)

        self.image = pygame.transform.scale(self.image, (self.rect2[2], self.rect2[3]))
        if self.rect.collidepoint(pygame.mouse.get_pos()) and (startTransitionY == 100 or startTransitionY == 0) and (startTransitionX == 100 or startTransitionX == 0) and pygame.mouse.get_focused():
            hovering = True
            self.rect = self.rect2.inflate(self.rect2[2]*0.2, self.rect2[3]*0.2)
            self.image = pygame.transform.scale(self.image, (self.rect2[2]*1.2, self.rect2[3]*1.2))

            self.upgrade = False
            if pygame.mouse.get_pressed()[0] == False and self.isClicking == True:
                self.isClicking = False
            if pygame.mouse.get_pressed()[0] and self.isClicking == False:
                if balance - self.cost >= 0:
                    #balance -= self.cost
                    self.bought += 1
                    if self.increment > 0:
                        self.capCheck = (var+self.increment < self.cap)
                    elif self.increment < 0:
                        self.capCheck = (var+self.increment > self.cap)

                    if self.capCheck:
                        self.upgrade = True
                        balance -= self.cost
                        self.cost = self.cost2 + self.costIncrement*self.bought
                    self.isClicking = True

            desc1 = ut_xs.render(self.desc, False, (0,0,0))
            desc1Rect = desc1.get_rect()
            desc1Rect.center = (self.rect2.center[0], self.rect2.center[1] + self.rect2[3]/2 + 10 + 20)
            screen.blit(desc1, desc1Rect)

            if self.capCheck:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
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
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_NO)

            cost = ut_xs.render(f'Cost: ${self.cost}', False, (0,0,0))
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

#upgrade types (i have no idea how to make this more efficient)

class hookUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global maxFishes
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(maxFishes, rect)
        if upgrade == True:
            maxFishes += self.increment
        if maxFishes > self.cap:
            maxFishes = self.cap


class spawnCapUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        #shopItem.__init__(self, name, desc, image, rect, cost, increment, cap)
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global fishSpawnCap
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(fishSpawnCap, rect)
        if upgrade == True:
            fishSpawnCap += self.increment
        if fishSpawnCap > self.cap:
            fishSpawnCap = self.cap


class reelTimeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global reelTime
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(reelTime, rect)
        if upgrade == True:
            reelTime += self.increment
        if reelTime < self.cap:
            reelTime = self.cap

class scaredRangeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global fishScaredRange
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(fishScaredRange, rect)
        if upgrade == True:
            fishScaredRange += self.increment
        if fishScaredRange < self.cap:
            fishScaredRange = self.cap

class catchTimeUpgrade(shopItem):
    def __init__(self, name, desc, image, rect, cost, costIncrement, increment, cap):
        self.shopItem = shopItem(name, desc, image, rect, cost, costIncrement, increment, cap)
        self.cap = cap

    def update(self, rect):
        global catchTimer
        self.increment = self.shopItem.increment
        upgrade = self.shopItem.update(catchTimer, rect)
        if upgrade == True:
            catchTimer += self.increment
        if catchTimer > self.cap:
            catchTimer = self.cap

#upgrades
hookupgrade = hookUpgrade("Hook upgrade", "Increase how much fish you can hold", "assets/hookupgrade.png", (WIDTH/4 - 16, HEIGHT/4, 32, 32), 50, 25, 5, 50)
spawncapupgrade = spawnCapUpgrade("Max fish upgrade", "Increase how much fish spawn at a time", "assets/maxfishupgrade.png", (2*WIDTH/4 - 16, HEIGHT/4, 32, 32), 30, 20, 1, 20)
reeltimeupgrade = reelTimeUpgrade("Reel time upgrade", "Decrease the time to reel in fish", "assets/reelupgrade.png", (3*WIDTH/4 - 16, HEIGHT/4, 32, 32), 25, 15, -10, 10)
scaredrangeupgrade = scaredRangeUpgrade("Better Lure", "Decrease the area where fish get scared", "assets/scaredrangeupgrade.png", (WIDTH/4 - 16, 2*HEIGHT/4, 32, 32), 55, 5, -8, 16)
catchtimeupgrade = catchTimeUpgrade("Hook Glue", "Increase time that fish stay on hook", "assets/catchtimeupgrade.png", (2*WIDTH/4 - 16, 2*HEIGHT/4, 32, 32), 40, 10, 10, 120)
#buttons
startbutton = button((WIDTH/2 - 50, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40), 1, "assets/fishbutton.png")
shopbutton = button((WIDTH/2 - 50, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40), 2, "assets/shopbutton.png")
#settingsbutton = button((WIDTH/2 - 50, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40), 3, "assets/settingsbutton.png")
exitbutton = button((WIDTH/2 - 50, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40), "exit", "assets/exitbutton.png")
sellbutton = button((20, HEIGHT-20, 100, 40), "sell", "assets/sellfishbutton.png")

homebutton = button((20, 20, 100, 40), 0, "assets/homebutton.png")
homebutton_up = button((20, 20, 100, 40), 0, "assets/homebutton-up.png")
homebutton_right = button((20, 20, 100, 40), 0, "assets/homebutton-right.png")

#images
#sunset/sunrise images
cloudsImage2_sunset = pygame.image.load("assets/clouds2-sunset.png")
cloudsImage_sunset = pygame.image.load("assets/clouds1-sunset.png")
fisherImage_normal_sunset = pygame.image.load("assets/fisher-sunset.png")
fisherImage_pull_sunset = pygame.image.load("assets/fisherpull.png")
dockImage_sunset = pygame.image.load("assets/dock-sunset.png")
skyColor_sunset = (4, 99, 171)
waterImage_sunset = pygame.image.load("assets/water-sunset.png")
sunImage_sunset = pygame.image.load("assets/sun-sunset-full.png")
bobberImage_sunset = pygame.image.load("assets/bobber-sunset.png")
titleImage_sunset = pygame.image.load("assets/title-sunset.png")
#normal images
cloudsImage2_noon = pygame.image.load("assets/clouds2-noon.png")
cloudsImage_noon = pygame.image.load("assets/clouds1-noon.png")
fisherImage_normal_noon = pygame.image.load("assets/fisher-noon.png")
fisherImage_pull_noon = pygame.image.load("assets/fisherpull.png")
dockImage_noon = pygame.image.load("assets/dock-noon.png")
skyColor_noon = (0, 175, 229)
waterImage_noon = pygame.image.load("assets/water-noon.png")
sunImage_noon = pygame.image.load("assets/sun-noon.png")
bobberImage_noon = pygame.image.load("assets/bobber-noon.png")
titleImage_noon = pygame.image.load("assets/title-noon.png")

cloudsImage2 = cloudsImage2_noon
cloudsImage = cloudsImage_noon
fisherImage_normal = fisherImage_normal_noon
fisherImage_pull = fisherImage_pull_noon
dockImage = dockImage_noon
skyColor = skyColor_noon
waterImage = waterImage_noon
sunImage = sunImage_noon
bobberImage = bobberImage_noon
titleImage = titleImage_noon

dockImage2 = pygame.transform.flip(dockImage, True, False)
waterImage2 = waterImage
fisherImage = fisherImage_normal

if wideMode:
    fisherImage_normal_noon = pygame.transform.scale_by(fisherImage_normal_noon, (4, 1))
    fisherImage_normal_sunset = pygame.transform.scale_by(fisherImage_normal_noon, (4, 1))
    fisherImage_pull_noon = pygame.transform.scale_by(fisherImage_normal_noon, (4, 1))
    fisherImage_pull_sunset = pygame.transform.scale_by(fisherImage_normal_noon, (4, 1))
    if lowGraphicsMode:
        fisherImage_normal = fisherImage_normal_noon
        fisherImage_pull = fisherImage_pull_noon

#sounds
ykwtm = pygame.mixer.Sound("assets/fish.mp3")

#music
mus_hotel2 = pygame.mixer.Sound("assets/hotel2.mp3")
mus_paradise = pygame.mixer.Sound("assets/paradise.mp3")
mus_menu = mus_hotel2

#functions
def checkSunset():

    global sunsetCheck, sunriseCheck, hour, minute

    """
    minute += 1
    if minute > 60:
        minute = 1
        hour += 1
    if hour > 24:
        hour = 1
    """
    now = datetime.datetime.now()

    hour = int(now.strftime("%H"))
    minute = int(now.strftime("%m"))

    sunsetCheck = 19 <= hour <= 24
    sunriseCheck = 1 <= hour <= 6

def checkSprites():
    global sunsetCheck, cloudsImage2, cloudsImage, fisherImage_normal, fisherImage_pull, fisherImage, dockImage, dockImage2, skyColor, waterImage, waterImage2, sunImage, bobberImage, titleImage

    if sunsetCheck or sunriseCheck:
        cloudsImage2 = cloudsImage2_sunset
        cloudsImage = cloudsImage_sunset
        fisherImage_normal = fisherImage_normal_sunset
        fisherImage_pull = fisherImage_pull_sunset
        dockImage = dockImage_sunset
        skyColor = skyColor_sunset
        waterImage = waterImage_sunset
        sunImage = sunImage_sunset
        bobberImage = bobberImage_sunset
        titleImage = titleImage_sunset
    else:
        cloudsImage2 = cloudsImage2_noon
        cloudsImage = cloudsImage_noon
        fisherImage_normal = fisherImage_normal_noon
        fisherImage_pull = fisherImage_pull_noon
        dockImage = dockImage_noon
        skyColor = skyColor_noon
        waterImage = waterImage_noon
        sunImage = sunImage_noon
        bobberImage = bobberImage_noon
        titleImage = titleImage_noon

    dockImage2 = pygame.transform.flip(dockImage, True, False)
    waterImage2 = waterImage
    fisherImage = fisherImage_normal
def checkMusic():
    global sunsetCheck, sunriseCheck, mus_fishing

    if sunsetCheck or sunriseCheck:
        mus_fishing = mus_hotel2
    else:
        mus_fishing = mus_paradise

checkSunset()

checkMusic()

if sunsetCheck or sunriseCheck:
    mus_menu.play(loops=-1)

def ease(t):
    return 1 - ((1 - t) ** 9)

prevMin = minute
if 1 <= hour <= 11:
    sunLerp = 1-(hour/11)+(minute/60)/11
if 12 <= hour <= 13:
    sunLerp = 0
if 14 <= hour <= 24:
    sunLerp = ((hour-13)/11)+(minute/60)/11


def drawbg():
    global cloudOffset, cloudOffset2, waterOffset, startTransitionY, skyColor, fishes, bobberPos, sunsetCheck, fishingrect, linePos, sunMove, sunsetCheck, sunriseCheck, sunLerp, prevMin, minute, hour, lowGraphicsMode, wideMode

    if lowGraphicsMode == False:
        checkSunset()

        checkMusic()

        checkSprites()

    screen.fill(skyColor)

    #sunsetMove = abs((hour-13)/12)#(minute/(60*12))
    #if sunriseCheck:

    if lowGraphicsMode == False:
        if minute != prevMin:
            if 1 <= hour <= 11:
                sunLerp -= 1/660
            if 14 <= hour <= 24:
                sunLerp += 1/660

        prevMin = minute

        if sunLerp < 0:
            sunLerp = 0
        if sunLerp > 1:
            sunLerp = 1

        sunMove = pygame.math.lerp(-250, 250, sunLerp)
    if lowGraphicsMode == True:
        sunMove = -250

    screen.blit(sunImage, (320,startTransitionY+sunMove))

    if lowGraphicsMode == False:
        screen.blit(cloudsImage2, (cloudOffset2,15+startTransitionY/4))

        cloudOffset2 += 0.25
        if cloudOffset2 > 0:
            cloudOffset2 = -680

    screen.blit(cloudsImage, (cloudOffset, -40+2*startTransitionY/5))

    cloudOffset += 0.5
    if cloudOffset > 0:
        cloudOffset = -730

    screen.blit(waterImage, (-100-70*math.sin(waterOffset),startTransitionY))

    if lowGraphicsMode == False:
        screen.blit(waterImage2, (-100+100*math.sin(waterOffset),startTransitionY*3))

    if sunsetCheck or sunriseCheck:
        waterOffset += 0.005
    else:
        waterOffset += 0.01

    #homebutton_area1.update((20, 20+startTransitionY*6, 100, 40))

    screen.blit(dockImage, (-2, startTransitionY*6-100))

    fisherImage = fisherImage_normal
    if reelAnim and not(wideMode):
        fisherImage = fisherImage_pull

    if not(wideMode):
        screen.blit(fisherImage, (0, startTransitionY*6-100))
    else:
        screen.blit(fisherImage, (-300, startTransitionY*6-100))

    for i in fishes:
        i.update()


    screen.blit(dockImage2, (WIDTH - 158, startTransitionY*6-100))

    bobberPos = (fishingrect[0], fishingrect[1]-11+startTransitionY*6)

    pygame.draw.line(screen, (0,0,0), linePos, (bobberPos[0]+15, bobberPos[1]), width=2)

    screen.blit(bobberImage, bobberPos)


def bobberMove():
    global moving, offsetX, offsetY, bobberSpeed

    pressed_keys = pygame.key.get_pressed()

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

def displayscreen(area):
    global bobberFallAnim, fishingMusic, reelAnim, menuMusic, startTransitionY, startTransitionX, offsetX, offsetY, bobberSpeed, bobberFall, bobberReel, exponent, waterOffset, fishCount, fishingrect, fishingrect2, moving, fishes, cloudOffset, cloudOffset2, xmove_temp, ymove_temp, reelTime, linePos, fishSpawnCap, fishCaughtArray, fishesHeld, balance, fisherImage, fishSFX, bobberPos, easingY, easingX, run, sunsetCheck, sunriseCheck, lowGraphicsMode, wideMode

    if area == "exit":
        run = False
        with open('save.philooxy', 'w') as f:
            lines = [f'{balance} \n', f'{reelTime} \n', f'{maxFishes} \n', f'{fishSpawnCap} \n', f'{fishScaredRange} \n', f'{catchTimer} \n',]
            f.write(f'{fishesHeld}\n')
            f.writelines(lines)

    if area == "sell":
        for i in fishesHeld:
            if i == 1:
                balance += 5
            elif i == 2:
                balance += 10
            fishesHeld.remove(i)
        area = 2

    if area == 0:

        if menuMusic == False:
            while len(fishes) > 0:
                for i in fishes:
                    fishes.remove(i)

            menuMusic = True
            if not(sunsetCheck) and not(sunriseCheck):
                pygame.mixer.stop()
                mus_menu.play(loops=-1)
            bobberFallAnim = True
            reelAnim = False
            bobberFall = 0
            bobberReel = 0
            offsetX = 0
            offsetY = 0
            fishCaughtArray = []
            fishingMusic = False
            if sunsetCheck or sunriseCheck:
                fishingMusic = True

        #startTransitionX = 100

        drawbg()

        screen.blit(titleImage, (100+700-startTransitionX*7, 50-700+startTransitionY*7))

        if lowGraphicsMode == True:
            startTransitionY = 100
            startTransitionX = 100
            linePos = (150, 101+startTransitionY*6)

        if startTransitionY < 100:
            startTransitionY = pygame.math.lerp(0, 100, ease(easingY))
            linePos = (150, 101+startTransitionY*6)
            easingY += 0.01

            if 99.7 <= startTransitionY < 100:
                startTransitionY = 100

            homebutton_up.update((20, 20+startTransitionY*6, 100, 40))

        elif startTransitionY == 100:
            offsetX, offsetY = -169, -124
            easingY = 0

        if startTransitionX < 100: 
            startTransitionX = pygame.math.lerp(0, 100, ease(easingX))
            easingX += 0.01

            if 99.7 <= startTransitionX < 100:
                startTransitionX = 100

            hookupgrade.update((WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
            spawncapupgrade.update((2*WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
            reeltimeupgrade.update((3*WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
            scaredrangeupgrade.update((WIDTH/4 - 16-startTransitionX*6, 2*HEIGHT/4, 32, 32))
            catchtimeupgrade.update((2*WIDTH/4 - 16-startTransitionX*6, 2*HEIGHT/4, 32, 32))

            homebutton_right.update((20-startTransitionX*6, 20, 100, 40))

        elif startTransitionX == 100:
            easingX = 0

        startbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
        shopbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
        #settingsbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
        exitbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))

    elif area == 1:

        menuMusic = False

        if fishingMusic == False:
            fishingMusic = True
            if not(sunsetCheck) and not(sunriseCheck):
                pygame.mixer.stop()
                mus_fishing.play(loops=-1)
                menuMusic = False
            if sunsetCheck or sunriseCheck:
                menuMusic = True

        if reelAnim == True and startTransitionY == 0.0:
            tempReelTime = reelTime*(len(fishCaughtArray))/2
            linePos = (140, 91)
            if bobberReel == 0:
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
                            fishesHeld.append(i.type)
                linePos = (150, 101)
                reelAnim = False
                bobberFallAnim = True

        moving = False
        if bobberFallAnim == True and startTransitionY == 0.0:
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


        if bobberFallAnim == False and reelAnim == False and startTransitionY == 0.0:
            bobberMove()

        fishingrect = pygame.Rect(WIDTH/2 - 16 + offsetX, HEIGHT/2 - 16 + 16 + offsetY, 32, 32)
        fishingrect2 = pygame.Rect(WIDTH/2 - fishScaredRange + offsetX, HEIGHT/2 - fishScaredRange + 16 + offsetY, 2*fishScaredRange, 2*fishScaredRange)

        drawbg()

        homebutton_up.update((20, 20+startTransitionY*6, 100, 40))

        if lowGraphicsMode == True:
            startTransitionY = 0
            linePos = (150, 101+startTransitionY*6)

        if startTransitionY > 0:

            startbutton.update((WIDTH/2 - 50, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
            shopbutton.update((WIDTH/2 - 50, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
            #settingsbutton.update((WIDTH/2 - 50, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
            exitbutton.update((WIDTH/2 - 50, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))

            linePos = (150, 101+startTransitionY*6)

            screen.blit(titleImage, (100, 50-700+startTransitionY*7))

            startTransitionY = pygame.math.lerp(100, 0, ease(easingY))

            easingY += 0.01

            if 0.3 >= startTransitionY > 0:
                startTransitionY = 0

        elif startTransitionY == 0:

            easingY = 0

            if len(fishes) < fishSpawnCap + len(fishCaughtArray):
                r = random.randint(1, 100)
                if r == 33:
                    if fishSFX == True:
                        ykwtm.play()
                    fish = fishy()

            fishCounter = ut.render(f'Fish Caught: {fishCount}', False, (0,0,0))
            fishCounterRect = fishCounter.get_rect()
            fishCounterRect.topright = (WIDTH - 20, 20)
            screen.blit(fishCounter, fishCounterRect)

            fishesHelder = ut.render(f'Fish Held: {len(fishCaughtArray)}/{maxFishes}', False, (0,0,0))
            fishesHelderRect = fishesHelder.get_rect()
            fishesHelderRect.bottomright = (WIDTH - 20, HEIGHT - 20)
            screen.blit(fishesHelder, fishesHelderRect)

    elif area == 2:

        drawbg()

        hookupgrade.update((WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
        spawncapupgrade.update((2*WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
        reeltimeupgrade.update((3*WIDTH/4 - 16-startTransitionX*6, HEIGHT/4, 32, 32))
        scaredrangeupgrade.update((WIDTH/4 - 16-startTransitionX*6, 2*HEIGHT/4, 32, 32))
        catchtimeupgrade.update((2*WIDTH/4 - 16-startTransitionX*6, 2*HEIGHT/4, 32, 32))

        homebutton_right.update((30-startTransitionX*6, 20, 100, 40))
        sellbutton.update((30-startTransitionX*6, HEIGHT - 60, 100, 40))

        fishCounter = ut.render(f'Fish: {len(fishesHeld)}', False, (0,0,0))
        fishCounterRect = fishCounter.get_rect()
        fishCounterRect.topright = (WIDTH - 20, 20)
        screen.blit(fishCounter, fishCounterRect)

        balanceCounter = ut.render(f'Balance: ${balance}', False, (0,0,0))
        balanceCounterRect = balanceCounter.get_rect()
        balanceCounterRect.topright = (WIDTH - 20, 60)
        screen.blit(balanceCounter, balanceCounterRect)
        
        if lowGraphicsMode == True:
            startTransitionX = 0

        if startTransitionX > 0:
            startbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 40 - 600 + startTransitionY*6, 100, 40))
            shopbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 90 - 600 + startTransitionY*6, 100, 40))
            #settingsbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 140 - 600 + startTransitionY * 6, 100, 40))
            exitbutton.update((WIDTH/2 - 50+600-startTransitionX*6, HEIGHT/2 + 190 - 600 + startTransitionY*6, 100, 40))

            screen.blit(titleImage, (100+700-startTransitionX*7, 50-700+startTransitionY*7))

            startTransitionX = pygame.math.lerp(100, 0, ease(easingX))
            easingX += 0.01

        if 0.3 >= startTransitionX > 0:
            startTransitionX = 0

            easingX += 0.01
        if startTransitionX == 0:
            easingX = 0
        


def update():
    pressed_keys = pygame.key.get_pressed()

    clock.tick(60)

    if pressed_keys[pygame.K_F11] or pressed_keys[pygame.K_f]:
        pygame.display.toggle_fullscreen()

    pygame.display.flip()

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill((255,255,255))

    hovering = False

    displayscreen(area)

    if hovering == False:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    update()