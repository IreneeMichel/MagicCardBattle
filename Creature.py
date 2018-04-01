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
    def __init__(self,card,player,is_invocation=False,origin=None,bonus=False,damages=0,triggerPlayingEffect=False,param={}) :
        if hasattr(player,"verbose") and player.verbose>3 : print "      Creature __init__ ",card.name," from ",player.name
        # origin is usually a cardInHand
        self.card=card
        if param : # sert pour le loadgame, beaucoup seront reecrases ensuite
            for n,v in param.iteritems() :
                setattr(self,n,v)
        self.is_dead = False
        self.max_pv =card.pv
        self.pv = self.max_pv - damages
        self.att=card.att
        self.name=card.name
        self.player=player
        self.game = player.game 
        self.marks={}
        if bonus==False :
            self.bonus=[copy(b) for b in card.bonus]
        else:
            self.bonus=bonus
            print "My bonus are defined and are: ",bonus
            if len(bonus)==0 and len(card.bonus)>0 :
                self.addMark("cross",size=(300,400),pos="center",typ="",level=1,value=0)
            for b in self.bonus :
                for e in card.bonus :
                    if b.__class__ is e.__class__ :
                        break
                else :
                    self.addMark(b.getInlineDescription(),typ="power",value=0)
        for b in self.bonus:
            b.owner=self
   
        self.ready=False
        card.costint = int(card.getCost())
        card.starcost = card.getStars()
        self.starcost=card.starcost
        self.game.setId(self)
        player.army.append(self)
        #print "army apres append",player,[(c.id,c.name) for c  in player.army]

        if card.pv==0 :
            # it is a spell
            #if not(self.bonus):
            #    print "creature",self,self.name,"de",self.player.name," bonus=",self.bonus
            for m in player.army :
                if m.max_pv>0 :
                    for b in m.bonus :
                        b.spellLaunched(self)
            for m in player.adv.army :
                for b in m.bonus :
                    b.otherSpellLaunched(self)
            #print "owner2",self.bonus[0].owner
            if origin and hasattr(origin,"getPosition") :
                self.setPosition(origin.getPosition())
            self.game.effect_list.append([1,self.id,"appear",[]])
            player.launch(self,card.bonus[0])
        else :
            if origin and isinstance(origin,Creature) :
                self.is_invocation=True
            else :
                self.is_invocation=False
            if not "simu" in self.player.name :
                print "creation de creature ",self.name
            for b in reversed(self.bonus) :
                #if not "simu" in self.player.name :
                #    print "after invoc ",b
                b.afterInvocation(self)
                if triggerPlayingEffect:
                    b.whenPlayed(self)
            for m in player.army :
                if m is not self :
                    for b in m.bonus :
                        b.additionalBonus(self)
            if triggerPlayingEffect:
                for m in player.adv.army :
                    if m.pv > 0 :
                        for b in m.bonus :
                            b.otherMonsterCreation(self)
            self.game.effect_list.append([1,self.id,"appear",[]])
    def __eq__(self, other):
        return self is other
    def equivalentto(self,other) :
