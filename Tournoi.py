# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 12:25:11 2018

@author: irene
"""
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

import CardGame
import time
import glob
import random
import deck_creation
from Player import Computer

all_decks = [d.replace("_"," ") for d in glob.glob("Decks/*.dek")]
random.shuffle(all_decks)

for d in ["Nains de Omaghetar","Mauvais Reves","Necroman","Mahishasura","Guilde des Braves d'Edemas",
                             "Horde","Demon","Vikings","Chateau","Le Lac","Pirates des Mers Maudites","invocationscampagne",
                             "Reveil De La Roche","Chasseurs des Plaines Neigeuses","MagiePure","Voyageurs d'Outreplans"]:
    dcomplet="Decks\\"+d+".dek"
    if dcomplet in all_decks :
        all_decks.remove(dcomplet)
    print d, " banned "
all_decks = all_decks

print all_decks

print time.localtime()[3:6]
matches = []
i=0
scores = {deck[6:-4]:0 for deck in all_decks}
for n in range(len(all_decks)-1) :
    deck=all_decks[n]
    for n2 in range(n+1,len(all_decks)) :
        deck2=all_decks[n2][6:-4]
        if deck[6:-4] != deck2:
            i+=1
            print i,": Battle between {0} and {1}".format(deck,deck2)
            matches.append((deck[6:-4],deck2))

history = []
print time.time()
for match in matches:
    game=CardGame.Game()
    start = time.localtime()[3:6]
    #game.defaultPlayers(player1_set,player2_set)
    print "\n\n PLAYING ",match
    game.player1=Computer(match[0],game.chooseDeck(match[0]),game,2,hide=False)
    #game.player2=Player(player2_set[0],game.chooseDeck(player2_set[1]),game)
    game.player2=Computer(match[1],game.chooseDeck(match[1]),game,2,hide=False)
    #game.player2=HostedPlayer(game)
    game.initialize(common_start=True)
#    if match[1] == "Voyageurs d'Outreplans":
#        game.activateOption("Baton de La Lune Rugissante")
#        game.activateOption("SetHeroLives40")
#    elif match[1] == "MagiePure":
#        game.activateOption("Recifs")
#    elif match[1] == "Reveil De La Roche":
#        game.activateOption("AgonieResonante")
#    elif match[1] == "Pirates des Mers Maudites":
#        game.activateOption("FrozenBoats")
#    elif match[1] == "Mahishasura":
#        game.activateOption("Lakshmi")
#    elif match[1] == "Le Lac":
#        game.activateOption("Algues")
#    elif match[1] == "Guilde des Braves d'Edemas":
#        game.activateOption("LimiteNombreCreatures3")
#    elif match[1] == "Chasseurs des Plaines Neigeuses":
#        game.activateOption("FroidIntenable")
    game.play()
    print "VICTORY OF ",game.get_winner()
    if game.get_winner():
        scores[game.get_winner()]+=1
    history.append((match,game.get_winner(),game.turn,game.firstplayer.name,(game.player1.pv,game.player2.pv),start))
    open("history.sav","w").write(str(history))