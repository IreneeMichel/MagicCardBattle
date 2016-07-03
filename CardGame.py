import os
import glob
import pygame
#import pickle
import traceback
os.chdir(os.path.dirname(os.path.realpath(__file__)))
"""
decks = open("all_decks.sav", "rb")
decks.close()
all_decks = pickle.load( open( "all_decks.sav", "rb" ))
"""
pygame.init()

from copy import copy
from Card import Card
from cardPowers import *
from Player import Player,Computer,Computer0
#from Creature import Creature,AnimatedCreature
from Sprites import Mouse,EndButton,HeroButton, ZoomOn
from random import choice

def g(self,i) :
     return self.sprites()[i]
pygame.sprite.OrderedUpdates.__getitem__=g # to be able to use reversed() on group
pygame.sprite.OrderedUpdates.append=pygame.sprite.OrderedUpdates.add  # to make group equivalent to list
def ind(self,obj) :
    return self.sprites().index(obj)
pygame.sprite.OrderedUpdates.index=ind
def ad(self,li2) :
    li1=copy(self)
    for i in li2 :
        li1.append(li2)
    return li1
pygame.sprite.OrderedUpdates.__add__=ad

        
BLACK = 0,0,0
BROWN = 90,60,20

card_back_img = pygame.image.load("gameAnimationImages/CardDosArgentum.png")
card_back_img = pygame.transform.scale(card_back_img,(163,240))



