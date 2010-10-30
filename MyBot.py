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

ShipsRemaining = []

class Strategy:
    def __init__(self, pw, dest_planet):
        self._pw = pw
        self._source_planet = None
        self._dest_planet = dest_planet
        self._num_ships = 0
        self._score = 0

    def PrintStrategyDebug(self, planet, ships):
        return
        if self._dest_planet.Owner() == 0:
            stderr.write("Colonize ")
        elif self._dest_planet.Owner() == 1:
            stderr.write("Reinforce ")
        else:
            stderr.write("Attack ")

        stderr.write(str(planet.PlanetID()) + " -> " + str(self._dest_planet.PlanetID()) + " N=" +str(ships) + '\n')
        stderr.flush()

    # simulate who will own the destination planet at the end of the game
    def Simulate(self, fleets):
        global GameTurnsRemaining
        
        ships = self._dest_planet.NumShips()
        owner = self._dest_planet.Owner()
        for _ in range(GameTurnsRemaining):
            if owner != 0:
                ships += self._dest_planet.GrowthRate()
            
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

    def Compute(self):
        
        fleets = []
        for fleet in self._pw.Fleets():
            if fleet.DestinationPlanet() == self._dest_planet.PlanetID():
                fleets.append(fleet)
        
        # without intervention
        [owner, _] = self.Simulate(fleets)
            
        # if I will be the owner no intervention is needed
        if owner == 1:
            return
      
        best_dist = 9999999
        best_worst_dist = 9999999
        
        global ShipsRemaining
        
        # intervention required from one of my planets
        for my_planet in self._pw.MyPlanets():
            
            ships_needed = self._dest_planet.NumShips() + self._dest_planet.GrowthRate()
            my_ships = ShipsRemaining[my_planet.PlanetID()]
            
            if my_ships < ships_needed:
                continue 
            
            dist = self._pw.Distance(my_planet.PlanetID(), self._dest_planet.PlanetID())
            
            fleets.append( Fleet(1, ships_needed, my_planet.PlanetID(), self._dest_planet.PlanetID(), dist, dist) )
            
            [owner, ships] = self.Simulate(fleets)
            
            # I will not succeede even if I'll sent a fleet
            if owner != 1:
                if self._score <= 1 and dist < best_worst_dist:
                    self._num_ships = max(my_planet.GrowthRate(), min(my_ships/2, dist * my_planet.GrowthRate()))
                    self._source_planet = my_planet
                    self._score = 1 # a non-zero score
                    best_worst_dist = dist
                continue
            
            metric = ships
       
            self.PrintStrategyDebug(my_planet, metric)
            
            if self._score < metric and dist < best_dist:
                self._source_planet = my_planet
                self._score = metric
                self._num_ships = ships_needed
                best_dist = dist
                
    def Execute(self):
        if(self._source_planet != None and self._num_ships > 0):
            self._pw.IssueOrder(self._source_planet.PlanetID(), self._dest_planet.PlanetID(), self._num_ships)
            ShipsRemaining[self._source_planet.PlanetID()] -= self._num_ships
        
        
def DoTurn(pw):
    global GameTurnsRemaining
    global ShipsRemaining
        
    ShipsRemaining = []
    for p in pw.Planets():
        ShipsRemaining.append(p.NumShips())
        
    for p in pw.NotMyPlanets():
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
        