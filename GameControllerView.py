__author__ = 'staug'
import pygame
import WorldMapView
import GameResources

class GameControllerView:

    def __init__(self, owner):
        self.owner = owner
        self.region_view = WorldMapView.RegionView(owner.region).view
        self.original_region_view = self.region_view.copy()

        self.camera = Camera(self)
        self.explorer_map = ExplorerMap(self)

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

class Camera:

    def __init__(self, owner):
        self.owner = owner
        self.camera_rect = pygame.Rect((0, 0), GameResources.CAMERA_WINDOW_SIZE)

    def is_displayable(self, tile_pos):
        """
        return True if the tile position can be displayed on the screen
        """
        return self.camera_rect.contains(GameControllerView.get_grid_rect(tile_pos))

    def move(self, tile_dx, tile_dy):
        self.camera_rect.move_ip(tile_dx * GameResources.TILE_WIDTH, tile_dy * GameResources.TILE_HEIGHT)
        self._normalize_rect()

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
                # TODO: set back to explored when tests are finished
                #if self.owner.owner.region.grid[(x,y)].explored:
                if self.owner.owner.region.grid[(x,y)].tile_type == 'F':
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

if __name__ == '__main__':
    pygame.init()

