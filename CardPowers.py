
import Spell
from Spell import Multiplier,SpellWithLevel,Invocation,SpellWithTwoLevels,Transformation,ConfereCapacite,PlaceCarteDansMain,PasDEffet, PlaceCarteDansPioche
from Bonus import BonusMonstre,BonusMonstreWithLevel,BonusMonstreWithTwoLevels,CoutReduit
from Bonus import Trigger,BonusMonstreGivingBonus,PlainteMaudite
from Sprites import Sprite
import Target
from Creature import Creature,AnimatedCreature
from copy import copy
from types import FunctionType,MethodType
from functools import partial

import re

printed_lines = ["None"]
def fprint(*args):
    printed_lines[0] = " ".join([str(a) for a in args])

PasDEffet=PasDEffet
Invocation=Invocation

class CoutSpecial :
    pass
"""
class InvocationAleatoireDUnType(InvocationAleatoireDUnType):
    pass
"""
Transformation=Transformation
PlaceCarteDansMain=PlaceCarteDansMain
PlaceCarteDansPioche=PlaceCarteDansPioche
PlainteMaudite=PlainteMaudite
ConfereCapacite=ConfereCapacite
CoutReduit=CoutReduit


#class CoutReduitParSituation(CoutReduitParSituation):
#    pass

class CoutReduitGraduel(BonusMonstreWithLevel) :
    interest=0    
    is_cost_alterator = True   
#    def constructor(self) :
#        #print "level is ",self.level
#        return "cardPowers."+self.__class__.__name__+"("+str(self.level)+")"
    def getCost(self,monster) :
        return self.level * (-2.0)
    def getStars(self):
        return self.level

    def whenPlayed(self,monster) : # ameliore l evaluation par l ordi de la valeur de la creature
        monster.bonus.remove(self)
        monster.starcost-=self.level

class Incarnation(BonusMonstre):
    interest=-1
    def death(self,monster):
        self.owner.player.pv = 0
        self.owner.player.sufferDamage(0)
        
    def removed(self):
        pass
    def afterInvocation(self,monster):
        for m in monster.player.army :
            if m is monster :
                continue
            if any([(b.__class__.__name__=="Incarnation") for b in m.bonus]) :
                for b in m.bonus :
                    if b.__class__.__name__=="Incarnation" :
                        m.bonus.remove(b)
                        m.die()
        monster.player.game.effect_list.append([13,monster.player.id,"endTurn",[]])
    def getDescription(self):
        return "Incarnation"
    
    def getInlineDescription(self):
        return "Incarnation"
    
    def getStars(self):
        return -2  
    def getCost(self,monster):
        return -0.2-monster.pv*0.3-monster.att*0.15

class EssentielEffect(Incarnation) :
    def death(self,monster):
        self.owner.game.player1.pv = 0
        self.owner.game.player1.sufferDamage(0)

class AuChoix(Multiplier) :
    # les spell n ont pas de owner, sinon cela pose pb dans les creaturecopy
    def getCost(self) :
        from collections import Counter
        lesmots=Counter(re.compile("CardPowers[.][a-zA-Z]+").findall(self.constructor()))
        add=sum([i*(i-1)/2. for i in lesmots.values()])
        return add*0.06+0.25+max(self.spell1.spell.getCost(),self.spell2.spell.getCost())+min(self.spell1.spell.getCost(),self.spell2.spell.getCost())*0.2
    
    def getStars(self):
        return max([self.spell1.spell.getStars(),self.spell2.spell.getStars()])    

    def getValue(self) :
        return max(self.spell1.spell.getValue(),self.spell1.spell.getValue())

    def getDescription(self) :
        return 'Choix :\n '+ self.spell1.spell.getDescription()+ "\n ou \n" + self.spell2.spell.getDescription()

    def effect(self,origin,target):
        #print("au choix : effect de auchoix sur ",target.name)
#        if hasattr(origin.player,"nv") :
#            print " "*4*(2-origin.player.nv)+"au choix : effect from",origin.name,origin.id," sur ",target.name,target.id
        if target.name=="choix1" or target.name=="choix2" :
            limo=[m for m in origin.player.army if m.name=="choix1" or m.name=="choix2" ]
            for m in limo :
                if origin.player.verbose >2 and hasattr(origin.player,"nv") : print( "+"*4*(2-origin.player.nv),m.name,m.id,"de",m.player.name," doit mourrir ")
                #origin.game.effect_list.append([1,m.id,"die",[]]) # n enleve pas de limo donc pas de reversed necessaire
                m.die()
            if target.name=="choix1":
            # print "choix 1:",self.spell1.spell
                if origin in origin.player.army :
                    origin.player.launch(origin,self.spell1.spell)
                else :
                    origin.player.launch(target,self.spell1.spell)
            else  :
            #print "choix 2:",self.spell2.spell
                if origin in origin.player.army :
                    origin.player.launch(origin,self.spell2.spell)
                else :
                    origin.player.launch(target,self.spell2.spell)
        else :
            print( "erreur dans auchoix :",target.name," is not choix1 or choix2")
            raise "erreur dans au choix"

            #self.choix1.kill()
            #self.choix2.kill()
        #→print("fin au choix : effect ")
        #self.spell2.spell.effect(target)
    def getTarget(self,origin):
        #if hasattr(origin.player,"nv") :print " "*4*(2-origin.player.nv)+"au choix : getTarget from",origin.name,origin.id," de ",origin.player.name,origin.player
#        if not origin.player is origin.game.player :
#            print( "pas de choix au tour adverse")
#            print("origin", origin.name,origin.id)
#            print("de", origin.player,"!=",origin.game.player)
#            print( origin.player.id,"!=",origin.game.player.id)
#            return None
        if not any([m.name=="choix1" or m.name=="choix2" for m in origin.player.army]) :
            #print "creation du choix , nest pas dans",[m.name for m in origin.player.army],'de',origin.player
            import pygame
            from Card import Card
            from Player import Computer0
            card1=Card("choix1",2,1) # faire des cartes avec un nom, seule solution pour retenir quel choix fait quoi
            # la variable interne serait copiee lors des simulations donc marche pas
            card2=Card("choix2",1,1)
            card1.starcost=0
            card2.starcost=0
            card1.costint=1
            card2.costint=1
            if isinstance(origin,AnimatedCreature) :
                card1.image=copy(origin.card.image)
                card2.image=copy(origin.card.image)
                font = pygame.font.SysFont("Calibri Bold",54)
                text = font.render(self.spell1.spell.getDescription(),False,(0,0,0))
                pygame.draw.rect(card1.image,(220,200,5), (20,300,338,235))
                card1.image.blit(text,(15,400))
                card1.image.set_alpha(255)
                # il faut que les cartes soient dans l armee avant la suite pour le computer
                b2=AnimatedCreature(origin,card1,origin.player)
                b2.is_invocation=True
                b2.max_pv=0
                text = font.render(self.spell2.spell.getDescription(),False,(0,0,0))
                pygame.draw.rect(card2.image,(220,200,5), (20,300,338,240))
                card2.image.blit(text,(15,400))
                card2.image.set_alpha(255)
                b=AnimatedCreature(origin,card2,origin.player)
                b.is_invocation=True
                b.max_pv=0
                #origin.player.orderArmy()
                b.index=len(origin.player.army)/2.+0.8
                b2.index=len(origin.player.army)/2.-1.6
                b.takePlace()
                b2.takePlace()
#                origin.game.effect_list.append([1,b.id,"takePlace",[]])     # apres animation          
#                origin.game.effect_list.append([1,b2.id,"takePlace",[]])               
            else :
                #print "in gettarget : not animated"
                b=Creature(card1,origin.player,origin)
                b.max_pv=0
                b.is_invocation=True
                b=Creature(card2,origin.player,origin)
                b.max_pv=0
                b.is_invocation=True
            return "choose"
        else :
            return "choose"
#            # mieux vaut attendre
#            print "attente pour au choix"
#            origin.game.effect_list.append([1,origin.player.id,"launch",[origin.id,self]])
#            return None

    def getInlineDescription(self):
        return "choix de sort"

class DeuxEffets(Multiplier):
    def getCost(self) :
        from collections import Counter
        lesmots=Counter(re.compile("CardPowers[.][a-zA-Z]+").findall(self.constructor()))
        add=sum([i*(i-1)/2. for i in lesmots.values()])
        return 0.05*add+0.2+abs(self.spell1.spell.getCost()+self.spell2.spell.getCost())
    def getStars(self):
#        if "DegatSurSonHeros" in self.spell1.spell.constructor() and "DegatSurSonHeros" in self.spell2.spell.constructor() :
#            return self.spell1.spell.getStars()+self.spell2.spell.getStars()+1
        return max(0,self.spell1.spell.getStars())+max(0,self.spell2.spell.getStars())
    def getValue(self) :
        return (self.spell1.spell.getValue()+self.spell2.spell.getValue())/2.
    def getDescription(self) :
        return self.spell1.spell.getDescription()+ "\n et " + self.spell2.spell.getDescription()
    def effect(self,origin,target):
        #print "deux effect : effect"
        pass
        #self.spell2.spell.effect(target)
    def getTarget(self,origin):
        #print "deux effect : getTarget from",origin.name," de ",origin.player.name
        #if not "-simu" in origin.player.name :
        #    print "deux effect : premier effet",self.spell1.spell.__class__.__name__," deuxieme",self.spell2.spell.__class__.__name__
        origin.player.game.effect_list.append([1,origin.player.id,"launch",[origin.id,self.spell2.spell]])        
        origin.player.launch(origin,self.spell1.spell)
        #print "deuxieme",self.spell2.spell
        #origin.player.launch(origin,self.spell2.spell)
        #return self.spell2.spell.getTarget(origin)
        return None
    def getInlineDescription(self):
        return self.spell1.spell.getInlineDescription()+' et '+self.spell1.spell.getInlineDescription()
