# Source File Name: 2_0.py
# Author's Name: Paul Bialo
# Date Last Modified: August 9, 2012
# Program Description: UN Squadron - Desert Assault. Side scrolling shoot em up.
# Revision History: Version 1.0 - Basic jet control and backgrounds
#                   Version 1.1 - Setting up the timer, bomb, and cluster classes
#                   Version 1.2 - Adding the heli enemy class (with 3 patterns)
#                               - Adding some others classes (helishot, medexplosion)
#                               - Implementing collision for destruction of enemies
#                               - Adding a 'targeting' system for enemy shots
#                               - Also implemented a file reader to make spawning of enemies easier to maintain
#                   Version 1.3 - Adding the turret enemy class (sprite changes depending on position of jet)
#                               - Added the flame turret enemy class
#                               - Assigning health to enemies and changing player weapon damages
#                   Version 1.4 - Adding a scoreboard to tally score
#                               - Adding healthbar and jet health tracking
#                               - Adding the start and gameover screens
#                               - Adding sound
#                               - Adding cluster quantity check (added GUI icon as well)
#                   Version 2.0 - Final touches, corrections, adjustments.
#
import pygame, random, math
pygame.init()

screen = pygame.display.set_mode((640, 480))

# The player's avatar
class Jet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/jets/A0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (100, 240)
        self.cluster = 2
        
        # Sound effects to keep them all in one place
        self.sndWarning = pygame.mixer.Sound("sound/warning.ogg")
        self.sndBullet = pygame.mixer.Sound("sound/bullet.ogg")
        self.sndBomb = pygame.mixer.Sound("sound/bomb.ogg")
        self.sndCluster = pygame.mixer.Sound("sound/cluster.ogg")
        self.sndFlame = pygame.mixer.Sound("sound/flame.ogg")
        self.sndMedExplosion = pygame.mixer.Sound("sound/medexplosion.ogg")
        self.sndExplosion = pygame.mixer.Sound("sound/explosion.ogg")
        self.sndBonus = pygame.mixer.Sound("sound/bonus.ogg")
        
    def checkKeys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT] and self.rect.right <= 640:
            self.rect = self.rect.move(5, 0)
        if keys[pygame.K_LEFT] and self.rect.left >= 0:
            self.rect = self.rect.move(-5, 0)
        if keys[pygame.K_DOWN] and self.rect.bottom <= 380:
            self.image = pygame.image.load("img/jets/A1.gif")
            self.image = self.image.convert()
            self.rect  = self.rect.move(0, 5)
        if keys[pygame.K_UP] and self.rect.top >= 0:
            self.image = pygame.image.load("img/jets/A2.gif")
            self.image = self.image.convert()
            self.rect = self.rect.move(0, -5)

    def update(self):
        self.image = pygame.image.load("img/jets/A0.gif")
        self.image = self.image.convert()
        self.turretCoordX = self.rect.right
        self.turretCoordY = self.rect.centery + 2
        self.bombCoordX = self.rect.centerx
        self.bombCoordY = self.rect.bottom
        self.checkKeys()
        
    def getPositionX(self):
        return self.rect.centerx   

    def getPositionY(self):
        return self.rect.centery        

# A forward shooting projectile
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/weapons/bullet.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.damage = 5

    def update(self):
        self.rect.centerx += 15

# The bomb sprite which has a 3 image animation. They drop down relative to the jet
class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/weapons/bomb0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = 2
        self.dy = 6
        self.img = []

        self.loadPics()
        self.frame = 0
        self.delay = 5
        self.pause = self.delay
        self.damage = 10
        
    def loadPics(self):
        for i in range(3):
            imgName = "img/weapons/bomb%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame == 1:
                self.dx = -3
                self.dy = 10
            if self.frame > 2:
                self.frame = 2
            
            self.image = self.img[self.frame]        

        self.rect.centery += self.dy
        self.rect.centerx += self.dx  

    def getPositionX(self):
        return self.rect.centerx   

    def getPositionY(self):
        return self.rect.centery

# Sprite for the animation of an exploding bomb        
class BombExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/explosions/bomb0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.img = []

        self.loadPics()
        self.frame = 0
        self.delay = 3
        self.pause = self.delay

    def loadPics(self):
        for i in range(7):
            imgName = "img/explosions/bomb%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame > 6:
                self.frame = 6
            
            self.image = self.img[self.frame] 

        self.rect.centerx -= 4 

# An item that can be collected for bonus points        
class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, pattern):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/bonus0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.dx = -3
        self.dy = 1
        self.rect.center = (x, y)
        self.count = 0
        
        self.img = []
        self.loadPics()
        self.frame = 0
        self.delay = 2
        self.pause = self.delay
        
    def update(self):
        self.count += 1
        if self.count >= 10:
            self.count = 0
            self.dy = -self.dy
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        if self.rect.centerx <= -40:
            self.kill() 

        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay           
            self.frame += 1
            if self.frame > 1:
                self.frame = 0           
            self.image = self.img[self.frame]
        
    def loadPics(self):
        for i in range(2):
            imgName = "img/enemies/bonus%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

