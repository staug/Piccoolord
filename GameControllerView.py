__author__ = 'staug'
import pygame
import WorldMapView
import GameResources
import copy

class GameControllerView:

    def __init__(self, owner):
        self.owner = owner
        self.region_view = WorldMapView.RegionView(owner.region).view
        self.original_region_view = self.region_view.copy()

        self.camera = Camera(self)
        self.explorer_map = ExplorerMap(self)

        self.shadowed_position = set()

    @staticmethod
    def get_grid_rect(pos, pix_width=GameResources.TILE_WIDTH, pix_height=GameResources.TILE_HEIGHT, dx=0, dy=0):
        return pygame.Rect((pos[0]*GameResources.TILE_WIDTH + dx, pos[1]*GameResources.TILE_HEIGHT + dy), (pix_width, pix_height))

    def _get_subsurface(self, pos,
                       pix_width=GameResources.TILE_WIDTH, pix_height=GameResources.TILE_HEIGHT, dx=0, dy=0, from_original=False):
        if from_original:
            return self.original_region_view.subsurface(GameControllerView.get_grid_rect(pos, pix_width, pix_height, dx, dy))
        else:
            return self.region_view.subsurface(GameControllerView.get_grid_rect(pos, pix_width, pix_height, dx, dy))

    def clear(self, grid_pos, dimension=(GameResources.TILE_WIDTH, GameResources.TILE_HEIGHT), dx=0, dy=0):
        """Copy from the original the rect mentioned. Return the rect"""
        rect = GameControllerView.get_grid_rect(grid_pos, dimension[0], dimension[1], dx, dy)
        self.region_view.blit(self._get_subsurface(grid_pos, dimension[0], dimension[1], dx, dy, from_original=True),
                              dest=rect)
        return rect

    def draw(self, surface_to_draw, grid_pos,
             dimension=(GameResources.TILE_WIDTH, GameResources.TILE_HEIGHT), dx=0, dy=0):
        """blit the surface to the game image with transparency"""
        rect = GameControllerView.get_grid_rect(grid_pos, dimension[0], dimension[1], dx, dy)
        #self.region_view.blit(surface_to_draw, dest = rect, special_flags=pygame.BLEND_RGBA_ADD)
        self.region_view.blit(surface_to_draw, dest = rect)
        return rect

    def is_displayable(self, tile_pos):
        return self.camera.is_displayable(tile_pos)

    def update_fog_of_war(self, grid_pos, radius):
        FieldOfView.compute(grid_pos, self.owner.region.size, radius,
                            self.owner.region.explore, self.owner.region.block_light, self.owner.region.reset_visible)

        # Now apply a mask on it
        # TODO: optimize the fog of war masking!
        dark = pygame.Surface((GameResources.TILE_WIDTH, GameResources.TILE_HEIGHT), 0, 32)
        dark.fill(GameResources.GAME_BG_COLOR)
        shadow = pygame.Surface((GameResources.TILE_WIDTH, GameResources.TILE_HEIGHT), 0, 32)
        shadow.fill(GameResources.GAME_BG_COLOR)
        shadow.set_alpha(125, pygame.RLEACCEL)
        for x in range(self.owner.region.size[0]):
            for y in range(self.owner.region.size[1]):
                if self.camera.is_displayable((x, y)):
                    if self.owner.region.grid[(x, y)].visible:
                        self._get_subsurface((x, y)).blit(self._get_subsurface((x, y), from_original=True), (0, 0))
                        self.shadowed_position.discard((x, y))
                    elif self.owner.region.grid[(x,y)].explored and (x,y) not in self.shadowed_position:
                        # other possible option; we could blit the visible tile, then the shadow
                        # this could be used if we want to do bitmasking...
                        self._get_subsurface((x, y)).blit(shadow, (0, 0))
                        self.shadowed_position.add((x,y))
                    elif (x,y) not in self.shadowed_position:
                        self._get_subsurface((x, y)).blit(dark, (0, 0))


