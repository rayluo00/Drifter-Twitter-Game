#!/usr/bin/python
################################################################################
#                                                                              #
# Cargo.py -- Resources, Modules, Comodities, etc.                             #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import random


##################################################################### Constants:
DEFAULT_CIV_SPAWN_CHANCE = 50

## Planet Types ##
planetTypeQt = 3
planetType = { 0:"Barren", 1:"Rocky", 2:"Water", 3:"Fire" }

## XXX Planet ##
# _RESOURCE_LIST = []
# _CHANCES = (harvest_chance_poor, harvest_chance_avg,
#             harvest_poor_min, harvest_poor_max,
#             harvest_avg_min,  harvest_avg_max,
#             harvest_good_min, harvest_good_max)
DEFAULT_CHANCES = (25, 90, 1, 20, 10, 33, 10, 25)
''' 25% chance only getting (1-20) of least valuable resouce.
    90% chance getting (10-33) of a random resource.
    10% chance getting (10-25) of most valuable resource. '''

## Barren Planet ##
BARREN_RESOUCE_LIST = ["Nothing","Dirt"]
BARREN_CHANCES = (50, 100, 0, 0, 0, 15, 0, 15 ) #50% chance of finding up to 15u dirt.

## Rocky Planet ##
ROCKY_RESOUCE_LIST = ["Dirt","Rocks","Stones","Metal","Gems"]
ROCKY_CHANCES = DEFAULT_CHANCES #TODO

## Water Planet ##
WATER_RESOUCE_LIST = ["Water","Ice","Holy Water"]
WATER_CHANCES = DEFAULT_CHANCES #TODO

## Fire Planet ##
FIRE_RESOUCE_LIST = ["Charcoal","Lava","Obsidian","Gems"]
FIRE_CHANCES = DEFAULT_CHANCES  #TODO


resourceType = {    0:BARREN_RESOUCE_LIST,
                    1:ROCKY_RESOUCE_LIST,
                    2:WATER_RESOUCE_LIST,
                    3:FIRE_RESOUCE_LIST     }
resouceChances = {  0:BARREN_CHANCES,
                    1:ROCKY_CHANCES,
                    2:WATER_CHANCES,
                    3:FIRE_CHANCES     }

refineConversions = { "Rocks":"Stones","Stones":"Gems",
                      "Ice":"Water","Water":"Holy Water","Holy Water":"Fuel",
                      "Lava":"Obsidian","Obsidian":"Gems","Charcoal":"Fuel" }

## Civilized Planet ##
ATTITUDE_RAND_MIN =             1 # Minimum Initial Attitude                # 
ATTITUDE_RAND_MAX =           100 # Maximum Initial Attitude                # 
ATTITUDE_FRIEND_MIN_DEFAULT =  50 # Defaulf Min Attitude to be Friendly     # 
ATTITUDE_ENEMY_MAX_DEFAULT =   25 # Default Max Attitude to be Hostile      # 
ATTITUDE_ANGER_RAND_MAX =      15 # Maximum attitude loss when being rude   #
ATTITUDE_HAPPY_RAND_MAX =      10 # Maximum attitude gain when being polite #
ATTITUDE_PRICE_ADJ_MIN =        1 # Minimum price adjustment from Attitude  # 
ATTITUDE_PRICE_ADJ_MAX =       10 # Maximum price adjustment from Attitude  # 

GAMBLING_BASE_CHANCE =         33 # Base percent chance of winning          #
GAMBLING_PAYOUT_MAX =           3 # Maximum payout multiplier applied       #
GAMBLING_DEBT_CAP =        100000 # Maximum debt before being banned        #

PRICE_ADJ_RND_MIN =           -10 # Minimum Random price adjustment         # 
PRICE_ADJ_RND_MAX =            10 # Maximum Random price adjustment         # 
PRICE_LOCAL_MIN =               1 # Minimum base price for local resources  # 
PRICE_LOCAL_MAX =              10 # Maximum base price for local resources  # 
PRICE_FOREIGN_MIN =            10 # Minimum base price for remote resources # 
PRICE_FOREIGN_MAX =            20 # Maximum base price for remote resources #

GEM_FLUX_LOW  =                 2 # Multipliers for Gem prices              #
GEM_FLUX_HIGH =                 5 

