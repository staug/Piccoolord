__author__ = 'staug'

import WorldMapLogic
import pygame
import GameResources
import random


class View:
        
    TILE_WIDTH = GameResources.TILE_WIDTH
    TILE_HEIGHT = GameResources.TILE_HEIGHT

class RegionView(View):
    """
    The view for the original regions
    """
    def __init__(self, region):
        self.owner = region
        self.view = pygame.Surface((self.owner.size[0] * self.TILE_WIDTH,
                                    self.owner.size[1] * self.TILE_HEIGHT),
                                   pygame.SRCALPHA, 32)
        self.__build_view()

    def __build_view(self):
        SOURCE_FILE = pygame.image.load('./resources/img/tile/caveTileset.png').convert_alpha()
        SOURCE_FILE2 = pygame.image.load('./resources/img/tile/tileset.png').convert_alpha()
        FLOOR_LIST = [
            SOURCE_FILE2.subsurface(pygame.Rect((8 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((9 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((10 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((11 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((12 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((13 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((14 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
            SOURCE_FILE2.subsurface(pygame.Rect((15 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))
        ]
        # Note, in the future many image dict depending on type: rocky, woody...
        # start with rocky
        IMAGES_DICT = {
            WorldMapLogic.Tile.GRID_WALLN: [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 8 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            #GRID_WALLN: [SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 2 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            WorldMapLogic.Tile.GRID_WALLE: [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 2 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            WorldMapLogic.Tile.GRID_WALLW: [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 1 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            # Links - only if needed
            "GRID_LINK1": [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            #"GRID_LINK1": [SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 1 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK2": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK3": [SOURCE_FILE.subsurface(pygame.Rect((1 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            #"GRID_LINK3": [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 0 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK4": [SOURCE_FILE.subsurface(pygame.Rect((1 * self.TILE_WIDTH, 3 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK5": [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                           SOURCE_FILE.subsurface(pygame.Rect((1 * self.TILE_WIDTH, 3 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            #"GRID_LINK5": [SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 1 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK6": [SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 3 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK8": [SOURCE_FILE.subsurface(pygame.Rect((2 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK9": [SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            #"GRID_LINK9": [SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 3 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK10": [SOURCE_FILE.subsurface(pygame.Rect((2 * self.TILE_WIDTH, 8 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "GRID_LINK12": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 3 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            # Decoration - Floor
            "DECO_F1x1": [SOURCE_FILE.subsurface(pygame.Rect((6 * self.TILE_WIDTH, 13 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((2 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 6 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((6 * self.TILE_WIDTH, 14 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((5 * self.TILE_WIDTH, 15 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_F1x2N": [SOURCE_FILE.subsurface(pygame.Rect((5 * self.TILE_WIDTH, 13 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                           SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 14 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_F1x2S": [SOURCE_FILE.subsurface(pygame.Rect((5 * self.TILE_WIDTH, 14 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                           SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 15 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_F2x2NW": [SOURCE_FILE.subsurface(pygame.Rect((6 * self.TILE_WIDTH, 15 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_F2x2NE": [SOURCE_FILE.subsurface(pygame.Rect((7 * self.TILE_WIDTH, 15 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_F2x2SW": [SOURCE_FILE.subsurface(pygame.Rect((6 * self.TILE_WIDTH, 16 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_F2x2SE": [SOURCE_FILE.subsurface(pygame.Rect((7 * self.TILE_WIDTH, 16 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGNW": [SOURCE_FILE.subsurface(pygame.Rect((1 * self.TILE_WIDTH, 10 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGN": [SOURCE_FILE.subsurface(pygame.Rect((2 * self.TILE_WIDTH, 10 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 13 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGNE": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 10 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGW": [SOURCE_FILE.subsurface(pygame.Rect((1 * self.TILE_WIDTH, 11 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                          SOURCE_FILE.subsurface(pygame.Rect((0 * self.TILE_WIDTH, 12 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGF": [SOURCE_FILE.subsurface(pygame.Rect((2 * self.TILE_WIDTH, 11 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGE": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 11 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGSW": [SOURCE_FILE.subsurface(pygame.Rect((1 * self.TILE_WIDTH, 12 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGS": [SOURCE_FILE.subsurface(pygame.Rect((2 * self.TILE_WIDTH, 12 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_BIGSE": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 12 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            # Decoration - Wall
            "DECO_W1x2N": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 7 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                           SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 8 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))],
            "DECO_W1x2S": [SOURCE_FILE.subsurface(pygame.Rect((3 * self.TILE_WIDTH, 8 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT))),
                           SOURCE_FILE.subsurface(pygame.Rect((4 * self.TILE_WIDTH, 9 * self.TILE_HEIGHT), (self.TILE_WIDTH, self.TILE_HEIGHT)))]
        }

        self.view.fill(GameResources.GAME_BG_COLOR)

        currentImageDictionary = IMAGES_DICT

        # go over rooms
        for place in (self.owner.places):
            floorImage = random.choice(FLOOR_LIST)
            indexDecoF1X2 = indexDecoF2X2 = indexDecoW1X2 = -1
            if "DECO_F1x2S" in currentImageDictionary:
                indexDecoF1X2 = random.randint(0, len(currentImageDictionary["DECO_F1x2S"]) - 1)  # Var for big deco
            if "DECO_W1x2S" in currentImageDictionary:
                indexDecoW1X2 = random.randint(0, len(currentImageDictionary["DECO_W1x2S"]) - 1)  # Var for big deco
            if "DECO_F2x2SE" in currentImageDictionary:
                indexDecoF2X2 = random.randint(0, len(currentImageDictionary["DECO_F2x2SE"]) - 1)

            for (x, y) in place.tiles.keys():
                gridType = self.owner.grid[(x, y)].tile_type
                if gridType in currentImageDictionary or gridType == WorldMapLogic.Tile.GRID_FLOOR:
                    # Layer 1: the Floor
                    if gridType == WorldMapLogic.Tile.GRID_FLOOR:
                        self.view.blit(floorImage, (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                    else:
                        for image in currentImageDictionary[gridType]:
                            self.view.blit(image, (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                        # Layer 2: the link between tiles
                    if gridType == WorldMapLogic.Tile.GRID_FLOOR:
                        linkImageRef = "GRID_LINK" + str(self.__compute_graphical_weight(self.owner, (x, y)))
                        if linkImageRef in currentImageDictionary:
                            for linkImage in currentImageDictionary[linkImageRef]:
                                self.view.blit(linkImage, (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                        # Layer 3: the deco
                    if self.owner.grid[(x, y)].decoration:
                        decoRef = "DECO_" + self.owner.grid[(x, y)].decoration
                        if decoRef in currentImageDictionary:
                            if "F1x1" in decoRef:  # Small deco: typically there may be multiple choice
                                self.view.blit(random.choice(currentImageDictionary[decoRef]),
                                                        (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                            elif "F1x2" in decoRef:  # Multi tile deco: they need to be the same across the room
                                self.view.blit(currentImageDictionary[decoRef][indexDecoF1X2],
                                                        (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                            elif "W1x2" in decoRef:
                                self.view.blit(currentImageDictionary[decoRef][indexDecoW1X2],
                                                        (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                            elif "F2x2" in decoRef:
                                self.view.blit(currentImageDictionary[decoRef][indexDecoF2X2],
                                                        (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))
                            else:  # This is for very big deco, like pool
                                self.view.blit(random.choice(currentImageDictionary[decoRef]),
                                                        (x * self.TILE_WIDTH, y * self.TILE_HEIGHT))

    def save(self, name):
        pygame.image.save(self.view, name + ".png")

    def __compute_graphical_weight(self, level_map, pos):
        (x, y) = pos
        return RegionView.weight(level_map.grid[(x, y - 1)]) * 1 +\
               RegionView.weight(level_map.grid[(x + 1, y)]) * 2 +\
               RegionView.weight(level_map.grid[(x, y + 1)]) * 4 +\
               RegionView.weight(level_map.grid[(x - 1, y)]) * 8

    @staticmethod
    def weight(tile):
        if not tile.part_of:
            return 0
        if tile.tile_type == WorldMapLogic.Tile.GRID_FLOOR:
            return 0
        return 1