# A special weapon that surrounds the jet with a cluster of explosions    
class Cluster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/weapons/cluster0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.img = []

        self.loadPics()
        self.frame = 0
        self.delay = 1
        self.pause = self.delay
        
    def loadPics(self):
        for i in range(26):
            imgName = "img/weapons/cluster%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame == 25:
                self.kill()

            
            self.image = self.img[self.frame] 
            self.rect = self.image.get_rect()            
            self.rect.centerx = self.x
            self.rect.centery = self.y

# The most popular enemy 
# The pattern parameter needs to be passed to select which path the heli will take     
class Heli(pygame.sprite.Sprite):
    def __init__(self, startx, starty, pattern):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/heli0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (startx, starty)
        self.img = []
        self.pattern = pattern
        self.hp = 5
        
        if self.pattern == 1:
            self.dx = -5
            self.dy = 0
         
        if self.pattern == 2:
            self.dx = -5
            self.dy = 0
            
        if self.pattern == 3:
            self.dx = -3
            self.dy = 0
            
        self.loadPics()
        self.frame = 0
        self.delay = 4
        self.pause = self.delay
        
        self.counter = 0
        
    def loadPics(self):
        if self.pattern == 1 or self.pattern == 2:
            for i in range(2):
                imgName = "img/enemies/heli%d.gif" % i
                tmpImg = pygame.image.load(imgName)
                tmpImg.convert()
                self.img.append(tmpImg)
                
        if self.pattern == 3:       
            for i in range(6):
                imgName = "img/enemies/helib%d.gif" % i
                tmpImg = pygame.image.load(imgName)
                tmpImg.convert()
                self.img.append(tmpImg)

    def update(self):
        # Patterns 1 and 2 are very similar and follow the following rules:
        if self.counter == 70 and self.pattern == 1:
            self.dx = -4
            self.dy = 1
        if self.counter == 70 and self.pattern == 2:
            self.dx = -4
            self.dy = -1
        if self.counter == 90 and self.pattern == 1:
            self.dx = -3
            self.dy = 2
        if self.counter == 90 and self.pattern == 2:
            self.dx = -3
            self.dy = -2
        if self.counter == 100 and self.pattern == 1:
            self.dx = -2
            self.dy = 1
        if self.counter == 100 and self.pattern == 2:
            self.dx = -2
            self.dy = -1
        if self.counter == 110 and self.pattern == 1:
            self.dx = 1
            self.dy = 0
        if self.counter == 110 and self.pattern == 2:
            self.dx = 1
            self.dy = 0
        if self.counter == 120 and self.pattern == 1:
            self.dx = 2
            self.dy = 0
        if self.counter == 120 and self.pattern == 2:
            self.dx = 2
            self.dy = 0
        if self.counter == 130 and self.pattern == 1:
            self.dx = 3
            self.dy = 0
        if self.counter == 130 and self.pattern == 2:
            self.dx = 3
            self.dy = 0
        if self.counter == 160 and self.pattern == 1:
            self.dx = 2
            self.dy = -4
        if self.counter == 160 and self.pattern == 2:
            self.dx = 2
            self.dy = -4    
        
        # Pattern 3 starts with the heli on the ground before it takes off
        if self.counter == 51 and self.pattern == 3:
            self.dx = 0
            self.dy = -2
        if self.counter == 61 and self.pattern == 3:
            self.dx = 0
            self.dy = -4
        if self.counter == 101 and self.pattern == 3:
            self.dx = -5
            self.dy = -1        
        if self.counter == 121 and self.pattern == 3:
            self.dx = -7
            self.dy = 0      
        
        if self.rect.centerx <= -20 or self.rect.centery <= -20:
            self.kill()
            
        self.rect.centerx += self.dx
        self.rect.centery += self.dy
        self.counter += 1
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            
            if self.pattern == 1 or self.pattern == 2:
                if self.frame > 1:
                    self.frame = 0
           
                self.image = self.img[self.frame] 
                
            if self.pattern == 3:
                if self.counter <= 50:
                    if self.frame > 1:
                        self.frame = 0
                if self.counter >= 51 and self.counter <=100:
                    if self.frame > 3:
                        self.frame = 2
                if self.counter >= 101:
                    if self.frame > 5:
                        self.frame = 4 
 
                self.image = self.img[self.frame]                 
                
    def getPositionX(self):
        return self.rect.centerx   

    def getPositionY(self):
        return self.rect.centery                

