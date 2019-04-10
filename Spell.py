import tkinter
import re
from Target import getTargetMenu, getNegativeSpellTargetMenu
import Level
import Target

UP=re.compile('(?=[A-Z])')


class Spell :
    hasLevel=False
    has_target=True
    positive = False
    negative = False
    positive = False
    isMultiplier=False
    target_locked=False
    is_cost_alterator = False
    def __init__(self,target = Target.UneCibleAuChoix()) :
        self.parent=None
        self.target = target
    def constructor(self) :
        return "CardPowers."+self.__class__.__name__+"("+self.target.constructor()+")"
    def getDescription(self):
        if self.has_target:
            return self.getSpellDescription()+" "+self.target.getDescription()
        else:
            return self.getSpellDescription()
    def getSpellDescription(self):
        return re.sub(UP,' ',self.__class__.__name__)
    def getInlineDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)
    
    def modifyTarget(self,*args) :
        if not(self.target_locked):
            print ("modified target",self.target.__class__.__name__)
            self.target=eval("Target."+self.add_target.get())()
            self.card.getCost()
            self.card.refreshWidget()
    def isChanged(self,*args) :
        choice=self.content.get()
        exec('from CardPowers import '+ choice)
        new=eval(choice+'()')
        if self.parent :
            if type(self.parent)==type([]) :
                print ("Spell changed in list")
                self.parent[self.parent.index(self)]=new
            else :
                self.parent.spell=new
            new.parent=self.parent
            new.card=self.card
            #print 'changed in ',self.parent.spell  # ligne marche pas pour pure spell
        else :
            monster.bonus[monster.bonus.index(self)]=new
        self.card.refreshWidget()
        #new.initWidget(self)
    def initWidget(self,master,get_spell_menu = None, negative_target = False):
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        if get_spell_menu:
            self.spell_list=get_spell_menu(master,self.content)
        else:
            self.spell_list=getSpellMenu(master,self.content)
        self.widget.add(self.spell_list)
        #Target selector
        if self.__class__.has_target:
            if not(hasattr(self,"target")) and not(negative_target):
                self.target = Target.UneCibleAuChoix()
            elif not(hasattr(self,"target")) or negative_target and self.target.__class__ == Target.UneCibleAuChoix:
                self.target = [Target.MasseAllie,Target.MasseEnnemi][self.positive]()
            self.add_target = tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
            if negative_target:
                self.addTarget_wid = getNegativeSpellTargetMenu(self.widget, self.add_target, self.negative)
            else:
                self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
            self.add_target.trace('w', self.modifyTarget)
            self.widget.add(self.addTarget_wid)
        #-------------
        #name_wid.pack()
        return self.widget
    def getStars(self):
        return 0
    def modifyOwnManaCost(self,cardinhand,cost):
        return cost
    def effect(*args):
        pass
    def addTarget(*args):
        pass
    def getTarget(self,origin):
        if self.has_target:
            return self.target.getTarget(origin)
    def additionalBonus(self,creature) :
        pass
    
    def isAlwaysNegative(self):
        return (hasattr(self,"target") and self.target.defined_side and ((self.negative and self.target.defined_side == "you") or (self.positive and self.target.defined_side == "him")))

    def willAct(self,creature):   
        targets= self.target.getTarget(creature)
        for mons in targets  :
           if mons.max_pv >0 :
               for i in mons.bonus :
                   targets=i.modifySpellTarget(targets)
        for mons in targets  :
           if mons.max_pv >0 :
               for i in mons.bonus :
                   targets=i.modifySpellTarget(targets)
        return len(targets)!=0
    def getValue(self) :  # interret au combat
        if self.has_target :
            if self.positive and (self.target.side=="you" or self.target.side=="choose") :
                return 1.
            elif self.negative and (self.target.side=="him" or self.target.side=="choose") :
                return 1.
            elif self.negative and (self.target.side=="you") :
                return -1.
            elif self.positive and (self.target.side=="him") :
                return -1.
            else :
                return 0.2
        else :
            if hasattr(self,"negative") :
                return (not self.negative )*1.
            else :
                return 1.
        
     
class PasDEffet(Spell) :
    has_target = False
    def getCost(self) :
        return 0.

