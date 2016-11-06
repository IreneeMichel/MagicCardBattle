
from Spell import Spell,Multiplier,SpellWithLevel,Invocation,SpellWithTwoLevels,Transformation,ConfereBonus
#from Invocation import Invocation,Transformation
from Bonus import BonusMonstre,BonusMonstreWithLevel,BonusMonstreWithTwoLevels
from Bonus import Trigger,BonusMonstreGivingBonus
#import pygame
from Sprites import Sprite
#from Target import Target
from Creature import Creature,AnimatedCreature
from copy import copy
#from Spell import possibleAsSpell,listMultiplier  # list of spells to be completed
#from Bonus import possibleAsBonus  # list of bonus or trigger to be completed
#possibleAsSpell=[]
#listMultiplier=[]
#possibleAsBonus=[]
from types import FunctionType,MethodType
from functools import partial
import random

class Invocation(Invocation):
    pass

"""
class InvocationAleatoireDUnType(InvocationAleatoireDUnType):
    pass
"""
class Transformation(Transformation):
    pass

class ConfereBonus(ConfereBonus):
    pass

class AuChoix(Multiplier) :
    # les spell n ont pas de owner, sinon cela pose pb dans les creaturecopy
    def getCost(self) :
        return 0.2+max(self.spell1.spell.getCost(),self.spell2.spell.getCost())+min(self.spell1.spell.getCost(),self.spell2.spell.getCost())*0.2
    def getDescription(self) :
        return 'Choix :\n '+ self.spell1.spell.getDescription()+ "\n ou \n" + self.spell2.spell.getDescription()
    def effect(self,origin,target):
        # print "au choix : effect de auchoix sur ",target.name
        for m in reversed(origin.player.army) :
            if m.name=="choix1" or m.name=="choix2" :
                #print m.name,"de",m.player.name," die "
                m.die()
        if target.name=="choix1":
            # print "choix 1:",self.spell1.spell
            origin.player.launch(origin,self.spell1.spell)
        elif target.name=="choix2" :
            #print "choix 2:",self.spell2.spell
            origin.player.launch(origin,self.spell2.spell)
        else :
            print "erreur dans auchoix"
            #print "choix",target.name
            from Player import Computer0
            if not isinstance(origin.player,Computer0) :
                origin.player.launch(origin,self) # on relaisse le choix

            #self.choix1.kill()
            #self.choix2.kill()
        #self.spell2.spell.effect(target)
    def getTarget(self,origin):
        #print "au choix : getTarget from",origin.name," de ",origin.player.name,origin.player
        if not any([m.name=="choix1" for m in origin.player.army]) :
            #print "creation du choix , nest pas dans",[m.name for m in origin.player.army],'de',origin.player
            import pygame
            from Card import Card
            from Player import Computer0
            card1=Card("choix1",1,1) # faire des cartes avec un nom, seule solution pour retenir quel choix fait quoi
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
                pygame.draw.rect(card1.image,(60,60,100), (20,300,338,235))
                card1.image.blit(text,(15,400))
                b=AnimatedCreature(origin,card1,origin.player,3)
                b.is_invocation=True
                b.pv=0
                text = font.render(self.spell2.spell.getDescription(),False,(0,0,0))
                pygame.draw.rect(card2.image,(60,60,100), (20,300,338,240))
                card2.image.blit(text,(15,400))
                b=AnimatedCreature(origin,card2,origin.player,4)
                b.is_invocation=True
                b.pv=0
                if isinstance(origin.player,Computer0) :
                    # il faut que les cartes soient danss l armee avant la suite
                    while origin.player.game.all_animations :
                            for a in reversed(origin.player.game.all_animations):
                                a.animate()
            else :
                #print "in gettarget : not animated"
                b=Creature(origin,card1,origin.player)
                b.pv=0
                b.is_invocation=True
                b=Creature(origin,card2,origin.player)
                b.pv=0
                b.is_invocation=True
        return "choose"
    def modifySpellTargetChoice(self,targets) :
        if any([m.name=="choix1" for m in targets]) :
            targets=[m for m in targets if m.name=="choix1" or m.name=="choix2" ]
            #print "self is removed from targets"
        return targets
    def getInlineDescription(self):
        return "choix de sort"

class DeuxEffets(Multiplier):
    def getCost(self) :
        return 0.2+self.spell1.spell.getCost()+self.spell2.spell.getCost()
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
        origin.player.launch(origin,self.spell1.spell)
        #print "deuxieme",self.spell2.spell
        origin.player.launch(origin,self.spell2.spell)
        #return self.spell2.spell.getTarget(origin)
        return None
    def getInlineDescription(self):
        return self.spell1.spell.getInlineDescription()
"""

class DeuxEffetsMemeCible(DeuxEffets):
    pass
"""

