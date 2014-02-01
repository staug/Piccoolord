# -*- coding: utf-8 -*-
# __author__ = 'staug'
import math
import GameObjectView
import random
import GameResources
import GameUtil
import ast


class GameObject:
    def __init__(self,
                 name,
                 resources,
                 pos=(0, 0),
                 blocking=False,
                 fighter=None,
                 ai=None,
                 player=None,
                 item=None,
                 equipment = None):
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

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.object = self

        self.equipment = equipment
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.object = self
            #there must be an Item component for the Equipment component to work properly
            self.item = Item(equipment.resources)
            self.item.object = self

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

    def __str__(self):
        result = self.name
        if self.fighter:
            result = result + ", [" + str(self.fighter) + "]"
        if self.player:
            result = result + ", [" + str(self.player) + "]"
        return result


class Player:

    def __init__(self, attributes=None, work=None, origin=None, destiny_points=None, xp=None):
        self.original_attributes = {}
        self.vanquished_enemy = []

        if destiny_points:
            self.destiny_points = destiny_points
        else:
            self.destiny_points = random.randint(0, 3)
        if xp:
            self.xp = xp
        else:
            self.xp = 0

        if not attributes:
            self.roll_attributes()
        else:
            names = [GameResources.ATTRIBUTE_COURAGE,
                     GameResources.ATTRIBUTE_INTELLIGENCE,
                     GameResources.ATTRIBUTE_CHARISME,
                     GameResources.ATTRIBUTE_ADRESSE,
                     GameResources.ATTRIBUTE_FORCE]
            for att in names:
                self.original_attributes[att] = attributes[att]
            self.destiny_points = self.original_attributes['Destiny']
            self.xp = self.original_attributes['xp']

        if work:
            self.work = work
        else:
            self.work = random.choice(self.define_possible_work())

        if origin:
            self.origin = origin
        else:
            self.origin = random.choice(self.define_possible_origin())

    @property
    def max_carry_value(self):
        return self.object.fighter.fo * 10

    def roll_attributes(self):
        names = [GameResources.ATTRIBUTE_COURAGE,
                 GameResources.ATTRIBUTE_INTELLIGENCE,
                 GameResources.ATTRIBUTE_CHARISME,
                 GameResources.ATTRIBUTE_ADRESSE,
                 GameResources.ATTRIBUTE_FORCE]
        for att in names:
            self.original_attributes[att] = random.randint(1, 6) + 7

        self.original_attributes[GameResources.ATTRIBUTE_ATTAQUE] = 14
        self.original_attributes[GameResources.ATTRIBUTE_PARADE] = 15

        self.original_attributes["hp"] = 20
        self.original_attributes["mp"] = 30

    def define_possible_origin(self):
        possible_origins = []
        names = [GameResources.ATTRIBUTE_COURAGE, GameResources.ATTRIBUTE_INTELLIGENCE,
                 GameResources.ATTRIBUTE_CHARISME, GameResources.ATTRIBUTE_ADRESSE, GameResources.ATTRIBUTE_FORCE]
        origin_limits = {
            "Humain": {},
            "Barbare": {
                GameResources.ATTRIBUTE_COURAGE: {"MIN": 12}, GameResources.ATTRIBUTE_FORCE: {"MIN": 13},
            },
            "Nain": {
                GameResources.ATTRIBUTE_COURAGE: {"MIN": 11}, GameResources.ATTRIBUTE_FORCE: {"MIN": 12},
            },
            "Haut Elfe": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 11}, GameResources.ATTRIBUTE_CHARISME: {"MIN": 12},
                GameResources.ATTRIBUTE_ADRESSE: {"MIN": 12}, GameResources.ATTRIBUTE_FORCE: {"MAX": 12},
            },
            "Demi Elfe": {
                GameResources.ATTRIBUTE_CHARISME: {"MIN": 10}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 11},
            },
            "Elfe Sylvain": {
                GameResources.ATTRIBUTE_CHARISME: {"MIN": 12}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 10},
                GameResources.ATTRIBUTE_FORCE: {"MAX": 11},
            },
            "Elfe Noir": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 12}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 13},
            },
            "Orque": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MAX": 8}, GameResources.ATTRIBUTE_CHARISME: {"MAX": 10},
                GameResources.ATTRIBUTE_FORCE: {"MIN": 12},
            },
            "Demi Orque": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MAX": 10}, GameResources.ATTRIBUTE_ADRESSE: {"MAX": 11},
                GameResources.ATTRIBUTE_FORCE: {"MIN": 12},
            },
            "Gobelin": {
                GameResources.ATTRIBUTE_COURAGE: {"MAX": 10}, GameResources.ATTRIBUTE_INTELLIGENCE: {"MAX": 10},
                GameResources.ATTRIBUTE_CHARISME: {"MAX": 8}, GameResources.ATTRIBUTE_FORCE: {"MAX": 9},
            },
            "Ogre": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MAX": 9}, GameResources.ATTRIBUTE_CHARISME: {"MAX": 10},
                GameResources.ATTRIBUTE_ADRESSE: {"MAX": 11}, GameResources.ATTRIBUTE_FORCE: {"MIN": 13},
            },
            "Hobbit": {
                GameResources.ATTRIBUTE_COURAGE: {"MIN": 12}, GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 10},
                GameResources.ATTRIBUTE_FORCE: {"MAX": 10},
            },
            "Gnome": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 10}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 13},
                GameResources.ATTRIBUTE_FORCE: {"MAX": 8},
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
        names = [GameResources.ATTRIBUTE_COURAGE, GameResources.ATTRIBUTE_INTELLIGENCE,
                 GameResources.ATTRIBUTE_CHARISME, GameResources.ATTRIBUTE_ADRESSE, GameResources.ATTRIBUTE_FORCE]
        work_limits = {
            "Guerrier": {
                GameResources.ATTRIBUTE_COURAGE: {"MIN": 12}, GameResources.ATTRIBUTE_FORCE: {"MIN": 12},
            },
            "Ninja": {
                GameResources.ATTRIBUTE_ADRESSE: {"MIN": 13},
            },
            "Voleur": {
                GameResources.ATTRIBUTE_ADRESSE: {"MIN": 12},
            },
            "Pretre": {
                GameResources.ATTRIBUTE_CHARISME: {"MIN": 12},
            },
            "Mage": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 12},
            },
            "Paladin": {
                GameResources.ATTRIBUTE_COURAGE: {"MIN": 12}, GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 10},
                GameResources.ATTRIBUTE_CHARISME: {"MIN": 11}, GameResources.ATTRIBUTE_FORCE: {"MIN": 9},
            },
            "Ranger": {
                GameResources.ATTRIBUTE_CHARISME: {"MIN": 10}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 10},
            },
            "Menestrel": {
                GameResources.ATTRIBUTE_CHARISME: {"MIN": 12}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 11},
            },
            "Marchand": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 12}, GameResources.ATTRIBUTE_CHARISME: {"MIN": 11},
            },
            "Ingenieur": {
                GameResources.ATTRIBUTE_ADRESSE: {"MIN": 11},
            },
            "Pirate": {
                GameResources.ATTRIBUTE_COURAGE: {"MIN": 11}, GameResources.ATTRIBUTE_ADRESSE: {"MIN": 11},
            },
            "Bourgeois": {
                GameResources.ATTRIBUTE_INTELLIGENCE: {"MIN": 10}, GameResources.ATTRIBUTE_CHARISME: {"MIN": 11},
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

    def __str__(self):
        return "XP={}, Destiné={}, Origine={}, Travail={}".format(
            self.xp, self.destiny_points, self.origin, self.work
        )


class Fighter:

    def __init__(self, resources=None):
        self.original_attributes = {}
        if resources:
            self.original_attributes = resources
            self.hp = int(self.original_attributes["hp"])
            self.mp = int(self.original_attributes["mp"])
            if "xp" in self.original_attributes:
                self.xp = int(self.original_attributes["xp"])
        # Fighter specific properties
        self.max_pary_per_turn = 1
        self.pary_this_turn = 0
        self.max_attack_per_turn = 1
        self.attack_this_turn = 0
        # Inventory specifics
        # Todo: put proper max weight
        self.inventory = Inventory(10)

    def replicate_player_attributes(self, player):
        self.original_attributes = player.original_attributes
        self.hp = self.original_attributes["hp"]
        self.mp = self.original_attributes["mp"]

    def reset_pary(self):
        """
        "Reset" the number of parades. This is done by substracting the parade max value; that way, for critical failure
         we can go beyond the max_pary_per_turn variable.
        @return: None
        """
        self.pary_this_turn -= self.max_pary_per_turn

    def reset_attack(self):
        self.attack_this_turn -= self.max_attack_per_turn

    @property
    def cou(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_COURAGE) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_COURAGE])

    @property
    def int(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_INTELLIGENCE) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_INTELLIGENCE])

    @property
    def cha(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_CHARISME) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_CHARISME])

    @property
    def ad(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_ADRESSE) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_ADRESSE])

    @property
    def fo(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_FORCE) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_FORCE])

    @property
    def at(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_ATTAQUE) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_ATTAQUE])

    @property
    def prd(self):
        return self.inventory.get_bonus(GameResources.ATTRIBUTE_PARADE) +\
               int(self.original_attributes[GameResources.ATTRIBUTE_PARADE])

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

    def take_damage(self, value, additional_bonus=0):
        self.hp -= random.randint(value[0], value[1])
        self.hp -= additional_bonus

    def death(self, player_component=None):
        if not player_component:
            # TODO: add player death
            #transform it into a nasty corpse! it doesn't block, can't be
            #attacked and doesn't move
            self.object.view.die()
            self.object.blocking = False
            self.object.ai = self.object.fighter = None
            self.object.name = "Restes de " + self.object.name

    def __str__(self):
        return "HP={}, COU={}, INT={}, CHA={}, FO={}, AT={}, PRD={}".format(
            self.hp, self.cou, self.int, self.cha, self.fo, self.at, self.prd
        )

    def fight(self, fighter_opponent):
        """
        Main entry for combat.
        Principle: at this stage the enemies are already ordered by courage.
        We simply test if the one who attacks has any attack left, make an attack (if possible),
        and test if the opponent is dead. If it is, we change the XP.
        @param fighter_opponent: The other enemy
        @return: None
        """
        print_resource = self.object.controller.text_display[GameResources.TEXT_FIGHT]
        print_resource.ADD_TEXT = "{} tent une attaque contre {} - Attaque = {}, parade opposant = {}".format(
            self.object.name, fighter_opponent.object.name, self.at, fighter_opponent.prd)

        if self.attack_this_turn < self.max_attack_per_turn:
            self._fight_round(fighter_opponent, print_resource)
        else:
            print_resource.ADD_TEXT = "{} ne peut plus attaquer à ce tour.".format(self.object.name)

        if fighter_opponent.hp <= 0:
            if self.object.player and fighter_opponent.xp:
                self.object.player.xp += fighter_opponent.xp
            fighter_opponent.death(player_component=fighter_opponent.object.player)

    def _fight_round(self, fighter_opponent, print_resource):
        # TODO: enhance critical success effects and failure

        at_test_result = GameUtil.pass_test(self.at)
        print_resource.ADD_TEXT = "Résultat jet attaque {}".format(at_test_result)
        self.attack_this_turn += 1

        if GameResources.CRITIC_SUCCESS in at_test_result:
            fighter_opponent.take_damage(self.pi, additional_bonus=random.randint(0, 5))  # no parry
        elif GameResources.CRITIC_FAILURE in at_test_result:
            self.attack_this_turn += self.max_attack_per_turn # we lose one round...
            self.pary_this_turn += self.max_pary_per_turn # we lose one round...
        elif GameResources.SUCCESS in at_test_result:
            # Success for attack, try to pary
            if fighter_opponent.pary_this_turn < fighter_opponent.max_pary_per_turn:
                prd_test_result = GameUtil.pass_test(fighter_opponent.prd)
                print_resource.ADD_TEXT = "Résultat jet parade {}".format(prd_test_result)
                fighter_opponent.pary_this_turn += 1
                if GameResources.CRITIC_SUCCESS in prd_test_result:
                    self.attack_this_turn += self.max_attack_per_turn # we lose one round...
                    self.pary_this_turn += self.max_pary_per_turn # we lose one round...
                elif GameResources.CRITIC_FAILURE in prd_test_result:
                    fighter_opponent.attack_this_turn += fighter_opponent.max_attack_per_turn # opponent loses one round...
                    fighter_opponent.pary_this_turn += fighter_opponent.max_pary_per_turn # opponent loses one round...
                elif GameResources.FAILURE in prd_test_result:
                    # Opponent did not manage to parry
                    fighter_opponent.take_damage(self.pi)

            else:
                print_resource.ADD_TEXT = "{} ne peut plus parer à ce tour.".format(fighter_opponent.object.name)




