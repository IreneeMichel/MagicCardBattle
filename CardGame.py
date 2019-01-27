import os
import glob
import pygame
import time
import random
import deck_creation
#import traceback
os.chdir(os.path.dirname(os.path.realpath(__file__)))

pygame.init()

from copy import copy
from Card import Card,readMonsters
import CardPowers
from Player import Player,Computer,Computer0,HostedPlayer
import Level
#from Creature import Creature,AnimatedCreature
from Sprites import Mouse,EndButton,HeroButton, ZoomOn,OrderedUpdates
from random import choice,sample

from math import floor

from outils import file2name
from outils import name2file
from outils import localpath

BLACK = 0,0,0
BROWN = 90,60,20

card_back_img = pygame.image.load("gameAnimationImages/CardDosArgentum.png")
card_back_img = pygame.transform.scale(card_back_img,(163,240))

pygame.mixer.init()


class Game():
    def __init__(self):
        pygame.init()
        #self.to_draw = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        try :
            from win32api import GetSystemMetrics
            dim=(GetSystemMetrics(0),GetSystemMetrics(1))
        except :
             try :
                  import tkinter
                  root = tkinter.Tk()
                  dim=(root.winfo_screenwidth(),root.winfo_screenheight())
                  root.destroy()
             except :
                  print( "\n********\n\nbad display !\n\n**********\n")
                  dim=(160,100)
        self.height = int(dim[1]*1.)
        self.width = int(dim[0]*1.)
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.bg = pygame.transform.scale(pygame.image.load("gameAnimationImages/background"+str(choice([1,2,3]))+".png"),(self.width,self.height))
        #background = pygame.image.load("gameAnimationImages/background.png")
        
        
        self.all_sprites = OrderedUpdates()
        self.temporary_sprites=OrderedUpdates()
        self.mouse = Mouse()
        self.endturn_button = EndButton((self.width,self.height))
        self.all_sprites.add(self.endturn_button)
        self.all_sprites.add(self.mouse)
        
        self.zoomed=None
        #self.animation_runing = False
        self.effect_list=[]
        self.animations = []
        
        self.screen.fill(BROWN)
        pygame.display.flip()
        #player = player1
        self.turn = 1
        self.creatures_limit = 9
        self.winner = None
        self.end = False   # a changer peut etre par appel de game.end()
        self.player1_avatar = self.player2_avatar = None
        self.mouse_icon = pygame.sprite.GroupSingle()
        self.mouse_icon.add(self.mouse)
        self.soc=None
        self.id=-1
        self.objects={}
        self.dead_monsters=[]

    def random(self,n,intrange) :
        return sample(list(range(intrange)),n)
    
    def defaultPlayers(self,set1,set2):
        #self.player1=Player(set1[0],self.chooseDeck(set1[1],1),self)
        self.player1=Computer(set1[0],self.chooseDeck(set1[1]),self,2,verbose=1,hide=False)
        self.player2=Computer(set2[0],self.chooseDeck(set2[1]),self,2,verbose=1,hide=False)
        if set1[2]!=None:
            self.player1.avatar_img=pygame.image.load(set1[2])            
        if set2[2]!=None:
            self.player2.avatar_img=pygame.image.load(set2[2])
        
        self.initialize()
    
    def initialize(self,common_start = True):
        if self.player1_avatar and not(hasattr(self.player1,"avatar_img") and self.player1.avatar_img):
            self.player1.avatar_img = self.player1_avatar
        else:
            if not(hasattr(self.player1,"avatar_img") and self.player1.avatar_img):                
                print( "ERROR NO AVATAR FOR PLAYER 1")
                self.player1.avatar_img=pygame.image.load("Avatars/Chevalier_noir#.png")
        if self.player2_avatar and not(hasattr(self.player2,"avatar_img") and self.player2.avatar_img):
            self.player2.avatar_img = self.player2_avatar
        else:
            if not(hasattr(self.player2,"avatar_img") and self.player2.avatar_img):
                print( "ERROR NO AVATAR FOR PLAYER 2")
                self.player2.avatar_img=pygame.image.load("Avatars/Chevalier_noir#.png")
        self.player1.position_y=self.height-90
        self.player2.position_y=80
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
        if not hasattr(self,"firstplayer") :
            self.firstplayer=choice([1,2])
        if self.firstplayer==1 :
            self.firstplayer=self.player1
        elif self.firstplayer==2 :
            self.firstplayer=self.player2
        self.player=self.firstplayer   
        self.setId(self.player)
        self.setId(self.player.adv)
        
        if common_start:
            self.player1.start()
            self.player2.start()            
            self.player.adv.drawCard(1) 
        else:
            
            self.player1.initialise()
            self.player2.initialise()  
        
        try:
            pygame.mixer.music.fadeout(1000)
        except:
            pass

    def defaultDeck(self) :
        raise "removed"
