#!/usr/bin/env python
################################################################################
#                                                                              #
# Drifter.py -- The Twitter Game Implementation                                #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

#System libraries
import datetime, io, random, sys, time

#Extra libraries
import pygame, twitter
from web import web

#Game libraries
sys.path.append("src/")
from src import Ship, Graphics
from DrifterCmd import *

##################################################################### Constants:

################################################################################
class TwitterGame():
    '''Implements a Twitter version of The Game.'''
    def __init__(self,name="Testing",run=True):
        self.name = name
        self.twitter = twitter.Twitter(self.name)
        self.starChart = None
        self.savedState = None
        while run: 
            self.drifter = Ship.Ship()
            self.command = CmdLineGame(False,self.drifter)
            self.command.commands = self.commands #Overwrite the command list to build a better regex
            self.command.registerFun(self.wingame,self.losegame)
            self.gfx = Graphics.Graphics(self.name,self.drifter,self.command.backstory()+"\n\n"+self.command.commands())
            if self.savedState:
                (self.drifter.cargo,self.drifter.credit) = self.savedState
            self.main()
        pygame.quit()

    def commands(self):
        '''Enumerate available commands into a msg.'''
        msg =                                     "drift"
        if   self.drifter.fuel > 0:        msg += ", home"
        if self.drifter.sys.pos != None:
            if self.drifter.sys.planets[self.drifter.sys.pos].resource.civ != None:
                attitude = self.drifter.sys.planets[self.drifter.sys.pos].resource.civ.Attitude()
                if attitude != "Hostile":
                    msg                        += ", buy, sell"
                    if attitude == "Friendly":
                        msg                    += ", refine, repair"
                msg                            += ", gamble, attack"
            msg                                += ", harvest"
        if self.drifter.sys.qt > 0:        msg += ", orbit"
        if   len(self.drifter.cargo) > 0:  msg += ", jettison"
        msg += ", win, lose"
        return msg
        
    def losegame(self):        
        self.gfx.txt = self.command.backstory()+"\n\n"+self.command.commands()
    def wingame(self):
        self.gfx.txt = ( "Congratulations! You have made it home!\n\n"
                     + "The enemy appears--seemingly out of nowhere.\n\n"
                     + "You are under attack!\n\n"
                     + "Emergency!!   Emergency!!\n\n"
                     + "All hands report to chryostasis immedetly!" )
        self.render("latest.png")
        self.twitter.sendTweet('', self.imgFileName)
        self.savedState = (self.drifter.cargo,self.drifter.credit)
    def render(self, filename):
        print("DEBUG... Rendering") #TODO: Ensuring no extra rendering occurs.
        self.imgFileName  = self.gfx.scene_gen(self.starChart,filename)
        pygame.display.flip()
        web.writeWeb(self.command.stasisYears, self.drifter.delta, self.drifter.credit)

    def main(self):
        ''' Play The Game. '''
        dispTop5 = True #Flag to say if we simply display the top 5, or run the top command
        result = None
        status = GAME_CONTINUE

        self.render("backstory.png") ; pygame.display.flip()

        while True:
            self.command.buildCommandRegex()
            self.twitter.isValidCommand = self.command.isValidCommand

            self.render("latest.png")

            try:
                print("Sending tweet with image...",)
                self.twitter.sendTweet('', self.imgFileName)
                print("Sent!")
            except:
                #Some twitter error occured, just keep polling
                print("Error sending tweet!\nSleeping for 15 MINUTES!!!")
                time.sleep(15 * 60)
                dispTop5 = True
                continue

            x = 1.5
            print("Sleeping for %.1f minutes...\n" % x)
            time.sleep(x * 60)

            print("I have awoken! Time to read the tweetmails!\n")

            try:
                tweets = self.twitter.getTweets()
                top5 = self.twitter.findTop5Votes()
            except:
                #Some twitter error occured, just keep polling
                print("Error getting tweets!\nSleeping for 15 MINUTES!!!")
                time.sleep(15 * 60)
                dispTop5 = True
                continue

            if dispTop5:
                #Only display the top 5, don't execute them
                print("Top 5 tweeted commands:\n", top5)
            else:
                #Run the top voted command!
                if len(top5) > 0:
                    cmdLine = top5[0][0].split()
                    cmd = cmdLine[0]
                    #Flag the winning votes
                    self.twitter.setSuccess(top5[0][0])
                    self.twitter.logTweets()
                    self.twitter.resetTweets()
                else:
                    cmdLine = ('drift',)
                    cmd = 'drift'

            #Toggle display/execute
            dispTop5 = (not dispTop5)
            #We just displayed the top 5, we didn't actually run a command
            #Just go back to the loop and sleep again
            if not dispTop5:
                self.gfx.txt = ( self.twitter.top5ToString(top5)
                                 + "\n\n" + self.command.listCargo()
                                 + "\n\nAvailable commands:\n\n" + self.command.commands() )
                continue

            #Some commands require us to update the star chart, most do not

            ############################################################# Drift:
            if cmd == "drift": #TODO Drifting while under attack is dangerous.
                self.starChart = None
                (result, status) = self.command.do(["drift"])
                if status == GAME_TERMINATE: return self.wingame()

            ######################################################### Head Home:
            elif cmd == "home":
                self.starChart = None
                (result,status) = self.command.do(["head"])
                if status == GAME_TERMINATE: return self.wingame()
            elif cmd == 'win':
                self.starChart = None
                return self.wingame()
            elif cmd == 'lose':
                self.starChart = None
                (result,status) = ("You haved failed to return home.",GAME_TERMINATE)
            ################################################### Everything else:
            else:
                (result,status) = self.command.do(cmdLine)

            ####################################################################
            if status == GAME_TERMINATE:
                self.gfx.txt = result + "\n\nGame will reset..."
                self.render("latest.png")
                self.twitter.sendTweet('', self.imgFileName)
                return self.losegame()
            if result != None:
                self.gfx.txt = ( self.twitter.top5ToString(top5)
                                 + result
                                 + "\n\n" + self.command.listCargo()
                                 + "\n\nAvailable commands:\n\n" + self.command.commands() )
                self.render("latest.png")

            if status != GAME_CONTINUE:  self.drifter.time += 1

########################################################################## MAIN:
if __name__ == '__main__': TwitterGame('zmcbot')
