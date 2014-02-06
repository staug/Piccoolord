# -*- coding: utf-8 -*-
"""
@author staug
@version 0.1
@summary Geographical representation of the game. Contains the world, which is a set of regions.
Each region has a physical representation - the grid (with all the tiles); and a logical
representation: the list of places. Each place has also reference to the tiles for easier
lookup. Last, the tile themselves have backward links to the regions.
"""
import random
import WorldMapResources
import WorldMapView
import sys


class World():
    """ @summary The world is divided in a set of regions.
    """

    def __init__(self,
                 name,
                 num_regions,
                 min_size_region,
                 max_size_region,
                 min_number_places,
                 max_number_places):
        """
        @summary Instantiate a new World. List of params:
        @param name: string, the name of the world
        @param num_regions: int, the number of regions/levels
        @param min_size_region: (int, int) the minimum size of each region
        @param max_size_region: (int, int) the maximum size of each region
        @param min_number_places: int the minimum number of place per region
        @param max_number_places: int the maximum size per region
        """
        self.name = name
        self.regions = []
        assert num_regions > 0, "The number of regions in the world has to be >0"
        assert (0, 0) < min_size_region < max_size_region, "Error in region size (min = 0 or min>max)"
        assert 0 < min_number_places < max_number_places, "Error in number of places (min = 0 or min>max)"
        for regionNumber in range(num_regions):
            size = (random.randint(min_size_region[0], max_size_region[0]),
                    random.randint(min_size_region[1], max_size_region[1]))
            self.regions.append(Region(size,
                                       random.randint(min_number_places, max_number_places),
                                       cave_like=(random.randint(0, 0) != 0)))

    def __str__(self):
        result = "[World: " + self.name + "\n"
        for a_region in self.regions:
            result += "{\n" + str(a_region) + "}\n"
        result += "]"
        return result