#class SpellWithoutLevel(Spell) :
#   hasLevel=False
#   hasTarget=False
#   def __init__(self,level=1) :    
#       self.level=level
#       self.parent=None
#   def getDescription(self) :
#       return re.sub(UP,' ',self.__class__.__name__)+' '+str(self.level)
#   def initWidget(self,master) :
#       self.widget=tkinter.PanedWindow(master,orient=HORIZONTAL)
#       self.content=tkinter.StringVar()
#       self.content.set(self.__class__.__name__)
#       self.content.trace("w", self.isChanged)
#       from CardPowers import list_spell,nbMultiplier
#       name_wid=OptionMenu(master,self.content,*list_spell)
#       name_wid["menu"].insert_separator(nbMultiplier)
#       #name_wid.pack()
#       self.widget.add(name_wid)
#       v=tkinter.StringVar()
#       v.set(str(self.level))
#       level_wid=tkinter.Spinbox(self.widget, from_=1, to=1000,textvariable=v,
#           command=1 )
#       level_wid.icursor(5)
#       self.widget.add(level_wid)
#       return self.widget  

class SpellWithLevel(Spell) :
    hasLevel=True
    def __init__(self,level=-1,target=-1) :
        if level==-1 :
            level=Level.NbFixe(1)
        if target==-1 :
            target=Target.UneCibleAuChoix()
        self.level=level
        self.parent=None
        #from Target import UneCibleAuChoix
        self.target = target

    def constructor(self) :
        #print "level is ",self.level
        return "CardPowers."+self.__class__.__name__+"("+self.level.constructor()+","+self.target.constructor()+")"

    def getSpellDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)+' '+self.level.getDescription("",s=False) +self.target.getDescription()
        
    def modifyLevelType(self,*args) :
            print ("modified level type",self.level.__class__.__name__)
            self.level=eval("Level."+self.add_level.get())()
            self.card.getCost()
            self.card.refreshWidget()
    
    def modifyLevel(self):
         print ("modified level to ",self.value.get())
         self.level.modifyLevel(self.value.get())
         self.card.getCost()
         self.card.refreshWidget()
            
    def initWidget(self,master, get_spell_menu=None, negative_target = False) :
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        if not(get_spell_menu):
            name_wid=getSpellMenu(master,self.content)
        else:
            name_wid=get_spell_menu(master,self.content)
        
        #name_wid.pack()
        self.widget.add(name_wid)
        
        self.add_level=tkinter.StringVar()
        self.add_level.set(self.level.__class__.__name__)
        self.level_wid=Level.getLevelMenu(self.widget, self.add_level)
        self.add_level.trace('w', self.modifyLevelType)
        self.widget.add(self.level_wid)
        
        self.value=tkinter.StringVar()
        self.value.set(str(self.level.level))
        value_wid=tkinter.Spinbox(self.widget, from_=1, to=1000,textvariable=self.value,
            command=self.modifyLevel )
        value_wid.icursor(5)
        self.widget.add(value_wid)
        
        
        if self.__class__.has_target:
            #Target selector
            if not(hasattr(self,"target")) and not(negative_target):
                self.target = Target.UneCibleAuChoix()
            elif not(hasattr(self,"target")) or negative_target and self.target.__class__ == Target.UneCibleAuChoix:
                self.target = [Target.MasseAllie,Target.MasseEnnemi][self.positive]()
            self.add_target = tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
            if negative_target:
                self.addTarget_wid = getNegativeSpellTargetMenu(self.widget, self.add_target, self.negative)
            else:
                self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
            self.add_target.trace('w', self.modifyTarget)
            self.widget.add(self.addTarget_wid)
            #ENd of target selector
        return self.widget
        

