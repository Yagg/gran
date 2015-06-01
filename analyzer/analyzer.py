# -*- coding: utf_8 -*-
__author__ = 'Yagg'

from jinja2 import Environment, PackageLoader

from commandStats import CommandStats
from raceStats import RaceStats

class Analyzer:
    def __init__(self, reports):
        self.reports = sorted(reports, key=lambda r: r.turn)
        self.firstRep = self.reports[0]
        self.lastRep = self.reports[-1]
        self.prevRep = self.reports[-2] if len(self.reports) > 1 else self.reports[-1]
        self.commands = set(map(lambda r: self.command(r.name), self.firstRep.races))
        self.commandRaces = [[r.name for r in self.firstRep.races if self.command(r.name) == c] for c in self.commands]
        self.zippedReports = zip(self.reports, [self.reports[0]]+self.reports[0:len(self.reports)-1])

    def command(self, race):
        a = race.partition('_')
        return a[0]

    def calcCommandStat(self, raceNames, commandName):
        sum = CommandStats(commandName)
        for rname in raceNames:
            lrRace = self.lastRep.getRace(rname)
            if lrRace.productivity() > 400:
                sum.dt += lrRace.driveTech
                sum.wt += lrRace.weaponTech
                sum.st += lrRace.shieldTech
                sum.ct += lrRace.cargoTech
                sum.cnt += 1
            sum.ind += lrRace.industry
            sum.pop += lrRace.population
            sum.rating += lrRace.rating()
            prRace = self.prevRep.getRace(rname)
            if prRace.productivity() > 400:
                sum.prevdt += prRace.driveTech
                sum.prevwt += prRace.weaponTech
                sum.prevst += prRace.shieldTech
                sum.prevct += prRace.cargoTech
                sum.prevcnt += 1
            sum.prevrating += prRace.rating()
            sum.prevind += prRace.industry
            sum.prevpop += prRace.population

        return sum

    def prepareCommandStatisticsForTemplate(self):
        commandStats = []
        for cmd in self.commandRaces:
            commandName = self.command(cmd[0])
            sum = self.calcCommandStat(cmd, commandName)
            commandStats.append(sum)
        return sorted(commandStats, key=lambda s: s.commandName)

    def collectShips(self, raceName, stats):
        for r in self.zippedReports:
            rr = r[0].getRace(raceName)
            prevrr = r[1].getRace(raceName)
            rstats = RaceStats(raceName)
            rstats.initFromRace(rr, prevrr)
            stats.prevTotalMass = stats.totalMassProduced()
            stats.sumTechDiff = stats.sumTechDiff + (rstats.techSum() - rstats.prevtechSum())
            stats.sumIndDiff = stats.sumIndDiff + rstats.indDiff()
            stats.sumL = stats.sumL + rstats.calcL()

    def prepareRacesStatisticsForTemplate(self):
        res = []
        for raceName in [item for sublist in self.commandRaces for item in sublist]:
            stats = RaceStats(raceName)
            r = self.lastRep.getRace(raceName)
            pr = self.prevRep.getRace(raceName)
            stats.initFromRace(r, pr)
            res.append(stats)
            self.collectShips(raceName, stats)
        return sorted(res, key=lambda r: r.name)

    def analyzeBattles(self, stats):
        race = self.firstRep.getReportRace()
        for r in self.zippedReports:
            rr = r[0].getRace(race.name)
            for rs in stats:
                rs.prevdestroyedMass = rs.destroyedMass
            battles = rr.battles
            for b in battles:
                flGroups = [item for sublist in b.groups for item in sublist]  # flatten groups
                destroyedGroups = [(g.ownerName, g.shipType, g.count - g.liveCount)
                                 for g in flGroups if g.count > g.liveCount]
                for (oname, grName, cnt) in destroyedGroups:
                    raceStats = filter(lambda sr: sr.name == oname, stats)[0]
                    raceGroup = filter(lambda gr: gr.name == grName, r[0].getRace(oname).shipTypes)[0]
                    raceStats.destroyedMass = raceStats.destroyedMass + raceGroup.weight * cnt

    def run(self):
        raceStats = self.prepareRacesStatisticsForTemplate()
        self.analyzeBattles(raceStats)
        commandStats = self.prepareCommandStatisticsForTemplate()
        for cs in commandStats:
            cs.destroyedMass = sum([rs.destroyedMass for rs in raceStats if self.command(rs.name) == cs.commandName])
            cs.prevDestroyedMass = sum([rs.prevdestroyedMass for rs in raceStats if self.command(rs.name) == cs.commandName])
            cs.mass = sum([rs.totalMassProduced() for rs in raceStats if self.command(rs.name) == cs.commandName])
            cs.prevMass = sum([rs.prevTotalMass for rs in raceStats if self.command(rs.name) == cs.commandName])

        env = Environment(loader=PackageLoader('gran', 'templates'))
        template = env.get_template('report.html')
        res = template.render(commandStats=commandStats, raceStats=raceStats)
        print res.encode('utf-8')

