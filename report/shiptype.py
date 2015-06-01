# -*- coding: utf_8 -*-
__author__ = 'Yagg'


class ShipType:
    def __init__(self, name, drive, ammo, weapon, shield, cargo, weight):
        self.name = name
        self.drive = drive
        self.ammo = ammo
        self.weapon = weapon
        self.shield = shield
        self.cargo = cargo
        self.weight = weight

    def __eq__(self, other):
        sdt = self.drive if self.drive <= 3 else self.drive / 4.0
        odt = other.drive if other.drive <= 3 else other.drive / 4.0
        return self.name == other.name and sdt == odt and self.ammo == other.ammo and self.weapon == other.weapon and self.shield == other.shield and self.cargo == other.cargo

    def shipMass(self):
        return self.drive + (self.ammo+1) * self.weapon/2.0 + self.shield + self.cargo
