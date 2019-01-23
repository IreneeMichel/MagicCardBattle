# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 18:15:59 2015

@author: Cyprien et Frederic MICHEL--DELETIE
"""
import os
#os.chdir(os.path.dirname(os.p ath.realpath(__file__)))

import pygame
from copy import copy
import glob
import math

import CoutCartesMonstres
import Player

import CardGame
from copy import copy

from types import MethodType

from outils import name2file,file2name

ORANGE = (200,100,0)
BLUE = (0,30,150)
GREEN = (0,200,20)
BLACK = (0,0,0)
RED =(255,0,0)

#import tkMessageBox

img_campaign_button = pygame.image.load("gameAnimationImages/PlayCampaignButton.png")
img_cardedit_button = pygame.image.load("gameAnimationImages/CardEditorButton.png")
img_deckcreation_button = pygame.image.load("gameAnimationImages/ChangeDeckButton.png")
img_playmission_button = pygame.image.load("gameAnimationImages/PlayMissionButton.png")
img_battle_button = pygame.image.load("gameAnimationImages/PlayBattleButton.png")
img_blank_button = pygame.image.load("gameAnimationImages/BlankButton.png")

if len(glob.glob("Cards/*.png"))<10 :
    print (" Cards not found ")
    exec(open('./TouchMonsterFiles.py').read())

all_cards = {}
from Card import readMonsters
for fn in glob.glob("CardFiles/all*.sav") :
    #print "load cards in ",f
    d = readMonsters(fn)
    all_cards.update(d)

#try:
#        pygame.mixer.init()
#        SOUND = True
#except:
#        SOUND = False
    
#if SOUND:    
#    pygame.mixer.music.load("Fantasy Celtic Music - Spirit of the Wild.mp3")
#    pygame.mixer.music.play(-1)

def is_around(i,ii,length):
    if ii < i -length or ii > i +length:
        return False
    else:
        return True

class Level():
    def __init__(self):
        self.options = ()
    def show(self):
        print ("Opponent: ",self.opponent.name)
        print ("scenario ",self.scenario)
        print ("Difficulty: ", self.difficulty)

    def makeImage(self,add=None):
        image = pygame.Surface((900,600))
        image.fill((255,255,255))
        img_avatar = pygame.transform.scale(pygame.image.load("Avatars/"+self.avatar),(150,150))
        w,h = img_avatar.get_size()
        image.blit(img_avatar,(650-w/2,100-h/2))
        font = pygame.font.SysFont("latobolditalic",24)
        text = font.render("Difficulty: "+self.difficulty,False,(3,0,0))
        text2 = font.render("Opponent: "+self.opponent.name,False,(3,0,0))
        image.blit(text,(100,80))
        image.blit(text2,(100,120))
        font = pygame.font.SysFont("latobolditalic",20)
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
        self.graphism = copy(self.image)
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

class Aura(pygame.sprite.Sprite):
    def __init__(self,position,size):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('gameAnimationImages/selection_button.png')
        self.image.convert_alpha()
        self.image = pygame.transform.scale(self.image,size)
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
    
class InteractiveButton(Button):
    aura = None

    def update(self):
        if is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2):
            if self.game.click == True:
                self.functiun(*self.argus)
            else:
                if not(self.aura):
                    
                    image = pygame.image.load('gameAnimationImages/selection_button.png')
                    image.convert_alpha()
                    image = pygame.transform.scale(image,self.size)
                    self.image = copy(self.graphism)
                    self.image.blit(image,[0,0])
                    self.aura = True
                    print ("activate aura")
                    
                    
        else:
            if self.aura:
                self.image = copy(self.graphism)
                self.aura = False




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
            print (deck_name)
            for k in deck.keys() :
                try :
                    all_cards[k].getCost()
                except Exception as e:
                    print ("error getCost with",k," in deck ",deck_name)
                    print(sorted(all_cards.keys()))
                    raise e
            try :
                stars = sum([all_cards[k[0]].getStars()*k[1] for k in deck.items()] )
            except :
                print (" in ",all_cards.keys(), " looking for ",deck.keys())
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
    def __init__(self,image,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game():
    def __init__(self):

        self.previous = self.modeSelection

        self.all_sprites_list = pygame.sprite.Group()
        self.blocked_decks= ["Nains de Omaghetar","Mauvais Reves","Necroman","Mahishasura","Guilde des Braves d'Edemas",
                             "Horde","Demon","Vikings","Chateau","Le Lac","Pirates des Mers Maudites","invocationscampagne",
                             "Reveil De La Roche","Chasseurs des Plaines Neigeuses","MagiePure","Voyageurs d'Outreplans"]
#        self.blocked_creature=[]
#        for i in self.blocked_decks :
#            df=os.path.join("Decks",i.replace(" ","_")+".dek")
#            try :
#                with open(df,"r") as fil: # problem with python : I wanted to use "rb"
#                    deck = eval(fil.read())
#                    self.blocked_creature=self.blocked_creature+deck.keys()
#            except :
#                print "ERROR ",df," not found"
         
        # print glob.glob("*")

        #self.steps = [None,self.modeSelection,self.matchSelection]
        #self.initSecondCampaign()

    def initFirstCampaign(self):
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
        "Vous etes donc contraint a vous battre. Mais a votre arrivee le mage se lance dans des incantations interdites et invoque une armee de demon diriges par un puissant seigneur. "][0]
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
        
        self.achievmentImage = None
        self.lastChance= None
        self.bg_color = ORANGE
        
        self.prog_file_name = "progression"
        
        self.slaughter()
        self.deckSelection(0,None)
    
    def initSecondCampaign(self):
        
        level1=Level()
        level1.image= pygame.image.load("gameAnimationImages/lac.jpg")
        level1.opponent = Profile("Autochtones du Lac","Le Lac",self,2)
        level1.difficulty = "Quite Easy"
        level1.scenario = ["Alors que vos troupes se retrouvaient pres d'un lac etrange, vous percevez un eclat brillant venant du fond du lac. Brillant, comme de l'or..."+
                            "Bien sur, il semble inutile de prevenir vos hommes. Cependant, alors que vous vous approchez de l'eau, la faune du lac s'attaque brusquement a vous." +
                             " Des pecheurs se joignent alors a eux, et vous vous trouvez forces a faire un choix: combattre ou renoncer. Ce serra combatre."][0]
        level1.avatar = "LeLac#.png"
        level1.options = ("Algues",)

        level2 = Level()
        level2.image= pygame.image.load("gameAnimationImages/pirates.jpg")
        level2.opponent = Profile('Capitaine "Barbe Fumante"',"Pirates des Mers Maudites",self,2)
        level2.difficulty = "Quite Hard"
        level2.scenario = ["Vous trouvez l'objet brillant, il se trouve etre un magnifique combas en or. Mais il n'indique pas le nord, et "+
                           "un des pecheurs vous informe sur la nature de l'objet: c'est un compas qui mene vers le legendaire Baton de la Lune Rugissante. "+
                           "C'est un objet d'une valeur inimaginable. Vous voila donc en quete de ce baton mystique, arpentant les dangereuses mers en"+
                           " se dirigeant vers le nord. Une attaque n'est donc pas surprennante."][0]
        level2.avatar = "MonCapitaine#.png"
        level2.options = ("FrozenBoats",)

        level3 = Level()
        level3.image= pygame.image.load("gameAnimationImages/terrestre.jpg")
        level3.opponent = Profile("Terre Primitive","Reveil De La Roche",self,2)
        level3.difficulty = "Hard"
        level3.scenario = ["Apres plusieurs moi de mer, vous mettez pied sur une ile tres surprennante. Personne ne se sent a l'aise, et on se rend vite compte que l'ile elle meme est maudite par des forces surhumaines."+
                    " La mort meme semble y avoir plus de povoir. Soudain, alors que la terre se secoue et se fissure,"+
                               " une voix porteuse de colere resonne gravement depuis les failles..."][0]
        level3.avatar = "EarthEntity#.png"
        level3.options = ("AgonieResonante",)

        level4 = Level()
        level4.image= pygame.image.load("gameAnimationImages/mahishasura.jpg")
        level4.opponent = Profile("Le Culte du Mahishasura","Mahishasura",self,2)
        level4.difficulty = "Medium"
        level4.scenario = ["Heureusement, une autre ile etait tres proche. Vous tombez alors sur des edifices surprennants, temoignants de la presence d'un peuple tres religieux. "+
                           "Vous identifiez les idoles comme etant indiennes lorsque les cultistes vous reperent et vous attaquent. Il est clair que vous etes pour eux des ennemis."][0]
        level4.avatar = "Mahishasura#.png"
        level4.options = ("Lakshmi",)
        
        level5 = Level()
        level5.image= pygame.image.load("gameAnimationImages/jungle.jpg")
        level5.opponent = Profile("Seth le Cruel","Guilde des Braves d'Edemas",self,2)
        level5.difficulty = "Quite Easy"
        level5.scenario = ['"Vous?! Je ne pensais pas vous trouver ici! Cette fois, vous ne me vaincrez pas, car mes nouveaux '+
                            'allies sont bien meilleurs que la horde stupide, et utiliseront cet espace restreint de combat a leur avantage.'+
                            ' Je vous presente la grande, et unique, Guilde des Braves d\'Edemas!"'][0]
        level5.options = ("LimiteNombreCreatures3",)        
        level5.avatar = "Gobelin#.png"
        
        level6 = Level()
        level6.image= pygame.image.load("gameAnimationImages/toundra.jpg")
        level6.opponent = Profile("Asmund des Plaines Neigeuses","Chasseurs des Plaines Neigeuses",self,2)
        level6.difficulty = "Hard"
        level6.scenario = ["Vous poursuivez votre quete vers le nord. Peu a peu, l'air se refroidit et la nourriture se fait plus rare."
                            +"Au bout de quelques jours, le froid devient insoutenable et vos hommes commencent a en souffrir."+
                            " Pire, le desespoir gagne vos troupes. C'est donc avec plaisir que vous decidez d'attaquer la tribu locale en pensant "+
                            "qu'elle vous permettra une victoire facile qui motivera vos troupes. Ce fut une grosse erreur." ][0]
        level6.options = ("FroidIntenable",)      
        level6.avatar = "ChefPlainesNeigeuses#.png"

        level7 = Level()
        level7.image= pygame.image.load("gameAnimationImages/voyageurs.jpg")
        level7.opponent = Profile("Les Recifs","MagiePure",self,2)
        level7.difficulty = "Hard"
        level7.scenario = ["Vous etes en vue de l'objet de votre quete. Cependant, la magie sort"+
              " du baton mystique en flots qui forment une mer etrange dans laquelle il faut s'enfoncer."+
              "Les vagues de magie pure ont scupte les rochers avoisinant en dangereux recifs."+
              "Les creatures qui viennent ici sont soit dechiquetes par ces recifs, soit elimines par la magie puissante qui sevit ici."][0]
        level7.avatar = "Recifs#.png"
        level7.options = ("Recifs",)  
        
        level8 = Level()
        level8.image= pygame.image.load("gameAnimationImages/staff.jpg")
        level8.opponent = Profile("Voyageurs d'Outreplans","Voyageurs d'Outreplans",self,2)
        level8.difficulty = "Hard"
        level8.scenario = ["Alors que vous vous emparez du baton, une force puissante le retire de vos mains et il se met a leviter. Devant les yeux de vos hommes s'ouvre alors un "+
                            "portail d'une ampleur gigantesque."
                           +" Une horde de creatures magiques debarque, et une grande louve a l'aspect astral apparait dans le ciel. Une voix terrifiante se fait alors entendre dans la plaine"+
                           ", elle semble provenir de l'immense visage: \" Cette magie n'est pas pour vous, humains. Un tel pouvoir serait bien trop dangereux entre vos mains. Pour la securite de votre monde, nous devons vous le prendre, "+
                           "ainsi que detruire tous ceux qui en eurent la connaissance.\" "+
                           "Vous devez a present vous battre pour vos vies, et pour recuperer le baton (il est donc bien evident que vous perdez si il est detruit)."][0]
        level8.avatar = "ReineDesVoyageurs#.png"
        level8.options = ("Baton de La Lune Rugissante","SetHeroLives40")      

        self.all_levels = [level1,level2,level3,level4,level5,level6,level7,level8]

        self.prog_file_name = "progression2"
        
        self.achievmentImage = None
        self.lastChance= None

        self.bg_color = ORANGE
        
        self.deckSelection(0,None)

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
        self.bg_img  = None
        button = Button(450,130,img_campaign_button,self.campaignSelection,self,[])
        self.all_sprites_list.add(button)
        button = Button(450,325,img_cardedit_button,self.coutCartesMonstres,self,[])
        self.all_sprites_list.add(button)
        button = Button(450,510,img_deckcreation_button,self.deckCreation,self,[])
        self.all_sprites_list.add(button)
        button = Button(450,695,img_battle_button,self.initDeckSelection,self,[])
        self.all_sprites_list.add(button)

    def matchSelection(self,deck):
        self.slaughter()
        self.progression = eval(open(self.prog_file_name,"r").read())
        if deck not in self.progression.keys():
            self.progression[deck]=(0,0,None)
        print("debug",copy,self.progression)
        oldmonstervalues=copy(self.progression[deck][2])
        # verification du deck
        if oldmonstervalues :
            newvalues=[int(m.getCost()*1000) for m in CardGame.Game().chooseDeck(deck)]
            print (sorted(oldmonstervalues))
            print (sorted(newvalues))
            differences=0
            for m in CardGame.Game().chooseDeck(deck) :
                v=int(m.getCost()*1000)
                if v in oldmonstervalues :
                    oldmonstervalues.remove(v)
                else :
                    print (m.name,int(m.getCost()*1000)," modifie ou non present precedemment")
                    differences+=1
            print ("il reste ",oldmonstervalues)
            if max(len(oldmonstervalues),differences)>2 :
                import tkinter
                result = tkinter.messagebox.askyesno("Le deck a trop changé","Voulez vous repartir a zero ?")
                print (result)
                if result==True :
                    self.progression[deck]=[0,0,None]
                else:
                    self.slaughter()
                    global screen
                    screen = pygame.display.set_mode(size)
                    self.initialize()
                    return
        level=self.progression[deck][0]
        print ( "Level are done until level: ",level)
        self.unlocked_levels = self.all_levels[:level+1]
        
        self.bg_color = (240,255,245)
        self.bg_img = pygame.transform.scale(pygame.image.load("gameAnimationImages/6467ea27fd38dec4efc93ce6cecf5bd2.jpg"),size)
        self.play_button = self.viewer = None
        for n,level in enumerate(self.all_levels):
            if level in self.unlocked_levels:
                locked = False
                image = pygame.transform.scale(level.image,(120,90))
            else:
                locked = True
                image = pygame.transform.scale(pygame.image.load("gameAnimationImages/locked-door.png"),(120,90))
            button = Button(100,110*(n+1)-50,image,self.displayMatch,self,[level,n,locked,deck])
            self.all_sprites_list.add(button)
        self.previous = self.modeSelection

    def deckSelection(self,n,deck):
        self.slaughter()
        self.bg_color = BLUE
        #print "n is :",n
        image = pygame.transform.scale(pygame.image.load("gameAnimationImages/BlankButton.png"),(240,100))
        if 1 or n==0:
            playable_decks = [file2name(d,'.dek') for d in glob.glob("Decks/*.dek")]
            all_decks = copy(playable_decks)
        
            for d in reversed(playable_decks):
                if d in self.blocked_decks:
                    playable_decks.remove(d)
            list_ = playable_decks
            print ("limited choice ",)
        else:
            list_ =  all_decks
        l = len(list_)
        print ("list_",list_)
        if n==2 : l+=1
        for x,i in enumerate(list_):
            angle = (x+1)*360/l
            x_center = int(math.sin(math.radians(angle))*350) + size[0]/2
            y_center = int(math.cos(math.radians(angle))*350) + size[1]/2
            #print x_center,y_center,angle
            if n==2:
                button = DeckButton(x_center,y_center,image,self.playBattle,self,[deck,i],i)
                self.all_sprites_list.add(button)
                #print "level 2 selection"
            elif n==0:
                button = DeckButton(x_center,y_center,image,self.matchSelection,self,[i],i)
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
            y_center = int(math.cos(math.radians(angle))*150) + size[1]/2
            #print x_center,y_center,angle
            button = DeckButton(x_center,y_center,image,self.startNetGame,self,[deck],"NET BATTLE")
            self.all_sprites_list.add(button)
            
            self.adv_type_button = Button(size[0]/2,size[1]/2,image2,self.changePlayerType,self,[])
            self.all_sprites_list.add(self.adv_type_button)
        self.previous = self.modeSelection
                
    def initDeckSelection(self):
        self.adversory_type = "Computer"
        self.deckSelection(1,None)
        self.previous = self.modeSelection
    
    def campaignSelection(self):
        self.slaughter()
        self.previous = self.modeSelection
        self.bg_color = (20,20,20)
        
        image = pygame.transform.scale(pygame.image.load("gameAnimationImages/button_campaign1.png"),[700,380])
        
        image2 = pygame.transform.scale(pygame.image.load("gameAnimationImages/button_campaign2.png"),[700,380])
        
        campaign_button1 = InteractiveButton(size[0]/2,250,image,self.initFirstCampaign,self,[])
        campaign_button2 = InteractiveButton(size[0]/2,size[1]-250,image2,self.initSecondCampaign,self,[])
        self.all_sprites_list.add(campaign_button1)
        self.all_sprites_list.add(campaign_button2)
        

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
        from deck_creation import getBlockedCreatures
        CoutCartesMonstres.run(getBlockedCreatures(self.blocked_decks))
        pygame.init()
        global screen

        screen = pygame.display.set_mode(size)
        self.slaughter()
        self.__init__()
        self.initialize()

    def deckCreation(self):
        from tkinter import Tk
        fenetre = Tk()
        fenetre.title('Clic to add a monster to deck _ close this windows to end deck creation')
        from deck_creation import DeckCreator
        a=DeckCreator(fenetre,self.blocked_decks)
        fenetre.mainloop()

#        global playable_decks
#        playable_decks = [file2name(d,'.dek') for d in glob.glob("Decks/*.dek")]
#        global all_decks
#        all_decks = copy(playable_decks)
#        for d in reversed(playable_decks):
#            if d in blocked_decks():
#                playable_decks.remove(d)

    def displayMatch(self,level,num,locked,deck):
        print ("Match number {0} selected".format(num))
        if self.viewer:
            self.viewer.kill()
        if self.lastChance :
            self.lastChance.kill()
            self.lastChance=None
        if self.achievmentImage :
            self.achievmentImage.kill()
        if not(locked):
            if self.play_button:
                self.play_button.kill()
            self.play_button = Button(475,500,pygame.transform.scale(img_playmission_button,(310,110)),self.selectMatch,self,[level,num,deck])
            self.all_sprites_list.add(self.play_button)
            level.show()

            achievement,trynumber,oldmonstervalues = self.progression[deck]
            self.viewer = Viewer(level.makeImage(),100,20)
            self.all_sprites_list.add(self.viewer)
            if self.all_levels.index(level)==achievement and trynumber==2 and achievement>0 :
                font = pygame.font.SysFont("latobolditalic",24)
                text = font.render("Attention, c'est votre derniere chance avant de devoir battre en retraite",False,(3,0,0))
                image = pygame.Surface((700,40))
                image.fill((205,205,205))
                #image.blit(text,(100,190+6*25))
                image.blit(text,(30,10))
                self.lastChance = Viewer(image,200,350)
                self.all_sprites_list.add(self.lastChance)
            self.achievmentImage = Viewer(pygame.transform.scale(pygame.image.load(["gameAnimationImages/AchievmentEmpty.png","gameAnimationImages/AchievmentDone.png"][self.progression[deck][0]>num]),(100,100)),750,650)
            self.all_sprites_list.add(self.achievmentImage)

        else:
            print( "Level Locked")
            if self.play_button:
                self.play_button.kill()
            self.achievmentImage = None
            self.viewer = Viewer(level.lockedImage(),100,20)
            self.all_sprites_list.add(self.viewer)

    def selectMatch(self,level,num,deck):
        self.previous = self.campaignSelection
        self.level_selected = level
        self.num = num
        self.playLevel(deck)

    def playLevel(self,deck):
        level = self.level_selected
        print ("*** Match number {0} played".format(self.num)," by ",deck)
        achievement,trynumber,oldmonstervalues = self.progression[deck]
        if self.all_levels.index(level)==achievement :
            if trynumber==2 and achievement>0 :
                self.progression[deck]=(achievement-1,1,oldmonstervalues)
            else :
                self.progression[deck]=(achievement,trynumber+1,oldmonstervalues)
        open(self.prog_file_name,"w").write(str(self.progression))
        import CardGame
        gam = CardGame.Game()
        self.runninggame = gam
        deck1=gam.chooseDeck(deck,1)
        gam.player1=Player.Player("Player",deck1,gam)#,2,verbose=0,hide=False)
        gam.player2=Player.Computer(level.opponent.name,gam.chooseDeck(level.opponent.deckname,2),gam,2,verbose=0,hide=True)
        if "" in deck1 :
            gam.player1.avatar_img=pygame.image.load(deck1[""])
        else :
            gam.player1.avatar_img=pygame.image.load("Avatars/Chevalier_noir#.png")
        gam.player2.avatar_img=pygame.image.load("Avatars/"+level.avatar)
        gam.initialize()
        print (level.options)
        for opt in level.options:
            gam.activateOption(opt)
        gam.play()
        winner = gam.get_winner() # player name or None if quit manually
        if winner == "Player" and self.all_levels.index(level)==achievement:
            print ("progression advanced")
            self.progression[deck]=(achievement+1,0,[int(m.getCost()*1000) for m in gam.chooseDeck(deck,1)])
            open(self.prog_file_name,"w").write(str(self.progression))
            #self.unlocked_levels = self.all_levels[:self.level_prog]
        self.slaughter()
        global screen
        screen = pygame.display.set_mode(size)
        self.initialize()

    def playBattle(self,deck1,deck2):
        print( "Arena Battle between {0} and {1}".format(deck1,deck2))
        gam = CardGame.Game()
        self.runninggame = gam
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
        global screen
        screen = pygame.display.set_mode(size)
        self.initialize()

    def startNetGame(self,deck_name) :
        print( "play net game with deck",deck_name)
        from CardGame import NetGame
        from Player import Player,HostedPlayer
        game = NetGame()
        self.runninggame = game
    #game.defaultPlayers(player1_set,player2_set)   
        game.player1=Player("Player",game.chooseDeck(deck_name),game)
        game.player2=HostedPlayer(game)
        game.initialize()
        game.play()


if __name__=='__main__':

    pygame.init()
    
    size = (900, 900)
    screen = pygame.display.set_mode(size)
    
    game = Game()   # game.gam ou game.runninggame is the Card Game
    
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
    game.bg_img = None
    
    while not(game.done):
        screen.fill(game.bg_color)
        if game.bg_img:
            screen.blit(game.bg_img,[0,0])
        game.update()
        pygame.display.flip()
        clock.tick(30)
    
    
    pygame.quit()