""" Bonus permanents ------------------------------------"""
class Provocation(BonusMonstre) :
    def getCost(self,monster) :
        return 0.5+monster.att*0.09+monster.pv*0.09       
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
    def getCost(self,monster) :
        return monster.att*0.6
    def getStars(self):
        return 1    
    def modifyAttackChoice(self,targets) :
        t=[]
        for c in self.owner.player.army :
            if c.pv>0 :
                t.append(c)
        t.append(self.owner.player.adv)
        for c in self.owner.player.adv.army :
            if c.pv>0 :
                t.append(c)
        return t

class Inciblable(BonusMonstre) :
    def getCost(self,monster) :
        return 0.6+monster.att/6.+monster.pv/6.
    def getStars(self):
        return 1
    def modifySpellTargetChoice(self,targets) :
        if self.owner in targets and not any([(b.__class__.__name__=="Insaisissable") for b in self.owner.bonus]) :
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets


class Insaisissable(BonusMonstre) :
    def getCost(self,monster) :
        return 1.3+monster.att/5.+monster.pv/5.
    def getStars(self):
        return 1
    def modifyDefenseChoice(self,targets) :
        if self.owner in targets : # is not if another has provocation
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets

class AttaqueADistance(BonusMonstre) :
    def beforeCombat(self,monster,other) :
        if monster is self.owner :
            olddef=other.defend
            oldafter=other.afterCombat
            def modifdef(monsterself,target) :
            #print " defend de ",other.name," modifiee"
                pass
            def modifafter(monsterself,target) :
                #print " apres combat de ",other.name," modifiee par attack a distance"
                monsterself.defend=olddef
                monsterself.afterCombat=oldafter
                oldafter(target)
            other.defend=MethodType(modifdef,other)
            other.afterCombat=MethodType(modifafter,other)
    def attackAnimationSprite(self,sprite):
        return Sprite(sprite,"gameAnimationImages/stone.png",[50,40]) 
    def getCost(self,monster) :
        return monster.att * 0.4 +0.1
    def getStars(self):
        return 1
        
   
class Furie(BonusMonstre):
    def getCost(self,monster) :
        return 0.2+monster.att/6. + monster.pv/8.
    def getStars(self):
        return 1
    def beforeCombat(self,monster,target) :
        if monster is self.owner and monster.n_attack<1. :
            monster.n_attack += 1
            monster.ready=True
    def afterInvocation(self,monster) :
        monster.n_attack = 0
    def endturn(self,monster):
        monster.n_attack = 0

class Initiative(BonusMonstre) :
    def getCost(self,monster) :
        return monster.att*0.45-0.1
    def getStars(self):
        return 1
    def beforeCombat(self,adv1,adv2) :
        monster=self.owner
        other=[adv1,adv2][adv1 is self.owner]
        if adv1 is self.owner :
            monster
        if all([(b.__class__.__name__!="Initiative") for b in other.bonus]):
            #print "before combat de Initiative"
            oldseq=FunctionType(other.combatSequence.func_code,globals(),closure=other.combatSequence.func_closure)
            oldatt= FunctionType(other.attack.func_code,globals(),closure=other.attack.func_closure)
            oldafter=FunctionType(other.afterCombat.func_code,globals(),closure=other.afterCombat.func_closure)
            def modifseq(monsterself,target) :
                #print" modif sequence"
                target.defend(monsterself)
                monsterself.attack(monster)
            def modifatt(monsterself,target) :
                #print " attack de ",other.name," modifiee"
                if monsterself.pv > 0 :
                    MethodType(oldatt,monsterself)(target)
            def modifafter(monsterself,target) :
                #print " apres combat de ",other.name," modifiee"
                monsterself.attack=MethodType(oldatt,monsterself)
                monsterself.combatSequence=MethodType(oldseq,monsterself)
                monsterself.afterCombat=MethodType(oldafter,monsterself)
                monsterself.afterCombat(target)
            other.attack=MethodType(modifatt,other)
            other.combatSequence=MethodType(modifseq,other)
            other.afterCombat=MethodType(modifafter,other)
    
class CoutReduit(BonusMonstre) :
    def getCost(self,monster) :
        co=[m.getCost(monster)+(m.getStars()>0)*1.5 for m in monster.bonus if m is not self]
        co=[c*0.3+0.1 for c in co if c>0]
        return -sum(co)-max(0.4,monster.att/12.+monster.pv/12.)
    def getStars(self):
        return 1
    def getDescription(self):
        return "cout reduit"
    def afterInvocation(self,monster) :    # ameliore l evaluation par l ordi de la valeur de la creature
        monster.bonus.remove(self)
        monster.starcost-=1


class Charge(BonusMonstre) :
    def getCost(self,monster) :
        return 0.45+monster.att/3.
    def afterInvocation(self,monster) :
        if monster.card :
            monster.ready=True

class NePeutPasAttaquer(BonusMonstre) :
    def getCost(self,monster) :                                                                          
        return -monster.att/4.2-0.2  
    def modifyAttackChoice(self,targets):
        if self.owner in targets  :
            return [self.owner]
        else :
            return []