"""

class DeuxEffetsMemeCible(DeuxEffets):
    pass
"""

""" Bonus permanents ------------------------------------"""
class Provocation(BonusMonstre) :
    interest=1
    def getCost(self,monster) :
        return 0.35+monster.att*0.08+monster.pv*0.08       
    def afterInvocation(self,monster) :
        monster.addMark("provocation",pos="center",size=(150,220),typ="external")
    def modifyDefenseChoice(self,targets) :
        if not any([(b.__class__.__name__=="Insaisissable") for b in self.owner.bonus]) :
            return [t for t in targets if any([(b.__class__.__name__=="Provocation") for b in t.bonus])]
        else :
            return targets
    def removed(self) :
        #print "tite verif ", creature," should be ",self.owner
        self.owner.removeMark("provocation")

class Determine(BonusMonstre) :
    interest=1
    def getCost(self,monster) :
        cost= 0.2+max(1.,monster.att)*0.45
        return cost
            
    def getStars(self):
        return 1    
    def modifyAttackChoice(self,targets) :
        t=[]
        for c in self.owner.player.army :
            if c.pv>0 :
                t.append(c)
        t.append(self.owner.player.adv)
        for c in self.owner.player.adv.army :
            if c.pv>0 and not any([(b.__class__.__name__=="Insaisissable") for b in self.owner.bonus]):
                t.append(c)
        return t

class Inciblable(BonusMonstre) :
    interest=1
    def getCost(self,monster) :
        return 0.3+monster.att/7.+monster.pv*0.1
    def getStars(self):
        return 1
    def modifySpellTargetChoice(self,targets) :
        if self.owner in targets and not any([(b.__class__.__name__=="Insaisissable") for b in self.owner.bonus]) :
            #print len(targets),
            targets.remove(self.owner)
            #print self.owner.name," de ",self.owner.player.name, " is removed from targets",len(targets),[i.name for i in targets]
        return targets

class InsensibleALaMagie(BonusMonstre) :
    interest=1
    def getCost(self,monster) :
        return 0.6+monster.att/4.+monster.pv*0.2
    def getStars(self):
        return 1
    def modifySpellTarget(self,targets) :
        if self.owner in targets and not any([(b.__class__.__name__=="Insaisissable") for b in self.owner.bonus]) :
            targets.remove(self.owner)
            if "imu" not in self.owner.player.name : print (self.owner.name,"self is removed from targets")
        else :
            if "imu" not in self.owner.player.name : print (self.owner.name,"InsensibleALaMagie but does not modify targets")
        return targets
    def modifySpellTargetChoice(self,targets) :
        if self.owner in targets and not any([(b.__class__.__name__=="Insaisissable") for b in self.owner.bonus]) and len(targets)>1 :
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets
    
class AbsorbeurDeMagie(BonusMonstre) :
    interest=1    
    def getCost(self,monster) :
        if  any([(b.__class__.__name__=="InsensibleALaMagie") for b in monster.bonus]) :
            #print len(targets),
            return 2.1+monster.att/7.+monster.pv/7.
        return 1.2
    def getStars(self):
        return 0
    def modifySpellTarget(self,targets) :
        fprint("AbsorbeurDeMagie modifySpellTarget")
        lita=[m for m in targets]
        for m in lita :
            if m.name!="choix1" and m.name!="choix2" and not any([(b.__class__.__name__=="AbsorbeurDeMagie") for b in m.bonus]) :
                targets.remove(m)
        #print "AbsorbeurDeMagie:nb affected targets",len(targets),(targets[0] is self.owner)
        return targets
    def modifySpellTargetChoice(self,targets) :
        fprint("AbsorbeurDeMagie modifySpellTargetChoice")
        #print "AbsorbeurDeMagie:poss are initialy",len(targets)
        for m in reversed(targets) :
            if not any([(b.__class__.__name__=="AbsorbeurDeMagie") for b in m.bonus]) :
                targets.remove(m)
        #print "AbsorbeurDeMagie:poss targets reduced to",len(targets)
        return targets
class Isole(BonusMonstre) :
    interest=1    
    def getCost(self,monster) :
        return 0.3+monster.att/7.+monster.pv/7.
    def getStars(self):
        return 0
    def modifySpellTarget(self,targets) :
        #print "appel modifySpellTargetChoice"
        if (self.owner in targets) and len(targets)>1 :
            targets.remove(self.owner)
            #print "self is removed from targets"
        else :
            pass
            #print "self is not removed from targets",(self.owner in targets),len(targets)
        return targets

class Errant(BonusMonstre):
    power = 1
    interest=0    
    is_cost_alterator=True
    def getStars(self):
        return int(self.power*0.8-0.3)

    def endturn(self,creature):
        ChangementDeCamp().effect(creature,creature)
    
    def whenPlayed(self,monster):
        if monster.costint>=2 :
            monster.player.drawCard(1)
        
    def getCost(self,monster) :
        powercosts = [abs(m.getCost(monster))*((m.interest>0)*1.5+(m.interest==0)*1.-0.5) for m in monster.bonus if not m.is_cost_alterator and not isinstance(m,Errant)]
        self.power = 0.2*sum([abs(p) for p in powercosts])+0.15*(monster.pv + monster.att)- int(0.5*sum([m.getStars() for m in monster.bonus if not isinstance(m,Errant)])+0.5)
        return 1.1-0.6*sum(powercosts)-0.35*monster.pv -0.2*monster.att
    
    def getDescription(self):
        return "Change d'armee a la fin de chaque tour"

class Insaisissable(BonusMonstre) :
    interest=1    
    def getCost(self,monster) :
        co=[m.getCost(monster)*0.9+(m.getStars()>0)*1.2 for m in monster.bonus if not m.is_cost_alterator and not m.__class__.__name__=="Insaisissable"]
        co=co+[monster.att*0.5,monster.pv*0.5]
        co=[abs(c) for c in co]
        return sum(co)*0.2
    def getStars(self):
        return 1
    def modifyDefenseChoice(self,targets) :
        if self.owner in targets : # is not if another has provocation
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets

class AttaqueADistance(BonusMonstre) :
    interest=1    
    def beforeCombat(self,monster,other) :
        if monster is self.owner :
            oldseq=FunctionType(monster.combatSequence.__code__,globals(),closure=monster.combatSequence.__closure__)
            
            def modifseq(monsterself,target) :
                #print" modif sequence"
                monsterself.attack(other)
                monster.combatSequence=MethodType(oldseq,monster)

#                monsterself.afterCombat(target)
            monster.combatSequence=MethodType(modifseq,monster)
            
#            olddef=other.defend
#            oldafter=other.afterCombat
#            def modifdef(monsterself,target) :
#            #print " defend de ",other.name," modifiee"
#                pass
#            def modifafter(monsterself,target) :
#                #print " apres combat de ",other.name," modifiee par attack a distance"
#                monsterself.defend=olddef
#                monsterself.afterCombat=oldafter
#                oldafter(target)
#            other.defend=MethodType(modifdef,other)
#            other.afterCombat=MethodType(modifafter,other)
    def attackAnimationSprite(self,sprite):
        return Sprite(sprite,"gameAnimationImages/stone.png",[50,40]) 
    def getCost(self,monster) :
        charge=sum([0.2 for m in monster.bonus if isinstance(m,Charge)])
        return monster.att * (0.35+charge) +0.1
    def getStars(self):
        return 1
        
   
class Furie(BonusMonstre):
    interest=1    
    def getCost(self,monster) :
        return 0.2+max(1.,monster.att)/6. + monster.pv*0.1
    def getStars(self):
        return 1
    def beforeCombat(self,monster,target) :
        if monster is self.owner and monster.n_attack<1. :
            monster.n_attack += 1
            monster.ready=True
    def afterInvocation(self,monster) :
        if not hasattr(monster,"n_attack") :
            monster.n_attack = 1
    def endturn(self,monster):
        monster.n_attack = 0

class Initiative(BonusMonstre) :
    interest=1    
    def getCost(self,monster) :
        return monster.att*0.6-0.1
    def getStars(self):
        return 1
    def beforeCombat(self,adv1,adv2) :
        monster=self.owner
        other=[adv1,adv2][adv1 is self.owner]
        #print "other=",other.name
        #print [(b.__class__.__name__!="Initiative") for b in other.bonus],[(b.__class__.__name__!="AttaqueADistance") for b in adv1.bonus]
        if (all([(b.__class__.__name__!="Initiative") for b in other.bonus])
            and all([(b.__class__.__name__!="AttaqueADistance") for b in adv1.bonus])
            and all([(b.__class__.__name__!="NePeutPasRiposter") for b in adv2.bonus])) :
            #print "before combat de Initiative"
            oldotherseq=FunctionType(other.combatSequence.__code__,globals(),closure=other.combatSequence.__closure__)
            oldmonsterseq=FunctionType(monster.combatSequence.__code__,globals(),closure=monster.combatSequence.__closure__)
            
            def modifseq(anyself,anytarget) :
                #print" modif sequence"
                monster.attack(other)
                if other.pv >0 :
                    other.attack(monster)
                other.combatSequence=MethodType(oldotherseq,other)
                monster.combatSequence=MethodType(oldmonsterseq,monster)
            other.combatSequence=MethodType(modifseq,other)
            monster.combatSequence=MethodType(modifseq,monster)
#            other.combatSequence=MethodType(modifseq,other)
#            other.afterCombat=MethodType(modifafter,other)



class Charge(BonusMonstre) :
    interest=0    
    def getCost(self,monster) :
        return 0.45+max(monster.att,1)*0.3
    def whenPlayed(self,monster) :
        if monster.card :
            monster.ready=True
        if self in monster.bonus :
            monster.bonus.remove(self)
        monster.setValue()

class CarteImportantePourOrdi(BonusMonstreWithLevel) :
    interest=1  
    def whenPlayed(self,monster) :
        self.owner.playedby=self.owner.player.id
    def getStars(self):
        return 0
    def getCost(self,monster) :
        return 0.
    def getDescription(self):
        return ""

class CarteImportantePourOrdiUneFois(CarteImportantePourOrdi) :
    def whenPlayed(self,monster) :
        for m in self.owner.player.army :
            if self.owner.name==m.name and not (self.owner is m):
                self.owner.bonus.remove(self)
                break
        else :
            self.owner.playedby=self.owner.player.id
  

class NePeutPasAttaquer(BonusMonstre) :
    interest=-0.8  # avec interst=-1, l ordi tape ses monstres et donne +1 attaque a ennemi   
    def getCost(self,monster) :
        add= any([isinstance(b,CoutReduit) for b in monster.bonus])                                                                      
        return -monster.att/4.3+add*0.1*monster.att-0.2  
    def modifyAttackChoice(self,targets):
        if self.owner in targets  :
            return [self.owner]
        else :
            return []

class NePeutPasAttaquerLesHeros(BonusMonstre) :
    interest=-0.4  # avec interst=-1, l ordi tape ses monstres et donne +1 attaque a ennemi   
    def getCost(self,monster) :
        #print("cout ne peu",0.-monster.att*0.1-0.05)                                                                   
        return 0.-monster.att*0.15-monster.pv*0.05
    def modifyAttackChoice(self,targets):
        if self.owner.player.adv in targets  :
            targets.remove(self.owner.player.adv)
        return targets
    def getDescription(self):
        return "Ne peut pas attaquer\n les heros."

class NePeutPasRiposter(BonusMonstre) :
    interest=-1    
    def getCost(self,monster) :                                                                          
        return -monster.att*0.2+0.
    def beforeCombat(self,adv1,adv2) :
        if "simu" not in self.owner.player.name :
            fprint( "%%%% NePeutPasRiposter beforeCombat ",adv1.name,"attaque",adv2.name)
        #print [(b.__class__.__name__!="Initiative") for b in other.bonus],[(b.__class__.__name__!="AttaqueADistance") for b in adv1.bonus]
        if adv2 is self.owner :
            if "simu" not in self.owner.player.name :
                fprint( self.owner.name," N Peut Pas Riposter  avec att=",self.owner.att)
            self.owner.oldatt=self.owner.att
            self.owner.att=0
    def afterCombat(self,owner,adv) :
        #print "other=",other.name
        #print [(b.__class__.__name__!="Initiative") for b in other.bonus],[(b.__class__.__name__!="AttaqueADistance") for b in adv1.bonus]
        if hasattr(self.owner,"oldatt") :
            self.owner.att=self.owner.oldatt
            delattr(self.owner,"oldatt")
            if "simu" not in self.owner.player.name :
                print( "NePeutPasRiposter  retour a",self.owner.att)
        else :
            if "simu" not in self.owner.player.name :
                print ("attaquant ne change pas")



class Camouflage(BonusMonstre) :
    interest=1    
    """
    def __init__:
        has_attacked=False
        """
    def getCost(self,monster) :  
        return 0.8+monster.att/8.+monster.pv/10.
    def getStars(self):
        return 0
    def afterInvocation(self,monster) :
        monster.addMark("camouflage_feuilles",pos="center",size=(150,200))
        monster.hidden=True   # pour verif que camouflage n est pas ajoute a chaque tour
    def beginTurn(self,monster) :
        self.removed()
        self.owner.bonus.remove(self)
        self.owner.setValue()
    def modifyDefenseChoice(self,targets) :
        if self.owner in targets and hasattr(self.owner,"hidden") and self.owner.hidden: # is not in list if another has provocation
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets
    def afterCombat(self,monster,target):
        self.removed()
    def modifySpellTargetChoice(self,targets) :
        if self.owner in targets and hasattr(self.owner,"hidden") and self.owner.hidden : 
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets
    def removed(self) :
        #print "remove camouflage"
        self.owner.hidden = False
        self.owner.removeMark("camouflage_feuilles")
        

""" Bonus permanents avec niveaux ------------------------- """

class CoutDesSortsReduit(BonusMonstreWithLevel) :
    interest=1    
    def getCost(self,monster) :
        return monster.att/10. + monster.pv/8. + 1.9*self.level-0.8
    def modifyManaCost(self,card,cost):
        if card.pv == 0 :
            return max(0,cost - self.level)
        else:
            return cost

class CoutDesMonstresReduit(BonusMonstreWithLevel) :
    interest=1    
    def getCost(self,monster) :
        return monster.att/8. + monster.pv/8. + 2.*self.level-0.8
    def modifyManaCost(self,card,cost):
        if card.pv >0 :
            return max(0,cost - self.level)
        else:
            return cost

#class DegatDesSortsAugmentes(BonusMonstreWithLevel) :
#    def getCost(self,monster) :
#        return monster.att/8. + monster.pv/8. + 2*self.level

class LienDeVie(BonusMonstreWithLevel) :
    interest=1    
    def getCost(self,monster) :
        return 0.1 + 0.8*self.level-monster.pv*0.1+max(0.,self.level+1-monster.pv)*0.2
    def getStars(self):
            return 1
    def modifyTakenDamage(self,damage):
        if damage <= self.level:
            self.owner.player.sufferDamage(damage)
            damage=0
        else:
            self.owner.player.sufferDamage(self.level)
            damage-=self.level
        self.owner.player.updateImage()
        return damage
    def removed(self) :
        self.owner.sufferDamage=MethodType(Creature.sufferDamage,self.owner)   

class Incassable(BonusMonstre):
    interest=1    
    def getCost(self,monster) :
        comp=sum([0.7 for b in monster.bonus if isinstance(b,Trigger)])
        return 0.2 + comp*(0.1*(1+monster.pv*0.8))+ (monster.att+1.)*(monster.pv)*0.15
    def getStars(self):
        return 1
    def modifyTakenDamage(self,damage):
        if damage>0 :
            damage=1
            self.owner.casse+=1
        if self.owner.casse>=self.owner.card.pv :
            self.owner.bonus.remove(self)
        return damage
    def afterInvocation(self,creature):
        creature.casse=0
#        def newSufferDamage(monsterself,damage):
#            if damage>0 :
#                monsterself.ancientSufferDamage(1)
#                monsterself.casse+=1
#                if monsterself.casse>=self.owner.card.pv :
#                    self.removed
#        creature.sufferDamage = MethodType(newSufferDamage,creature)
           

class GardienDeVie(BonusMonstre) :
    interest=1    
    def getCost(self,monster) :
        return 0.8
    def modifyPlayerSuffer(self,player,damage):
        if damage==0 :
            return 0
        self.owner.sufferDamage(damage)
        return 0

class DonneBonus(BonusMonstreWithTwoLevels) :
    interest=0.2 # si le bonus ne se voit pas sur le terrain, alors peu d interret    
    def getCost(self,monster) :
        return self.level2*1.2 + self.level*1.6 + max(0.,(self.level-self.level2)*0.2) + monster.pv/8.  -0.3
    def getDescription(self):
        return "Donne a tous les allies +"+str(self.level)+"/+"+str(self.level2)
    def afterInvocation(self,creature):
        for m in self.owner.player.army :
            if not m is self.owner and m.pv>0 :
                self.additionalBonus(m)
    def removed(self) :
        #print "tite verif ", creature," should be ",self.owner
        limo=[m for m in self.owner.player.army]
        for target in limo :
            if target.pv>0 :
                self.removeOn(target)
    def removeOn(self,target) :
        if not target is self.owner and target.pv>0 :
            target.max_pv -= min(self.level2,target.card.pv+1)
            target.att -= min(self.level,target.card.att+1)
            if target.att<0 :
                target.att=0
            if self.level2 :
                target.removeMark("bonus_mark_pv",min(self.level2,target.card.pv+1))
            if self.level :
                target.removeMark("bonus_mark_dam",min(self.level,target.card.att+1))        
            target.pv -= min(self.level2,target.card.pv+1)
            if target.pv <1 :
                target.die()
    def death(self,creature) :
        self.removed()
    def additionalBonus(self,target):
        pvgain=min(self.level2,target.card.pv+1)
        target.pv += pvgain
        target.max_pv += pvgain
        attgain=min(self.level,target.card.att+1)
        target.att += attgain
        if self.level2 :
            target.addMark("bonus_mark_pv",typ="number",level=pvgain,size=(100,100),pos="se")
        if self.level :
            target.addMark("bonus_mark_dam",size=(100,100),typ="number",level=attgain,pos="sw")

#def removed(self):
#        for m in self.owner.player.army :
#            for p in m.bonus :
#                if hasattr(p,origin) and (p.origin is self) :
#                    m.bonus.remove(p)

