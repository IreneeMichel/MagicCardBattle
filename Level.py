# -*- coding: utf-8 -*-
"""
Created on Mon Sep 04 20:13:39 2017

@author: test
"""

from Tkinter import OptionMenu
#import random

class Level():
    
    def __init__(self,level=1):
        self.level = level
    
    def getLevel(self,origin):
        return self.level
        
    def constructor(self) :
        return "Level.NbFixe("+str(self.level)+")"
        
    def getInlineDescription(self,unit,s=True):
        return self.getDescription(unit,s=True)
        
    def getDescription(self,unit,s=True):
        return str(self.level)+" "+unit+("s"*(self.level>1)*s)
        
    def getCostMultiplier(self,spell):
        return self.level
        
    def getStars(self):
        return 0
    
    def modifyLevel(self,n):
        self.level = int(n)
        
    def getDescriptionBonus(level1,level2):
        return "+"+str(level1.level)+"//+"+str(level2.level)+" "

class NbFixe(Level):
    pass

class RelativeLevel(Level):
    level = 1
    extension = ""
    def constructor(self):
        return "Level."+self.__class__.__name__+"("+str(self.level)+")"
    
    
    def getDescription(self,unit,s=True):
        return str(self.level)+" "+unit+"s"*(s and self.level>1)+self.extension
    
    def getDescriptionBonus(level1,level2):
        return "+"+str(level1.level)+"//+"+str(level2.level)+" "+level1.extension+" "


class ParCarteEnMain(RelativeLevel):
    extension = " par carte en main"
    
    def getLevel(self,origin):
        return len(origin.player.hand)*self.level
    
    def getCostMultiplier(self,spell):
        return 5.*self.level

class ParCarteEnMainAdverse(RelativeLevel):
    extension = " par carte dans la main adverse"
    
    def getLevel(self,origin):
        return len(origin.player.adv.hand)*self.level
    
    def getCostMultiplier(self,spell):
        return 4*self.level


class ParEnnemi(RelativeLevel):
    extension = " par ennemi"
    
    def getLevel(self,origin):
        return len(origin.player.adv.army)*self.level
    
    def getCostMultiplier(self,spell):
        return 4.*self.level

class ParAllie(RelativeLevel):
    extension = " par allie"
    
    def getLevel(self,origin):
        return len(origin.player.army)*self.level
    
    def getCostMultiplier(self,spell):
        return 4.6*self.level

class ParChargeEnnemi(RelativeLevel):
    extension = " par pouvoir Charge dans le deck adverse"
    
    def getLevel(self,origin):
        l=[]
        for c in origin.player.adv.deck:
            try:
                l.append(c.pv > 0 and any([ bon.__class__.__name__ == "Charge" for bon in c.bonus]))
            except:
                print c.name,c,"doesn't have bonus",c.pv
        return l.count(True)*self.level
    
    
    def getCostMultiplier(self,spell):
        if spell.getValue()>0. :    
            return 4.5*self.level
        else :
            return 18.*self.level

        
level_dir = dir()

def getLevelMenu(master,variable) :
    # print target_dir
    class_content=[p for p in level_dir if type(eval(p)) == type(Level) and issubclass(eval(p),Level)]
    # print class_content
    if "Level" in class_content: class_content.remove("Level")
    if "RelativeLevel" in class_content: class_content.remove("RelativeLevel")
    # print class_content
    bm = OptionMenu(master,variable,*class_content)
    """
    bm["menu"].insert_separator(nbPossibleTargets)
    bm["menu"].insert_separator(nbPossibleTargets+2)
    """
    return bm