class SpellWithTwoLevels(SpellWithLevel) :
    hasLevel=True
    def __init__(self,level=-1,level2=-1,target=-1) :        
        if level==-1 :
            level=Level.NbFixe(1)
        if level2==-1 :
            level2=Level.NbFixe(1)
        if target==-1 :
            target=Target.UneCibleAuChoix()
        self.level=level
        self.level2 = level2
        self.target = target
        self.parent=None
        
    def constructor(self) :
        return ("CardPowers."+self.__class__.__name__+"("+self.level.constructor()+","+
               self.level2.constructor()+","+self.target.constructor()+")")
               
    def getSpellDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)+' '+self.level.getDescription("",s=False)+"/ "+self.level2.getDescription("",s=False)
        
    def modifyLevel2Type(self,*args) :
            print ("modified level type",self.level.__class__.__name__)
            self.level2=eval("Level."+self.add_level2.get())()
            self.card.getCost()
            self.card.refreshWidget()

    def modifyLevel2(self):
         print ("modified level to ",self.value2.get())
         self.level2.modifyLevel(self.value2.get())
         self.card.getCost()
         self.card.refreshWidget()

    def initWidget(self,master, get_spell_menu =None, negative_target=False) :
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        if not(get_spell_menu):
            name_wid=getSpellMenu(master,self.content)
        else:
            name_wid=get_spell_menu(master,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        
        self.add_level=tkinter.StringVar()
        self.add_level.set(self.level.__class__.__name__)
        self.level_wid=Level.getLevelMenu(self.widget, self.add_level)
        self.add_level.trace('w', self.modifyLevelType)
        self.widget.add(self.level_wid)
        
        self.value=tkinter.StringVar()
        self.value.set(str(self.level.level))
        value_wid=tkinter.Spinbox(self.widget, from_=0, to=100,textvariable=self.value,
            command=self.modifyLevel )
        value_wid.icursor(5)
        self.widget.add(value_wid)
        
        self.add_level2=tkinter.StringVar()
        self.add_level2.set(self.level.__class__.__name__)
        self.level_wid2=Level.getLevelMenu(self.widget, self.add_level2)
        self.add_level2.trace('w', self.modifyLevel2Type)
        self.widget.add(self.level_wid2)
        
        self.value2=tkinter.StringVar()
        self.value2.set(str(self.level2.level))
        value_wid=tkinter.Spinbox(self.widget, from_=0, to=100,textvariable=self.value2,
            command=self.modifyLevel2 )
        value_wid.icursor(5)
        self.widget.add(value_wid)      
        if self.__class__.has_target:
            #Target selector
            if not(hasattr(self,"target")) and not(negative_target):
                self.target = Target.UneCibleAuChoix()
            elif not(hasattr(self,"target")) or negative_target and self.target.__class__ == Target.UneCibleAuChoix:
                self.target = [Target.MasseAllie,Target.MasseEnnemi][self.positive]()

            self.add_target = tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
            if negative_target:
                self.addTarget_wid = getNegativeSpellTargetMenu(self.widget, self.add_target, self.negative)                
            else:
                self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
            self.add_target.trace('w', self.modifyTarget)
            self.widget.add(self.addTarget_wid)
        #-------------
        return self.widget

class spellContainer :
    def __init__(self,spell) :
        self.spell=spell

class Multiplier(Spell) :
    hasLevel=False
    isMultiplier=True
    has_target = False
    def __init__(self,spell1=None,spell2=None) :
        self.target = None
        if not spell1 :
            spell1=PasDEffet()    # question pour pro de python: trouver pourquoi pas directement dans la signature
        if not spell2:
            spell2=PasDEffet()
        self.parent=None
        self.spell1=spellContainer(spell1)
        self.spell2=spellContainer(spell2)
    def constructor(self) :
        return ("CardPowers."+self.__class__.__name__+"("+self.spell1.spell.constructor()+","
              +self.spell2.spell.constructor()+")")
    def initWidget(self,master):
        for s in [self.spell1,self.spell2] :
            s.spell.parent=s
            s.spell.card=self.card
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        spell_wid=tkinter.PanedWindow(self.widget,orient=tkinter.VERTICAL)
        spell1_wid=self.spell1.spell.initWidget(spell_wid)
        spell2_wid=self.spell2.spell.initWidget(spell_wid)
        spell_wid.add(spell1_wid)
        spell_wid.add(spell2_wid)       
        self.widget.add(spell_wid)
        return self.widget
    def getTarget(self,origin):
        return [origin]


class Invocation(SpellWithLevel) :
    isTrigger=True
    hasLevel=False
    has_target = False
    def __init__(self,level=None,monster=None) :
        if level==None:
            level = Level.NbFixe(1)
        if not monster :
            from Card import Card
            monster=Card('Mouton',1,1)
        self.monster=monster
        self.level = level
        self.parent=None
        self.has_target = False
        self.target = None
        
    def constructor(self) :
        return ("Spell."+self.__class__.__name__+"("+self.level.constructor()+
                ","+self.monster.constructor()+")")
                
    def initWidget(self,master) :
        self.monster.parent=self
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)

        self.add_level=tkinter.StringVar()
        self.add_level.set(self.level.__class__.__name__)
        self.level_wid=Level.getLevelMenu(self.widget, self.add_level)
        self.add_level.trace('w', self.modifyLevelType)
        self.widget.add(self.level_wid)
        
        self.value=tkinter.StringVar()
        self.value.set(str(self.level.level))
        value_wid=tkinter.Spinbox(self.widget, from_=1, to=1000,textvariable=self.value,
            command=self.modifyLevel )
        value_wid.icursor(5)
        self.widget.add(value_wid)

        spell_wid=self.monster.init_as_invocation(self.widget,spells = self.__class__.__name__ == "PlaceCarteDansMain")
        self.monster.card=self.card

        self.widget.add(spell_wid)
        return self.widget
        
    def getStars(self):
        return 1 + self.monster.getStars()

    def getCost(self):
        return self.monster.getCost()*self.level.getCostMultiplier(self) + (self.level.getCostMultiplier(self))*0.5
    
    def getDescription(self) :
        return self.__class__.__name__+' de ' + self.level.getDescription(self.monster.name,s=False)
    
    def getInlineDescription(self) :
        #return self.__class__.__name__+' de '+ self.level.getInlineDescription(self.monster.getDescription(),s=False)
        return self.__class__.__name__+' de '+ self.level.getInlineDescription(self.monster.getInlineDescription(),s=False)
    def getTarget(self,invocator):
        if hasattr(invocator,"is_invocation") and invocator.is_invocation :
            print( "Invocation does not invocate")
            return []
        else :
            #if not "simu" in invocator.player.name :
            #    print( "Invocation target is invocator")
            return [invocator.player]
    def effect(self,invocator,invocator2=None): # pour un sort on a self,origin,target
        #if not "simu" in invocator.player.name :
        #    print( "invocation effect for ",invocator.player.name)
        from Creature import Creature,AnimatedCreature
        self.monster.costint=int(self.monster.getCost())
        self.monster.starcost=self.monster.getStars()
        for i in range(self.level.getLevel(invocator)):
            if isinstance(invocator,AnimatedCreature) :
                #print "invocation level=",self.level," army len=",len(invocator.player.army)
                b=AnimatedCreature(invocator,self.monster,invocator.player)  #this makes invocator move
            else :
                b=Creature(self.monster,invocator.player,invocator)
            b.ready=False
            b.is_invocation=True
            #b.card.costint=b.costint
            #b.starcost=self.monster.getStars()


