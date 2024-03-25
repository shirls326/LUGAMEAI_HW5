# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 (main, Sep 11 2023, 08:31:25) [Clang 14.0.6 ]
# Embedded file name: BaselineHero.py
# Compiled at: 2024-01-02 15:33:12
# Size of source mod 2**32: 4705 bytes
import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
from constants import *
from utils import *
from core import *
from moba2 import *

class BaselineHero(Hero):

    def __init__(self, position, orientation, world, image=AGENT, speed=SPEED, viewangle=360, hitpoints=HEROHITPOINTS, firerate=FIRERATE, bulletclass=BigBullet, dodgerate=DODGERATE, areaeffectrate=AREAEFFECTRATE, areaeffectdamage=AREAEFFECTDAMAGE):
        Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)
        self.states = [BLIdle]
        self.states += [BLHunt, BLKill]

    def start(self):
        Hero.start(self)
        self.changeState(BLIdle)


class BLIdle(State):

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.agent.stopMoving()

    def execute(self, delta=0):
        State.execute(self, delta)
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        hero = None
        for a in enemies:
            if isinstance(a, Hero):
                hero = a
                break

        if hero is not None:
            self.agent.changeState(BLHunt, hero)


class BLHunt(State):

    def parseArgs(self, args):
        self.target = args[0]

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.agent.navigateTo(self.target.getLocation())

    def execute(self, delta=0):
        State.execute(self, delta)
        hit = rayTraceWorld(self.agent.getLocation(), self.target.getLocation(), self.agent.world.getLines())
        if self.target.isAlive() == False:
            self.agent.changeState(BLIdle)
        else:
            if distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 2:
                if hit == None:
                    self.agent.changeState(BLKill, self.target)
            elif self.agent.getMoveTarget() == None:
                self.agent.navigateTo(self.target.getLocation())
        blShootAtMinions(self.agent)


class BLKill(State):

    def parseArgs(self, args):
        self.target = args[0]

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.agent.stopMoving()

    def execute(self, delta=0):
        State.execute(self, delta)
        if self.target.isAlive() == False:
            self.agent.changeState(BLIdle)
        else:
            if self.target not in self.agent.getVisible():
                self.agent.changeState(BLHunt, self.target)
            else:
                if distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE - 2:
                    self.agent.changeState(BLHunt, self.target)
                else:
                    self.agent.turnToFace(self.target.getLocation())
                    self.agent.shoot()


def blShootAtMinions(agent):
    heros = agent.getVisibleType(Hero)
    minions = agent.getVisibleType(Minion)
    target = None
    for m in heros + minions:
        if m.getTeam() != agent.getTeam() and distance(agent.getLocation(), m.getLocation()) < BIGBULLETRANGE - 2:
            target = m
            break

    if target is not None:
        if distance(agent.getLocation(), target.getLocation()) <= AREAEFFECTRANGE + target.getRadius():
            agent.areaEffect()
        else:
            agent.turnToFace(target.getLocation())
            agent.shoot()

# okay decompiling BaselineHero.pyc