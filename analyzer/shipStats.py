# -*- coding: utf_8 -*-
__author__ = 'Yagg'

class ShipStats:
    def __init__(self, shipType, seenCount, destroyedCount):
        self.shipType = shipType
        self.seenCount = seenCount
        self.destroyedCount = destroyedCount

    def liveCount(self):
        return self.seenCount - self.destroyedCount