class Region:
    """@summary A region/level in the world. A region has a grid and a list of places.
    """

    def __init__(self,
                 size,
                 number_places,
                 cave_like=True):
        """
        @summary Instantiate a new Region. List of params:
        @param size: (int, int) the actual size of the region
        @param number_places: int the number of places this region should contain
        """
        self.size = size
        self.grid = {}
        self.__starting_positions = []
        self.name = Place.name_generator()
        self.cave_like = cave_like
        if cave_like:
            while not self.__generate_region_cave():
                print("World "+self.name+" discarded - generating new one")
                self.name = Place.name_generator()
                pass
        else:
            self.places = []
            self.connections = {}
            self.__generate_region_map(number_places)

    def get_starting_position(self):
        """
        @return the next available starting position, and removes it from the stack
        """
        assert self.__starting_positions > 0, "No more starting positions"
        return self.__starting_positions.pop()

    def explore(self, grid_pos):
        """Flag the Tile in the grid as visible. Used by the Fog of war.
        """
        self.grid[grid_pos].set_visible(True)

    def reset_visible(self, grid_pos):
        """Reset the visible flag, but keep the explored status. Used by the Fog of war.
        """
        self.grid[grid_pos].set_visible(False)

    # TODO: add real light blocking stuff
    def block_light(self, grid_pos):
        return self.grid[grid_pos].blocking

    def __generate_region_cave(self):
        '''
        Generate a cavelike structure. Less rectangular than the previous...
        @return: True if the room was correct
        '''
        # Refer to:
        # http://www.roguebasin.com/index.php?title=Cellular_Automata_Method_for_Generating_Random_Cave-Like_Levels
        # First: we initialize the map
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                if random.randint(0, 100) <= 40:  # 40 % chance of wall
                    self.grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_WALL)
                else:
                    self.grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_BLANK)

        # First iteration:
        for iteration in range(4):
            next_gen_grid = {}
            for x in range(0, self.size[0]):
                for y in range(0, self.size[1]):
                    nb_wall = self.__nb_wall_around((x, y), 1)
                    nb_wall_2 = self.__nb_wall_around((x, y), 2)
                    if nb_wall >= 5 or nb_wall_2 <= 1:
                        next_gen_grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_WALL)
                    else:
                        next_gen_grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_BLANK)
            # copy...
            for x in range(0, self.size[0]):
                for y in range(1, self.size[1]):
                    self.grid[(x, y)] = Tile((x, y), tile_type=next_gen_grid[(x, y)].tile_type)

        # Final Tweak to smooth:
        for iteration in range(3):
            next_gen_grid = {}
            for x in range(0, self.size[0]):
                for y in range(0, self.size[1]):
                    nb_wall = self.__nb_wall_around((x, y), 1)
                    if nb_wall >= 5:
                        next_gen_grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_WALL)
                    else:
                        next_gen_grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_BLANK)
            # copy...
            for x in range(0, self.size[0]):
                for y in range(1, self.size[1]):
                    self.grid[(x, y)] = Tile((x, y), tile_type=next_gen_grid[(x, y)].tile_type)

        # Set the external wall
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                if x == 0 or y == 0 or x == self.size[0] - 1 or y == self.size[1] - 1:
                    self.grid[(x, y)] = Tile((x, y), tile_type=Tile.GRID_WALL)

        # Try to flood
        (x, y) = (0, 0)
        while self.grid[(x, y)].tile_type != Tile.GRID_BLANK:
            (x, y) = (random.randint(0, self.size[0] - 1), random.randint(0, self.size[1] - 1))
        save = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        self.__flood((x, y))
        sys.setrecursionlimit(save)

        # Final check: do we have some non connected places
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                if self.grid[(x, y)].tile_type == Tile.GRID_BLANK:
                    self.__starting_positions = []
                    return False
                elif self.grid[(x,y)].tile_type == Tile.GRID_FLOOR:
                    self.__starting_positions.append((x,y))

        random.shuffle(self.__starting_positions)
        return True

    def __flood(self, pos):
        if pos not in self.grid or self.grid[pos].tile_type == Tile.GRID_WALL or self.grid[pos].tile_type == Tile.GRID_FLOOR:
            return
        if self.grid[pos].tile_type == Tile.GRID_BLANK:
            (x, y) = pos
            self.grid[pos].tile_type = Tile.GRID_FLOOR
            self.__flood((x - 1, y))
            self.__flood((x - 1, y - 1))
            self.__flood((x - 1, y + 1))
            self.__flood((x, y - 1))
            self.__flood((x, y + 1))
            self.__flood((x + 1, y))
            self.__flood((x + 1, y - 1))
            self.__flood((x + 1, y + 1))

    def __nb_wall_around(self, pos, distance):
        result = 0
        for x in range(pos[0] - distance, pos[0] + distance + 1):
            for y in range(pos[1] - distance, pos[1] + distance + 1):
                if (x, y) not in self.grid or self.grid[(x, y)].tile_type == Tile.GRID_WALL:
                    result += 1
        return result

    def __generate_region_map(self, max_number_places):
        """
        Generate the whole map, add the deco
        """
        min_place_size = (max((int((self.size[0] / max_number_places) / 8), 5)),
                          max((int((self.size[1] / max_number_places) / 8), 5)))
        max_place_size = (max((int((self.size[0] / max_number_places) / 2), 15)),
                          max((int((self.size[1] / max_number_places) / 2), 15)))

        # First: we fill all floor with generic Tile
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                self.grid[(x, y)] = Tile((x, y))

        # Now draw the starting place and put it in the middle of the grid
        self.places.append(self.__generate_place(min_place_size, max_place_size))
        self.places[0].position = (int(self.size[0] / 2 - (self.places[0].size[0] / 2)),
                                   int(self.size[1] / 2 - (self.places[0].size[1] / 2)))
        self.__carve_place(self.places[0],
                           (int(self.size[0] / 2 - (self.places[0].size[0] / 2)),
                            int(self.size[1] / 2 - (self.places[0].size[1] / 2))))

        # Main algorithm
        while len(self.places) < max_number_places:
            # select a place next to where we will try to place the place
            neighbor_place = random.choice(self.places)
            # list all the walls of this place, select one, corners will be excluded in next function
            walls = []
            for x in range(neighbor_place.position[0] + 2, neighbor_place.position[0] + neighbor_place.size[0] - 2):
                walls.append((x, neighbor_place.position[1]))
                walls.append((x, neighbor_place.position[1] + neighbor_place.size[1] - 1))
            for y in range(neighbor_place.position[1] + 2, neighbor_place.position[1] + neighbor_place.size[1] - 2):
                walls.append((neighbor_place.position[0], y))
                walls.append((neighbor_place.position[0] + neighbor_place.size[0] - 1, y))
            cut_in_wall_position = random.choice(walls)

            # find where we cut
            direction = self.__get_cut_direction(cut_in_wall_position)
            if direction:
                # create a place if it was not a corner
                new_place = self.__generate_place(min_place_size, max_place_size)
                # and place it, with a corridor in between
                # Note: North and South are always connected with a corridor of at least 1
                #corridor_size = random.randrange(2, max(min_place_size[0], min_place_size[1]))
                # corridor_size = random.randrange(1, min(max(min_place_size[0], min_place_size[1]), 3))
                corridor_size = 1
                if direction == "NORTH":
                    new_place.position = (int(cut_in_wall_position[0] - (new_place.size[0] / 2)),
                                          int(cut_in_wall_position[1] - new_place.size[1] - corridor_size))
                elif direction == "SOUTH":
                    new_place.position = (int(cut_in_wall_position[0] - (new_place.size[0] / 2)),
                                          int(cut_in_wall_position[1] + 1 + corridor_size))
                elif direction == "EAST":
                    new_place.position = (int(cut_in_wall_position[0] + 1 + corridor_size),
                                          int(cut_in_wall_position[1] - (new_place.size[1] / 2)))
                elif direction == "WEST":
                    new_place.position = (int(cut_in_wall_position[0] - (new_place.size[0]) - corridor_size),
                                          int(cut_in_wall_position[1] - (new_place.size[1] / 2)))

                if self.__space_for_new_place(new_place):
                    self.__carve_place(new_place, new_place.position)
                    self.__connect_places(cut_in_wall_position, direction, corridor_size, new_place)
                    self.places.append(new_place)

                    neighbor_place.connections.append(new_place)
                    new_place.connections.append(neighbor_place)

        # Adding the deco
        # random.shuffle(self.places)
        # for place in self.places:
        #     if place.size[0] > 11 and place.size[1] > 11:
        #         if random.randint(0, 100) < 60:
        #             self.__deco_big_floor(place)
        #     if random.randint(0, 100) < 30:
        #         self.__deco_2x2_floor(place)
        #     if random.randint(0, 100) < 50:
        #         for i in range(0, random.randint(0, 3)):
        #             self.__deco_1x2_floor(place)
        #     if random.randint(0, 100) < 60:
        #         for i in range(0, random.randint(0, 5)):
        #             self.__deco_1x1_floor(place)
        #     for i in range(0, random.randint(0, 5)):
        #         self.__deco_1x2_wall(place)

        # Now we have finished.. We tie back all the tiles that belong to the places for easier further treatment
        for x in range(0, self.size[0]):
            for y in range(0, self.size[1]):
                current_place = self.grid[(x, y)].part_of
                if current_place:
                    current_place.tiles[(x, y)] = self.grid[(x, y)]
                    if not self.grid[(x, y)].blocking:
                        self.__starting_positions.append((x, y))
        random.shuffle(self.__starting_positions)


    def __deco_1x1_floor(self, current_place):
        if current_place.size[0] > 4 and current_place.size[1] > 4:
            x = random.randint(current_place.position[0] + 2, current_place.position[0] + current_place.size[0] - 3)
            y = random.randint(current_place.position[1] + 2, current_place.position[1] + current_place.size[1] - 3)
            if not self.grid[(x, y)].decoration:
                self.grid[(x, y)].decoration = "F1x1"
                return True
        return False

    def __deco_1x2_floor(self, current_place):
        if current_place.size[0] > 4 and current_place.size[1] > 5:
            x = random.randint(current_place.position[0] + 2, current_place.position[0] + current_place.size[0] - 3)
            y = random.randint(current_place.position[1] + 3, current_place.position[1] + current_place.size[1] - 3)
            if not self.grid[(x, y)].decoration and not self.grid[(x, y - 1)].decoration:
                self.grid[(x, y)].decoration = "F1x2S"
                self.grid[(x, y - 1)].decoration = "F1x2N"
                return True
            return False

    def __deco_1x2_wall(self, current_place):
        if current_place.size[0] > 4 and current_place.size[1] > 4:
            x = random.randint(current_place.position[0] + 2, current_place.position[0] + current_place.size[0] - 3)
            y = current_place.position[1]
            if not (not (self.grid[(x, y)].tile_type == Tile.GRID_WALLN)
                    or self.grid[(x, y)].decoration
                    or self.grid[(x, y + 1)].decoration):
                self.grid[(x, y)].decoration = "W1x2N"
                self.grid[(x, y + 1)].decoration = "W1x2S"
                return True
            return False

    def __deco_2x2_floor(self, current_place):
        if current_place.size[0] > 5 and current_place.size[1] > 5:
            x = random.randint(current_place.position[0] + 3, current_place.position[0] + current_place.size[0] - 3)
            y = random.randint(current_place.position[1] + 3, current_place.position[1] + current_place.size[1] - 3)
            if not (self.grid[(x, y)].decoration
                    or self.grid[(x, y - 1)].decoration
                    or self.grid[(x - 1, y - 1)].decoration
                    or self.grid[(x - 1, y)].decoration):
                self.grid[(x, y)].decoration = "F2x2SE"
                self.grid[(x - 1, y)].decoration = "F2x2SW"
                self.grid[(x, y - 1)].decoration = "F2x2NE"
                self.grid[(x - 1, y - 1)].decoration = "F2x2NW"
                return True
            return False

    def __deco_big_floor(self, current_place):
        """Valid for pool only... or similar!
        """
        if current_place.size[0] > 11 and current_place.size[1] > 11:
            start_x = random.randint(current_place.position[0] + 3, current_place.position[0] + 5)
            stop_x = random.randint(current_place.position[0] + current_place.size[0] - 6,
                                    current_place.position[0] + current_place.size[0] - 3)
            start_y = random.randint(current_place.position[1] + 3, current_place.position[1] + 5)
            stop_y = random.randint(current_place.position[1] + current_place.size[1] - 6,
                                    current_place.position[1] + current_place.size[1] - 3)
            for x in range(start_x, stop_x + 1):
                for y in range(start_y, stop_y + 1):
                    if self.grid[(x, y)].decoration or not self.grid[(x, y)].tile_type == Tile.GRID_FLOOR:
                        return False
                # Now we have make sure we have place, we can place the big deco
            for x in range(start_x, stop_x + 1):
                for y in range(start_y, stop_y + 1):
                    if (x, y) == (start_x, start_y):
                        self.grid[(x, y)].decoration = "BIGNW"
                    elif (x, y) == (stop_x, stop_y):
                        self.grid[(x, y)].decoration = "BIGSE"
                    elif (x, y) == (stop_x, start_y):
                        self.grid[(x, y)].decoration = "BIGNE"
                    elif (x, y) == (start_x, stop_y):
                        self.grid[(x, y)].decoration = "BIGSW"
                    elif x == start_x:
                        self.grid[(x, y)].decoration = "BIGW"
                    elif x == stop_x:
                        self.grid[(x, y)].decoration = "BIGE"
                    elif y == start_y:
                        self.grid[(x, y)].decoration = "BIGN"
                    elif y == stop_y:
                        self.grid[(x, y)].decoration = "BIGS"
                    else:
                        self.grid[(x, y)].decoration = "BIGF"
            return True

    def __generate_place(self, min_size, max_size):
        size_x = random.randint(min_size[0], max_size[0])
        size_y = random.randint(min_size[1], max_size[1])
        return Place((size_x, size_y), (0, 0))

    def __carve_place(self, place, position):
        # Place the place, i.e. set the grid tiles to the place
        (x_pos, y_pos) = position
        for x in range(x_pos, x_pos + place.size[0]):
            for y in range(y_pos, y_pos + place.size[1]):
                if (x, y) == (x_pos, y_pos):
                    self.grid[(x, y)].tile_type = Tile.GRID_CORNERNW
                elif (x, y) == (x_pos + place.size[0] - 1, y_pos + place.size[1] - 1):
                    self.grid[(x, y)].tile_type = Tile.GRID_CORNERSE
                elif (x, y) == (x_pos + place.size[0] - 1, y_pos):
                    self.grid[(x, y)].tile_type = Tile.GRID_CORNERNE
                elif (x, y) == (x_pos, y_pos + place.size[1] - 1):
                    self.grid[(x, y)].tile_type = Tile.GRID_CORNERSW
                elif x == x_pos:
                    self.grid[(x, y)].tile_type = Tile.GRID_WALLW
                elif x == x_pos + place.size[0] - 1:
                    self.grid[(x, y)].tile_type = Tile.GRID_WALLE
                elif y == y_pos:
                    self.grid[(x, y)].tile_type = Tile.GRID_WALLN
                elif y == y_pos + place.size[1] - 1:
                    self.grid[(x, y)].tile_type = Tile.GRID_WALLS
                else:
                    self.grid[(x, y)].tile_type = Tile.GRID_FLOOR
                self.grid[(x, y)].part_of = place

    def __space_for_new_place(self, place):
        # Return false if one of the part of the place is out of the grid or not blank
        for x in range(place.position[0], place.position[0] + place.size[0]):
            for y in range(place.position[1], place.position[1] + place.size[1]):
                if x < MARGIN_AROUND or x > self.size[0] - 1 - MARGIN_AROUND:
                    return False
                if y < MARGIN_AROUND or y > self.size[1] - 1 - MARGIN_AROUND:
                    return False
                if self.grid[(x, y)].tile_type != Tile.GRID_BLANK:
                    return False
        return True

    def __get_cut_direction(self, position):
        if self.grid[position].tile_type == Tile.GRID_WALLN:
            return "NORTH"
        elif self.grid[position].tile_type == Tile.GRID_WALLE:
            return "EAST"
        elif self.grid[position].tile_type == Tile.GRID_WALLS:
            return "SOUTH"
        elif self.grid[position].tile_type == Tile.GRID_WALLW:
            return "WEST"
        else:
            return None

    def __connect_places(self, cut_in_wall_position, direction, corridor_size, new_place):
        #TODO: SET THE CORRIDOR WIDTH
        corridor_width = random.randint(0, 2)
        # We pierce a hole in the nearby place
        #self.grid[cut_in_wall_position].tile_type = Tile.GRID_FLOOR
        # Note: when carving, it is more beautiful to tweak a little bit West and East...
        if direction == "NORTH":
            # we pierce the corridor
            for pos in range(0, corridor_size + 1):
                self.grid[(cut_in_wall_position[0], cut_in_wall_position[1] - pos)].tile_type = Tile.GRID_FLOOR
                self.grid[(cut_in_wall_position[0], cut_in_wall_position[1] - pos)].part_of = new_place
                # and here, we add the wall to the corridor
                self.grid[(cut_in_wall_position[0] - 1, cut_in_wall_position[1] - pos)].tile_type = Tile.GRID_WALLW
                self.grid[(cut_in_wall_position[0] - 1, cut_in_wall_position[1] - pos)].part_of = new_place
                self.grid[(cut_in_wall_position[0] + 1, cut_in_wall_position[1] - pos)].tile_type = Tile.GRID_WALLE
                self.grid[(cut_in_wall_position[0] + 1, cut_in_wall_position[1] - pos)].part_of = new_place
                # and last part, we take care of the hole and tile around the new place hole
            self.grid[
                (cut_in_wall_position[0], cut_in_wall_position[1] - 1 - corridor_size)].tile_type = Tile.GRID_FLOOR
        elif direction == "SOUTH":
            for pos in range(0, corridor_size + 1):
                self.grid[(cut_in_wall_position[0], cut_in_wall_position[1] + pos)].tile_type = Tile.GRID_FLOOR
                self.grid[(cut_in_wall_position[0], cut_in_wall_position[1] + pos)].part_of = new_place
                self.grid[(cut_in_wall_position[0] - 1, cut_in_wall_position[1] + pos)].tile_type = Tile.GRID_WALLW
                self.grid[(cut_in_wall_position[0] - 1, cut_in_wall_position[1] + pos)].part_of = new_place
                self.grid[(cut_in_wall_position[0] + 1, cut_in_wall_position[1] + pos)].tile_type = Tile.GRID_WALLE
                self.grid[(cut_in_wall_position[0] + 1, cut_in_wall_position[1] + pos)].part_of = new_place
            self.grid[
                (cut_in_wall_position[0], cut_in_wall_position[1] + 1 + corridor_size)].tile_type = Tile.GRID_FLOOR
        elif direction == "EAST":  # East and West: we carve the corridor 1 step more...
            for pos in range(0, corridor_size + 2):
                self.grid[(cut_in_wall_position[0] + pos, cut_in_wall_position[1])].tile_type = Tile.GRID_FLOOR
                self.grid[(cut_in_wall_position[0] + pos, cut_in_wall_position[1])].part_of = new_place
                self.grid[(cut_in_wall_position[0] + pos, cut_in_wall_position[1] - 1)].tile_type = Tile.GRID_WALLN
                self.grid[(cut_in_wall_position[0] + pos, cut_in_wall_position[1] - 1)].part_of = new_place
                self.grid[(cut_in_wall_position[0] + pos, cut_in_wall_position[1] + 1)].tile_type = Tile.GRID_WALLS
                self.grid[(cut_in_wall_position[0] + pos, cut_in_wall_position[1] + 1)].part_of = new_place
        elif direction == "WEST":
            for pos in range(0, corridor_size + 2):
                self.grid[(cut_in_wall_position[0] - pos, cut_in_wall_position[1])].tile_type = Tile.GRID_FLOOR
                self.grid[(cut_in_wall_position[0] - pos, cut_in_wall_position[1])].part_of = new_place
                self.grid[(cut_in_wall_position[0] - pos, cut_in_wall_position[1] - 1)].tile_type = Tile.GRID_WALLN
                self.grid[(cut_in_wall_position[0] - pos, cut_in_wall_position[1] - 1)].part_of = new_place
                self.grid[(cut_in_wall_position[0] - pos, cut_in_wall_position[1] + 1)].tile_type = Tile.GRID_WALLS
                self.grid[(cut_in_wall_position[0] - pos, cut_in_wall_position[1] + 1)].part_of = new_place

    def __str__(self):
        result = self.name + " (" + str(self.size[0]) + "x" + str(self.size[1]) + ")\n"
        for place in self.places:
            result += "\t" + str(place) + "\n"
        result += "\n\t" + "Grid:  " + str(len(self.places)) + "\n\n"
        for y in range(0, self.size[1]):
            row = ""
            for x in range(0, self.size[0]):
                row += str((self.grid[(x, y)]).tile_type)
            result += "\t\t" + row + "\n"
        return result