#        trollrouge=Card("Troll rouge",4,4)
#        trollrouge.addBonus(Provocation())
#        vase=Card("Vase",1,2)
#        vase.addBonus(Provocation())
#        minivase=Card("Mini Vase",1,1)
#        minivase.addBonus(Provocation())
#        vase.addBonus(CriDeGuerre(Invocation(minivase)))
#        feufollet=Card("Follet",1,1)
#        feufollet.addBonus(Insaisissable())                                               
#        archer_elfe=Card("Archer elfe",2,2)
#        archer_elfe.addBonus(Charge())
#        archer_elfe.addBonus(AttaqueADistance())
#        gobhorde=Card("Goblin de la horde",3,1)
#        gobhorde.addBonus(CriDeGuerre(DegatMasse(1)))
#        templier=Card("Templier",3,3)
#        templier.addBonus(FurieDesVents())
#        mouton = Card("mouton",1,1)
#        mouton.addBonus(Provocation())
#        trou=Card("Trou",0,4)
#        trou.addBonus(ChaqueTour(Invocation(mouton)))
#        trou.addBonus(Insaisissable())
#        trou.addBonus(CoutReduit())  
#        pretresse = Card("Pretresse des Mers",2,3)
#        pretresse.addBonus(CriDeGuerre(GuerrisonMasse(1)))
#        pingouin = Card("Pingouin",2,3)
#        murlock = Card("Abominable Murlock",4,6)
#        murlock.addBonus(Provocation())
#        catapulte = Card("Catapulte",4,6)
#        catapulte.addBonus(NePeutPasRiposter())
#        seigneur = Card("Seigneur des Cryptes",3,7)
#        seigneur.addBonus(QuandIlEstBlesse(GuerisonTotale()))
#        tim = Card("Tim",1,1)
#        tim.addBonus(Insaisissable())
#        tim.addBonus(ALaPlaceDeLAttaque(Degat(1)))
#        tigre = Card("Tigre Blanc",5,5)
#        tigre.addBonus(Camouflage())
#        barbare = Card("Barbare Sanguinaire",3,5)
#        barbare.addBonus(QuandIlTue(DegatMasse(1)))
#        deck=[Card("Troll gris",4,4)]*2+[murlock,trollrouge,templier,mouton,mouton,gobhorde,archer_elfe,archer_elfe,archer_elfe,pretresse,pingouin,vase,trou]*2
#        deck=[Card("Troll gris",4,4)]*2+[mouton,seigneur,seigneur,barbare,catapulte,barbare,catapulte,pingouin,vase,trou,gobhorde]*3#+[archer_elfe,mouton]*1
        return deck

    def chooseDeck(self,name=None,n_p=0) :
        #from deck_creation import utilisation_list

        all_decks = [file2name(fname,'.dek') for fname in glob.glob("Decks/*.dek")]
        #print "possible decks are :",all_decks
        deck = []
        if not(name in all_decks):
            print ("all decks", all_decks)
            while not deck:
                print (name," is not accessible")
                name = raw_input("choose a deck in list :")
                if name in all_decks :
                    break
        
        if name!=None and name in all_decks:
            all_cards={}
            for f in glob.glob("CardFiles/all*.sav") :
                #print "load cards in ",f
                d = readMonsters(f)
                all_cards.update(d)
            name=name2file("Decks",name,".dek")
            deck_names=eval(open(name).read())
            #print deck_names
            for d,c in deck_names.items():
                if d != "AvatarImage":
                    try :
                        k=all_cards[d]
                    except Exception as inst :
                        print( "error with card ",d)
                        print( "in",all_cards.keys())
                        print( "error=",inst)
                        raise "fatal error"
                    for v in range(c):
                        deck.append(k)
                    #print d
                else:
                    if n_p == 1:
                        self.player1_avatar = pygame.image.load(localpath(c))
                    elif n_p == 2:
                        self.player2_avatar = pygame.image.load(localpath(c))
        else :
            deck=None

        from CardPowers import Camouflage, Provocation,DonneArmureAuHero
        for d in reversed(deck):
            if (any([b.__class__==Camouflage for b in d.bonus]) or any([b.__class__==Camouflage for b in d.bonus])) and (any([(b.__class__==Provocation) for b in d.bonus]) or any([(b.__class__==DonneArmureAuHero) for b in d.bonus])):
                for i in range(60):
                    print( "Cheater !!!!!!")
                deck = []
                from Card import mouton
                for i in range(30):
                    deck.append(mouton)
                break

        return deck
     
    def randomDeck(self):
         all_cards={}
         for f in glob.glob("CardFiles/all*.sav") :
                #print "load cards in ",f
                d = readMonsters(f)
                all_cards.update(d)
         deck = []
         for i in range(30):
              card = random.choice(all_cards.values())
              print("cardname",card.name)
              deck.append(card)
         return deck
        
    def activateOption(self,keyword):
        from Creature import AnimatedCreature
        if keyword[:12] ==  "SetHeroLives":
            hp = int(keyword[12:])
            self.player1.max_pv = self.player1.pv= hp            
            self.player2.max_pv = self.player2.pv= hp
            self.player1.icon.update()
            self.player2.icon.update()
        
        if keyword[:14] == "SetInitialMana":
            self.turn = int(keyword[14:])
            self.player.mana = int(keyword[14:])
        
        if keyword[:21] == "LimiteNombreCreatures":
            self.creatures_limit = int(keyword[21:])

        if keyword == "FrozenBoats":
            undead_monsters = readMonsters("CardFiles/undead_monsters.sav")
            card = undead_monsters["Navire Gele"]
            
            print( "summoned frozen boats")
            
            for player in self.player1,self.player2:          
                for i in range(2):
                    AnimatedCreature([self.width/2,self.height/2],card,player,triggerPlayingEffect=True)
                player.orderArmy()
        
        if keyword == "Algues":
            nature_monsters = readMonsters("CardFiles/nature_monsters.sav")
            card = nature_monsters["Algue Envahissante"]
            
            AnimatedCreature([self.width/2,self.height/2],card,self.player2,triggerPlayingEffect=False)

        if keyword == "Moneyeur Fou":
            nature_monsters = readMonsters("CardFiles/unknown_monsters.sav")
            card = nature_monsters["Moneyeur Fou"]
            
            AnimatedCreature([self.width/2,self.height/2],card,self.player2,triggerPlayingEffect=False)
        
        if keyword == "Lakshmi":
            nature_monsters = readMonsters("CardFiles/indian_monsters.sav")
            card = nature_monsters["Lakshmi"]
            
            AnimatedCreature([self.width/2,self.height/2],card,self.player1,triggerPlayingEffect=False)
        
        if keyword == "Baton de La Lune Rugissante":
            felys_monsters = readMonsters("CardFiles/felys_monsters.sav")
            card = felys_monsters["Baton de La Lune Rugissante"]
            
            AnimatedCreature([self.width/2,self.height/2],card,self.player1,triggerPlayingEffect=False)
        
        if keyword == "AgonieResonante":
            def death(self,creature):
                if not creature.is_invocation : creature.player.launch(creature,self.spell)
                if not creature.is_invocation : creature.player.launch(creature,self.spell)
            from CardPowers import RaleDAgonie
            RaleDAgonie.death=death
        else :
            from imp import reload
            reload(CardPowers)
            from CardPowers import RaleDAgonie
            

        if keyword == "Profusion":
            for player in self.player1, self.player2:
                
                for card in player.deck+[c.content for c in player.hand]:
                    if card.pv>0:
                         card.bonus.append(CardPowers.CriDeGuerre(CardPowers.PiocheCartes(Level.NbFixe(1))))
        
        
        if keyword == "FroidIntenable":
            from CardPowers import Souffrant,InsensibleALaMagie,Isole
            for player in self.player1, self.player2:                
                for card in player.deck+[c.content for c in player.hand]:                    
                    if card.pv>0 and not(any([b.__class__ in (Souffrant,InsensibleALaMagie,Isole) for b in card.bonus])):
                        card.bonus.append(CardPowers.Souffrant())
                            #print card.name, " rale d'agonie mofifie par l'option"
        if keyword == "Recifs":
            aqua_monsters = readMonsters("CardFiles/aqua_monsters.sav")
            card = aqua_monsters["Recifs"]
            
            for player in self.player1,self.player2:
                AnimatedCreature([self.width/2,self.height/2],card,player,triggerPlayingEffect=False)
            
            card = aqua_monsters["Mer De Corail"]
            
            AnimatedCreature([self.width/2,self.height/2],card,self.player1,triggerPlayingEffect=False)
            player.orderArmy()

    def changePlayer(self):
        a=[m.name for m in self.player1.army if m.pv<1]+[m.name for m in self.player2.army if m.pv<1]
        if len(a)>0 :
            print( "zombi :",a)
            raise 0
        if self.player.adv.pv<=0 :
            self.player.adv.icon.update()
            return
        #print "change player"
        if self.player == self.player1:
            self.player = self.player2
        elif self.player == self.player2:
            self.player = self.player1        
        else:
            print( "error of player")
        if hasattr(self.player,"verbose") and self.player.verbose>0 : print( "****  turn of player ",self.player.name)
        self.endturn_button.update(self.player)
        self.all_sprites.draw(self.screen) # pour mettre a jour endturn_button a l ecran
        if self.player==self.firstplayer :
            self.turn += 1
        if isinstance(self.player,Computer0) :
            self.saveGame()
        self.player.beginOfTurn()

    def waitEndOfEffects(self):
        while self.effect_list :
            self.treatEffectList()
        mlist=[ m for m in self.player1.army if m.pv<1 or m.max_pv==0 ]+[m for m in self.player2.army if m.pv<1 or m.max_pv==0 ]
        for m in reversed(mlist) :
            m.die()
        
    def play(self) :
        #print "game play"
        #self.player.takeTurn(self.turn)
        pygame.mouse.set_visible(False)
        while (not self.end) or (self.animation_runing) :
            self.update()
        #print "game ended"
        pygame.mouse.set_visible(True)

    def update(self) :
        #print "game update"
        #space = False
        import CardPowers # utile pour les effets dans effect_list
        self.screen.fill(BROWN)
        self.screen.blit(self.bg,(0,0))
        drawing=OrderedUpdates()
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
        for player in self.player1, self.player2:
            for c in player.hand:
                c.updateImage()
            player.hand.draw(self.screen)
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
                    print( "Escape key pressed")
                    self.end=True
                    