class PlaceCarteDansMain(Invocation):
    has_target = False
    def getDescription(self) :
        return "Place dans votre main \n"+self.level.getDescription("carte " + self.monster.name,False)

    def getInlineDescription(self) :
        return "Place dans votre main "+self.level.getInlineDescription("carte " + self.monster.getInlineDescription(),False)
    
    def getTarget(self,invocator):
        return [invocator.player]

    def effect(self,invocator,invocator2=None): # pour un sort on a self,origin,target
        self.monster.costint=int(self.monster.getCost())
        self.monster.starcost=self.monster.getStars()
        invocator.player.deck = [self.monster]*self.level.getLevel(invocator) + invocator.player.deck
        for i in range(self.level.getLevel(invocator)) :
          invocator.player.game.effect_list.append([3+i,invocator.player.id,"drawCard",[]])          #b.card.costint=b.costint
            #b.starcost=self.monster.getStars()   

    def getStars(self):
        self.monster.getCost()
        return 1+self.monster.getStars()

    def getCost(self):
        #print "PlaceCarteDansMain cost is : ",2.25*self.level.getCostMultiplier(self)-1.5
        return 2.25*self.level.getCostMultiplier(self)-1.5

class Transformation(Spell) :
    isTrigger=True
    hasLevel=False
    has_target = True
    positive = False
    def __init__(self,monster=None,target=Target.UneCibleAuChoix()) :
        if not monster :
            from Card import Card
            monster=Card('Mouton',1,1)
        self.monster=monster
        self.level = 1
        self.monster.parent=self
        self.parent=None
        self.target = target
    def constructor(self) :
        return ("Spell."+self.__class__.__name__+"("+self.monster.constructor()+","+
            self.target.constructor()+")")
    def initWidget(self,master) :
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        spell_wid=self.monster.init_as_invocation(self.widget)
        self.monster.card=self.card
        #Target selector
        if not(hasattr(self,"target")):
            self.target = Target.UneCibleAuChoix()        
        self.add_target = tkinter.StringVar(self.widget)
        self.add_target.set(self.target.__class__.__name__) # default value
        self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
        self.add_target.trace('w', self.modifyTarget)
        self.widget.add(self.addTarget_wid)
    #-------------
        self.widget.add(spell_wid)
        return self.widget
    def getStars(self):
        return self.monster.getStars()+1*(self.target.getCostMultiplier(self)>1.1)
    def getCost(self):
        return ( 2.3+max(
        self.monster.getCost()-2.4,
        max(3.5-self.monster.att/2.-self.monster.pv/2,self.monster.pv/2)+sum([abs(-0.4-p.interest)*p.getCost(self.monster) for p in self.monster.bonus])
        ,2.))*1.*max(1.,self.target.getCostMultiplier(self))
    def getDescription(self) :
        return self.__class__.__name__+' en '+ self.monster.getDescription()+' de '+self.target.getDescription()
    def getInlineDescription(self) :
        return self.__class__.__name__+' en '+ self.monster.getInlineDescription()+' de '+self.target.getInlineDescription()
    def effect(self,origin,target):
        print("transformation effect",target)
        if target.pv>0 :
            from copy import copy
            from Creature import AnimatedCreature,Creature
            from CardPowers import CriDeGuerre
            if isinstance(target,Creature) :
                #print "avant transfo card=",target.card.name
                target.is_dead=True # evite effet raleDAgonie
                target.die()
                for b in target.bonus : # il faut quand meme enlever les bonus
                    #print "removed ",b
                    b.removed()
                oldcard=target.card
                newmonster=copy(self.monster)
                newmonster.bonus=copy(self.monster.bonus)
                for b in reversed(newmonster.bonus) :
                    if isinstance(b,CriDeGuerre) :
                        newmonster.bonus.remove(b)
                newmonster.costint=int(newmonster.getCost())
                newmonster.starcost=newmonster.getStars()
                if isinstance(target,AnimatedCreature):
                    target=AnimatedCreature(target,newmonster,target.player)  #this makes invocator move
                    self.card=oldcard  # can only be done after creature appears so appearing must be instantaneous
                else :
                    target=Creature(newmonster,target.player,target)
                    target.card=oldcard
                #target.
            else :
                if not "simu" in origin.player.name :
                    print ("no effect on ",target)
             