class Game():
    def __init__(self):
        pygame.init()
        #self.to_draw = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        try :
            from win32api import GetSystemMetrics
            dim=(GetSystemMetrics(0),GetSystemMetrics(1))
        except :
            dim=(1000,600)
        self.height = int(dim[1]*1.)
        self.width = int(dim[0]*1.)
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.bg = pygame.transform.scale(pygame.image.load("gameAnimationImages/background"+str(choice([1,2,3]))+".png"),(self.width,self.height))
        #background = pygame.image.load("gameAnimationImages/background.png")
        
        
        self.all_sprites = pygame.sprite.OrderedUpdates()
        self.temporary_sprites=pygame.sprite.OrderedUpdates()
        self.mouse = Mouse()
        self.all_sprites.add(self.mouse)
        self.endturn_button = EndButton((self.width,self.height))
        self.all_sprites.add(self.endturn_button)
        
        self.zoomed=None
        self.animation_runing = False
        self.all_animations = []
        
        self.screen.fill(BROWN)
        pygame.display.flip()
        #player = player1
        self.turn = 1
        self.winner = None
        self.end = False   # a changer peut etre par appel de game.end()
        self.player1_avatar = self.player2_avatar = None
        self.mouse_icon = pygame.sprite.GroupSingle()
        self.mouse_icon.add(self.mouse)
    
    def defaultPlayers(self,set1,set2):
        #self.player1=Player(set1[0],self.chooseDeck(set1[1],1),self)
        self.player1=Computer(set1[0],self.chooseDeck(set1[1]),self,2,verbose=1,hide=False)
        self.player2=Computer(set2[0],self.chooseDeck(set2[1]),self,2,verbose=1,hide=False)
        if set1[2]!=None:
            self.player1.avatar_img=pygame.image.load(set1[2])            
        if set2[2]!=None:
            self.player2.avatar_img=pygame.image.load(set2[2])
        
        self.initialise()
    
    def initialise(self):
        if self.player1_avatar and not(hasattr(self.player1,"avatar_img") and self.player1.avatar_img):
            self.player1.avatar_img = self.player1_avatar
        else:
            if not(hasattr(self.player1,"avatar_img") and self.player1.avatar_img):                
                print "ERROR NO AVATAR FOR PLAYER 1"
                self.player1.avatar_img=pygame.image.load("Avatars/Chevalier_noir#.png")
        if self.player2_avatar and not(hasattr(self.player2,"avatar_img") and self.player2.avatar_img):
            self.player2.avatar_img = self.player2_avatar
        else:
            if not(hasattr(self.player2,"avatar_img") and self.player2.avatar_img):
                print "ERROR NO AVATAR FOR PLAYER 2"
                self.player1.avatar_img=pygame.image.load("Avatars/Chevalier_noir#.png")
        self.player1.position_y=(840*self.height)/900
        self.player2.position_y=(70*self.height)/900
        self.player1.army.position_y=self.height-300
        self.player2.army.position_y=300
        self.player1.hand.position_x=self.width-100
        self.player2.hand.position_x=100
        self.player1.deck_pos = (self.width-100,self.height-100)
        self.player2.deck_pos = (100,100)
        self.player1.adv=self.player2
        self.player2.adv=self.player1
        
        self.player1.icon = HeroButton(self.player1)
        self.all_sprites.add(self.player1.icon)
        self.player2.icon = HeroButton(self.player2)
        self.all_sprites.add(self.player2.icon)
        
        self.firstplayer=choice([self.player1,self.player2])
        print "FIRST PLAYER IS",self.firstplayer.name
        self.player=self.firstplayer
        self.player.adv.drawCard(1)
        
        self.player1.start()
        self.player2.start()
        
        
    def defaultDeck(self) :
        trollrouge=Card("Troll rouge",4,4)
        trollrouge.addBonus(Provocation())
        vase=Card("Vase",1,2)
        vase.addBonus(Provocation())
        minivase=Card("Mini Vase",1,1)
        minivase.addBonus(Provocation())
        vase.addBonus(CriDeGuerre(Invocation(minivase)))
        feufollet=Card("Follet",1,1)
        feufollet.addBonus(Insaisissable())                                               
        archer_elfe=Card("Archer elfe",2,2)
        archer_elfe.addBonus(Charge())
        archer_elfe.addBonus(AttaqueADistance())
        gobhorde=Card("Goblin de la horde",3,1)
        gobhorde.addBonus(CriDeGuerre(DegatMasse(1)))
        templier=Card("Templier",3,3)
        templier.addBonus(FurieDesVents())
        mouton = Card("mouton",1,1)
        mouton.addBonus(Provocation())
        trou=Card("Trou",0,4)
        trou.addBonus(ChaqueTour(Invocation(mouton)))
        trou.addBonus(Insaisissable())
        trou.addBonus(CoutReduit())  
        pretresse = Card("Pretresse des Mers",2,3)
        pretresse.addBonus(CriDeGuerre(GuerrisonMasse(1)))
        pingouin = Card("Pingouin",2,3)
        murlock = Card("Abominable Murlock",4,6)
        murlock.addBonus(Provocation())
        catapulte = Card("Catapulte",4,6)
        catapulte.addBonus(NePeutPasRiposter())
        seigneur = Card("Seigneur des Cryptes",3,7)
        seigneur.addBonus(QuandIlEstBlesse(GuerisonTotale()))
        tim = Card("Tim",1,1)
        tim.addBonus(Insaisissable())
        tim.addBonus(ALaPlaceDeLAttaque(Degat(1)))
        tigre = Card("Tigre Blanc",5,5)
        tigre.addBonus(Camouflage())
        barbare = Card("Barbare Sanguinaire",3,5)
        barbare.addBonus(QuandIlTue(DegatMasse(1)))
        deck=[Card("Troll gris",4,4)]*2+[murlock,trollrouge,templier,mouton,mouton,gobhorde,archer_elfe,archer_elfe,archer_elfe,pretresse,pingouin,vase,trou]*2
        deck=[Card("Troll gris",4,4)]*2+[mouton,seigneur,seigneur,barbare,catapulte,barbare,catapulte,pingouin,vase,trou,gobhorde]*3#+[archer_elfe,mouton]*1
        return deck
    def chooseDeck(self,name=None,n_p=0) :
        #from deck_creation import utilisation_list
        import pickle
        #all_decks = pickle.load( open( "all_decks.sav", "rb" ))
        all_decks = [fname[fname.index("\\")+1:-4].replace("_"," ") for fname in glob.glob("Decks/*.dek")]
        #print "possible decks are :",all_decks
        deck = []
        
        if not(name in all_decks):
            while not deck:
                print name," is not accessible"
                name = raw_input("choose a deck in list :")
                if name in all_decks :
                    break
        
        if name!=None and name in all_decks:
            all_cards={}
            for f in glob.glob("CardFiles/all*.sav") :
                #print "load cards in ",f
                d = pickle.load( open(f, "r" ))
                all_cards.update(d)
            name="Decks\\"+name.replace(" ","_")+".dek"
            deck_names=pickle.load( open(name))
            #print deck_names
            for d,c in deck_names.items():
                if d != "AvatarImage":
                    try :
                        k=all_cards[d]
                    except Exception as inst :
                        print "error with card ",d
                        print "in",all_cards.keys()
                        print "error=",inst
                        raise "fatal error"
                    for v in range(c):
                        deck.append(k)
                    #print d
                else:
                    if n_p == 1:
                        self.player1_avatar = pygame.image.load(c)
                    elif n_p == 2:
                        self.player2_avatar = pygame.image.load(c)
        else :
            deck=None
        
        from cardPowers import Camouflage, Provocation
        for d in reversed(deck):
            if (any([b.__class__==Camouflage for b in d.bonus]) or any([b.__class__==Camouflage for b in d.bonus])) and (any([(b.__class__==Provocation) for b in d.bonus]) or any([(b.__class__==DonneArmureAuHero) for b in d.bonus])):
                for i in range(60):
                    print "Cheater !!!!!!"
                deck = []
                from Card import mouton
                for i in range(30):
                    deck.append(mouton)
                break

        return deck
    def changePlayer(self):
        #print "change player"
        if self.player == self.player1:
            self.player = self.player2
        elif self.player == self.player2:
            self.player = self.player1        
        else:
            print "error of player"
        if hasattr(self.player,"verbose") and self.player.verbose>0 : print "****  turn of player ",self.player.name
        self.endturn_button.update(self.player)
        if self.player==self.firstplayer :
            self.turn += 1
        self.player.beginOfTurn()
    
    def play(self) :
        #print "game play"
        #self.player.takeTurn(self.turn)
        while not self.end :
            self.update()
        #print "game ended"

    def update(self) :
        # print "game update"
        #space = False
        self.screen.fill(BROWN)
        self.screen.blit(self.bg,(0,0))
        drawing=pygame.sprite.OrderedUpdates()
        for p in self.player.adv.army :
            drawing.add(p)
            if hasattr(p,"child"):
                for effect in reversed(p.child): # reversed pour voir sarcophage dessus
                    drawing.add(effect)
        for p in self.player.army  :
            drawing.add(p)
            if hasattr(p,"child"):
                for effect in reversed(p.child):
                    drawing.add(effect)
        drawing.draw(self.screen)
        ##print "draw  "," ".join([i.content.nom for i in self.player1.hand.sprites()])
        self.player2.hand.draw(self.screen)
        self.player1.hand.draw(self.screen)
        self.temporary_sprites.draw(self.screen)
        #self.player1.hand.draw(self.screen)
        events = pygame.event.get()
        for event in events: 
            if event.type == pygame.QUIT:
                self.end = True
            if event.type == pygame.KEYDOWN:
            #if event.key == pygame.K_SPACE:
            #    space = True
                if event.key == pygame.K_ESCAPE:
                    print "Escape key pressed"
                    self.end=True
                    
