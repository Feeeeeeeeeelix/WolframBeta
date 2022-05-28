#!opt/homebrew/Cellar/python@3.8/3.8.12_1/Frameworks/Python.framework/Versions/3.8

import pygame as p
import Engine, Map, Values  # imports other files



values = Values.Values()  # loading in the other files
values.class_animationController = Engine.AnimationController(values)
values.class_map = Map.Map(values)
values.class_scrolling = Engine.Scrolling(values)
values.class_physics = Engine.Physics(values)
values.class_playerInputs = Engine.playerInputs(values)
values.class_collisions = Engine.Collisions(values)
values.class_userInterface = Engine.UserInterface(values)
values.class_settings = Values.Settings(values)
values.class_mainMenu = Values.MainMenu(values)


def main():
    p.init()  # Initialisation of pygame
    p.display.set_caption("Slime's still alive")
    values.screen = p.display.set_mode((values.WIDTH, values.HEIGHT))
    values.clock = p.time.Clock()
    values.musicPlayer = p.mixer.Sound("music.mp3")
    values.musicPlayer.play(-1)
    values.musicPlayer.set_volume(values.volume)
    values.loadingPictures()  # loads pictures
    values.class_settings.LoadSettings()  # loads settings from database
    while values.running:
        values.class_playerInputs.Input()  # gets the inputs, entered by the player
        if values.inMenu:
            values.class_mainMenu.MainMenuController()  # Main Menu also loads all objects as well as their textures
        if values.inGame:
            values.class_physics.DeltaTime()  # calculates dtime wich is needed in following steps
            values.class_physics.PositionUpdate()  # gets the new position from the given inputs
            if not values.inEditMode:
                values.class_collisions.CharCollision()  # verifies that new position is possible
            values.class_scrolling.Scrolling()  # calculates cameraposition
            values.class_map.DrawMap()  # Draws frame
            if values.isDead:  # if dead
                values.class_userInterface.DeathScreen()  # show death screen
            if values.isFinished:  # if won
                values.class_userInterface.WinScreen()  # schow win screen
            values.class_userInterface.Dash()  # show dash availability
            if values.inEditMode and not values.inSettings:
                values.class_userInterface.Editing()
        if values.inSettings:  # Draws settings interface over still frame
            values.class_settings.SettingsController()
        p.display.flip()  # do a barrel roll
        #values.clock.tick(60)  # locks fps




if __name__ == "__main__":  # executes main function
    main()
