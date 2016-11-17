#!/usr/bin/env python

################################################################################
#                                                                              #
# Graphics.py -- Graphics Functions                                            #
#                                                                              #
#   Western Washington University -- CSCI 4/597H -- Spring 2016                #
#                                                                              #
################################################################################

import os, sys, time, math, pygame

import Ship

from Cargo import planetType

##################################################################### Constants:
RAD = 0.0174533 # One Degree Radian

CRED_SYMBOL = u"\u00A2"  # "Cent"

## Tuning Parameters ##
SCREEN_SIZE = (WIDTH_FULL, HEIGHT_FULL) = (1600,1200)

## Round Dashboard ##
DASH_IMG_NAME = "dash-round-big.png"
FUEL_GUAGE_START_LOC = (283,1139)
FUEL_GUAGE_OFFSET    =  15.0
FUEL_GUAGE_LINE_LEN  =  113
FUEL_GUAGE_LINE_WID  =  6
SHIELD_STATUS_CENTER = (1264,926)
DASH_DELTA_TOP_RIGHT = (929,719)
DASH_CREDIT_TOP_LEFT = (1250,1138)
DASH_FONT_SIZE       =  42
TERM_TOP_LEFT        = (432,818)
TERM_FONT_SIZE       =  20
TERM_CHAR_WIDTH      =  61
PANL_FONT_SIZE       =  33
PANEL_TOP_LEFT       = (1223,6)
PANEL_CHAR_WIDTH     =  19
SHIELD_SCALE         = (120,120)

## Star Chart Properties ##
CHART_RING_INNER_LOC_X =  611
CHART_RING_DELTA_AVG   =  180
CHART_RING_MIDDLE_Y    =  560
CHART_PLANET_SCALE     = (240,240)

############################################################## Helper Functions:
def load_img(name):
    '''
    Function: load_img
    Parameter:
        name: The name of the image to load.
     The image is expected to be in the ./img directory
    '''
    name = os.path.join("img",name)
    try:
        img = pygame.image.load(name)
        if img.get_alpha() is None: img = img.convert()
        else: img = img.convert_alpha()
    except (pygame.error, message):
        #TODO: NameError: global name 'message' is not defined
        print ("ERROR: Unable to load image:", name)
        raise (SystemExit, message)
    return img

def save_img(me,dirName,fileName):
    '''
    Function: save_img
    Parameters:
        me: The image to be saved.
        dirName: The name of the directory to save the image in.
        fileName: The name of the file itself.
    '''
    dirName = os.path.join("dat",dirName)
    if not os.path.exists(dirName): os.makedirs(dirName)
    fileName = os.path.join(dirName,fileName)
    pygame.image.save(me,fileName)
    return fileName

def get_fuel_line_end(qt):
    '''
    Function: get_fuel_line_end
    Parameter:
        qt: The quantity of fuel to gauge.
     Determines the endpoint of the fuel gauge indicator line.
     The angle is offset by n degrees radian, and scaled by the qt as a percentage.
    '''
    import operator as op
    n = FUEL_GUAGE_OFFSET * RAD
    omega = n + (qt/100.0)*(math.pi - (2*n))
    y =  FUEL_GUAGE_LINE_LEN * math.sin(-omega)
    x = -FUEL_GUAGE_LINE_LEN * math.cos(-omega)
    return tuple(map(op.add, FUEL_GUAGE_START_LOC, (x,y)))

def chunkstring(string, length):
    '''http://stackoverflow.com/questions/18854620/whats-the-best-way-to-split-a-string-into-fixed-length-chunks-and-work-with-the'''
    return (string[0+i:length+i] for i in range(0, len(string), length))

