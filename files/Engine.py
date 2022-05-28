import pygame as p


class Physics:

    def __init__(self, values):
        self.values = values

        self.getTicksLastFrame = 0

    def Right(self):
        if self.values.xVelocity < self.values.runSpeed and self.values.xAcceleration < self.values.runAcceleration:
            self.values.xAcceleration = self.values.runAcceleration

    def Left(self):
        if self.values.xVelocity > -self.values.runSpeed and self.values.xAcceleration > -self.values.runAcceleration:
            self.values.xAcceleration = -self.values.runAcceleration

    def Jump(self):
        if self.values.isGrounded:
            self.values.yVelocity -= self.values.jumpBoost

    def Dash(self):
        if self.values.dashCooldown <= 0 and not self.values.inEditMode:
            if self.values.pressedRight:
                self.values.xPosition += self.values.dashDistance
                self.values.dashCooldown = self.values.dashCooldownValue
                self.values.isDashFrame = True
            elif self.values.pressedLeft:
                self.values.xPosition -= self.values.dashDistance
                self.values.dashCooldown = self.values.dashCooldownValue
                self.values.isDashFrame = True

    def Gravity(self):
        if not self.values.isFinished and not self.values.isDead:
            self.values.yAcceleration += self.values.gravitationalAcceleration

    def Braking(self):
        if -self.values.idleThreshhold * self.values.dTime <= self.values.xVelocity <= self.values.idleThreshhold * self.values.dTime:
            self.values.xVelocity = 0
        elif self.values.xVelocity > self.values.runSpeed and self.values.isGrounded:  # ground drag
            self.values.xAcceleration -= self.values.groundDrag
        elif self.values.xVelocity < -self.values.runSpeed and self.values.isGrounded: 
            self.values.xAcceleration += self.values.groundDrag
        elif self.values.xVelocity > self.values.runSpeed and not self.values.isGrounded:  # air drag
            self.values.xAcceleration -= self.values.airDrag
        elif self.values.xVelocity < -self.values.runSpeed and not self.values.isGrounded:
            self.values.xAcceleration += self.values.airDrag
        elif self.values.xVelocity > 0 and not self.values.pressedRight:
            self.values.xAcceleration -= self.values.groundDrag * self.values.xVelocity/100
        elif self.values.xVelocity < 0 and not self.values.pressedLeft:
            self.values.xAcceleration += self.values.groundDrag * -self.values.xVelocity/100

    def PositionUpdate(self):   # update pos, vel, acc
        self.values.isIdle = True
        self.values.isDashFrame = False
        self.values.dashCooldown -= 1 * self.values.dTime

        if self.values.pressedRight and self.values.pressedLeft:  # cancelling adversary movement
            pass

        elif self.values.pressedRight:  # calling right function if bound key is pressed
            self.Right()
            self.values.isIdle = False

        elif self.values.pressedLeft:  # calling left function if bound key is pressed
            self.Left()
            self.values.isIdle = False

        if self.values.pressedDash:  # calling dash function if bound key is pressed
            self.Dash()

        if self.values.pressedJump:  # calling jump function if bound key is pressed
            self.Jump()
            self.values.isGrounded = False

        self.Gravity()
        self.Braking()

        self.values.xVelocity += self.values.xAcceleration * self.values.dTime
        self.values.yVelocity += self.values.yAcceleration * self.values.dTime
        self.values.xPosition += self.values.xVelocity * self.values.dTime
        self.values.yPosition += self.values.yVelocity * self.values.dTime
        self.values.xAcceleration = 0
        self.values.yAcceleration = 0

        self.CharHitbox()
        self.Death()
        self.Win()

    def CharHitbox(self):
        self.values.charDisplayHitbox = p.Rect(
               (self.values.xPosition - self.values.cameraPosition - (self.values.charWidth / 2)) * self.values.xFactor,
               (self.values.yPosition - (self.values.charHeight / 2)) * self.values.yFactor,
               self.values.charWidth * self.values.xFactor, self.values.charHeight * self.values.yFactor)

        self.values.charHitbox = p.Rect(self.values.xPosition - 50, self.values.yPosition - 50,
                                        self.values.charWidth, self.values.charHeight)

    def Death(self):
        if not self.values.inEditMode:
            if self.values.yPosition >= 1200:
                self.values.isDead = True
            for i in range(len(self.values.allObstacles)):
                if self.values.allObstacles[i].colliderect(self.values.charHitbox):
                    self.values.isDead = True
                    self.values.xVelocity, self.values.yVelocity = 0, 0

    def Win(self):
        if not self.values.inEditMode and not self.values.isDead:
            for i in range(len(self.values.allGoals)):
                if self.values.allGoals[i].colliderect(self.values.charHitbox):
                    self.values.isFinished = True
                    self.values.xVelocity, self.values.yVelocity = 0, 0

    def DeltaTime(self):
        t = p.time.get_ticks()  #gets time since start of program
        self.values.dTime = (t - self.getTicksLastFrame) / 1000.0  #gets time since last frame in ms
        self.getTicksLastFrame = t

        if self.values.dTime > .3 or self.values.inSettings:   #process suspended or huuuuuuge lags or editing settings = no movement
            self.values.dTime = 0

    def ResetEngine(self):
        self.values.allPlatforms = []
        self.values.allObstacles = []
        self.values.allGoals = []
        self.values.xPosition = 0
        self.values.yPosition = - 50
        self.values.xVelocity = 0
        self.values.yVelocity = 0
        self.values.isDead = False
        self.values.isFinished = False
        self.values.allPlatformTextures = []