#        keys = pygame.key.get_pressed()
#        if keys[pygame.K_h] and keys[pygame.K_m]:
#            self.player.mana+=10
#            print "MANA CHEAT ACTIVATED"
#        if keys[pygame.K_p]:
#            self.winner = self.player1.name
#        if keys[pygame.K_c]:
#            self.winner = self.player2.name
        if self.player.adv.spell_pending :
            if not isinstance(self.player.adv,Computer0) :
                pygame.draw.rect(self.screen,(60,60,100), (200,100,300,50))
                font = pygame.font.SysFont('Arial', 15)
                self.screen.blit(font.render('Target for '+self.player.adv.spell_pending[1].getInlineDescription(), True, (255,0,0)), (200, 100))
                # print "adv.spell pending"
            print "game adv spell pending"
            self.player.adv.update(events)
            #if hasattr(self.player,"verify_value") :
            #    del self.player.verify_value # on ne peut plus verifier l effet d une action si le joueur influe librement dessus
        elif len(self.all_animations)<1 :
            self.animation_runing=False
            if not isinstance(self.player,Computer0):
                if self.player.Attacker_selected:
                    a=pygame.draw.rect(self.screen,(60,60,100), (200,100,300,30))
                    font = pygame.font.SysFont('Arial', 15)
                    self.screen.blit(font.render('Target for '+self.player.Attacker_selected.name+' attack', True, (255,0,0)), (200, 100))
                if self.player.spell_pending :
                    a=pygame.draw.rect(self.screen,(60,60,100), (200,100,300,30))
                    font = pygame.font.SysFont('Arial', 15)
                    self.screen.blit(font.render('Target for '+self.player.spell_pending[1].getInlineDescription(), True, (255,0,0)), (200, 100))             
            self.player.update(events) # computer play here        
            
        for a in self.all_animations:
            a.animate()
        self.mouse.update()                                      
        self.display_zoom()          
        font = pygame.font.SysFont("Calibri",32)
        text = font.render("MANA = "+str(self.player.mana),False,(255,0,0))
        text2 = font.render("PLAYER = "+str(self.player.name),False,(255,0,0))           
        self.screen.blit(card_back_img,(self.player1.deck_pos[0]-81,self.player1.deck_pos[1]-120))
        self.screen.blit(card_back_img,(self.player2.deck_pos[0]-81,self.player2.deck_pos[1]-120))
        self.screen.blit(text,((1000*self.width)/1600,(600*self.height)/900))
        self.screen.blit(text2,((1000*self.width)/1600,(700*self.height)/900))
        
        pygame.display.set_caption("Magic Card Battle")
        self.all_sprites.draw(self.screen)
        #self.to_draw.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)

    def display_zoom(self) :
        if not(self.animation_runing) :
            pos=pygame.mouse.get_pos()
            mouselist=[s for s in self.player2.army if hasattr(s,"rect") and s.rect.collidepoint(pos)]
            if self.player2.hide_cards == False:
                 mouselist+=[s for s in self.player2.hand if hasattr(s,"rect") and s.rect.collidepoint(pos)]
            mouselist+=[s for s in self.player1.army if hasattr(s,"rect") and s.rect.collidepoint(pos)]
            if self.player1.hide_cards == False:
                 mouselist+=[s for s in self.player1.hand if hasattr(s,"rect") and s.rect.collidepoint(pos)]
            if mouselist :
                self.zoomed = ZoomOn(mouselist[-1])
                self.screen.blit(self.zoomed.image,(self.width/2-141,self.height/2-204))              
            else:
                self.zoomed = ZoomOn(None)
        else:
            self.zoomed = ZoomOn(None)
    
    def get_winner(self):
        return self.winner