# The heli's projectile (also used by turrets)        
class HeliShot(pygame.sprite.Sprite):
    def __init__(self, heliX, heliY, jetX, jetY):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/helishot0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()

        self.heliX = heliX
        self.heliY = heliY
        self.jetX = jetX
        self.jetY = jetY
        
        # These will story the coordinates of the shot to avoid an issue with incrementing the 
        # sprite position with a decimal value (which led to inaccurate shots)
        self.shotX = heliX
        self.shotY = heliY
        
        self.rect.center = (heliX, heliY)
        self.velocity = 6
        
        # Using our enemyProjectileVector function to 
        self.componentX, self.componentY = enemyProjectileVector(heliX, heliY, jetX, jetY)
        
        self.dx = self.velocity * self.componentX
        # To make up for the coordinate system starting in the top left
        self.dy = -1 * self.velocity * self.componentY        
                    
        self.img = []
            
        self.loadPics()
        self.frame = 0
        self.delay = 1
        self.pause = self.delay      
        
    def loadPics(self):
        for i in range(4):
            imgName = "img/enemies/helishot%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame > 3:
                self.frame = 0
           
            self.image = self.img[self.frame] 
        
        # To update the shot position, an extra step taken to make the shots more accurate:
        self.shotX += self.dx
        self.shotY += self.dy
        self.rect.centerx = self.shotX
        self.rect.centery = self.shotY
        if self.rect.centerx <= -20 or self.rect.centerx >= 700 or self.rect.centery <= -20 or self.rect.centery >= 500:
            self.kill()
            
# A turret that shoots straight up        
class FlameTurret(pygame.sprite.Sprite):
    def __init__(self, x, y, pattern):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/flameturret0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.img = []

        self.loadPics()
        self.hp = 40
        self.frame = 0
        self.counter = 0
        self.shoot = -1
        self.delay = 4
        self.pause = self.delay

    def loadPics(self):
        for i in range(3):
            imgName = "img/enemies/flameturret%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay           
            self.frame += 1
            self.counter += 1
            if self.frame > 2:
                self.frame = 2
          
        self.image = self.img[self.frame] 
        self.rect.centerx -= 3
        if self.rect.centerx <= -40:
            self.kill()
    
    def getTurretX(self):
        return self.rect.centerx
        
    def getTurretY(self):
        return self.rect.top
        
    def getPositionX(self):
        return self.rect.centerx
        
    def getPositionY(self):
        return self.rect.centery

# The projectile for the flame turret        
class FlameShot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/flameshot0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.img = []

        self.loadPics()
        self.frame = 0
        self.delay = 4
        self.pause = self.delay

    def loadPics(self):
        for i in range(15):
            imgName = "img/enemies/flameshot%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame == 14:
                self.frame = 11
          
            self.image = self.img[self.frame] 
        self.rect.centerx -= 3
        
    def getPositionX(self):
        return self.rect.centerx   

    def getPositionY(self):
        return self.rect.centery        

# A small ground based turret that tracks the jet and fires        
class SmallTurret(pygame.sprite.Sprite):
    def __init__(self, x, y, pattern):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/smallturret0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = -3
        self.img = []
        self.hp = 20

        self.loadPics()
        self.frame = 0
        self.counter = 0
        
    def loadPics(self):
        for i in range(9):
            imgName = "img/enemies/smallturret%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)
    
    def targeting(self, jetX, jetY):
        self.targetingX, self.targetingY = enemyProjectileVector(self.rect.centerx, self.rect.centery, jetX, jetY)
        self.theta = radianToDegree(math.atan2(self.targetingY, self.targetingX))
        if self.theta <= 190:
            self.frame = 0
        if self.theta <= 160:
            self.frame = 1            
        if self.theta <= 140:
            self.frame = 2   
        if self.theta <= 120:
            self.frame = 3   
        if self.theta <= 80:
            self.frame = 4
        if self.theta <= 60:
            self.frame = 5   
        if self.theta <= 40:
            self.frame = 6   
        if self.theta <= 20:
            self.frame = 7       
    
    def getTurretX(self):
        if self.frame == 0:
            return (self.rect.centerx - 28)
        if self.frame == 1:
            return (self.rect.centerx - 26)
        if self.frame == 2:
            return (self.rect.centerx - 22)
        if self.frame == 3:
            return (self.rect.centerx - 12)
        if self.frame == 4:
            return (self.rect.centerx)
        if self.frame == 5:
            return (self.rect.centerx + 12)
        if self.frame == 6:
            return (self.rect.centerx + 22)
        if self.frame == 7:
            return (self.rect.centerx + 26) 
        if self.frame == 7:
            return (self.rect.centerx + 28) 
            
    def getTurretY(self):
        if self.frame == 0:
            return (self.rect.centery - 3)
        if self.frame == 1:
            return (self.rect.centery - 15)
        if self.frame == 2:
            return (self.rect.centery - 22)
        if self.frame == 3:
            return (self.rect.centery - 27)
        if self.frame == 4:
            return (self.rect.centery - 29)
        if self.frame == 5:
            return (self.rect.centery - 27)
        if self.frame == 6:
            return (self.rect.centery - 22)
        if self.frame == 7:
            return (self.rect.centery - 15) 
        if self.frame == 8:
            return (self.rect.centery - 3) 
            
    def update(self):        
        self.counter += 1
        self.image = self.img[self.frame]        
        self.rect.centerx += self.dx  
        if self.rect.centerx <= -40:
            self.kill()
            
    def getPositionX(self):
        return self.rect.centerx   

    def getPositionY(self):
        return self.rect.centery        

