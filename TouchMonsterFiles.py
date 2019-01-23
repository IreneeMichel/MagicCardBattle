# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 13:26:15 2016

@author: enfants
"""
import os
#import pickle
import glob
#import types
#import time

os.chdir(os.path.dirname(os.path.realpath(__file__)))

#from Card import Card
#from Target import MasseEnemi,MasseEnnemi,Personnel
#from cardPowers import Guerison,GuerisonHeros

#def searchPower(o,max_depth=8) :
#    for o2n in dir(o) :
#        p=getattr(o,o2n)
#        if isinstance(p,MasseEnemi) :
#            print " pb found masse enemis"
#            setattr(o,o2n,MasseEnnemi())
#        """
#        if isinstance(p,Personal) :
#            print " pb found personel"
#            setattr(o,o2n,Personnel())
#        if isinstance(p,Guerrison) :
#            print " pb found guerison"
#            setattr(o,o2n,Guerison())
#            getattr(o,o2n).level=p.level
#            getattr(o,o2n).target=p.target
#        if isinstance(p,GuerrisonHero) :
#            print " pb found guerison hero"
#            setattr(o,o2n,GuerisonHeros())
#            getattr(o,o2n).level=p.level
#        """
#    for o2n in dir(o) :
#        o2=getattr(o,o2n)
#        if type(o2)==type([]) :
#            #print o2n," is list",o2
#            for o3 in o2 :
##                if isinstance(o3,Guerrison) :
##                    print " pb found"
##                    o2.append(Guerison())
##                    o2[-1].level=o3.level
##                    o2[-1].target=o3.target
##                    o2.remove(o3)
##                elif isinstance(o3,GuerrisonHero) :
##                    print " pb found"
##                    o2.append(GuerisonHeros())
##                    o2[-1].level=o3.level
##                    o2.remove(o3)     
##                else :
#                if type(o3)==types.InstanceType and max_depth>0 :
#                        searchPower(o3,max_depth-1)
#        if type(o2)==types.InstanceType and max_depth>0 and o2n!="card" :
#            searchPower(o2,max_depth-1)

#for f in glob.glob("CardFiles/*_monsters.sav"):
#     if f in ("CardFiles\\all_monsters.sav","CardFiles\\recup_monsters.sav") :
#         continue
#     print "** cards in ",f
#     with open(f, "rb") as fi:
#         mobs = pickle.load( fi)
#     for n,m in mobs.items() :   
#         print "* "+n
#         searchPower(m)
#     pickle.dump(mobs,open(f,"wb"))
from Card import readMonsters

print ("nettoyage unknown_monsters.sav")
monsters = readMonsters(os.path.join("CardFiles","unknown_monsters.sav"))
for f in glob.glob("CardFiles/*_monsters.sav"):
     if ("unknown_monsters.sav" in f) or ("all_monsters.sav" in f) or ("recup_monsters.sav" in f) :
         continue
     print ("cards in ",f)
     good = readMonsters(f)
     for m in good :
         if m in monsters :
             print( m)
             del monsters[m]

open(os.path.join("CardFiles","unknown_monsters.sav"),"w").write("\n".join([m.constructor() for m in monsters.values()]))


all_monsters = readMonsters(os.path.join("CardFiles","all_monsters.sav"))

#         monsters.update(good)
#    
#    pickle.dump(monsters,open(  "CardFiles/all_monsters.sav","wb"))   

print ("recreation toutes images et met Majuscule")
bad_opt={}
problem=[]
for f in glob.glob("CardFiles/*_monsters.sav"):
     if ("all_monsters.sav" in f) or ("recup_monsters.sav" in f) :
         continue
     print ("** cards in ",f)
     mobs = readMonsters( f)
     for n,m in mobs.items() :
         print ("* "+n)
         try :
             goodname=n[0].upper()+n[1:]
             if n!=goodname :
                 m.deleteCreature(n)
                 if goodname in all_monsters :
                     continue            
             try:
                 if n!=m.name :
                     m.deleteCreature(m.name)
                 try:
                     m.name=goodname
                     if "CardFiles" not in m.dumping_file :
                         m.dumping_file="CardFiles/"+m.dumping_file
                     m.save()
                     try:
                         co=m.getCost()
                         if (co-int(co))<0.5 and m.pv>0 :
                             bad_opt[n]=(co,m.monster_type)
                     except:
                        problem.append([f,n,"part 3"])
                     #time.wait(1)
                 except Exception as err:
                     print (err)
                     problem.append([f,n,"part 2.5 : recherche image"])                    
             except :
                problem.append([f,n,"part 2"])
         except:
             problem.append([f,n,"part 1"])

print ("problem with ",problem)
print ("\na revoir",bad_opt)

             
 