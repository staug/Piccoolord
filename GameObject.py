__author__ = 'staug'
import math
import GameObjectView
import random
import GameController
import GameResources
import GameUtil

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

    def __init__(self, attributes=None, work=None, origin=None):
        self.original_attributes = {}
        self.vanquished_enemy = []
        self.destiny_points = random.randint(0, 3)

        if not attributes:
            self.roll_attributes()
        else:
            names = ["COU", "INT", "CHA", "AD", "FO"]
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
        names = ["COU", "INT", "CHA", "AD", "FO"]
        for att in names:
            self.original_attributes[att] = random.randint(1, 6) + 7

        self.original_attributes["AT"] = 8
        self.original_attributes["PRD"] = 10

        self.original_attributes["HP"] = 20
        self.original_attributes["MP"] = 30


    def define_possible_origin(self):
        possible_origins = []
        names = ["COU", "INT", "CHA", "AD", "FO"]
        origin_limits = {
            "Humain": {},
            "Barbare": {
                "COU": {"MIN": 12}, "FO": {"MIN": 13},
            },
            "Nain": {
                "COU": {"MIN": 11}, "FO": {"MIN": 12},
            },
            "Haut Elfe": {
                "INT": {"MIN": 11}, "CHA": {"MIN": 12}, "AD": {"MIN": 12}, "FO": {"MAX": 12},
            },
            "Demi Elfe": {
                "CHA": {"MIN": 10}, "AD": {"MIN": 11},
            },
            "Elfe Sylvain": {
                "CHA": {"MIN": 12}, "AD": {"MIN": 10}, "FO": {"MAX": 11},
            },
            "Elfe Noir": {
                "INT": {"MIN": 12}, "AD": {"MIN": 13},
            },
            "Orque": {
                "INT": {"MAX": 8}, "CHA": {"MAX": 10}, "FO": {"MIN": 12},
            },
            "Demi Orque": {
                "INT": {"MAX": 10}, "AD": {"MAX": 11}, "FO": {"MIN": 12},
            },
            "Gobelin": {
                "COU": {"MAX": 10}, "INT": {"MAX": 10}, "CHA": {"MAX": 8}, "FO": {"MAX": 9},
            },
            "Ogre": {
                "INT": {"MAX": 9}, "CHA": {"MAX": 10}, "AD": {"MAX": 11}, "FO": {"MIN": 13},
            },
            "Hobbit": {
                "COU": {"MIN": 12}, "INT": {"MIN": 10}, "FO": {"MAX": 10},
            },
            "Gnome": {
                "INT": {"MIN": 10}, "AD": {"MIN": 13}, "FO": {"MAX": 8},
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
        names = ["COU", "INT", "CHA", "AD", "FO"]
        work_limits = {
            "Guerrier": {
                "COU": {"MIN": 12}, "FO": {"MIN": 12},
            },
            "Ninja": {
                "AD": {"MIN": 13},
            },
            "Voleur": {
                "AD": {"MIN": 12},
            },
            "Pretre": {
                "CHA": {"MIN": 12},
            },
            "Mage": {
                "INT": {"MIN": 12},
            },
            "Paladin": {
                "COU": {"MIN": 12}, "INT": {"MIN": 10}, "CHA": {"MIN": 11}, "FO": {"MIN": 9},
            },
            "Ranger": {
                "CHA": {"MIN": 10}, "AD": {"MIN": 10},
            },
            "Menestrel": {
                "CHA": {"MIN": 12}, "AD": {"MIN": 11},
            },
            "Marchand": {
                "INT": {"MIN": 12}, "CHA": {"MIN": 11},
            },
            "Ingenieur": {
                "AD": {"MIN": 11},
            },
            "Pirate": {
                "COU": {"MIN": 11}, "AD": {"MIN": 11},
            },
            "Bourgeois": {
                "INT": {"MIN": 10}, "CHA": {"MIN": 11},
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

    @property
    def pi(self):
        # TODO: define impact points!
        return (3, 5)

    def take_damage(self, value):
        self.hp -= value

    def fight(self, opponent):
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

class BasicMonsterAI(ArtificialIntelligence):

    def __init__(self, ticker, speed=1, target_strategy=None, attack_distance=1):
        self.ticker = ticker
        self.speed = 1
        self.ticker.schedule_turn(self.speed, self)
        if target_strategy:
            self.target_strategy = target_strategy
        else:
            self.target_strategy = self.find_closest_enemy
        self.attack_distance = attack_distance

    def move_towards(self, target_pos):
        # TODO: every x turn, compute A* algo
        # except if distance is < x...
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

    def find_closest_player(self):
        controller = self.owner.owner
        closest_player= controller.player
        distance = self.owner.distance_to(closest_player)
        for player in controller.player_party:
            if self.owner.distance_to(player.owner) < distance:
                closest_player = player
        return closest_player.owner

    def find_weakest_enemy(self):
        pass

    def take_turn(self):
        # find the closest enemy
        target = self.target_strategy()
        if self.owner.distance_to(target) < self.attack_distance:
            self.owner.fighter.fight(target.fighter)
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
