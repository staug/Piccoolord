__author__ = 'staug'
import random
import GameResources
import heapq


def pass_test(property_tested,
              random_value_max=20,
              critic_success_value=1,
              critic_failure_value=1):
        value = random.randint(1, random_value_max)
        if value <= critic_success_value:
            return GameResources.CRITIC_SUCCESS
        elif value <= property_tested:
            return GameResources.SUCCESS
        elif value > random_value_max - critic_failure_value:
            return GameResources.CRITIC_FAILURE
        else:
            return GameResources.FAILURE


class AStar(object):
    """
    Implementation of the A* Algo
    from http://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/
    The end result is in the path variable, which is empty if no path is found
    """
    class Cell(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.parent = None
            self.g = self.h = self.f = 0

    def __init__(self, start, end, blocks, region_dimension, search_dimension=None):
        """
        Initiate an A* research on a grid. The end result is in the path variable, which is empty if no path is found
        The path variable doesn't contain the start and end variable
        @param start: the position of the place to start
        @param end: the end position
        @param blocks: a list of (x,y) that represents blocking parts
        @param region_dimension: the maximum size of the grid
        @param search_dimension: if specified, will setup a rectangle centered on the start position to minimize the
        search.
        """
        self.op = []
        heapq.heapify(self.op)
        self.cl = set()
        self.cells = {}
        if search_dimension:
            (self.grid_width, self.grid_height) = search_dimension
            for x in range(max(0, start[0] - self.grid_width / 2),
                           min(region_dimension[0], start[0] + self.grid_width / 2)):
                for y in range(max(0, start[1] - self.grid_height / 2),
                               min(region_dimension[1], start[1] + self.grid_height / 2)):
                    if (x, y) not in blocks:
                        self.cells[(x, y)] = AStar.Cell(x, y)
        else:
            (self.grid_width, self.grid_height) = region_dimension
            for x in range(region_dimension[0]):
                for y in range(region_dimension[1]):
                    if (x, y) not in blocks:
                        self.cells[(x, y)] = AStar.Cell(x, y)
        self.start = self.end = None
        if end in self.cells:
            self.start = self.cells[start]
            self.end = self.cells[end]
        self.path = []
        self._process()

    def _get_heuristic(self, cell):
        """
        Compute the heuristic value H for a cell: distance between
        this cell and the ending cell multiply by 10.
        @param cell
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def _get_adjacent_cells(self, cell):
        """
        Returns adjacent cells to a cell. Clockwise starting
        from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list
        """
        cells = []
        keys = [(cell.x+1, cell.y), (cell.x, cell.y-1), (cell.x-1, cell.y),(cell.x, cell.y+1)]
        for a_key in keys:
            if a_key in self.cells:
                cells.append(self.cells[a_key])
        return cells

    def _update_cell(self, adj, cell):
        """
        Update adjacent cell
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self._get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def _process(self):
        # add starting cell to open heap queue
        if self.start:
            heapq.heappush(self.op, (self.start.f, self.start))
        while len(self.op):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.op)
            # add cell to closed list so we don't process it twice
            self.cl.add(cell)
            # if ending cell, display found path
            if cell is self.end:
                self._build_path()
                break
            # get adjacent cells for cell
            adj_cells = self._get_adjacent_cells(cell)
            for c in adj_cells:
                #if c.reachable and c not in self.cl:
                if c not in self.cl:
                    if (c.f, c) in self.op:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found for this adj
                        # cell.
                        if c.g > cell.g + 10:
                            self._update_cell(c, cell)
                    else:
                        self._update_cell(c, cell)
                        # add adj cell to open list
                        heapq.heappush(self.op, (c.f, c))

    def _build_path(self):
        """
        Set in the variable
        """
        cell = self.end
        while cell.parent is not self.start:
            cell = cell.parent
            self.path.insert(0, cell)