import Tkinter
import re
from Target import getTargetMenu
import Target
UP=re.compile('(?=[A-Z])')


class Spell :
    hasLevel=False
    has_target=True
    positive = False
    isMultiplier=False
    target_locked=False
    def __init__(self) :
        self.parent=None
        self.target = Target.UneCibleAuChoix()
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
            print "modified target",self.target.__class__.__name__
            self.target=eval("Target."+self.add_target.get())()
            self.card.getCost()
            self.card.refreshWidget()
    def isChanged(self,*args) :
        choice=self.content.get()
        exec('from cardPowers import '+ choice)
        new=eval(choice+'()')
        if self.parent :
            if type(self.parent)==type([]) :
                print "Spell changed in list"
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
    def initWidget(self,master):
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        self.spell_list=getSpellMenu(master,self.content)
        self.widget.add(self.spell_list)
        #Target selector
        if self.__class__.has_target:        
            if not(hasattr(self,"target")):
                self.target = Target.UneCibleAuChoix()        
            self.add_target = Tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
            self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
            self.add_target.trace('w', self.modifyTarget)
            self.widget.add(self.addTarget_wid)
        #-------------
        #name_wid.pack()
        return self.widget
    def getStars(self):
        return 0
    def effect(*args):
        pass
    def addTarget(*args):
        pass
    def getTarget(self,origin):
        if self.has_target:
            return self.target.getTarget(origin)
    def modifySpellTargetChoice(self,targets) :
        return targets
    def additionalBonus(self,creature) :
        pass
        
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
#       self.widget=Tkinter.PanedWindow(master,orient=HORIZONTAL)
#       self.content=Tkinter.StringVar()
#       self.content.set(self.__class__.__name__)
#       self.content.trace("w", self.isChanged)
#       from cardPowers import list_spell,nbMultiplier
#       name_wid=OptionMenu(master,self.content,*list_spell)
#       name_wid["menu"].insert_separator(nbMultiplier)
#       #name_wid.pack()
#       self.widget.add(name_wid)
#       v=Tkinter.StringVar()
#       v.set(str(self.level))
#       level_wid=Tkinter.Spinbox(self.widget, from_=1, to=1000,textvariable=v,
#           command=1 )
#       level_wid.icursor(5)
#       self.widget.add(level_wid)
#       return self.widget  

