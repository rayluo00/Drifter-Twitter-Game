# main.py:
# The main program that run the game bot

#Python Libraries
import sys, time, random, math

#Our libraries
#import gfx, twitter

'''
NOTES : 
========================================
in space:
automate - lose 2 fuel if no action has been made in a couple hours.
========================================
'''

# Classes for an 'object' for the ship and planets.
class makePlanet (object):
   def __init__(node):
      node.planetNum = -1
      node.planetType = None
      node.resources = {}
      node.adjPlanets = []
      node.civ = None
      node.civHealth = None
      node.civStatus = None
      node.tradingPrices = {}
      node.treasury = 0

class makeMilFalcon (object):
   def __init__(node):
      node.fuel = 100
      node.health = 100
      node.resources = {}
      node.damageMin = 8
      node.damageMax = 11
      node.currPlanet = None
      node.treasury = 0

numTurns = 0

rockResourceList = ["Stone", "Rock", "Dirt", "Metal"]
waterResourceList = ["Water", "Ice", "Steam"]
fireResourceList = ["Obsidian", "Lava", "Diamond", "Charcoal"]

# Generate resources on a planet randomly based on the
# planet type.
def genPlanetResources (planet):
   index = 1
   resourceList = {}

   if (planet.planetType == "Rock"):
      for i in range (0, 3):
         currResource = rockResourceList[random.randint(0, 3)]
         if (currResource not in resourceList):
            resourceList.update({currResource:index})
   elif (planet.planetType == "Watr"):
      for i in range (0, 3):
         currResource = waterResourceList[random.randint(0, 2)]
         if (currResource not in resourceList):
            resourceList.update({currResource:index})
   elif (planet.planetType == "Fire"):
      for i in range (0, 3):
         currResource = fireResourceList[random.randint(0, 3)]
         if (currResource not in resourceList):
            resourceList.update({currResource:index})
   return resourceList

# Generate a 10x10 matrix with all nodes connected to create the
# universe. Planets has resources and possible civilization.
def generateMap ():
   universe =  []
   planetTypeOpt = {0:"Rock", 1:"Watr", 2:"Fire"}
   civOpt = {0:"Trading", 1:"Bandit"}

   for i in range (0, 100):
      planet = makePlanet()
      planet.planetNum = i
      planet.planetType = planetTypeOpt[random.randint(0, 2)]
      planet.treasury = random.randint(80, 150)
      planet.resources = genPlanetResources(planet)

      if ((i+10) < 100):
         planet.adjPlanets.append(i+10)
      if ((i-10) >= 0):
         planet.adjPlanets.append(i-10)
      if ((i%10) != 0):
         planet.adjPlanets.append(i-1)
      if (((i-9)%10) != 0):
         planet.adjPlanets.append(i+1)

      if (random.randint(0,99) in range (0, 49)):
         chosenCiv = random.randint(0,1)
         planet.civ = civOpt[chosenCiv]
         if (chosenCiv == 1):
            planet.civHealth = 55
            planet.civStatus = "Hostile"
         else:
            planet.civHealth = 70
            planet.civStatus = "Passive"
            
      universe.append(planet)

   homePlanet = universe[random.randint(0, 9)]
   homePlanet.planetType = "HOME"

   startPlanet = universe[random.randint(90, 99)]
   startPlanet.planetType = "STRT"

   milFalcon = makeMilFalcon()
   milFalcon.currPlanet = startPlanet.planetNum

   return (milFalcon, universe)

# Ship goes to the next planet adjacent to the current planet.
def cmd_goto (gotoPlanet, milFalcon, universe):
   global numTurns
   currentPlanet = milFalcon.currPlanet
   adjPlanets = universe[currentPlanet].adjPlanets

   if (universe[currentPlanet].civStatus == "Hostile"):
      civAttack (milFalcon, universe)

   if (gotoPlanet in adjPlanets):
      print("- Travelling to Planet #", gotoPlanet, "...")
      milFalcon.currPlanet = gotoPlanet
      milFalcon.fuel = milFalcon.fuel - 10
      numTurns = numTurns + 1
   else:
      print("- Planet #", gotoPlanet, "is not adjacent.")
   return 0

