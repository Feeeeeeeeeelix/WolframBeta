import sqlite3
import pygame as p


class Values:
    def __init__(self):
        """Constant variables"""
        self.originalWIDTH, self.originalHEIGHT = 1920, 1080

        self.inEditMode = False
        self.isDead = False
        self.isFinished = False

        self.WIDTH, self.HEIGHT = 1920, 1080
        self.xFactor, self.yFactor = self.WIDTH / self.originalWIDTH, self.HEIGHT / self.originalHEIGHT
        self.pixelSCALE = 10
        self.charWidth, self.charHeight = 10 * self.pixelSCALE, 10 * self.pixelSCALE

        self.newWIDTH, self.newHEIGHT = self.WIDTH, self.HEIGHT

        self.screen = any
        self.clock = any

        self.musicPlayer = any

        self.runSpeed = 400  # values for basic actions
        self.playingRunSpeed = 400
        self.editingRunSpeed = 1500
        self.runAcceleration = 10000
        self.jumpBoost = 1500
        self.groundDrag = 3000
        self.airDrag = self.groundDrag / 4
        self.gravitationalAcceleration = 3000

        self.idleThreshhold = 500
        self.slimeBounciness = .8
        self.platformHEIGHT = 44 * self.pixelSCALE
        self.minPlatformWidth = 28 * self.pixelSCALE
        self.minPlatformHEIGHT = 6 * self.pixelSCALE

        self.dashDistance = 300
        self.dashBounceVel = self.dashDistance * 10
        self.dashCooldownValue = 3


        self.db = ("Levels.db")
        self.dbCustom = ("CustomLevels.db")
        self.dbSettings = ("Settings.db")

        self.inputRight = p.K_d  # default keybinds
        self.inputLeft = p.K_a
        self.inputJump = p.K_w
        self.inputAltJump = p.K_SPACE
        self.inputDash = p.K_LSHIFT
        self.inputSettings = p.K_ESCAPE

        self.newInputRight = int
        self.newInputLeft = int
        self.newInputJump = int
        self.newInputAltJump = int
        self.newInputDash = int
        self.newInputSettings = int

        self.scrollingSpeed = 1.0


            # player pics
        self.slimePics = {}
        self.slimePicNames = ["slime_left", "slime_front", "slime_right", "slime_squashed", "slime_happy", "slime_sad"]  # name of image files

            # environment pics
        self.allPlatforms = []
        self.allGoals = []
        self.allObstacles = []
        self.allPlatformTextures = []
        self.backgroundIMG = "background"   # name of image files
        self.background2IMG = "background2"   # name of image files
        self.borderIMG = "borders"
        self.platformEndIMG = "platform_end"
        self.platformPillarIMG = "platform_pillar"
        self.platformProlongationsIMG = ["platform_prolongation_" + str(i) for i in range(12)]
        self.platformMainsIMG = ["platform_main_" + str(i) for i in range(24)]
        self.chainStartIMG = "chains_start"
        self.chainsIMG = ["chains_" + str(i) for i in range(12)]

            # setting pics
        self.settingsBackgroundIMG = "settings_background"

        """real time changing variables"""
        self.dTime = 0
        self.charHitbox = p.Rect(0, 0, 0, 0)
        self.charDisplayHitbox = p.Rect(0, 0, 0, 0)
        self.volume = .8

        self.xPosition = 0
        self.yPosition = 512
        self.xVelocity = 0
        self.yVelocity = 0
        self.xAcceleration = 0
        self.yAcceleration = 0

        self.cameraPosition = - self.WIDTH / 2

        self.running = True
        self.isIdle = True
        self.pressedRight = False
        self.pressedLeft = False
        self.pressedJump = False
        self.pressedDash = False
        self.M1click = False
        self.M1hold = False
        self.inGame = False
        self.inMenu = True
        self.inSettings = False
        self.isGrounded = False
        self.isBouncing = False
        self.lookingForInput = False
        self.newKey = -1
        self.currentLevel = None

        self.dashCooldown = 0
        self.isDashFrame = False

        self.currentFrameSlimePic = any

        """class instances"""
        self.class_animationController = any
        self.class_map = any
        self.class_scrolling = any
        self.class_physics = any
        self.class_playerInputs = any
        self.class_collisions = any
        self.class_userInterface = any
        self.class_settings = any
        self.class_mainMenu = any

    def loadingPictures(self):
        self.background = p.transform.scale(p.image.load("images/" + self.backgroundIMG + ".png"),
                                            (self.WIDTH, self.HEIGHT)).convert_alpha() # loading environment images to variables

        self.background2 = p.transform.scale(p.image.load("images/" + self.background2IMG + ".png"),
                                             (self.WIDTH, self.HEIGHT)).convert_alpha()

        self.border = p.transform.scale(p.image.load("images/" + self.borderIMG + ".png"),
                                        (self.WIDTH, self.HEIGHT)).convert_alpha()

        self.platformPillar = p.transform.scale(p.image.load("images/" + self.platformPillarIMG + ".png"),
                                                (24 * self.pixelSCALE,
                                                 38 * self.pixelSCALE)).convert_alpha()

        self.platformEnd = p.transform.scale(p.image.load("images/" + self.platformEndIMG + ".png"),
                                             (1 * self.pixelSCALE,
                                              3 * self.pixelSCALE)).convert()

        self.platformProlongations = [
            p.transform.scale(p.image.load("images/" + self.platformProlongationsIMG[i] + ".png"),
                              (1 * self.pixelSCALE,
                               5 * self.pixelSCALE)).convert() for i in range(12)]

        self.platformMains = [p.transform.scale(p.image.load("images/" + self.platformMainsIMG[i] + ".png"),
                                                (1 * self.pixelSCALE,
                                                 6 * self.pixelSCALE)).convert() for i in range(24)]
        self.chains = [p.transform.scale(p.image.load("images/" + self.chainsIMG[i] + ".png"),
                                         (1 * self.pixelSCALE,
                                          2 * self.pixelSCALE)).convert() for i in range(12)]
        self.chainStart = p.transform.scale(p.image.load("images/" + self.chainStartIMG + ".png"),
                                            (3 * self.pixelSCALE,
                                             2 * self.pixelSCALE)).convert_alpha()

        for picName in self.slimePicNames:  # loading player images to variables
            self.slimePics[picName] = p.transform.scale(p.image.load("images/" + picName + ".png"),
                                                        (self.charWidth * self.xFactor,
                                                         self.charHeight * self.yFactor)).convert_alpha()
            # loading setting images to variables
        self.settingsBackground = p.transform.scale(p.image.load(f"images/{self.settingsBackgroundIMG}.png"),
                                                    (self.WIDTH, self.HEIGHT)).convert_alpha()


