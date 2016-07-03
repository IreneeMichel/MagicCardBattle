from Spell import Spell,PasDEffet,getSpellMenu
from Tkinter import *
import re
UP=re.compile('(?=[A-Z])')

class BonusMonstre :
    isTrigger=False
    hasTarget=False
    def __init__(self) :
        self.parent=None
    def afterInvocation(self,creature) :
        pass
    def additionalBonus(self,creature) :
        pass
    def otherDeath(self,creature) :
        pass
    def enemyDeath(self,creature):
        pass
    def beforeCombat(self,me,other) :  
        pass
    def afterCombat(self,me,other) :  
        pass
    def modifyDamage(self,attacker,damage,target) : 
        return damage
    #def damage(self,creature,damage) :   # effect of bonus if damage taken
    #    pass
    def death(self,creature) :   # effect of bonus if creature die
        pass
    def endturn(self,player):  # Effect at the end of the turn
        pass
    def modifyPlayerSuffer(self,player,damage):
        return damage
    def attackAnimationSprite(self,sprite) :
        return sprite
    def modifyAttackChoice(self,targets):
        return targets
    def modifyDefenseChoice(self,targets):
        return targets
    def modifyManaCost(self,card,cost):
        return cost
    def modifySpellTargetChoice(self,targets):
        return targets
    def spellLaunched(self,*args):
        pass
    def otherSpellLaunched(self,*args):
        pass
    def otherMonsterCreation(self,something):
        pass
    def getDescription(self):
        return re.sub(UP,' ',self.__class__.__name__)
    def getInlineDescription(self):
        return re.sub(UP,' ',self.__class__.__name__)
    def isChanged(self,*args) :
        print "bonus or trigger change"
        choice=self.content.get()
        exec('from cardPowers import '+ choice)
        new=eval(choice+'()')
        new.parent=self.parent
        new.card=self.card
        if self.parent :
            #parent.spell=new
            if type(self.parent)==type([]) :
                print "BonusMonstre changed in list"
                self.parent[self.parent.index(self)]=new
            else :
                print "BonusMonstre changed in widget"
                self.parent.spell=new
        else :
            print "BonusMonstre with no parent ?"
        self.card.refreshWidget()
    def initWidget(self,master) :
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        self.widget=getBonusMenu(master,self.content)
        #name_wid.pack()
        return self.widget
    def getStars(self):
        return 0
    def removed(self):
        pass   
    
class PasDeBonus(BonusMonstre) :
    def getCost(self,monster) :
        return 0.

class BonusMonstreWithLevel(BonusMonstre) :
    isTrigger=False
    def __init__(self,level=1) :
        self.level = level
        self.parent=None
    def getDescription(self) :
        return  re.sub(UP,' ',self.__class__.__name__)+' '+ str(self.level)
    def modifyLevel(self,*args) :
        print "modified level",self.level
        self.level=int(self.level_wid.get())
        self.card.getCost()
    def initWidget(self,master) :
        self.widget=PanedWindow(master,orient=HORIZONTAL)
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getBonusMenu(master,self.content)
        self.widget.add(name_wid)
        v=StringVar()
        v.set(str(self.level))
        self.level_wid=Spinbox(self.widget, from_=1, to=1000,textvariable=v,
            command=self.modifyLevel )
        self.level_wid.icursor(5)
        self.widget.add(self.level_wid)
        return self.widget
    def getStars(self):
        return 1

class BonusMonstreWithTwoLevels(BonusMonstre):
    isTrigger=False
    hasTarget=False
    def __init__(self,level=1,level2=1) :
        self.level = level
        self.level2 = level2
        self.parent=None
    def getDescription(self) :
        return  re.sub(UP,' ',self.__class__.__name__)+' '+ str(self.level)
    def modifyLevel(self,*args) :
        print "modified level",self.level
        self.level=int(self.level_wid.get())
        self.card.getCost()
    def modifyLevel2(self,*args) :
        print "modified level",self.level
        self.level2=int(self.level_wid2.get())
        self.card.getCost()
    def initWidget(self,master) :
        self.widget=PanedWindow(master,orient=HORIZONTAL)
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getBonusMenu(master,self.content)
        self.widget.add(name_wid)
        v=StringVar()
        a = StringVar()
        v.set(str(self.level))
        a.set(str(self.level2))
        self.level_wid=Spinbox(self.widget, from_=0, to=1000,textvariable=v,
            command=self.modifyLevel )
        self.level_wid2=Spinbox(self.widget, from_=0, to=1000,textvariable=a,
            command=self.modifyLevel2 )
        self.level_wid.icursor(5)
        self.level_wid2.icursor(5)
        self.widget.add(self.level_wid)
        self.widget.add(self.level_wid2)
        return self.widget
        
    def getStars(self):
        return 1

class BonusMonstreGivingBonus(BonusMonstre) :
    isTrigger=False
    hasLevel=False
    hasTarget=False
    def __init__(self,spell=PasDeBonus()) :
        self.spell=spell
        self.parent=None
        self.restriction=""
    def getDescription(self):
        return re.sub(UP,' ',self.__class__.__name__)+' :\n'+self.spell.getDescription()
    def restrictionChanged(self,*args) :
        self.restriction=self.restrict.get()
    def initWidget(self,master) :
        self.spell.parent=self
        self.spell.card=self.card
        self.widget=PanedWindow(master,orient=HORIZONTAL)
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getBonusMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        bonus_wid=self.spell.initWidget(self.widget)
        self.widget.add(bonus_wid)
        self.restrict=StringVar()
        self.restrict.set(self.restriction)
        self.restrict.trace("w", self.restrictionChanged)
        res_wid=Entry(self.widget,textvariable=self.restrict)
        self.widget.add(res_wid)
        return self.widget
    def getStars(self):
        return 3*self.spell.getStars()

class Trigger(BonusMonstre) :
    isTrigger=True
    def __init__(self,spell=PasDEffet()) :
        self.spell=spell
        self.parent=None
    def getDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)+' :\n'+self.spell.getDescription()
    def getInlineDescription(self) :
        return re.sub(UP,' ',self.__class__.__name__)+' :'+self.spell.getInlineDescription()
    def initWidget(self,master) :
        self.spell.card=self.card
        self.spell.parent=self
        self.widget=PanedWindow(master,orient=HORIZONTAL)
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        name_wid=getBonusMenu(self.widget,self.content)
        #name_wid.pack()
        self.widget.add(name_wid)
        spell_wid=self.spell.initWidget(self.widget)
        self.widget.add(spell_wid)
        return self.widget
    def getStars(self):
        return self.spell.getStars()

def getBonusMenu(master,variable) :
    import cardPowers
    #print dir(cardPowers)
    class_content=[p for p in dir(cardPowers) if  hasattr(getattr(cardPowers,p),'getCost')]
    list_bonus=[p for p in class_content if issubclass(getattr(cardPowers,p),BonusMonstre)
       and not getattr(cardPowers,p).isTrigger ]
    nbPossibleBonus=len(list_bonus)
    list_bonus+=[p for p in class_content if issubclass(getattr(cardPowers,p),BonusMonstre)
       and getattr(cardPowers,p).isTrigger ] # liste comme texte pour menus
    #print list_bonus
    bm = OptionMenu(master,variable,*list_bonus)
    bm["menu"].insert_separator(nbPossibleBonus)
    return bm