class Collisions:
    def __init__(self, values):
        self.values = values
        self.xPositionLf = self.yPositionLf = 0

    def CharCollision(self):

        hitboxTop = self.values.yPosition - self.values.charHeight / 2
        hitboxBottom = self.values.yPosition + self.values.charHeight / 2
        hitboxLeft = self.values.xPosition - self.values.charWidth / 2
        hitboxRight = self.values.xPosition + self.values.charWidth / 2

        hitboxTopLf = self.yPositionLf - self.values.charHeight / 2
        hitboxBottomLf = self.yPositionLf + self.values.charHeight / 2
        hitboxLeftLf = self.xPositionLf - self.values.charWidth / 2
        hitboxRightLf = self.xPositionLf + self.values.charWidth / 2

        self.values.isGrounded = False

        for obj in self.values.allPlatforms:
            objTop, objLeft, objBottom, objRight = obj.y, obj.x, obj.y + obj.h, obj.x + obj.w

            topCollision = hitboxTop - objBottom
            bottomCollision = objTop - hitboxBottom
            leftCollision = hitboxLeft - objRight
            rightCollision = objLeft - hitboxRight

            topCollisionLf = hitboxTopLf - objBottom
            leftCollisionLf = hitboxLeftLf - objRight
            bottomCollisionLf = objTop - hitboxBottomLf
            rightCollisionLf = objLeft - hitboxRightLf

            if topCollision <= 0 and objLeft < hitboxRight < objRight + self.values.charWidth and topCollisionLf >= 0 and self.values.yVelocity < 0:
                self.values.yPosition = objBottom + self.values.charHeight / 2
                self.values.yVelocity = -self.values.slimeBounciness * self.values.yVelocity if self.values.pressedJump else 0
            if leftCollision <= 0 and objBottom > hitboxTop > objTop - self.values.charHeight and leftCollisionLf >= 0 and self.values.xVelocity < 0:
                self.values.xPosition = objRight + self.values.charWidth / 2
                if self.values.pressedJump and self.values.isDashFrame:
                    self.values.xVelocity = -self.values.slimeBounciness * self.values.xVelocity + self.values.dashBounceVel
                elif self.values.pressedJump:
                    self.values.xVelocity = -self.values.slimeBounciness * self.values.xVelocity
                else:
                    self.values.xVelocity = 0
            if bottomCollision <= 0 and objLeft < hitboxRight < objRight + self.values.charWidth and bottomCollisionLf >= 0 and self.values.yVelocity > 0: # and objLeft < hitboxRightLf < objRight + self.values.charWidth
                self.values.yPosition = objTop - self.values.charHeight / 2
                self.values.yVelocity = -self.values.slimeBounciness * self.values.yVelocity if self.values.pressedJump else 0
                self.values.isGrounded = False if self.values.pressedJump else True
            if rightCollision < 0 and objBottom >= hitboxTop > objTop - self.values.charHeight and rightCollisionLf >= 0and self.values.xVelocity > 0: # and objBottom > hitboxTopLf > objTop - self.values.charHeight
                self.values.xPosition = objLeft - self.values.charWidth / 2
                if self.values.pressedJump and self.values.isDashFrame:
                    self.values.xVelocity = -self.values.slimeBounciness * self.values.xVelocity - self.values.dashBounceVel
                elif self.values.pressedJump:
                    self.values.xVelocity = -self.values.slimeBounciness * self.values.xVelocity
                else:
                    self.values.xVelocity = 0

        self.xPositionLf, self.yPositionLf = self.values.xPosition, self.values.yPosition