#        keys = pygame.key.get_pressed()
#        if keys[pygame.K_h] and keys[pygame.K_m]:
#            self.player.mana+=10
#            print "MANA CHEAT ACTIVATED"
#        if keys[pygame.K_p]:
#            self.winner = self.player1.name
#        if keys[pygame.K_c]:
#            self.winner = self.player2.name
            #if hasattr(self.player,"verify_value") :
            #    del self.player.verify_value # on ne peut plus verifier l effet d une action si le joueur influe librement dessus
        self.treatEffectList()
        if len(self.animations)<1  :
            self.animation_runing=False
            # spell pending n'est que pour les joueurs humains
            if self.player.adv.spell_pending :
                if not isinstance(self.player.adv,Computer0) :
                    pygame.draw.rect(self.screen,(60,60,100), (200,100,300,50))
                    font = pygame.font.SysFont('Arial', 15)
                    self.screen.blit(font.render('Target for '+self.player.adv.spell_pending[1].getInlineDescription(), True, (255,0,0)), (200, 100))
                # print "adv.spell pending"
            #print "game adv spell pending"
                self.player.adv.update(events) # choisit cible  
            else :
                if not isinstance(self.player,Computer0):
                    if self.player.spell_pending :
                        a=pygame.draw.rect(self.screen,(60,60,100), (200,100,300,30))
                        font = pygame.font.SysFont('Arial', 15)
                        self.screen.blit(font.render('Target for '+self.player.spell_pending[1].getInlineDescription(), True, (255,0,0)), (200, 100))
                    elif self.player.Attacker_selected:
                        a=pygame.draw.rect(self.screen,(60,60,100), (200,100,300,30))
                        font = pygame.font.SysFont('Arial', 15)
                        self.screen.blit(font.render('Target for '+self.player.Attacker_selected.name+' attack', True, (255,0,0)), (200, 100))
                self.player.update(events)    # joue ou choisit cible      