class BonusParAllies(BonusMonstreWithTwoLevels) :
    interest=0.2    
    def getCost(self,monster) :
        plus=0.
        for b in monster.bonus :
            if isinstance(b,Charge) :
                plus+=0.3
            if isinstance(b,Determine) :
                plus+=0.5
            if isinstance(b,Initiative) :
                plus+=0.4
        return (self.level*2.1  + self.level2*1.7 + max(0.,self.level-self.level2)*0.3)*(1.+plus)
    def getStars(self):
        return 1
    def getDescription(self):
        return "A +"+str(self.level)+"/+"+str(self.level2) +" par allies"
    def afterInvocation(self,target):
        n=len([m for m in target.player.army if m.max_pv>0 and not m.is_dead])-1
        target.pv += self.level2*n
        target.max_pv += self.level2*n
        target.att += self.level*n       
        if self.level2 :
            #print "dans bonus par allie addMark"
            target.addMark("bonus_mark_pv",typ="number",level=self.level2*n,size=(100,100),pos="se")
        if self.level :
            target.addMark("bonus_mark_dam",size=(100,100),typ="number",level=self.level*n,pos="sw")
    def otherDeath(self,creature) :
        self.owner.pv -= self.level2
        self.owner.max_pv -= self.level2
        self.owner.att -= self.level
        if self.level2 :
            self.owner.removeMark("bonus_mark_pv",level=self.level2)
        if self.level :
            self.owner.removeMark("bonus_mark_dam",level=self.level)
        if self.owner.pv<1 :
            self.owner.die()
    def additionalBonus(self,creature):
        self.owner.pv += self.level2
        self.owner.max_pv += self.level2
        self.owner.att += self.level
        if self.level2 :
            self.owner.addMark("bonus_mark_pv",level=self.level2,typ="number",size=(100,100),pos="se")
        if self.level :
            self.owner.addMark("bonus_mark_dam",level=self.level,typ="number",size=(100,100),pos="sw")
    def removed(self) :
        target=self.owner
        n=len([m for m in target.player.army if m.max_pv>0 and not m.is_dead])-1
        target.pv -= self.level2*n
        target.max_pv -= self.level2*n
        target.att -= self.level*n        
        if self.level2 :
            self.owner.removeMark("bonus_mark_pv",level=self.level2*n)
        if self.level :
            self.owner.removeMark("bonus_mark_dam",level=self.level*n)
        if self.owner.pv<1 :
            self.owner.die()


class BonusParEnnemi(BonusMonstreWithTwoLevels) :
    interest=0.2    
    def getCost(self,monster) :
        plus=0.
        for b in monster.bonus :
            if isinstance(b,Charge) :
                plus+=0.3
            if isinstance(b,Determine) :
                plus+=0.5
            if isinstance(b,Initiative) :
                plus+=0.4
        return (self.level*1.9  + self.level2*1.5 + max(0.,self.level-self.level2)*0.2)*(1.+plus)
    def getStars(self):
        return 1
    def getDescription(self):
        return "A +"+str(self.level)+"/+"+str(self.level2) +" par ennemi"
    def afterInvocation(self,target):
        n=len([m for m in target.player.adv.army if m.max_pv>0 and not m.is_dead])
        target.pv += self.level2*n
        target.max_pv += self.level2*n
        target.att += self.level*n      
        if self.level2 :
            #print "dans bonus par ennemi addMark"
            target.addMark("bonus_mark_pv",typ="number",level=self.level2*n,size=(100,100),pos="se")
        if self.level :
            target.addMark("bonus_mark_dam",size=(100,100),typ="number",level=self.level*n,pos="sw")
    def enemyDeath(self,creature) :
        self.owner.pv -= self.level2
        self.owner.max_pv -= self.level2
        self.owner.att -= self.level
        if self.level2 :
            self.owner.removeMark("bonus_mark_pv",level=self.level2)
        if self.level :
            self.owner.removeMark("bonus_mark_dam",level=self.level)
        if self.owner.pv<1 :
            self.owner.die()
    def otherMonsterCreation(self,creature):
        self.owner.pv += self.level2
        self.owner.max_pv += self.level2
        self.owner.att += self.level
        if self.level2 :
            self.owner.addMark("bonus_mark_pv",level=self.level2,typ="number",size=(100,100),pos="se")
        if self.level :
            self.owner.addMark("bonus_mark_dam",level=self.level,typ="number",size=(100,100),pos="sw")
    def removed(self) :
        target=self.owner
        n=len([m for m in target.player.adv.army if m.max_pv>0 and not m.is_dead])
        target.pv -= self.level2*n
        target.max_pv -= self.level2*n
        target.att -= self.level*n        
        if self.level2 :
            self.owner.removeMark("bonus_mark_pv",level=self.level2*n)
        if self.level :
            self.owner.removeMark("bonus_mark_dam",level=self.level*n)
        if self.owner.pv<1 :
            self.owner.die()
#class BonusParServiteurs(BonusMonstreWithTwoLevels) :

class DonneArmureAuHero(BonusMonstreWithLevel) :
    interest=1    
    def getCost(self,monster) :
        return 0.2+self.level*0.7 + monster.pv/12. 
    def getDescription(self):
        return "Donne {0} point".format(self.level)+"s"*(self.level>1)+" d'armure au hero"
    def modifyPlayerSuffer(self,player,damage):
        if damage<self.level:
            return 0
        else:
            return damage-self.level
    
    def getStars(self):
        return 0


""" Donne capacites a tous les allies  ----------------- """
                                       
class DonneCapacitesAuxAllies(BonusMonstreGivingBonus) :
    def getCost(self,monster) :
        from Card import troll
#        if self.spell.__class__.__name__=="NePeutPasAttaquer" or self.spell.__class__.__name__=="ALaPlaceDeLAttaque" :
#            return max(20,self.spell.getCost(troll))
#        if self.spell.__class__.__name__=="Incarnation"  :
#            return 100
        self.interest=self.spell.interest
        return max(0.35-self.spell.getCost(troll)*1.4,self.spell.getCost(troll)*(1.+0.4*(self.interest<0.)))*3.1 + 0.2
    def getStars(self):
        return self.spell.getStars() + 1
    def getDescription(self):
        return "Donne a tous les allies "+self.restriction+":"+("\n"*bool(self.restriction))+self.spell.getDescription()
    def afterInvocation(self,creature):
        self.interest=self.spell.interest
        if self.spell.__class__.__name__!="CriDeGuerre" :
            for m in self.owner.player.army :
                if not m is self.owner and m.pv>0 :
                    if self.restriction in m.name :
                        # print 'ajoute bonus a ',m.name
                        self.additionalBonus(m)
                    else :
                        pass
                        #print m.name ,"ne profite pas"                               
    def removed(self) :
        for target in self.owner.player.army :
            if target.pv>0 :
                self.removeOn(target)
    def removeOn(self,target) :
        if not target is self.owner :
            if self.restriction in target.name  :                          
              for b in reversed(target.bonus) :
                if isinstance(b,self.spell.__class__):
                    # print "trouve bonus ",target.name," pour remove ",len(target.bonus)
                    b.removed()
                    target.bonus.remove(b)   # utile removed n enleve pas le bonus
                    # print "->",len(target.bonus)
                    break
    def death(self,creature) :
        self.removed()
    def additionalBonus(self,target):
        if self.restriction in target.name :
            target.bonus.append(copy(self.spell))
            target.bonus[-1].owner=target
            target.bonus[-1].afterInvocation(target)
        
    
""" Conditions  -----------------"""

class CriDeGuerre(Trigger) :
    interest=0
    def getCost(self,monster) :
        if isinstance(self.spell.target,Target.Personnel) :
            return 0.4+self.spell.getCost()*1.2
        else :
            return 0.3+self.spell.getCost()
    def whenPlayed(self,creature):
        if creature.pv<=0 :
            return
        if not "simu" in creature.player.name :
            fprint( "creature",creature.name," crideguerre ",self.spell.constructor())
        #else :
             #print "dans simulation  : creature",creature.name," crideguerre ",self.spell.constructor()           
        creature.player.launch(creature,self.spell)
        if self in creature.bonus :
            creature.bonus.remove(self) # ameliore l evaluation par l ordi de la valeur de la creature 
        creature.starcost-=self.spell.getStars()
        creature.setValue()

class AuDebutDuProchainTour(Trigger) :
    #interest= beaucoup
    def getCost(self,monster) :
        comp=sum([1 for b in monster.bonus if isinstance(b,Camouflage)])
        return self.spell.getCost()*(0.65+comp*0.2)
        
    def endturn(self,creature) :
        creature.attente_faite=True
        
    def beginTurn(self,creature):
        if not hasattr(creature,"attente_faite") :
            return
        delattr(creature,"attente_faite")
        #else :
             #print "dans simulation  : creature",creature.name," crideguerre ",self.spell.constructor()           
        creature.player.launch(creature,self.spell)
        if self in creature.bonus :
            creature.bonus.remove(self) # ameliore l evaluation par l ordi de la valeur de la creature 
        creature.starcost-=self.spell.getStars()
        creature.setValue()

class ChaqueTour(Trigger) :
    def getCost(self,monster) :
#        if ".AuChoix" in self.spell.constructor() :
#            fprint( "il y a un pb avec un AuChoix dans ChaqueTour or le spell est ",self.spell.constructor())
#            return 99
        self.interest=self.spell.getValue()
        return abs(self.spell.getCost()*1.4)-0.3+self.spell.getStars()*0.2
    def getStars(self):
        return 1 + self.spell.getStars()
    def endturn(self,creature) :
        if hasattr(self.owner,"tour2") or  (not any([(b.__class__.__name__=="Errant") for b in creature.bonus]) ):
            creature.game.effect_list.append([1,creature.player.id,"launch",[creature.id,self.spell]])
        self.owner.tour2=True