class MainMenu:
    def __init__(self, values):
        self.values = values

        self.inLevelSelect = False
        self.inCredits = False
        self.inCustomLevelSelect = False
        self.inEditCustomLevels = False

    def MainMenuController(self):
        if self.values.inSettings:
            pass
        elif self.inLevelSelect:
            self.LevelSelect()
        elif self.inCustomLevelSelect:
            self.CustomLevelSelect()
        elif self.inEditCustomLevels:
            self.EditCustomLevels()
        elif self.inCredits:
            self.Credits()
        else:
            self.TitleScreen()

    def TitleScreen(self):
        self.values.screen.blit(self.values.background, (0, 0))

        ###  Spielen Button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Spielen", (200, 300), 300, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inLevelSelect = True

        ###  Credits Button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Credits", (30, 950), 100, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inCredits = True

    def LevelSelect(self):
        self.values.screen.blit(self.values.background, (0, 0))

        ###  Select a Level TEXT ###
        self.values.class_userInterface.DisplayText("Select a level", (100, 30), 100, "White",
                                                    self.values.screen, False, "Blue")

        levels = self.CountLevels(False)

        for level in range(1, levels+1):
            self.LevelButton(level, 100 + level * 110, 100, False, True)

        ###  Custom Levels button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Custom Levels", (950, 950), 100, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inLevelSelect = False
            self.inCustomLevelSelect = True

        ###  Back button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inLevelSelect = False

    def CustomLevelSelect(self):
        self.values.screen.blit(self.values.background, (0, 0))
        ###  Select a Level TEXT ###
        self.values.class_userInterface.DisplayText("Select a level", (100, 30), 100, "White",
                                                    self.values.screen, False, "Blue")

        levels = self.CountLevels(True)

        for level in range(1, levels+1):
            self.LevelButton(level, 100 + level * 110, 100, True, True)

        ###  Edit Custom Levels button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Edit Custom Levels", (600, 950), 100, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inCustomLevelSelect = False
            self.inEditCustomLevels = True

        ###  Back button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inCustomLevelSelect = False
            self.inLevelSelect = True

    def EditCustomLevels(self):
        self.values.screen.blit(self.values.background, (0, 0))
        ###  Select a Level TEXT ###
        self.values.class_userInterface.DisplayText("Select a level to Edit", (100, 30), 100, "White",
                                                    self.values.screen, False, "Blue")

        levels = self.CountLevels(True)
        for level in range(1, levels+1):
            self.LevelButton(level, 100 + level * 110, 100, True, False)


        ### New Custom Level button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("New Custom Level", (740, 950), 100,
                                                                   "White", self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.class_map.SaveMap(levels+1, True)

        ### Back button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inEditCustomLevels = False
            self.inCustomLevelSelect = True

    def CountLevels(self, isCustom):
        isLastLevel = False
        levels = 0
        while not isLastLevel:
            try:
                self.values.class_map.LoadMap(levels+1, True, isCustom)
                levels += 1
            except:
                isLastLevel = True
        return levels

    def LevelButton(self, level, y, size, isCustom, isGonnaPlay):
        ###  Level Button ###
        if level % 2:
            buttonHitbox = self.values.class_userInterface.DisplayText(f"Level {str(level)}", (300, y), size, "Orange",
                                                                       self.values.screen, True, "light Blue")
        else:
            buttonHitbox = self.values.class_userInterface.DisplayText(f"Level {str(level)}", (1000, y - 110), size, "Orange",
                                                                       self.values.screen, True, "light Blue")
        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.currentLevel = level
            self.values.class_map.LoadMap(level, False, isCustom)  # loads obj from map
            for obj in self.values.allPlatforms:  # creates textures now that obj are loaded
                self.values.class_map.createPlatformTexture(obj)

            if self.values.WIDTH != self.values.originalWIDTH:  # because the textures are generated after loading
                for i in range(len(self.values.allPlatforms)):  # the settings, the rescaling is skipped so here it is
                    if self.values.allPlatforms[i].w >= self.values.minPlatformWidth:
                        self.values.allPlatformTextures[i] = p.transform.scale(self.values.allPlatformTextures[i],
                                                                               (self.values.allPlatforms[i].w * self.values.xFactor,
                                                                                self.values.HEIGHT))

            if isGonnaPlay:
                self.values.inEditMode = False
                self.values.runSpeed = self.values.playingRunSpeed
            else:
                self.values.inEditMode = True
                self.values.yPosition = 10000
                self.values.runSpeed = self.values.editingRunSpeed

            self.values.inMenu = False
            self.values.inGame = True

    def Credits(self):
        self.values.screen.blit(self.values.background, (0, 0))

        self.values.class_userInterface.DisplayText("Code by:", (200, 30), 100, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Konrad Linden,", (500, 150), 80, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Cassiel Cleriot-Merker", (500, 260), 80, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Art by:", (200, 360), 100, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Cassiel Cleriot-Merker,", (500, 480), 80, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Silas", (500, 590), 80, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Music by:", (200, 690), 100, "White",
                                                    self.values.screen, False, "Blue")
        self.values.class_userInterface.DisplayText("Jakob Köhn", (500, 810), 80, "White",
                                                    self.values.screen, False, "Blue")

        ###  Back button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inCredits = False


