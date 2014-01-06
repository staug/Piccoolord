__author__ = 'staug'
import math
import GameObjectView
import random
import GameController


class GameObject:
    def __init__(self,
                 name,
                 resources,
                 pos=(0, 0),
                 blocking=False,
                 fighter=None,
                 ai=None,
                 player=None):
        self.pos = self.old_pos = pos
        self.name = name
        self.blocking = blocking
        self.resources = resources
        self.view = None

        self.player = player
        if self.player:
            self.player.owner = self

        self.fighter = fighter
        if self.fighter:  # let the fighter component know who owns it
            self.fighter.owner = self
            if self.player:
                self.fighter.replicate_player_attributes(self.player)

        self.ai = ai
        if self.ai:  # let the AI component know who owns it
            self.ai.owner = self



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


class Player:

    def __init__(self, automatic=True):
        self.original_attributes = {}
        self.vanquished_enemy = []
        if automatic:
            self.roll_attributes()

    def roll_attributes(self):
        names = ["COU", "INT", "CHA", "AD", "FO"]
        for att in names:
            self.original_attributes[att] = random.randint(1, 6) + 7
        self.destiny_points = random.randint(0, 3)

        self.original_attributes["AT"] = 8
        self.original_attributes["PRD"] = 10

        self.original_attributes["HP"] = 10
        self.original_attributes["MP"] = 10


    def define_possible_origin(self):
        # TODO
        possible_origins = []
        names = ["COU", "INT", "CHA", "AD", "FO"]
        origin_limits = {
            "Humain": {},
            "Barbare": {
                "COU": {"MIN": 12},
                "FO": {"MIN": 13},
            },
            "Nain": {
                "COU": {"MIN": 11},
                "FO": {"MIN": 12},
            },
            "Haut Elfe": {
                "INT": {"MIN": 11},
                "CHA": {"MIN": 12},
                "AD": {"MIN": 12},
                "FO": {"MAX": 12},
            },
            "Demi Elfe": {
                "CHA": {"MIN": 10},
                "AD": {"MIN": 11},
            },
            "Elfe Sylvain": {
                "CHA": {"MIN": 12},
                "AD": {"MIN": 10},
                "FO": {"MAX": 11},
            },
            "Elfe Noir": {
                "INT": {"MIN": 12},
                "AD": {"MIN": 13},
            },
        }
        for origin in origin_limits.keys():
            ok = True
            for att in names:
                if att in origin_limits[origin].keys():
                    limit = origin_limits[origin][att]
                    if "MIN" in limit.keys():
                        if self.original_attributes[att] < limit["MIN"]:
                            ok = False
                    elif self.original_attributes[att] > limit["MAX"]:
                            ok = False
            if ok:
                possible_origins.append(origin)
        return possible_origins


class Fighter:

    def __init__(self, resources=None):
        self.original_attributes = {}
        if resources:
            self.original_attributes = resources
        self.hp = self.original_attributes["HP"]
        self.mp = self.original_attributes["MP"]

    def replicate_player_attributes(self, player):
        self.original_attributes = player.original_attributes
        self.hp = self.original_attributes["HP"]
        self.mp = self.original_attributes["MP"]

    @property
    def cou(self):
        return self.original_attributes["COU"]

    @property
    def int(self):
        return self.original_attributes["INT"]

    @property
    def cha(self):
        return self.original_attributes["CHA"]

    @property
    def ad(self):
        return self.original_attributes["AD"]

    @property
    def fo(self):
        return self.original_attributes["FO"]

    @property
    def at(self):
        return self.original_attributes["AT"]

    @property
    def prd(self):
        return self.original_attributes["PRD"]

    @property
    def mag_phy(self):
        return (self.int + self.ad) / 2

    @property
    def mag_psy(self):
        return (self.int + self.cha) / 2

    @property
    def mag_res(self):
        return (self.int + self.cou + self.fo) / 3


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
        player = self.owner.owner.player
        self.move_towards(player.pos)
        self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn



if __name__ == '__main__':
    test = Player()
    print("Attributes: {} - Origin: {}".format(test.original_attributes, test.define_possible_origin()))