# Harvest resources on the planet, if planet has bandits they
# have a chance to attack the ship. 70% chance success.
def cmd_harvest (milFalcon, universe):
   global numTurns
   currentPlanet = milFalcon.currPlanet
   
   if (bool(universe[currentPlanet].resources)):
      numTurns = numTurns + 1
      if (random.randint(0, 99) in range(0, 69)):
         print("- SUCCESSFUL HARVEST!")
         for key, value in universe[currentPlanet].resources.items():
            if (key not in milFalcon.resources):
               milFalcon.resources.update({key:1})
            else:
               milFalcon.resources.update({key:(milFalcon.resources[key]+1)})
      else:
         print("- UNSUCCESSFUL HARVEST..")
   else:
      print("- There are no resources left on this planet.")

   civAttack (milFalcon, universe)
   universe[currentPlanet].resources = None
   milFalcon.fuel = milFalcon.fuel - 5
   return 0

def sellPriceHelper (universe, itemAmmt, itemType, currentPlanet):
   global rockResourceList, waterResourceList, fireResourceList
   
   for i in range (0, itemAmmt):
      buyPrice = random.randint(3, 12)
      # Cut prices of item by half if item from same planet.
      if (itemType == universe[currentPlanet].planetType):
         buyPrice = math.ceil(buyPrice / 2)

      # Set the item with corresponding buyPrice
      if (itemType == "Rock"):
         currResource = rockResourceList[random.randint(0, 3)]
         if (currResource not in universe[currentPlanet].tradingPrices):
            universe[currentPlanet].tradingPrices.update({currResource:buyPrice})
      elif (itemType == "Watr"):
         currResource = waterResourceList[random.randint(0, 2)]
         if (currResource not in universe[currentPlanet].tradingPrices):
            universe[currentPlanet].tradingPrices.update({currResource:buyPrice})
      elif (itemType == "Fire"):
         currResource = fireResourceList[random.randint(0, 3)]
         if (currResource not in universe[currentPlanet].tradingPrices):
            universe[currentPlanet].tradingPrices.update({currResource:buyPrice})
   
   return 0

# Set the trading prices for the civilization.
# New prices and items for every tenth turn.
def setSellPrices (milFalcon, universe):
   currentPlanet = milFalcon.currPlanet
   planetType = universe[currentPlanet].planetType

   rockItemAmmt = random.randint(0, 3)
   waterItemAmmt = random.randint(0, 3)
   fireItemAmmt = random.randint(0, 3)

   universe[currentPlanet].tradingPrices = {}
   for i in range(0, 3):
      if (i == 0):
         sellPriceHelper(universe, rockItemAmmt, "Rock", currentPlanet)
      elif (i == 1):
         sellPriceHelper(universe, waterItemAmmt, "Watr", currentPlanet)
      else:
         sellPriceHelper(universe, fireItemAmmt, "Fire", currentPlanet)
         
   return 0

# Trade with the civilization that the ship is on.
def cmd_sell (milFalcon, universe, sellItem, sellAmmt):
   global numTurns
   currentPlanet = milFalcon.currPlanet

   if ((sellItem not in universe[currentPlanet].tradingPrices) and (sellItem not in milFalcon.resources)):
      print("Can not sell item", sellItem, ".")
      return 0
      
   if (universe[currentPlanet].civ == "Trading"):
      if (bool(milFalcon.resources)):
         if (universe[currentPlanet].civStatus == "Passive") :
            if (sellAmmt > milFalcon.resources.get(sellItem)):
               sellAmmt = milFalcon.resources.get(sellItem)
            
            civPriceTag = universe[currentPlanet].tradingPrices.get(sellItem)
            civSoldForPrice = civPriceTag * sellAmmt
            
            milFalcon.treasury = civSoldForPrice
            newItemAmmt = milFalcon.resources.get(sellItem) - sellAmmt
            milFalcon.resources.update({sellItem:newItemAmmt})
            if (milFalcon.resources.get(sellItem) <= 0):
               milFalcon.resources.pop(sellItem)
            
            universe[currentPlanet].treasury -= civSoldForPrice
            print("- Trading", sellAmmt, sellItem, "for", civSoldForPrice, "coins.")
            numTurns = numTurns + 1
         else:
            print("- This civilization does not want to trade with you.");
      else:
         print("- You have no items to sell.")
   else:
      print("- No civilization wants to trade.")

   civAttack(milFalcon, universe)
   return 0

