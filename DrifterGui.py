#!/usr/bin/python
################################################################################
#                                                                              #
# DrifterGui.py -- The Graphical Game Implementation                           #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import random, sys, time

import pygame

sys.path.append("src/")
from src import Ship, Graphics

from DrifterCmd import *

##################################################################### Constants:
# COMMANDS #
CMD_QUIT       = pygame.K_q
CMD_HEAD_HOME  = pygame.K_z
CMD_DRIFT      = pygame.K_x
CMD_DEPART     = pygame.K_0
CMD_ORBIT_1    = pygame.K_1
CMD_ORBIT_2    = pygame.K_2
CMD_ORBIT_3    = pygame.K_3
CMD_ORBIT_4    = pygame.K_4
CMD_ORBIT_5    = pygame.K_5
CMD_ORBIT_6    = pygame.K_6
CMD_HARVEST_X  = 240           # Click on rectangular region within Planet.
CMD_HARVEST_Y  = 275
#CMD_JETTISON  = pygame.K_j
#CMD_BUY       = pygame.K_b
#CMD_SELL      = pygame.K_s
#CMD_REFINE    = pygame.K_r
#CMD_GAMBLE    = pygame.K_g
#CMD_ATTACK    = pygame.K_a

################################################################################
#TODO: print --> self.print : write to ship's console. Also create ships console
class GuiGame():
    '''Implements a Graphical version of The Game.'''
    def __init__(self,name="Testing",run=True):
        self.name    = name
        self.drifter = Ship.Ship()
        self.command = CmdLineGame(False,self.drifter)
        self.gfx     = Graphics.Graphics(self.name,self.drifter,self.command.backstory()+"\n\n"+self.command.commands())
        self.starChart = None
        if run: self.main() ; pygame.quit()
    def render(self,filename):
        print "DEBUG... Rendering"#TODO: Ensuring no extra rendering occurs.
        self.gfx.scene_gen(self.starChart,filename)
    def main(self):
        self.render("Backstory.png") ; pygame.display.flip()
        while True:
            for event in pygame.event.get():
                result = None ; status = GAME_CONTINUE
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    cmd = event.key

                    ###################################################### Quit:
                    if cmd == CMD_QUIT: return

                    ##################################################### Drift:
                    if cmd == CMD_DRIFT:
                        self.starChart = None
                        (result,status) = self.command.do(["drift"])
                        
                    ################################################# Head Home:
                    if cmd == CMD_HEAD_HOME:
                        self.starChart = None
                        (result,status) = self.command.do(["head"])

                    ############################################## Orbit Planet:
                    if cmd == CMD_ORBIT_1: (result,status) = self.command.do(["orbit","1"])
                    if cmd == CMD_ORBIT_2: (result,status) = self.command.do(["orbit","2"])
                    if cmd == CMD_ORBIT_3: (result,status) = self.command.do(["orbit","3"])
                    if cmd == CMD_ORBIT_4: (result,status) = self.command.do(["orbit","4"])
                    if cmd == CMD_ORBIT_5: (result,status) = self.command.do(["orbit","5"])
                    if cmd == CMD_ORBIT_6: (result,status) = self.command.do(["orbit","6"])

                    ############################################# Depart System:
                    if cmd == CMD_DEPART:  (result,status) = self.command.do(["depart"])
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (x,y) = event.pos
                    
                    ################################################### Harvest:
                    if x <= CMD_HARVEST_X and y <= CMD_HARVEST_Y:
                        (result,status) = self.command.do(["harvest"])

                ################################################################
                if result != None:
                    self.gfx.txt = ( result
                                   + "\n\n" + self.command.listCargo()
                                   + "\n\n" + self.command.commands() )
                    if self.name == "Testing": self.render(time.asctime())
                    else:                      self.render("Latest.png");
                    pygame.display.flip()
                if status == GAME_TERMINATE: return
                if status != GAME_CONTINUE:  self.drifter.time += 1

########################################################################## MAIN:
if __name__ == '__main__': GuiGame(time.asctime())
