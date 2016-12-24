# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 18:15:59 2015

@author: Cyprien et Frederic MICHEL--DELETIE
"""
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import pygame
from copy import copy
import glob
import math

import CoutCartesMonstres
import deck_creation
import Player

import CardGame
#import pickle

from types import MethodType

from outils import name2file,file2name

ORANGE = (200,100,0)
BLUE = (0,30,150)
GREEN = (0,200,20)
BLACK = (0,0,0)
RED =(255,0,0)

blocked_decks = deck_creation.blocked_decks
# print glob.glob("*")
playable_decks = [file2name(d,'.dek') for d in glob.glob("Decks/*.dek")]
all_decks = copy(playable_decks)

for d in reversed(playable_decks):
    if d in blocked_decks:
        playable_decks.remove(d)

img_campaign_button = pygame.image.load("gameAnimationImages/PlayCampaignButton.png")
img_cardedit_button = pygame.image.load("gameAnimationImages/CardEditorButton.png")
img_deckcreation_button = pygame.image.load("gameAnimationImages/ChangeDeckButton.png")
img_playmission_button = pygame.image.load("gameAnimationImages/PlayMissionButton.png")
img_battle_button = pygame.image.load("gameAnimationImages/PlayBattleButton.png")
img_blank_button = pygame.image.load("gameAnimationImages/BlankButton.png")

if len(glob.glob("Cards/*.png"))<10 :
    print " Cards not found "
    execfile('./TouchMonsterFiles.py')

all_cards = {}
from Card import readMonsters
for fn in glob.glob("CardFiles/all*.sav") :
    #print "load cards in ",f
    d = readMonsters(fn)
    all_cards.update(d)



def is_around(i,ii,length):
    if ii < i -length or ii > i +length:
        return False
    else:
        return True

class Level():
    def __init__(self):
        pass
    def show(self):
        print "Opponent: ",self.opponent.name
        print "scenario ",self.scenario
        print "Difficulty: ", self.difficulty

    def makeImage(self):
        image = pygame.Surface((900,600))
        image.fill((255,255,255))
        img_avatar = pygame.transform.scale(pygame.image.load("Avatars/"+self.avatar),(150,150))
        w,h = img_avatar.get_size()
        image.blit(img_avatar,(650-w/2,100-h/2))
        font = pygame.font.SysFont("Calibri",24)
        text = font.render("Difficulty: "+self.difficulty,False,(3,0,0))
        text2 = font.render("Opponent: "+self.opponent.name,False,(3,0,0))
        image.blit(text,(100,80))
        image.blit(text2,(100,120))
        font = pygame.font.SysFont("Calibri",14)
        scenario = self.scenario
        text3="" ; text=[]
        for let in scenario :
            text3+=let
            if let==" " and len(text3)>100:
                text.append(text3)
                text3=""
        text.append(text3)
        for i,t in enumerate(text) :
                line = font.render(t,False,(3,0,0))
                image.blit(line,(100,190+i*25))
        image.set_colorkey((255,255,255))
        return image

    def lockedImage(self):
        image = pygame.Surface((600,600))
        image.fill((255,255,255))

        font = pygame.font.SysFont("Calibri",24)
        text = font.render("Level Locked: ",False,(3,0,0))
        text2 = font.render("Achieve previous level to unlock ",False,(3,0,0))
        image.blit(text,(100,80))
        image.blit(text2,(100,120))
        image.set_colorkey((255,255,255))
        return image


class Button(pygame.sprite.Sprite):

    def __init__(self,x_center,y_center,image,fonction,game,argus):

        self.game = game
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.convert_alpha()
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = x_center - self.size[0]/2
        self.rect.y = y_center - self.size[1]/2
        self.functiun = fonction
        self.argus = argus

    def update(self):
        if is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2):
            if self.game.click == True:
                self.functiun(*self.argus)

class DeckButton(Button):
    def __init__(self,x_center,y_center,image,fonction,game,argus,deck_name):
        Button.__init__(self,x_center,y_center,image,fonction,game,argus)
        #print " deck name is",deck_name
        size = (1500,2000)
        font_size = 36
        if deck_name != "NET BATTLE" :
          with open(name2file("Decks",deck_name,".dek"),"r") as fil:
            deck = eval(fil.read())
            del deck["AvatarImage"]
            [all_cards[k[0]].getCost() for k in deck.items()] # a cause de RaleDAgonie qui a besoin d un appel a getcost avant
            try :
                stars = sum([all_cards[k[0]].getStars()*k[1] for k in deck.items()] )
            except :
                print " in ",all_cards.keys(), " looking for ",deck.keys()
                raise
            if stars>15 and len(argus)!=2:
                self.accessible = False
                color = RED
                def updat(self):
                    pass
                self.update = MethodType(updat,self)
            elif stars>15:
                self.accessible = True
                color = RED
            else:
                self.accessible = True
                color = GREEN
        else :
            color=BLUE
            self.accessible=True
            stars=0

        while size[0]>self.size[0]-30:
            self.image = copy(image)
            font = pygame.font.SysFont("Heraldic",font_size,italic=True,bold=True)
            text = font.render(deck_name+"- "+(str(stars)+"*")*(stars!=0),False,color)
            size = font.size(deck_name+"- "+(str(stars)+"*")*(stars!=0))
            self.image.blit(text,(self.size[0]/2-size[0]/2,self.size[1]/2-size[1]/2))
            font_size-=1

class PlayerImage(pygame.sprite.Sprite):
    def __init__(self,x_center,y_center,image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image.set_colorkey(BLACK)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = x_center-self.size[0]/2
        self.rect.y = y_center-self.size[1]/2

class Profile():
    def __init__(self,name,deckname,game,level):
        self.name = name
        self.deckname = deckname
        self.game = game
        self.level = level

class Viewer(pygame.sprite.Sprite):
    def __init__(self,image,(x,y)):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game():
    def __init__(self):

        self.previous = self.modeSelection

        self.all_sprites_list = pygame.sprite.Group()
        #self.steps = [None,self.modeSelection,self.matchSelection]

        level1=Level()
        level1.image= pygame.image.load("gameAnimationImages/level3.jpg")
        level1.opponent = Profile("Seth le Cruel","Horde",self,2)
        level1.difficulty = "Easy"
        level1.scenario = ["Alors que vous achetiez des poissons, vous entendez des bruits d'armes. Votre village est attaque!!! "+
        "Les troupes du Gobelin Seth prennent d'assaut la ville, profitant de l'absence de l'armee locale en croisade. "+
        "Vous accourez donc evidemment avec vos hommes au secours du village et combatez les etres brutaux de la horde."][0]
        level1.avatar = "Gobelin#.png"

        level2 = Level()
        level2.image= pygame.image.load("gameAnimationImages/level2.jpg")
        level2.opponent = Profile("Otehir le Robuste","Nains de Omaghetar",self,2)
        level2.difficulty = "Easy"
        level2.scenario = ["Alors que vous recuperiez l'armement des gobelins, vous remarquez une marque distincte sur les armes. Cette marque est celle des nains de la mine de Omaghetar"+
        " dont les actions sont depuis longtemps tennues secretes." + " C'est surement eux qui armaient les gobelins, pour toucher un peu de leurs benefices et eliminer leurs rivals. "+
        "L'objectif de votre mission: Allez a la mine et tuez leur chef, Otehir le Robuste."][0]
        level2.avatar = "Roi_des_Nains#.png"


        level3 = Level()
        level3.image= pygame.image.load("gameAnimationImages/level1.jpg")
        level3.opponent = Profile("Le viking inconnu","Vikings",self,2)
        level3.difficulty = "Medium"
        level3.scenario = ["Alors que vous dormiez pres de la mer, des vikings debarquent a grand cris. "+
        "Si personne ne les arrete, il est clair qu'ils massacreront la population avant l'arrivee de renforts. "+
        "Vos hommes sont prets, il ne vous reste plus qu'a vous mettre en travers de leur route. "][0]
        level3.avatar = "Vikings#.png"

        level31 = Level()
        level31.image= pygame.image.load("gameAnimationImages/level31.jpg")
        level31.opponent = Profile("Seigneur Demon","Demon",self,2)
        level31.difficulty = "Medium"
        level31.scenario = ["Vous avez vaincu la horde, mais le chef du village, un de vos proches, est gravement blesse. "+
        "Il paraitrait qu'il existe un sort permettant de soigner le chef, decrit dans \"Maitrise de la Magie Cyclique \", un grimmoire "+
        "magique detenu par le mage Antonidus. Alors que vous lui avez poliment demande, il vous rit au nez et vous defie de le vaincre. "+
        "Vous etes donc contraint a vous battre. Mais a votre arrivee le mage se lance dans des incantations interdites et invoque une armee de demon dirige par un puissant seigneur. "][0]
        level31.avatar = "Demon#.png"

        level4=Level()
        level4.image= pygame.image.load("gameAnimationImages/level4.jpg")
        level4.opponent = Profile("Archimage Antonidus","Mauvais Reves",self,2)
        level4.difficulty = "Hard"
        level4.scenario =  [" Le mage est surpris de votre victoire contre les demons, mais il est loin d'etre sans defences. "+
        " Il invoque a ses cotes des creatures issues des plus mauvais reves..."][0]
        level4.avatar = "ArchmageAntonidusHearthstone#.png"

        level5=Level()
        level5.image= pygame.image.load("gameAnimationImages/level5.jpg")
        level5.opponent = Profile("Legion des morts","Necroman",self,2)
        level5.difficulty = "Hard"
        level5.scenario = ["Alors que vous tentez vous meme d'executer les instructions du livre, le chef du village se releve brusquement. "+
        "Vos rejouissances sont courtes: vous constatez avec effroi son regard vitreux et comprenez qu'il n'est plus qu'un mort-vivant! " +
        "L'archimage s'est joue de vous et a modifie le livre pour vous faire executer une incantation interdite. "+
        "Et votre ami n'est pas le seul, tout les morts de la region se levent, animes par une soif de carnage. "][0]
        level5.avatar = "Legion#.png"

        level6=Level()
        level6.image= pygame.image.load("gameAnimationImages/level6.jpg")
        level6.opponent = Profile("Chateau","Chateau",self,2)
        level6.difficulty = "Hard"
        level6.scenario = ("Vous revenez victorieux sous les acclamations de la foule. "+
        "Pourtant, le roi vous reserve un accueil froid, derange par votre popularite et votre puissance. " +
        "Il vous donne un titre de noblesse tres tres loin dans le nord. "+
        "Quoi ! Allez vous laisser ce roi vous imposer un exil, alors qu il merite moins son trone que vous ? ")
        level6.avatar = "LeRoi#.png"

        self.all_levels = [level1,level2,level3,level31,level4,level5,level6]
        progress = open("progression","r")
        progress.seek(0,0)
        self.level_prog = int(progress.read())
        progress.close()
        print "Level are done until level: ",self.level_prog
        self.unlocked_levels = self.all_levels[:self.level_prog]
        self.achievment = None

        self.bg_color = ORANGE
    def update(self):
        self.click = False
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.slaughter()
                    self.previous()
        pygame.display.set_caption("Magic Card Battle")
        self.all_sprites_list.update()
        self.all_sprites_list.draw(screen)

    def slaughter(self):
        for b in self.all_sprites_list:
            b.kill()
        #del self.steps[0]
        #if self.steps:
        #    self.steps[0]()

    def initialize(self):
        self.modeSelection()

    def modeSelection(self):
        self.bg_color = ORANGE
        button = Button(450,110,img_campaign_button,self.Exemple,self,[])
        self.all_sprites_list.add(button)
        button = Button(450,295,img_cardedit_button,self.coutCartesMonstres,self,[])
        self.all_sprites_list.add(button)
        button = Button(450,460,img_deckcreation_button,self.deckCreation,self,[])
        self.all_sprites_list.add(button)
        button = Button(450,635,img_battle_button,self.initDeckSelection,self,[])
        self.all_sprites_list.add(button)

    def matchSelection(self):
        self.play_button = self.viewer = None
        for n,i in enumerate(self.all_levels):
            if i in self.unlocked_levels:
                locked = False
                image = pygame.transform.scale(i.image,(120,90))
            else:
                locked = True
                image = pygame.transform.scale(pygame.image.load("gameAnimationImages/locked-door.png"),(120,90))
            button = Button(100,110*(n+1)-50,image,self.displayMatch,self,[i,n,locked])
            self.all_sprites_list.add(button)
        self.previous = self.modeSelection

    def deckSelection(self,n,deck):
        self.slaughter()
        self.bg_color = BLUE
        #print "n is :",n
        image = pygame.transform.scale(pygame.image.load("gameAnimationImages/BlankButton.png"),(240,100))
        if n==0:
            list_ = playable_decks
        else:
            list_ =  all_decks
        l = len(list_)
        print "list_",list_
        if n==2 : l+=1
        for x,i in enumerate(list_):
            angle = (x+1)*360/l
            x_center = int(math.sin(math.radians(angle))*300) + size[0]/2
            y_center = int(math.cos(math.radians(angle))*300) + size[1]/2
            #print x_center,y_center,angle
            if n==2:
                button = DeckButton(x_center,y_center,image,self.playBattle,self,[deck,i],i)
                self.all_sprites_list.add(button)
                #print "level 2 selection"
            elif n==0:
                button = DeckButton(x_center,y_center,image,self.playLevel,self,[i],i)
                self.all_sprites_list.add(button)
            else:
                button = DeckButton(x_center,y_center,image,self.deckSelection,self,[2,i],i)
                self.all_sprites_list.add(button)
                #print "level 1 selection"
        image2 = pygame.image.load(["gameAnimationImages/PlayerButton1.png","gameAnimationImages/PlayerButton1.png","gameAnimationImages/PlayerButton2.png"][n])
        if not(n == 2):
            self.all_sprites_list.add(PlayerImage(size[0]/2,size[1]/2,image2))
        else:
            angle = 360.
            x_center = int(math.sin(math.radians(angle))*300) + size[0]/2
            y_center = int(math.cos(math.radians(angle))*300) + size[1]/2
            #print x_center,y_center,angle
            button = DeckButton(x_center,y_center,image,self.startNetGame,self,[deck],"NET BATTLE")
            self.all_sprites_list.add(button)
            
            self.adv_type_button = Button(size[0]/2,size[1]/2,image2,self.changePlayerType,self,[])
            self.all_sprites_list.add(self.adv_type_button)
        self.previous = self.initDeckSelection
                
    def initDeckSelection(self):
        self.adversory_type = "Computer"
        self.deckSelection(1,None)
        self.previous = self.modeSelection

    def changePlayerType(self):
        if self.adversory_type == "Player":
            self.adversory_type = "Computer"
        else:
            self.adversory_type = "Player"
        self.adv_type_button.kill()
        image = pygame.image.load(["gameAnimationImages/PlayerButton2.png","gameAnimationImages/PlayerButton3.png"][self.adversory_type=="Player"])
        self.adv_type_button = Button(size[0]/2,size[1]/2,image,self.changePlayerType,self,[])
        self.all_sprites_list.add(self.adv_type_button)

    def Exemple(self):
        self.slaughter()
        self.matchSelection()

    def coutCartesMonstres(self):
        CoutCartesMonstres.run()
        pygame.init()
        global screen

        screen = pygame.display.set_mode((900,800))
        self.slaughter()
        self.__init__()
        self.initialize()

    def deckCreation(self):
        deck_creation.run()
        global playable_decks
        playable_decks = [file2name(d,'.dek') for d in glob.glob("Decks/*.dek")]
        global all_decks
        all_decks = copy(playable_decks)
        for d in reversed(playable_decks):
            if d in blocked_decks:
                playable_decks.remove(d)

    def displayMatch(self,level,num,locked):
        print "Match number {0} selected".format(num)
        if not(locked):
            if self.play_button:
                self.play_button.kill()
            self.play_button = Button(475,400,pygame.transform.scale(img_playmission_button,(310,110)),self.selectMatch,self,[level,num])
            self.all_sprites_list.add(self.play_button)
            level.show()
            if self.viewer:
                self.viewer.kill()
            self.viewer = Viewer(level.makeImage(),(100,20))
            self.all_sprites_list.add(self.viewer)
            if self.achievment:
                self.achievment.kill()
            self.achievment = Viewer(pygame.transform.scale(pygame.image.load(["gameAnimationImages/AchievmentEmpty.png","gameAnimationImages/AchievmentDone.png"][self.level_prog>num+1]),(100,100)),(750,650))
            self.all_sprites_list.add(self.achievment)

        else:
            print "Level Locked"
            if self.play_button:
                self.play_button.kill()
            if self.viewer:
                self.viewer.kill()
            if self.achievment:
                self.achievment.kill()
                self.achievment = None
            self.viewer = Viewer(level.lockedImage(),(100,20))
            self.all_sprites_list.add(self.viewer)

    def selectMatch(self,level,num):
        self.deckSelection(0,None)
        self.previous = self.modeSelection
        self.level_selected = level
        self.num = num

    def playLevel(self,deck):
        level = self.level_selected
        print "Match number {0} played".format(self.num)
        import CardGame
        gam = CardGame.Game()
        deck1=gam.chooseDeck(deck,1)
        gam.player1=Player.Player("Player",deck1,gam)#,2,verbose=0,hide=False)
        gam.player2=Player.Computer(level.opponent.name,gam.chooseDeck(level.opponent.deckname,2),gam,level.opponent.level,verbose=0,hide=True)
        if "" in deck1 :
            gam.player1.avatar_img=pygame.image.load(deck1[""])
        else :
            gam.player1.avatar_img=pygame.image.load("Avatars/Chevalier_noir#.png")
        gam.player2.avatar_img=pygame.image.load("Avatars/"+level.avatar)
        gam.initialize()
        gam.play()
        winner = gam.get_winner() # player name or None if quit manually
        if winner == "Player" and self.level_prog==self.all_levels.index(level)+1:
            print "progression advanced"
            self.level_prog += 1
            progress = open("progression","w")
            progress.write(str(self.level_prog))
            progress.close()
            self.unlocked_levels = self.all_levels[:self.level_prog]

        self.slaughter()
        size = (900, 800)
        global screen
        screen = pygame.display.set_mode(size)
        self.initialize()

    def playBattle(self,deck1,deck2):
        print "Arena Battle between {0} and {1}".format(deck1,deck2)
        gam = CardGame.Game()
        gam.player1=Player.Player("Player",gam.chooseDeck(deck1,1),gam)#,2,verbose=0,hide=False)
        if self.adversory_type == "Computer":
            gam.player2=Player.Computer("Opponent",gam.chooseDeck(deck2,2),gam,2,verbose=0,hide=True)
        else:
            gam.player2=Player.Player("Player 2",gam.chooseDeck(deck2,2),gam)
        gam.player1.avatar_img=None
        gam.player2.avatar_img=None
        gam.initialize()
        gam.play()
        self.slaughter()
        size = (900, 800)
        global screen
        screen = pygame.display.set_mode(size)
        self.initialize()

    def startNetGame(self,deck_name) :
        print "play net game with deck",deck_name
        from CardGame import NetGame
        from Player import Player,HostedPlayer
        game = NetGame()
    #game.defaultPlayers(player1_set,player2_set)   
        game.player1=Player("Player",game.chooseDeck(deck_name),game)
        game.player2=HostedPlayer(game)
        game.initialize()
        game.play()



pygame.init()

size = (900, 800)
screen = pygame.display.set_mode(size)

game = Game()

clock = pygame.time.Clock()

game.done = False
game.initialize()

"""
game.adversory_type = "Computer"

scores = {}
for d in decks:



for i in all_decks[:1]:
    for x in all_decks[:1]:
        game.playBattle(i,x)
 """


while not(game.done):
    screen.fill(game.bg_color)
    game.update()
    pygame.display.flip()
    clock.tick(30)


pygame.quit()
