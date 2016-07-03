import pygame
from copy import copy
from functools import partial
from Sprites import Animation,Sprite,Attach_to_Creature
#,Mark
import random
from types import MethodType,FunctionType
#from Spell import Multiplier
from Card import Card
wound_img = pygame.transform.scale(pygame.image.load("gameAnimationImages/damage.png"),(300,260))
wound_img.set_colorkey((0,0,0))

class Creature() :
    def __init__(self,origin,card,player) :
        if hasattr(player,"verbose") and player.verbose>4 : print "      Creature __init__ ",card.name," from ",player.name
        # origin is usually a cardInHand
        #print "creature init",card.name
        self.card=card
        self.is_dead = False
        self.max_pv = self.pv=card.pv
        self.att=card.att
        self.name=card.name
        self.bonus=[copy(b) for b in card.bonus]
        for b in self.bonus :
            b.owner=self
        self.player=player
        self.game = player.game    
        self.ready=False
        self.starcost=card.starcost
        player.army.append(self)
        #print "army apres add",player,[(c,c.name) for c  in player.army]
        self.marks={}   # ligne temproraire
        if self.pv==0 :
            # it is a spell
            #print "creature",self,self.name,"de",self.player.name," bonus=",self.bonus
            for m in player.army :
                if m.max_pv>0 :
                    for b in m.bonus :
                        b.spellLaunched(self)
            for m in player.adv.army :
                for b in m.bonus :
                    b.otherSpellLaunched(self)
            #print "owner2",self.bonus[0].owner        
            player.launch(self,card.bonus[0])
        else :
            self.marks={}
            if isinstance(origin,Creature) :
                self.is_invocation=True
            else :
                self.is_invocation=False
            for b in reversed(self.bonus) :
                #print "after invoc ",b
                b.afterInvocation(self)
            for m in player.army :
                if m is not self :
                    for b in m.bonus :
                        b.additionalBonus(self)
            for m in player.adv.army :
                if m.pv > 0 :
                    for b in m.bonus :
                        b.otherMonsterCreation(self)
            if len(player.army)>9 and "choix1"!=self.name and "choix2"!=self.name :
                player.sacrify()
    def beginTurn(self) :
        #if isinstance(self,AnimatedCreature) : print "normal begin turn de ",self.name
        self.ready=True
    def getInlineDescription(self):
        return self.name +" ("+str(self.att)+"  "+str(self.pv)+' '.join(
            [b.getInlineDescription() for b in self.bonus]) +" )"
    def endTurn(self):
        for p in reversed(self.bonus):  # pour bien remettre les choses en place
            p.endturn(self)
    def combatAnim(self,target) :
        self.combat(target)
    def combat(self,target) :
        #from Player import Player
        #if not isinstance(target,Player) : print "combat de base",self.name,"contre ",target.name
        self.ready=False
        for b in self.bonus :
            b.beforeCombat(self,target)
        if target != self :
            for b in target.bonus :
                b.beforeCombat(self,target)
        self.combatSequence(target)
        self.afterCombat(target)
        target.afterCombat(self)
    def afterCombat(self,adv) :
        #from Player import Player
        #if not isinstance(adv,Player) : print "aftercombat basic",self.name
        #if self.pv <1 :
        for b in reversed(self.bonus) :
            b.afterCombat(self,adv)
    def combatSequence(self,target) :
        self.attack(target)
        target.defend(self)
    def attack(self,target) :
        damage=self.att
        for b in self.bonus :
            damage=b.modifyDamage(self,damage,target)
        target.sufferDamage(damage)
    def defend(self,target) :
        self.attack(target)
    def sufferDamage(self,damage) :
        self.sufferDamageAnimation(damage)
        self.pv-=damage
        if self.pv <1 and self.pv+damage>0 :
            #"print "                   die due to damage"
            self.die()
    def sufferDamageAnimation(self,damage) :
         pass
    def updateImage(self) :
        pass
    def addMark(self,name,pos="center",typ="external",level=1,size=0,value=0) :
        if "-simu" not in self.player.name :
            print "fatal error Mark playing",self.name
            raise "toto"
        self.marks[name]=[value]
    def removeMark(self,name,level=1) :
        if name in self.marks :
            del self.marks[name]
    def hasMark(self,name) :
        return (name in self.marks)
    def die(self):
        self.pv=0
        if self.is_dead == False :
            self.is_dead = True
            if self.max_pv>0 :
                for b in self.bonus:       
                    b.death(self)
                for m in self.player.army :
                    if m.max_pv>0 and m is not self  :
                        for b in m.bonus:
                            b.otherDeath(self)
                for m in self.player.adv.army :
                    if m.max_pv>0 and m is not self  :
                        for b in m.bonus:
                            b.enemyDeath(self)
        # dans la simu le monstre sera dans l armee donc il faut que le remove soit apres le launch de agonie
        if self in self.player.army :
            self.player.army.remove(self)
        else :
            pass
            # spells are removed from army 
            #if self.max_pv<1 :
            #print "Strange  : creature",self,self.name," not in army ?"
            #print self.player,self.player.name," army was : ",self.player.army,[c.name for c in self.player.army]
            #b=0/0
    def castSpellAnimation(self) :
        pass             
    def copy_methods(self, klass, *methods):
        """Copy methods from `klass` into this object.
        """
        for method in methods:
            self.copy_method(klass, method)
    def takePlace(self,add=0):
        #print "    takePlace de creature=pass"
        pass
   
