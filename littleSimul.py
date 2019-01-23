# -*- coding: utf-8 -*-
"""
Created on Sat Mar 24 10:41:05 2018

@author: test
"""
import random


base_deck = [0]*2+[1]*2+[2]*2+[4]*2+9*[3]+[5]*13

combo = 0
conqueror = 0
sectary = 0
total = 10000
total_draw = 0

for i in range(total):
    deck = base_deck[:]
    random.shuffle(deck)
    n=1
    added = 0
    hand = []
    while not(0 in hand and 1 in hand and 2 in hand and 4 in hand):
        hand.append(deck.pop(0))
        n += 1
        if hand[-1]==3:
            added +=1
        if n == 12 or (n<12 and 0 in hand and 1 in hand and 2 in hand and 4 in hand):
            if 0 in hand:
                conqueror += 1
            if 1 in hand:
                sectary += 1
            if 0 in hand and 1 in hand and 2 in hand and 4 in hand:
                combo += 1
    total_draw += len(hand)-added

print combo, total, ": thus a ratio of ",float(combo)*100/total
print conqueror, total, ": thus a ratio of ",float(conqueror)*100/total
print sectary, total, ": thus a ratio of ",float(sectary)*100/total
print "Average cards drawn before combo in hand : ",float(total_draw)/total