CIV_DAM_MIN =                  10 # Minimum damage done by civ defenses     # 
CIV_DAM_MAX =                  33 # Maximum damage done by civ defenses     # 
PLAYER_BASE_DAM_MIN =           3 # Base Minimum damage done by player      #
PLAYER_BASE_DAM_MAX =          12 # Base Maximum damage done by player      #

################################################################## Civilization:
class Civilization():
    '''
    attitude   -- The civilizations attitude toward player as a percentage.
    fiendlyMin -- Minimum attitude for civilization to remain friendly.
    enemyMax   -- Civilization will be hostile until attitude reaches this max.
    ty         -- Host planet type index.
    price      -- Prices of available resources for trade.
    '''
    def __init__(self,ty,fri=ATTITUDE_FRIEND_MIN_DEFAULT,foe=ATTITUDE_ENEMY_MAX_DEFAULT):
        self.fiendlyMin = fri ; self.enemyMax = foe ; self.ty = ty
        self.attitude = random.randint(ATTITUDE_RAND_MIN,ATTITUDE_RAND_MAX)
        self.price = {}
        for i in range (len(resourceType[self.ty])):
            self.price[resourceType[self.ty][i]] = random.randint(PRICE_LOCAL_MIN,PRICE_LOCAL_MAX)
        self.price.pop("Nothing",None)
        self.price["Gems"] = random.randint(PRICE_FOREIGN_MIN*GEM_FLUX_LOW,PRICE_FOREIGN_MAX*GEM_FLUX_HIGH)
        #TODO: if "Gems" not in local resources: else use PRICE_LOCAL_ * GEM_FLUX_
        self.price["Fuel"] = random.randint(PRICE_FOREIGN_MIN,PRICE_LOCAL_MAX)
        #TODO: Add remote resources for trade, with higher prices by default
    def Attitude(self,op=0):
        ''' Returns attitude string, and/or optionally modifies attitude.'''
        self.attitude += op
        if   self.attitude >= self.fiendlyMin:  return "Friendly"
        elif self.attitude >= self.enemyMax:    return "Neutral"
        else:                                   return "Hostile"
    def updatePrices(self): #TODO: Currently unused
        keys = list(self.price.keys())
        for i in range (len(keys)):
            adj = 0
            if keys[i] not in resourceType[self.ty]:
                adj += random.randint(PRICE_ADJ_RND_MIN,PRICE_ADJ_RND_MAX)
            if random.randint(0,100) < self.civ.attitude:
                  adj -= random.randint(ATTITUDE_PRICE_ADJ_MIN,ATTITUDE_PRICE_ADJ_MAX)
            else: adj += random.randint(ATTITUDE_PRICE_ADJ_MIN,ATTITUDE_PRICE_ADJ_MAX)
            self.price[keys[i]] += adj
        #TODO: Remove or Add random foreign resources for trade, except "Gems"
    def attack(self,dam):
        self.attitude -= random.randint(1,ATTITUDE_ANGER_RAND_MAX) * random.randint(1,dam) #TODO Tune
        if self.attitude < 0: self.attitude = 0
        return int(random.randint(CIV_DAM_MIN,CIV_DAM_MAX)*(100-self.attitude)/100)
    def refine(self,amt,item):
        result = {}
        if item in refineConversions:
            if self.attitude >= self.fiendlyMin:
                result[refineConversions[item]] = int(amt*2/3)
            elif self.attitude >= self.enemyMax:
                result[refineConversions[item]] = int(amt*1/2)
            else:
                result[refineConversions[item]] = int(amt*1/3)
                if random.randint(1,100) > self.attitude:
                    result["Damage"] = random.randint(CIV_DAM_MIN,CIV_DAM_MAX)
        else: result[item] = amt
        return result
    def gamble(self,bet=0,debt=0):
        '''
        Bad attitude makes it harder to win.
        Losing may increase attitude toward you, winning decrease it.
        Losing is "safe" in that you wont be attacked for it.
        Passing in negative bet is suicidal on enemy planet.
        Being in debt while gambling is more dangerous, and if you reach the
            cap it is inefectual except for generating damage and ire.
        ''' #TODO: Effects should be indirectly scaled by bet amt
            #      Otherwise, a player could restore attitude fast with
            #      many small bets. We want it to be restored but not too fast.
        win = dam = 0
        if bet > 0:
            win = random.randint(0,100)
            if win < int((GAMBLING_BASE_CHANCE+self.attitude)/200):
                win = bet * random.randint(0,GAMBLING_PAYOUT_MAX)
            else: win = -bet
            if win <= 0:
                  self.attitude += random.randint(0,ATTITUDE_HAPPY_RAND_MAX)
            else:
                self.attitude -= random.randint(0,ATTITUDE_ANGER_RAND_MAX)
        else: self.attitude -= random.randint(0,ATTITUDE_ANGER_RAND_MAX) # Cheater! #
        if self.attitude <= self.enemyMax and win > 0: dam += self.attack(0)
        if debt <= -GAMBLING_DEBT_CAP:
            self.attitude -= random.randint(0,ATTITUDE_ANGER_RAND_MAX)
            win = 0 ; dam += self.attack(0)
        return (win,dam)
                
