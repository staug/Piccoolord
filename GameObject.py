__author__ = 'staug'
import math
import GameObjectView


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
        #move by the given amount, if the destination is not blocked
        if not self.owner.region.grid[(self.pos[0]+dx, self.pos[1]+dy)].blocking\
            and (dx != 0 or dy != 0):
            self.old_pos = self.pos
            self.pos = (self.pos[0]+dx, self.pos[1]+dy)
            if not self.view:
                self.view = GameObjectView.GameObjectView(self.resources)
                self.view.owner = self
            self.view.move()