class Souffrant(BonusMonstre):
    interest=-1    
    def getCost(self,monster):
        if any([(b.__class__.__name__=="RaleDAgonie") for b in monster.bonus]) :
            return 0.05
        return -0.1-0.1*monster.att-0.05*monster.pv-0.1*len(monster.bonus)
    def getStars(self):
        return 0
    def afterInvocation(self,monster):
        monster.addMark("Souffrant",typ="power",value=-0.2)
        self.owner = monster
    def beginTurn(self,monster):
        monster.sufferDamage(1)    
    def removed(self):
        self.owner.removeMark("Souffrant")

class AvecAttaque(Trigger):
    def getCost(self,monster) :
        self.interest=self.spell.getValue()
        comp=sum([1 for b in monster.bonus if isinstance(b,Charge) or isinstance(b,Furie)])
        return max(self.spell.getCost()*(1.2-0.7*(self.spell.has_target and isinstance(self.spell.target,Target.UneCibleAuChoix))+comp*0.4)+ monster.pv/12. -0.3+self.spell.getStars()*0.2,0.)
    def getStars(self):
        return self.spell.getStars()
    
    def beforeCombat(self,attacker,defender) :
        if self.owner is attacker :
            from Target import UneCibleAuChoix
            if self.spell.has_target and isinstance(self.spell.target,UneCibleAuChoix) :
                #self.spell.getTarget=MethodType(getTarget,self.spell)
                self.owner.player.spellEffect(self.spell,attacker,[defender])
            else :
                self.owner.player.launch(attacker,self.spell)

class ALaPlaceDeLAttaque(Trigger):
    def getCost(self,monster) :
        comp=sum([1 for b in monster.bonus if isinstance(b,Charge) or isinstance(b,Furie)])
        self.interest=[-1,0,1][(self.spell.getCost()>monster.att/3.)+self.spell.positive]
        if self.spell.getValue()>0 :
            return (self.spell.getCost()+self.spell.getStars()*0.2)*1.2*(1.+comp*0.4)+0.4-0.2*monster.att
        else :
            return (self.spell.getCost()+self.spell.getStars()*0.2)*1.2*(1.+comp*0.4)+0.8
    def getStars(self):
        return self.spell.getStars()
    def beforeCombat(self,owner,target):
        #print "appel before combat",owner.name,target.name
        if target is owner :
            #print "before combat ->spell"
            old_att = FunctionType(owner.combatSequence.__code__,globals(),closure=owner.combatSequence.__closure__)
            def new_combatSeq(oneself,thesame):
                oneself.player.launch(oneself,self.spell)
                oneself.combatSequence = MethodType(old_att,oneself)
                #print "launch a la place de combat"
            owner.combatSequence = MethodType(new_combatSeq,owner)
    def modifyAttackChoice(self,targets) :
        #print "attack choice =owner ( a la place de attaque)"
        return [self.owner]
        
class QuandIlTue(Trigger):
    def getCost(self,monster) :
        self.interest=self.spell.getValue()
        fac=1.1+(self.spell.getValue()<0)*1.
        return self.spell.getCost()*fac+self.spell.getStars()*0.2
    def getStars(self):
        return self.spell.getStars()
#    def afterInvocation(self,creature):
#        self.owner.old_att = FunctionType(creature.attack.__code__,globals(),closure=creature.attack.__closure__)
#        def new_att(oneself,target):
#            MethodType(self.owner.old_att,oneself)(target)
#        creature.attack = MethodType(new_att,creature)
#        print("creature",creature,self.owner," has old_att")
#    def removed(self) :
#        if not hasattr(self.owner,"old_att") :
#            print("owner ",self.owner,self.owner.name, " has no old attack due to QuandIlTue removed")
#            return
#        self.owner.attack = MethodType(self.owner.old_att,self.owner)
#    def beforeCombat(self,attacker,defender) :
#        creature=self.owner
#        adv=[attacker,defender][attacker is creature]
#        self.previouspv=adv.pv
#        from Target import UneCibleAuChoix
#        if isinstance(self.spell.target,UneCibleAuChoix) :
#            creature.attacked_target=adv
#            def getTarget(oneself,crea) :
#                return  [crea.attacked_target]
#            self.spell.getTarget=MethodType(getTarget,self.spell)
    def afterCombat(self,creature,adv) : 
        if hasattr(adv,"is_dead") and adv.is_dead and not (hasattr(adv,"is_invocation") and adv.is_invocation and adv.player==self.owner) :
            creature.player.launch(creature,self.spell)
#        else :
#            fprint( " pas de degat vu, pas d effet : previous=",self.previouspv,">",adv.pv)

        
class QuandIlBlesse(Trigger):
    def getCost(self,monster) :
        comp=any([isinstance(b,Incassable) for b in monster.bonus])*0.3+monster.pv/12.+1.
        fac=1.+(self.spell.getValue()<0)*0.5
        self.interest=self.spell.getValue()
        return self.spell.getCost()*(1.9-0.9*(self.spell.has_target and isinstance(self.spell.target,Target.UneCibleAuChoix)))*comp*fac-0.3+self.spell.getStars()*0.3
    def getStars(self):
        return self.spell.getStars()+1
    def beforeCombat(self,attacker,defender) :
        creature=self.owner
        adv=[attacker,defender][attacker is creature]
        self.previouspv=adv.pv
        from Target import UneCibleAuChoix
        if isinstance(self.spell.target,UneCibleAuChoix) :
            creature.attacked_target=adv
            def getTarget(oneself,crea) :
                return  [crea.attacked_target]
            self.spell.getTarget=MethodType(getTarget,self.spell)
    def afterCombat(self,creature,adv) : 
        if self.previouspv>adv.pv :
            self.owner.player.launch(creature,self.spell)
        else :
            fprint( " pas de degat vu, pas d effet : previous=",self.previouspv,">",adv.pv)
        def getTarget(oneself,crea) :
            return  [crea.attacked_target]
        from Target import UneCibleAuChoix
        if isinstance(self.spell.target,UneCibleAuChoix) :
            self.spell.getTarget=MethodType(getTarget,self.spell)

class QuandUnAllieEstTue(Trigger):
    def beginTurn(self,monster) :
        self.owner.deadThisTurn=0
    def getCost(self,monster) :        
        fac=1.+(self.spell.getValue()<0)*0.6
        self.interest=self.spell.getValue()
        return abs(self.spell.getCost()*1.3+0.5)*fac-0.3+self.spell.getStars()*0.4
    def getStars(self):
        return 1 + self.spell.getStars()
    def otherDeath(self,creature) :
        if ((not hasattr(self.owner,"deadThisTurn")) or self.owner.deadThisTurn<4) :
            if hasattr(self.owner,"deadThisTurn") :
                self.owner.deadThisTurn+=1
            else :
                self.owner.deadThisTurn=1
            #print("other death")
            self.owner.player.game.effect_list.append([1,self.owner.player.id,"launch",[self.owner.id,self.spell]])


#class QuandUnAllieEstBlesse(Trigger):
#    def getCost(self,monster) :        
#        return self.spell.getCost()*2.5+1
#    def getStars(self):
#        return 2 + self.spell.getStars()

#class QuandUnServiteurEstBlesse(Trigger):
#    def getCost(self,monster) :        
#        return self.spell.getCost()*3+1.5
#    def getStars(self):
#        return 2 + self.spell.getStars()

class QuandIlEstBlesse(Trigger):
    def beginTurn(self,monster) :
        self.owner.damageThisTurn=0
    def getCost(self,monster) :
        fac=1.+(self.spell.getValue()<0)*1.
        self.interest=self.spell.getValue()
        return abs(self.spell.getCost()*(1.5+monster.pv*0.2))*fac-0.6-0.3+self.spell.getStars()*0.6
    def getStars(self):
        return 1 + self.spell.getStars()
    def modifyTakenDamage(self,damage):
        if damage>0:
            if  ((not hasattr(self.owner,"damageThisTurn")) or self.owner.damageThisTurn<4) :
                if hasattr(self.owner,"damageThisTurn") :
                    self.owner.damageThisTurn+=1
                else :
                    self.owner.damageThisTurn=1
                self.owner.player.game.effect_list.append([1,self.owner.player.id,"launch",[self.owner.id,self.spell]])

        return damage
    def removed(self) :
        self.owner.sufferDamage = MethodType(Creature.sufferDamage,self.owner)

class QuandLAdvLanceUnSort(Trigger):
    def beginTurn(self,monster) :
        self.owner.otherSpellThisTurn=0
    def getCost(self,monster) :
        self.interest=self.spell.getValue()
        fac=1.+(self.spell.getValue()<0)*1.2
        return abs(0.2 + self.spell.getCost()*0.7*fac)-0.5+self.spell.getStars()*0.2
    def getStars(self):
        return 1 + self.spell.getStars()
    def getDescription(self):
        return "Chaque fois que l ennemi lance un sort: \n"+self.spell.getDescription()
    def otherSpellLaunched(self,one_spell):
        fprint('declanchement trig otherSpellLaunched')
        if  ((not hasattr(self.owner,"otherSpellThisTurn")) or self.owner.otherSpellThisTurn<4) :
            self.owner.player.game.effect_list.append([1,self.owner.player.id,"launch",[self.owner.id,self.spell]])
            if hasattr(self.owner,"otherSpellThisTurn") :
                self.owner.otherSpellThisTurn+=1
            else :
                self.owner.otherSpellThisTurn=1
        # old self.owner.player.launch(self.owner,self.spell)
        
