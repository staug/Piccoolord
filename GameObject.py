__author__ = 'staug'
import math
import GameObjectView
import random
import GameController
import GameResources
import GameUtil
import types

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
            self.player.object = self

        self.fighter = fighter
        if self.fighter:  # let the fighter component know who owns it
            self.fighter.object = self
            if self.player:
                self.fighter.replicate_player_attributes(self.player)

        self.ai = ai
        if self.ai:  # let the AI component know who owns it
            self.ai.object = self



    def draw(self):
        if not self.view:
            self.view = GameObjectView.GameObjectView(self.resources)
            self.view.owner = self
        self.view.draw()

    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked. Return True if move was valid.
        if self.controller.is_blocked((self.pos[0]+dx, self.pos[1]+dy)) or (dx == dy == 0):
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
        assert(not self.controller.is_blocked(new_pos))
        self.old_pos = self.pos
        self.pos = new_pos
        if not self.view:
            self.view = GameObjectView.GameObjectView(self.resources)
            self.view.owner = self
        self.view.move()

    def distance_to(self, other_object):
        #return the distance to another object
        dx = other_object.pos[0] - self.pos[0]
        dy = other_object.pos[1] - self.pos[1]
        return math.sqrt(dx ** 2 + dy ** 2)


class Player:

    def __init__(self, attributes=None, work=None, origin=None):
        self.original_attributes = {}
        self.vanquished_enemy = []
        self.destiny_points = random.randint(0, 3)

        if not attributes:
            self.roll_attributes()
        else:
            names = ["cou", "int", "cha", "ad", "fo"]
            for att in names:
                self.original_attributes[att] = attributes[att]

        if work:
            self.work = work
        else:
            self.work = random.choice(self.define_possible_work())

        if origin:
            self.work = work
        else:
            self.work = random.choice(self.define_possible_work())


    def roll_attributes(self):
        names = ["cou", "int", "cha", "ad", "fo"]
        for att in names:
            self.original_attributes[att] = random.randint(1, 6) + 7

        self.original_attributes["at"] = 8
        self.original_attributes["prd"] = 10

        self.original_attributes["hp"] = 20
        self.original_attributes["mp"] = 30


    def define_possible_origin(self):
        possible_origins = []
        names = ["cou", "int", "cha", "ad", "fo"]
        origin_limits = {
            "Humain": {},
            "Barbare": {
                "cou": {"MIN": 12}, "fo": {"MIN": 13},
            },
            "Nain": {
                "cou": {"MIN": 11}, "fo": {"MIN": 12},
            },
            "Haut Elfe": {
                "int": {"MIN": 11}, "cha": {"MIN": 12}, "ad": {"MIN": 12}, "fo": {"MAX": 12},
            },
            "Demi Elfe": {
                "cha": {"MIN": 10}, "ad": {"MIN": 11},
            },
            "Elfe Sylvain": {
                "cha": {"MIN": 12}, "ad": {"MIN": 10}, "fo": {"MAX": 11},
            },
            "Elfe Noir": {
                "int": {"MIN": 12}, "ad": {"MIN": 13},
            },
            "Orque": {
                "int": {"MAX": 8}, "cha": {"MAX": 10}, "fo": {"MIN": 12},
            },
            "Demi Orque": {
                "int": {"MAX": 10}, "ad": {"MAX": 11}, "fo": {"MIN": 12},
            },
            "Gobelin": {
                "cou": {"MAX": 10}, "int": {"MAX": 10}, "cha": {"MAX": 8}, "fo": {"MAX": 9},
            },
            "Ogre": {
                "int": {"MAX": 9}, "cha": {"MAX": 10}, "ad": {"MAX": 11}, "fo": {"MIN": 13},
            },
            "Hobbit": {
                "cou": {"MIN": 12}, "int": {"MIN": 10}, "fo": {"MAX": 10},
            },
            "Gnome": {
                "int": {"MIN": 10}, "ad": {"MIN": 13}, "fo": {"MAX": 8},
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

    def define_possible_work(self):
        # TODO: race prevents some work!
        possible_works = []
        names = ["cou", "int", "cha", "ad", "fo"]
        work_limits = {
            "Guerrier": {
                "cou": {"MIN": 12}, "fo": {"MIN": 12},
            },
            "Ninja": {
                "ad": {"MIN": 13},
            },
            "Voleur": {
                "ad": {"MIN": 12},
            },
            "Pretre": {
                "cha": {"MIN": 12},
            },
            "Mage": {
                "int": {"MIN": 12},
            },
            "Paladin": {
                "cou": {"MIN": 12}, "int": {"MIN": 10}, "cha": {"MIN": 11}, "fo": {"MIN": 9},
            },
            "Ranger": {
                "cha": {"MIN": 10}, "ad": {"MIN": 10},
            },
            "Menestrel": {
                "cha": {"MIN": 12}, "ad": {"MIN": 11},
            },
            "Marchand": {
                "int": {"MIN": 12}, "cha": {"MIN": 11},
            },
            "Ingenieur": {
                "ad": {"MIN": 11},
            },
            "Pirate": {
                "cou": {"MIN": 11}, "ad": {"MIN": 11},
            },
            "Bourgeois": {
                "int": {"MIN": 10}, "cha": {"MIN": 11},
            },
        }
        for work in work_limits.keys():
            ok = True
            for att in names:
                if att in work_limits[work].keys():
                    limit = work_limits[work][att]
                    if "MIN" in limit.keys():
                        if self.original_attributes[att] < limit["MIN"]:
                            ok = False
                    elif self.original_attributes[att] > limit["MAX"]:
                            ok = False
            if ok:
                possible_works.append(work)
        if len(possible_works) == 0:
            possible_works.append("Aucun")
        return possible_works


class Fighter:

    def __init__(self, resources=None):
        self.original_attributes = {}
        if resources:
            self.original_attributes = resources
            self.hp = self.original_attributes["hp"]
            self.mp = self.original_attributes["mp"]

    def replicate_player_attributes(self, player):
        self.original_attributes = player.original_attributes
        self.hp = self.original_attributes["hp"]
        self.mp = self.original_attributes["mp"]

    @property
    def cou(self):
        return self.original_attributes["cou"]

    @property
    def int(self):
        return self.original_attributes["int"]

    @property
    def cha(self):
        return self.original_attributes["cha"]

    @property
    def ad(self):
        return self.original_attributes["ad"]

    @property
    def fo(self):
        return self.original_attributes["fo"]

    @property
    def at(self):
        return self.original_attributes["at"]

    @property
    def prd(self):
        return self.original_attributes["prd"]

    @property
    def mag_phy(self):
        return (self.int + self.ad) / 2

    @property
    def mag_psy(self):
        return (self.int + self.cha) / 2

    @property
    def mag_res(self):
        return (self.int + self.cou + self.fo) / 3

    @property
    def pi(self):
        # TODO: define impact points!
        return (3, 5)

    def take_damage(self, value):
        self.hp -= value

    def fight(self, opponent):
        print("{} attacks {}".format(self.object.name, opponent.object.name))
        # TODO: courage fight first, critical success and failure; Remove printing
        at_test_result = GameUtil.pass_test(self.at)
        print("EVAL: " + at_test_result)
        if GameResources.SUCCESS in at_test_result:
            # Success for attack, try to pary
            print("PARADE")
            prd_test_result = GameUtil.pass_test(opponent.prd)
            print("EVAL: " + prd_test_result)
            if GameResources.FAILURE in prd_test_result:
                # Opponent did not manage to parry
                opponent.take_damage(random.randint(self.pi[0], self.pi[1]))
                print("HP = {}".format(opponent.hp))

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
        # TODO: every x turn, compute A* algo
        # except if distance is < x...
        dx = target_pos[0] - self.object.pos[0]
        dy = target_pos[1] - self.object.pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        success = self.object.move(dx, dy)
        tries = 0
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(possible_moves)
        while not (success or tries > 3):
            a_move = possible_moves[tries]
            success = self.object.move(a_move[0], a_move[1])
            tries += 1

    def take_turn(self):
        player = self.object.controller.player
        self.move_towards(player.pos)
        self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn

class BasicMonsterAI(ArtificialIntelligence):

    def __init__(self, ticker, speed=1, target_strategy=None, attack_distance=1):
        self.ticker = ticker
        self.speed = 1
        self.ticker.schedule_turn(self.speed, self)
        if target_strategy:
            self.target_strategy = target_strategy
        else:
            self.target_strategy = GameResources.TARGET_STRATEGY_CLOSEST
        self.attack_distance = attack_distance

    def move_towards(self, target_pos):
        # TODO: every x turn, compute A* algo
        # except if distance is < x...
        dx = target_pos[0] - self.object.pos[0]
        dy = target_pos[1] - self.object.pos[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        success = self.object.move(dx, dy)
        tries = 0
        possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(possible_moves)
        while not (success or tries > 3):
            a_move = possible_moves[tries]
            success = self.object.move(a_move[0], a_move[1])
            tries += 1

    def find_closest_player(self):
        controller = self.object.controller
        closest_player = controller.player
        distance = self.object.distance_to(closest_player)
        for player in controller.player_party:
            if self.object.distance_to(player) < distance:
                closest_player = player
        return closest_player

    def find_weakest_player(self):
        pass

    def take_turn(self):
        # find the closest enemy
        if self.target_strategy == GameResources.TARGET_STRATEGY_CLOSEST:
            target = self.find_closest_player()
        elif self.target_strategy == GameResources.TARGET_STRATEGY_WEAKEST:
            target = self.find_weakest_player()
        if self.object.distance_to(target) <= self.attack_distance:
            self.object.fighter.fight(target.fighter)
        else:
            self.move_towards(target.pos)
        self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn


if __name__ == '__main__':
    playerA = Player()
    fighterA = Fighter()
    fighterA.replicate_player_attributes(playerA)
    print("Attributes: {} - Origin: {} - Work: {}".format(
        playerA.original_attributes,
        playerA.define_possible_origin(),
        playerA.define_possible_work()))
    playerB = Player()
    fighterB = Fighter()
    fighterB.replicate_player_attributes(playerB)
    print("Attributes: {} - Origin: {} - Work: {}".format(
        playerB.original_attributes,
        playerB.define_possible_origin(),
        playerB.define_possible_work()))
    while fighterA.hp > 0 and fighterB.hp > 0:
        print("Attaque A")
        fighterA.fight(fighterB)
        print("Attaque B")
        fighterB.fight(fighterA)
