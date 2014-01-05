__author__ = 'staug'
import math
import GameObjectView
import random
import GameController


class GameObject:
    def __init__(self, name, resources, pos=(0, 0), blocking=False, fighter=None, ai=None):
        self.pos = self.old_pos = pos
        self.name = name
        self.blocking = blocking
        self.resources = resources

        self.fighter = fighter
        if self.fighter:  # let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  # let the AI component know who owns it
            self.ai.owner = self

        self.view = None


    def draw(self):
        if not self.view:
            self.view = GameObjectView.GameObjectView(self.resources)
            self.view.owner = self
        self.view.draw()


    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked. Return True if move was valid.
        if self.owner.is_blocked((self.pos[0]+dx, self.pos[1]+dy)) or (dx == dy == 0):
            return False
        self.old_pos = self.pos
        self.pos = (self.pos[0]+dx, self.pos[1]+dy)
        if not self.view:
            self.view = GameObjectView.GameObjectView(self.resources)
            self.view.owner = self
        self.view.move()
        return True

    def move_to(self, new_pos):
        #Used by the AI only. new_pos should be valid
        assert(not self.owner.is_blocked(new_pos))
        self.old_pos = self.pos
        self.pos = new_pos
        if not self.view:
            self.view = GameObjectView.GameObjectView(self.resources)
            self.view.owner = self
        self.view.move()


    def distance_to(self, other):
        #return the distance to another object
        dx = other.pos[0] - self.pos[0]
        dy = other.pos[1] - self.pos[1]
        return math.sqrt(dx ** 2 + dy ** 2)


class ArtificialIntelligence:

    def __init__(self):
        pass

    def take_turn(self):
        print("WARNING - TAKE TURN NOT IMPLEMENTED")


class FollowerAI(ArtificialIntelligence):

    def __init__(self, ticker):
        self.ticker = ticker
        self.speed = 1
        self.ticker.schedule_turn(self.speed, self)

    def move_towards(self, target_pos):
        dx = target_pos[0] - self.owner.pos[0]
        dy = target_pos[1] - self.owner.pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        success = self.owner.move(dx, dy)
        tries = 0
        while not success or tries > 5:
            move = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
            success = self.owner.move(move[0], move[1])
            tries += 1

    def take_turn(self):
        player = self.owner.owner.get_player()
        self.move_towards(player.pos)
        self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn
