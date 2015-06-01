# -*- coding: utf_8 -*-
__author__ = 'Yagg'

class Race:
    def __init__(self, name, driveTech, weaponTech, shieldTech, cargoTech, population, industry, planets, relation):
        self.name = name
        self.driveTech = driveTech
        self.weaponTech = weaponTech
        self.shieldTech = shieldTech
        self.cargoTech = cargoTech
        self.population = population
        self.industry = industry
        self.planetsCount = planets
        self.relation = relation

        self.shipTypes = []
        self.groups = []
        self.battles = []
        self.sciences = []
        self.incomings = []
        self.planets = []
        self.bombings = []
        self.fleets = []
        self.routes = []

    def productivity(self):
        return self.population*0.25 + self.industry*0.75

    def rating(self):
        return self.productivity()*(self.driveTech+self.weaponTech+self.shieldTech)
