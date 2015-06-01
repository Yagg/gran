# -*- coding: utf_8 -*-
__author__ = 'Yagg'


class ShipGroup:
    def __init__(self, ownerName, count, shipType, driveTech, weaponTech, shieldTech, cargoTech, cargoType, cargoQuantity):
        self.count = count
        self.shipType = shipType
        self.driveTech = driveTech
        self.weaponTech = weaponTech
        self.shieldTech = shieldTech
        self.cargoTech = cargoTech
        self.cargoType = cargoType
        self.cargoQuantity = cargoQuantity
        self.ownerName = ownerName

        self.shipMass = 0
        self.number = -1

        self.liveCount = 0
        self.battleStatus = ''

        self.destinationPlanet = ''
        self.sourcePlanet = ''
        self.range = 0.0
        self.speed = 0.0

        self.fleetName = ''
        self.groupStatus = ''