def cmd_buy (milFalcon, universe, butItem, buyAmmt):
   
   
   return 0

# Fights the civilization on the planet, the civilization status will
# change to 'Hostile' when attacked.
def cmd_fight (milFalcon, universe):
   global numTurns
   currentPlanet = milFalcon.currPlanet
   civ = universe[currentPlanet].civ
   civHealth = universe[currentPlanet].civHealth

   if (civ == None):
      print("- No civilization to attack.")
      return 0
   elif (civ == "Bandit"):
      print("Bandit Camp | Health :", civHealth, "[", universe[currentPlanet].civStatus,"]\n")
   elif (civ == "Trading"):
      universe[currentPlanet].civStatus = "Hostile"
      print("Trading Camp | Health :", civHealth, "[", universe[currentPlanet].civStatus,"]\n")
      
   userAttack = random.randint(milFalcon.damageMin, milFalcon.damageMax)
   universe[currentPlanet].civHealth = universe[currentPlanet].civHealth - userAttack
   print("- User attacked for", userAttack, "damage.")
   
   civAttack(milFalcon, universe)

   if (universe[currentPlanet].civHealth <= 0):
      universe[currentPlanet].civ = None
      universe[currentPlanet].civStatus = None
      universe[currentPlanet].civHealth = None
      print("\nCivilization was defeated!")

      numTurns = numTurns + 1
   return 0

# Bandits attack ship if they perform an action on a planet with bandits.
# 70% chance of attacking.
def civAttack (milFalcon, universe):
   currentPlanet = milFalcon.currPlanet
   if (universe[currentPlanet].civStatus == "Hostile") :
      if (random.randint(0, 99) in range(0, 69)):
         civAttack = random.randint(1, 4)
         milFalcon.health = milFalcon.health - civAttack
         print("-", universe[currentPlanet].civ, "civilization dealt", civAttack, "damage.")    
   return 0

# Quit the game.
def quitGame (milFalcon, universe) :
   sys.exit(0)

# Update the status of the game
def updateStatus (milFalcon, universe) :
   global numTurns
   currentPlanet = milFalcon.currPlanet
   print("TURN =", numTurns)
   print(
      "\n=========================== BEGIN =========================\n"
      "Ship Stats :\n",
      "Health :", milFalcon.health, "| Fuel :", milFalcon.fuel, "| Current Planet :", milFalcon.currPlanet, "\n",
      "Damage :", milFalcon.damageMin,"-",milFalcon.damageMax, "| Money :", milFalcon.treasury, "\n",
      "Resources :", milFalcon.resources,"\n",
      "Adjacent Planets :", universe[currentPlanet].adjPlanets, "\n\n"
      "Planet Stats :\n",
      "Planet Number : ", universe[currentPlanet].planetNum, "| Planet Type : ", universe[currentPlanet].planetType,"\n",
      "Planet Resources :", universe[currentPlanet].resources,"\n",
      "Civilization :", universe[currentPlanet].civ, "[", universe[currentPlanet].civStatus,"] | Civ's Health :",
      universe[currentPlanet].civHealth, "| Treasury :", universe[currentPlanet].treasury)

   if (universe[currentPlanet].civ == "Trading" and universe[currentPlanet].civStatus == "Passive"):
      if (((numTurns % 10) == 0) or (not bool(universe[currentPlanet].tradingPrices))):
         setSellPrices(milFalcon, universe)
      if (bool(universe[currentPlanet].tradingPrices)):
         print("\nTrading Prices:")
         if (milFalcon.fuel < 100):
            print(" * Gas =", math.ceil((100 - milFalcon.fuel)/3))
      for key, value in universe[currentPlanet].tradingPrices.items():
         print(" *", key, "=", value)
   
   print("\n=========================== END ===========================\n")
   return 0

