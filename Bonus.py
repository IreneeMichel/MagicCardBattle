from Spell import Spell,PasDEffet,getSpellMenu
from tkinter import *
import re
import Level
UP=re.compile('(?=[A-Z])')

class BonusMonstre :
    isTrigger=False
    hasTarget=False
    is_cost_alterator = False
    def __init__(self) :
        self.parent=None
    def constructor(self) :
        return "CardPowers."+self.__class__.__name__+"()"
    def afterInvocation(self,creature) :
        pass
    def whenPlayed(self,creature) :
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
    def modifyOwnManaCost(self,cardinhand,cost):
        return cost
    def modifyTakenDamage(self,damage) : 
        return damage
    #def damage(self,creature,damage) :   # effect of bonus if damage taken
    #    pass
    def death(self,creature) :   # effect of bonus if creature die
        pass
    def endturn(self,monster):  # Effect at the end of the turn
        pass
    def beginTurn(self,monster):
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
    def modifySpellTarget(self,targets) :
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
        print ("bonus or trigger change")
        choice=self.content.get()
        exec('from CardPowers import '+ choice)
        new=eval(choice+'()')
        new.parent=self.parent
        new.card=self.card
        if self.parent :
            #parent.spell=new
            if type(self.parent)==type([]) :
                print ("BonusMonstre changed in list")
                self.parent[self.parent.index(self)]=new
            else :
                print ("BonusMonstre changed in widget")
                self.parent.spell=new
        else :
            print ("BonusMonstre with no parent ?")
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
    interest=0
    def getCost(self,monster) :
        return 0.

class BonusMonstreWithLevel(BonusMonstre) :
    isTrigger=False
    def __init__(self,level=1) :
        self.level = level
        self.parent=None
    def constructor(self) :
        return "CardPowers."+self.__class__.__name__+"("+str(self.level)+")"
    def getDescription(self) :
        return  re.sub(UP,' ',self.__class__.__name__)+' '+ str(self.level)
    def modifyLevel(self,*args) :
        print ("modified level",self.level)
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
    def constructor(self) :
        return "CardPowers."+self.__class__.__name__+"("+str(self.level)+","+str(self.level2)+")"
    def getDescription(self) :
        return  re.sub(UP,' ',self.__class__.__name__)+' '+ str(self.level)
    def modifyLevel(self,*args) :
        print ("modified level",self.level)
        self.level=int(self.level_wid.get())
        self.card.getCost()
    def modifyLevel2(self,*args) :
        print ("modified level",self.level)
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
        self.interest=self.spell.interest
    def constructor(self) :
        return "CardPowers."+self.__class__.__name__+"("+self.spell.constructor()+")"
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
    def __init__(self,spell=None) :
        if spell :
            self.spell=spell
        else :
            self.spell=PasDEffet()
        self.parent=None
        self.interest=self.spell.getValue() # init est rappele quand la carte ou creature est cree
    def constructor(self) :
        return "CardPowers."+self.__class__.__name__+"("+self.spell.constructor()+")"
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
    import CardPowers
    #print dir(CardPowers)
    class_content=[p for p in dir(CardPowers) if  hasattr(getattr(CardPowers,p),'getCost') and ('Effect' not in p)]
    list_bonus=[p for p in class_content if issubclass(getattr(CardPowers,p),BonusMonstre)
       and not getattr(CardPowers,p).isTrigger ]
    nbPossibleBonus=len(list_bonus)
    list_bonus+=[p for p in class_content if issubclass(getattr(CardPowers,p),BonusMonstre)
       and getattr(CardPowers,p).isTrigger ] # liste comme texte pour menus
    #print list_bonus
    bm = OptionMenu(master,variable,*list_bonus)
    bm["menu"].insert_separator(nbPossibleBonus)
    return bm

def getCostAlteratorMenu(master,variable) :
    import CardPowers
    #print dir(CardPowers)
    class_content=[p for p in dir(CardPowers) if  hasattr(getattr(CardPowers,p),'getCost') and ('Effect' not in p) and eval("CardPowers."+p).is_cost_alterator]
    bm = OptionMenu(master,variable,*class_content)
    return bm

