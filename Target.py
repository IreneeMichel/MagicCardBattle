# -*- coding: utf-8 -*-
"""
Created on Wed Dec 09 16:40:35 2015

@author: test
"""
from Tkinter import OptionMenu
#import random

class Target():
    side=None
#    def getTarget(self,origin):
#        return "choose"
    def constructor(self) :
        return "Target."+self.__class__.__name__+"()"
    def getInlineDescription(self,*args):
        return self.__class__.__name__
    def getDescription(self,*args):
        return self.__class__.__name__
    def getCostMultiplier(self,spell):
        return 1
    def getStars(self):
        return 0

class UneCibleAuChoix(Target):
    side = "choose"
    def getTarget(self,origin):
        return "choose"
    def getCostMultiplier(self,spell):
        return 1
    def getDescription(self,compulsary=False):
        if compulsary:
            return "une cible au choix"
        else:
            return " "
"""
class EnemiAleatoir(Target):
    def getTarget(self,origin):
        if len(origin.player.adv.army)<2:
            return origin.player.adv.army
        else:
            if type(origin.player.adv.army)==type([]):
                return [random.choice(origin.player.adv.army)]
            else:
                return [random.choice(origin.player.adv.army.sprites())]
    def getCostMultiplier(self,spell):
        return 0.75
    def getDescription(self,compulsary=False):
        return "\n"*(1-compulsary)+" ennemi(s) au hasard"

class Personal(Target):
    def getTarget(self,origin):
        return [origin]
    def getCostMultiplier(self,spell):
        return 0.75
"""        
class Personnel(Target):
    side = "you"
    def getTarget(self,origin):
        if origin.pv<1 or origin.max_pv<1  : return []
        return [origin]
    def getCostMultiplier(self,spell):
        return 0.75

#class MasseEnemi(Target):
#    def getTarget(self,origin):
#        return origin.player.adv.army
#    def getCostMultiplier(self,spell):
#        return 3.
#    def getDescription(self,compulsary=False):
#        return "Tous ennemis"
# 
class MasseEnnemi(Target):
    side = "him"
    def getTarget(self,origin):
        return [m for m in origin.player.adv.army if m and m.pv>0 and m.max_pv>0 ]
    def getCostMultiplier(self,spell):
        return 3.
    def getDescription(self,compulsary=False):
        return "Tous ennemis"


class MasseAllie(Target):
    side = "you"
    def getTarget(self,origin):
        return [m for m in origin.player.army if m and m.pv>0 and m!=origin  and m.max_pv>0 ]
    def getCostMultiplier(self,spell):
        return 3.    
    def getDescription(self,compulsary=False):
        return "Tous allies"


class Armaguedon(Target):
    side = None
    def getTarget(self,origin):
        try:
            return [m for m in origin.player.army if m and m.pv>0  and m.max_pv>0 ]+[m for m in origin.player.adv.army if m and m.pv>0  and m.max_pv>0 ]
        except:
            print "ANOMALIE de TARGET"
            return origin.player.army+origin.player.adv.army
    def getCostMultiplier(self,spell):
        return 1.8
        

target_dir = dir()

def getTargetMenu(master,variable) :
    # print target_dir
    class_content=[p for p in target_dir if type(eval(p)) == type(Target) and issubclass(eval(p),Target)]
    # print class_content
    if "Target" in class_content: class_content.remove("Target")
    if "MasseEnemi" in class_content: class_content.remove("MasseEnemi")
    # print class_content
    bm = OptionMenu(master,variable,*class_content)
    """
    bm["menu"].insert_separator(nbPossibleTargets)
    bm["menu"].insert_separator(nbPossibleTargets+2)
    """
    return bm

def getNegativeSpellTargetMenu(master,variable,spell_negative):
    class_content=[p for p in target_dir if type(eval(p)) == type(Target) and issubclass(eval(p),Target) and [eval(p).side=="him",eval(p).side=="you"][spell_negative]]
    if "Target" in class_content: class_content.remove("Target")
    if "MasseEnemi" in class_content: class_content.remove("MasseEnemi")
    # print class_content
    bm = OptionMenu(master,variable,*class_content)
    return bm