class QuandVousLancezUnSort(Trigger):
    def beginTurn(self,monster) :
        self.owner.spellThisTurn=0
    def getCost(self,monster) :
        self.interest=self.spell.getValue()
        surcout=0
        if (self.spell.__class__.__name__=="PlaceCarteDansMain" or self.spell.__class__.__name__=="PiocheCartes"
                  or  self.spell.__class__.__name__=="GainMana") :
            surcout=1.
        return abs(0.2 + self.spell.getCost()*1.5)+0.4+self.spell.getStars()*0.8+surcout
    def getStars(self):
        surcout=0
        if (self.spell.__class__.__name__=="PlaceCarteDansMain" or self.spell.__class__.__name__=="PiocheCartes"
                  or  self.spell.__class__.__name__=="GainMana") :
            surcout=1 
        return 1 + self.spell.getStars()+surcout
    def getDescription(self):
        return "A chaque fois que vous lancez un sort: \n"+self.spell.getDescription()
    def spellLaunched(self,one_spell):
        #print " spell launched en plus (bonus de ",self.owner.name,") player=",self.owner.player.name
        #self.spell.owner=self.owner # utile pour quoi ?
        if  ((not hasattr(self.owner,"spellThisTurn")) or self.owner.spellThisTurn<4) :
            self.owner.player.game.effect_list.append([1,self.owner.player.id,"launch",[self.owner.id,self.spell]])
            if hasattr(self.owner,"spellThisTurn") :
                self.owner.spellThisTurn+=1
            else :
                self.owner.spellThisTurn=1
        #old : self.owner.player.launch(self.owner,self.spell)

class QuandLAdvInvoqueUnMonstre(Trigger): 
    def beginTurn(self,monster) :
        self.owner.invocThisTurn=0
    def getCost(self,monster) :
        self.interest=self.spell.getValue()
        fac=1.1+(self.spell.getValue()<0)*1.
        return abs(0.4 + self.spell.getCost()*fac)-0.6+self.spell.getStars()*0.2
    def getStars(self):
        return 1 + self.spell.getStars()
    def getDescription(self):
        return "A chaque nouvel ennemi: \n"+self.spell.getDescription()
    def otherMonsterCreation(self,one_spell):
        if  ((not hasattr(self.owner,"invocThisTurn")) or self.owner.invocThisTurn<4) :
            self.spell.owner=self.owner
            if hasattr(self.owner,"invocThisTurn") :
                self.owner.invocThisTurn+=1
            else :
                self.owner.invocThisTurn=1
            self.owner.player.game.effect_list.append([1,self.owner.player.id,"launch",[self.owner.id,self.spell]])

class RaleDAgonie(Trigger) :
    def getCost(self,monster) :
        self.interest=self.spell.getValue()
        cost = self.spell.getCost()
        if any([p.__class__ == Charge for p in monster.bonus]):
            return 0.3 + (1.+0.3*(self.interest<0.))*cost
        else:
            return 0.3 + cost*(0.7+0.7*(self.interest<0.))
    def getStars(self):
        return self.spell.getStars()
    def death(self,creature):
        #print "activation rale d agonie"
        if not creature.is_invocation : 
            creature.player.game.effect_list.append([1,creature.player.id,"launch",[creature.id,self.spell]])     


""" Sorts avec niveaux  -----------------"""

class DegatCreature(SpellWithLevel) :
    has_target=True
    positive=False
    negative=True
    def getCost(self) :
        n=min(12,self.level.getCostMultiplier(self))
        return (n*0.9-0.08*n*(n-1)/2)*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        #print "degat effect sur",target.name,target.game
        if isinstance(target,Creature) :
            target.sufferDamage(self.level.getLevel(origin))
    
    def getDescription(self):
        return "Inflige "+self.level.getDescription("degat sur creature") + self.target.getDescription()

class InteretPourOrdi(SpellWithLevel) :
    has_target=True
    positive=False
    negative=True
    def getCost(self) :
        return -0.2 # correspond au plus de deuxeffets
    def effect(self,origin,target):
        ""  
    def getDescription(self):
        return ""

class DegatSurSonHeros(SpellWithLevel) :
    positive=False
    negative=True
    has_target = False     
    def getTarget(self,origin):
        #print "GainMana origin.player",origin.player
        return [origin.player]
    def getStars(self):
        return 0
    def getCost(self) :
        self.interest=-1
        return self.level.getCostMultiplier(self)*0.6
    def effect(self,origin,target):
        #print "degat effect sur",target.name,target.game,self.level.getLevel(origin)
        target.pv-=self.level.getLevel(origin) # pas de reductio de degat sur ce malus
        target.sufferDamage(0)
    def willAct(self,creature):
        return (self.level.getLevel(creature)>0)
    def getDescription(self):
        return "Inflige "+self.level.getDescription("degat")+" sur son heros"
    def getValue(self) :  # interret au combat
        return -1.
        
class Degat(SpellWithLevel) :
    positive=False
    negative=True
    def getCost(self) :
        n=self.level.getCostMultiplier(self)
        return (n*0.9+0.08*n*(n-1)/2)*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        #print "degat effect sur",target.name,target.game
        target.sufferDamage(self.level.getLevel(origin))
    
    def getDescription(self):
        return "Inflige "+self.level.getDescription("degat") + self.target.getDescription()


class Bonus(SpellWithTwoLevels) :
    positive=True   
    def getCost(self) :
        att=self.level.getCostMultiplier(self)
        pv=self.level2.getCostMultiplier(self)
        return 0.1+(att*0.7+pv*0.5+max(0.,att-pv)*0.2)*(0.5+self.target.getCostMultiplier(self))
    def getDescription(self):
        pers = (self.target.__class__.__name__ == "Personnel")
        if self.level.__class__ != self.level2.__class__:
            return ("Donne","Gagne")[pers]+" +{0}/+{1}".format(self.level.getDescription("",False),self.level2.getDescription("",False))+ (1-pers)*(self.target.getDescription())
        else:
            return ("Donne","Gagne")[pers]+self.level.__class__.getDescriptionBonus(self.level,self.level2)+ (1-pers)*(self.target.getDescription())
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0:
            if not(any([isinstance(b,BonusEffect) for b in target.bonus])):
                b=BonusEffect(target)
                b.owner=target
                b.level = min(self.level.getLevel(target),target.card.att+1)
                b.level2 = min(self.level2.getLevel(target),target.card.pv+1)
                target.bonus.append(b)
                b.afterInvocation(target)
                target.addMark(b.getInlineDescription(),typ="power",value=[-1,1][self.positive])
            else:
                for b in target.bonus:
                    if isinstance(b,BonusEffect):
                        b.increaseLevel(min(self.level.getLevel(target),target.card.att+1),min(self.level2.getLevel(target),target.card.pv+1))
                        break
            target.setValue()

class BonusEffect(BonusMonstreWithTwoLevels):
    interest=0 # se voit sur le carac 
    def getCost(self,monster) :
        return self.level*0.5  + self.level2*0.5
    def getDescription(self):
        return "Bonus"
    def getInlineDescription(self):
        return "Bonus"
        
    def afterInvocation(self,target):
        target.pv += self.level2
        target.max_pv += self.level2
        target.att += self.level
        if self.level2 :
            target.addMark("bonus_mark_pv",typ="number",level=self.level2,size=(100,100),pos="se")
        if self.level :
            target.addMark("bonus_mark_dam",size=(100,100),typ="number",level=self.level,pos="sw")
    def increaseLevel(self,level,level2):
        self.owner.pv += level2
        self.owner.max_pv += level2
        self.owner.att += level
        if level2 :
            self.owner.addMark("bonus_mark_pv",typ="number",level=level2,size=(100,100),pos="se")
        if level :
            self.owner.addMark("bonus_mark_dam",size=(100,100),typ="number",level=level,pos="sw")  
        self.level2 += level2
        self.level += level      
    def removed(self) :
        target=self.owner
        target.pv -= self.level2
        target.max_pv -= self.level2
        target.att -= self.level    
        if self.level2 :
            self.owner.removeMark("bonus_mark_pv",level=self.level2)
        if self.level :
            self.owner.removeMark("bonus_mark_dam",level=self.level)
        if self.owner.pv<1:
            self.owner.die()
        self.owner.setValue()
"""
class Malus(SpellWithLevel) :
    positive = False
    def getCost(self) :
        return (self.level)*(self.target.getCostMultiplier(self)+0.1)
"""
#class Bonus1Tour(SpellWithLevel) :
#    positive = True
#    def getCost(self) :
#        return self.level * 0.5*self.target.getCostMultiplier(self)
#    def getSpellDescription(self):
#        return "Donne +{0} att aux allies ce tour".format(self.level)

class PiocheCartes(SpellWithLevel) :
    has_target = False
    positive = True
    def getCost(self) :
        return self.level.getCostMultiplier(self)*1.95-1.25        
    def getSpellDescription(self):
        return "Piochez "+self.level.getDescription("carte")
    def getStars(self):
        return 1
    def getTarget(self,creature) :
        return  [creature.player]
    def effect(self,origin,player):
        origin.player.drawCard(n=self.level.getLevel(origin))

class CopieMain(Spell.Spell) :
    positive = True # false is default
    has_target = True
    def getCost(self) :
        return 1.+2.*max(self.target.getCostMultiplier(self),1.)*(1.+(self.target.getCostMultiplier(self)==1.8))
    def getStars(self):
        return 2
    def effect(self,origin,creature):
        # print "activation of CopieMain"
        if isinstance(creature,Creature) and creature.max_pv>0 :
            origin.player.deck=[creature.card]+origin.player.deck
            origin.player.drawCard(1)
    def getDescription(self):
        return "Place une copie dans \n votre main "+self.target.getDescription(False)