# Was not used during this version of the game
class LargeTurret(pygame.sprite.Sprite):
    def __init__(self, x, y, pattern):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/enemies/largeturret0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.dx = -4
        self.img = []

        self.loadPics()
        self.frame = 0
        self.counter = 0
        
    def loadPics(self):
        for i in range(9):
            imgName = "img/enemies/largeturret%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)
    
    def targeting(self, jetX, jetY):
        self.targetingX, self.targetingY = enemyProjectileVector(self.rect.centerx, self.rect.centery, jetX, jetY)
        self.theta = radianToDegree(math.atan2(self.targetingY, self.targetingX))
        if self.theta <= 190:
            self.frame = 0
        if self.theta <= 160:
            self.frame = 1            
        if self.theta <= 140:
            self.frame = 2   
        if self.theta <= 120:
            self.frame = 3   
        if self.theta <= 80:
            self.frame = 4
        if self.theta <= 60:
            self.frame = 5   
        if self.theta <= 40:
            self.frame = 6   
        if self.theta <= 20:
            self.frame = 7       
#34, 38    1, 34  0, 27  
    def getTurretX(self):
        if self.frame == 0:
            return (self.rect.centerx - 33)
        if self.frame == 1:
            return (self.rect.centerx - 33)
        if self.frame == 2:
            return (self.rect.centerx - 22)
        if self.frame == 3:
            return (self.rect.centerx - 12)
        if self.frame == 4:
            return (self.rect.centerx)
        if self.frame == 5:
            return (self.rect.centerx + 12)
        if self.frame == 6:
            return (self.rect.centerx + 22)
        if self.frame == 7:
            return (self.rect.centerx + 26) 
        if self.frame == 7:
            return (self.rect.centerx + 28) 
            
    def getTurretY(self):
        if self.frame == 0:
            return (self.rect.centery - 4)
        if self.frame == 1:
            return (self.rect.centery - 11)
        if self.frame == 2:
            return (self.rect.centery - 22)
        if self.frame == 3:
            return (self.rect.centery - 27)
        if self.frame == 4:
            return (self.rect.centery - 29)
        if self.frame == 5:
            return (self.rect.centery - 27)
        if self.frame == 6:
            return (self.rect.centery - 22)
        if self.frame == 7:
            return (self.rect.centery - 15) 
        if self.frame == 8:
            return (self.rect.centery - 3) 
            
    def update(self):        
        self.counter += 1
        self.image = self.img[self.frame]        
        self.rect.centerx += self.dx  

    def getPositionX(self):
        return self.rect.centerx   

    def getPositionY(self):
        return self.rect.centery  
 
# The explosion animation for when some enemies are destroyed 
class MedExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/explosions/med0.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.img = []

        self.loadPics()
        self.frame = 0
        self.delay = 3
        self.pause = self.delay

    def loadPics(self):
        for i in range(8):
            imgName = "img/explosions/med%d.gif" % i
            tmpImg = pygame.image.load(imgName)
            tmpImg.convert()
            self.img.append(tmpImg)

    def update(self):
        self.pause -= 1
        if self.pause <= 0:
            self.pause = self.delay
            
            self.frame += 1
            if self.frame > 6:
                self.kill()
            
            self.image = self.img[self.frame] 

        self.rect.centerx -= 4 
 
