# -*- coding: utf_8 -*-
__author__ = 'Yagg'

class Planet:
    def __init__(self, number, xcoord, ycoord, name, size, population, industry, resources, production, capitals,
                 materials, colonists):
        self.number = number
        self.xcoord = xcoord
        self.ycoord = ycoord
        self.name = name
        self.size = size
        self.population = population
        self.industry = industry
        self.resources = resources
        self.production = production
        self.materials = materials
        self.colonists = colonists
        self.capitals = capitals

    def L(self):
        return self.population*0.25 + self.capitals*0.75

