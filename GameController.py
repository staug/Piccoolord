__author__ = 'staug'

import WorldMapLogic
import GameControllerView
import GameObject

class GameController:

    def __init__(self):
        self.world = WorldMapLogic.World("Piccool Dungeon", 3, (80, 80), (120, 120), 40, 60)
        self.view = GameControllerView.GameControllerView(self)
        self.setup_level(0)

        self.player_party = []
        self.player_index = 0

    def setup_level(self, level_number=0):
        self.region = self.world.regions[level_number]
        self.ticker = Ticker()
        self.objects = set()

        # set of walls and other blocking object:
        self.blocks = set()
        for x in range(self.region.size[0]):
            for y in range(self.region.size[1]):
                if self.region.grid[(x, y)].blocking:
                    self.blocks.add((x,y))

    def is_blocked(self, grid_pos):
        """
        test if the current position at (x,y) is blocking. It is blocking if the grid is blocked, or if
         there is an object that is currently on this position and this object is blocking
        """
        #first test the map tile
        if self.region.grid[(grid_pos)].blocking:
            return True

        #now check for any blocking objects
        for an_object in self.objects:
            if an_object.blocking and an_object.pos == grid_pos:
                return True

        return False

    @property
    def blocking_set(self):
        """
        The list of all blocking tiles in the game, including the objects
        """
        all_blocks = self.blocks.copy()
        for an_object in self.objects:
            if an_object.blocking:
                all_blocks.add(an_object.pos)
        return all_blocks

    def add_object(self, obj):
        obj.owner = self
        self.__add_remove_object(obj)

    def remove_object(self, obj):
        obj.owner = None
        self.__add_remove_object(obj, False)

    def __add_remove_object(self, obj, add=True):
        if add:
            self.objects.add(obj)
            if obj.player:
                self.player_party.append(obj)
        else:
            self.objects.remove(obj)
            if obj.player:
                self.player_party.remove(obj)

    @property
    def player(self):
        return self.player_party[self.player_index]


class Ticker(object):
    """Simple timer for roguelike games.
    Taken from http://www.roguebasin.com/index.php?title=A_simple_turn_scheduling_system_--_Python_implementation"""

    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do {ticks: [obj1, obj2, ...], ticks+1: [...], ...}

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def next_turn(self, increment=1):
        self.ticks += increment
        things_to_do = self.schedule.pop(self.ticks, [])
        for obj in things_to_do:
            obj.take_turn()


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
    a_controller.add_object(player)

    p2_ai = GameObject.FollowerAI(a_controller.ticker)
    player2 = GameObject.GameObject('player2', config._sections['Skeletton'], a_controller.region.get_starting_position(), blocking=True, ai=p2_ai)
    a_controller.add_object(player2)

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

        if dx != 0 or dy != 0:
            a_controller.player.move(dx, dy)
            # a_controller.view.update_fog_of_war(player.pos, 3)
            a_controller.ticker.next_turn()

            a_controller.view.explorer_map.center(a_controller.player.pos)
            if a_controller.view.camera.close_edge(a_controller.player.pos):
                a_controller.view.camera.center(a_controller.player.pos)
            for obj in a_controller.objects:
                print("Name: {} Pos: {}".format(obj.name, obj.pos))


        for obj in a_controller.objects:
            obj.draw()

        windowSurface.blit(a_controller.view.region_view, (0,0), area=a_controller.view.camera.camera_rect)
        windowSurface.blit(a_controller.view.explorer_map.surface, (50,50), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.display.update()
        mainClock.tick(30) # Feel free to experiment with any FPS setting.