##################################################################### PlanetSys:
class PlanetSys():
    #TODO: Have muliple planet images of each kind and randomize selection.
    #TODO: Rotate the spheres randomly to simulate time passing in orbit.
    def __init__(self):
        self.planetImg = {} ; self.planetImgBig = {}
        self.planetImg["Rocky" ] = load_img("planet000.png")
        self.planetImg["Water" ] = load_img("planet001.png")
        self.planetImg["Fire"  ] = load_img("planet002.png")
        self.planetImg["Barren"] = load_img("planet003.png")
        self.planetImg["City"  ] = load_img("city-overlay.png")
        self.planetImgBig["Rocky" ] = load_img("planet000-1440.png")
        self.planetImgBig["Water" ] = load_img("planet001-1440.png")
        self.planetImgBig["Fire"  ] = load_img("planet002-1440.png")
        self.planetImgBig["Barren"] = load_img("planet003-1440.png")
        self.planetImgBig["City"  ] = load_img("city-overlay-big.png")
        self.stockSolarSystemImg = load_img("star-chart-big.png" )
        self.panel               = load_img("panel-right-big.png")
        self.solarSystemImg = None
    def gen_sys(self,sysInfo):
        self.solarSystemImg = self.stockSolarSystemImg.copy()
        for i in range (0, sysInfo.qt):
            x = CHART_RING_INNER_LOC_X + i*CHART_RING_DELTA_AVG
            y = CHART_RING_MIDDLE_Y
            #TODO: Randomize location, ensure stagger, follow ellipse
            img = self.planetImg[sysInfo.planets[i].resource.kind].copy()
            img = pygame.transform.scale(img,CHART_PLANET_SCALE)
            img_rect = img.get_rect()
            img_rect.center = (x,y)
            self.solarSystemImg.blit(img,img_rect)
        return self.solarSystemImg

############################################################### ShieldIndicator:
class ShieldIndicator():#TODO: pre-scale images.
    def __init__(self):                                                                      #  STATUS  #
        self.images = [pygame.transform.scale(load_img("shield-red.png"),SHIELD_SCALE),      #  0 - 29  #
                       pygame.transform.scale(load_img("shield-orange.png"),SHIELD_SCALE),   # 30 - 49  #
                       pygame.transform.scale(load_img("shield-yellow.png"),SHIELD_SCALE),   # 50 - 69  #
                       pygame.transform.scale(load_img("shield-green.png"),SHIELD_SCALE),    # 70 - 89  #
                       pygame.transform.scale(load_img("shield-blue.png"),SHIELD_SCALE)]     # 90 - 100 #
    def get(self,status):
        if status < 30: return self.images[0]                                                # RED      #
        if status < 50: return self.images[1]                                                # ORANGE   #
        if status < 70: return self.images[2]                                                # YELLOW   #
        if status < 90: return self.images[3]                                                # GREEN    #
        else:           return self.images[4]                                                # BLUE     #