#        print [p1.__class__ for p1 in self.bonus],[p1.__class__ for p1 in other.bonus],[p1.__class__==p2.__class__ for p1,p2 in zip(self.bonus,other.bonus)]
#        if self.name==other.name :
#            print (self.pv  == other.pv) , (self.att == other.att) , all([p1.__class__==p2.__class__ for p1,p2 in zip(self.bonus,other.bonus)]) , (self.ready == other.ready) , (self.player == other.player)
#            raise
        return (self.pv  == other.pv) and (self.att == other.att) and all([p1.__class__==p2.__class__ for p1,p2 in zip(self.bonus,other.bonus)]) and (self.ready == other.ready) and (self.player == other.player)        
    def beginTurn(self) :
        #if isinstance(self,AnimatedCreature) : print "normal begin turn de ",self.name
        self.ready=True
        for b in self.bonus:
            b.beginTurn(self)
        self.updateImage()
    def getInlineDescription(self):
        return self.name +" ("+str(self.att)+"  "+str(self.pv)+' '.join(
            [b.getInlineDescription() for b in self.bonus]) +" )"
    def endTurn(self):
        for p in reversed(self.bonus):  # pour bien remettre les choses en place
            p.endturn(self)
    def combatAnim(self,target) :
        self.combat(target)
    def combat(self,target) :
        #from Player import Computer0
        #if not isinstance(target.player,Computer0) : print "combat de base",self,"attaque ",target
        #if isinstance(self.player,Computer0) : print " "*4*(2-self.player.nv),"combat de base",self.name,"attaque ",target.name
        self.ready=False
        for b in self.bonus :
            #print b.__class__.__name__
            b.beforeCombat(self,target)
        if target != self :
            for b in target.bonus :
                #print b.__class__.__name__
                b.beforeCombat(self,target)
        self.combatSequence(target)
        self.game.effect_list.append([2,self.id,"afterCombat",[target.id]]) # apres le defend
        self.game.effect_list.append([2,target.id,"afterCombat",[self.id]])
        self.game.effect_list.append([2,self.id,"updateImage",[]])
    def afterCombat(self,adv) :
        #from Player import Player
        #if not isinstance(adv,Player) : print "aftercombat basic",self.name
        #if self.pv <1 :
        for b in reversed(self.bonus) :
            b.afterCombat(self,adv)
    def combatSequence(self,target) :
#        print "infos sur defend ,game ",self.player.game.player1.name, " : ",[1,target.id,"defend",[self.id]],"    ",len(self.player.game.effect_list)
        self.player.game.effect_list.append([1,target.id,"defend",[self.id]])        
        self.attack(target)
        #target.defend(self)
        #if self.att>0 : print "combat sequence",self.name,target.name,'de',target.player.name
    def attack(self,target) :
        #print "att",[(m.name,m.att) for m in self.player.army]
        damage=self.att
#        for b in self.bonus :
#            damage=b.modifyDamage(self,damage,target)
        target.sufferDamage(damage)
    def defend(self,target) :
        #print "defend normal"
        self.attack(target)
    def sufferDamage(self,damage):
        if self.max_pv==0 :
            print "error degat sur sort ?",self.name
            raise
        for b in reversed(self.bonus) : # pour que le dernier modificateur soit le premier a agir
            damage=b.modifyTakenDamage(damage)
        if damage > 0 :
            self.sufferDamageAnimation(damage)
        self.pv-=damage
        self.updateImage()
        if self.pv <1 and self.pv+damage>0 :
            #"print "                   die due to damage"
            self.die()
#    def sufferDamageAnimation(self,damage) :
#         pass
    def updateImage(self) :
        pass
    def sufferDamageAnimation(self,damage) :
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
    
#    def constructor(self):
#        
#        #serra rappele par un game 
#        
#        player_str = "self.player"+str(1+[self.player.game.player1,self.player.game.player2].index(self.player))
#        return "Creature("+player_str
    
    def getValue(self):
        if self.pv > 0 and not any([(p.__class__.__name__=="Errant") for p in self.bonus]) :
            #print "get cost",self.name,[p.__class__.__name__ for p in self.bonus]
            cost=self.att/2.+self.pv/2.+sum([abs(p.getCost(self))*p.interest*(2.+self.pv)/4. for p in self.bonus])
            #print self.att/2.,self.pv/2.,[(p.__class__.__name__,abs(p.getCost(self))*p.interest*(2.+self.pv)/4.) for p in self.bonus]
            for b in self.bonus :
                if b.interest>1. :
                    print "pb value with ",b.__class__,self.name
                    b=0/0
            #if len(self.bonus)>0 : print self.name,cost,[(p.constructor(),abs(p.getCost(self))*p.interest) for p in self.bonus],2.5*sum([p.getStars() for p in self.bonus])
#            for p in self.bonus :
#                if abs(p.getCost(self))*p.interest < 0. :
#                    print p.constructor()," is negative "
            #print "cost",cost,2.5*sum([p.getStars() for p in self.bonus]),sum([m[0] for m in self.marks.values()])
            return cost+2.5*sum([p.getStars() for p in self.bonus])+sum([m[0] for m in self.marks.values()])
        else :
            return 0
    
    def die(self):
        if hasattr(self.player,"nv") :
            nv=self.player.nv
            verbose=self.player.verbose>2
        elif  hasattr(self.player.adv,"nv"):
            nv=self.player.adv.nv
            verbose=self.player.adv.verbose>2
        else :
            verbose=False
        if verbose : print " "*4*(2-nv), "die",self.name,self.id," de ",self.player.name," qui a ",[m.id for m in self.player.army]