class Settings:
    def __init__(self, values):
        self.values = values

        self.inResMenu = False  # variable used, to verify if the player is in the Settings/Resolution Menu
        self.inKeyMenu = False  # variable used, to verify if the player is in the Settings/Keybinds Menu
        self.inAudioMenu = False

        self.lfRight = False  # these are needed, so that u cant press any buttons while assigning a new key
        self.lfLeft = False  # lf = looking for (Input)
        self.lfJump = False
        self.lfAltJump = False
        self.lfDash = False
        self.lfSettings = False

        self.db = self.values.dbSettings

    def SettingsController(self):
        if self.inResMenu:
            self.ResolutionInterface()
        elif self.inKeyMenu:
            self.KeybindInterface()
        elif self.inAudioMenu:
            self.AudioInterface()
        else:
            self.MainInterface()

    def MainInterface(self):
        self.values.screen.blit(self.values.settingsBackground, (0, 0))  # displays background for settings menu
        y = 0

        ###  Resume button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Resume", (300, 220 + y * 120), 100, "White",
                                                                   self.values.screen, True, "Blue")
        y += 1

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.inSettings = False

        if self.values.inGame:
            ###  Return to Title Screen button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Return to Main Menu", (300, 220 + y * 120), 100, "White",
                                                                       self.values.screen, True, "Blue")
            y += 1

            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                if self.values.inEditMode:
                    self.values.class_map.SaveMap(self.values.currentLevel, False)
                self.values.inGame = False
                self.values.inMenu = True
                self.values.inSettings = False

                self.values.class_physics.ResetEngine()

        if self.values.inGame and self.values.inEditMode:
            ###  Return without saving button ###
            buttonHitbox = self.values.class_userInterface.DisplayText("Return without saving", (300, 220 + y * 120), 100, "White",
                                                                       self.values.screen, True, "Blue")
            y += 1

            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.values.inGame = False
                self.values.inMenu = True
                self.values.inSettings = False

                self.values.class_physics.ResetEngine()

        ###  Audio button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Audio", (300, 220 + y * 120), 100,
                                                                   "White",
                                                                   self.values.screen, True, "Blue")
        y += 1

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inAudioMenu = True

        ###  Resolution button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Resolution", (300, 220 + y * 120), 100, "White",
                                                                   self.values.screen, True, "Blue")
        y += 1

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inResMenu = True

        ###  Keybinds button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Keybinds", (300, 220 + y * 120), 100, "White",
                                                                   self.values.screen, True, "Blue")
        y += 1

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inKeyMenu = True

        ###  Quit button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Quit", (300, 220 + y * 120), 100, "White",
                                                                   self.values.screen, True, "Blue")
        y += 1

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            if self.values.inEditMode:
                self.values.class_map.SaveMap(self.values.currentLevel, False)
            self.values.running = False

    def AudioInterface(self):
        self.values.screen.blit(self.values.settingsBackground, (0, 0))  # displays background for settings menu
        ###  Vollume on/off button ###
        switchTo = "On" if self.values.volume == 0 else "Off"

        buttonHitbox = self.values.class_userInterface.DisplayText(f"Turn Music {switchTo}", (600, 300), 100, "Orange",
                                                                   self.values.screen, True, "light blue")
        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.volume = .8 if switchTo == "On" else 0
            self.values.musicPlayer.set_volume(self.values.volume)

        ###  Volume Up button ###
        buttonHitbox = self.values.class_userInterface.DisplayText(f"Volume Up", (600, 420), 100, "Orange",
                                                                   self.values.screen, True, "light blue")
        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.volume += .1
            self.values.musicPlayer.set_volume(self.values.volume)
        ###  Volume down button ###
        buttonHitbox = self.values.class_userInterface.DisplayText(f"Volume Down", (600, 560), 100, "Orange",
                                                                   self.values.screen, True, "light blue")
        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.volume -= .1
            self.values.musicPlayer.set_volume(self.values.volume)

        ###  Back button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inAudioMenu = False

    def ResolutionInterface(self):
        self.values.screen.blit(self.values.settingsBackground, (0, 0))  # displays background for settings menu

        ###  Resolution TEXT ###
        self.values.class_userInterface.DisplayText("Resolution", (650, 100), 100, "White",
                                                    self.values.screen, False, "Blue")

        ###  Ultra HD button ###
        self.ResolutionButton(3849, 2160, "Ultra HD", 300)

        ###  WQHD button ###
        self.ResolutionButton(2560, 1440, "WQHD", 380)

        ###  Full HD button ###
        self.ResolutionButton(1920, 1080, "Full HD", 460)

        ###  HD button ###
        self.ResolutionButton(1280, 720, "HD", 540)

        ###  PAL button ###
        self.ResolutionButton(720, 480, "PAL", 620)

        ###  Resume button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Resume", (50, 870), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):  # on click
            self.values.inSettings = False

        ###  Back button ###
        buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                   self.values.screen, True, "Blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.inResMenu = False

    def ResolutionButton(self, width, height, name, y):
        ###  Resolution button ###
        buttonHitbox = self.values.class_userInterface.DisplayText(f"{name} ({width} x {height})", (600, y), 70,
                                                                   "Orange", self.values.screen, True, "light blue")

        if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
            self.values.newWIDTH = width
            self.values.newHEIGHT = height
            self.StoreSettings()
            self.LoadSettings()

    def KeybindInterface(self):
        self.values.screen.blit(self.values.settingsBackground, (0, 0))  # displays background for settings menu

        ###  Keybinds TEXT ###
        self.values.class_userInterface.DisplayText("Keybinds", (650, 100), 100, "White",
                                                    self.values.screen, False, "Blue")

        ###  Right button ###
        newInput, self.lfRight = self.KeybindButton("Right", (600, 300), self.lfRight)
        if newInput is not None:
            self.values.newInputRight =newInput
            self.StoreSettings()
            self.LoadSettings()
            newInput = None

        ###  Left button ###
        newInput, self.lfLeft = self.KeybindButton("Left", (600, 380), self.lfLeft)
        if newInput is not None:
            self.values.newInputLeft = newInput
            self.StoreSettings()
            self.LoadSettings()
            newInput = None

        ###  Jump button ###
        newInput, self.lfJump = self.KeybindButton("Jump", (600, 460), self.lfJump)
        if newInput is not None:
            self.values.newInputJump = newInput
            self.StoreSettings()
            self.LoadSettings()
            newInput = None

        ###  ALtJump button ###
        newInput, self.lfAltJump = self.KeybindButton("Jump 2", (600, 540), self.lfAltJump)
        if newInput is not None:
            self.values.newInputAltJump = newInput
            self.StoreSettings()
            self.LoadSettings()
            newInput = None

        ###  Dash button ###
        newInput, self.lfDash = self.KeybindButton("Dash", (600, 620), self.lfDash)
        if newInput is not None:
            self.values.newInputDash = newInput
            self.StoreSettings()
            self.LoadSettings()
            newInput = None

        ###  Settings button ###
        newInput, self.lfSettings = self.KeybindButton("Settings", (600, 700), self.lfSettings)
        if newInput is not None:
            self.values.newInputSettings = newInput
            self.StoreSettings()
            self.LoadSettings()
            newInput = None

        ###  Resume button ###
        if not self.values.lookingForInput:
            buttonHitbox = self.values.class_userInterface.DisplayText("Resume", (50, 870), 80, "White",
                                                                       self.values.screen, True, "Blue")

            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):  # on click
                self.values.inSettings = False

        ###  Back button ###
        if not self.values.lookingForInput:
            buttonHitbox = self.values.class_userInterface.DisplayText("Back", (50, 970), 80, "White",
                                                                       self.values.screen, True, "Blue")

            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.inKeyMenu = False

    def KeybindButton(self, text, pos, lf):
        if not self.values.lookingForInput or self.values.lookingForInput and lf:
            ### button ###
            buttonHitbox = self.values.class_userInterface.DisplayText(text, pos, 70,
                                                                       "orange", self.values.screen, True, "light Blue")

            if self.values.class_userInterface.ClickedUIObject(buttonHitbox):
                self.values.lookingForInput = True
                lf = True
            if self.values.lookingForInput and lf:
                ###  Press any key TEXT ###

                p.draw.rect(self.values.screen, "White", (350*self.values.xFactor, 430*self.values.yFactor,
                                                          1150*self.values.xFactor, 160*self.values.yFactor))
                self.values.class_userInterface.DisplayText("Press any key", (400, 450), 120, "Blue",
                                                            self.values.screen, False, "Blue")

            if self.values.newKey != -1 and lf:
                returnkey = self.values.newKey
                self.values.newKey = -1
                lf = False
                return returnkey, lf
            else:
                return None, lf
        else:
            return None, lf


    def StoreSettings(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()

            if self.values.newInputRight != self.values.inputRight:
                cur.execute(f"UPDATE keybinds SET key = {self.values.newInputRight}"
                            f" WHERE action = 'inputRight'")
            if self.values.newInputLeft != self.values.inputLeft:
                cur.execute(f"UPDATE keybinds SET key = {self.values.newInputLeft}"
                            f" WHERE action = 'inputLeft'")
            if self.values.newInputJump != self.values.inputJump:
                cur.execute(f"UPDATE keybinds SET key = {self.values.newInputJump}"
                            f" WHERE action = 'inputJump'")
            if self.values.newInputAltJump != self.values.inputAltJump:
                cur.execute(f"UPDATE keybinds SET key = {self.values.newInputAltJump}"
                            f" WHERE action = 'inputAltJump'")
            if self.values.newInputDash != self.values.inputDash:
                cur.execute(f"UPDATE keybinds SET key = {self.values.newInputDash}"
                            f" WHERE action = 'inputDash'")
            if self.values.newInputSettings != self.values.inputSettings:
                cur.execute(f"UPDATE keybinds SET key = {self.values.newInputSettings}"
                            f" WHERE action = 'inputSettings'")

            if self.values.newWIDTH != self.values.WIDTH:
                cur.execute(f"UPDATE resolution SET value = {self.values.newWIDTH}"
                            f" WHERE type = 'width'")
            if self.values.newHEIGHT != self.values.HEIGHT:
                cur.execute(f"UPDATE resolution SET value = {self.values.newHEIGHT}"
                            f" WHERE type = 'height'")

            conn.commit()

            cur.close()

    def LoadSettings(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()

            cur.execute(f"SELECT key FROM keybinds WHERE action = 'inputRight'")
            self.values.inputRight = cur.fetchall()[0][0]
            cur.execute(f"SELECT key FROM keybinds WHERE action = 'inputLeft'")
            self.values.inputLeft = cur.fetchall()[0][0]
            cur.execute(f"SELECT key FROM keybinds WHERE action = 'inputJump'")
            self.values.inputJump = cur.fetchall()[0][0]
            cur.execute(f"SELECT key FROM keybinds WHERE action = 'inputAltJump'")
            self.values.inputAltJump = cur.fetchall()[0][0]
            cur.execute(f"SELECT key FROM keybinds WHERE action = 'inputDash'")
            self.values.inputDash = cur.fetchall()[0][0]
            cur.execute(f"SELECT key FROM keybinds WHERE action = 'inputSettings'")
            self.values.inputSettings = cur.fetchall()[0][0]

            cur.execute(f"SELECT value FROM resolution WHERE type = 'width'")
            self.values.WIDTH = cur.fetchall()[0][0]
            cur.execute(f"SELECT value FROM resolution WHERE type = 'height'")
            self.values.HEIGHT = cur.fetchall()[0][0]

            conn.commit()
            cur.close()

            # recalculating stuff for new resolution
            self.values.xFactor, self.values.yFactor = self.values.WIDTH / self.values.originalWIDTH, \
                                                       self.values.HEIGHT / self.values.originalHEIGHT

            self.values.screen = p.display.set_mode((self.values.WIDTH, self.values.HEIGHT))

            self.values.loadingPictures()

            for i in range(len(self.values.allPlatforms)):
                if self.values.allPlatforms[i].w >= self.values.minPlatformWidth:
                    self.values.allPlatformTextures[i] = p.transform.scale(self.values.allPlatformTextures[i],
                                                                           (self.values.allPlatforms[i].w * self.values.xFactor,
                                                                            self.values.HEIGHT))

            self.values.newWIDTH, self.values.newHEIGHT = self.values.WIDTH, self.values.HEIGHT

            self.values.newInputRight = self.values.inputRight
            self.values.newInputLeft = self.values.inputLeft
            self.values.newInputJump = self.values.inputJump
            self.values.newInputAltJump = self.values.inputAltJump
            self.values.newInputDash = self.values.inputDash
            self.values.newInputSettings = self.values.inputSettings

            self.values.yPosition -= 20 * self.values.yFactor  # so that the slime doesn't glitch through the floor