#                    print "effets",self.game.effect_list
#                    self.game.waitEndOfEffects()
#                    print "fin des effets",self.game.effect_list
                
                     # computer play here
        #print "effect_list",self.effect_list
        for a in reversed(self.animations):
            a.animate()
        if self.animations :
            self.animation_runing=True
        else :
            self.animation_runing=False
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
        
    def treatEffectList(self) :
        import Target,Spell   # peut etre utilise dans les eval
        for a in self.effect_list :
            if self.player.adv.spell_pending or self.player.spell_pending :
                #print("spell pending dans treat effect")
                break
            a[0]=a[0]-1
            #print "effect_list compte a rebour",a[0]
            if a[0]==0 :
                #print self.player1.name," effect_list declanche ",a
                a[0]==-1  # l effet est pris en compte, la simulation va le considere deja effectue
                method_name=a[2]
                args=a[3]
                if args!=None :
                    for i in range(len(args)) :
                        if type(args[i])==type(1) :
                            if args[i] in self.objects :
                                args[i]=self.objects[args[i]]
                            else :
                                print( "error with args of effect ",a)
                                print( "object ",args[i]," not in object list ")
                                print( "in game ",self.player1.name)
                                print( "\nwith objects ",self.objects)
                                print( [(a.name,a.id) for a in self.objects.values()])
                                raise "erreur dans effect_list"
                if a[1]!=None :
                    if type(a[1])==type(1) :
                        if a[1] in self.objects :
                            actinginst=self.objects[a[1]]
                        else :
                            print( "error with effect ",a)
                            print( "object ",a[1]," not in object list ")
                            print ("\nwith objects ",self.objects )
                            print ([(a.name,a.id) for a in self.objects.values()])
                            raise "erreur dans effect_list"
                    else :
                       actinginst=a[1]   # spells are not in objects list, not copied and acting directly, they have no owner
                    if method_name=="effect" and args[1].pv <1  and args[1].name!="choix1" and args[1].name!="choix2" :
                        if (not isinstance(self,SimulationGame)) or self.player.nv>-1 :
                            print( "                no effect on dead ",args[1].name)
                        continue
                    try :                              
                        if args :
                            exec("actinginst."+method_name+"(*args)")
                        else :
                            exec("actinginst."+method_name+"()")
                    except Exception as e :
                        print( e)
                        print( "error with effect ",a)
                        print( ' with origin and args names ',[m.name  for m in ([actinginst]+args) if hasattr(m,"name") ])
                        print( self.player1.name,"error on a execution of",actinginst,".",method_name+"(*",args,")")
                        raise e                   
                else :
                    try :
                        if args :
                            exec(method_name+"(*args)")
                        else :
                            exec(method_name+"()")
                    except Exception as e :
                        print( e)
                        print( self.player1.name,"error on a execute (no object a[1])  ",method_name+"(",a[3],")")
                        print( "\nwith objects ",self.objects )
                        raise e
        for i in range(len(self.effect_list)-1,-1,-1) : # ensuite on les supprime
            if self.effect_list[i][0]<1 :
                #print "dans effect_list on enelve",self.effect_list[i]
                del self.effect_list[i]
        if not self.effect_list :
            mlist=[ m for m in self.player1.army]+[m for m in self.player2.army]
            for m in reversed(mlist) :
                if m.pv<=0 and m.name!="choix1" and m.name !="choix2" :
                    print( "un mort vivant !",m.name,m.id)
                    m.die()
            #if self.dead_monsters : print "# raz de dead_monsters for ",self.player1.name," rests ",[m.id for m in self.player1.army]+[m.id for m in self.player2.army]
            self.dead_monsters=[]
            if (not self.player.spell_pending) and (not self.player.adv.spell_pending) :
                if len([m.id for m in self.player.army if m.pv>0 ])>self.creatures_limit :
                    print( " monstre en trop ",[m.name for m in self.player.army if m.pv>0 ]," >",self.creatures_limit)
                    if len([m.id for m in self.player.army if m.pv>0 ])>self.creatures_limit+1 :
                        for isac in range(1,len([m.id for m in self.player.army if m.pv>0 ])-self.creatures_limit) :
                            self.effect_list.append([isac,self.player.id,"sacrify",None])
                    self.player.sacrify()               
                if len([m.id for m in self.player.adv.army if m.pv>0 ])>self.creatures_limit :
                    self.player.adv.sacrify()               

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
                if self.zoomed != mouselist[-1]:
                    sound = pygame.mixer.Sound("Sounds/2731.wav")
                    sound.set_volume(0.3)
                    sound.play(0)
                self.zoomed = ZoomOn(mouselist[-1])
                self.screen.blit(self.zoomed.image,(self.width/2-141,self.height/2-204))              
            else:
                self.zoomed = ZoomOn(None)
        else:
            self.zoomed = ZoomOn(None)
    
    def get_winner(self):
        return self.winner
        
    def setId(self,object) :
        self.id+=1
        self.objects[self.id]=object
