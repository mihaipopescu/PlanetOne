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
#from sys import stderr
from math import ceil

GoldenRatio = 0.61803399
GameTurnsRemaining = 200


class Strategy:
    def __init__(self, pw, source_planet):
        self._pw = pw
        self._source_planet = source_planet
        self._dest_planet = None
        self._num_ships = 0
        self._score = 0

    def PrintStrategyDebug(self, name, planet, metric):
        #stderr.write(str(self._source_planet.PlanetID()) + name + str(planet.PlanetID()) + " =" +str(metric) + '\n')
        #stderr.flush()
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
        
        [owner, ships] = self.SimulateForPlanet(planet, fleets)
       
        me = self._source_planet.Owner()
        if owner == me and ships > planet.NumShips():
            return 0;
        
        dist = self._pw.Distance(self._source_planet.PlanetID(), planet.PlanetID())
        
        if dist == 0:
            return -1
        
        fleets.append(Fleet(self._source_planet.Owner(), self._num_ships, self._source_planet.PlanetID(), planet.PlanetID(), dist, dist))
        
        [owner, ships] = self.SimulateForPlanet(planet, fleets)
               
        if owner == me:
            return ships
                            
        return -ships
    
    def Colonize(self):
        for neutral_planet in self._pw.NeutralPlanets():
    
            metric = self.GetMetricForPlanet(neutral_planet)
            
            self.PrintStrategyDebug(" colonize ", neutral_planet, metric)
                     
            if self._score < metric:
                self._score = metric
                self._dest_planet = neutral_planet

            
    def Reinforce(self):
        # find an attacked planet that I can help
        for my_planet in self._pw.MyPlanets():
            
            # I cannot reinforce myself, let's try another planet
            if my_planet.PlanetID() == self._source_planet.PlanetID():
                continue
            
            threatened = False
            for enemy_fleet in self._pw.EnemyFleets():
                if enemy_fleet.DestinationPlanet() == my_planet.PlanetID():
                    threatened = True
            
            if not threatened:
                continue
            
            metric = self.GetMetricForPlanet(my_planet)
            self.PrintStrategyDebug(" reinforce ", my_planet, metric)
            
            # test with other strategy score
            if self._score < metric:
                self._score = metric
                self._dest_planet = my_planet
                
    
    def Attack(self):
        # attack an enemy planet
        for enemy_planet in self._pw.EnemyPlanets():
            
            metric = self.GetMetricForPlanet(enemy_planet)
            self.PrintStrategyDebug(" attack ", enemy_planet, metric)
            
            if self._score < metric:
                self._dest_planet = enemy_planet
                self._score = metric
            
                

    def Flee(self):
        metric = self.GetMetricForPlanet(self._source_planet)
        
        # If I stay here, I will loose my ships! So, let's flee!
        if metric < 0:
            # take all ships ... and apply the best strategy with them
            self._num_ships = self._source_planet.NumShips()
            #stderr.write("Flee!\n")
        else:
            # else take only half
            self._num_ships = int(ceil(self._source_planet.NumShips() * GoldenRatio))
    

    def Compute(self):
        self.Flee()
        self.Colonize()
        self.Reinforce()
        self.Attack()

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
        