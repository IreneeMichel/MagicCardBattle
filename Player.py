import random
import pygame                 
#print "import complete"
from copy import copy
from math import floor
from cardPowers import *
from Sprites import CardInHand,Animation
from functools import partial
from Creature import Creature,AnimatedCreature,CreatureCopy

class Player:
    def __init__(self,name,deck,game) :
        self.name=name
        self.deck = deck
        random.shuffle(self.deck)
        for c in self.deck :
            c.costint=int(floor(c.getCost()))
            c.starcost=c.getStars()
        if not ("-simu" in name) :
            self.hand=pygame.sprite.OrderedUpdates()
            self.army= pygame.sprite.OrderedUpdates() # includes weapons and unbunded permanent spells
        self.max_pv = self.pv=30       
        self.game = game
        self.player=self
        self.att=0            
        self.bonus=[]
        self.Attacker_selected = None
        self.spell_pending = None
        self.mana=0
        self.ending=False
        self.hide_cards = False
    
    def start(self):        
        if self.deck:
            self.drawCard(3)
        self.center = self.icon.center
        #self.size = self.icon.size
        self.mana=self.game.turn
        self.nb_invocation_done_this_turn=0
    
    def drawCard(self,n=1,defined=None) :
        if hasattr(self,"verbose") and self.verbose>4 : print " appel de drawCard "
        wait = 0
        totaln=len(self.hand)+n
        # a recoder avec des pop
        for i in self.hand :
            i.takePlace(add=n)
        if not(defined):            
            for i,c in enumerate(self.deck[0:n]):
                self.hand.add(CardInHand(c,self,totaln-n+i,totaln,not(self.hide_cards),wait))           
                wait += 10
        else: # la carte choisie ne disparait pas du pack
            self.hand.add(CardInHand(defined,self,totaln,totaln,not(self.hide_cards),wait))
        #for i,card in enumerate(self.hand):
        #   card.organise_cards(i+1,len(self.hand))
        self.deck=self.deck[n:]
 
    def beginOfTurn(self) :
        self.mana=self.game.turn
        #self.turn=n
        for mons in self.army :
            mons.beginTurn()
        self.drawCard()
        self.nb_invocation_done_this_turn=0
               
    def sufferDamage(self,damage) :
        #self.sufferDamageAnimation(damage)
        for c in self.army:
            for b in c.bonus:
                damage = b.modifyPlayerSuffer(self,damage)
        self.pv-=damage
        if self.pv<1:
            # more to add...
            self.game.end = True
            self.game.winner = self.adv.name
            print " *** "+self.name+" is dead ****"
        self.icon.update()
    def attack(self,target) :
        pass
    def defend(self,target) :
        pass
    def afterCombat(self,target) :
        pass
    def combatSequence(self,target) :
        pass
    def selection(self,selection): # creature selected for attack
        #print "selection de player "
        self.Attacker_selected = selection
        self.Attacker_selected.image.set_alpha(55)
        valide_target=self.attack_targets(self.Attacker_selected)
        if len(valide_target)==1 and (valide_target[0] in self.army) :
            self.Attacker_selected.combatAnim(valide_target[0])
            self.deselection()
        else :
            self.game.mouse.mode = "target"
        
    def deselection(self):
        if self.Attacker_selected!=None:
            #print "deselection attacker"
            self.Attacker_selected.image.set_alpha(255)
            self.Attacker_selected = None
            if not self.spell_pending :
                self.game.mouse.mode = "normal"
        else :
            #print "deselection spell"
            self.spell_pending = None
            self.game.mouse.mode = "normal"
        self.orderArmy()
    def launch(self,origin,spell) :
        if hasattr(self,"verbose") : print " "*4*(2-self.nv)+"player ",self.name,"launch ",spell.getInlineDescription(),"from",origin,"  army is len",len(self.army)
        origin.castSpellAnimation()
        target=spell.getTarget(origin)
        #print " target in launch ; ",target
        if target=="choose" :
            #print " launch choose de player"
