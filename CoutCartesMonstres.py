import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
#import sys
#sys.path.append('MagicCardBattle')
#from math import floor
#import re
#import pickle
#import shutil
#UP=re.compile('(?=[A-Z])')

#--------------------------
#from Spell import -
from Card import Card
#from cardPowers import *
#possibleAsTarget=[Personne]
# target

#--------------------------

#----------------------------
#for p in possibleAsBonus : 
#   #permet d utiliser "provocation" plutot que "Provocation()"
#   if not p.isTrigger and not p.hasTarget :
#       exec(p.__name__.lower()+"="+p.__name__+"()")
        
#--------------------------

"""
troll=Card("Troll gris",4,4)
troll.getCost()
troll2=Card("Troll rouge",4,4)
troll2.addBonus(Provocation())
troll2.getCost()
gob=Card("Goblin guerrisseur",2,2)
gob.addBonus(CriDeGuerre(Guerrison(4)))
gob.getCost()
"""

#------------------------------------------

from Tkinter import Tk

def run(blocked_creature=[]):
    fenetre = Tk()
    fenetre['bg']='white'
    fenetre.title("Creation de Monstre")
    Card.blocked_creature=blocked_creature
    monster=Card("mouton",1,1)
    monster.photofile='./photo/mouton.jpg'
    monster.initWidget(fenetre)
    fenetre.mainloop()
    #fenetre.destroy()

if __name__ == "__main__":
    run()
    #import os
#    import pickle
#    #os.chdir('C:\\Users\enfants\Documents\MagicCardBattle')
#    import glob
#
#
#    
#         
#    with open( "CardFiles/all_monsters.sav", "rb") as f:
#         monsters = pickle.load( f)
#    
#
#hum={}
#for n,m in monsters.items() :
#    if "human" in m.dumping_file :
#       m.dumping_file="CardFiles/human_monsters.sav"
#       hum[n]=m
#pickle.dump(hum,open(  "CardFiles/human_monsters.sav","wb"))