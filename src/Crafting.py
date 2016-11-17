#!/usr/bin/python
################################################################################
#                                                                              #
# Crafting.py -- The crafting mechanism.                                       #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import random

'''
Dictionary of requirements to craft the item. 
Uses the command : craft [amount to craft] [name of crafted item]
'''

CRAFT_FUEL          = {"Plasma":4, "Laser":6, "Holy Water":8}
CRAFT_PLASMA        = {"Charcoal":8, "Holy Water":8, "Obsidian":8}
CRAFT_LASER         = {"Metal":5, "Stones":4, "Lava":2, "Charcoal":5}
CRAFT_MOTHERBOARD   = {"Metal":3, "Plasma":4, "Gems":2}
CRAFT_FOAM          = {"Holy Water":2, "Charcoal":1}
CRAFT_COOLANT       = {"Water":3, "Ice":5, "Beaker":2}
CRAFT_CARGO         = {"Metal":15, "Stones":7, "Lava":3, "Water":6, "Gems":5}
CRAFT_SAND          = {"Stones":5}
CRAFT_GLASS         = {"Sand":3, "Lava":1, "Water":2}
CRAFT_ENGINE        = {"Motherboard":2, "Coolant":4, "Metal":7}
CRAFT_BEAKER        = {"Glass":3}
REPAIR_SHIP         = {"Metal":7, "Coolant":3, "Engine":2, "Glass":5}


## Dictionary to map the requirements to the item. ##
CRAFT_LIST = {"Laser":CRAFT_LASER, "Cargo":CRAFT_CARGO, "Plasma":CRAFT_PLASMA, "Fuel":CRAFT_FUEL,
              "Motherboard":CRAFT_MOTHERBOARD, "Foam":CRAFT_FOAM, "Coolant":CRAFT_COOLANT, "Sand":CRAFT_SAND,
              "Glass":CRAFT_GLASS, "Engine":CRAFT_ENGINE, "Beaker":CRAFT_BEAKER, "repair":REPAIR_SHIP}

########################################################################## Craft:
class Craft():
   def craft(ship, inv, item, amt):
      req = CRAFT_LIST.get(item)

      for key in req:
           if (key not in inv):
              return (" - Unable to craft "+ str(item) + ". Missing '"+key+"'.\n")
           elif ((req[key] * amt) > inv[key]): 
              return (" - Unable to craft " + str(item) + ". Need " + str(((req[key] * amt) - inv[key])) + " '"+key+"'.\n")

      for key in req:
         inv[key] -= (req[key] * amt)
         if inv[key] == 0:
            inv.pop(key)

      if (item == "Cargo"):
         ship.cap += 25 * amt
      if (item == "Fuel"):
         ship.fuel += 10 * amt
         if (ship.fuel > 100):
            ship.guel = 100
      if (item == "repair"):
         ship.health += 15
         if (ship.health > 100):
            ship.health = 100
      else:
         if item not in inv:
            ship.cargo.update({item:amt})
         else:
            ship.cargo.update({item:inv[item]+amt})
      return (" - You crafted "+ str(amt) + " "+str(item) + "(s)!\n")

if __name__ == '__main__':
   crafting = Craft()