class PlainteMaudite(Trigger) :
    def getCost(self,monster) :
        self.getStars()
        return 0.

    def getStars(self):
        if self.spell.getCost()+3*self.spell.getStars()>=5:
            if self.spell.hasLevel :
                if self.spell.level.level>=1 :
                    self.spell.level.level-=1
                    if self.spell.getCost()+3*self.spell.getStars()<5:
                        self.spell.level.level+=1
                else :
                    if hasattr(self.spell,"level2") :
                        self.spell.level2.level-=1
                        if self.spell.getCost()+3*self.spell.getStars()<5:
                            self.spell.level2.level+=1                    
            return -2
        elif self.spell.getCost()+3*self.spell.getStars()>=2:
            return -1
        else:
            return 0

    def whenPlayed(self,creature):
        if self.spell.willAct(creature):
            creature.player.launch(creature,self.spell)
        else:
            creature.is_dead=True # pour annuler rale d agonie
            creature.die()
            for b in creature.bonus : # il faut quand meme enlever les bonus
                    #print "removed ",b
                    b.removed()
        if self in creature.bonus :
            creature.bonus.remove(self) # ameliore l evaluation par l ordi de la valeur de la creature
        creature.starcost -= self.getStars()
        #4print "\ncreature.starcost",creature.name,creature.starcost
    
    
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
        spell_wid=self.spell.initWidget(self.widget,get_spell_menu =  getNegativeSpellMenu, negative_target = True)
        self.widget.add(spell_wid)
        return self.widget

def getNegativeSpellMenu(master,variable) :
    from tkinter import OptionMenu
    #print dir(CardPowers)
       
    list_spells = ['Assassinat','Degat','Bonus','BouclierDivin','Guerison','DegatSurSonHeros',
    'GuerisonTotale','ReduitUnServiteurA1Vie','ReduitUnServiteurA1Att',"DefausserSoi"]
    
    
    bm = OptionMenu(master,variable,*list_spells)
    return bm

  
    
class CoutReduit(BonusMonstre) :
    interest=0    
    is_cost_alterator = True
    def getCost(self,monster) :
        if monster.pv > 0:
            co=[m.getCost(monster)+(m.getStars()>0)*1.2 for m in monster.bonus if not m.is_cost_alterator]
            co=co+[monster.att*0.5,monster.pv*0.5]
            co.sort(reverse=True)
            co=[c*(0.16+i*0.05) for i,c in enumerate(co) if c>0]
        else:
            co = [0.15 * sum([b.getCost() for b in monster.bonus if not b.is_cost_alterator])]
        return -sum(co)-0.3

    def initWidget(self,master) :
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        self.widget=getCostAlteratorMenu(master,self.content)
        #name_wid.pack()
        return self.widget

    def getStars(self):
        return 1
    def getDescription(self):
        return "cout reduit"
    def whenPlayed(self,monster) :    # ameliore l evaluation par l ordi de la valeur de la creature
        monster.bonus.remove(self)
        monster.starcost-=1  

class CoutReduitParSituation(CoutReduit, BonusMonstreWithLevel) :
    interest=0    
    is_cost_alterator = True
    def __init__(self,level=Level.NbFixe(1)) :
        self.level = level
        self.parent=None
    def getValue(self):
        return 1
    def getCost(self,monster) :
        return self.level.getCostMultiplier(self)
    def modifyOwnManaCost(self,cardinhand,cost):
        return cost - self.level.getLevel(cardinhand)
    def getStars(self):
        return 0

    def constructor(self) :
        #print "level is ",self.level
        return "CardPowers."+self.__class__.__name__+"("+self.level.constructor()+")"

    def getDescription(self) :
        return "Cout Reduit de "+self.level.getDescription("",s=False)
        
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
            
    def initWidget(self,master) :
        self.widget=PanedWindow(master,orient=HORIZONTAL)
        self.content=StringVar()
        self.content.set(self.__class__.__name__)
        self.content.trace("w", self.isChanged)
        
        name_wid=getCostAlteratorMenu(master,self.content)
        
        #name_wid.pack()
        self.widget.add(name_wid)
        
        self.add_level=StringVar()
        self.add_level.set(self.level.__class__.__name__)
        self.level_wid=Level.getLevelMenu(self.widget, self.add_level)
        self.add_level.trace('w', self.modifyLevelType)
        self.widget.add(self.level_wid)
        
        self.value=StringVar()
        self.value.set(str(self.level.level))
        value_wid=Spinbox(self.widget, from_=1, to=1000,textvariable=self.value,
            command=self.modifyLevel )
        value_wid.icursor(5)
        self.widget.add(value_wid)
        
        return self.widget