# Part of the background during the game 
class Road(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/backgrounds/road.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.dx = 3
        self.reset()
        
    def update(self):
        self.rect.left -= self.dx
        if self.rect.right <= 640:
            self.reset() 
    
    def reset(self):
        self.rect.left = 0
        self.rect.bottom = 480

# Part of the background during the game         
class Sky(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/backgrounds/sky.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.dx = 1
        self.rect.bottom = 300
        self.reset()
                
    def update(self):
        self.rect.left -= self.dx
        if self.rect.right <= 640:
            self.reset() 
    
    def reset(self):
        self.rect.left = 0        

# Shows the player his current health        
class HealthBar(pygame.sprite.Sprite):        
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/gui/hp7.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.center = (570, 430)        
        self.health = 7
        self.count = 0
        self.invul = 0
        
    def update(self): 
        self.count += 1
        if self.invul == 0:
            if self.health == 7:
                self.image = pygame.image.load("img/gui/hp7.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
            if self.health == 6:
                self.image = pygame.image.load("img/gui/hp6.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
            if self.health == 5:
                self.image = pygame.image.load("img/gui/hp5.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
            if self.health == 4:
                self.image = pygame.image.load("img/gui/hp4.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
            if self.health == 3:
                self.image = pygame.image.load("img/gui/hp3.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
            if self.health == 2:
                self.image = pygame.image.load("img/gui/hp2.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
            if self.health == 1:
                self.image = pygame.image.load("img/gui/hp1.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
        if self.invul == 1:
                self.image = pygame.image.load("img/gui/hp8.gif")
                self.image = self.image.convert()
                self.rect = self.image.get_rect()
                self.rect.bottomright = (630, 470)    
        if self.count >= 120 and self.invul == 1:
            self.invul = 0
 
# Keeps track of clusters remaining
class ClusterGUI(pygame.sprite.Sprite):        
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/gui/cluster1.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.rect.bottomright = (450, 470)
        self.qty = 2
                
    def update(self):
        if self.qty == 0:
            self.image = pygame.image.load("img/gui/cluster0.gif")
        if self.qty == 1:
            self.image = pygame.image.load("img/gui/cluster1.gif")
        if self.qty == 2:
            self.image = pygame.image.load("img/gui/cluster2.gif")
            
# Keeps track of the player's score 
class Scoreboard(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.score = 0
        self.font = pygame.font.SysFont("None", 30)
        
    def update(self):
        self.text = "Score: %d" % (self.score)
        self.image = self.font.render(self.text, 1, (0, 0, 0))
        self.rect = self.image.get_rect()      
        
class Timer():
    def __init__(self):
        self.gameTicks = 0 
    
    def update(self):
        self.gameTicks += 1

    def returnTick(self):
        return self.gameTicks

# A simple function to determine the direction shots are made by enemies            
def enemyProjectileVector(enemyX, enemyY, jetX, jetY):
    dx = jetX - enemyX
    # Due to the pygame coordinate system starting in the top left, dy needs to be multiplied by -1
    dy = -1 * (jetY - enemyY)
    theta = math.atan2(dy, dx)
    vectorX = math.cos(theta)
    vectorY = math.sin(theta)
    return vectorX, vectorY

# Quick conversion to degrees for simplification
def radianToDegree(radians):
    degrees = 180 * radians / math.pi
    return degrees

# Image used for the start screen    
class StartScreenImage(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/gui/startscreen.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()      

# Used to show some text in between waves of enemies (getting harder)
# However, I had issues getting this to work late in the project        
class Stage1Clear (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/gui/stage1clear.gif")
        self.image = self.image.convert()
        self.rect = self.image.get_rect() 
        self.counter = 0
        
        def update(self):
            self.counter += 1
            if self.counter == 150:
                self.kill()
 
# Image used for the gameover screen 
class GameoverScreenImage(pygame.sprite.Sprite):
    def __init__(self, win):
        pygame.sprite.Sprite.__init__(self)
        self.win = win
        if self.win == False:
            self.image = pygame.image.load("img/gui/gameoverlose.gif")
            self.image = self.image.convert()
            self.rect = self.image.get_rect() 
        else:
            self.image = pygame.image.load("img/gui/gameoverwin.gif")
            self.image = self.image.convert()
            self.rect = self.image.get_rect() 
        
# The start screen function   
def startScreen():
    startScreenImage = StartScreenImage()
    pygame.display.set_caption("UN Squadron: Desert Assault")
    startScreenSprites = pygame.sprite.Group(startScreenImage)
    
    # Introduction music
    pygame.mixer.init()
    sndIntro= pygame.mixer.Sound("sound/startmusic.ogg")
    sndIntro.play(-1)
    
    keepGoing = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
                donePlaying = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                    donePlaying = True
                if event.key == pygame.K_RETURN:
                    keepGoing = False
                    startPlaying = True
                 
        startScreenSprites.draw(screen)        
        startScreenSprites.update()

        pygame.display.flip()

    sndIntro.stop()
    pygame.mouse.set_visible(True)
    return startPlaying

# The gameover screen 
def gameover(score, win):   
    pygame.display.set_caption("UN Squadron: Desert Assault")
    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    gameoverScreenImage = GameoverScreenImage(win)
    gameoverSprite = pygame.sprite.Group(gameoverScreenImage)
    
    # Gameover music
    pygame.mixer.init()
    if win == True:
        sndGameover= pygame.mixer.Sound("sound/gameoverwinmusic.ogg")
    else:
        sndGameover= pygame.mixer.Sound("sound/gameoverlosemusic.ogg")
    sndGameover.play()
    
    # Label for score that will be blitted
    gameoverFont = pygame.font.SysFont(None, 35)
    gameoverScore = "Your score: %d" % score
    gameoverLabel = gameoverFont.render(gameoverScore, 1, (255, 255, 255))
    
    keepGoing = True
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    while keepGoing:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
                donePlaying = True              
            if event.key == pygame.K_ESCAPE:
                keepGoing = False
                donePlaying = True
            if event.key == pygame.K_RETURN:
                keepGoing = False
                donePlaying = False      
                
        
        gameoverSprite.draw(screen)        
        gameoverSprite.update()
        
        screen.blit(gameoverLabel, (120, 420))

        pygame.display.flip()

    sndGameover.stop()
    pygame.mouse.set_visible(True)
    return donePlaying
    
def game():
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("UN Squadron: Desert Assault")
    
    # The game music
    pygame.mixer.init()
    sndGame= pygame.mixer.Sound("sound/gamemusic.ogg")
    sndGame.play()
        
    background = pygame.Surface(screen.get_size())
    screen.blit(background, (0, 0))
    road = Road()
    sky = Sky()
    jet = Jet()
    timer = Timer()
    clusterGUI = ClusterGUI()
    scoreboard = Scoreboard()
    healthBar = HealthBar()
        
    jetSprites = pygame.sprite.Group(jet)
    backgroundSprites = pygame.sprite.Group(sky, road)
    
    bulletSprites = pygame.sprite.Group()
    bombSprites = pygame.sprite.Group()
    clusterSprites = pygame.sprite.Group()
    heliSprites = pygame.sprite.Group()
    heliShotSprites = pygame.sprite.Group()
    smallTurretSprites = pygame.sprite.Group()
    largeTurretSprites = pygame.sprite.Group()
    flameTurretSprites = pygame.sprite.Group()
    flameShotSprites = pygame.sprite.Group()
    explosionSprites = pygame.sprite.Group()
    bonusSprites = pygame.sprite.Group()
    stageSprites = pygame.sprite.Group()
    guiSprites = pygame.sprite.Group(scoreboard, healthBar, clusterGUI)
    
    clock = pygame.time.Clock()
    
    # To load information for when enemies enter the screen: 
    enemiesFile = open( "enemies.txt" );
    enemyList = []
    for line in enemiesFile.readlines():
        enemy = [int(value) for value in line.split()] 
        enemyList.append(enemy)
    enemiesFile.close()
    
    keepGoing = True
    
    while keepGoing:
        clock.tick(30)
        pygame.mouse.set_visible(False)
        # The player's controls are detected here
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    bullet = Bullet(jet.turretCoordX, jet.turretCoordY)
                    bulletSprites.add(bullet)
                    jet.sndBullet.play()
                if event.key == pygame.K_x:
                    bomb = Bomb(jet.bombCoordX, jet.bombCoordY)
                    bombSprites.add(bomb)
                if event.key == pygame.K_c and clusterGUI.qty > 0:
                    cluster = Cluster(jet.getPositionX(), jet.getPositionY())
                    clusterSprites.add(cluster)  
                    jet.sndCluster.play()
                    clusterGUI.qty -= 1
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                    donePlaying = True
        
        for bomb in bombSprites:
            if bomb.rect.bottom >= 370:
                bombExplosion = BombExplosion(bomb.getPositionX(), bomb.getPositionY())
                explosionSprites.add(bombExplosion)
                jet.sndBomb.play()
                bomb.kill()      
        
        # Checking for collision between enemies and weapons
        # First for the helis
        for heli in heliSprites:
            for bullet in bulletSprites:
                heliCollisionCheck = pygame.sprite.collide_mask(bullet, heli)
                if heliCollisionCheck:
                    heli.hp -= bullet.damage
                    bullet.kill()
                    if heli.hp <= 0:
                        medExplosion = MedExplosion(heli.getPositionX(), heli.getPositionY())
                        explosionSprites.add(medExplosion)
                        jet.sndBomb.play()
                        bullet.kill()
                        scoreboard.score += 50
                        heli.kill()
                        jet.sndExplosion.play()
            for bomb in bombSprites:
                heliCollisionCheck = pygame.sprite.collide_mask(bomb, heli)
                if heliCollisionCheck:
                    heli.hp -= bomb.damage
                    bombExplosion = BombExplosion(bomb.getPositionX(), bomb.getPositionY())
                    explosionSprites.add(bombExplosion)      
                    jet.sndBomb.play()
                    bomb.kill()
                    if heli.hp <= 0:
                        medExplosion = MedExplosion(heli.getPositionX(), heli.getPositionY())
                        explosionSprites.add(medExplosion)
                        scoreboard.score += 50
                        heli.kill()
                        jet.sndExplosion.play()
            for cluster in clusterSprites:
                heliCollisionCheck = pygame.sprite.collide_mask(cluster, heli)
                if heliCollisionCheck:
                    medExplosion = MedExplosion(heli.getPositionX(), heli.getPositionY())
                    explosionSprites.add(medExplosion)
                    scoreboard.score += 50
                    heli.kill()
                    jet.sndExplosion.play()
        
        # Then for the small turret
        for smallTurret in smallTurretSprites:
            for bullet in bulletSprites:
                smallTurretCollisionCheck = pygame.sprite.collide_mask(bullet, smallTurret)
                if smallTurretCollisionCheck:
                    smallTurret.hp -= bullet.damage
                    bullet.kill()
                    if smallTurret.hp <= 0:
                        medExplosion = MedExplosion(smallTurret.getPositionX(), smallTurret.getPositionY())
                        explosionSprites.add(medExplosion)
                        bullet.kill()
                        scoreboard.score += 100
                        smallTurret.kill()
                        jet.sndMedExplosion.play()
            for bomb in bombSprites:
                smallTurretCollisionCheck = pygame.sprite.collide_mask(bomb, smallTurret)
                if smallTurretCollisionCheck:
                    smallTurret.hp -= bomb.damage
                    bombExplosion = BombExplosion(bomb.getPositionX(), bomb.getPositionY())
                    explosionSprites.add(bombExplosion) 
                    jet.sndBomb.play()
                    bomb.kill()
                    if smallTurret.hp <= 0:
                        medExplosion = MedExplosion(smallTurret.getPositionX(), smallTurret.getPositionY())
                        explosionSprites.add(medExplosion)
                        scoreboard.score += 100
                        smallTurret.kill()
                        jet.sndMedExplosion.play()
            for cluster in clusterSprites:
                smallTurretCollisionCheck = pygame.sprite.collide_mask(cluster, smallTurret)
                if smallTurretCollisionCheck:
                    medExplosion = MedExplosion(smallTurret.getPositionX(), smallTurret.getPositionY())
                    explosionSprites.add(medExplosion)
                    scoreboard.score += 100
                    smallTurret.kill()
                    jet.sndMedExplosion.play()
         
        # Collisions for the flame turret
        for flameTurret in flameTurretSprites:
            for bullet in bulletSprites:
                flameTurretCollisionCheck = pygame.sprite.collide_mask(bullet, flameTurret)
                if flameTurretCollisionCheck:
                    flameTurret.hp -= bullet.damage
                    bullet.kill()
                    if flameTurret.hp <= 0:
                        medExplosion = MedExplosion(flameTurret.getPositionX(), flameTurret.getPositionY())
                        explosionSprites.add(medExplosion)
                        bullet.kill()
                        scoreboard.score += 200
                        flameTurret.kill()
                        jet.sndFlame.stop()
                        jet.sndMedExplosion.play()
                        for flameShot in flameShotSprites:
                            flameShot.kill()
            for bomb in bombSprites:
                smallTurretCollisionCheck = pygame.sprite.collide_mask(bomb, flameTurret)
                if smallTurretCollisionCheck:
                    flameTurret.hp -= bomb.damage
                    bombExplosion = BombExplosion(flameTurret.getPositionX(), flameTurret.getPositionY())
                    explosionSprites.add(bombExplosion)
                    jet.sndBomb.play()
                    bomb.kill()
                    if flameTurret.hp <= 0:
                        medExplosion = MedExplosion(flameTurret.getPositionX(), flameTurret.getPositionY())
                        explosionSprites.add(medExplosion)
                        scoreboard.score += 200
                        flameTurret.kill()
                        jet.sndMedExplosion.play()
            for cluster in clusterSprites:
                smallTurretCollisionCheck = pygame.sprite.collide_mask(cluster, flameTurret)
                if smallTurretCollisionCheck:
                    medExplosion = MedExplosion(flameTurret.getPositionX(), flameTurret.getPositionY())
                    explosionSprites.add(medExplosion)
                    scoreboard.score += 200
                    flameTurret.kill()
                    jet.sndMedExplosion.play()
                    
        # Collisions with the cluster weapon with helishots (defensive bonus)            
        for cluster in clusterSprites:
            for heliShot in heliShotSprites:
                heliClusterCollisionCheck = pygame.sprite.collide_mask(cluster, heliShot)
                if heliClusterCollisionCheck:
                    heliShot.kill()
        
        # If player picks up a bonus
        for bonus in bonusSprites:
            bonusJetCollisionCheck = pygame.sprite.collide_mask(jet, bonus)
            if bonusJetCollisionCheck:
                bonus.kill()
                jet.sndBonus.play()
                scoreboard.score += 1000
        
        # Adding conditions for when the enemies fire
        for heli in heliSprites:
            for n in range(10):
                if heli.counter == 40 * n:
                    heliShot = HeliShot(heli.rect.centerx, heli.rect.centery, jet.getPositionX(), jet.getPositionY())
                    heliShotSprites.add(heliShot)
        
        for smallTurret in smallTurretSprites:
            smallTurret.targeting(jet.getPositionX(), jet.getPositionY())
            for n in range(10):
                if smallTurret.counter == 50 * n:
                    heliShot = HeliShot(smallTurret.getTurretX(), smallTurret.getTurretY(), jet.getPositionX(), jet.getPositionY())
                    heliShotSprites.add(heliShot)

        for largeTurret in largeTurretSprites:
            largeTurret.targeting(jet.getPositionX(), jet.getPositionY())
            for n in range(10):
                if largeTurret.counter == 50 * n:
                    heliShot = HeliShot(largeTurret.getTurretX(), largeTurret.getTurretY(), jet.getPositionX(), jet.getPositionY())
                    heliShotSprites.add(heliShot)
                    
        for flameTurret in flameTurretSprites:
            if flameTurret.counter == 2:
                flameShot = FlameShot(flameTurret.getTurretX(), flameTurret.getTurretY())
                flameShotSprites.add(flameShot)
                jet.sndFlame.play()
                
        # Checking for collisions with the player jet
        for heliShot in heliShotSprites:
            heliShotJetCollisionCheck = pygame.sprite.collide_mask(heliShot, jet)
            if heliShotJetCollisionCheck and healthBar.invul == 0:
                healthBar.invul = 1
                healthBar.health -= 1
                healthBar.count = 0
                jet.sndWarning.play()
        for flameShot in flameShotSprites:
            flameShotJetCollisionCheck = pygame.sprite.collide_mask(flameShot, jet)
            if flameShotJetCollisionCheck and healthBar.invul == 0:
                healthBar.invul = 1
                healthBar.health -= 1
                healthBar.count = 0
                jet.sndWarning.play()
        for heli in heliSprites:
            heliJetCollisionCheck = pygame.sprite.collide_mask(heli, jet)
            if heliJetCollisionCheck and healthBar.invul == 0:
                healthBar.invul = 1
                healthBar.health -= 1
                healthBar.count = 0     
                jet.sndWarning.play()
        for smallTurret in smallTurretSprites:
            smallTurretJetCollisionCheck = pygame.sprite.collide_mask(smallTurret, jet)
            if smallTurretJetCollisionCheck and healthBar.invul == 0:
                healthBar.invul = 1
                healthBar.health -= 1
                healthBar.count = 0 
                jet.sndWarning.play()
        for flameTurret in flameTurretSprites:
            flameTurretJetCollisionCheck = pygame.sprite.collide_mask(flameTurret, jet)
            if flameTurretJetCollisionCheck and healthBar.invul == 0:
                healthBar.invul = 1
                healthBar.health -= 1
                healthBar.count = 0 
                jet.sndWarning.play()
        
        # Player loses
        if healthBar.health <= 0:
            gameOver = True
            keepGoing = False
            win = False
            
        # Checking to see if an enemy needs to be added this tick
        for enemy in enemyList:
            if enemy[0] == timer.returnTick():
                if enemy[1] == 1:
                    heli = Heli(enemy[2], enemy[3], enemy[4])
                    heliSprites.add(heli)
                if enemy[1] == 2:
                    smallTurret = SmallTurret(enemy[2], enemy[3], enemy[4])
                    smallTurretSprites.add(smallTurret)
                if enemy[1] == 3:
                    largeTurret = LargeTurret(enemy[2], enemy[3], enemy[4])
                    largeTurretSprites.add(largeTurret)         
                if enemy[1] == 4:
                    flameTurret = FlameTurret(enemy[2], enemy[3], enemy[4])
                    flameTurretSprites.add(flameTurret)      
                if enemy[1] == 5:
                    bonus = Bonus(enemy[2], enemy[3], enemy[4])
                    bonusSprites.add(bonus)     
                    
        # Small breaks between stages, 1 cluster is restocked to a max of 2
        # The stage clear did not work. Will try to fix and improve on for 1B.
        if timer.returnTick() == 1100:
            clusterGUI.qty += 1
            if clusterGUI.qty > 2:
                clusterGUI.qty = 2
            stage1Clear = Stage1Clear()
            guiSprites.add(stage1Clear)

        if timer.returnTick() == 2400:
            clusterGUI.qty += 1
            if clusterGUI.qty > 2:
                clusterGUI.qty = 2
            stage1Clear = Stage1Clear()
            guiSprites.add(stage1Clear)
            
        if timer.returnTick() == 3600:
            scoreboard.score += (1000 * healthBar.health) # Bonus for winning
            gameOver = True
            keepGoing = False
            win = True    
            
        # Updating the sprites
      
        backgroundSprites.update()
        backgroundSprites.draw(screen)
        
        bulletSprites.update()
        bulletSprites.draw(screen)

        bombSprites.update()
        bombSprites.draw(screen)

        clusterSprites.update()
        clusterSprites.draw(screen)        
        
        explosionSprites.update()
        explosionSprites.draw(screen)
        
        heliSprites.update()
        heliSprites.draw(screen)
        
        heliShotSprites.update()
        heliShotSprites.draw(screen)
        
        smallTurretSprites.update()
        smallTurretSprites.draw(screen)
        
        largeTurretSprites.update()
        largeTurretSprites.draw(screen)
        
        flameTurretSprites.update()
        flameTurretSprites.draw(screen)
        
        flameShotSprites.update()
        flameShotSprites.draw(screen)
        
        bonusSprites.update()
        bonusSprites.draw(screen)
        
        jetSprites.update()
        jetSprites.draw(screen)

        guiSprites.update()
        guiSprites.draw(screen)
        
        timer.update()
        print (timer.returnTick())
        print (jet.getPositionX())
        print (clock.get_fps())
        pygame.display.flip()
           
    #return mouse cursor
    pygame.mouse.set_visible(True) 
    
    sndGame.stop()
    pygame.mouse.set_visible(True) 
    return scoreboard.score, gameOver, win
    
def main():
    donePlaying = False
    score = 0
    if startScreen() == True:
        while not donePlaying:
            score, gameOver, win = game()
            if gameOver:
                donePlaying = gameover(score, win)    

if __name__ == "__main__":
    main()
    