#        if hasattr(object,"name") :
#            print "%%",self.player1.name," object ",object.__class__.__name__,object.name," devient ",self.id
        object.id=self.id
        
    def saveGame(self):
        if isinstance(self.player1,Computer) and isinstance(self.player2,Computer) and self.turn<4 :
            save_slot = "GameSaves/save-turn"+str(self.turn)+".sav"
        else :
            save_slot = "GameSaves/save-default.sav"
        
        save_dic = {}
        
        save_dic["Turn"] = self.turn
        save_dic["ActualPlayer"] = [self.player1,self.player2].index(self.player)
        save_dic["FirstPlayer"] = [self.player1,self.player2].index(self.firstplayer)
        save_dic["Player1Hand"] = [card.constructor() for card in self.player1.hand]
        save_dic["Player2Hand"] = [card.constructor() for card in self.player2.hand]
        save_dic["Player1Army"] = [crea.constructor() for crea in self.player1.army]
        save_dic["Player2Army"] = [crea.constructor() for crea in self.player2.army]
        save_dic["Player1Deck"] = [card.name for card in self.player1.deck]
        save_dic["Player2Deck"] = [card.name for card in self.player2.deck]
        save_dic["Player1Hides"] = self.player1.hide_cards
        save_dic["Player2Hides"] = self.player2.hide_cards
        save_dic["Player1Pv"] = self.player1.pv
        save_dic["Player2Pv"] = self.player2.pv
        save_dic["creatures_limit"] = self.creatures_limit
        
        with open(save_slot,"w") as fil:
            fil.write(str(save_dic))
    
    def loadGame(self):
        
        from Sprites import CardInHand
        import CardPowers,Target
        from Creature import AnimatedCreature
        import Spell
        
        load_slot = "GameSaves/save-default.sav"
        #load_slot = "GameSaves/save-turn1.sav"
        
        with open(load_slot,"r") as fil:
            load_dic = eval(fil.read())
        
        self.turn = load_dic["Turn"]
        self.firstplayer = [self.player1,self.player2][load_dic["FirstPlayer"]]
        self.player = [self.player1,self.player2][load_dic["ActualPlayer"]]
        self.creatures_limit=load_dic["creatures_limit"]
        
        all_cards={}
        for f in glob.glob("CardFiles/all*.sav") :
                #print "load cards in ",f
            d = readMonsters(f)
            all_cards.update(d)
        
        self.player1.deck = [all_cards[c] for c in load_dic["Player1Deck"]]
        self.player2.deck = [all_cards[c] for c in load_dic["Player2Deck"]]
        
        self.player1.pv = load_dic["Player1Pv"]
        self.player2.pv = load_dic["Player2Pv"]
        
        a = 1
        for player,handadress,armykey,hide in (self.player1,"Player1Hand","Player1Army","Player1Hide"),( self.player2,"Player2Hand","Player2Army","Player2Hide"):            
            for c in player.deck :
                c.costint=int(floor(c.getCost()))
                c.starcost=c.getStars()
            hand =load_dic[handadress]
            for c in hand:
                card = eval(c)
                player.hand.add(card)
            army =load_dic[armykey]
            class Origin():
                do_not_animate = True
            #simultaneous = len(army) #used by eval
            for c in army:
                #simultaneous -= 1
                origin = [self.width/2,self.height*(a-1)] # used by eval(c) command below
                #origin #just to avoid spyder complain
                crea = eval(c)
                player.army.add(crea)
            player.mana = self.turn
            player.center = player.icon.center
            player.nb_invocation_done_this_turn = 0
            player.icon.update()
            
            #a=2
            
        
        print ("load",load_dic)
        #self.player1.orderArmy()
        #self.player2.orderArmy()
        for c in self.player1.hand:
            c.takePlace()
        for c in self.player2.hand:
            c.takePlace()
        
        self.endturn_button.update(self.player)
        self.player.beginOfTurn()
        
        