class NePeutPasRiposter(BonusMonstre) :
    def getCost(self,monster) :                                                                          
        return -monster.att/4.5+0.1
    def afterInvocation(self,monster):
        def defend(oneself,enemy):
		pass
        monster.defend = MethodType(defend,monster)

#class Protecteur(BonusMonstre) :
#    def getCost(self,monster) :
#        return 100.5+monster.att/8+monster.pv/8.

class Camouflage(BonusMonstre) :
    """
    def __init__:
        has_attacked=False
        """
    def getCost(self,monster) :
    
        return 0.8+monster.att/8.+monster.pv/10.
    def getStars(self):
        return 0
    def afterInvocation(self,monster) :
        monster.hidden = True
        monster.addMark("camouflage_feuilles",pos="center",size=(150,200))
        old_bt = FunctionType(monster.beginTurn.func_code,globals(),closure=monster.beginTurn.func_closure)
        def bt(oneself):
            for b in oneself.bonus :
                if b.__class__.__name__=="Camouflage" : # class Camouflage can be "not defined" ?!
                    b.removed()
                    oneself.bonus.remove(b)
                    break
            oneself.beginTurn =  MethodType(old_bt,oneself)
            oneself.beginTurn()                    
            #print "         creature",target,target.name,"de",target.player.name,"  gains gel",self           
        monster.beginTurn = MethodType(bt,monster)
    def modifyDefenseChoice(self,targets) :
        if self.owner in targets and hasattr(self.owner,'hidden') and self.owner.hidden: # is not if another has provocation
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets
    def afterCombat(self,monster,target):
        if monster.hidden :
            self.removed()
    def modifySpellTargetChoice(self,targets) :
        if self.owner in targets and hasattr(self.owner,'hidden') and self.owner.hidden : # is not if another has provocation
            targets.remove(self.owner)
            #print "self is removed from targets"
        return targets
    def removed(self) :
        #print "remove camouflage"
        self.owner.hidden = False
        self.owner.removeMark("camouflage_feuilles")
        

""" Bonus permanents avec niveaux ------------------------- """

class CoutDesSortsReduit(BonusMonstreWithLevel) :
    def getCost(self,monster) :
        return monster.att/10. + monster.pv/8. + 0.9*self.level
    def modifyManaCost(self,card,cost):
        if card.pv == 0 :
            return max(0,cost - self.level)
        else:
            return cost

class CoutDesMonstresReduit(BonusMonstreWithLevel) :
    def getCost(self,monster) :
        return monster.att/8. + monster.pv/8. + 1.3*self.level
    def modifyManaCost(self,card,cost):
        if card.pv >0 :
            return max(0,cost - self.level)
        else:
            return cost

#class DegatDesSortsAugmentes(BonusMonstreWithLevel) :
#    def getCost(self,monster) :
#        return monster.att/8. + monster.pv/8. + 2*self.level

class LienDeVie(BonusMonstreWithLevel) :
    def getCost(self,monster) :
        return 0.4 + 0.5*self.level
    def getStars(self):
            return 1
    def afterInvocation(self,creature):
        creature.ancientSufferDamage = creature.sufferDamage
        def newSufferDamage(monsterself,damage):
            if damage <= self.level:
                monsterself.player.sufferDamage(damage)
            elif damage-self.level>=monsterself.pv:
                monsterself.ancientSufferDamage(damage)
            else:
                monsterself.player.sufferDamage(self.level)
                monsterself.ancientSufferDamage(damage-self.level)
        creature.sufferDamage = MethodType(newSufferDamage,creature)
    def removed(self) :
        self.owner.sufferDamage=MethodType(Creature.sufferDamage,self.owner)   
            

class GardienDeVie(BonusMonstre) :
    def getCost(self,monster) :
        return 0.2 + monster.pv/12. + monster.att/8.
    def modifyPlayerSuffer(self,player,damage):
        if damage==0 :
            return 0
        if self.owner.pv > damage:
            self.owner.sufferDamage(damage)
            return 0
        else:
            pv = self.owner.pv
            self.owner.sufferDamage(pv)
            return damage - pv

class DonneBonus(BonusMonstreWithTwoLevels) :
    def getCost(self,monster) :
        return self.level2*1.0 + self.level*1.3 + monster.pv/8. 
    def getDescription(self):
        return "Donne a tous les allies +"+str(self.level)+"/+"+str(self.level2)
    def afterInvocation(self,creature):
        for m in self.owner.player.army :
            if not m is self.owner and m.pv>0 :
                self.additionalBonus(m)
    def removed(self) :
        #print "tite verif ", creature," should be ",self.owner
        for target in reversed(self.owner.player.army) :
            if target.pv>0 :
                self.removeOn(target)
    def removeOn(self,target) :
        if not target is self.owner and target.pv>0 :
            target.max_pv -= self.level2
            target.att -= self.level
            if target.att<0 :
                target.att=0
            if self.level2 :
                target.removeMark("bonus_mark_pv",self.level2)
            if self.level :
                target.removeMark("bonus_mark_dam",self.level)        
            target.pv -= self.level2
            if target.pv <1 :
                target.die()
    def death(self,creature) :
        self.removed()
    def additionalBonus(self,target):
        target.pv += self.level2
        target.max_pv += self.level2
        target.att += self.level
        if self.level2 :
            target.addMark("bonus_mark_pv",typ="number",level=self.level2,size=(100,100),pos="se")
        if self.level :
            target.addMark("bonus_mark_dam",size=(100,100),typ="number",level=self.level,pos="sw")

