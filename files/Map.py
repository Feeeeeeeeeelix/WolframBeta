import pygame as p
from random import randint
import sqlite3


class Map:
    def __init__(self, values):
        self.values = values

    def createPlatformTexture(self, obj):
        if obj.w >= self.values.minPlatformWidth:  # calls texture creation only for those platforms with minimum width
            platform = obj
            textureScreen = p.Surface((platform.w, self.values.originalHEIGHT), p.SRCALPHA)  # surface initialisation

            # puffer is referring to the number of platform prolongations, that are added to the main part of the platform
            pufferToDraw = 0
            while (platform.w - 4*self.values.pixelSCALE) // (24*self.values.pixelSCALE) != \
                  (platform.w - 4*self.values.pixelSCALE - (pufferToDraw * self.values.pixelSCALE)) / (24*self.values.pixelSCALE):
            # its width-4px because at least one puffer(5px) and at least one endpiece(3px) have to be on either side
            # 24 px is the minimum length of a mainpart(6px), because the pillars are 24px wide
                pufferToDraw += 1  # calculating how many puffers(5px) are to be drawn

            textureScreen.blit(self.values.platformEnd,
                               (0, (self.values.originalHEIGHT-self.values.platformHEIGHT)+self.values.pixelSCALE))  # startpiece
            textureScreen.blit(self.values.platformProlongations[randint(0, 11)],  # minimum of 1 prolongation
                               (self.values.pixelSCALE, (self.values.originalHEIGHT-self.values.platformHEIGHT)))
            drawnX = 2 * self.values.pixelSCALE#drawnX keeps track of where on the x axis we need to draw the next part

            for _ in range(pufferToDraw // 2):  # first half of puffer zone
                textureScreen.blit(self.values.platformProlongations[randint(0, 11)],
                                   (drawnX, (self.values.originalHEIGHT-44*self.values.pixelSCALE)))
                drawnX += 1 * self.values.pixelSCALE

            for _ in range((platform.w - 4*self.values.pixelSCALE) // (24*self.values.pixelSCALE)):  # mainparts
                # if platform low enough draw pillar else draw chain
                if platform.y >= self.values.originalHEIGHT - 44*self.values.pixelSCALE: # pillar
                    textureScreen.blit(self.values.platformPillar,
                                       (drawnX, (self.values.originalHEIGHT-44*self.values.pixelSCALE)+6*self.values.pixelSCALE))
                else: #chain
                    textureScreen.blit(self.values.chainStart,
                                       (drawnX + 12*self.values.pixelSCALE - 1*self.values.pixelSCALE,
                                        (self.values.originalHEIGHT-44*self.values.pixelSCALE)-2*self.values.pixelSCALE))  # chain start
                    for i in range((self.values.originalHEIGHT-44*self.values.pixelSCALE)//(2*self.values.pixelSCALE)):  # determines length of chain
                        textureScreen.blit(self.values.chains[randint(0, 11)],
                                           (drawnX + 12*self.values.pixelSCALE,
                                            (self.values.originalHEIGHT-44*self.values.pixelSCALE)-40-(i*20)))  # chains

                for _ in range(24): # creates a mainpart(6px) out of 24 mainpartparts
                    textureScreen.blit(self.values.platformMains[randint(0, 23)],
                                       (drawnX, (self.values.originalHEIGHT-44*self.values.pixelSCALE)))
                    drawnX += 1*self.values.pixelSCALE

            for _ in range(pufferToDraw - (pufferToDraw // 2)):  # 2nd half of puffer zone
                textureScreen.blit(self.values.platformProlongations[randint(0, 11)],
                                   (drawnX, (self.values.originalHEIGHT-44*self.values.pixelSCALE)))
                drawnX += 1*self.values.pixelSCALE

            textureScreen.blit(self.values.platformProlongations[randint(0, 11)],
                               (drawnX, (self.values.originalHEIGHT-44*self.values.pixelSCALE)))
            textureScreen.blit(self.values.platformEnd,
                               (drawnX + 1*self.values.pixelSCALE,
                                (self.values.originalHEIGHT-44*self.values.pixelSCALE)+1*self.values.pixelSCALE))  # end

            self.values.allPlatformTextures.append(textureScreen)

    def DrawMap(self):
        self.values.class_animationController.PlayerAnimations()  # updating slime pic
        negBoundary, posBoundary = self.GetBoundaries()
        for i in range((posBoundary - negBoundary)//self.values.originalWIDTH + 4):
            self.values.screen.blit(self.values.background2,
                                    (-negBoundary//self.values.originalWIDTH - 2 *self.values.WIDTH  # negative part + 2 just to be sure
                                     - self.values.cameraPosition * self.values.xFactor + i * self.values.WIDTH, 0)) # rest

        self.values.screen.blit(self.values.currentFrameSlimePic, self.values.charDisplayHitbox)

        if self.values.inEditMode:
            for i in range(len(self.values.allPlatforms)):
                if self.values.allPlatforms[i].w >= self.values.minPlatformWidth:
                    p.draw.rect(self.values.screen, "Blue", (
                    self.values.allPlatforms[i].x * self.values.xFactor-self.values.cameraPosition * self.values.xFactor,
                    self.values.allPlatforms[i].y*self.values.yFactor,
                    self.values.allPlatforms[i].w*self.values.xFactor,
                    self.values.allPlatforms[i].h*self.values.yFactor))
        else:
            for i in range(len(self.values.allPlatforms)):
                if self.values.allPlatforms[i].w >= self.values.minPlatformWidth:
                    self.values.screen.blit(self.values.allPlatformTextures[i],
                                            ((self.values.allPlatforms[i].x - self.values.cameraPosition) * self.values.xFactor,
                                            ((self.values.allPlatforms[i].y+self.values.platformHEIGHT-self.values.originalHEIGHT)*self.values.yFactor)))

        for i in range(len(self.values.allObstacles)):
            p.draw.rect(self.values.screen, "Red", (
                self.values.allObstacles[i].x * self.values.xFactor - self.values.cameraPosition * self.values.xFactor,
                self.values.allObstacles[i].y * self.values.yFactor,
                self.values.allObstacles[i].w * self.values.xFactor,
                self.values.allObstacles[i].h * self.values.yFactor))

        for i in range(len(self.values.allGoals)):
            p.draw.rect(self.values.screen, "Green", (
            self.values.allGoals[i].x * self.values.xFactor - self.values.cameraPosition * self.values.xFactor,
            self.values.allGoals[i].y * self.values.yFactor,
            self.values.allGoals[i].w * self.values.xFactor,
            self.values.allGoals[i].h * self.values.yFactor))

        for i in range((posBoundary - negBoundary) // self.values.originalWIDTH + 4):
            self.values.screen.blit(self.values.border,
                                    (-negBoundary // self.values.originalWIDTH - 2 * self.values.WIDTH  # negative part + 2 just to be sure
                                     - self.values.cameraPosition * self.values.xFactor + i * self.values.WIDTH, 0))  # rest

    def GetBoundaries(self):
        smallestX = 0
        biggestX = 0

        for i in range(len(self.values.allPlatforms)):
            if self.values.allPlatforms[i].x < smallestX:
                smallestX = self.values.allPlatforms[i].x
            if self.values.allPlatforms[i].x + self.values.allPlatforms[i].w > biggestX:
                biggestX = self.values.allPlatforms[i].x + self.values.allPlatforms[i].w

        return smallestX, biggestX

    def LoadMap(self, level, isTest, isCustom):
        db = self.values.db if not isCustom else self.values.dbCustom

        with sqlite3.connect(db) as conn:
            cur = conn.cursor()

            cur.execute(f"SELECT * FROM lvl{level}")
            for obj in cur:
                if not isTest:
                    if obj[4] == 0 and obj[5] == 0:
                        self.values.allPlatforms.append(p.Rect(obj[0], obj[1], obj[2], obj[3]))
                    elif obj[4] != 0:
                        self.values.allObstacles.append(p.Rect(obj[0], obj[1], obj[2], obj[3]))
                    elif obj[5] != 0:
                        self.values.allGoals.append(p.Rect(obj[0], obj[1], obj[2], obj[3]))

    def SaveMap(self, level, isNew):
        db = self.values.dbCustom

        with sqlite3.connect(db) as conn:
            cur = conn.cursor()

            if not isNew:
                cur.execute(f"DROP TABLE lvl{level}")
            cur.execute(f'CREATE TABLE lvl{level} ( X INTEGER, Y INTEGER, Width INTEGER, Height INTEGER, isDangerous INTEGER, isGoal INTEGER)')
            for obj in self.values.allPlatforms:
                cur.execute(f"INSERT INTO lvl{level}(X,Y,Width,Height,isDangerous,isGoal) VALUES({obj.x}, {obj.y}, {obj.w}, {obj.h}, 0, 0)")
            for obj in self.values.allGoals:
                cur.execute(f"INSERT INTO lvl{level}(X,Y,Width,Height,isDangerous,isGoal) VALUES({obj.x}, {obj.y}, {obj.w}, {obj.h}, 0, 1)")
            for obj in self.values.allObstacles:
                cur.execute(f"INSERT INTO lvl{level}(X,Y,Width,Height,isDangerous,isGoal) VALUES({obj.x}, {obj.y}, {obj.w}, {obj.h}, 1, 0)")