################################################################ Graphics Class:
class Graphics():
    '''
    screen: The display to which the graphics are rendered.
    name:      Name of current game. Used to organize saved images.
    player:    The Ship.
    sh:        The shield indicator object.
    sys:       Planet and solar system image resource object.
    txt:       The text to display on the ship's terminal.
    font:      The default font for the dashboard.
    term:      The font used in the ship's terminal.
    bg[_rect]: The background star-field image.
    db[_rect]: The dashboard image.
    '''
    def __init__(self,name,player,backstory=None):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.name = name
        self.player = player
        self.sh = ShieldIndicator()
        self.sys = PlanetSys()
        self.txt = backstory
        pygame.font.init()
        if pygame.font:
            self.font = pygame.font.SysFont("monospace",DASH_FONT_SIZE)
            self.font.set_bold(True)
            self.term = pygame.font.SysFont("monospace",TERM_FONT_SIZE)
            self.panl = pygame.font.SysFont("monospace",PANL_FONT_SIZE)
            # self.term.set_bold(True)
        else:
            print ("ERROR: Pygame: Unable to load font.")
            pygame.quit()
            sys.exit(1)
        self.bg = load_img("star-field.png")
        self.bg_rect = self.bg.get_rect()
        self.db = load_img(DASH_IMG_NAME)
        self.db_rect = self.db.get_rect()
    def scene_gen(self,sol_sys,fileName="latest.png"):
        '''Generate's Scene Image '''
        # Draw Background #
        if self.player.sys.pos == None:
              if sol_sys == None: sol_sys = self.sys.gen_sys(self.player.sys)
              self.screen.blit(self.sys.solarSystemImg,self.sys.solarSystemImg.get_rect())
        else: self.screen.blit(self.bg,self.bg_rect)
        self.screen.blit(self.db,self.db_rect) # Draw the Dashboard #

        # Draw Fuel Gauge Indicator #
        pygame.draw.line(self.screen, pygame.Color("red"),
            FUEL_GUAGE_START_LOC, get_fuel_line_end(self.player.fuel), FUEL_GUAGE_LINE_WID)

        # Draw Shield Status Indicator #
        splash = self.sh.get(self.player.health)
        splash_rect = splash.get_rect()
        splash_rect.center = SHIELD_STATUS_CENTER
        self.screen.blit(splash,splash_rect)
        txt = self.font.render(str(self.player.health),1,pygame.Color("black"))
        txt_rect = txt.get_rect()
        txt_rect.center = SHIELD_STATUS_CENTER
        self.screen.blit(txt,txt_rect)

        # Display Distance From Home #
        txt = self.font.render(str(self.player.delta),1,pygame.Color("yellow"))
        #TODO: Perhaps change color based on distance?
        txt_rect = txt.get_rect()
        txt_rect.topright = DASH_DELTA_TOP_RIGHT
        self.screen.blit(txt,txt_rect)

        # Display Universal Credits Balance #
        if self.player.credit < 0:
            txt = self.font.render(CRED_SYMBOL+str(self.player.credit),1,pygame.Color("red"))
        else:
            txt = self.font.render(CRED_SYMBOL+str(self.player.credit),1,pygame.Color("green"))
        txt_rect = txt.get_rect()
        txt_rect.topleft = DASH_CREDIT_TOP_LEFT
        self.screen.blit(txt,txt_rect)

        # Display Text on Ship Console #
        if self.txt != None:
            print(self.txt)
            i = 0 ; size = self.term.get_linesize()
            for line in self.txt.split("\n\n"):
                for txt in chunkstring(line,TERM_CHAR_WIDTH):
                    txt = txt.replace('\n',' ').lstrip()
                    txt = self.term.render(txt,1,pygame.Color("grey"))
                    txt_rect.topleft = TERM_TOP_LEFT
                    txt_rect.top += i * size
                    self.screen.blit(txt,txt_rect)
                    i += 1
                i += 1
        #TODO: Handle potential overflow, convert to method.

        # Draw Current Planet #
        if self.player.sys.pos != None:
            planet = self.player.sys.planets[self.player.sys.pos]
            kind   = planet.resource.kind
            splash = self.sys.planetImgBig.get(kind,"Barren")
            s_rect = splash.get_rect()
            s_rect.center = (0,0)
            self.screen.blit(splash,s_rect)
            if planet.resource.civ != None:
                splash = self.sys.planetImgBig.get("City")
                s_rect = splash.get_rect()
                s_rect.center = (0,0)
                self.screen.blit(splash,s_rect)
                splash = self.sys.panel
                s_rect = splash.get_rect()
                self.screen.blit(splash,s_rect)
                i = 1 ; size = self.panl.get_linesize()
                scanOutput = self.player.sys.scan().split("]")
                #TODO: Display more of scan information
                # scanOutput[0].split()
                #                      [0] ==  index/total               (TODO on dash)
                #                      [1] == "Civilized"                (can tell by city-overlay)
                #                      [2] == "Friendly|Neutral|Hostile" (done)
                #                      [3] ==  kind                      (can tell by planet image)
                txt = scanOutput[0].split()[2].lstrip()
                txt = self.font.render(txt,1,pygame.Color("black"))
                txt_rect.topleft = PANEL_TOP_LEFT
                self.screen.blit(txt,txt_rect)
                for line in scanOutput[1].split("}")[2].split(","):
                    for txt in chunkstring(line,PANEL_CHAR_WIDTH):
                        txt = txt.replace('\n',' ').replace('}','').replace('{','').lstrip()
                        #print ("TESTING:"+txt)
                        txt = self.panl.render(txt,1,pygame.Color("black"))
                        txt_rect.topleft = PANEL_TOP_LEFT
                        txt_rect.top += i * size
                        self.screen.blit(txt,txt_rect)
                        i += 1
                i += 1
                

        return save_img(self.screen,self.name,fileName)


############################################################## Main for Testing:
if __name__ == '__main__':
    scene_gen( "Testing", Ship.Ship() )
    # pygame.display.flip()
    pygame.quit()