#            if self.spell_pending :
#                print "on attends que le sort ",self.spell_pending[1].getInlineDescription()," soit lance"
            
            while self.spell_pending :
                #print "turn of ",self.name
                #print "player is",self.game.player.name
                self.game.update()  # on attends que le sort precedent soit lance
            self.game.mouse.mode = "target"
            self.game.mouse.update()
            self.spell_pending=(origin,spell)
            #print "new spell is pending :",spell.getInlineDescription()
        elif target :
            #poss=self.spell_targets(origin)
            #target=[t for t in target if t in poss]
            self.spellEffect(spell,origin,target)
            #print "spell is done"
        if hasattr(origin,"die") and origin.pv<1 and origin.is_dead == False :
            #print "     player launch die "
            if origin.card.pv==0 :
                origin.is_dead=True
            origin.die()        
        #print "fin launch from",origin,"  army is ",self.army
    def sacrify(self) :
        if len(self.army)>0 :
            self.launch(self.army[0],Sacrifice())
    def spellEffect(self,spell,origin,targets) :
       if hasattr(self,"verbose") and self.verbose>4 : print "      ",self.name,"appel de spellEffect ",spell.getInlineDescription()
       if origin.max_pv==0 :
           origin.pv=-1
       for t in reversed(targets) :
            if not (t is origin) :
                eff=partial(spell.effect,origin,t)
                sp=Sprite(origin,"gameAnimationImages/boule_energie_verte.png",[180,180])
                if isinstance(t,Player) : t=t.icon
                phase0=(t.getPosition(),10,None,eff)    
                Animation(sp,[phase0],True)
            else :
                #spell.player = self
                spell.effect(origin,t)
            
    def update(self,events):
        #print "player update"
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:             
                if hasattr(self,"verbose") and self.verbose>4 : print "           event Button in Player.update "
                pos=pygame.mouse.get_pos()
                if self.Attacker_selected != None:
                    # Creature
                    contact=[s for s in self.adv.army if hasattr(s,"rect") and s.rect.collidepoint(pos)]
                    contact+=[s for s in self.army if hasattr(s,"rect") and s.rect.collidepoint(pos)]
                    if self.adv.icon.rect.collidepoint(pos) :
                        contact.append(self.adv)
                    valide_target=self.attack_targets(self.Attacker_selected)
                    for t in contact :
                        if t in valide_target :
                            self.Attacker_selected.combatAnim(t)
                            break
                        """
                        if hasattr(t,"name") :
                            print t.name,"is not a possible target"
                        else :
                            print "bad target with no name"
                        """
                    self.deselection()                       
                elif self.spell_pending != None:
                    #print "clic et spell pending"
                    # Creature
                    origin,spell=self.spell_pending
                    contact=[s for s in self.adv.army if s.rect.collidepoint(pos)]
                    contact+=[s for s in self.army if s.rect.collidepoint(pos)]
                    if self.adv.icon.rect.collidepoint(pos) :
                        contact.append(self.adv)
                    if self.icon.rect.collidepoint(pos) :
                        contact.append(self)
                    valide_target=self.spell_targets(origin,spell.positive)
                    if len(valide_target)<1 :
                        #print "unvalide target"
                        self.deselection()
                        return
                    for t in contact :
                        if t in valide_target :
                            self.deselection()                     
                            self.spellEffect(spell,origin,[t])
                            break
                        """
                        if hasattr(t,"name") :
                            print t.name,"is not a possible target"
                        else :
                            print "bad target with no name"
                        """
                else :  
                    # Contact of mouse with hand or creature 
                    zoomedcard=self.game.zoomed.card
                    if isinstance(zoomedcard,Creature) and zoomedcard.player==self:
                        if zoomedcard.ready :
                            self.selection(zoomedcard)        
                    elif isinstance(zoomedcard,CardInHand) and zoomedcard.player==self:
                        if self.actualCost(zoomedcard) <= self.mana:
                            if zoomedcard.content.pv >0 and self.nb_invocation_done_this_turn>=5 :
                                print "only 5 monster per Turn can be created"
                            else :
                                self.playCard(zoomedcard)
                    elif zoomedcard :  # should be only None left
                        print "unknown type ?"    
                # Clicked on end button
                if self.game.endturn_button.rect.collidepoint(pos):               
                    self.deselection()
                    if not self.ending :
                        self.endTurn()             
        #print "fin player update"
    def actualCost(self,card) :
        if isinstance(card,CardInHand) :
            card=card.content
        cost=card.costint
        for cr in self.army:
            if cr.max_pv>0 :
                for b in cr.bonus:
                    cost = b.modifyManaCost(card,cost)
        return cost
        
    def playCard(self,hand_card) :
        if hasattr(self,"verbose") and self.verbose>4 : print "         appel de playCard "
        #print "play card"
        if hand_card.content.pv ==0 :
            hand_card.show()
        else :
            self.nb_invocation_done_this_turn+=1
        self.mana-=self.actualCost(hand_card)
        AnimatedCreature(hand_card,hand_card.content,self)
        # the card is removed from hand and added to army at end of animation
        #origin.kill()
    def endTurn(self):
        #print "player end Turn"
        if hasattr(self,"verbose") and self.verbose>4 : print "         appel de endTurn "
        #print "endTurn"
        self.ending=True
        for cr in reversed(self.army): # si un mort, pas d erreur d indice
            if cr.max_pv>0 : cr.endTurn()
        while self.spell_pending or self.game.all_animations :
            #print "end Turn spell pending"
            self.game.update()
            #self.game.mouse.update()
            #self.update(pygame.event.get())  # on attends que le sort precedent soit lance
        self.ending=False
        #if hasattr(self,"verify_value") :
        #    del self.verify_value
        self.game.changePlayer()
        #print "fin player end Turn"
    def attack_targets(self,monster):
        if hasattr(self,"verbose") and self.verbose>4 : print "         appel de attack_targets "
        #print "%%%%%% attack_targets  !"
        targets=[]
        for mons in self.adv.army :
            targets.append(mons)
        targets.append(self.adv)
        for mons in self.adv.army :
            for b in mons.bonus :
                targets=b.modifyDefenseChoice(targets)
        for mons in self.army :
            if mons is not monster :
                targets.append(mons)
        for b in monster.bonus :
            targets=b.modifyAttackChoice(targets)
        if hasattr(self,"verbose") and self.verbose>4 : print "       fin attack_targets ",len(targets)
        return targets
    def spell_targets(self,monster,is_positive) :
        # is_positive permet de classer pour ordi bete sur qui lancer en premier
        if hasattr(self,"verbose") and self.verbose>4 : print "         appel de spell_targets "
        #print "%%%%%% spell_targets  !"
        targets=[]
        if "choix1" in [m.name for m in self.army] : # pas bien : devrait pas utiliser nom specifique de pouvoir
            return [m for m in self.army if "choix" in m.name]
        else :
            if is_positive : 
                for mons in self.army :
                    if mons.pv>0 : targets.append(mons)
                if is_positive!=-1 :
                    for mons in self.adv.army :
                        if mons.pv>0 : targets.append(mons)
            else :
                for mons in self.adv.army :
                    if mons.pv>0 : targets.append(mons)
                for mons in self.army :
                    if mons.pv>0 : targets.append(mons)
            if is_positive!=-1 :
                targets.append(self.adv)
                targets.append(self)
            for mons in self.adv.army :
                for i in mons.bonus :
                    targets=i.modifySpellTargetChoice(targets)
            if hasattr(self,"verbose") and self.verbose>4 : print "         len(targets) ",len(self.adv.army),"+1+",len(self.army),"+1->",len(targets)
            return targets
    def castSpellAnimation(self) :
        pass
    def orderArmy(self,add=0):
        i=0
        for c in self.army :
            if c.pv>0:
                c.index=i
                #print c.name,"takes place",i
                c.takePlace(add=add)
                i+=1
        