class ArtificialIntelligence:

    def __init__(self):
        pass

    def take_turn(self):
        print("WARNING - TAKE TURN NOT IMPLEMENTED")

    def __lt__(self, other):
        if self.object and self.object.fighter and other.object and other.object.fighter:
            return self.object.fighter.cou < other.object.fighter.cou
        return True

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
        self.object.fighter.reset_pary()
        self.object.fighter.reset_attack()
        player = self.object.controller.player
        self.move_towards(player.pos)
        self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn



class HumanPlayerAI(ArtificialIntelligence):

    def __init__(self, ticker):
        self.ticker = ticker
        self.speed = 1
        self.ticker.schedule_turn(self.speed, self)

    def take_turn(self):
        self.object.fighter.reset_pary()
        self.object.fighter.reset_attack()

        self.object.controller.scene.player_took_action = False
        (dx, dy) = (self.object.controller.scene.dx, self.object.controller.scene.dy)
        if dx == dy == 0:
            self.ticker.schedule_turn(0, self)
        else:
            monster_at_destination = self.object.controller.get_monster_at((self.object.pos[0]+dx, self.object.pos[1]+dy))
            if monster_at_destination:
                self.object.fighter.fight(monster_at_destination.fighter)
                self.object.controller.scene.player_took_action = True
            elif self.object.controller.player.move(dx, dy):
                # todo: adapt the field of view
                self.object.controller.view.update_fog_of_war(self.object.pos, 3)
                self.object.controller.scene.player_took_action = True
            else:
                self.ticker.schedule_turn(0, self)

        if self.object.controller.scene.player_took_action:
            self.ticker.schedule_turn(self.speed, self)
            self.ticker.schedule_turn(0, self)


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
                distance = self.object.distance_to(player)
        return closest_player

    def find_weakest_player(self):
        controller = self.object.controller
        weakest_player = controller.player
        for player in controller.player_party:
            if player.hp < weakest_player.hp:
                weakest_player = player
        return weakest_player

    def take_turn(self):
        if self.object.fighter: # Make sure we are not dead
            self.object.fighter.reset_pary()
            self.object.fighter.reset_attack()

            # locate enemy
            target = None
            if self.target_strategy == GameResources.TARGET_STRATEGY_CLOSEST:
                target = self.find_closest_player()
            elif self.target_strategy == GameResources.TARGET_STRATEGY_WEAKEST:
                target = self.find_weakest_player()

            if self.object.distance_to(target) <= self.attack_distance:
                if self.object.fighter:
                    self.object.fighter.fight(target.fighter)
                    if self.object.fighter: # if we are not dead...
                        self.ticker.schedule_turn(self.speed, self)  # schedule next turn
            else:
                self.move_towards(target.pos)
                self.ticker.schedule_turn(self.speed, self)     # and schedule the next turn


