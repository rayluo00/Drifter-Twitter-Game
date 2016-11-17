#!/usr/bin/python
################################################################################
#                                                                              #
# Ship.py -- The Spaceship                                                     #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import random
from Planets import System
from Crafting import Craft, CRAFT_LIST


##################################################################### Constants:
MAX_PLANETS = 6
INIT_CARGO_CAP = 100

# Starting Money #
INIT_CREDIT_MIN = -100 # Or Debt!
INIT_CREDIT_MAX =  100

# Starting Fuel #
INIT_FUEL_MIN = 0
INIT_FUEL_MAX = 100

# Distance From Home (Light Years) #
INIT_DIST_MIN = 1
INIT_DIST_MAX = 100
INIT_DIST_MULTIPLIER = 1000

# Traveling Distances #
DRIFT_DIST_MIN = 3
DRIFT_DIST_MAX = 15
HEAD_DIST_MIN = 1
HEAD_DIST_MAX = 10

# Fuel (percentage) Gained from Drifing #
DRIFT_FUEL_GAIN_MIN = 1
DRIFT_FUEL_GAIN_MAX = 10

STILL_ALIVE = True

#################################################################### Ship Class:
class Ship():
    '''
    fuel    -- Percentage of fuel tank full.
    health  -- Percentage of ship hull integrity.
    cargo   -- Dictionary of resources.
    cap     -- Cargo capacity.
    usedcap -- Cargo capacity in use.
    delta   -- Distance from home.
    heading -- Toward home or away? (+1 vs -1)
    sys     -- The current system.
    time    -- Time taken to get home.
    credit  -- Universal monetery credits for trading with non-hostile civs.
    '''
    def __init__(self):
        self.fuel = random.randint(INIT_FUEL_MIN,INIT_FUEL_MAX)
        self.delta = random.randint(INIT_DIST_MIN,INIT_DIST_MAX)*INIT_DIST_MULTIPLIER
        self.sys = System(MAX_PLANETS)
        self.health = 100 ; self.time = 0 ; self.heading = 0
        while self.heading == 0: self.heading = random.randint(-1,1)
        self.cargo = {} ; self.cap = INIT_CARGO_CAP ; self.usedcap = 0
        self.credit = random.randint(INIT_CREDIT_MIN,INIT_CREDIT_MAX)
    def fuelerize(self,qt):
        '''Adjust fuel level by qt.'''
        self.fuel += qt
        if self.fuel > 100: self.fuel = 100;
        if self.fuel < 0:   self.fuel = 0;
    def depart(self,cost,dist):
        '''Depart the current system. Return TRUE if arrived at Home.'''
        self.fuelerize(cost) ; self.delta -= self.heading * dist 
        if self.delta <= 0:              return True
        self.sys = System(MAX_PLANETS) ; return False
    def drift(self):
        '''Depart the System while not only preserving fuel but accumulating it.'''
        if self.sys.pos == None:
            tval = self.depart(
                 random.randint(DRIFT_FUEL_GAIN_MIN,DRIFT_FUEL_GAIN_MAX),
                 random.randint(DRIFT_DIST_MIN,DRIFT_DIST_MAX) )
            self.heading = 0
            while self.heading == 0: self.heading = random.randint(-1,1)
        else:
            self.sys.pos = None ; return False
        return tval
    def goHome(self):
        '''Depart the system, using fuel to go home.'''
        if self.fuel > 0:
            self.heading = 1
            return self.depart(-self.fuel,self.fuel*random.randint(HEAD_DIST_MIN,HEAD_DIST_MAX))
        return False
    def harvest(self,result=None):
        '''Acquire resources from result param or else planet being orbited.'''
        '''Returns (STILL_ALIVE?,result)'''
        #TODO: Pass through any Modifiers from ship Modules
        if result == None: result = self.sys.harvest()
        if result != None:
            res_keys = list(result.keys())
            for i in range (len(res_keys)):
                if res_keys[i] == "Nothing": continue
                if res_keys[i] == "Damage":
                    if not self.harm(result['Damage']): return (False,None) # Died #
                elif res_keys[i] == "Fuel": self.fuelerize(result['Fuel'])
                else: self.load(result[res_keys[i]],res_keys[i])
        return (STILL_ALIVE,result)
    def load(self,amt=0,item=None):
        '''Load some cargo to into the cargo bay. Returns acutal amount added.'''
        if item != None and int(amt) > 0 and self.usedcap < self.cap: 
            # Have Room For More #
            if self.usedcap+amt > self.cap: # But not that much room #
                amt = self.cap-self.usedcap
            self.usedcap += amt
            if item not in  self.cargo:
                if amt > 0: self.cargo[item]  = amt
            else:           self.cargo[item] += amt
            return amt
        return 0
    def jettison(self,amt,item):
        ''' Jettison some cargo to make room for more. Returns acutal amount removed. '''
        if item != None and int(amt) > 0 and item in self.cargo:
            #if int(amt) > self.cargo[item] : amt = self.cargo[item]
            self.cargo[item] -= amt ; self.usedcap -= amt
            if self.cargo[item] <= 0:
                if self.cargo[item] < 0:
                    self.usedcap -= self.cargo[item]
                del self.cargo[item]
            if self.usedcap < 0: self.usedcap = 0
            return amt
        return 0
    def shop(self,cmd,amt,item):
        '''Buy and Sell'''
        price = self.sys.buy(item)
        if price > 0: # Item Available #
            if cmd == "buy":
                if (price*amt) > self.credit: amt = int(self.credit / price)
                self.credit -= price * amt ; self.load(amt,item)
            if cmd == "sell" and item in self.cargo:
                if amt > self.cargo[item]: amt = self.cargo[item]
                self.credit += price * amt ; self.jettison(amt,item) 
        if price < 0: return (self.harm(-price),amt) # Under Attack #
        return (True,amt)
    def harm(self,amt):
        '''Apply some amt of damage to self. Return True if survived it.'''
        self.health -= amt
        if self.health <= 0: return not STILL_ALIVE
        else:                return     STILL_ALIVE
    def refine(self,qt,item):
        '''Refine a quantity of some resouce item into better stuff.'''
        if self.sys.pos != None and self.sys.planets[self.sys.pos].resource.civ != None:
            return self.harvest(self.sys.planets[self.sys.pos].resource.civ.refine(self.jettison(qt,item),item))
        return STILL_ALIVE
    def gamble(self,bet=0):
        '''Try to randomly gain credits with some risk of loss and even death'''
        '''Allow gambling debt to accumulate.'''
        '''Returns (STILL_ALIVE?,winnings,damage)'''
        if self.sys.pos != None and self.sys.planets[self.sys.pos].resource.civ != None:
            (win,damage) = self.sys.planets[self.sys.pos].resource.civ.gamble(bet,self.credit)
            self.credit += win ; return (self.harm(damage),win,damage)
        return (STILL_ALIVE,None,0)
    def craft(self,amt=0,item=None):
        '''Craft the items ship's cargo resources.'''
        if item != None and int(amt) > 0 and item in CRAFT_LIST:
            return (Craft.craft(self, self.cargo, item, amt))
        return ("Sorry, you can not craft that item..")
    def gm(self):
        self.cargo.update({"Dirt":1000})
        self.cargo.update({"Rocks":1000})
        self.cargo.update({"Stones":1000})
        self.cargo.update({"Metal":1000})
        self.cargo.update({"Gems":1000})
        self.cargo.update({"Water":1000})
        self.cargo.update({"Ice":1000})
        self.cargo.update({"Holy Water":1000})
        self.cargo.update({"Charcoal":1000})
        self.cargo.update({"Lava":1000})
        self.cargo.update({"Obsidian":1000})
        self.cargo.update({"Engine":1000})
        self.cargo.update({"Coolant":1000})
        self.cargo.update({"Glass":1000})    

############################################################## Main for Testing:
if __name__ == '__main__':
    USSEnterprise = Ship()
    print ("Ship:\n\tDistance Home:\t{} Light Years\n\tHull Integrity:\t{}%\n\tFuel:\t{}%".format( 
        USSEnterprise.delta, USSEnterprise.health, USSEnterprise.fuel ))