class Computer0(Player) : 
    def getChoice(self,poss):
        #print "get choice computer0"
        return poss[0]
    def verifySituation(self) :
        if hasattr(self,"verify_value") and self.verify_value != self.evaluateSituation(self,self.adv,False) :
            print "error : situation not as expected for ",self.name,self
            print " simulation gave",self.verify_value
            print "reality gives",
            self.verbose+=2
            self.evaluateSituation(self,self.adv,True)
            raise "bug"
        if hasattr(self,"verify_value") :
            #print "** VERIF **"
            del self.verify_value
    def play(self) :
        #print "computer play"
        if hasattr(self,"verbose") and self.verbose>4 : print " "*4*(2-self.nv)+" computer ",self.name," plays "       
        # verification of situation let by previous action
        #self.verifySituation()
        # now next action ?
        while self.adv.spell_pending :
            print "spell pending"
            pass
        poss=[]
        poss.append((self.endTurn,"End your turn"))
        for mons in self.army :
                if mons.ready and mons.pv>0 :
                    if (any([isinstance(b,NePeutPasAttaquer) for b in mons.bonus]) 
                        and not any([isinstance(b,ALaPlaceDeLAttaque) for b in mons.bonus]) ) :
                            continue
                    poss.append((partial(self.select_attack_target,mons),"Attack with "+mons.name))
        for c in self.hand :
            if not isinstance(c,SimulationComputer.NotPlayableCard) :
                if hasattr(c,"content") :
                    pv=c.content.pv
                else :
                    pv=c.pv
                if self.actualCost(c)<=self.mana and (pv==0 or self.nb_invocation_done_this_turn<5):
                    poss.append((partial(self.playCard,c),"Creation of "+c.getInlineDescription()))
        choice=self.getChoice(poss)
        #print "computer ",self.name, " has chosen ",choice[1]
        choice[0]() 
        #if isinstance(self,SimulationComputer) : # action is  instant only for simulation computer
        #    self.verifySituation()
        self.orderArmy()
        #print "end of computer play"
    def select_attack_target(self,monster) :
        if hasattr(self,"verbose") and self.verbose>4 : print " "*4*(2-self.nv)+"computer ",self.name," select attack target "       
        #print "attack choice !"
        targets=self.attack_targets(monster)
        #print "for computer , target is ",targets
        if targets :
            poss=[(m,"Attack "+"own "*(m.player is self)+m.getInlineDescription()+str(len(m.marks)),monster) for m in targets if isinstance(m,Creature)]
            if self.adv in targets :
                poss.append((self.adv,"Attack ennemy heroes",monster))
                # ttttt
            choice=self.getChoice(poss)
            target=choice[0]
            monster.combatAnim(target)
        else :
            monster.ready=False
        #if isinstance(self,SimulationComputer) : # action is  instant only for simulation computer
        #    self.verifySituation()

    def launch(self,origin,spell) :
        if hasattr(self,"verbose") and self.verbose>1 : print " "*4*(2-self.nv)+"computer ",self.name," launch ",spell.getInlineDescription()," from ",origin.name
        #if hasattr(self,"verify_value") : del self.verify_value # le sort va modifier l etat du jeu
        origin.castSpellAnimation()
        target=spell.getTarget(origin)
        #print "for computer launch , target=",target
        if target=="choose" :
            #print " launch choose de computer"
            targets=self.spell_targets(origin,spell.positive)
            #print "in launch (choose), target =", [t.name for t in targets]
            if not targets :
                print " no available target for ",spell.getInlineDescription()
                return 
            poss=[(m,"cast "+spell.getInlineDescription()+" on "+"own "*(m.player is self)+m.getInlineDescription(),origin,spell) for m in targets if isinstance(m,Creature)]
            if self.adv in targets :
                poss.append((self.adv,"aim at ennemy hero",origin,spell))
            if self in targets :
                poss.append((self.adv,"aim at your hero",origin,spell))
            target=[self.getChoice(poss)[0]]
            if hasattr(self,"verbose") and self.verbose>2 : print "           choosen target for spell is ",target[0].name,"  ",target
        if target :
            self.spellEffect(spell,origin,target)
            #if isinstance(self,SimulationComputer) : # action is  instant only for simulation computer
            #    self.verifySituation()

        if (origin.card.pv==0) or (origin.pv==0 and not origin.is_dead)  :
            origin.is_dead=True
            origin.die()

    def update(self,events):
        if hasattr(self,"verbose") and self.verbose>4 : print " "*4*(2-self.nv)+"computer ",self.name," update "       
        #if self.game.frames%40 == 1:
        self.play()