#def removed(self):
#        for m in self.owner.player.army :
#            for p in m.bonus :
#                if hasattr(p,origin) and (p.origin is self) :
#                    m.bonus.remove(p)

class BonusParAllies(BonusMonstreWithTwoLevels) :
    def getCost(self,monster) :
        return self.level*1.6  + self.level2*1.4
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
    def getCost(self,monster) :
        return self.level*1.6 + self.level2*1.4
    def getStars(self):
        return 1
    def getDescription(self):
        return "A +"+str(self.level)+"/+"+str(self.level2) +" par enemis"
    def afterInvocation(self,target):
        n=len([m for m in target.player.adv.army if m.max_pv>0 and not m.is_dead])
        target.pv += self.level2*n
        target.max_pv += self.level2*n
        target.att += self.level*n      
        if self.level2 :
            #print "dans bonus par enemi addMark"
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
    def getCost(self,monster) :
        return 0.3+self.level*0.7 + monster.pv/12. + monster.att/12.
    def getDescription(self):
        return "Donne {0} point".format(self.level)+"s"*(self.level>1)+" d'armure au hero"
    def modifyPlayerSuffer(self,player,damage):
        if damage<self.level:
            return 0
        else:
            return damage-self.level
    
    def getStars(self):
        return 0

#class DonneAttaqueAuHero(BonusMonstreWithLevel) :
#    def getCost(self,monster) :
#        return self.level + monster.pv/6. + monster.att/6.
#    def getDescription(self):
#        return "Donne {0} point d'attaque au hero".format(self.level)

#class MalusAttaque(BonusMonstreWithLevel) :
#    def getCost(self,monster) :
#        if monster.att >= self.level:
#            return -self.level*0.25
#        else:
#            return - monster.att*0.25
#
#class MalusRiposte(BonusMonstreWithLevel) :
#    def getCost(self,monster) :
#        if monster.att >= self.level:
#            return -self.level*0.25
#        else:
#            return - monster.att*0.25

#class BonusContre1Type(BonusMonstreWithLevel) :
#    def getCost(self,monster) :
#        return self.level*0.25

""" Donne capacites a tous les allies  ----------------- """
                                       
class DonneCapacitesAuxAllies(BonusMonstreGivingBonus) :
    def getCost(self,monster) :
        from Card import troll
        return max(0.2-self.spell.getCost(troll),self.spell.getCost(troll))*3. + 0.8
    def getStars(self):
        return self.spell.getStars() + 1
    def getDescription(self):
        return "Donne a tous les allies "+self.restriction+":"+("\n"*bool(self.restriction))+self.spell.getDescription()
    def afterInvocation(self,creature):
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
                    target.bonus.remove(b)
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
    def getCost(self,monster) :
        return 0.4+self.spell.getCost()
    def afterInvocation(self,creature):
        creature.player.launch(creature,self.spell)
        if self in creature.bonus :
            creature.bonus.remove(self) # ameliore l evaluation par l ordi de la valeur de la creature 
        creature.starcost-=self.spell.getStars()

class ChaqueTour(Trigger) :
    def getCost(self,monster) :
        return self.spell.getCost()*1.6-0.2
    def getStars(self):
        return 1 + self.spell.getStars()
    def endturn(self,creature) :
        creature.player.launch(creature,self.spell)

class AvecAttaque(Trigger):
    def getCost(self,monster) :
        return self.spell.getCost()*1.4+0.1
    def getStars(self):
        return self.spell.getStars()
    def afterInvocation(self,creature):
        self.old_att = FunctionType(creature.combatSequence.func_code,globals(),closure=creature.combatSequence.func_closure)
        def new_att(oneself,target):
            MethodType(self.old_att,oneself)(target)
            oneself.attacked_target=target
            oneself.player.launch(oneself,self.spell)
        def getTarget(oneself,crea) :
            return  [crea.attacked_target]
        from Target import UneCibleAuChoix
        if isinstance(self.spell.target,UneCibleAuChoix) :
            self.spell.getTarget=MethodType(getTarget,self.spell)
        creature.combatSequence = MethodType(new_att,creature)
    def removed(self) :
        self.owner.combatSequence = MethodType(self.old_att,self.owner)