class ConfereBonus(Spell) :
    hasLevel=False
    hasTarget=True
    def __init__(self,spell=None,target=Target.UneCibleAuChoix()) :
        from Bonus import PasDeBonus
        if not spell :
            spell=PasDeBonus()
        self.target = target
        self.spell=spell
        self.parent=None
    def constructor(self) :
        return ("Spell."+self.__class__.__name__+"("+self.spell.constructor()+","+
            self.target.constructor()+")")
    def getCost(self) :
        if self.spell.interest<0.6 :
            self.positive=False
            self.negative=True
        elif self.spell.interest>0.6 :
            self.positive=True
            self.negative=False
        else :
            self.positive=False;
            self.negative=False
        from Card import troll
        if self.spell.__class__.__name__=="NePeutPasAttaquer" or self.spell.__class__.__name__=="ALaPlaceDeLAttaque" :
            return max(4,self.spell.getCost(troll)*1.4)*self.target.getCostMultiplier(self)
        return (abs(self.spell.getCost(troll)-0.2)*1.2 + 0.8)*self.target.getCostMultiplier(self)
    def getSpellDescription(self):
        return "Donne "+self.spell.getDescription()
    def effect(self,origin,target):
        from Creature import Creature
        if isinstance(target,Creature) and target.pv>0 :
            from copy import copy
            b=copy(self.spell)
            b.owner=target
            target.bonus.append(b)
            target.starcost+=b.getStars()
            b.afterInvocation(target)
            target.addMark(self.spell.getInlineDescription(),typ="power",value=0) # value determine par interest du bonus
            target.starcost+=[-0.5,0][self.positive]
            target.setValue()
    def initWidget(self,master) :
        #from Bonus import getBonusMenu
        self.spell.parent=self
        self.spell.card=self.card
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        print("reed",self.spell)
        bonus_wid=self.spell.initWidget(self.widget,forother=True)
        self.widget.add(bonus_wid)
        if not(hasattr(self,"target")):
            self.target = Target.UneCibleAuChoix()        
        self.add_target = tkinter.StringVar(self.widget)
        self.add_target.set(self.target.__class__.__name__) # default value
        self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
        self.add_target.trace('w', self.modifyTarget)
        self.widget.add(self.addTarget_wid)

        return self.widget
    def getStars(self):
        return self.spell.getStars()*(1+(self.target.getCostMultiplier(self)>1))