class playerInputs:
    def __init__(self, values):
        self.values = values

    def Input(self):
        self.values.M1click = False

        for e in p.event.get():
            if e.type == p.QUIT:
                self.values.running = False
            if e.type == p.KEYDOWN:           #KEYDOWN
                if e.key == self.values.inputRight:
                    self.values.pressedRight = True
                if e.key == self.values.inputLeft:
                    self.values.pressedLeft = True
                if e.key == self.values.inputJump or e.key == self.values.inputAltJump:
                    self.values.pressedJump = True
                if e.key == self.values.inputDash:
                    self.values.pressedDash = True
                if e.key == self.values.inputSettings:
                    self.values.inSettings = not self.values.inSettings

                if self.values.lookingForInput:
                    self.values.newKey = e.key
                    self.values.lookingForInput = False

            if e.type == p.MOUSEBUTTONDOWN:     #MOUSEDOWN
                self.values.M1hold = True
                self.values.M1click = True

            if e.type == p.MOUSEBUTTONUP:     #MOUSEUP
                self.values.M1hold = False

            if e.type == p.KEYUP:             #KEYUP
                if e.key == self.values.inputRight:
                    self.values.pressedRight = False
                if e.key == self.values.inputLeft:
                    self.values.pressedLeft = False
                if e.key == self.values.inputJump or e.key == self.values.inputAltJump:
                    self.values.pressedJump = False
                if e.key == self.values.inputDash:
                    self.values.pressedDash = False




        if self.values.dTime == 0:  # if process is suspended inputs are cancelled, cause if a key goes up while suspended the game won't notice and it'll think its still pressed
            self.values.pressedRight = False
            self.values.pressedLeft = False
            self.values.pressedJump = False
            self.values.pressedDash = False


class Scrolling:
    def __init__(self, values):
        self.values = values
    def Scrolling(self):

        playerX = self.values.xPosition - self.values.originalWIDTH / 2

        diffX = playerX - self.values.cameraPosition

        self.values.cameraPosition += diffX * self.values.scrollingSpeed * self.values.dTime\
                                    + self.values.xVelocity * self.values.scrollingSpeed * self.values.dTime




class AnimationController:
    def __init__(self, values):
        self.values = values

    def PlayerAnimations(self):
        if self.values.isFinished:
            self.values.currentFrameSlimePic = self.values.slimePics["slime_happy"]
        elif self.values.isDead:
            self.values.currentFrameSlimePic = self.values.slimePics["slime_sad"]
        elif self.values.xVelocity < -self.values.idleThreshhold * self.values.dTime:
            self.values.currentFrameSlimePic = self.values.slimePics["slime_left"]  # slime facing left
        elif -self.values.idleThreshhold * self.values.dTime <= self.values.xVelocity <= self.values.idleThreshhold * self.values.dTime:
            self.values.currentFrameSlimePic = self.values.slimePics["slime_front"]  # slime facing front
        elif self.values.xVelocity > self.values.idleThreshhold * self.values.dTime:
            self.values.currentFrameSlimePic = self.values.slimePics["slime_right"]  # slime facing right