class ALaPlaceDeLAttaque(Trigger):
    def getCost(self,monster) :
        comp=sum([1 for b in monster.bonus if isinstance(b,Charge) or isinstance(b,Furie)])
        return self.spell.getCost()*1.5*(1.+comp*0.3)+0.4
    def getStars(self):
        return self.spell.getStars()
    def beforeCombat(self,owner,target):
        #print "appel before combat",owner.name,target.name
        if target is owner :
            #print "before combat ->spell"
            old_att = FunctionType(owner.combatSequence.func_code,globals(),closure=owner.combatSequence.func_closure)
            def new_combatSeq(oneself,thesame):
                oneself.player.launch(oneself,self.spell)
                oneself.combatSequence = MethodType(old_att,oneself)
                #print "launch a la place de combat"
            owner.combatSequence = MethodType(new_combatSeq,owner)

    def modifyAttackChoice(self,targets) :
        #print "attack choice =owner ( a la place de attaque)"
        if self.owner.att==0 :
            targets=[]
        if self.owner not in targets :
            targets.append(self.owner)
        return targets
        
class QuandIlTue(Trigger):
    def getCost(self,monster) :
        return self.spell.getCost()*1.1+0.2
    def getStars(self):
        return self.spell.getStars()
    def afterInvocation(self,creature):
        self.old_att = FunctionType(creature.attack.func_code,globals(),closure=creature.combatSequence.func_closure)
        def new_att(oneself,target):
            MethodType(self.old_att,oneself)(target)
            if hasattr(target,"is_dead") and target.is_dead and not (hasattr(target,"is_invocation") and target.is_invocation and target.player==self.owner) :
            	oneself.player.launch(oneself,self.spell)
        creature.attack = MethodType(new_att,creature)
    def removed(self) :
        self.owner.attack = MethodType(self.old_att,self.owner)

class QuandUnAllieEstTue(Trigger):
    def getCost(self,monster) :        
        return self.spell.getCost()*1.3+0.5
    def getStars(self):
        return 1 + self.spell.getStars()
    def otherDeath(self,creature) :
        if not hasattr(creature,"is_invocation") or not creature.is_invocation :
            self.owner.player.launch(self.owner,self.spell)


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
    def getCost(self,monster) :
        return self.spell.getCost()*1.6
    def getStars(self):
        return 1 + self.spell.getStars()
    def afterInvocation(self,creature):
        old_suff = FunctionType(creature.sufferDamage.func_code,globals(),closure=creature.sufferDamage.func_closure)
        def new_suff(oneself,damage):
            MethodType(old_suff,oneself)(damage)
            if oneself.pv < 1:
                oneself.sufferDamage = MethodType(old_suff,oneself)
            if damage>0:
                adv=self.owner.player.adv
                status=[(m.name,m.ready) for m in adv.army]+[(m.name,m.ready) for m in self.owner.player.army]
                if status!=self.owner.memory :
                    self.owner.memory=status
                    oneself.player.launch(oneself,self.spell)
                #elif "-simu" not in self.owner.player.name :
                #    print "QuandIlEstBlesse unactive because game did not move"
        creature.sufferDamage = MethodType(new_suff,creature)
        self.owner.memory=None
    def removed(self) :
        self.owner.sufferDamage = MethodType(Creature.sufferDamage,self.owner)
    def endturn(self,creature) :
        self.owner.memory=None

class QuandLAdvLanceUnSort(Trigger):
    def getCost(self,monster) :
        return 0.2 + self.spell.getCost()*0.6
    def getStars(self):
        return 1 + self.spell.getStars()
    def getDescription(self):
        return "Chaque fois que l ennemi lance un sort: \n"+self.spell.getDescription()
    def otherSpellLaunched(self,one_spell):
        self.owner.player.launch(self.owner,self.spell)
        
class QuandVousLancezUnSort(Trigger):
    def getCost(self,monster) :
        return 0.2 + self.spell.getCost()*0.8
    def getStars(self):
        return 1 + self.spell.getStars()
    def getDescription(self):
        return "A chaque fois que vous lancez un sort: \n"+self.spell.getDescription()
    def spellLaunched(self,one_spell):
        #print " spell launched en plus (bonus de ",self.owner.name,") player=",self.owner.player.name
        self.spell.owner=self.owner
        self.owner.player.launch(self.owner,self.spell)

class QuandLAdvInvoqueUnMonstre(Trigger):
    def getCost(self,monster) :
        return 0.4 + self.spell.getCost()*1.
    def getStars(self):
        return 1 + self.spell.getStars()
    def getDescription(self):
        return "A chaque nouvel ennemi: \n"+self.spell.getDescription()
    def otherMonsterCreation(self,one_spell):
        self.spell.owner=self.owner
        self.owner.player.launch(self.owner,self.spell)

