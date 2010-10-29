#!/usr/bin/env python
#

"""
// The DoTurn function is where your code goes. The PlanetWars object contains
// the state of the game, including information about all planets and fleets
// that currently exist. Inside this function, you issue orders using the
// pw.IssueOrder() function. For example, to send 10 ships from planet 3 to
// planet 8, you would say pw.IssueOrder(3, 8, 10).
//
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own. Check out the tutorials and articles on the contest website at
// http://www.ai-contest.com/resources.
"""

from PlanetWars import PlanetWars, Fleet
from sys import stderr


GoldenRatio = 0.61803399
GameTurnsRemaining = 200



class Strategy:
    def __init__(self, pw, source_planet):
        self._pw = pw
        self._source_planet = source_planet
        self._dest_planet = None
        self._num_ships = 0
        self._score = 0

    def PrintStrategyDebug(self, planet, metric):
        return
        stderr.write(str(self._source_planet.PlanetID()))
        if planet.Owner() == 0:
            stderr.write(" colonize ")
        elif planet.Owner() == self._source_planet.Owner():
            stderr.write(" reinforce ")
        else:
            stderr.write(" attack ")
        stderr.write(str(planet.PlanetID()) + " =" +str(metric) + '\n')
        stderr.flush()
        pass

    def SimulateForPlanet(self, planet, fleets):
        global GameTurnsRemaining
        
        ships = planet.NumShips()
        owner = planet.Owner()
        for _ in range(GameTurnsRemaining):
            if owner != 0:
                ships += planet.GrowthRate()
            
            for fleet in fleets:
                fleet._turns_remaining -= 1                
                if fleet.TurnsRemaining() == 0:
                    if owner != fleet.Owner():
                        ships -= fleet.NumShips()
                        if ships < 0:
                            ships = -ships
                            owner = fleet.Owner()
                    else:
                        ships += fleet.NumShips()
                    
        return [owner, ships]

    def GetMetricForPlanet(self, planet):
        fleets = []
        for fleet in self._pw.Fleets():
            if fleet.DestinationPlanet() == planet.PlanetID():
                fleets.append(fleet)
        
        [owner, _] = self.SimulateForPlanet(planet, fleets)
       
        dist = self._pw.Distance(self._source_planet.PlanetID(), planet.PlanetID())
       
        me = self._source_planet.Owner()
        if owner == me or dist == 0:
            return 0;
        
        fleets.append(Fleet(self._source_planet.Owner(), self._num_ships, self._source_planet.PlanetID(), planet.PlanetID(), dist, dist))
        
        [owner, ships] = self.SimulateForPlanet(planet, fleets)
        
        if owner == me:
            return ships/dist
                            
        return -ships/dist
    
    def Compute(self):
        
        self._num_ships = self._source_planet.NumShips()

        for planet in self._pw.Planets():
            
            metric = self.GetMetricForPlanet(planet)
            self.PrintStrategyDebug(planet, metric)
            
            if self._score < metric:
                self._dest_planet = planet
                self._score = metric

    def Execute(self):
        if(self._dest_planet != None and self._num_ships > 0):
            self._pw.IssueOrder(self._source_planet.PlanetID(), self._dest_planet.PlanetID(), self._num_ships)
        
        
def DoTurn(pw):
    global GameTurnsRemaining
        
    for p in pw.MyPlanets():
        strategy = Strategy(pw, p)
        strategy.Compute()
        if strategy._score > 0:
            strategy.Execute()
    
    GameTurnsRemaining -= 1


def main():
    map_data = ''
    while(True):
        current_line = raw_input()
        if len(current_line) >= 2 and current_line.startswith("go"):
            pw = PlanetWars(map_data)
            DoTurn(pw)
            pw.FinishTurn()
            map_data = ''
        else:
            map_data += current_line + '\n'


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    try:
        main()
    except KeyboardInterrupt:
        print 'ctrl-c, leaving ...'
        