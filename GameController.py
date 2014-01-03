__author__ = 'staug'

import WorldMapLogic
import GameControllerView


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
    while True:
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

                if event.key == pygame.K_UP:
                    moveUp = True
                    moveDown = False
                    if not moveLeft and not moveRight:
                        # only change the direction to up if the player wasn't moving left/right
                        direction = UP
                elif event.key == pygame.K_DOWN:
                    moveDown = True
                    moveUp = False
                    if not moveLeft and not moveRight:
                        direction = DOWN
                elif event.key == pygame.K_LEFT:
                    moveLeft = True
                    moveRight = False
                    if not moveUp and not moveDown:
                        direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    moveRight = True
                    moveLeft = False
                    if not moveUp and not moveDown:
                        direction = RIGHT

            elif event.type == pygame.KEYUP:

                if event.key == pygame.K_UP:
                    moveUp = False
                    # if the player was moving in a sideways direction before, change the direction the player is facing.
                    if moveLeft:
                        direction = LEFT
                    if moveRight:
                        direction = RIGHT
                elif event.key == pygame.K_DOWN:
                    moveDown = False
                    if moveLeft:
                        direction = LEFT
                    if moveRight:
                        direction = RIGHT
                elif event.key == pygame.K_LEFT:
                    moveLeft = False
                    if moveUp:
                        direction = UP
                    if moveDown:
                        direction = DOWN
                elif event.key == pygame.K_RIGHT:
                    moveRight = False
                    if moveUp:
                        direction = UP
                    if moveDown:
                        direction = DOWN

        if moveUp:
            dy -= 1
        if moveDown:
            dy += 1
        if moveLeft:
            dx -= 1
        if moveRight:
            dx += 1

        a_controller.view.camera.move(dx, dy)
        windowSurface.blit(a_controller.view.region_view, (0,0), area=a_controller.view.camera.camera_rect)
        windowSurface.blit(a_controller.view.explorer_map.surface, (50,50), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        mainClock.tick(30) # Feel free to experiment with any FPS setting.