class Computer(Computer0) :
    def __init__(self,name,deck,game,nv,action=None,verbose=0,hide=True) :
        if verbose>4 : 
            print " "*4*(2-nv)+"init computer ",name,self
        self.verbose=verbose
        Player.__init__(self,name,deck,game)
        self.nv=nv
        self.hide_cards = hide
        #print " "*2*(2-self.nv)+"init Computer   nv=",nv," with action",action
        self.action=action
    def evaluateSituation(self,player1,player2,verbose=False) :
        if self.verbose>4 : print " "*4*(2-self.nv)+"appel de evaluateSituation for computer ",self.name
        armyval=[1.+i.att*2+i.pv*(1+max(2,i.starcost))+2*len(i.bonus)+sum([m[0] for m in i.marks.values()]) for i in player1.army if i.pv>0 ]
        if verbose and self.verbose>0 : print " "*4*(2-self.nv),len(player1.army)," monstres  ",[i.name for i in player1.army if i.pv>0 ]," de valeur ",armyval 
        armyval2=[1.+i.att*2+i.pv*(1+max(2,i.starcost))+2*len(i.bonus)+sum([m[0] for m in i.marks.values()]) for i in player2.army if i.pv>0 ]
        if verbose and self.verbose>0 : print " "*4*(2-self.nv),len(player2.army)," monstres ",[i.name for i in player2.army if i.pv>0 ],"  de valeur ",armyval2
        if len(armyval)>5 :
            armyval=armyval[0:6]
            if verbose and self.verbose>2 : print " "*4*(2-self.nv)+"too big army reduced to",armyval
        if self.verbose>2 and verbose and (player1.pv<1 or player2.pv<1) :
            print " "*4*(2-self.nv)+"one dead player in evaluation"
        #if any([not hasattr(c,"costint") for c in player1.hand]) :
        #    for c in player1.hand :
        #        print c,c.name,hasattr(c,"costint")
        val=sum(armyval)-sum(armyval2)+(player1.pv+(player1.pv<8)*(player1.pv-8)*2+(player1.pv>0)*100)*2-(player2.pv+(player2.pv<8)*(player2.pv-8)*2+(player2.pv>0)*100)*2+sum([2+c.costint+c.starcost*2 for c in player1.hand])-3*len(player2.hand)-player1.mana
        if verbose and self.verbose>0 : print " "*4*(2-self.nv)+" val cartes = ",[2+c.costint+c.starcost*2 for c in player1.hand],"contre 3*",len(player2.hand), " ; diff de ",player1.pv*3-player2.pv*3,";-",player1.mana,"mana -  total=",val
        h=[c.name for c in player1.hand if not isinstance(c,SimulationComputer.NotPlayableCard)]
        if len(set(h))<len(h)-3 :
            val-=(len(h)-len(set(h)))*12
            if self.verbose>2 :  print "penalite main avec trop de cartes identiques",(len(h)-len(set(h)))*12
        return val
    def getChoice(self,poss):
        if self.verbose>1 : print " "*4*(2-self.nv)+"appel de getChoice for computer ",self.name
        if self.verbose<-15 : raise "bad verbose" 
        if self.action!=None :
            if self.verbose>2 : print " "*4*(2-self.nv)+"choice ordered"
            action=self.action[0]
            if self.action[1]!=len(poss) or self.action[2]!=poss[action][1] :
                if self.action[1]!=len(poss) : 
                    print "erreur dans player.getChoice (action decidee), devrait avoir ",self.action[1]," possibilites et en a ",len(poss)
                else :
                    print " erreur dans player.getChoice (action decidee) :", self.action[2]," n est pas ",poss[action][1]
                if self.action[2] not in [p[1] for p in poss]  :
                    print "army1 is ",[(a.name,a.ready,a.pv,a.marks.keys()) for a in self.army]
                    print "army2 is ",[(a.name,a.ready,a.pv,a.marks.keys()) for a in self.adv.army]
                    print "mana=",self.mana
                    print "erreur sur le nombre ou nom de poss : la simu a comme possibilite ",[p[1] for p in poss]
                    if len(poss[0])>2 : print "pour ",poss[0][2].name,poss[0][2].ready,poss[0][2].marks.keys(),poss[0][2].bonus
                    print "Ne peut pas faire ",self.action[2]
                    if self.verbose>0 : raise "erreur player.getChoice"
                    print "A la place fait poss[-1]\n"
                    return poss[-1]
                print "peut quand meme faire ",self.action[2],"\n"
                return poss[[p[1] for p in poss].index(self.action[2])]
            if self.verbose>0 : print " "*4*(2-self.nv)+"I have to try action ",action," ( ",len(poss)," possibilities ) "
            self.action=None
            return poss[action]
        else :
            if len(poss[0])>2 : # simulation d attaque
                playing_monster=poss[0][2]
                if self.verbose>1 : print " "*4*(2-self.nv)+"choice of a target for the attack or spell",playing_monster.name
            else :
                playing_monster=None
            if len(poss)>1 :
                from CardGame import SimulationGame
                best,best_val=0,-300
                if self.verbose>0 : print " "*4*(2-self.nv)+"** I am ",self.name,' and I must evaluate ',len(poss),' options'
                if self.verbose>3 : print " "*4*(2-self.nv)+"before getChoice, situation is ",
                Sit_init=self.evaluateSituation(self,self.adv,self.verbose>3)
                if playing_monster :
                    if hasattr(playing_monster,"name") :
                        if self.verbose>1 :  print " "*4*(2-self.nv)+"playing monster is",playing_monster.name
                    else :
                        print " "*4*(2-self.nv)+"playing monster is unamed ",playing_monster
                    if playing_monster in self.army :
                        pmi=self.army.index(playing_monster)
                    else :
                        if self.verbose>3 : print playing_monster," not in ",self.army
                        if self.verbose>3 : print "origin of spell will be added to army"
                        pmi=len(self.army)
                for i in range(len(poss)) :
                    if poss[i][1] in [p[1] for p in poss[0:i]] :
                        if self.verbose>0 : print " "*4*(2-self.nv)+"* skip poss ",i,poss[i][1]
                        continue
                    if self.nv>1  or poss[i][1] != "End your turn" : # le lvl 1 n a pas a evaluer le end turn car il arrivera forcemennt
                        if self.verbose>0 : print " "*4*(2-self.nv)+"* evaluation of poss ",i,poss[i][1]
                        # creation d'une simugame
                        simugame=SimulationGame(self.game)
                        comp1=SimulationComputer(self.name+"-simu1",[],simugame,self.nv-1,[i,len(poss),poss[i][1]],verbose=self.verbose-1)
                        comp2=SimulationComputer(self.adv.name+"-simu2",[],simugame,self.nv-1,verbose=self.verbose-1)
                        comp1.pv,comp2.pv=self.pv,self.adv.pv
                        comp1.army=[CreatureCopy(m,comp1) for m in self.army]
                        #print "army comp1",comp1.army
                        comp2.army=[CreatureCopy(m,comp2) for m in self.adv.army]
                        comp1.hand=[]
                        comp2.hand=[SimulationComputer.NotPlayableCard()]*len(self.adv.hand)
                        for c in self.hand :
                            if isinstance(c,CardInHand) :
                                comp1.hand.append(c.content) # a normal player has cardInHand in hand
                            else :
                                comp1.hand.append(c)  # a simulation computer has card in hand
                        comp1.adv=comp2 ; comp2.adv=comp1
                        comp1.deck=copy(self.deck)
                        comp2.deck=[SimulationComputer.NotPlayableCard()]*10
                        comp1.mana=self.mana
                        comp1.nb_invocation_done_this_turn=self.nb_invocation_done_this_turn
                        comp2.nb_invocation_done_this_turn=0
                        if self is self.game.player1 :
                            simugame.player=simugame.player1=comp1
                            simugame.player2=comp2
                        else :
                            simugame.player=simugame.player2=comp1
                            simugame.player1=comp2
                        simugame.firstplayer=self.game.firstplayer
                        if self.verbose>1 : print " "*4*(2-self.nv)+"avant actions, army de playing ",comp1,"=",[c.name for c in comp1.army]
                        # maintenant on joue la simugame :
                        if playing_monster : # simulation d attaque
                            if pmi < len(comp1.army) :
                                playmo=comp1.army[pmi]
                            else :
                                playmo=CreatureCopy(playing_monster,comp1) # usually a spell card
                                playmo.pv=playmo.max_pv=0
                                comp1.army.append(playmo)
                            if len(poss[0])>3 :
                                comp1.launch(playmo,poss[0][3]) # the playing monster copy is the last
                            else :
                                comp1.select_attack_target(playmo) # the playing monster copy is the last
                        else :  # au niveau 1 : une seule action
                            comp1.play()
                        verify_value=self.evaluateSituation(comp1,comp2,self.verbose>1)                    
                        for m in comp1.army : # on prends au mieux en compte les effets declanches
                            if m.card.pv==0 and m.pv >= 0 :
                                if playing_monster and not m is playing_monster :
                                    if self.verbose>1 : print " "*4*(2-self.nv)+" one additional effect from pending ",m.name,"card before evaluation",m.max_pv
                                    comp1.launch(m,m.bonus[0])
                        if self.nv>1 :
                            while simugame.player is comp1 and comp2.pv>0:
                                if self.verbose>4 : print " "*4*(2-self.nv)+"+comp1 replays"
                                comp1.play()
                            while simugame.player is comp2 and comp2.pv>0 and comp1.pv>0:
                                if self.verbose>4 : print " "*4*(2-self.nv)+"+comp2 plays"
                                comp2.play()
                        val=self.evaluateSituation(comp1,comp2,verbose=True)+verify_value/4.
                        if poss[i][1] == "End your turn" :
                            val+=1.2
                        if self.verbose>0 : print " "*4*(2-self.nv)+"poss",i,poss[i][1],"  val=",val
                    else :
                        #verify_value=Sit_init
                        val=Sit_init+1.2
                    if val>best_val :
                        best=i ; best_val=val
                        #if self.game.player is self : # ordi est en train de jouer
                        #    self.verify_value=verify_value
                        if self.nv>1  and comp2.pv<1 and not ("-simu"  in self.name) :
                            #print "ordi pense gagner ",self.name," contre ",self.adv.name
                            return poss[best]
                if self.verbose>1 or (self.verbose>0 and ("-simu" not in self.name)) : print " "*4*(2-self.nv)+"** Best is ",poss[best][1]," with val=",best_val
                if best_val< -190 and not ("-simu" in self.name):
                    for i in self.hand :
                        i.show()
                    #print "ordi pense avoir perdu"
                    self.hide_cards = False  # avoue sa defaite
                #if not isinstance(self.game,SimulationGame) and (self.game.player is self) :
                #    if len(self.game.all_animations)>0 and hasattr(self,"verify_value") :
                #        del self.verify_value # incapable d evaluer l effet des animations
                #print "poss[best]",poss[best]
                return poss[best]
            else :
                if self.verbose>1 : print " "*4*(2-self.nv)+"**ordi ",self.name,": une seule action (",poss[0][1],")"
                return poss[0]