class PlaceCarteDansPioche(PlaceCarteDansMain):
    has_target = False
    def getDescription(self) :
        return "Place dans votre pioche \n"+self.level.getDescription("carte " + self.monster.name,False)

    def getInlineDescription(self) :
        return "Place dans votre pioche "+self.level.getInlineDescription("carte " + self.monster.getInlineDescription(),False)
    
    def getTarget(self,invocator):
        return [invocator.player]

    def effect(self,invocator,invocator2=None): # pour un sort on a self,origin,target
        self.monster.costint=int(self.monster.getCost())
        self.monster.starcost=self.monster.getStars()
        for n in range(self.level.getLevel(invocator)):
            i = invocator.player.game.random(1,len(invocator.player.deck)+1)[0]
            invocator.player.deck = invocator.player.deck[0:i]+[self.monster]+invocator.player.deck[i:]
            #invocator.player.drawCard(self.level.getLevel(invocator))
                #b.card.costint=b.costint
                #b.starcost=self.monster.getStars()

    def getStars(self):
        self.monster.getCost()
        return [0,1][self.monster.getStars()>2]

    def getCost(self):
        #print "PlaceCarteDansMain cost is : ",2.25*self.level.getCostMultiplier(self)-1.5
        return 0.1+0.65*self.level.getCostMultiplier(self)*(self.monster.getStars()*1.2-2*(self.monster.getStars()>2))+0.1*self.level.getCostMultiplier(self)
    def initWidget(self,master) :
        self.monster.parent=self
        self.widget=tkinter.PanedWindow(master,orient=tkinter.HORIZONTAL)
        self.content=tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)

        self.add_level=tkinter.StringVar()
        self.add_level.set(self.level.__class__.__name__)
        self.level_wid=Level.getLevelMenu(self.widget, self.add_level)
        self.add_level.trace('w', self.modifyLevelType)
        self.widget.add(self.level_wid)
        
        self.value=tkinter.StringVar()
        self.value.set(str(self.level.level))
        value_wid=tkinter.Spinbox(self.widget, from_=1, to=1000,textvariable=self.value,
            command=self.modifyLevel )
        value_wid.icursor(5)
        self.widget.add(value_wid)

        spell_wid=self.monster.init_as_card(self.widget)
        self.monster.card=self.card

        self.widget.add(spell_wid)
        return self.widget

#possibleAsSpell=[PasDEffet]
#listMultiplier=[]
def getSpellMenu(master,variable) :
    import CardPowers
    #print dir(CardPowers)
    class_content=[p for p in dir(CardPowers) if hasattr(getattr(CardPowers,p),'getCost')]
    list_spells=[p for p in class_content if issubclass(getattr(CardPowers,p),Spell)
       and not getattr(CardPowers,p).isMultiplier ]
    nbPossibleSpells=len(list_spells)
    list_spells+=['Invocation']
    list_spells+=[p for p in class_content if issubclass(getattr(CardPowers,p),Spell)
       and getattr(CardPowers,p).isMultiplier ] # liste comme texte pour menus
    #print list_spells
    bm = tkinter.OptionMenu(master,variable,*list_spells)
    bm["menu"].insert_separator(nbPossibleSpells)
    bm["menu"].insert_separator(nbPossibleSpells+2)
    return bm