class RaleDAgonie(Trigger) :
    def getCost(self,monster) :
        cost = self.spell.getCost()
        if cost > monster.att/2. + monster.pv/2.:
            self.stars = 1
        else:
            self.stars = 0
        return 0.3 + cost*0.7
    def getStars(self):
        return self.stars + self.spell.getStars()
    def death(self,creature):
        #print "activation rale d agonie"
        creature.player.launch(creature,self.spell)

""" Sorts avec niveaux  -----------------"""

class Degat(SpellWithLevel) :
    positive = False
    def getCost(self) :
        return self.level*0.95*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        #print "degat effect"
        target.sufferDamage(self.level)


class Bonus(SpellWithTwoLevels) :
    positive = True
    def getCost(self) :
       return (self.level*1.25+self.level2*1.)*(0.35+self.target.getCostMultiplier(self))
    def getDescription(self):
        if self.target.__class__.__name__ == "Personnel":
            return "Gagne +{0}/+{1}".format(self.level,self.level2)
        else:
            return "Donne +{0}/+{1} ".format(self.level,self.level2)+self.target.getDescription()
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0 :
            target.pv += self.level2
            target.max_pv += self.level2
            target.att += self.level
            target.addMark("bonus_mark_pv",size=(100,100),pos="se",typ="number",level=self.level2)
            target.addMark("bonus_mark_dam",size=(100,100),pos='sw',typ="number",level=self.level)


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
        return self.level*1.9-1.5        
    def getSpellDescription(self):
        return "Piochez {0} carte".format(self.level)+"s"*(self.level>1)
    def getStars(self):
        return 1
    def getTarget(self,creature) :
        return  [creature.player]
    def effect(self,origin,player):
        player.drawCard(n=self.level)

class CopieMain(Spell) :
    positive = True # false is default
    has_target = True
    def getCost(self) :
        return 0.2+2.*self.target.getCostMultiplier(self)*(1.+(self.target.getCostMultiplier(self)==2))
    def getStars(self):
        return 2
    def effect(self,origin,creature):
        # print "activation of CopieMain"
        if isinstance(creature,Creature) and creature.max_pv>0 :
            origin.player.deck=[creature.card]+origin.player.deck
            origin.player.drawCard(1)
    def getDescription(self):
        return "Place une copie dans \n votre main "+self.target.getDescription(False)

class CopieInvoque(Spell) :
    positive = True # false is default
    has_target = True
    def getCost(self) :
        return 0.1+6.*self.target.getCostMultiplier(self)*(1.+(self.target.getCostMultiplier(self)==2))
    def getStars(self):
        return 2
    def effect(self,origin,creature):
        if isinstance(creature,Creature) and creature.card.pv >0:
            card2=copy(creature.card)
            card2.bonus=[b for b in card2.bonus if b.__class__.__name__!="CriDeGuerre"]
            if isinstance(creature,AnimatedCreature)  :
                b=AnimatedCreature(origin,card2,origin.player)
            else :
                b=Creature(origin,card2,origin.player)
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
    def getCost(self) :
        return self.level*0.5*self.target.getCostMultiplier(self)
    def effect(self,origin,creature):
        creature.pv = min(creature.pv+self.level,creature.max_pv)
        if hasattr(creature,"updateImage") :
            creature.updateImage()
        if hasattr(creature,"icon") : #Hero
            creature.icon.update()

class GuerisonHeros(SpellWithLevel):
    has_target = False
    def getCost(self) :
        return self.level*0.45
    def getTarget(self,creature) :
        return  [creature.player]
    def effect(self,origin,creature):
        creature.pv = min(creature.pv+self.level,creature.max_pv)
        if hasattr(creature,"icon") :
            creature.icon.update()
    def getDescription(self):
        return ("Guerit le hero de {0} point"+"s"*(self.level>1)+" de vie").format(self.level)

class FaireDefausser(SpellWithLevel) :
    has_target = False
    def getCost(self) :
        return 0.3 + self.level*2.3    
    def getDescription(self):
        return ("Fait defausser {0} carte"+"s"*(self.level>1)+" \n au hero adverse").format(self.level)
    def getTarget(self,creature) :
        return  [creature.player.adv]
    def effect(self,origin,creature):
        # creature is the adv player
        # print creature
        from Sprites import Animation
        if len(creature.hand)>self.level :
            ca=random.sample(creature.hand, self.level)
        else :
            ca=creature.hand
        for c in ca :
            if hasattr(creature,"icon") :
                c.show()
                destination=origin.getPosition()
                effect=partial(creature.hand.remove,c)
                phase0 = (destination,10, [2,20],effect)
                Animation(c,[phase0])
            else :
                creature.hand.remove(c)

"""Sorts  ------------------------"""


class BouclierDivin(Spell) :
    positive = True
    def getCost(self) :
        return (-0.4+self.target.getCostMultiplier(self))
    def getStars(self):
        return 1
    def effect(self,origin,target):
        #print "appel bouclier divin effect"
        if isinstance(target,Creature) and (not target.hasMark("bouclier_divin")) and (not target.hasMark("sarcophage")) and target.pv>0 :
            target.addMark("bouclier_divin",size=(160,230),pos="center",typ="external",value=2)
            old_bt = FunctionType(target.sufferDamage.func_code,globals(),closure=target.sufferDamage.func_closure)
            def sd(oneself,damages):