class Inventory:
    """ The inventory characteristics - limitations, max weight...
    """
    def __init__(self, max_weight):
        self.inventory = []

    def get_equipped_in_slot(self, slot):  #returns the equipment in a slot, or None if it's empty
        for obj in self.inventory:
            if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
                return obj.equipment
        return None

    def get_all_equipped(self):  #returns a list of equipped items
        equipped_list = []
        for obj in self.inventory:
            if obj.equipment and obj.equipment.is_equipped:
                equipped_list.append(obj.equipment)
        return equipped_list

    @property
    def weight(self):
        return sum(obj.item.weight for obj in self.inventory)

    def append(self, item_object):
        self.inventory.append(item_object)

    def remove(self, item_object):
        self.inventory.remove(item_object)

    def equipment_compatible(self, equipment):
        # Todo: add equipment incompatibilities
        return True

    def get_bonus(self, type_of_bonus):
        return sum(equipment.get_bonus(type_of_bonus) for equipment in self.get_all_equipped())


class Item:

    def __init__(self, resources):
        self.resources = resources
        self.weight = 0
        self.use_function = None
        if "weight" in self.resources:
            self.weight = int(self.resources["weight"])
        if "use_function" in self.resources:
            self.use_function = self.resources["use_function"]
        self.max_use_number = -1  # Infinity by convention
        if "max_use_number" in self.resources:
            self.max_use_number = int(self.resources["max_use_number"])
        self.nb_use = 0
        self.inventory = None

    def pick_up(self):
        # add to the current player's inventory and remove from the map
        inventory = self.object.controller.player.fighter.inventory
        print_resource = self.object.controller.text_display[GameResources.TEXT_DIALOGUE]
        if inventory.weight + self.weight > self.object.controller.player.player.max_carry_value:
            print_resource.ADD_TEXT = "Vous portez déjà {}. Cet objet est trop lourd ({}) " \
                                      "pour votre capacité {}".format(inventory.weight,
                                                                      self.weight,
                                                                      inventory.max_weight)
        else:
            inventory.append(self.object)
            self.inventory = inventory
            print_resource.ADD_TEXT = "Vous ramassez un(e) {}".format(self.object.name)
            self.object.controller.remove_object(self.object)

            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.object.equipment
            if equipment and inventory.equipment_compatible(equipment):
                if inventory.get_equipped_in_slot(equipment.slot) is None:
                    equipment.equip()

    def drop(self):
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.object.equipment:
            self.object.equipment.dequip()

        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        self.object.controller.append(self.object)
        self.inventory.remove(self.object)
        self.object.pos = self.object.controller.player.pos
        self.object.controller.text_display[GameResources.TEXT_DIALOGUE].ADD_TEXT = \
            "Vous laissez tomber un(e) {}".format(self.object.name)

    def use(self):
        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.object.equipment:
            self.object.equipment.toggle_equip()
            return

        #just call the "use_function" if it is defined
        if self.use_function is None or (self.max_use_number != -1 and self.nb_use >= self.max_use_number):
            self.object.controller.text_display[GameResources.TEXT_DIALOGUE].ADD_TEXT = \
                "{} ne peut pas être utilisé(e)".format(self.object.name)
        else:
            if self.use_function() != 'cancelled':
                self.nb_use += 1
                if self.nb_use >= self.max_use_number:
                    self.inventory.remove(self.object)  #destroy after use, unless it was cancelled for some reason


class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, resources):
        self.resources = resources
        self.modifier = {}
        if "modifier" in self.resources:
            self.modifier = ast.literal_eval(self.resources["modifier"])

        self.slot = "NONE"
        if "slot" in resources:
            self.slot = resources["slot"]

        self.is_equipped = False

    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):
        #if the slot is already being used, dequip whatever is there first
        old_equipment = self.object.controller.player.fighter.inventory.get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        self.object.controller.text_display[GameResources.TEXT_DIALOGUE].ADD_TEXT =\
            self.object.name + ' équipé(e) sur ' + self.slot + '.'

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped:
            return
        self.is_equipped = False
        self.object.controller.text_display[GameResources.TEXT_DIALOGUE].ADD_TEXT =\
            self.object.name + ' enlevé(e) de ' + self.slot + '.'

    def get_bonus(self, type_of_bonus):
        if self.is_equipped:
            if type_of_bonus in self.modifier:
                return int(self.modifier[type_of_bonus])
        return 0

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