##################################################################### Resources:
class Resource():
    '''
    type    -- Type of resources available on this planet.
    res     -- List of natural resources available on this planet.
    civ     -- The planet's civilization, if any.
    Private:
        harvest_chance_poor -- Chance of getting only poorest quality item.
        harvest_chance_avg  -- Chance of getting random item.
        harvest_poor_min    -- Minimum quantity recieved from poor harvest.
        harvest_poor_max    -- Maximum quantity recieved from poor harvest.
        harvest_avg_min     -- Minimum quantity recieved from random harvest.
        harvest_avg_max     -- Maximum quantity recieved from random harvest.
        harvest_good_min    -- Minimum quantity recieved from good harvest.
        harvest_good_max    -- Maximum quantity recieved from good harvest.
    '''
    def __init__(self,ty,civ_chance=DEFAULT_CIV_SPAWN_CHANCE):
        ''' 
            kind        -- planetType, or None for random.
            civ_chance  -- Chance for planet to be inhabited by people.
        '''
        self.res  = resourceType[ty] ; self.kind = planetType[ty] ; self.ty = ty
        if random.randint(1,100) in range (1, civ_chance):
                self.civ = Civilization(ty) #TODO: Use fri,foe params
        else:   self.civ = None
        (self.harvest_chance_poor,self.harvest_chance_avg,
         self.harvest_poor_min,self.harvest_poor_max,
         self.harvest_avg_min,self.harvest_avg_max,
         self.harvest_good_min,self.harvest_good_max) = resouceChances[ty]
    def harvest(self,bonus=0):
        '''Returns {'resource':quantity}. Assumes planet has verified success.'''
        result = {}
        if self.civ != None:
            if self.civ.Attitude(-random.randint(0,ATTITUDE_ANGER_RAND_MAX)) == "Hostile":
                result['Damage'] = random.randint(CIV_DAM_MIN,CIV_DAM_MAX) #TODO: apply modifiers from ship modules
        chance = random.randint(0,100) #TODO: Get More Resources at a time?
        if chance <= self.harvest_chance_poor:
            result[min(self.res)] = random.randint(self.harvest_poor_min,self.harvest_poor_max) + bonus
        elif chance <= self.harvest_chance_avg:
            result[self.res[random.randint(0,len(self.res)-1)]] = random.randint(self.harvest_avg_min,self.harvest_avg_max) + bonus
        else: result[max(self.res)] = random.randint(self.harvest_good_min,self.harvest_good_max) + bonus
        return result
    def buy(self,item):
        '''Returns the price per item, 0 if item is unavialable, or damage.'''
        if self.civ == None: return 0
        if self.civ.Attitude() == "Hostile":
            if random.randint(0,100) > self.civ.attitude:
                if random.randint(0,100) < self.civ.attitude:
                    self.civ.attitude += random.randint(0,ATTITUDE_HAPPY_RAND_MAX)
                else:
                    value = random.randint(0,ATTITUDE_ANGER_RAND_MAX)
                    self.civ.attitude -= value
                    return value
        return self.civ.price.get(item,0)
    def attack(self,low=PLAYER_BASE_DAM_MIN,high=PLAYER_BASE_DAM_MAX):
        damRecv = 0 ; damDone = random.randint(low,high)
        if self.civ != None: damRecv += self.civ.attack(damDone)
        return (damDone,damRecv)