class SimulationGame(Game):
    def __init__(self,original_game) :
        self.turn=original_game.turn
        self.all_animations=None
    def changePlayer(self):
        if self.player == self.player1:
            self.player = self.player2
        else :
            self.player = self.player1        
        self.player.beginOfTurn()
    def play(self,n) :
        # n number of actions seen
        while not self.end :
            self.player.update(events) # computer plays

        
if __name__=="__main__" :
    sets = {}
    sets["Aqua"]=("Poseidon","Fureur des Mers","Avatars/poseidon#.png")
    sets["Horde"]=("Seth le Cruel","Horde","Avatars/Gobelin#.png")
    sets["Undead"]=("la Legion","Necroman","Avatars/Legion#.png")
    sets["Humain"]=("Otehir le robuste","default","Avatars/Roi_des_Nains#.png")
    sets["Reve"]=("Aglac","Mauvais Reves","Avatars/Roi_des_Nains#.png")
    sets["Humain2"]=("Ruminata le faible","Chateau","Avatars/Roi_des_Nains#.png")
    sets["Mage"]=("Antonidus","Magie","Avatars/ArchmageAntonidusHearthstone#.png")
    sets["Nain"]=("Othehir le robuste","Nains de Omaghetar","Avatars/Roi_des_Nains#.png")
    sets["Foret"]=("La Foret","La Foret Sauvage","Avatars/ForetSauvage#.png")
    sets["Demon"]=("Seigneur Noir","Demon","Avatars/Demon#.png")
    sets["Bourrin"]=("Seigneur Noir","Bourrin","Avatars/Demon#.png")
    sets["Grimace"]=("La Limace","Limace","Avatars/ForetSauvage#.png")
    sets["Nocturne"]=("Seigneur Sombre","Nocturne","Avatars/SeigneurNoir#.png")
    sets["Ogres"]=("Grand Chef des Ogres","Ogres du Grand Sud","Avatars/ChefOgre#.png")
    player2_set = sets["Undead"]
    player1_set = sets["Reve"]
    game = Game()
    game.defaultPlayers(player1_set,player2_set)
    game.play()
    pygame.quit()

        