class CreatureCopy(Creature) :
    def __init__(self,original,player) :
        for i in dir(original) :
            if i not in ("sufferDamageAnimation","takePlace","castSpellAnimation","combatAnim","appear","die","addMark","removeMark","updateImage") and i[0]!= "_":
                if callable(getattr(original,i)) :
                    m1=getattr(original,i)
                    f=FunctionType(m1.func_code,globals(),closure=m1.func_closure)
                    m=MethodType(f,self)
                    setattr(self,i,m)
                else :
                    setattr(self,i,copy(getattr(original,i)))
        self.player=player  # difference importante avec l original : game et player
        self.game=player.game
        self.bonus=[copy(b) for b in original.bonus]
        for b in self.bonus :
            b.owner=self

#class AnimatedSpell(Sprite,Spell):
#    def __init__(self,origin,card,player) :
#        if not hasattr(card,"image") :
#            name=card.name.replace(" ","_")
#            card.image = pygame.image.load(name+".png")
#        Sprite.__init__(self,origin,pygame.transform.scale(card.image,(136, 200)))
#        #        self.player=player
#        effect=partial(self.appear,*(origin,card,player))  # creature appears only then
#        #destination=self.getPlace(add=1)
#        phase0 = (destination,30, self.size,effect)
#        Animation(origin,[phase0])
#        #self.game.all_animations.add(self)
#        #self.game.animation_runing = True        
#        #self.anim_num = 0
#        #player.army.add(self)
#    def attack(self,creature) :
#        #self.setPosition(origin.center)
#        Spell.__init__(self,origin,card,player)    
#        player.hand.remove(origin)
#        #print "init animated creature done"
   