class CopieInvoque(Spell.Spell) :
    positive = True # false is default
    has_target = True
    def getCost(self) :
        return 0.1+6.*max(self.target.getCostMultiplier(self),1.)*(1.+(self.target.getCostMultiplier(self)==1.8))
    def getStars(self):
        return 2
    def effect(self,origin,creature):
        if isinstance(creature,Creature) and creature.card.pv >0:
            card2=copy(creature.card)
            card2.bonus=[b for b in card2.bonus if b.__class__.__name__!="CriDeGuerre"]
            if isinstance(creature,AnimatedCreature)  :
                b=AnimatedCreature(origin,card2,origin.player)
            else :
                b=Creature(card2,origin.player,origin)
            b.is_invocation=True
            b.card=copy(creature.card)           
    def getDescription(self):
        return "Invoque une copie dans votre \n armee "+self.target.getDescription(False)


#class ChoisirDesCartesDefausse(SpellWithLevel) :
#    has_target = False
#    def getCost(self) :
#        return self.level*6 - 3
#    def getStars(self):
#        return 2

#class ChoisirDesCartesPioche(SpellWithLevel) :
#    has_target = False
#    def getCost(self) :
#        return self.level*5 - 2
#    def getStars(self):
#        return 1
"""
class Guerrison(SpellWithLevel):
    pass

class GuerrisonHero(SpellWithLevel):
    pass
"""

class Guerison(SpellWithLevel) :   
    positive = True
    negative=False
    def getCost(self) :
        return self.level.getCostMultiplier(self)*0.45*(0.5+self.target.getCostMultiplier(self)/2.)
    def effect(self,origin,creature):
        creature.pv = min(creature.pv+self.level.getLevel(origin),creature.max_pv)
        if hasattr(creature,"updateImage") :
            creature.updateImage()
        if hasattr(creature,"icon") : #Hero
            creature.icon.update()
        if isinstance(creature,Creature) :
            creature.setValue() 
    def getDescription(self):
        return "Gueris "+self.target.getDescription(False)+ " de "+self.level.getDescription("point"+"s"*(self.level.level>1)+" de vie",s=False)
    
    def willAct(self,creature):
        targets= self.target.getTarget(creature)
        for mons in targets  :
           if mons.max_pv >0 :
               for i in mons.bonus :
                   targets=i.modifySpellTarget(targets)
        return any([cr.max_pv-cr.pv>0 for cr in targets])

class GuerisonHeros(SpellWithLevel):
    has_target = False
    positive = True
    def getCost(self) :
        return self.level.getCostMultiplier(self)*0.42
    def getTarget(self,creature) :
        return  [creature.player]
    def effect(self,origin,creature):
        origin.player.pv = min(origin.player.pv+self.level.getLevel(origin),origin.player.max_pv)
        if hasattr(origin.player,"icon") :
            origin.player.icon.update()
    def getDescription(self):
        return ("Guerit le hero de "+self.level.getDescription("point"+"s"*(self.level.level>1)+" de vie",s=False))

class FaireDefausser(SpellWithLevel) :
    has_target = False
    positive = True
    def getCost(self) :
        return 0.3 + self.level.getCostMultiplier(self)*2.4    
    def getDescription(self):
        return ("Fait defausser {0} \n au hero adverse").format(self.level.getDescription("carte"))
    def getTarget(self,creature) :
        return  [creature.player.adv]
    def effect(self,origin,advplayer):
        fprint('FaireDefausser effect')
        from Sprites import Animation
        if len(advplayer.hand)>self.level.getLevel(origin) :
            fprint("appel de game.random de faire defausser")
            ca = [advplayer.hand[i] for i in advplayer.game.random(self.level.getLevel(origin),len(advplayer.hand))]
        else :
            ca=advplayer.hand
        for c in ca :
            if hasattr(advplayer,"icon") :
                c.show()
                destination=origin.getPosition()               
                phase0 = (destination,10, [2,20])
                Animation(c,[phase0])
            advplayer.hand.remove(c)
    
class DefausserSoi(FaireDefausser) :
    has_target = False
    positive=False   
    negative = True
    def getCost(self) :
        return 0.3 + self.level.getCostMultiplier(self)*2.3    
    def getDescription(self):
        return ("Defaussez {0} \n cartes").format(self.level.getDescription("carte"))
    def getTarget(self,creature) :
        return  [creature.player]
        
    def willAct(self,creature):
        return len(creature.player.hand)!=0
    def getValue(self) :  # interret au combat
        return -1.

class Sarcophage(SpellWithLevel) :
    positive = False
    negative = False
    def getCost(self) :
        return ((3.+0.6*self.level.getCostMultiplier(self)))*max([self.target.getCostMultiplier(self)-0.5,0.6])
#    def Effect(self) :
    def getStars(self):
        if self.target.getCostMultiplier(self)>1.5:
            return 1
        else:
            return 0
    def effect(self,origin,target):
        if isinstance(target,AnimatedCreature) : fprint( "appel sarco effect")
        if isinstance(target,Creature) and target.pv>0:
            if hasattr(target,"sarcoturn") and target.sarcoturn>0 :
                target.sarcoturn = max(target.sarcoturn,self.level.getLevel(origin))
                return
            #print "sarco sur",target.name
            #if isinstance(target,AnimatedCreature) : print "sarco sur",target.name
            target.addMark("sarcophage",size=(200,280),pos="center",typ="external",level=1,value=-2)                    
            def doNotModifyTarget(monsterself,targets):
                return targets
            for b in target.bonus :
                b.modifyDefenseChoice=MethodType(doNotModifyTarget,b)
            #print target.name," get nePeutpeasattaquer"
            target.bonus.append(SarcophageEffect(self.level.getLevel(origin)))
            target.bonus[-1].owner=target
            target.bonus.append(NePeutPasAttaquer())
            target.bonus[-1].owner=target
            target.bonus.append(NePeutPasRiposter())
            target.bonus[-1].owner=target
            target.sarcoturn = self.level.getLevel(origin)
            target.setValue()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : fprint( "pas d effet sur ",target.name)
    def willAct(self,creature):
        targets= self.target.getTarget(creature)
        for mons in targets  :
           if mons.max_pv >0 :
               for i in mons.bonus :
                   targets=i.modifySpellTarget(targets)
        return len(self.target.getTarget(creature))!=0 and any([not(hasattr(cr,"sarcoturn")) for cr in targets])
    
class SarcophageEffect(BonusMonstreWithLevel) :
    interest=0
    def getCost(self,monster) :
        return 1
    def modifyTakenDamage(self,damage):
        if damage>0:
            self.owner.sarcoturn-=damage
        if  self.owner.sarcoturn<=0 :
            self.owner.game.effect_list.append([4,None,"CardPowers.SarcophageEffect().removeOn",[self.owner.id]])       # attendre apres la riposte pour enlever l effet                      
        return 0
#    def afterCombat(self,mons,adv):
#        if  self.owner.sarcoturn<=0 :  # attendre apres la defense pour enlever l effet
#            self.removed()
#            self.owner.bonus.remove(self)   
#    def endturn(self,creature) :
#        if  self.owner.sarcoturn<=0 :
#            self.removed()
#            self.owner.bonus.remove(self)   
    def removed(self) :
        for cla in NePeutPasAttaquer,NePeutPasRiposter :
            for b in self.owner.bonus :
                    if isinstance(b,cla) :
                        self.owner.bonus.remove(b)
                        break
        self.owner.removeMark("sarcophage")                    
        self.owner.setValue()
    def removeOn(self,creature) :
        test=[isinstance(b,SarcophageEffect) for b in creature.bonus]
        if True in test :
            sarc=creature.bonus[test.index(True)]
            sarc.removed()
            creature.bonus.remove(sarc)
        
class Gel(Spell.Spell) :
    positive = False
    negative = True
    def getCost(self) :
        self.level=1.4
        return self.level*(self.target.getCostMultiplier(self)-0.4)*1.2
    def getStars(self):
        if self.target.getCostMultiplier(self)>1.5:
            return 1
        else:
            return 0
    def effect(self,origin,target):
        #print "appel gel effect"
        if isinstance(target,Creature) and target.pv>0 :
            if target.hasMark("gel") :
                target.iceturn+=1
            else :
                #print "gel sur",target.name,"de",target.player.name
                target.addMark("gel",size=(150,250),pos="center",typ="external",level=1,value=-1)
                target.bonus.append(GelEffect())
                target.bonus[-1].owner=target  
                target.iceturn=1 
                target.ready=False
                target.setValue()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : fprint( "pas d effet sur ",target.name)
class GelEffect(BonusMonstreWithLevel) :
    interest=-1
    def getCost(self,monster) :
        return -0.6-self.owner.iceturn*0.3-self.owner.att*0.1
    def afterInvocation(self,monster):
        monster.addMark("gel",size=(150,250),pos="center",typ="external",level=1,value=-1)
        self.owner = monster
    def beginTurn(self,monster):
        self.owner.ready=False
        self.owner.iceturn -= 1
        if self.owner.iceturn<1 :
            self.removed()
            self.owner.bonus.remove(self)
            #print "after classic remove on ",self.owner.name,self.owner.id,self.owner.bonus
    def removed(self) :
        #print "gel removed from ",self.owner.id,self.owner.bonus
        self.owner.removeMark("gel")
        self.owner.setValue()
        #delattr(self.owner,"iceturn") The attriute is kept, and reinitialised when the next Gel will come
                  
            

"""Sorts  ------------------------"""


