#!/usr/bin/python
################################################################################
#                                                                              #
# Planets.py -- Planets and Solar Systems                                      #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import random

from Cargo import Resource, planetTypeQt, DEFAULT_CIV_SPAWN_CHANCE


##################################################################### Constants:
MAX_BASE_CHANCE = 66
MIN_HEALTH      = 25
HARVEST_DAM_MIN =  1
HARVEST_DAM_MAX =  6

################################################################## Planet Class:
class Planet():
    '''
    resource    -- Civilization and Resources on Planet.
    health      -- Remaining population, or resources, if any.
    baseChance  -- Base chance for gathering, fighting, etc.
    '''
    def __init__(self,kind,civ_chance = DEFAULT_CIV_SPAWN_CHANCE):
        self.resource = Resource(kind,civ_chance)
        self.health = random.randint(MIN_HEALTH,100)
        self.baseChance = random.randint(0,MAX_BASE_CHANCE)
    def harvest(self,adj = 0, bonus = 0):
        if self.resource.civ == None and self.health > 0:
            self.health -= random.randint(HARVEST_DAM_MIN,HARVEST_DAM_MAX)
        if self.health > 0:
            if (adj + random.randint(1,100)) > self.baseChance:
                return self.resource.harvest(bonus)
        return None
    def attack(self):
        (damPlanet,damShip) = self.resource.attack()
        self.health -= damPlanet
        return (damPlanet,damShip)

        
################################################################## System Class:
class System():
    '''
    qt      -- Quantity of planets in this system.
    planets -- List of planets in this system.
    pos -- Index of which planet is being orbited? or None
    '''
    def __init__(self,maxQt,civ_chance = DEFAULT_CIV_SPAWN_CHANCE):
        self.qt = random.randint(0, maxQt)
        self.planets = []
        for i in range (0, self.qt): self.planets.append(
                           Planet( random.randint(0,planetTypeQt), civ_chance) )
        self.pos = None
    def orbit(self,idx):
        origin = self.pos
        if(( idx >= 0 )and( idx < self.qt )): self.pos = idx
        else: self.pos = None
        return (self.pos,origin)
    def scan(self):
        string = ""
        if self.pos != None:
            string += "[{}/{} ".format(self.pos+1,self.qt)
            if self.planets[self.pos].resource.civ != None:
                string += "Civilized " + self.planets[self.pos].resource.civ.Attitude() + ' '
            string +=       self.planets[self.pos].resource.kind      + ']'
            string += '{' + str(self.planets[self.pos].health)        + '}'
            if self.planets[self.pos].resource.civ != None:
                string += '{' + str(self.planets[self.pos].resource.civ.attitude) + '}'
                string += str(self.planets[self.pos].resource.civ.price)
            else: string += str(self.planets[self.pos].resource.res)
        else: string += "[0/{}]".format(self.qt)
        return string
    def harvest(self,adj=0,bonus=0):
        if self.pos != None:
            planet = self.planets[self.pos] ; result = planet.harvest(adj,bonus)
            if planet.health <= 0:
                if planet.resource.civ == None:
                    if planet.resource.kind != "Barren":
                        self.planets[self.pos] = Planet(0, 0);
                else: self.planets[self.pos] = Planet(planet.resource.ty, 0);
            return result
        else: return None #TODO: Solar scoop? gain fuel without leaving system.
    def buy(self,item):
        if self.pos == None: return 0 #TODO: Trade with other ships
        return self.planets[self.pos].resource.buy(item)
    def attack(self): #TODO: have Modifiers
        if self.pos == None: return (0,0) #TODO: Fight with other ships
        return self.planets[self.pos].attack()

############################################################## Main for Testing:
if __name__ == '__main__':
    max_planets = 6
    sys = System(max_planets)
    
