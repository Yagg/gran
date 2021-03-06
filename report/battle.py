# -*- coding: utf_8 -*-
__author__ = 'Yagg'

class Battle:
    def __init__(self, planet, planetName):
        self.planet = planet
        self.planetName = planetName
        self.groups = []
        self.protocol = None

class ProtocolRecord:
    def __init__(self, attackerName, attackerShipType, defenderName, defenderShipType, status):
        self.attackerName = attackerName
        self.attackerShipType = attackerShipType
        self.defenderName = defenderName
        self.defenderShipType = defenderShipType
        self.status = status
