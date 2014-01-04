__author__ = 'staug'

import WorldMapLogic
import GameControllerView
import GameObject

class GameController:

    def __init__(self):
        self.world = WorldMapLogic.World("Piccool Dungeon", 3, (80, 80), (120, 120), 40, 60)
        self.region = self.world.regions[0]
        self.view = GameControllerView.GameControllerView(self)

        self.objects = []


    def is_blocked(self, x, y):
        '''
        test if the current position at (x,y) is blocking. It is blocking if the grid is blocked, or if
         there is an object that is currently on this position and this object is blocking
        '''
        #first test the map tile
        if self.region.grid[(x, y)].blocking:
            return True

        #now check for any blocking objects
        for an_object in self.objects:
            if an_object.blocking and an_object.x == x and an_object.y == y:
                return True

        return False

if __name__ == '__main__':
    # The following is for the test only
    import pygame
    import GameResources
    import sys
    import ConfigParser

    pygame.init()
    windowSurface = pygame.display.set_mode(GameResources.GLOBAL_WINDOW_SIZE, 0, 32)
    BGCOLOR = (100, 50, 50)
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    moveUp = moveDown = moveLeft = moveRight = False
    mainClock = pygame.time.Clock()
    dx = dy = 0

    a_controller = GameController()

    # import the player for test
    config = ConfigParser.RawConfigParser()
    config.read('resources/definitions.ini')
    player = GameObject.GameObject('player', config._sections['Player'], a_controller.region.get_starting_position(), blocking=True)
    player.owner = a_controller
    print(player.pos)
    a_controller.view.camera.center(player.pos)
    while True:
        moveUp = moveDown = moveLeft = moveRight = False
        dx = dy = 0
        windowSurface.fill(BGCOLOR)
        for event in pygame.event.get(): # event handling loop

        # handle ending the program
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.KEYUP:

                if event.key == pygame.K_UP:
                    moveUp = True
                elif event.key == pygame.K_DOWN:
                    moveDown = True
                elif event.key == pygame.K_LEFT:
                    moveLeft = True
                elif event.key == pygame.K_RIGHT:
                    moveRight = True
                if event.key == pygame.K_c:
                    a_controller.view.camera.center(player.pos)

        if moveUp:
            dy -= 1
        if moveDown:
            dy += 1
        if moveLeft:
            dx -= 1
        if moveRight:
            dx += 1

        player.move(dx, dy)
        player.draw()

        #a_controller.view.camera.move(dx, dy)
        windowSurface.blit(a_controller.view.region_view, (0,0), area=a_controller.view.camera.camera_rect)
        windowSurface.blit(a_controller.view.explorer_map.surface, (50,50), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        mainClock.tick(30) # Feel free to experiment with any FPS setting.