class Camera:

    def __init__(self, owner):
        self.owner = owner
        self.camera_rect = pygame.Rect((0, 0), GameResources.CAMERA_WINDOW_SIZE)

    def is_displayable(self, tile_pos):
        """
        return True if the tile position can be displayed on the screen
        """
        return self.camera_rect.colliderect(GameControllerView.get_grid_rect(tile_pos))

    def move(self, tile_dx, tile_dy):
        self.camera_rect.move_ip(tile_dx * GameResources.TILE_WIDTH, tile_dy * GameResources.TILE_HEIGHT)
        self._normalize_rect()

    def close_edge(self, tile_pos):
        """ Test if the tile pos is close to the camera edge. return True if the Camera should move """
        subset_camera = pygame.Rect((0, 0),
                                    (GameResources.CAMERA_WINDOW_SIZE[0] / 2, GameResources.CAMERA_WINDOW_SIZE[1] / 2))
        subset_camera.center = self.camera_rect.center
        return not subset_camera.contains(GameControllerView.get_grid_rect(tile_pos))

    def center(self, pos):
        center_x = pos[0] * GameResources.TILE_WIDTH
        center_y = pos[1] * GameResources.TILE_HEIGHT
        self.camera_rect.center = (center_x, center_y)
        self._normalize_rect()

    def _normalize_rect(self):
        if not self.owner.region_view.get_rect().contains(self.camera_rect):
            self.camera_rect.left = max(0, self.camera_rect.left)
            self.camera_rect.top = max(0, self.camera_rect.top)
            self.camera_rect.right = min(self.owner.region_view.get_rect().right, self.camera_rect.right)
            self.camera_rect.bottom = min(self.owner.region_view.get_rect().bottom, self.camera_rect.bottom)


class ExplorerMap:

    def __init__(self, owner, tile_size = 4):
        self.owner = owner
        self.tile_size = tile_size
        self.center((self.owner.owner.region.size[0] / 2, self.owner.owner.region.size[1] / 2))

    def _build_image(self):
        size = self.owner.owner.region.size
        map_surface = pygame.Surface((int(size[0] * self.tile_size),
                                      int(size[1] * self.tile_size)), pygame.SRCALPHA, 32)
        #map_surface.fill(GameResources.MAP_BG_COLOR)
        for x in range(0, size[0]):
            for y in range(0, size[1]):
                if self.owner.owner.region.grid[(x,y)].visible:
                    map_surface.fill(GameResources.MAP_VISIBLE_COLOR,
                                     rect=pygame.Rect((x * self.tile_size, y * self.tile_size),
                                                      (self.tile_size, self.tile_size)))
                elif self.owner.owner.region.grid[(x,y)].explored:
                    map_surface.fill(GameResources.MAP_EXPLORED_COLOR,
                                     rect=pygame.Rect((x * self.tile_size, y * self.tile_size),
                                                      (self.tile_size, self.tile_size)))
        return map_surface

    def center(self, pos):
        center_x = pos[0] * self.tile_size
        center_y = pos[1] * self.tile_size
        self.current_center = (center_x, center_y)

    @property
    def surface(self):
        map_surface = self._build_image()
        window_surface = pygame.Surface((GameResources.MAP_WINDOW_SIZE))
        rect = pygame.Rect((max(self.current_center[0] - GameResources.MAP_WINDOW_SIZE[0] / 2, 0),
                           max(self.current_center[1] - GameResources.MAP_WINDOW_SIZE[1] / 2, 0)),
                           GameResources.MAP_WINDOW_SIZE)
        window_surface.blit(map_surface, (0, 0), area=rect, special_flags=pygame.BLEND_RGBA_ADD)
        return window_surface