class SpellWithLevel(Spell) :
    hasLevel=True
    def __init__(self,level=1) :        
        self.level=level
        self.parent=None
        #from Target import UneCibleAuChoix
        self.target = Target.UneCibleAuChoix()
    def getSpellDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)+' '+str(self.level)   
    def modifyLevel(self,*args) :
        print "modified level",self.level
        self.level=int(self.value.get())
        self.card.getCost()
    def initWidget(self,master) :
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(master,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        self.value=Tkinter.StringVar()
        self.value.set(str(self.level))
        level_wid=Tkinter.Spinbox(self.widget, from_=1, to=1000,textvariable=self.value,
            command=self.modifyLevel )
        level_wid.icursor(5)
        self.widget.add(level_wid)
        
        if self.__class__.has_target:
            #Target selector
            if not(hasattr(self,"target")):
                self.target = Target.UneCibleAuChoix()        
            self.add_target = Tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
            self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
            self.add_target.trace('w', self.modifyTarget)
            self.widget.add(self.addTarget_wid)
            #ENd of target selector
        return self.widget
        

class SpellWithTwoLevels(Spell) :
    hasLevel=True
    def __init__(self,level=1,level2=1) :        
        self.level=level
        self.level2 = level2
        self.target = Target.UneCibleAuChoix()
        self.parent=None
    def getSpellDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)+' '+str(self.level)+"/"+str(self.level2)
    def modifyLevel(self,*args) :
        print "modified level",self.level
        self.level=int(self.value.get())
        self.card.getCost()
    def modifyLevel2(self,*args) :
        print "modified level",self.level
        self.level2=int(self.value2.get())
        self.card.getCost()
    def initWidget(self,master) :
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(master,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        self.value=Tkinter.StringVar()
        self.value.set(str(self.level))
        self.value2=Tkinter.StringVar()
        self.value2.set(str(self.level2))
        level_wid=Tkinter.Spinbox(self.widget, from_=0, to=1000,textvariable=self.value,
            command=self.modifyLevel )
        level_wid2=Tkinter.Spinbox(self.widget, from_=0, to=1000,textvariable=self.value2,
            command=self.modifyLevel2 )
        level_wid.icursor(5)
        level_wid2.icursor(5)
        self.widget.add(level_wid)
        self.widget.add(level_wid2)        
        if self.__class__.has_target:
            #Target selector
            if not(hasattr(self,"target")):
                self.target = Target.UneCibleAuChoix()        
            self.add_target = Tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
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
    def initWidget(self,master):
        for s in [self.spell1,self.spell2] :
            s.spell.parent=s
            s.spell.card=self.card
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        spell_wid=Tkinter.PanedWindow(self.widget,orient=Tkinter.VERTICAL)
        spell1_wid=self.spell1.spell.initWidget(spell_wid)
        spell2_wid=self.spell2.spell.initWidget(spell_wid)
        spell_wid.add(spell1_wid)
        spell_wid.add(spell2_wid)       
        self.widget.add(spell_wid)
        return self.widget
    def getStars(self):
        return self.spell1.spell.getStars()+self.spell2.spell.getStars()
    def getTarget(self,origin):
        return [origin]


class Invocation(Spell) :
    isTrigger=True
    hasLevel=False
    def __init__(self,monster=None) :
        if not monster :
            from Card import troll
            monster=troll
        self.monster=monster
        self.level = 1
        self.parent=None
        self.has_target = False
        self.target = None
    def initWidget(self,master) :
        self.monster.parent=self
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        self.value=Tkinter.StringVar()
        self.value.set(str(self.level))
        spell_wid=self.monster.init_as_invocation(self.widget)
        self.monster.card=self.card
        number_wid = Tkinter.Spinbox(self.widget, from_=1, to=20, textvariable=self.value,command= self.modifyLevel)        
        number_wid.icursor(5)
        self.widget.add(number_wid)
        self.widget.add(spell_wid)
        return self.widget
    def modifyLevel(self,*args) :
        print "modified number",self.level
        self.level=int(self.value.get())
        self.card.getCost()
    def getStars(self):
        return 1 + self.monster.getStars()
    def getCost(self):
        return self.monster.getCost()*self.level + (self.level-1)*0.5
    def getDescription(self) :
        return self.__class__.__name__+' de '+ str(self.level) +" " + self.monster.getDescription()
    def getInlineDescription(self) :
        return self.__class__.__name__+' de '+ str(self.level) +" " + self.monster.getInlineDescription()
    def getTarget(self,invocator):
        if hasattr(invocator,"is_invocation") and invocator.is_invocation :
            #print "Invocation does not invocate"
            return []
        else :
            return [invocator]
    def effect(self,invocator,invocator2=None): # pour un sort on a self,origin,target
        from Creature import Creature,AnimatedCreature
        self.monster.costint=int(self.monster.getCost())
        self.monster.starcost=self.monster.getStars()
        for i in range(self.level):
            if isinstance(invocator,AnimatedCreature) :
                #print "invocation level=",self.level," army len=",len(invocator.player.army)
                b=AnimatedCreature(invocator,self.monster,invocator.player,simultaneous=self.level)  #this makes invocator move
            else :
                b=Creature(invocator,self.monster,invocator.player)
            b.is_invocation=True
            #b.card.costint=b.costint
            #b.starcost=self.monster.getStars()
"""
class InvocationAleatoireDUnType(Spell) :
    isTrigger=True
    hasLevel=False
    has_target = False
    def __init__(self,race=None) :
        if not race:
            race = "human"
        self.race=race
        self.level = 1
        self.parent=None
    def initWidget(self,master) :
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        self.value=Tkinter.StringVar()
        self.value.set(str(self.level))
        self.content= Tkinter.StringVar()
        self.content.set(self.race)
        self.content.trace("w", self.changeType)        
        spell_wid= Tkinter.OptionMenu(self.widget,self.content,*self.allChoices())
        number_wid = Tkinter.Spinbox(self.widget, from_=1, to=20, textvariable=self.value,command= self.modifyLevel)        
        number_wid.icursor(5)
        self.widget.add(number_wid)
        self.widget.add(spell_wid)
        return self.widget
    def allChoices(self):
        import glob
        choices = [c[:c.index("_monsters.sav")] for c in glob.glob("*_monsters.sav")]
        print "Possible choices for type: ",choices
        choices.remove("unknown")
        return choices
    def modifyLevel(self,*args) :
        print "modified number",self.level
        self.level=int(self.value.get())
        self.card.getCost()
    def getStars(self):
        return 1# + self.monster.getStars()
    def getCost(self):
        return 4*self.level + (self.level-1)*0.5
    def getDescription(self) :
        return 'Invocation de '+ str(self.level) +"\n \"" + self.race + "\" aleatoir"
    def getInlineDescription(self) :
        return 'Invocation de '+ str(self.level) +" \"" + self.race + "\" aleatoir"
    def getTarget(self,invocator):
        return [invocator]
    def changeType(self,*args):
        self.race = self.content.get()
        print "New type for the invocation : ",self.race
    def effect(self,invocator,i2):
        import pickle
        with open(self.race+"_monsters.sav","rb") as file:
            possible_monsters = pickle.load(file).values()
            import random
            monster = random.choice(possible_monsters)
            monster.costint=int(monster.getCost())
            monster.starcost=monster.getStars()
            from Creature import Creature,AnimatedCreature
            for i in range(self.level):
                if isinstance(invocator,AnimatedCreature) :
                    b=AnimatedCreature(invocator,monster,invocator.player,simultaneous=self.level)  #this makes invocator move
                    print "invocation est passe"
                else :
                    b=Creature(invocator,monster,invocator.player)
                #b.costint=int(monster.getCost())
                #b.starcost=monster.getStars()
                b.is_invocation=True
"""
class Transformation(Spell) :
    isTrigger=True
    hasLevel=False
    has_target = True
    positive = False
    def __init__(self,monster=None) :
        if not monster :
            from Card import mouton
            monster=mouton
        self.monster=monster
        self.level = 1
        self.monster.parent=self
        self.parent=None
        self.target = Target.UneCibleAuChoix()
    def initWidget(self,master) :
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        spell_wid=self.monster.init_as_invocation(self.widget)
        self.monster.card=self.card
        if self.__class__.has_target:
            #Target selector
            if not(hasattr(self,"target")):
                self.target = Target.UneCibleAuChoix()        
            self.add_target = Tkinter.StringVar(self.widget)
            self.add_target.set(self.target.__class__.__name__) # default value
            self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
            self.add_target.trace('w', self.modifyTarget)
            self.widget.add(self.addTarget_wid)
        #-------------
        self.widget.add(spell_wid)
        return self.widget
    def getStars(self):
        return self.monster.getStars()
    def getCost(self):
        return 1.7+max(self.monster.getCost()-2,4-self.monster.getCost(),1.5)*1.2*max(1.,self.target.getCostMultiplier(self))
    def getDescription(self) :
        return self.__class__.__name__+' en '+ self.monster.getDescription()+' de '+self.target.getDescription()
    def getInlineDescription(self) :
        return self.__class__.__name__+' de '+ str(self.level) +" " + self.monster.getInlineDescription()
    def effect(self,origin,target):
        if target.pv>0 :
            from copy import copy
            from Creature import AnimatedCreature,Creature
            from cardPowers import CriDeGuerre
            if isinstance(target,Creature) :
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
                    target=AnimatedCreature(target,newmonster,target.player,simultaneous=1)  #this makes invocator move
                else :
                    target=Creature(target,newmonster,target.player)
                target.card=oldcard
                #target.
            else :
                if not "simu" in origin.player.name :
                    print "no effect on ",target
             
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
        self.positive=True
    def getCost(self) :
        from Card import troll
        if self.spell.getCost(troll)<0. :
            self.positive=False
        else :
            self.positive=True
        return (abs(self.spell.getCost(troll)-0.2)*1.3 + 1.1)*self.target.getCostMultiplier(self)
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
            target.addMark(self.spell.getInlineDescription(),typ="power",value=[-1,1][self.positive])
            target.starcost+=[-0.5,0][self.positive]
    def initWidget(self,master) :
        #from Bonus import getBonusMenu
        self.spell.parent=self
        self.spell.card=self.card
        self.widget=Tkinter.PanedWindow(master,orient=Tkinter.HORIZONTAL)
        self.content=Tkinter.StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getSpellMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        bonus_wid=self.spell.initWidget(self.widget)
        self.widget.add(bonus_wid)
        if not(hasattr(self,"target")):
            self.target = Target.UneCibleAuChoix()        
        self.add_target = Tkinter.StringVar(self.widget)
        self.add_target.set(self.target.__class__.__name__) # default value
        self.addTarget_wid = getTargetMenu(self.widget, self.add_target)
        self.add_target.trace('w', self.modifyTarget)
        self.widget.add(self.addTarget_wid)

        return self.widget
    def getStars(self):
        return self.spell.getStars()*(1+(self.target.getCostMultiplier(self)>1))

#possibleAsSpell=[PasDEffet]
#listMultiplier=[]
def getSpellMenu(master,variable) :
    import cardPowers
    #print dir(cardPowers)
    class_content=[p for p in dir(cardPowers) if hasattr(getattr(cardPowers,p),'getCost')]
    list_spells=[p for p in class_content if issubclass(getattr(cardPowers,p),Spell)
       and not getattr(cardPowers,p).isMultiplier ]
    nbPossibleSpells=len(list_spells)
    list_spells+=['Invocation']
    list_spells+=[p for p in class_content if issubclass(getattr(cardPowers,p),Spell)
       and getattr(cardPowers,p).isMultiplier ] # liste comme texte pour menus
    #print list_spells
    bm = Tkinter.OptionMenu(master,variable,*list_spells)
    bm["menu"].insert_separator(nbPossibleSpells)
    bm["menu"].insert_separator(nbPossibleSpells+2)    
    return bm