class Place:
    """
    A place is a logical representation. It is mainly used for its naming and
    as a way to group together tiles.
    """

    def __init__(self, size, position):
        self.name = Place.name_generator()
        self.size = size
        self.position = position
        self.tiles = {}  # reference between position and tile
        self.connections = []

    def __str__(self):
        return self.name + " (" + str(self.size[0]) + "x" + str(self.size[1]) + ")"

    @staticmethod
    def name_generator():
        part1 = random.choice(WorldMapResources.PLACE_NAME_PART1).title()
        part2 = random.choice(WorldMapResources.PLACE_NAME_PART2)
        part2 = part2[0].lower() + part2[1:]
        part3 = random.choice(WorldMapResources.PLACE_NAME_PART3).title()
        return part1 + ' ' + part2 + ' of ' + part3


class Tile():
    """The smallest localization unit. Can be a floor, wall or empty
    """

    def __init__(self,
                 position,
                 tile_type=None):
        self.position = position
        self.tile_type = tile_type
        if not tile_type:
            self.tile_type = Tile.GRID_BLANK
        self.visible = False
        self.explored = False
        self.decoration = None
        self.part_of = None

    def __str__(self):
        return "Tile at " + str(self.position)

    @property
    def blocking(self):
        return self.decoration or not (self.tile_type == Tile.GRID_FLOOR)

    def set_visible(self,
                    value):
        """
        @summary Define a tile visibility. If true, it is set explored also.
        @param value: the value to be set
        """
        self.visible = value
        if self.visible:
            self.explored = True

    GRID_BLANK = 'O'  # blank space (non-useable)
    GRID_FLOOR = 'F'  # floor tile (walkable)
    GRID_WALLN = 'N'  # wall tile facing NORTH.
    GRID_WALLE = 'E'  # wall tile facing EAST.
    GRID_WALLS = 'S'  # wall tile facing SOUTH.
    GRID_WALLW = 'W'  # wall tile facing WEST.
    GRID_CORNERNW = 'n'  # corner
    GRID_CORNERSW = 'w'  # corner
    GRID_CORNERNE = 'e'  # corner
    GRID_CORNERSE = 's'  # corner

    GRID_WALL = "W"
    GRID_FLOODED = "F"
    # Operations

# Constants only valid there
# A map level
MARGIN_AROUND = 3  # This is the space that we need to leave around the maze for good graphic

if __name__ == '__main__':
    print(Region((80, 80), 1, cave_like=True))

    # a_world = World("Test", 3, (80, 80), (120, 120), 40, 60)
    # for region in a_world.regions:
    #     view = WorldMapView.RegionView(region)
    #     view.save(region.name)