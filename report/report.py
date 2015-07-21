# -*- coding: utf_8 -*-
__author__ = 'Yagg'

import sys
import zipfile
import cStringIO
import re

from race import *
from science import *
from shiptype import *
from planet import *
from battle import *
from shipGroup import *
from bombing import *

class Report:
    def __init__(self, filename):
        self.currentRace = ''
        self.turn = 0
        self.gamename = ''
        self.galaxysize = 0
        self.planetsNum = 0
        self.players = 0

        self.planets = []

        self.races = []

        self.sectionTable = {
            'Your vote': self.skipSection,
            'Status of Players': self.parseStatus,
            '(\S+)\s+Sciences': self.parseSciences,
            '(\S+)\s+Ship Types': self.parseShipTypes,
            'Map around': self.skipSection,
            '(\S+)\s+Planets': self.parsePlanets,
            'Ships In Production': self.parseProdShips,
            'Incoming Groups': self.parseIncoming,
            '(\S+)\s+Groups': self.parseGroups,
            'Broadcast Message': self.skipSection,
            'Battle at \((\S+)\)\s+(\S+)': self.parseBattle,
            'Bombings': self.parseBombings,
            '(\S+)\s+Routes': self.parseRoutes,
            '(\S+)\s+Fleets': self.parseFleets,
            'Role state': self.skipSection
        }

        self.filename = filename
        self.load()

    def load(self):
        try:
            if zipfile.is_zipfile(self.filename):
                with zipfile.ZipFile(self.filename, "r") as zf:
                    n = zf.namelist()
                    rep = zf.read(n[0])
            else:
                with open(self.filename, "r") as fp:
                    rep = fp.read()
            return self.parse_report(rep)
        except Exception as e:
            print >> sys.stderr, e.message
            return False

    def parse_report(self, report):
        strings = cStringIO.StringIO(report)
        header = strings.readline() + strings.readline()
        m = re.search('\s+(\S+)\s+Report for Galaxy PLUS\s+(\S+)\s+Turn\s+(\S+)\s+', header)
        if m:
            self.currentRace = m.group(1)
            self.turn = int(m.group(3))
            self.gamename = m.group(2)
        else:
            print >> sys.stderr, 'Wrong report header'
            return False
        strings.readline()  # empty
        galinfo = strings.readline()
        m = re.search('Size:\s+(\S+)\s+Planets:\s+(\S+)\s+Players:\s+(\S+)', galinfo)
        if m:
            self.galaxysize = float(m.group(1))
            self.planetsNum = int(m.group(2))
            self.players = int(m.group(3))
        else:
            print >> sys.stderr, 'Wrong galaxy info'
            return False

        l = strings.readline()  # empty line
        if not l:
            return False
        while True:
            sectionheader = strings.readline()
            if not sectionheader:
                break
            if sectionheader == '\r\n' or sectionheader == '\r' or sectionheader == '\n':
                continue

            l = strings.readline()  # empty line
            if not l:
                return False

            found = False
            for r in self.sectionTable.keys():
                sm = re.search(r, sectionheader)
                if sm:
                    found = True
                    res = self.sectionTable[r](strings, sm, sectionheader)
                    if not res[0]:
                        print >> sys.stderr, 'Error in section %s' % sectionheader
                        if res[1]:
                            print >> sys.stderr, '   with line:\n%s' % res[1]
                        return False
                    break
            if not found:
                print >> sys.stderr, 'Not found parser for section %s' % sectionheader
                self.skipSection(strings, None, sectionheader)

        for race in self.races:
            addLst = []
            for st in race.battleGroups:
                grp = filter(lambda gr: gr.shipType == st.shipType and st.liveCount == gr.count
                                        and st.destinationPlanet == gr.destinationPlanet, race.groups)
                gg = filter(lambda gr: gr.shipType == st.shipType
                                       and st.destinationPlanet == gr.destinationPlanet, race.groups)
                if not grp:
                    if gg:
                        ggCnt = sum([x.count for x in gg])
                        if ggCnt <= st.liveCount:
                            addLst.append(st)
                    else:
                        addLst.append(st)
            race.groups.extend(addLst)
        return True

    def skipSection(self, strings, rem, sectionheader):
        while True:
            line = strings.readline()
            if not line or line == '\r\n' or line == '\r' or line == '\n':
                break
        return (True, line)

    def commonSectionParse(self, strings, regex, action, skipHeaders = True):
        if skipHeaders:
            line = strings.readline()  # skip headers
            if not line or line == '\r\n' or line == '\r' or line == '\n':
                return False, line

        while True:
            line = strings.readline()
            if not line or line == '\r\n' or line == '\r' or line == '\n':
                break
            m = re.search(regex, line)
            if m:
                action(m)
            else:
                return False, line
        return True, line

    def parseStatus(self, strings, rem, sectionheader):
        def action(m):
            r = Race(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)),
                     float(m.group(6)), float(m.group(7)),
                     float(m.group(8)), m.group(9))
            self.races.append(r)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def rreplace(self, source, target, replacement, replacements=None):
        return replacement.join(source.rsplit(target, replacements))

    def getRace(self, raceName):
        if raceName == 'Your':
            raceName = self.currentRace
        return next((x for x in self.races if x.name == raceName or self.rreplace(x.name, '_RIP','',1) == raceName), None)

    def getReportRace(self):
        return self.getRace(self.currentRace)

    def parseSciences(self, strings, rem, sectionheader):
        race = self.getRace(rem.group(1))
        if not race:
            return False, None

        def action(m):
            s = Science(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
            race.sciences.append(s)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def parseShipTypes(self, strings, rem, sectionheader):
        race = self.getRace(rem.group(1))
        if not race:
            return False, None

        def action(m):
            st = ShipType(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)),
                          float(m.group(6)), float(m.group(7)))
            race.shipTypes.append(st)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def parsePlanets(self, strings, rem, sectionheader):
        if rem.group(1) == 'Uninhabited':
            return self.parseUninhabitedPlanets(strings, rem, sectionheader)
        if rem.group(1) == 'Unidentified':
            return self.parseUnidentifiedPlanets(strings, rem, sectionheader)

        race = self.getRace(rem.group(1))
        if not race:
            return False, None

        def action(m):
            st = Planet(int(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4), float(m.group(5)),
                        float(m.group(6)), float(m.group(7)), float(m.group(8)), m.group(9), float(m.group(10)),
                        float(m.group(11)), float(m.group(12)))
            race.planets.append(st)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def parseProdShips(self, strings, rem, sectionheader):
        return self.skipSection(strings, rem, sectionheader)

    def parseUninhabitedPlanets(self, strings, rem, sectionheader):
        def action(m):
            st = Planet(int(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4), float(m.group(5)),
                        0, 0, float(m.group(6)), '', float(m.group(7)),
                        float(m.group(8)), 0)
            self.planets.append(st)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def parseUnidentifiedPlanets(self, strings, rem, sectionheader):
        def action(m):
            st = Planet(int(m.group(1)), float(m.group(2)), float(m.group(3)), '', 0,
                        0, 0, 0, '', 0,
                        0, 0)
            self.planets.append(st)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def parseGroups(self, strings, rem, sectionheader):
        if rem.group(1) == 'Unidentified':
            return self.skipSection(strings, rem, sectionheader)

        race = self.getRace(rem.group(1))
        if not race:
            return False, None

        def actionAlien(m):
            st = ShipGroup(race.name, float(m.group(1)), m.group(2), float(m.group(3)), float(m.group(4)),
                           float(m.group(5)), float(m.group(6)), m.group(7), float(m.group(8)))
            st.number = m.group(1)
            st.destinationPlanet = m.group(9)
            st.speed = float(m.group(10))
            st.shipMass = float(m.group(11))
            race.groups.append(st)

        def actionAlly(m):
            st = ShipGroup(race.name, float(m.group(2)), m.group(3), float(m.group(4)), float(m.group(5)),
                           float(m.group(6)), float(m.group(7)), m.group(8), float(m.group(9)))
            st.number = m.group(1)
            st.destinationPlanet = m.group(10)
            st.sourcePlanet = m.group(11)
            st.range = float(m.group(12))
            st.speed = float(m.group(13))
            st.shipMass = float(m.group(14))
            st.fleetName = m.group(15)
            st.groupStatus = m.group(16)
            race.groups.append(st)

        header = strings.readline()
        if re.search('\s*G\s+#\s+T\s+D\s+W\s+S\s+C\s+T\s+Q\s+D\s+F\s+R\s+P\s+M\s+L', header):
            return self.commonSectionParse(strings,
                                           '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                           actionAlly, False)
        else:
            return self.commonSectionParse(strings,
                                           '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                           actionAlien, False)

    def parseBattleGroups(self, strings, line, battle):
        m = re.search('(\S+)\s+Groups', line)
        if not m:
            return False, line, None
        race = self.getRace(m.group(1))
        if not race:
            return False, line, None
        line = strings.readline()  # skip empty line
        if not line:
            return False, line, None

        gr = []

        def action(m):
            st = ShipGroup(race.name, int(m.group(1)), m.group(2), float(m.group(3)), float(m.group(4)), float(m.group(5)),
                           float(m.group(6)), m.group(7), float(m.group(8)))
            st.liveCount = int(m.group(9))
            st.battleStatus = m.group(10)
            st.destinationPlanet = battle.planetName
            gr.append(st)
            race.battleGroups.append(st)

        stat, rline = self.commonSectionParse(strings,
                                              '(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                              action)
        if not stat:
            return False, rline, None
        return True, rline, gr

    def parseBattleProtocol(self, strings):
        line = strings.readline()  # skip empty line
        if not line:
            return False, line, None

        proto = []

        def action(m):
            rec = ProtocolRecord(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))
            proto.append(rec)

        stat, rline = self.commonSectionParse(strings,
                                              '(\S+)\s+(\S+)\s+fires on\s+(\S+)\s+(\S+)\s+:\s+(\S+)',
                                              action, False)
        if not stat:
            return False, rline, None
        return True, rline, proto

    def parseBattle(self, strings, rem, sectionheader):
        battle = Battle(rem.group(1), rem.group(2))

        while True:
            line = strings.readline()  # battle section header
            if re.search('Battle Protocol', line):
                status, pline, bp = self.parseBattleProtocol(strings)
                if not status:
                    return False, pline
                battle.protocol = bp
                break
            else:
                status, pline, gr = self.parseBattleGroups(strings, line, battle)
                if not status:
                    return False, pline
                battle.groups.append(gr)

        race = self.getReportRace()
        race.battles.append(battle)
        # for glist in battle.groups:
        #     raceName = glist[0].ownerName
        #     race = self.getRace(raceName)
        #     if not race:
        #         return False, 'Can not find race ' + raceName + ' for battle at '+battle.planet
        #     race.battles.append(battle)

        return True, pline

    def parseBombings(self, strings, rem, sectionheader):
        race = self.getReportRace()
        if not race:
            return False, None

        def action(m):
            st = Bombing(m.group(1), m.group(2), int(m.group(3)), m.group(4), float(m.group(5)), float(m.group(6)),
                          m.group(7), float(m.group(8)), float(m.group(9)),float(m.group(10)),float(m.group(11)),
                         m.group(12))
            race.bombings.append(st)

        return self.commonSectionParse(strings,
                                       '\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
                                       action)

    def parseIncoming(self, strings, rem, sectionheader):
        return self.skipSection(strings, rem, sectionheader)

    def parseRoutes(self, strings, rem, sectionheader):
        return self.skipSection(strings, rem, sectionheader)

    def parseFleets(self, strings, rem, sectionheader):
        return self.skipSection(strings, rem, sectionheader)
