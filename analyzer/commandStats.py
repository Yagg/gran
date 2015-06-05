# -*- coding: utf_8 -*-
__author__ = 'Yagg'

class CommandStats:
    def __init__(self, commandName):
        self.commandName = commandName
        self.dt = 0
        self.wt = 0
        self.st = 0
        self.ct = 0
        self.pop = 0
        self.ind = 0
        self.cnt = 0
        self.rating = 0

        self.prevdt = 0
        self.prevwt = 0
        self.prevst = 0
        self.prevct = 0
        self.prevpop = 0
        self.prevind = 0
        self.prevcnt = 0
        self.prevrating = 0

        self.mass = 0
        self.destroyedMass = 0
        self.prevMass = 0
        self.prevDestroyedMass = 0
        self.visibleMass = 0