#                if "-simu" not in oneself.player.name :
#                    print "defense modif par bouclier divin",damages
                if damages>0 :
                    #print "destroyind the D Shield",self," of ",oneself,oneself.name,"de",oneself.player.name
                    oneself.removeMark("bouclier_divin")
                    oneself.sufferDamage = MethodType(old_bt,oneself)
            target.sufferDamage = MethodType(sd,target)
            #print "   creating divine Shield ",self,"for ",target,target.name,"de",target.player.name
        else :
			pass
            #from Player import Computer0 
            #if (not isinstance(target.player,Computer0)) : print "pas d effet sur ",target.name


class Assassinat(Spell) :
    positive = False
    def getCost(self) :
        self.level=5
        return self.level*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        #print "appel assassinat effect"
        if isinstance(target,Creature) and target.pv>0 :
            target.die()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : print "pas d effet sur ",target.name

class Sacrifice(Spell) :
    positive = -1  # sur son armme obligatoirement
#    def getTarget(self,origin):
#        return "choose own"
    def getCost(self) :
        return 5*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        #print "appel assassinat effect"
        if isinstance(target,Creature) and target.pv>0 and target.player==origin.player :
            target.is_dead=True # pour annuler rale d agonie qui pourrait etre une invocation
            target.die()
            for b in target.bonus : # il faut quand meme enlever les bonus
                #print "removed ",b
                b.removed()
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : print "pas d effet sur ",target.name

class ChangementDeCamp(Spell) :
    positive = False
    def getCost(self) :
        self.level=10
        return self.level*self.target.getCostMultiplier(self)
    def getStars(self):
        return 1
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0 :
            
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
                    if b.__class__.__name__!="CriDeGuerre" :
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
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : print "pas d effet sur ",target.name


class ReduitUnServiteurA1Vie(Spell) :
    positive = False
    def getCost(self) :
        self.level=3
        return self.level*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0 :
            min=target.max_pv-target.card.pv+1
            target.sufferDamageAnimation(target.pv-min)
            target.pv = min
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : 
                print "pas d effet sur ",target.name
    
    def getSpellDescription(self):
        return "Reduit a 1 point de vie "


class Cataclysme(Spell) :
    positive = False
    has_target = False
    def getCost(self) :
        self.level=8.5
        return self.level
    def getTarget(self,origin):
        t=[m for m in origin.player.army if m.pv>0]+[m for m in origin.player.adv.army if m.pv>0]
        return t
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.pv>0 :
            target.die()
        #else :
        #    if hasattr(target,"name") and target.name : 
        #        print "pas d effet sur ",target.name,target
    def getDescription(self):
        return "Detruit tous les serviteurs"


    

class ReduitUnServiteurA1Att(Spell) :
    positive = False
    def getCost(self) :
        self.level=3
        return 2.8*self.target.getCostMultiplier(self)
    def effect(self,origin,target):
        if isinstance(target,Creature) and target.att>1 and target.pv>0:
            target.addMark("bonus_mark_dam",size=(100,100),pos='sw',typ="number",level=1-target.att)            
            target.att = 1
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : print "pas d effet sur ",target.name
    
    def getSpellDescription(self):
        return "Reduit a 1 d'attaque "


class Gel(Spell) :
    positive = False
    def getCost(self) :
        self.level=1.4
        return self.level*(self.target.getCostMultiplier(self)-0.3)
    def effect(self,origin,target):
        #print "appel gel effect"
        if isinstance(target,Creature) and target.pv>0 :
            if hasattr(target,"iceturn") :
                target.iceturn+=1
            else :
                target.addMark("gel",size=(150,250),pos="center",typ="external",level=1,value=-1)
                
                old_bt = FunctionType(target.beginTurn.func_code,globals(),closure=target.beginTurn.func_closure)
                def bt(oneself):
                    oneself.iceturn -= 1
                    if oneself.iceturn>= 1:
                        #print "         creature",oneself,oneself.name,"de",oneself.player.name,"  looses gel",self                    
                        MethodType(old_bt,oneself)()
                        oneself.ready = False
                    else:
                        #print "         creature",oneself,oneself.name,"de",oneself.player.name,"  looses gel effect",self
                        oneself.removeMark("gel")
                        oneself.beginTurn =  MethodType(old_bt,oneself)
                        delattr(oneself,"iceturn")
                        oneself.beginTurn()
                        
                #print "         creature",target,target.name,"de",target.player.name,"  gains gel",self           
                target.beginTurn = MethodType(bt,target)
                target.iceturn = 2
                target.ready=False
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : print "pas d effet sur ",target.name