class SimulationGame(Game):
    def __init__(self,original_game,playingcomputer,tested_action) :
        from Player import SimulationComputer
        from Creature import CreatureCopy
        self.turn=original_game.turn
        self.all_animations=None
        self.animations=None
        self.creatures_limit = original_game.creatures_limit
        self.effect_list=[[el[0],el[1],el[2],copy(el[3])] for el in original_game.effect_list if el[0]>0]
        self.id=original_game.id
        comp1=SimulationComputer(playingcomputer.name+"-simu1",[],self,playingcomputer.nv-1,tested_action,verbose=playingcomputer.verbose-1)
        #print "simu game init with ",comp1.name," and effect_list=",self.effect_list
        comp2=SimulationComputer(playingcomputer.adv.name+"-simu2",[],self,playingcomputer.nv-1,verbose=playingcomputer.verbose-1)
        comp1.pv,comp2.pv=playingcomputer.pv,playingcomputer.adv.pv
        comp1.id,comp2.id=playingcomputer.id,playingcomputer.adv.id
        comp1.army=[CreatureCopy(m,comp1) for m in playingcomputer.army]
        comp2.army=[CreatureCopy(m,comp2) for m in playingcomputer.adv.army]
        comp1.hand=[]
        comp2.hand=[SimulationComputer.NotPlayableCard()]*len(playingcomputer.adv.hand)
        for c in playingcomputer.hand :
            if c.__class__.__name__=="CardInHand" :
                comp1.hand.append(c.content) # a normal player has cardInHand in hand
            else :
                comp1.hand.append(c)  # a simulation computer has card in hand
        comp1.adv=comp2 ; comp2.adv=comp1
        comp1.deck=[SimulationComputer.NotPlayableCard()]*30
        comp2.deck=[SimulationComputer.NotPlayableCard()]*30
        comp1.mana=playingcomputer.mana
        comp1.nb_invocation_done_this_turn=playingcomputer.nb_invocation_done_this_turn
        comp2.nb_invocation_done_this_turn=0
        if playingcomputer is original_game.player1 :
            self.player=self.player1=comp1
            self.player2=comp2
        else :
            self.player=self.player2=comp1
            self.player1=comp2
            #simugame.firstplayer=self.game.firstplayer
        self.objects={}
        self.dead_monsters=[CreatureCopy(m,[comp1,comp2][comp2.id==m.player.id]) for m in original_game.dead_monsters ]
        #print (playingcomputer.nv-1)*"    "+"for game copy ",len(self.dead_monsters)," dead monsters"
        for o in [comp1,comp2]+comp1.army+comp2.army+self.dead_monsters:
            self.objects[o.id]=o
        #print "#creation of simulation game for",comp1.name," with obects ",self.objects.keys()
    def changePlayer(self):
        if self.player == self.player1:
            self.player = self.player2
        else :
            self.player = self.player1
        if self.player.pv>0 :
            self.player.beginOfTurn()
    def play(self,n) :
        # n number of actions seen
        while not self.end :
            self.player.update(events) # computer plays