#        print "self.pv",self.pv,type(self.pv)        
        self.pv=0
        if self in self.player.army :
            #print "%",self.name,self.id," de ",self.player.name," put in dead monsters "
            self.player.army.remove(self)
            self.player.game.dead_monsters.append(self)
            #print "for ",self.player.name," are dead",[m.name for m in self.player.game.dead_monsters]
        else :
            #print self.name," not in army ; en dead monsters  ?",self in self.player.game.dead_monsters
            if not (self in self.player.game.dead_monsters) :
                self.player.game.dead_monsters.append(self)
        if verbose : 
            print " "*4*(2-nv),"deads are ",[(m.name[:4],m.id) for m in self.player.game.dead_monsters]
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
        if self in self.player.army :
            print "very big problem"
            raise
        # dans la simu le monstre sera dans l armee donc il faut que le remove soit apres le launch de agonie
            # spells are removed from army 
            #if self.max_pv<1 :
            #print "Strange  : creature",self,self.name," not in army ?"
            #print self.player,self.player.name," army was : ",self.player.army,[c.name for c in self.player.army]
            #b=0/0
#    def castSpellAnimation(self) :
#        pass             
    def copy_methods(self, klass, *methods):
        """Copy methods from `klass` into this object.
        """
        for method in methods:
            self.copy_method(klass, method)
    def appear(self) :
        pass
    def takePlace(self,add=0):
        #print "    takePlace de creature=pass"
        pass
    def castSpellAnimation(self) :
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
   
class AnimatedCreature(Sprite,Creature) :
    def __init__(self,origin,card,player,**args) :
        if not hasattr(card,"image") :
            name=card.name.replace(" ","_")
            try :
                card.image = pygame.image.load("Cards/"+name+".png")
            except :
                import glob
                lina=glob.glob("*"+name+"*.png")+glob.glob("*/*"+name+"*.png")
                if lina :
                    card.image = pygame.image.load(lina[0])
                else :
                    screen_info = pygame.display.Info() #Required to set a good resolution for the game screen
                    height,width = screen_info.current_h, screen_info.current_w
                    print "image manquante ,name=",name
                    card.image = card.createImage(True)
                    pygame.image.save(card.image,name+".png")
                    card.image = pygame.image.load(name+".png")
                    pygame.display.set_mode((width,height))
        Sprite.__init__(self,origin,pygame.transform.scale(card.image,(136, 200)))
        self.baseImage=copy(card.image)
        self.all_effects = {}
        Creature.__init__(self,card,player,**args)

        self.index=len(player.army)
#        if not(type(origin)==type([])):
#            if card.pv>0:
#                destination=self.getPlace()
#                phase0 = (destination,10, self.size)
#                Animation(origin,[phase0])
#            else :
#                destination=[800,450]
#                phase0 = (destination,8, self.size)
#                phase1 = (destination,10, (272, 400))
#                phase2 = (destination,20, (600, 400))
#                Animation(origin,[phase0,phase1,phase2])
#        else :
#            print "origin is []"
                
    def equivalentto(self,other) :
        # les animated creaturepeuvent etre comparees a des autres sprites
        return (other.__class__==self.__class__) and Creature.equivalentto(self,other)
    def appear(self) :
        #print "appears",self.name
#        Sprite.__init__(self,origin,pygame.transform.scale(card.image,(136, 200)))
        #print [(c.name , len(c.content.bonus)) for c in player.hand]
#        if origin in player.hand :
#            player.hand.remove(origin) # old comment :remove avant creature sinon le getchoice de la simulation l oublie
        #self.setPosition(origin.center)