class GuerisonTotale(Spell) :
    positive = True
    def getCost(self) :
        self.level=2.8
        return self.level*self.target.getCostMultiplier(self)
    def effect(self,origin,creature):
        creature.pv = creature.max_pv
        if hasattr(creature,"updateImage") :
            creature.updateImage()

class Sarcophage(SpellWithLevel) :
    positive = False
    def getCost(self) :
        return (1.6+self.level*0.5)*self.target.getCostMultiplier(self)
#    def Effect(self) :
    def effect(self,origin,target):
        #if isinstance(target,AnimatedCreature) : print "appel sarco effect"
        if isinstance(target,Creature) and target.pv>0:
            if hasattr(target,"sarcoturn") :
                target.sarcoturn = max(target.sarcoturn,self.level)
                return
            #print "sarco sur",target.name
            #if isinstance(target,AnimatedCreature) : print "sarco sur",target.name
            target.addMark("sarcophage",size=(200,280),pos="center",typ="external",level=1,value=-2)            
            old_sd = FunctionType(target.sufferDamage.func_code,globals(),closure=target.sufferDamage.func_closure)
            def sd(oneself,damages):
                #Don't react
                oneself.sarcoturn-=damages
                if oneself.sarcoturn <= 0:
                    #print "fin sarcophage",oneself.name
                    del oneself.sarcoturn
                    oneself.removeMark("sarcophage")
                    #print "destroyind the D Shield",self," of ",oneself,oneself.name,"de",oneself.player.name
                    oneself.sufferDamage = MethodType(old_sd,oneself)
                    for i,b in enumerate(oneself.bonus) :
                        b.modifyDefenseChoice=MethodType(b.__class__.modifyDefenseChoice,b)
                        #print " apres combat de ",other.name," modifiee"
                    for b in reversed(oneself.bonus) :
                        if b.__class__.__name__=="NePeutPasAttaquer" :
                            oneself.bonus.remove(b)
                            break                   
                        #print selfsarco.name,"retrouve bien sa riposte"
            target.sufferDamage = MethodType(sd,target)
            def doNothing(monsterself,oponent) :
                #if isinstance(monsterself,AnimatedCreature) : print "pas de defense en sarcophage"
                pass
            def modifbefore(bonusself,oponent,oneself) :
                #if isinstance(oneself,AnimatedCreature) : print "sarco modifbefore : pas de riposte pour",oneself," attaque par",oponent
                old_def=FunctionType(oneself.defend.func_code,globals(),closure=oneself.defend.func_closure)
                oneself.defend=MethodType(doNothing,oneself)
                oldafter=FunctionType(oneself.afterCombat.func_code,globals(),closure=oneself.afterCombat.func_closure)
                def modifafter(selfsarco,other) :
                        #if isinstance(other,AnimatedCreature) : print selfsarco,"retrouve bien sa riposte apres"
                        selfsarco.defend=MethodType(old_def,selfsarco)
                        selfsarco.afterCombat=MethodType(oldafter,selfsarco)
                oneself.afterCombat=MethodType(modifafter,oneself)                    
            def doNotModifyTarget(monsterself,targets):
                return targets
            for b in target.bonus :
                b.modifyDefenseChoice=MethodType(doNotModifyTarget,b)
            target.bonus.append(NePeutPasAttaquer())
            target.bonus[-1].owner=target
            target.bonus[-1].beforeCombat=MethodType(modifbefore,target.bonus[-1])
            target.sarcoturn = self.level            
        else :
            from Player import Computer0
            if (not isinstance(origin.player,Computer0))  : print "pas d effet sur ",target.name

class EnlevePouvoirSpeciaux(Spell) :
    positive = False
    def getCost(self) :
        return 2.3*self.target.getCostMultiplier(self)
    def effect(self,origin,creature):
        if isinstance(creature,Creature) and creature.pv>0:
            for b in reversed(creature.bonus) :
                b.removed()
            #for k,m in reversed(creature.marks.items()) :
            #    if hasattr(m, '__getitem__') and m[3]=="power" :
            #        del creature.marks[k]
            creature.bonus=[]
            creature.addMark("cross",size=(300,400),pos="center",typ="",level=1,value=0)    
    def getDescription(self):
        return "Enleve tous les pouvoirs speciaux \n"+self.target.getDescription(True)

class GainMana(Spell) :
    positive = True
    has_target = False
    def getCost(self) :
        return 0.98       
    def getTarget(self,origin):
        return [origin.player]
    def effect(self,origin,target):
        target.mana+=2
        #origin.die()
        #else :
        #    if hasattr(target,"name") and target.name : 
        #        print "pas d effet sur ",target.name,target
    def getDescription(self):
        return "Augmente de 2 le Mana"

class Reinitialize(Spell) :
    positive = True
    has_target = True
    def getCost(self) :
        return 3.      
    def effect(self,origin,target):
        if target.pv>0 and hasattr(target,"card") :
            Transformation(target.card).effect(origin,target)
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