class NetGame(Game) :
    def __init__(self) :
        Game.__init__(self)
        import socket
        import tkinter
        self.local = self.host=socket.gethostbyname(socket.gethostname()) # Get local machine ip
        from tkinter import Tk,PanedWindow,StringVar,Entry,Button,VERTICAL,HORIZONTAL,Label
        fenetre=Tk()
        fenetre.title('Socket parameters') 
        self.netgame_win = PanedWindow(fenetre, orient=VERTICAL)
        host_zone=PanedWindow(self.netgame_win, orient=HORIZONTAL)
        host=StringVar()
        host.set(self.local)
        def modifHost(*args) :
            self.host=host.get()
            if self.local==self.host :
                start_button.config(text="Create")
            else :
                start_button.config(text="Join")
        host.trace("w", modifHost)
        host_wid=Entry(host_zone, width=30,textvariable=host)
        host_wid.pack()
        host_label=Label(fenetre, text="Host (you are "+self.local+") :")
        host_zone.add(host_label)
        host_zone.add(host_wid)
        self.netgame_win.add(host_zone)
        port_zone=PanedWindow(self.netgame_win, orient=HORIZONTAL)
        port=StringVar()
        self.port=52333
        port.set(str(self.port))
        # adress_wid=Label(None, textvariable=self.cost, background='red',width=5, anchor=W)
        def modifPort(*args) :
            #print "modify port to",port.get()
            try :
                self.port=int(port.get())
            except :
                port.set("")
        port.trace("w", modifPort)
        port_wid=Entry(fenetre, width=30,textvariable=port)
        #port_wid.grid(column=0, row=1)
        host_wid.focus() 
        port_wid.pack()
        port_label=Label(fenetre, text="Port :")
        port_zone.add(port_label)
        port_zone.add(port_wid)
        self.netgame_win.add(port_zone)
        #Create the open button
        def start() :
            fenetre.destroy()
        start_button=Button(self.netgame_win,text="Create",command=start)
        self.netgame_win.add(start_button)
        self.netgame_win.pack()
        #fenetre.focus_set()
        #start_button.focus()        
        fenetre.mainloop()
             # Import socket module
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # Reserve a port for your service.
        if self.local==self.host :
            self.soc.bind((self.host, self.port))        # Bind to the port
            print( "socket listening")
            self.soc.listen(5)                 # Now wait for client connection.

            self.soc, addr = self.soc.accept()     # Establish connection with client.
            print( 'Got connection from', addr)
            #self.soc.send('Thank you for connecting')
            #c.close()                # Close the connection
            self.firstplayer=choice([1,2])
            print( "FIRST PLAYER IS",self.firstplayer)
            self.soc.send(str(3-self.firstplayer).encode('utf-8'))
        else :
            self.soc.connect((self.host, self.port))
            print( "connect ok")
            p=self.soc.recv(1024).decode('utf-8')
            try :
                self.firstplayer=int(p)
            except :
                print( "error concerning first player, got ",p)
            #self.soc.close()                     # Close the socket when done
    def initialize(self) :
        if self.firstplayer==1 : # player1 doit etre le local
            print( "first player is local")
            self.player1.sendDeck()
            self.player2.receiveDeck()
        else :
            print( "first player is hosted")
            self.player2.receiveDeck()
            self.player1.sendDeck()         
        Game.initialize(self)
        if self.player==self.player2 :
            self.endturn_button.update(self.player)
    def send(self,str):
        print("send :"+str)
        self.soc.send(str.encode('utf-8'))
    def random(self,n,intrange) :
        if self.local==self.host :
            jet=sample(list(range(intrange)),n)
            print( "send",jet)
            self.soc.send(" ".join(map(str,jet)).encode('utf-8'))
        else :
            print( "waiting ",n," random number in range",intrange)
            p=self.soc.recv(1024).decode('utf-8')
            print( "recv ",p)
            jet=map(int,p.strip().split())
            print( "got",jet)
        return jet
    
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
    player2_set = sets["Nain"]
    player1_set = sets["Nain"]
    #game = NetGame()
    
    game = Game()
    
    #game.player1=Computer("Ennemi 1",game.chooseDeck("Voyageurs d'Outreplans"),game,2,hide=False,verbose=5)#,2,hide=False)
    game.player1=Player(player2_set[0],game.chooseDeck(player2_set[1]),game)
    game.player2=Computer("Ennemi 2",game.chooseDeck("Reveil De La Roche"),game,2,hide=False,verbose=5)
    #game.player2=HostedPlayer(game)
    
    game.initialize(common_start=False)
    game.loadGame()
    game.play()
    """    
    simu = SimulationGame(game)
    from Player import SimulationComputer
    simuplayer = SimulationComputer("mr-simu",[],simu,2)
    simu.player1 = simuplayer
    simu.player2 = SimulationComputer("mr-simu2",[],simu,2)

    all_cards={}
    for f in glob.glob("CardFiles/all*.sav") :
        #print "load cards in ",f
        d = readMonsters(f)
        all_cards.update(d)
    
    evaluated =  []
    simuplayer.hand = []
    simu.id = 1
    simu.objects = {}
    simuplayer.adv = simu.player2
    simu.player2.army = []
    for c in all_cards.values():
        if c.pv>0:
            simuplayer.army = []
            print c.constructor()
            cr = Creature(c,simuplayer,triggerPlayingEffect = False)
            evaluated.append((cr.getValue(),c.constructor()))
            print cr.getValue()
    evaluated.sort()
    """
    pygame.quit()

        
