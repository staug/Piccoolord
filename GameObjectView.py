__author__ = 'staug'
import PythonExtraLib.Pyganim as pyganim
import pygame
import ast
import GameControllerView

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
        """
        This method prepares the road for the future draw. It doesn't call teh draw method it self,
        the draw needs to be called separately.
        """
        self.is_moving = True
        self.distance_left_to_move_x = self.distance_left_to_move_y = 0
        self.distance_moved_x = self.distance_moved_y = 0
        original_rect = GameControllerView.GameControllerView.get_grid_rect(self.owner.old_pos)
        target_rect = GameControllerView.GameControllerView.get_grid_rect(self.owner.pos)
        self.distance_left_to_move_x = target_rect.centerx - original_rect.centerx
        self.distance_left_to_move_y = target_rect.centery - original_rect.centery
        if self.animated:
            if self.distance_left_to_move_x > 0:
                self.direction = "RIGHT"
            elif self.distance_left_to_move_x < 0:
                self.direction = "LEFT"
            elif self.distance_left_to_move_y > 0:
                self.direction = "DOWN"
            else:
                self.direction = "UP"

    def draw(self):
        """
        Main function to draw. Test if it should do something, and calls the private clear method first before
        rendering on screen. Return teh list of rect impacted.
        """
        dirty_recs = []
        if self._get_game_view().is_displayable(self.owner.pos) \
            or self._get_game_view().is_displayable(self.owner.old_pos):
            if self.is_moving:
                # first, we clear the old
                #TODO
                pass
            elif self.redraw:
                #TODO
                self.redraw = False
                pass
        return dirty_recs

    def _clear(self, dx=0, dy=0):
        pass

    def need_redraw(self, value = True):
        self.redraw = value

    def _get_game_view(self):
        return self.owner.owner.view

class AnimatedGameObjectView(GameObjectView):
    pass


class StaticGameObjectView(GameObjectView):
    pass