class FieldOfView:
    """
    Author:         Aaron MacDonald
    Date:           June 14, 2007

    Description:    An implementation of the precise permissive field
                    of view algorithm for use in tile-based games.
                    Based on the algorithm presented at
                    http://roguebasin.roguelikedevelopment.org/
                      index.php?title=
                      Precise_Permissive_Field_of_View.

    You are free to use or modify this code as long as this notice is
    included.
    This code is released without warranty.
    """

    def __init__(self):
        pass

    @staticmethod
    def compute(start_grid_pos, map_size, radius, funcVisitTile, funcTileBlocked, funcResetVisitTile):
        """
            Determines which coordinates on a 2D grid are visible from a
            particular coordinate.

            start_grid_pos:         The (x, y) coordinate on the grid that
                                    is the centre of view.

            map_size:               The maximum extents of the grid.  The
                                    minimum extents are assumed to be both
                                    zero.

            radius:                 How far the field of view may extend
                                    in either direction along the x and y
                                    axis.

            funcVisitTile:          User function that takes two integers
                                    representing an (x, y) coordinate.  Is
                                    used to "visit" visible coordinates.

            funcTileBlocked:        User function that takes two integers
                                    representing an (x, y) coordinate.
                                    Returns True if the coordinate blocks
                                    sight to coordinates "behind" it.

            funcResetVisitTile:     User function that reset the visible tile """
        (start_x, start_y) = start_grid_pos
        (map_width, map_height) = map_size

        visited = set() # Keep track of what tiles have been visited so
                        # that no tile will be visited twice.


        # Ge the dimensions of the actual field of view, making
        # sure not to go off the map or beyond the radius.

        if start_x < radius:
            minExtentX = start_x
        else:
            minExtentX = radius

        if map_width - start_x - 1 < radius:
            maxExtentX = map_width - start_x - 1
        else:
            maxExtentX = radius

        if start_y < radius:
            minExtentY = start_y
        else:
            minExtentY = radius

        if map_height - start_y - 1 < radius:
            maxExtentY = map_height - start_y - 1
        else:
            maxExtentY = radius

        #TODO: optimize below to visit only the stuff at the limit of the radius?
        for x in range(map_width):
            for y in range(map_height):
                funcResetVisitTile((x, y))

        # Will always see the centre.
        funcVisitTile((start_x, start_y))
        visited.add((start_x, start_y))


        # Northeast quadrant
        FieldOfView.__checkQuadrant(visited, start_x, start_y, 1, 1, \
          maxExtentX, maxExtentY, \
          funcVisitTile, funcTileBlocked)

        # Southeast quadrant
        FieldOfView.__checkQuadrant(visited, start_x, start_y, 1, -1, \
          maxExtentX, minExtentY, \
          funcVisitTile, funcTileBlocked)

        # Southwest quadrant
        FieldOfView.__checkQuadrant(visited, start_x, start_y, -1, -1, \
          minExtentX, minExtentY, \
          funcVisitTile, funcTileBlocked)

        # Northwest quadrant
        FieldOfView.__checkQuadrant(visited, start_x, start_y, -1, 1, \
          minExtentX, maxExtentY, \
          funcVisitTile, funcTileBlocked)

    #-------------------------------------------------------------

    class __Line(object):
            def __init__(self, xi, yi, xf, yf):
                self.xi = xi
                self.yi = yi
                self.xf = xf
                self.yf = yf

            dx = property(fget = lambda self: self.xf - self.xi)
            dy = property(fget = lambda self: self.yf - self.yi)

            def pBelow(self, x, y):
                return self.relativeSlope(x, y) > 0

            def pBelowOrCollinear(self, x, y):
                return self.relativeSlope(x, y) >= 0

            def pAbove(self, x, y):
                return self.relativeSlope(x, y) < 0

            def pAboveOrCollinear(self, x, y):
                return self.relativeSlope(x, y) <= 0

            def pCollinear(self, x, y):
                return self.relativeSlope(x, y) == 0

            def lineCollinear(self, line):
                return self.pCollinear(line.xi, line.yi) \
                  and self.pCollinear(line.xf, line.yf)

            def relativeSlope(self, x, y):
                return (self.dy * (self.xf - x)) \
                  - (self.dx * (self.yf - y))

    class __ViewBump:
        def __init__(self, x, y, parent):
            self.x = x
            self.y = y
            self.parent = parent

    class __View:
        def __init__(self, shallowLine, steepLine):
            self.shallowLine = shallowLine
            self.steepLine = steepLine

            self.shallowBump = None
            self.steepBump = None

    @staticmethod
    def __checkQuadrant(visited, startX, startY, dx, dy, extentX, extentY, funcVisitTile, funcTileBlocked):
        activeViews = []

        shallowLine = FieldOfView.__Line(0, 1, extentX, 0)
        steepLine = FieldOfView.__Line(1, 0, 0, extentY)

        activeViews.append( FieldOfView.__View(shallowLine, steepLine) )
        viewIndex = 0

        # Visit the tiles diagonally and going outwards
        #
        # .
        # .
        # .           .
        # 9        .
        # 5  8  .
        # 2  4  7
        # @  1  3  6  .  .  .
        maxI = extentX + extentY
        i = 1
        while i != maxI + 1 and len(activeViews) > 0:
            if 0 > i - extentX:
                startJ = 0
            else:
                startJ = i - extentX

            if i < extentY:
                maxJ = i
            else:
                maxJ = extentY

            j = startJ
            while j != maxJ + 1 and viewIndex < len(activeViews):
                x = i - j
                y = j
                FieldOfView.__visitCoord(visited, startX, startY, x, y, dx, dy, \
                  viewIndex, activeViews, \
                  funcVisitTile, funcTileBlocked)

                j += 1

            i += 1

    @staticmethod
    def __visitCoord(visited, startX, startY, x, y, dx, dy, viewIndex, \
      activeViews, funcVisitTile, funcTileBlocked):
        # The top left and bottom right corners of the current coordinate.
        topLeft = (x, y + 1)
        bottomRight = (x + 1, y)

        while viewIndex < len(activeViews) \
          and activeViews[viewIndex].steepLine.pBelowOrCollinear( \
           bottomRight[0], bottomRight[1]):
            # The current coordinate is above the current view and is
            # ignored.  The steeper fields may need it though.
            viewIndex += 1

        if viewIndex == len(activeViews) \
          or activeViews[viewIndex].shallowLine.pAboveOrCollinear( \
           topLeft[0], topLeft[1]):
            # Either the current coordinate is above all of the fields
            # or it is below all of the fields.
            return

        # It is now known that the current coordinate is between the steep
        # and shallow lines of the current view.

        isBlocked = False

        # The real quadrant coordinates
        realX = x * dx
        realY = y * dy

        if (startX + realX, startY + realY) not in visited:
            visited.add((startX + realX, startY + realY))
            funcVisitTile((startX + realX, startY + realY))

        isBlocked = funcTileBlocked((startX + realX, startY + realY))

        if not isBlocked:
            # The current coordinate does not block sight and therefore
            # has no effect on the view.
            return

        if activeViews[viewIndex].shallowLine.pAbove( \
           bottomRight[0], bottomRight[1]) \
          and activeViews[viewIndex].steepLine.pBelow( \
           topLeft[0], topLeft[1]):
            # The current coordinate is intersected by both lines in the
            # current view.  The view is completely blocked.
            del activeViews[viewIndex]
        elif activeViews[viewIndex].shallowLine.pAbove( \
          bottomRight[0], bottomRight[1]):
            # The current coordinate is intersected by the shallow line of
            # the current view.  The shallow line needs to be raised.
            FieldOfView.__addShallowBump(topLeft[0], topLeft[1], \
              activeViews, viewIndex)
            FieldOfView.__check_view(activeViews, viewIndex)
        elif activeViews[viewIndex].steepLine.pBelow( \
          topLeft[0], topLeft[1]):
            # The current coordinate is intersected by the steep line of
            # the current view.  The steep line needs to be lowered.
            FieldOfView.__addSteepBump(bottomRight[0], bottomRight[1], activeViews, \
              viewIndex)
            FieldOfView.__check_view(activeViews, viewIndex)
        else:
            # The current coordinate is completely between the two lines
            # of the current view.  Split the current view into two views
            # above and below the current coordinate.

            shallowViewIndex = viewIndex
            viewIndex += 1
            steepViewIndex = viewIndex

            activeViews.insert(shallowViewIndex, copy.deepcopy(activeViews[shallowViewIndex]))

            FieldOfView.__addSteepBump(bottomRight[0], bottomRight[1], \
              activeViews, shallowViewIndex)
            if not FieldOfView.__check_view(activeViews, shallowViewIndex):
                viewIndex -= 1
                steepViewIndex -= 1

            FieldOfView.__addShallowBump(topLeft[0], topLeft[1], activeViews, \
              steepViewIndex)
            FieldOfView.__check_view(activeViews, steepViewIndex)

    @staticmethod
    def __addShallowBump(x, y, activeViews, viewIndex):
        activeViews[viewIndex].shallowLine.xf = x
        activeViews[viewIndex].shallowLine.yf = y

        activeViews[viewIndex].shallowBump = FieldOfView.__ViewBump(x, y, \
          activeViews[viewIndex].shallowBump)

        curBump = activeViews[viewIndex].steepBump
        while curBump is not None:
            if activeViews[viewIndex].shallowLine.pAbove( \
              curBump.x, curBump.y):
                activeViews[viewIndex].shallowLine.xi = curBump.x
                activeViews[viewIndex].shallowLine.yi = curBump.y

            curBump = curBump.parent

    @staticmethod
    def __addSteepBump(x, y, activeViews, viewIndex):
        activeViews[viewIndex].steepLine.xf = x
        activeViews[viewIndex].steepLine.yf = y

        activeViews[viewIndex].steepBump = FieldOfView.__ViewBump(x, y, \
          activeViews[viewIndex].steepBump)

        curBump = activeViews[viewIndex].shallowBump
        while curBump is not None:
            if activeViews[viewIndex].steepLine.pBelow( \
              curBump.x, curBump.y):
                activeViews[viewIndex].steepLine.xi = curBump.x
                activeViews[viewIndex].steepLine.yi = curBump.y

            curBump = curBump.parent

    @staticmethod
    def __check_view(activeViews, viewIndex):
        """
            Removes the view in activeViews at index viewIndex if
                - The two lines are coolinear
                - The lines pass through either extremity
        """

        shallowLine = activeViews[viewIndex].shallowLine
        steepLine = activeViews[viewIndex].steepLine

        if shallowLine.lineCollinear(steepLine) and (shallowLine.pCollinear(0, 1) or shallowLine.pCollinear(1, 0)):
            del activeViews[viewIndex]
            return False
        else:
            return True

if __name__ == '__main__':
    pygame.init()