class AnimatedCreature(Sprite,Creature) :
    def __init__(self,origin,card,player,simultaneous=1) :
        #print "animated creature init ",card.name,origin,card
        # creature is init only after effect
        if not hasattr(card,"image") :
            name=card.name.replace(" ","_")
            card.image = pygame.image.load("Cards/"+name+".png")
        Sprite.__init__(self,origin,pygame.transform.scale(card.image,(136, 200)))
        self.game=player.game
        self.player=player
        self.index = len(player.army)+simultaneous-1
        self.graphism = copy(card.image)
        self.name=card.name   # ligne utile pour debug de getplace
        player.orderArmy(add=simultaneous)
        effect=partial(self.appear,*(origin,card,player))  # creature appears only then
        if card.pv>0 :
            destination=self.getPlace(add=simultaneous)
        else :
            destination=[800,450]
        phase0 = (destination,10, self.size,effect)
        Animation(origin,[phase0])
        self.all_effects = {}
        #self.game.all_animations.add(self)
        #self.game.animation_runing = True        
        #self.anim_num = 0
        #player.army.add(self)
    def appear(self,origin,card,player) :
        #print "appear",origin,card
        if origin in player.hand :
            player.hand.remove(origin) # remove avant creature sinon le getchoice de la simulation l oublie
        self.setPosition(origin.center)
        Creature.__init__(self,origin,card,player)
        player.orderArmy(add=0)

        #print "init animated creature done"

    def castSpellAnimation(self) :#print "launch from",origin,"  army is ",self.army
        sp=Sprite(self,"gameAnimationImages/boule_energie_bleue.png",[20,20])
        phase0=(self.getPosition(),8,[250,250],None)    
        Animation(sp,[phase0],True)

    def sufferDamageAnimation(self,damage) :
        #Sprite(sprite,"gameAnimationImages/stone.png")
        phase1 = (self.center,5,[4.*damage]*2,self.updateImage)
        Animation(Sprite(self,wound_img),[phase1],True)     
    def updateImage(self):
        #print "UPDATE_IMG"
        # pas sur d avoir une card ici
        # le graphism a une taille connue, l image peut etre reduite 
        self.graphism = copy(self.card.image)
        wound=self.max_pv - self.pv
        if not "wound" in self.marks :
            if wound :
                self.marks["wound"]=[0,wound_img,"random",wound,"multiple"]
        else :
            self.marks["wound"][3]=wound
        self.child=[]
        #print " update",self.name,"with",self.marks.keys()
        for i,o in self.marks.items() :
            #print "update mark",i,o
            value,image,position,level,typ=o
            lx,ly=image.get_size()
            if typ=="external" :
                sx,sy=self.size
            else :
                sx,sy=self.graphism.get_size()
            #print " creature size is ",self.size
            nb=[1,level][typ=="multiple"]
            #print "nb",nb,":",level,typ
            for i in range(nb) :
                if position=="random" :
                    pos_mod=(random.random()*(sx*1.-lx)+sx*0.0,random.random()*(sy*1.-ly)+sy*0.)
                elif position=="center" : # ce serait mieux de faire ce calcul dans addMark
                    pos_mod=(sx/2.-lx/2.,sy/2.-ly/2.)
                    #print "center, pos_mod",pos_mod
                elif position=="sw" : # ce serait mieux de faire ce calcul dans addMark
                    pos_mod=(sx*0.3-lx/2.,sy*0.9-ly/2.)
                    #print "sw, pos_mod",pos_mod
                elif position=="se" : # ce serait mieux de faire ce calcul dans addMark
                    pos_mod=(sx*0.7-lx/2.,sy*0.9-ly/2.)
                elif position=="s" : # ce serait mieux de faire ce calcul dans addMark
                    pos_mod=(sx*0.5-lx/2.,sy*0.9-ly/2.)
                    #print "se, pos_mod",pos_mod
                else :
                    pos_mod=position
                if typ=="external" :
                    #print "external"
                    self.child.append(Attach_to_Creature(self,image,pos_mod))
                else :
                    #print " blit de mark ",image,position," sur ",self.name
                    self.graphism.blit(image,pos_mod)
                    if typ=="number" :
                        font = pygame.font.SysFont("Calibri Bold",46)
                        text = font.render("+"*(level>0)+str(level),False,(0,0,0))
                        self.graphism.blit(text,(pos_mod[0]+lx/2-20,pos_mod[1]+ly/2-15))

        self.image = pygame.transform.scale(self.graphism,self.size)
              
    def addMark(self,name,pos="center",typ="external",level=1,size=0,value=0) :
        # a mark is list of an origin (string or instance), an image (or list of) (string or image), a position on card
        # image and position are string
        #print "add Mark"
        #print " addMark , creature ",self.name," has ",self.marks.keys()," and we add ",name
        
        if not (name in self.marks) :            
            #effect = eval(tipe)(self,eff_img,pos,level)
            if typ=="power" :
                nbpo=len([1 for m in self.marks.values() if m[4]=="power"])
                pos=(187.-5.5*len(name),167*2.+(4-nbpo)*20*2.)
                image=pygame.Surface((10+11*len(name),30))
                image.fill((60,60,100))
                font = pygame.font.SysFont("Calibri Bold",30)
                text = font.render(name,False,(0,0,0))
                image.blit(text,(5,10))    
            else :
                fname=name
                if not "." in name :
                    fname=name+".png"
                try :
                    image=pygame.image.load(fname)
                except :
                    try :
                        image=pygame.image.load("gameAnimationImages/"+fname)
                    except :
                        import glob
                        u=glob.glob("*/"+fname)
                        if u :
                            image=pygame.image.load(u[0])
                        else :
                            print "Mark : */"+fname," not found"
                            raise
            if size :
                image = pygame.transform.scale(image,size)
            #image.convert_alpha()
    
            image.set_colorkey((0,0,0))
            self.marks[name]=[value,image,pos,level,typ]
        #    self.game.temporary_sprites.add(effect)
        #    self.all_effects[name]=effect
        else :
        #    == "Mark":
            self.marks[name][3] += level
        #print " addMark , creature ",self.name," has ",self.marks.keys()
        self.updateImage()
        
        #if name in marks
        #self.marks.append((name,origin,image,position))
        #self.graphism.blit(image,position)
    def removeMark(self,name,level=0) :
        if not name in self.marks  :
            print "removeMark : fatal error : name",name," not in marks ",self.marks.keys()," of creature ",self.name,self
            return
        if level :
            #print " level ->",self.marks[name][2],"-",level
            self.marks[name][3]-=level
        if self.marks[name][3]==0 or not level :
            del self.marks[name]
        #print " removeMark ",name,", creature ",self.name," now has ",self.marks.keys()
        self.updateImage()
    #def imageEffect(self,(name,image_name,size),pos=(0,0),tipe="Attach_to_Creature",level=0):

    #def destroyEffect(self,name,lv=0):
    #    print name," destroyed from ",self
    def combatAnim(self,target):
        #print "combat de base pour animated creature"
        if target is not self :
            phase1 = (target.center,10, None,partial(self.combat,*(target,)))
            phase2=(self.center,10,None,None)
            animated_sprite=self
            for b in self.bonus :
                animated_sprite=b.attackAnimationSprite(animated_sprite)
            a=Animation(animated_sprite,[phase1]+[phase2]*(animated_sprite==self),animated_sprite!=self)
            a.phase_time = 2 # l attaque ne fait plus que 9/10 du trajet
        else :
            self.combat(target)
        
    def die(self):
        self.kill()
        Creature.die(self)
        self.player.orderArmy()
        
        if self.all_effects:
            for e in reversed(self.all_effects.keys()):
                self.game.temporary_sprites.remove(self.all_effects[e])
 
    def getPlace(self,add=0):
        # add is to prepare the add or remove of a card
        nb=len([m for m in self.player.army if m.pv>0])
        x = self.game.width/2 + (80*(self.index*2 - nb-add+1)*self.game.width)/1600
        #print self.name," getPlace ",self.index,"/(",len(self.player.army),"+",add,")   x=",x
        y=self.player.army.position_y
        return (x,y)
        
    def takePlace(self,add=0):
        #print "          take place de",self,self.name
        Animation(self,[(self.getPlace(add),3, self.size,None)])
    
            
            
            
            

    #def initAnimation(self):
    #    pass
        #print "init_animation with no effect"