class BouclierDivin(Spell.Spell) :
    positive = True
    negative = False
    def getCost(self) :
        return (-0.4+self.target.getCostMultiplier(self))
    def getStars(self):
        return 1
    def effect(self,origin,target):
        #print ("appel bouclier divin effect")
        if isinstance(target,Creature) and (not target.hasMark("bouclier_divin")) and (not target.hasMark("sarcophage")) :
            target.addMark("bouclier_divin",size=(160,230),pos="center",typ="external",value=2)
            target.bonus.append(BouclierDivinEffect())
            target.bonus[-1].owner=target
            target.setValue()
    def willAct(self,creature):        
        targets= self.target.getTarget(creature)
#        for mons in targets  :
#           if mons.max_pv >0 :
#               for i in mons.bonus :
#                   targets=i.modifySpellTarget(targets)
        return len(targets)!=0 and any([not (BouclierDivinEffect in [b.__class__ for b in cr.bonus]) for cr in targets])
class BouclierDivinEffect(BonusMonstre) :
    interest=1
    def getCost(self,monster) :
        return 3
    def modifyTakenDamage(self,damage):
        if damage>0:
            self.owner.removeMark("bouclier_divin")
            self.owner.bonus.remove(self)
        return 0
    def removed(self) :
        self.owner.removeMark("bouclier_divin")
        self.owner.setValue()
        
    def afterInvocation(self,monster):
        monster.addMark("bouclier_divin",size=(160,230),pos="center",typ="external",value=2)


class Assassinat(Spell.Spell) :
    positive = False
    negative = True
    def getCost(self) :
        self.level=5.2
        return self.level*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        #print "appel assassinat effect"
        if isinstance(target,Creature) and target.pv>0 :
            target.die()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : fprint( "pas d effet sur ",target.name)

class Sacrifice(Spell.Spell) :
    positive = False  # sur son armme obligatoirement
    negative=True
#    def getTarget(self,origin):
#        return "choose own"
    def getTarget(self,origin):
        #print "au choix : getTarget from",origin.name," de ",origin.player.name,origin.player
        return "choose"
    def getCost(self) :
        return 5*(2*self.target.getCostMultiplier(self)-1.)
    def effect(self,origin,target):
        fprint( "appel sacrifice effect")
        if isinstance(target,Creature) and target.pv>0 and target.player==origin.player :
            if any([b.__class__.__name__=="Errant" for b in target.bonus]) :
                ChangementDeCamp().effect(origin,target)
            else :
                target.is_dead=True # pour annuler rale d agonie qui pourrait etre une invocation
                target.die()
                for b in target.bonus : # il faut quand meme enlever les bonus
                    #print "removed ",b
                    b.removed()
        else :
            fprint( "target sacrifice refuse")
            if origin.pv >0 and isinstance(origin,Creature) and origin.is_dead==False :
                target=origin
            else :
                if all([m.is_dead for m in origin.player.army]) :
                    fprint("plus rien a sacrifier")
                    return
                target=[m for m in origin.player.army if m.is_dead==False][0]
            fprint( "ce sera ",target.name,target.id)
            target.is_dead=True # pour annuler rale d agonie qui pourrait etre une invocation
            target.die()
            for b in target.bonus : # il faut quand meme enlever les bonus
            #print "removed ",b
                b.removed()

class ChangementDeCamp(Spell.Spell) :
    positive = False
    negative = True
    def getCost(self) :
        return 11.*(-0.1+self.target.getCostMultiplier(self)+0.5*isinstance(self.target,Target.Armaguedon))
    def getStars(self):
        return 1
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0 and not any([b.__class__.__name__=="Incarnation" for b in target.bonus]) :
            #print ("cahnge camp",target.name)
            for b in reversed(target.bonus) :
                b.removed() # remove effect (bonus given to ...) but not bonus itself
            for m in target.player.adv.army :
                if m.pv>0 :
                  for b in m.bonus:
                    if not isinstance(b,Trigger):
                        b.enemyDeath(self)
            for m in target.player.army :
                if m.pv>0 :
                  if not m is target :
                    for b in m.bonus :
                        if not isinstance(b,Trigger):
                            b.otherDeath(target)
                        if hasattr(b,"removeOn") :
                            b.removeOn(target)
            if target in target.player.army :
                target.player.army.remove(target)
                
                target.player = target.player.adv
                target.player.army.append(target)

                for b in target.bonus :
                    b.afterInvocation(target) # removed effect appear again
                for m in target.player.army :
                    if m.pv>0 and m is not target :
                        for b in m.bonus :
                            b.additionalBonus(target)
                for e,i in enumerate(target.player.army):
                    i.index = e
                    i.takePlace(add=0)
                if len([m for m in target.player.army if m.pv>0])>9 :
                    target.player.sacrify()
                target.ready=False
                target.updateImage()
                target.takePlace()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : fprint( "pas d effet sur ",target.name)


class ReduitUnServiteurA1Vie(Spell.Spell) :
    positive = False
    negative = True
    def getCost(self) :
        self.level=3
        return self.level*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0 :
            target.sufferDamage(target.pv-1)
            target.pv = 1
            target.setValue()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : 
                fprint( "pas d effet sur ",target.name)
    
    def getSpellDescription(self):
        return "Reduit a 1 point de vie "
    
    
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
        return any([cr.pv>1 for cr in targets])


class Cataclysme(Spell.Spell) :
    positive = False
    has_target = False
    def getCost(self) :
        self.level=8.0
        return self.level
    def getTarget(self,origin):
        t=[m for m in origin.player.army if m.pv>0]+[m for m in origin.player.adv.army if m.pv>0]
        for m in t :
            if isinstance(m,Creature) and m.pv>0 and not any([b.__class__.__name__=="Incarnation" for b in m.bonus]):
                m.die()
        return None
    def effect(self,origin,target):
        pass
        #else :
        #    if hasattr(target,"name") and target.name : 
        #        print "pas d effet sur ",target.name,target
    def getDescription(self):
        return "Detruit tous les serviteurs"


    

class ReduitUnServiteurA1Att(Spell.Spell) :
    positive = False
    negative = True
    def getCost(self) :
        self.level=3
        return 2.6*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.att>1 and target.pv>0:
            target.addMark("bonus_mark_dam",size=(100,100),pos='sw',typ="number",level=1-target.att)            
            target.att = 1
            target.setValue()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : fprint( "pas d effet sur ",target.name)
    
    def getSpellDescription(self):
        return "Reduit a 1 d'attaque "

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
        return any([cr.att>1 for cr in targets])

class GuerisonTotale(Spell.Spell) :
    positive = True
    negative=False
    def getCost(self) :
        self.level=3.2
        return self.level*self.target.getCostMultiplier(self)
    def effect(self,origin,creature):
        creature.pv = creature.max_pv
        if hasattr(creature,"updateImage") :
            creature.updateImage()
        creature.setValue()
            
    def willAct(self,creature):    
        targets= self.target.getTarget(creature)
        for mons in targets  :
           if mons.max_pv >0 :
               for i in mons.bonus :
                   targets=i.modifySpellTarget(targets)
        return any([cr.max_pv-cr.pv>0 for cr in targets])



class EnlevePouvoirSpeciaux(Spell.Spell) :
    positive = False
    negative=False
    def getCost(self) :
        return 2.6*(-0.2+max(1.,self.target.getCostMultiplier(self)))
    def effect(self,origin,creature):
        if isinstance(creature,Creature) and creature.pv>0 and len(creature.bonus)>0 :
            affliction=None
            incarnation=None
            for b in reversed(creature.bonus) :
                b.removed()
                if b.__class__.__name__[0:9]=="NePeutPas" :
                    affliction=b
                if b.__class__.__name__=="Incarnation" :
                    incarnation=b
            #for k,m in reversed(creature.marks.items()) :
            #    if hasattr(m, '__getitem__') and m[3]=="power" :
            #        del creature.marks[k]
            creature.bonus=[]
            if affliction :
                creature.bonus.append(affliction)
            if incarnation :
                creature.bonus.append(incarnation)
            creature.addMark("cross",size=(300,400),pos="center",typ="",level=1,value=0)
            creature.setValue()
    def getDescription(self):
        return "Enleve tous les pouvoirs speciaux \n"+self.target.getDescription(True)

class GainMana(Spell.Spell) :
    positive = True
    negative=False
    has_target = False
    def getCost(self) :
        return 0.98       
    def getTarget(self,origin):
        #print "GainMana origin.player",origin.player
        return [origin.player]
    def effect(self,origin,target):
        target.mana+=2
        #origin.die()
        #else :
        #    if hasattr(target,"name") and target.name : 
        #        print "pas d effet sur ",target.name,target
    def getDescription(self):
        return "Augmente de 2 le Mana"

class Reinitialize(Spell.Spell) :
    positive = True
    has_target = True
    def getCost(self) :
        return 3.2     
    def effect(self,origin,target):
        if target.pv>0 and hasattr(target,"card") :
            import copy
            #print "reinit transforme en ",target.card.name
            Transformation(copy.copy(target.card)).effect(origin,target)
            target.ready=False
        #else :
        #    if hasattr(target,"name") and target.name : 
        #        print "pas d effet sur ",target.name,target
    def getDescription(self):
        if self.target.__class__.__name__ != "Personnel":
            return "Fait devenir "+self.target.getDescription()+" comme initialement"
        else:
            return "Redevient comme initialement"


# ---------------------
#from Invocation import Invocation
#possibleAsSpell.append(Invocation)

# ---------------------

#list_bonus=[p.__name__ for p in possibleAsBonus if not p.isTrigger ] # liste comme texte pour menus
#nbPossibleBonus=len(list_bonus) # pour separator
#list_bonus+=[p.__name__ for p in possibleAsBonus if p.isTrigger ]
#list_spell=[s.__name__ for s in listMultiplier]+[s.__name__ for s in possibleAsSpell] # liste comme texte pour menus
#nbMultiplier=len(listMultiplier)

