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

class Strategy:
    def __init__(self, pw, source_planet):
        self._pw = pw
        self._source_planet = source_planet
        self._dest_planet = None
        self._num_ships = 0
        self._score = 0

    def SimulateForPlanet(self, planet, my_fleets, enemy_fleets):
        ships = planet.NumShips()
        owner = planet.Owner()
        while True:
            stop = True
            ships += planet.GrowthRate()
            
            for my_fleet in my_fleets:
                if my_fleet.TurnsRemaining() > 0:
                        my_fleet._turns_remaining -= 1
                        stop = False
                else:
                    if owner != my_fleet.Owner():
                        ships -= my_fleet.NumShips()
                        if ships < 0:
                            stderr.write('I take over! ')
                            ships = -ships
                            owner = my_fleet.Owner()
                    else:
                        ships += my_fleet.NumShips()
                    
            for enemy_fleet in enemy_fleets:
                if enemy_fleet.TurnsRemaining() > 0:
                    enemy_fleet._turns_remaining -= 1
                    stop = False
                else:
                    if owner != enemy_fleet.Owner():
                        ships -= enemy_fleet.NumShips()
                        if ships < 0:
                            stderr.write('enemy takes over! ')
                            ships = -ships
                            owner = enemy_fleet.Owner()
                    else:
                        ships += enemy_fleet.NumShips()

            if stop:
                break
            
        return [owner, ships]

    def GetMetricForPlanet(self, planet):
        my_fleets = []
        for my_fleet in self._pw.MyFleets():
            if my_fleet.DestinationPlanet() == planet.PlanetID():
                my_fleets.append(my_fleet)
        
        enemy_fleets = []
        for enemy_fleet in self._pw.EnemyFleets():
            if enemy_fleet.DestinationPlanet() == planet.PlanetID():
                enemy_fleets.append(enemy_fleet)
                
        stderr.write("Without intervention ")
        [owner, _] = self.SimulateForPlanet(planet, my_fleets, enemy_fleets)
        
        me = self._source_planet.Owner()
        if owner == me:
            return 0;
        
        dist = self._pw.Distance(self._source_planet.PlanetID(), planet.PlanetID())
        
        if dist == 0:
            return -1
        
        my_fleets.append(Fleet(self._source_planet.Owner(), self._num_ships, self._source_planet.PlanetID(), planet.PlanetID(), dist, dist))
        
        stderr.write("\nWith intervention ")
        [owner, ships] = self.SimulateForPlanet(planet, my_fleets, enemy_fleets)
        stderr.write('\n')
        
        if owner == me:
            return ships
                            
        return -1
    
    def Colonize(self):
        for neutral_planet in self._pw.NeutralPlanets():
            # suicide attempt ? No Kamikaze fleets!
            if self._num_ships < neutral_planet.NumShips():
                continue
            
            metric = self.GetMetricForPlanet(neutral_planet)
            
            if self._score < metric:
                self._score = metric
                self._dest_planet = neutral_planet
                stderr.write("Colonize score: " + str(self._score)+'\n')
          
            
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
            
            # test with other strategy score
            if self._score < metric:
                self._score = metric
                self._dest_planet = my_planet
                stderr.write("Reinforce score: " + str(self._score)+'\n')
    
    
    def Attack(self):
        # attack an enemy planet
        for enemy_planet in self._pw.EnemyPlanets():
            
            metric = self.GetMetricForPlanet(enemy_planet)
            
            if self._score < metric:
                self._dest_planet = enemy_planet
                self._score = metric
                stderr.write("Attack score: " + str(self._score)+'\n')


    def Steal(self):
        # steal a neutral planet that the enemy will capture
        for enemy_fleet in self._pw.EnemyFleets():
            enemy_planet = self._pw.GetPlanet(enemy_fleet.SourcePlanet())
            metric = self.GetMetricForPlanet(enemy_planet)
                
            if self._score < metric:
                self._dest_planet = enemy_planet
                self._score = metric
                stderr.write("Steal attacker score: " + str(self._score)+'\n')
            
            planet = self._pw.GetPlanet(enemy_fleet.DestinationPlanet())    
            if planet.Owner() != 0:
                continue
            
            metric = self.GetMetricForPlanet(planet)
            
            if self._score < metric:
                self._dest_planet = planet
                self._score = metric
                stderr.write("Steal attacked score: " + str(self._score)+'\n')
            
            
        # steal the planet that the enemy have gone from

    def Flee(self):
        metric = self.GetMetricForPlanet(self._source_planet)
        
        # If I stay here, I will loose my ships! So, let's flee!
        if metric < 0:
            # take all ships ... and apply the best strategy with them
            self._num_ships = self._source_planet.NumShips()
            stderr.write("Flee !\n")
        else:
            # else take only half
            self._num_ships = self._source_planet.NumShips() / 2
    

    def Compute(self):
        self.Flee()
        self.Colonize()
        self.Reinforce()
        self.Attack()
        self.Steal()
        
    def Execute(self):
        if(self._dest_planet != None and self._num_ships > 0):
            self._pw.IssueOrder(self._source_planet.PlanetID(), self._dest_planet.PlanetID(), self._num_ships)
            stderr.flush()
        
        
def DoTurn(pw):
    
    for p in pw.MyPlanets():
        strategy = Strategy(pw, p)
        strategy.Compute()
        if strategy._score > 0:
            strategy.Execute()


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
        