def tradeTele (milFalcon, universe):
   for i in range (random.randint(0,70), 100):
      if ((universe[i].civ == "Trading") and (milFalcon.currPlanet != i)):
         milFalcon.currPlanet = i;
         return 0

def banditTele (milFalcon, universe):
   for i in range (random.randint(0,70), 100):
      if ((universe[i].civ == "Bandit") and (milFalcon.currPlanet != i)):
         milFalcon.currPlanet = i;
         return 0

def godMode (milFalcon, universe):
   milFalcon.fuel = 100
   milFalcon.health = 100
   milFalcon.damageMin = 100
   milFalcon.damageMax = 100
   milFalcon.treasury = 100

   for i in range(0, 4):
      key = rockResourceList[i]
      milFalcon.resources.update({key:100})

   for i in range(0, 3):
      key = waterResourceList[i]
      milFalcon.resources.update({key:100})

   for i in range(0, 4):
      key = fireResourceList[i]
      milFalcon.resources.update({key:100})
      
   return 0

# Display all the possible commands the user can perform.
def cmd_help (milFalcon, universe):
   print("LIST OF COMMANDS :\n",
         "help                        : Show list of available commands to perform in-game.\n",
         "fight                       : Fight with the civilization inhabiting the planet.\n",
         "harvest                     : Harvest the resources on the planet if available.\n",
         "goto [PLANET #]             : Travel to the available adjacent planet.\n",
         "sell [ITEM NAME] [AMMOUNT]  : Sell items with the planet's civilization if they are [Passive].\n")
      
# Run function corresponding to user input.
def startGame (milFalcon, universe):
   commandList = {"help":cmd_help, "goto":cmd_goto, "harvest":cmd_harvest,
                  "sell":cmd_sell, "fight":cmd_fight, "gas":cmd_buy, "q":quitGame,
                  "ttele":tradeTele, "btele":banditTele, "gm":godMode}
   
   print("Welcome to [INSERT GAME NAME]!")
   updateStatus(milFalcon, universe)

   while (True):
      if (universe[milFalcon.currPlanet].planetType == "HOME"):
         print("Congratulations! You made it back home!")
         break
      
      userInput = input("$ ")

      if (userInput.split()[0] in commandList):
         if (userInput.split()[0] == "goto"):
            if (len(userInput.split()) != 2):
               print("- ERROR : Invalid command for 'goto'.")
            else:
               cmd_goto(int(userInput.split()[1]), milFalcon, universe)
         elif (userInput.split()[0] == "sell"):
            if (len(userInput.split()) != 3):
               print("- Error : Invalid command for 'sell'")
            else:
               cmd_sell(milFalcon, universe, userInput.split()[1], int(userInput.split()[2]))
         elif (userInput.split()[0] == "buy"):
            argc = len(userInput.split())
            if (argc == 3):
               cmd_sell(milFalcon, universe, userInput.split()[1], int(userInput.split()[2]))
            elif (argc == 2 and userInput.split()[1] == "gas"):
               cmd_sell(milFalcon, universe, userInput.split()[1], -1)
         else:
            commandList[userInput.split()[0]](milFalcon, universe)
      updateStatus(milFalcon, universe)

   return 0

# Main function to create the map and start the game.
def main ():
   milFalcon, universe = generateMap()
   startGame(milFalcon, universe)
   return 0


if __name__ == '__main__': main()
