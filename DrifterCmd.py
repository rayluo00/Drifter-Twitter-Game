#!/usr/bin/env python
################################################################################
#                                                                              #
# DrifterCmd.py -- The Command Line Game Implementation                        #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import copy, random, re, sys, time

sys.path.append("src/")
from src import Ship
from src.Crafting import CRAFT_LIST
from src.Cargo import CIV_DAM_MIN, CIV_DAM_MAX

raw_input = input #python3


##################################################################### Constants:
STASIS_YEARS_MIN = 99
STASIS_YEARS_MAX = 666

GAME_ACTION    = -1   # The Command Has Been Executed
GAME_CONTINUE  =  0   # The Requested Command Was Invalid
GAME_TERMINATE =  1   # The Game Is Completed

################################################################################
class CmdLineGame():
    '''Implements a Command Line version of The Game.'''
    def __init__(self,run=True,ship=None):
        if ship == None: self.drifter = Ship.Ship()
        else:            self.drifter = ship
        self.validRegex = None
        self.stasisYears = 0
        self.validCmds = [
            ['orbit', 'PLANETS'],
            ['depart'],
            ['drift'],
            ['home'],
            ['harvest'],
            ['jettison', '#', 'INV'],
            ['buy', '#', 'P_INV'],
            ['sell', '#', 'INV'],
            ['attack'],
            ['refine', '#', 'INV'],
            ['gamble', '#'],
            ['repair'],
            ['craft', '#', 'CRAFT'],
            ['gm'],
            ['win'],
            ['lose']
        ]
        if run: self.main()
    def registerFun(self,winfun,loosefun):
        self.wingame = winfun
        self.losegame = loosefun
    def backstory(self):
        '''Return the backstory string.'''

        if not self.stasisYears:
            self.stasisYears = random.randint(STASIS_YEARS_MIN,STASIS_YEARS_MAX)

        #TODO: Add more randomized flavour.
        string  = "The last thing you remember before awaking from chryostasis,"
        string += " is the captain\nbeing decapitated by some flying debris. "
        string += "There was a battle. You don't know if\nthe enemy was destroyed,"
        string += " but obviously your ship is intact. The onboard computer\n"
        string += "reports that you have been in stasis for {} years. ".format(self.stasisYears)
        string += "The ship has been drifting\nthe entire time.\n\n"
        string += "You are {} light years from home, ".format(self.drifter.delta)
        string += "but the solar sails are functional.\n"
        if self.drifter.credit < 0:
            string += "You have a gambling debt of ${} universal credits.\n".format(-self.drifter.credit)
        string += "\nYou may return to stasis and allow the ship to drift at any time. "
        string += "Or, if you\nhave fuel, you can head toward home. "
        if self.drifter.sys.qt > 0: string += "Perhaps one of these nearby planets has\n"
        else: string += "If you happen upon a solar system with\nplanets, perhaps you may find "
        string += "something interesting.\n"
        return string
    def replaceNumbers(self, msg):
        numbers = {
            'first':  '1',
            'one':    '1',
            'second': '2',
            'two':    '2',
            'third':  '3',
            'three':  '3',
            'fourth': '4',
            'four':   '4',
            'fifth':  '5',
            'five':   '5',
            'sixth':  '6',
            'six':    '6'
        }
        msgSplit = msg.lower().split()
        for x in range(len(msgSplit)):
            if msgSplit[x] in numbers:
                msgSplit[x] = numbers[msgSplit[x]]
        msg = ' '.join(msgSplit)
        return msg
    def buildRegexFromList(self, listForRegex):
        buildRegex = '('
        for c in listForRegex:
            buildRegex += c + '|'
        buildRegex = buildRegex[:-1]
        buildRegex += ')'
        if buildRegex == ')':
            buildRegex = ''
        return buildRegex
    def buildCommandRegex(self):
        curCmds = self.commands().split(', ')
        #You can always drift
        curCmds.append('drift')
        print(curCmds)
        buildRegex = ''
        curRegex = ''
        #Copy the commands because we don't want to lose this list!
        validCmds = copy.copy(self.validCmds)
        #Remove commands not currently applicable
        for c in validCmds:
            if c[0] not in curCmds:
                validCmds.remove(c)

        for c in validCmds:
            curRegex = '(?P<{}>.*?'.format(c[0])
            for o in c:
                if o == '#':
                    curRegex += '(\d+)'
                elif o == '#O':
                    curRegex += '(\d*)'
                elif o == 'PLANETS':
                    planets = self.drifter.sys.qt
                    if planets:
                        curRegex += '([1-{}])'.format(planets)
                    else:
                        curRegex = ''
                        break
                elif o == 'INV':
                    inv = self.buildRegexFromList(self.drifter.cargo)
                    if inv:
                        curRegex += inv
                    else:
                        curRegex = ''
                        break
                elif o == 'P_INV':
                    if self.drifter.sys.pos != None and self.drifter.sys.planets[self.drifter.sys.pos].resource.civ:
                        pinv = self.buildRegexFromList(self.drifter.sys.planets[self.drifter.sys.pos].resource.civ.price)
                        if pinv:
                            curRegex += pinv
                        else:
                            curRegex = ''
                            break
                    else:
                        curRegex = ''
                        break
                elif o == 'CRAFT':
                    craft = self.buildRegexFromList(CRAFT_LIST)
                    if craft:
                        curRegex += '(' + craft + ')'
                    else:
                        curRegex = ''
                        break
                else:
                    curRegex += '(' + o.replace(' ', '.*?') + ')'
                curRegex += '.*?'
            if curRegex:
                buildRegex += curRegex + ')|'
        #Strip the last '|'
        buildRegex = buildRegex[:-1]
        print(buildRegex)
        #Save the regex
        self.validRegex = buildRegex
    def isValidCommand(self, cmd):
        validCommand = ''
        cmd = self.replaceNumbers(cmd)
        if not self.validRegex:
            self.buildCommandRegex()
        m = re.search(self.validRegex, cmd, re.I)
        if m:
            for x in m.groupdict():
                if m.group(x):
                    for y in range(len(m.groups())):
                        if x == m.groups()[y]:
                            print(y, m.groups())
                            for z in range(y, len(m.groups())):
                                print(z, m.groups()[z])
                                if z >= 1 and m.groups()[z] and m.groups()[z-1] != m.groups()[z]:
                                    validCommand += (m.groups()[z] + ' ')
                            break
                        # if y and (m.group(x) != y or x == y):
                        #     validCommand += (y + ' ')
            validCommand = validCommand[:-1]
            print("Valid Command: ", validCommand)
            return validCommand
        else:
            print("No valid command")
            return None
    def commands(self):
        '''Enumerate available commands into a string.'''
        string =               "Available commands are: drift"
        if self.drifter.fuel > 0: string          += ", home"
        if self.drifter.sys.pos != None:
            if self.drifter.sys.planets[self.drifter.sys.pos].resource.civ != None:
                attitude = self.drifter.sys.planets[self.drifter.sys.pos].resource.civ.Attitude()
                if attitude != "Hostile":
                    string                        += ", buy, sell"
                    if attitude == "Friendly":
                        string                    += ", refine, repair"
                string                            += ", gamble, attack"
            else: string                          += ", harvest"
        if self.drifter.sys.qt > 0:      string += ", orbit"
        if   len(self.drifter.cargo) > 0:  string += ", jettison"
        string += ", and quit.\n"
        return string
    def wingame(self):
        #TODO: Calculate Score -- Compare to High Score List
        return ('#' * (80-9) + " YOU WIN!\n",GAME_TERMINATE)
    def losegame(self,string):
        return (string + "\n" + '#' * (80-10) + " YOU LOSE!\n",GAME_TERMINATE)
    def status(self):
        '''Create status string.'''
        return "[T:{}|D:{}|F:{}|H:{}|${}]".format(
                self.drifter.time,   self.drifter.delta,
                self.drifter.fuel,   self.drifter.health,
                self.drifter.credit              )
    def listCargo(self):
        return "Cargo[{}%]:{}".format(
                int(100*(self.drifter.usedcap/self.drifter.cap)),
                self.drifter.cargo   )
    def holyWaterHack(self,string): #XXX#
        ''' XXX Change "Holy" to "Holy Water" XXX'''
        ''' Also Ensure Item is Capitalized '''
        string = string.capitalize()
        if string == "Holy": return "Holy Water"
        else:                return  string
    def main(self):
        ''' Play The Game. '''
        print(('#' * 80) + "\n" + self.backstory() + "\nIf you are still confused type 'help' at the prompt.\n")
        while True:
            print ("{}\n{}\nScan:{}".format( self.commands(),
                                             self.listCargo(),
                                             self.drifter.sys.scan() ))
            self.buildCommandRegex()
            try:
                cmdLine = raw_input(self.status()+" What will you do? ").split()
            except (EOFError) : cmdLine[0] = "quit" # CTRL-D Quits

            cmdLine2 = self.isValidCommand(' '.join(cmdLine))
            if cmdLine2:
                cmdLine = cmdLine2.split()

            (output,status) = self.do(cmdLine)
            print ("\n" + ('#' * 80) + "\n" + output)
            if status == GAME_TERMINATE: sys.exit(0)
            if status != GAME_CONTINUE:  self.drifter.time += 1
    def do(self,cmdLine):
            '''Perform a cmd and Return Result String and status.'''
            cmd = cmdLine[0]
            ############################################################## Help:
            if cmd == "help": #TODO Add command parameter
                return ("The ship status is described as so:\n\t"
                      +"[T:time|D:distance|F:fuel|H:health|$credits]"
                      +"\nWhere time is how many turns have elapsed. "
                      +"Distance is how far from home you\nare. "
                      +"Planets indicate how many are in the current system. "
                      +"And credits is the\nbalance of your universal monetary exchange account. "
                      +"\n\nThe planet scan is described as so:\n\t"
                      +"[i/n type]{health}[resource,list]"
                      +"\nWhere i is the number of the planet "
                      +"and n is quantity of planets in the system.\n",
                      GAME_CONTINUE)

            ############################################################## Quit:
            if cmd == "quit" or cmd == "exit" or cmd == "q":
                return self.losegame("\tSELF DESTRUCT SEQUENCE ACTIVATED!")

            ############################################################# Drift:
            if cmd == "drift":
                driftString = "The space craft is allowed to drift..."
                if self.drifter.sys.pos != None:
                    if self.drifter.sys.planets[self.drifter.sys.pos].resource.civ != None:
                        attitude = self.drifter.sys.planets[self.drifter.sys.pos].resource.civ.Attitude()
                        if attitude == "Hostile":
                            civDmg = random.randint(CIV_DAM_MIN, CIV_DAM_MAX)
                            self.drifter.harm(civDmg);
                            driftString += " The civilization attacked for {} as you tried to flee.".format(civDmg);
                            
                if self.drifter.drift(): return self.wingame()
                return (driftString,GAME_ACTION)

            ######################################################### Head Home:
            if cmd == "home":
                if self.drifter.goHome(): return self.wingame()
                return ("The ship autopilot is set to head home..." + "\n\n"
                    "You are awakened from chryostasis when the fuel runs out.",GAME_ACTION)

            ########################################################### Harvest:
            if cmd == "harvest":
                (alive,result) = self.drifter.harvest()
                if not alive: self.losegame("The local population rise against you and destroy the ship.")
                else: return ("Harvesting...\n\nFound: {}".format(result),GAME_ACTION)

            ###################################################### Orbit Planet:
            if cmd == "orbit":
                try:
                    planetNum = int(cmdLine[1]) - 1
                    (position,origin) = self.drifter.sys.orbit(planetNum)
                    if position != origin:
                        if position != None:
                            return ("Entering orbit of planet #{}".format(cmdLine[1]),GAME_ACTION)
                        else: return ("Orbit of planet #{} had decayed".format(cmdLine[1]),GAME_ACTION)
                    else: return ("",GAME_CONTINUE)
                except (IndexError, ValueError):
                    return ("?\n\tUsage: 'orbit n'",GAME_CONTINUE)

            ##################################################### Depart System:
            if cmd == "depart": #XXX Not Necessary && Costs Travel Time XXX#
                old = self.drifter.sys.pos
                if old != None: old+=1
                self.drifter.sys.pos = None
                return ("You leave the {} planet.".format(old),GAME_ACTION)

            #################################################### Jettison Cargo:
            if cmd == "jettison":
                try:
                    cmdLine[2] = self.holyWaterHack(cmdLine[2])
                    cmdLine[1] = self.drifter.jettison(int(cmdLine[1]),cmdLine[2])
                    return ("Jettisoning {} {}".format(cmdLine[1], cmdLine[2]),GAME_ACTION)
                except (IndexError, ValueError):
                    return ("?\n\tUsage: 'jettison n item'",GAME_CONTINUE)

            ####################################################### Buy or Sell:
            if cmd == "buy" or cmd == "sell":
                try:
                    cmdLine[2] = self.holyWaterHack(cmdLine[2])
                    (alive,cmdLine[1]) = self.drifter.shop(cmd,int(cmdLine[1]),cmdLine[2])
                    if not alive:
                        self.losegame("While trying to make a deal to {} {} {}".
                             format(cmd,cmdLine[1],cmdLine[2])
                            +", you were seized and put to death.")
                    else: return ("You {} {} {}.".format(cmd,cmdLine[1],cmdLine[2]),GAME_ACTION)
                except (IndexError, ValueError):
                    return ("?\n\tUsage: '{} n item'".format(cmd),GAME_CONTINUE)

            ############################################################ Attack:
            if cmd == "attack":
                (damDone,damSustained) = self.drifter.sys.attack()
                if not self.drifter.harm(damDone):
                    self.losegame("Your ship was destroyed in battle.") 
                return ("You attack for {} damage, while sustaining {} damage.".
                        format(damDone,damSustained),GAME_ACTION) 

            ############################################################ Repair:
            #NOTE : Repairing the ship uses the crafting system to check if the user's cargo
            #       meets the necessary requirements to repair the ship. Repairing ship increase
            #       ship's health by 15.

            #REQUIREMENTS: To repair the ship, the user must have these materials in their cargo.
            #              7 Metals , 3 Coolant , 2 Engine , 5 Glass

            if cmd == "repair":
                try:
                    if self.drifter.sys.pos and self.drifter.sys.planets[self.drifter.sys.pos].resource.civ:
                        attitude = self.drifter.sys.planets[self.drifter.sys.pos].resource.civ.Attitude()
                        if (attitude == "Friendly" or attitude == "Neutral"):
                            self.drifter.craft(1, cmdLine[0]);
                        else: return ("You're currently under attack! Get out before you try to repair.\n",GAME_CONTINUE)
                    else:
                        return ("You must orbit a civilized planet in order to repair!\n", GAME_CONTINUE)
                except (IndexError, ValueError):
                    return ("Unable to repair the ship.",GAME_CONTINUE)

            ############################################################ Refine:
            if cmd == "refine": #TODO: Planet charges for this service?
                try:
                    cmdLine[2] = self.holyWaterHack(cmdLine[2])
                    (alive,result) = self.drifter.refine(int(cmdLine[1]),cmdLine[2])
                    if not alive: self.losegame("You were caught tresspassing in "
                            +  "the refinery, seized, and put to death.")
                    return ("Refining {} {}...\n\nResult: {}".format(cmdLine[1],cmdLine[2],result),GAME_ACTION)
                except (IndexError, ValueError):
                    return ("?\n\tUsage: 'refine n item'",GAME_CONTINUE)

            ############################################################ Gamble:
            if cmd == "gamble":
                try:
                    (alive,result,dam) = self.drifter.gamble(int(cmdLine[1]))
                    if dam > 0: damage = "Another gambler accused you of cheating and attacks for {} damage!".format(dam)
                    else:       damage = ""
                    if not alive:
                        self.losegame("Another gambler accused you of cheating."
                            + " You have been seized and put to death.")
                    if result == None: return ("You make a bet with yourself and win!",GAME_ACTION)
                    if result < 0: return (damage+"You gamble away {} credits!".format(-result),GAME_ACTION)
                    else:          return (damage+"You make a bet for {} and win {}".format(cmdLine[1],result),GAME_ACTION)
                except (IndexError, ValueError):
                    return ("?\n\tUsage: 'gamble bet'",GAME_CONTINUE)

            ############################################################# Craft:
            if cmd == "craft":
                try:
                    craftString = self.drifter.craft(int(cmdLine[1]),cmdLine[2])
                    return (craftString,GAME_ACTION)
                except (IndexError, ValueError):
                    return ("?\n\tUsage: 'craft n item'",GAME_CONTINUE)

            ############################################################### God:
            if cmd == "gm":
                self.drifter.gm()
                return("You unlock the secrets of the universe!",GAME_CONTINUE)

            if cmd == "win":
                return self.wingame()
            if cmd == "lose":
                return self.losegame()

            ####################################################################
            return ("\"{}\" is an invalid command.".format(cmd),GAME_CONTINUE)
            #Or: self.do("drift",None)

########################################################################## MAIN:
if __name__ == '__main__': CmdLineGame()