class UserInterface:
    def __init__(self, values):
        self.values = values
        p.font.init()
        self.font = p.font.Font('freesansbold.ttf', 200)  # sets font for text

        self.selectedObj = None
        self.index = None
        self.isMoving = False
        self.isScaling = False

        self.isPlatform = False
        self.isObstacle = False
        self.isGoal = False

    def DeathScreen(self):
        self.values.dTime = 0
        self.values.screen.blit(p.transform.scale(self.values.slimePics["slime_sad"],
                                                  (self.values.HEIGHT*.8, self.values.HEIGHT*.8)),
                                (self.values.WIDTH*.25, self.values.HEIGHT*.1))
        ###  Death TEXT ###
        self.values.class_userInterface.DisplayText("You died", (650, 100), 100, "Dark Red",
                                                    self.values.screen, False, "Blue")

        ###  try again button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Try again", (30, 900), 100, "orange",
                                                                   self.values.screen, True, "light Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.xPosition = 0
            self.values.yPosition = -50
            self.values.isDead = False

    def WinScreen(self):
        self.values.dTime = 0
        self.values.screen.blit(p.transform.scale(self.values.slimePics["slime_happy"],
                                                  (self.values.HEIGHT*.8, self.values.HEIGHT*.8)),
                                (self.values.WIDTH*.25, self.values.HEIGHT*.1))

        ###  Win TEXT ###
        self.values.class_userInterface.DisplayText("Level Complete", (450, 100), 100, "White",
                                                    self.values.screen, False, "Blue")

        ###  Return to Main Menu button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Return to Main Menu", (30, 900), 100, "Orange",
                                                                   self.values.screen, True, "light blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            if self.values.inEditMode:
                self.values.class_map.SaveMap(self.values.currentLevel, False)
            self.values.inGame = False
            self.values.inMenu = True
            self.values.inSettings = False
            self.values.isFinished = False

            self.values.class_physics.ResetEngine()

    def Dash(self):
        if self.values.dashCooldown <= 0 and not self.values.inEditMode:
            self.values.class_userInterface.DisplayText("Dash", (1700, 950), 50, "White",
                                                        self.values.screen, False, "Blue")
        elif not self.values.inEditMode:
            self.values.class_userInterface.DisplayText("Dash", (1700, 950), 50, "dark Grey",
                                                        self.values.screen, False, "Blue")


    def Editing(self):
        ### the first part gets the obj u clicked on ###
        for i in range(len(self.values.allPlatforms)):
            obj = p.Rect((self.values.allPlatforms[i].x - self.values.cameraPosition) * self.values.xFactor,
                         self.values.allPlatforms[i].y * self.values.yFactor,
                         self.values.allPlatforms[i].w * self.values.xFactor,
                         self.values.allPlatforms[i].h * self.values.yFactor)
            if obj.collidepoint(p.mouse.get_pos()) and self.values.M1click and self.selectedObj is None:
                self.selectedObj = obj
                self.index = i
                self.isPlatform = True
                self.values.M1click = False

        for i in range(len(self.values.allObstacles)):
            obj = p.Rect((self.values.allObstacles[i].x-self.values.cameraPosition) * self.values.xFactor,
                         self.values.allObstacles[i].y * self.values.yFactor,
                         self.values.allObstacles[i].w * self.values.xFactor,
                         self.values.allObstacles[i].h * self.values.yFactor)
            if obj.collidepoint(p.mouse.get_pos()) and self.values.M1click and self.selectedObj is None:
                self.selectedObj = obj
                self.index = i
                self.isObstacle = True
                self.values.M1click = False

        for i in range(len(self.values.allGoals)):
            obj = p.Rect((self.values.allGoals[i].x-self.values.cameraPosition) * self.values.xFactor,
                         self.values.allGoals[i].y * self.values.yFactor,
                         self.values.allGoals[i].w * self.values.xFactor,
                         self.values.allGoals[i].h * self.values.yFactor)
            if obj.collidepoint(p.mouse.get_pos()) and self.values.M1click and self.selectedObj is None:
                self.selectedObj = obj
                self.index = i
                self.isGoal = True
                self.values.M1click = False

        if self.selectedObj is None:
            ### click on any Object TEXT ###
            self.values.class_userInterface.DisplayText("Click on any Object", (450, 100), 80, "white",
                                                        self.values.screen, False, "light blue")
            ### Add Platform button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Add Platform", (100, 770), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.values.allPlatforms.append(p.Rect(self.values.originalWIDTH//2 + self.values.cameraPosition,
                                                       self.values.originalHEIGHT // 2, 300, 60))

            ### Add Obstacle button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Add Obstacle", (100, 870), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.values.allObstacles.append(p.Rect(self.values.originalWIDTH//2 + self.values.cameraPosition,
                                                       self.values.originalHEIGHT // 2, 300, 60))

            ### Add goal button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Add Goal", (100, 970), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.values.allGoals.append(p.Rect(self.values.originalWIDTH//2 + self.values.cameraPosition,
                                                   self.values.originalHEIGHT // 2, 300, 60))

            ### Save Level button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Save Level", (1200, 970), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.values.M1click = False
                self.values.class_map.SaveMap(self.values.currentLevel, False)

        elif not self.isMoving and not self.isScaling:

            ### change pos button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Change Position", (100, 970), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.isMoving = True
                self.values.M1hold = False

            ### change Scale button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Change Scale", (1100, 970), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.isScaling = True
                self.values.M1hold = False

        if self.values.M1click and not self.isMoving and not self.isScaling and self.selectedObj is not None:
            self.selectedObj = None
            self.isPlatform = False
            self.isObstacle = False
            self.isGoal = False

        elif self.isMoving:
            ### Back button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Back", (900, 970), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.isMoving = False
            if self.values.M1hold and self.isMoving:  # so that obj isnt moved to the back button
                if self.isPlatform:
                    self.values.allPlatforms[self.index] = \
                        p.Rect(p.mouse.get_pos()[0] / self.values.xFactor + self.values.cameraPosition,
                               p.mouse.get_pos()[1] / self.values.yFactor,
                               self.values.allPlatforms[self.index].w, self.values.allPlatforms[self.index].h)
                elif self.isObstacle:
                    self.values.allObstacles[self.index] = \
                        p.Rect(p.mouse.get_pos()[0]/self.values.xFactor + self.values.cameraPosition,
                               p.mouse.get_pos()[1]/self.values.yFactor,
                               self.values.allObstacles[self.index].w, self.values.allObstacles[self.index].h)
                elif self.isGoal:
                    self.values.allGoals[self.index] = \
                        p.Rect(p.mouse.get_pos()[0]/self.values.xFactor + self.values.cameraPosition,
                               p.mouse.get_pos()[1]/self.values.yFactor,
                               self.values.allGoals[self.index].w, self.values.allGoals[self.index].h)


        elif self.isScaling:
            ### Back button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Back", (900, 970), 80, "Orange",
                                                                       self.values.screen, True, "light blue")
            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.isScaling = False
            if self.values.M1hold and self.isScaling:
                if self.isPlatform:
                    newWidth = p.mouse.get_pos()[0]/self.values.xFactor + self.values.cameraPosition - self.values.allPlatforms[self.index].x
                    newWidth = int(newWidth/self.values.pixelSCALE) * self.values.pixelSCALE

                    if newWidth <= self.values.minPlatformWidth:
                        newWidth = self.values.minPlatformWidth

                    self.values.allPlatforms[self.index] = p.Rect(self.values.allPlatforms[self.index].x,
                                                                  self.values.allPlatforms[self.index].y,
                                                                  newWidth, self.values.minPlatformHEIGHT)
                elif self.isObstacle:
                    newWidth = p.mouse.get_pos()[0] / self.values.xFactor + self.values.cameraPosition - self.values.allObstacles[self.index].x
                    newWidth = int(newWidth / self.values.pixelSCALE) * self.values.pixelSCALE

                    newHeight = p.mouse.get_pos()[1] / self.values.yFactor - self.values.allObstacles[self.index].y
                    newHeight = int(newHeight / self.values.pixelSCALE) * self.values.pixelSCALE

                    if newWidth <= 5 * self.values.pixelSCALE:
                        newWidth = 5 * self.values.pixelSCALE
                    if newHeight <= 5 * self.values.pixelSCALE:
                        newHeight = 5 * self.values.pixelSCALE

                    self.values.allObstacles[self.index] = p.Rect(self.values.allObstacles[self.index].x,
                                                                  self.values.allObstacles[self.index].y,
                                                                  newWidth, newHeight)
                elif self.isGoal:
                    newWidth = p.mouse.get_pos()[0] / self.values.xFactor + self.values.cameraPosition - self.values.allGoals[self.index].x
                    newWidth = int(newWidth / self.values.pixelSCALE) * self.values.pixelSCALE

                    newHeight = p.mouse.get_pos()[1] / self.values.yFactor - self.values.allGoals[self.index].y
                    newHeight = int(newHeight / self.values.pixelSCALE) * self.values.pixelSCALE

                    if newWidth <= 5 * self.values.pixelSCALE:
                        newWidth = 5 * self.values.pixelSCALE
                    if newHeight <= 5 * self.values.pixelSCALE:
                        newHeight = 5 * self.values.pixelSCALE
                    self.values.allGoals[self.index] = p.Rect(self.values.allGoals[self.index].x,
                                                                  self.values.allGoals[self.index].y,
                                                                  newWidth, newHeight)


    def ClickedUIObject(self, uiObject):
        return True if uiObject.collidepoint(p.mouse.get_pos()) and self.values.M1click else False

    def HighlightOnHover(self, uiObject, color):
        if uiObject.collidepoint(p.mouse.get_pos()):
            p.draw.rect(self.values.screen, color, uiObject)

    def DisplayText(self, text, position, size, color, surface, highlight, highlightcolor):
        textPosition = (position[0] * self.values.xFactor, position[1] * self.values.yFactor)
        textSize = (size * len(text) * .7 * self.values.xFactor, size * 1 * self.values.yFactor)

        text = self.font.render(text, True, color)  # generates text
        text = p.transform.scale(text, textSize).convert_alpha()  # resizes text

        textRect = p.Rect(textPosition[0], textPosition[1], text.get_rect().w, text.get_rect().h)  # gets textbackground

        if highlight:  # highlight text using the textbackground
            self.HighlightOnHover(textRect, highlightcolor)

        surface.blit(text, textPosition)

        return textRect
