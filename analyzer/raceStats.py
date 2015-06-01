# -*- coding: utf_8 -*-
__author__ = 'Yagg'

class RaceStats:
    def __init__(self, name):
        self.name = name

        self.dt = 0
        self.wt = 0
        self.st = 0
        self.ct = 0
        self.pop = 0
        self.ind = 0

        self.prevdt = 0
        self.prevwt = 0
        self.prevst = 0
        self.prevct = 0
        self.prevpop = 0
        self.prevind = 0

        self.prevdestroyedMass = 0
        self.prevTotalMass = 0
        self.destroyedMass = 0

        self.sumL = 0
        self.sumIndDiff = 0
        self.sumTechDiff = 0

        self.destroyedGroups = []
        self.seenGroups = []
        self.lastGroupsDiff = []

        self.shipStats = []
        self.totalSeenMass = 0

    def totalMassProduced(self):
        val = (self.sumL - 2000 - (self.sumIndDiff * 5) - (self.sumTechDiff * 5000)) / (10.0 + 1.0/10.0)
        return val if val > 0 else 0

    def initFromRace(self, race, prevrace):
        self.dt = race.driveTech
        self.prevdt = prevrace.driveTech
        self.wt = race.weaponTech
        self.prevwt = prevrace.weaponTech
        self.st = race.shieldTech
        self.prevst = prevrace.shieldTech
        self.ct = race.cargoTech
        self.prevct = prevrace.cargoTech
        self.pop = race.population
        self.prevpop = prevrace.population
        self.ind = race.industry
        self.prevind = prevrace.industry

    def techSum(self):
        return self.dt+self.wt+self.st+self.ct

    def prevtechSum(self):
        return self.prevdt+self.prevwt+self.prevst+self.prevct

    def prevL(self):
        return self.prevpop*0.25 + self.prevind*0.75

    def L(self):
        return self.pop*0.25 + self.ind*0.75

    def indDiff(self):
        indDiff = self.ind - self.prevind
        return indDiff if indDiff > 0 else 0

    def popForL(self):
        notGrowed = 2000 if self.prevpop >= 2000 else 0
        selfGrowth = (self.prevpop - notGrowed)*0.08
        return self.pop - selfGrowth

    def calcL(self):
        indDiff = self.ind - self.prevind
        return self.popForL() * 0.25 + (self.prevind if indDiff > 0 else self.ind) * 0.75

    def LSpentToTech(self):
        return (self.techSum()-self.prevtechSum()) * 5000.0

    def LSpentToInd(self):
        indDiff = self.ind - self.prevind
        return (indDiff if indDiff > 0 else 0) * 5  # (5.0 + 1.0/10.0)

    def LSpentToMass(self):
        l = self.calcL() - self.LSpentToTech() - self.LSpentToInd()
        eps = 0.00001
        return l if (l-eps) > 0 else 0

    def massProdused(self):
        return self.LSpentToMass() / (10.0 + 1.0/10.0)