#        Creature.__init__(self,card,player,is_invocation=(isinstance(origin,Creature)),bonus=self.defined_bonus,damages=self.initial_damages,triggerPlayingEffect=self.triggerPlayingEffect)
        self.updateImage()
        if self.max_pv>0:
            destination=self.getPlace()
            phase0 = (destination,5, self.size)
            Animation(self,[phase0])
        else :
            destination=[800,450]
            phase0 = (destination,4, self.size)
            phase1 = (destination,5, (272, 400))
            Animation(self,[phase0,phase1])
        self.game.effect_list.append([19,self.player.id,"orderArmy",[]])

        #print "init animated creature done"

    def castSpellAnimation(self) :#print "launch from",origin,"  army is ",self.army
        sp=Sprite(self,"gameAnimationImages/boule_energie_bleue.png",[20,20])
        phase0=(self.getPosition(),8,[250,250])    
        Animation(sp,[phase0],True)

    def sufferDamageAnimation(self,damage) :
        #Sprite(sprite,"gameAnimationImages/stone.png")
        phase1 = (self.center,4,[4.*damage]*2)
        Animation(Sprite(self,wound_img),[phase1],True)

    def updateImage(self):
        #print "UPDATE_IMG"
        # on va creer le graphisme qui est l image de base modifiee par debats, ...
        # le graphism a une taille connue, l image peut etre reduite 
        self.graphism = copy(self.baseImage)
        if self.max_pv!=0 :
            wound=self.max_pv - self.pv
            #print "wound=",wound
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
            if self.ready or self.player!=self.game.player or self.pv==0 :
                #print "ready ",self.ready,self.name
                self.graphism.set_alpha(255)
            else :
                #print "gris",self.name,self.pv
                self.graphism.set_alpha(180)
        self.image = pygame.transform.scale(self.graphism,self.size)
        #self.image.set_alpha(180)
              
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
                    image=pygame.image.load("gameAnimationImages/"+fname)
                except :
                    try :
                        image=pygame.image.load(fname)                
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
            phase1 = (target.center,10, None)
            phase2=(self.center,10,None)
            animated_sprite=self
            for b in self.bonus :
                animated_sprite=b.attackAnimationSprite(animated_sprite)
            a=Animation(animated_sprite,[phase1]+[phase2]*(animated_sprite==self),animated_sprite!=self)
            a.phase_time = 2 # l attaque ne fait plus que 9/10 du trajet
            self.player.game.effect_list.append([9,self.id,"combat",[target.id]])
        else :
            self.combat(target)
    def die(self):
        Creature.die(self)
        self.kill()
        self.player.orderArmy()
        self.player.game.effect_list.append([10,self.player.id,"orderArmy",[]])
        if self.all_effects:
            for e in reversed(self.all_effects.keys()):
                self.game.temporary_sprites.remove(self.all_effects[e])
 
    def getPlace(self,add=0):
        # add is to prepare the add or remove of a card
        nb=len([m for m in self.player.army if m.pv>0])
        x = self.game.width/2 + (80*(self.index*2 - nb-add+1)*self.game.width)/1600
        #print self.name," getPlace ",self.index,"/(",len(self.player.army),"+",add,")   x=",x
        y=self.player.army.position_y
        if self.pv==0 :
            y=y/2+self.game.height/4
        return (x,y)
        
    def takePlace(self,add=0):
        #print "          take place de",self.name," en ",self.getPlace(add)[0]
        Animation(self,[(self.getPlace(add),4, self.size)])
        
    def endTurn(self):
        #print "end turn for ",self.name
        self.graphism.set_alpha(255)   
        self.image.set_alpha(255)
        Creature.endTurn(self)
    
    def constructor(self):
        # self,origin,card,player,simultaneous=1,now=False) :
        player = "self.player"+str([self.player.game.player1,self.player.game.player2].index(self.player)+1)
        bonus = "["+",".join([b.constructor() for b in self.bonus])+"]"
        paramdict=repr({att : getattr(self,att) for att in dir(self) if type(getattr(self,att)) in (type(1),type(True))})            
        return "AnimatedCreature(origin,"+self.card.constructor()+","+player+",bonus="+bonus+",damages="+str(self.max_pv-self.pv)+",param="+paramdict+")"
      
            
            
            

    #def initAnimation(self):
    #    pass
        #print "init_animation with no effect"


