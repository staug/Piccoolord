__author__ = 'staug'
import PythonExtraLib.Pyganim as pyganim
import pygame
import ast
import GameControllerView


class GameObjectView:

    def __init__(self, resources):
        self.width = int(resources['image_size_x'])
        self.height = int(resources['image_size_y'])
        (x_top, y_top) = ast.literal_eval(resources['image_top'])
        self.animated = (resources['image_animated'] == 'yes')

        sprite_surface = pygame.image.load(resources['image_file']).convert_alpha()
        if self.animated:
            # Now split the image - we assume always 3
            rec_lists = [[pygame.Rect(x_top + self.width * i, y_top + j * self.height, self.width, self.height)
                              for i in range(3)] for j in range(4)]
            self.images = {
                "UP": pyganim.PygAnimation([(sprite_surface.subsurface(rec_lists[0][0]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[0][1]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[0][2]), 0.1)]),
                "RIGHT": pyganim.PygAnimation([(sprite_surface.subsurface(rec_lists[1][0]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[1][1]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[1][2]), 0.1)]),
                "DOWN": pyganim.PygAnimation([(sprite_surface.subsurface(rec_lists[2][0]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[2][1]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[2][2]), 0.1)]),
                "LEFT": pyganim.PygAnimation([(sprite_surface.subsurface(rec_lists[3][0]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[3][1]), 0.1),
                                            (sprite_surface.subsurface(rec_lists[3][2]), 0.1)])
            }
        else:
            self.images = {"UP": pyganim.PygAnimation([(sprite_surface.subsurface(
                pygame.Rect((x_top, y_top), (self.width, self.height))), 100)])}
        self.direction = "UP"
        self.is_moving = False
        self.redraw = True
        self._dirty_element_to_erase = []

    def move(self):
        """
        This method prepares the road for the future draw. It doesn't call teh draw method it self,
        the draw needs to be called separately.
        """

        # if we were already moving, we erase the old position on the next draw, so we keep it here
        if self.is_moving:
            self._dirty_element_to_erase.append((self.old_grid_pos, self.distance_moved_x, self.distance_moved_y))

        # First, we make a copy of the old pos as the draw may be slower
        self.old_grid_pos = self.owner.old_pos
        self.target_grid_pos = self.owner.pos

        self.is_moving = True
        self.distance_to_move_x = self.distance_to_move_y = 0
        self.distance_moved_x = self.distance_moved_y = 0
        original_rect = GameControllerView.GameControllerView.get_grid_rect(self.old_grid_pos)
        target_rect = GameControllerView.GameControllerView.get_grid_rect(self.target_grid_pos)
        self.distance_to_move_x = target_rect.centerx - original_rect.centerx
        self.distance_to_move_y = target_rect.centery - original_rect.centery
        if self.animated:
            if self.distance_to_move_x > 0:
                self.direction = "RIGHT"
            elif self.distance_to_move_x < 0:
                self.direction = "LEFT"
            elif self.distance_to_move_y > 0:
                self.direction = "DOWN"
            else:
                self.direction = "UP"
        self.images[self.direction].play(startTime=self.owner.controller.clock.get_time())

    def draw(self):
        """
        Main function to draw. Test if it should do something, and calls the private clear method first before
        rendering on screen. Return teh list of rect impacted.
        """
        dirty_recs = []
        if self._get_game_view().is_displayable(self.owner.pos) or \
                self._get_game_view().is_displayable(self.owner.old_pos):
            if self.is_moving:
                # Exceptional case; there may be a double move going on
                for dirty in self._dirty_element_to_erase:
                    dirty_recs += self._get_game_view().clear(dirty[0], dx=dirty[1], dy=dirty[2])
                self._dirty_element_to_erase = []
                # first, we clear the old
                dirty_recs += self._get_game_view().clear(self.old_grid_pos, dx=self.distance_moved_x, dy=self.distance_moved_y)
                if self.distance_to_move_x != 0 and self.distance_to_move_x != self.distance_moved_x:
                    if self.distance_to_move_x > 0:
                        self.distance_moved_x += 1
                    else:
                        self.distance_moved_x -= 1
                if self.distance_to_move_y != 0 and self.distance_to_move_y != self.distance_moved_y:
                    if self.distance_to_move_y > 0:
                        self.distance_moved_y += 1
                    else:
                        self.distance_moved_y -= 1
                # we paint the new one
                dirty_recs += self._get_game_view().draw(self.images[self.direction].getCurrentFrameSpecial(), self.old_grid_pos,
                                                         dx=self.distance_moved_x, dy=self.distance_moved_y)
                # and we test if we have finished
                if self.distance_to_move_x == self.distance_moved_x and self.distance_to_move_y == self.distance_moved_y:
                    self.is_moving = False
                    self.images[self.direction].stop()
            elif self.redraw:
                dirty_recs += self._get_game_view().clear(self.owner.pos)
                dirty_recs += self._get_game_view().draw(self.images[self.direction].getCurrentFrameSpecial(),
                                                         self.owner.pos)
                self.redraw = False
        return dirty_recs

    def need_redraw(self, value=True):
        self.redraw = value

    def _get_game_view(self):
        return self.owner.controller.view


class PlayerView:

    def __init__(self, player):
        self.player = player

    def player_surface(self):
        """
        Render the player rectangular area on the left border of the screen
        """
        pass
        #TODO: implement the player surface area