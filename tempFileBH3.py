# uncompyle6 version 3.9.1
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.11.5 (main, Sep 11 2023, 08:31:25) [Clang 14.0.6 ]
# Embedded file name: BaselineHero3.py
# Compiled at: 2024-01-02 15:33:12
# Size of source mod 2**32: 6989 bytes
import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
from constants import *
from utils import *
from core import *
from moba2 import *

class BaselineHero3(Hero):

    def __init__(self, position, orientation, world, image=AGENT, speed=SPEED, viewangle=360, hitpoints=HEROHITPOINTS, firerate=FIRERATE, bulletclass=BigBullet, dodgerate=DODGERATE, areaeffectrate=AREAEFFECTRATE, areaeffectdamage=AREAEFFECTDAMAGE):
        Hero.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)
        self.states = [BL3Idle]
        self.states += [BL3Hunt, BL3Kill, BL3Retreat, BL3Buff]

    def start(self):
        Hero.start(self)
        self.changeState(BL3Idle)


class BL3Idle(State):

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

        if self.agent.getHitpoints() < self.agent.getMaxHitpoints() / 2.0:
            self.agent.changeState(BL3Retreat)
        else:
            if hero is not None and self.agent.level > hero.level + 2:
                self.agent.changeState(BL3Hunt, hero)
            else:
                self.agent.changeState(BL3Buff)


class BL3Hunt(State):

    def parseArgs(self, args):
        self.target = args[0]

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.agent.navigateTo(self.target.getLocation())

    def execute(self, delta=0):
        State.execute(self, delta)
        hit = rayTraceWorld(self.agent.getLocation(), self.target.getLocation(), self.agent.world.getLines())
        if self.agent.getHitpoints() < self.agent.getMaxHitpoints() / 2.0:
            self.agent.changeState(BL3Retreat)
        else:
            if self.target.isAlive() == False:
                self.agent.changeState(BL3Idle)
            else:
                if distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 2:
                    if hit == None:
                        self.agent.changeState(BL3Kill, self.target)
                elif self.agent.getMoveTarget() == None:
                    self.agent.navigateTo(self.target.getLocation())
        BL3shootAtMinions(self.agent)


class BL3Kill(State):

    def parseArgs(self, args):
        self.target = args[0]

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.agent.stopMoving()

    def execute(self, delta=0):
        State.execute(self, delta)
        if self.agent.getHitpoints() < self.agent.getMaxHitpoints() / 2.0:
            self.agent.changeState(BL3Retreat)
        else:
            if self.target.isAlive() == False:
                self.agent.changeState(BL3Idle)
            else:
                if self.target not in self.agent.getVisible():
                    self.agent.changeState(BL3Hunt, self.target)
                else:
                    if distance(self.agent.getLocation(), self.target.getLocation()) > BIGBULLETRANGE - 2:
                        self.agent.changeState(BL3Hunt, self.target)
                    else:
                        self.agent.turnToFace(self.target.getLocation())
                        self.agent.shoot()


class BL3Retreat(State):

    def enter(self, oldstate):
        State.enter(self, oldstate)
        base = self.agent.world.getBaseForTeam(self.agent.getTeam())
        if base is not None:
            self.agent.navigateTo(base.getLocation())

    def execute(self, delta=0):
        State.execute(self, delta)
        if self.agent.getMoveTarget() == None:
            self.agent.changeState(BL3Retreat)
        else:
            if self.agent.getHitpoints() == self.agent.getMaxHitpoints():
                self.agent.changeState(BL3Idle)
        BL3shootAtMinions(self.agent)


class BL3Buff(State):

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.target = None
        self.timer = 0
        enemies = self.agent.world.getEnemyNPCs(self.agent.getTeam())
        if len(enemies) > 0:
            for e in enemies:
                if isinstance(e, Minion):
                    self.target = e
                    break

        if self.target is not None:
            self.agent.navigateTo(self.target.getLocation())

    def execute(self, delta=0):
        State.execute(self, delta)
        if self.target == None:
            self.agent.changeState(BL3Buff)
        else:
            self.timer = self.timer + 1
            if self.target.isAlive == False:
                self.agent.changeState(BL3Idle)
            else:
                if self.agent.getHitpoints() < self.agent.getMaxHitpoints() / 2.0:
                    self.agent.changeState(BL3Retreat)
                else:
                    if distance(self.agent.getLocation(), self.target.getLocation()) < BIGBULLETRANGE - 2:
                        hit = rayTraceWorld(self.agent.getLocation(), self.target.getLocation(), self.agent.world.getLines())
                        if hit == None:
                            self.agent.changeState(BL3Kill, self.target)
                    elif self.timer > 50 or self.agent.getMoveTarget() == None:
                        self.agent.navigateTo(self.target.getLocation())
                        self.timer = 0
        BL3shootAtMinions(self.agent)


def BL3shootAtMinions(agent):
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

# okay decompiling BaselineHero3.pyc