# -*- coding: utf-8 -*-
"""
Created on Tue Sep 05 10:54:46 2017

@author: test
"""

import glob
import cardPowers
from Spell import SpellWithLevel
import types
import re

print dir(cardPowers)


level_spells = []


for power in dir(cardPowers):
    if type(eval("cardPowers."+power)) == types.ClassType and issubclass(eval("cardPowers."+power),SpellWithLevel):
        print eval("cardPowers."+power).__name__," is spell with level"
        level_spells.append(eval("cardPowers."+power).__name__)

level_spells.remove("Bonus")
level_spells.append("Invocation")

for monster_file in glob.glob("Protection\\*.sav"):
    with open(monster_file,"r") as mfile:
        reader = mfile.read()
        for sp in level_spells:
            while re.search("cardPowers."+sp+"\((?!Level.)",reader):
                start = re.search("cardPowers."+sp+"\((?!Level.)",reader).start()
                print "made a change at ",start
                print reader[start:start+len(sp)+12]+"Level.NbFixe("+reader[start+len(sp)+12]+")"
                
                if re.search("[0-9][0-9]",reader[start:start+len(sp)+16]):
                    print "two digit level changed in ",monster_file
                    reader = reader[0:start+len(sp)+12]+"Level.NbFixe("+reader[start+len(sp)+12]+reader[start+len(sp)+13]+")"+reader[start+len(sp)+14:]
                else:
                    print reader[start:start+len(sp)+16]
                    reader = reader[0:start+len(sp)+12]+"Level.NbFixe("+reader[start+len(sp)+12]+")"+reader[start+len(sp)+13:]
            
    
    for sp in "Invocation","PlaceCarteDansMain":
        while re.search("Spell."+sp+"\((?!Level.)",reader):
                    start = re.search("Spell."+sp+"\((?!Level.)",reader).start()
                    print "made a change at ",start
                    print reader[start:start+len(sp)+7]+"Level.NbFixe("+reader[start+len(sp)+7]+")"
                    if re.search("[0-9][0-9]",reader[start:start+len(sp)+7]):
                        print "two digit level changed in ",monster_file
                        reader = reader[0:start+len(sp)+7]+"Level.NbFixe("+reader[start+len(sp)+7]+reader[start+len(sp)+8]+")"+reader[start+len(sp)+9:]
                    else:
                        reader = reader[0:start+len(sp)+7]+"Level.NbFixe("+reader[start+len(sp)+7]+")"+reader[start+len(sp)+8:]
    while re.search("cardPowers.Bonus\((?!Level.)",reader):
        start = re.search("cardPowers.Bonus\((?!Level.)",reader).start()
        print "made a change at ",start
        print reader[start:start+17]+"Level.NbFixe("+reader[start+17]+"),Level.NbFixe("+reader[start+19]+")"
        reader = reader[0:start+17]+"Level.NbFixe("+reader[start+17]+"),Level.NbFixe("+reader[start+19]+")"+reader[start+20:]
    """
    while "Etheres" in reader:
        reader = reader.replace("Etheres","CampagneMagique")
    """
    open(monster_file,"w").write(reader)
                