__author__ = 'staug'
import PythonExtraLib.Pyganim as pyganim
import pygame
import ast

# tODO: switch to two classes??
# Todo: Manage a list of dirty rects
class GameObjectView:

    def __init__(self, resources):
        self.width = int(resources['image_size_x'])
        self.height = int(resources['image_size_y'])
        (x_top, y_top) = ast.literal_eval(resources['image_top'])
        self.animated = (resources['image_animated'] == 'yes')

        sprite_surface = pygame.image.load(resources['image_file']).convert_alpha()
        if self.animated:
            # Now split the image - we assume always 3
            self.images = {
                "UP": pyganim.PygAnimation([(sprite_surface.subsurface(pygame.Rect(x_top + self.width * i,
                                                                                   y_top,
                                                                                   self.width, self.height),
                                                                       0.1))
                                            for i in range(3)]),
                "RIGHT": pyganim.PygAnimation([(sprite_surface.subsurface(pygame.Rect(x_top + self.width * i,
                                                                                      y_top + 1 * self.height,
                                                                                      self.width, self.height)), 0.1)
                                               for i in range(3)]),
                "DOWN": pyganim.PygAnimation([(sprite_surface.subsurface(pygame.Rect(x_top + self.width * i,
                                                                                     y_top + 2 * self.height,
                                                                                     self.width, self.height)), 0.1)
                                              for i in range(3)]),
                "LEFT": pyganim.PygAnimation([(sprite_surface.subsurface(pygame.Rect(x_top + self.width * i,
                                                                                     y_top + 3 * self.height,
                                                                                     self.width, self.height)), 0.1)
                                              for i in range(3)])
            }
        else:
            self.images = {"UP": pyganim.PygAnimation([(sprite_surface.subsurface(
                pygame.Rect((x_top, y_top), (self.width, self.height))), 100)])}
        self.direction = "UP"
        self.is_moving = False
        self.redraw = True

    def move(self):
        self.is_moving = True
        original_grid_pos = self.owner.old_pos
        target_grid_pos = self.owner.old_pos
        self.distance_left_to_move_x = self.distance_left_to_move_y = 0

    def draw(self):
        if self.animated:
            pass
        elif self.redraw:
            self.redraw = False
            pass
        pass

    def _clear(self):
        pass

    def need_redraw(self, value = True):
        self.redraw = value

class AnimatedGameObjectView(GameObjectView):
    pass


class StaticGameObjectView(GameObjectView):
    pass
