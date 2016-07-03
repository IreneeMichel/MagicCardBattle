import pickle
import glob
from copy import copy
import deck_creation
import random
import CardGame
import Player
import pygame
import time

cards = {}
files = glob.glob('CardFiles/*.sav')

print files

for fil in files:
    f = open(fil,"rb")
    p = pickle.load(f)
    cards.update(p)
    f.close()

print cards
print len(cards)

begin = time.clock()

powers = {}

for c in cards.values():
    for p in c.bonus:
        if p.__class__.__name__ in powers.keys():
            powers[p.__class__.__name__] += 1
        else:
            powers[p.__class__.__name__] = 1

nums = powers.values()
numbers = copy(nums)
for n in numbers:
    if nums.count(n)>1:
        nums.remove(n)
nums.sort()
nums = reversed(nums)

ordered = {}
for i in nums:
    po = []
    for p in powers.keys():
        if powers[p] == i:
            po.append(p)
    print i,po,round((100.*i)/len(cards),2),"%"
    ordered[i]=po


for e,p in enumerate(nums):
    print e,": ",ordered[p],", statistic = ",(100.*p)/len(cards),"(",p,")"


blocked_decks = deck_creation.get_blocked_decks()
playable_decks = [d[d.index("\\")+1:d.index(".dek")].replace("_"," ") for d in glob.glob("Decks/*.dek")]
#playable_decks.remove("default")
playable_decks.remove("Fried Frenchs")
all_decks = copy(playable_decks)
for d in reversed(playable_decks):
    if d in blocked_decks:
        playable_decks.remove(d)
print "all_decks: ",all_decks

scores = {}
for d in all_decks:
    scores[d] = 0
    


for deck in all_decks:
    with open("Decks\\"+deck.replace(" ","_")+".dek","rb") as f:
        print "\n*** ",deck
        dec = pickle.load(f)
        print dec
        deck_cards = []
        for m in dec:
            if m != "AvatarImage":
                for i in range(dec[m]):
                    if m in cards:
                        deck_cards.append(cards[m])
        print "Cost average, ",sum(int(unit.getCost()) for unit in deck_cards)/float(len(deck_cards))
        deck_powers = []
        for unit in deck_cards:
            for power in unit.bonus:
                deck_powers.append(power.__class__)
        #print "Powers of deck ",deck_powers
        powers_by_num = {}
        for p in deck_powers:
            if deck_powers.count(p) in powers_by_num:
                if p in powers_by_num[deck_powers.count(p)]:
                    pass
                else:
                    powers_by_num[deck_powers.count(p)].append(p)
            else:
                powers_by_num[deck_powers.count(p)] = [p]
        print "Powers of deck by num ",powers_by_num
        keys = powers_by_num.keys()
        keys.sort()
        print "Diversity  ",sum(len(i) for i in powers_by_num.values())
        print "Principal Powers are ",",".join("/".join(p.__name__ for p in powers_by_num[k]) for k in reversed(keys[-3:]))
                
        



historic = []
#print all_decks
tyio = 0

all_decks = ["Chateau","Nains de Omaghetar","Nocturne","Ogres du Grand Sud","Demon","Bourrin","Vikings","Horde","Necroman","Mauvais Reves","default"]
print "\n\nPlan: "
nb = 0
ad = copy(all_decks)
for p in reversed(ad):
    for c in reversed(ad):
        if c != p:
            print "Battle between ",p,"and",c
            nb += 1
    ad.remove(p)

print "\n Number of Battles:", nb,"\n\n\n"

for i in range(2):
    for p in reversed(all_decks):
        for c in reversed(all_decks):
            if c != p:
                actual_time  = int(time.clock()-begin)
                print "Time = "+str(int(actual_time/60))+"'"+str(actual_time%60)   
                print "Battle between ",p," and ",c
                gam = CardGame.Game()
                gam.player1=Player.Computer(p,gam.chooseDeck(p,1),gam,2,verbose=0,hide=False)
                gam.player2=Player.Computer(c,gam.chooseDeck(c,2),gam,2,verbose=0,hide=False)
                gam.player1.deck_name = p
                gam.player2.deck_name = c
                gam.player1.avatar_img=None
                gam.player2.avatar_img=None
                gam.initialise()
                gam.play()
                w = gam.get_winner()
                if w:
                    game_result = [p,c,w,gam.turn,gam.firstplayer.deck_name,actual_time]
                    historic.append(game_result)
                    print "victory of ",w
                    scores[w] += 1
                else:
                    break
        all_decks.remove(p)

pygame.quit()

print "\n"*5+" SCORES: "
for s in scores.keys():
    print s,scores[s]

print "\nBATTLE HISTORIC:"
for h in historic:
    print int(h[5]/60),"'",h[5]%60,": Battle between ",h[0]," and ",h[1],": winner is ",h[2],"(turn ",h[3],", first player was ",h[4],")"