#    def takeSimulatedTurn(self) :
#        if self.verbose>0 : print "simulated turn of another ",self.name,type(self),self.__class__.__name__
#        self.mana=self.game.turn
#        #self.turn=n
#        for mons in self.army :
#            mons.ready=True
        #print dir(self)
        #self.turnBeginActions()
#        self.play()
#        if self.verbose>1 : print "fin simulated turn"
#    def printSituation(self) :
#        print "computer player ",self.name, len(self.hand)," cartes    ",len(self.army)," monstres"

class SimulationComputer(Computer) :
    class NotPlayableCard :
        costint=6
        starcost=1
        pv=2
        name="NotPlayableCard"
        def getCost(self):
            return 6
    def playCard(self,card) :
        if self.verbose>3 : print " "*4*(2-self.nv)+"appel de playCard for simulationcomputer ",self.name," ",card.name
        if card.pv >=0 :
            self.nb_invocation_done_this_turn+=1
        self.mana-=self.actualCost(card) # avant effet carte car sinon fausse evalation lorsquelle est issue du choix de la cible
        self.hand.remove(card) # pour que si il faut choisir cible au moment de l invocation
        # le hand.remove soit bien pris en compte dans l evaluation
        #print "after remove ",len(self.hand)
        Creature(card,card,self)

        #self.army.append(c) - would be too late here because creature.__init__ can already kill the monster
        #print c,c.name,"appended to army"
        #origin.kill()
    def drawCard(self,n=1,defined=None) :
        if hasattr(self,"verbose") and self.verbose>4 : print " "*4*(2-self.nv)+"appel de simulation drawCard for",self.name
        if not(defined):
            self.hand+=self.deck[:n]           
            self.deck=self.deck[n:]
        else:
            self.hand+=defined
    def spellEffect(self,spell,origin,targets) :
        if hasattr(self,"verbose") and self.verbose>4 : print " "*4*(2-self.nv)+"appel de simulationComputer spellEffect ",spell.getInlineDescription()
        if origin.max_pv==0 :
            origin.pv=-1 # sert aux evaluations de sorts croises
        for t in reversed(targets) : # reversed car si il y a un mort, la liste raccourcit
            spell.effect(origin,t)
        
    def sufferDamage(self,damage) :
        #self.sufferDamage
        for c in self.army:
            if c.max_pv>0 : # on exclue la carte sort 
                for b in c.bonus:
                    damage = b.modifyPlayerSuffer(self,damage)
        self.pv-=damage       
    def orderArmy(self,add=0) :
        pass

