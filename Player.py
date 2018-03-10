import random
import pygame      
import math           
#print "import complete"
from copy import copy
from math import floor
from cardPowers import *
from Sprites import CardInHand,Animation
from functools import partial
from Creature import Creature,AnimatedCreature,CreatureCopy

class Player:
    verbose = 0
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
        
    def sendDeck(self) :
        print "send Deck"
        self.game.soc.send(self.name+"\n"+"["+",".join([c.constructor() for c in self.deck])+"]")
        while 1 :
            demand=self.game.soc.recv(1024)
            if demand=="Thanks" :
                print "deck sent with success"
                break
            print "net is asking for ",demand
            from outils import name2file
            cheminImage = name2file("Cards",demand,".png")
            fichierImage = open(cheminImage, "rb")
            #On convertit la taille en string
            import os
            tailleImage = str(os.path.getsize(cheminImage))
            #On rajoute des 0 devant la taille pour avoir 8 char
            tailleImage = "0"*(8-len(tailleImage)) + tailleImage               
            #On a la taille de l'image, on l'envoie au client
            self.game.soc.send(tailleImage.encode())
            #On envoit le contenu du fichier
            self.game.soc.send(fichierImage.read()) 
    def equivalentto(self,other) :
        return self is other             
    def start(self):
        if self.deck:
            self.drawCard(3)
        #self.size = self.icon.size
        self.initialise()
    
    def initialise(self):
        self.center = self.icon.center
        self.mana=self.game.turn
        self.nb_invocation_done_this_turn=0
    
    def drawCard(self,n=1,defined=None) :
        if self.verbose>4 : print " appel de drawCard "
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
        for c in [ c1 for c1 in self.army if c1.pv>0]  :
            for b in c.bonus:
                damage = b.modifyPlayerSuffer(self,damage)
        self.pv-=damage
        if self.pv<1:
            # more to add...
            self.game.end = True
            self.game.winner = self.adv.name
            print " *** "+self.name+" is dead ****"
        self.icon.update()
    def updateImage(self) :
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
        if hasattr(self,"nv") and self.verbose: print " "*4*(2-self.nv)+"player ",self.name,"launch ",spell.getInlineDescription(),"from",origin,"  army is len",len(self.army)
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
            print "spell",spell.__class__.__name__,origin,target
            self.spellEffect(spell,origin,target)
            #print "spell is done"
        if hasattr(origin,"die") and origin.pv<1 and origin.is_dead == False :
            #print "     player launch die "
            origin.is_dead=True
#            if origin.card.pv==0 :
#                
#            else :
#                #print "on passe bien ici (player launch)",origin.name,origin.card.pv
#            
            self.game.effect_list.append([4,origin.id,"die",None])
        print "fin launch from",origin.name,"  army is ,", [m.name for m in self.army]
    def sacrify(self) :
        if len(self.army)>0 :
            self.launch(self.army[0],Sacrifice())
    def spellEffect(self,spell,origin,targets) :
       #if self.verbose>3 : print " "*4*(2-self.nv)+self.name,"appel de spellEffect ",spell.getInlineDescription(),"from",origin.name,"on",[t.name for t in targets]
       if origin.max_pv==0 :
           origin.pv=-1
       if not (origin.id  in self.game.objects)  :
            print "origin",origin.name,origin.id, " not in objects list  for",self.name 
            print "objects list contains", self.game.objects.keys()
            raise Exception("origin error")
       for mons in reversed(targets)  :
           if mons.max_pv >0 :
               for i in mons.bonus :
                   targets=i.modifySpellTarget(targets)
       for t in reversed(targets) :
            #print "effect ",spell.__class__.__name__," on ",t.name,t.id
            if spell.__class__.__name__!="AuChoix" and "choix1"==t.name :
                print "eerrrooe au choix" 
                0/0
            if not (t.id  in self.game.objects)  :
                print "target",t.name,t.id, " not in objects list for",self.name 
                print "objects list contains", self.game.objects.keys()
                raise Exception("target error")
            if not (t is origin) :
                #eff=partial(spell.effect,origin,t)
                self.game.effect_list.append([10,None,spell.constructor()+".effect",[origin.id,t.id]])
                self.spellEffectAnimation(origin,t)
            else :
                #spell.player = self
                spell.effect(origin,t)
    def spellEffectAnimation(self,origin,t) :
        self.game.effect_list.append([11,t.id,"updateImage",None])
        sp=Sprite(origin,"gameAnimationImages/boule_energie_verte.png",[180,180])
        if isinstance(t,Player) : t=t.icon
        phase0=(t.getPosition(),10,None)    
        Animation(sp,[phase0],True)
        
    def update(self,events):
        #print "player update"
        soc=self.game.soc
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:             
                if self.verbose>4 : print "           event Button in Player.update "
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
                            if soc : soc.send("Attack "+t.name[:6]+" "+str(t.id)+"\n")                          
                            break
                    else :                        
                        if soc : soc.send("None\n")
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
                    valide_target=self.spell_targets(origin,spell)
                    if len(valide_target)<1 :
                        print "unvalide target ; no valide target",[m.name for m in valide_target]
                        self.deselection()
                        return
                    for t in contact :
                        if t in valide_target :
                            self.deselection()                     
                            self.spellEffect(spell,origin,[t])
                            if soc : soc.send("aim at "+t.name[:6]+" "+str(t.id)+"\n")
                            break
                        else :
                            print len(contact)," contacts here but no valid target"
                        """
                        if hasattr(t,"name") :
                            print t.name,"is not a possible target"
                        else :
                            print "bad target with no name"
                        """
                else :  
                    # Contact of mouse with hand or creature 
                    #print "Contact of mouse with hand or creature",isinstance(zoomedcard,Creature),zoomedcard.player==self
                    zoomedcard=self.game.zoomed.card
                    if isinstance(zoomedcard,Creature) and zoomedcard.player==self:
                        if zoomedcard.ready :
                            if any([isinstance(b,NePeutPasAttaquer) for b in zoomedcard.bonus]) :
                                    pass
                            else :
                                self.selection(zoomedcard)
                                if soc : soc.send("Attack with "+zoomedcard.name+" "+str(zoomedcard.id)+"\n")
                    elif isinstance(zoomedcard,CardInHand) and zoomedcard.player==self:
                        if self.actualCost(zoomedcard) <= self.mana:
                            if self.nb_invocation_done_this_turn>=5 :
                                print "only 5 monster per Turn can be created"
                            else :
                                self.playCard(zoomedcard)
                                if soc : soc.send("Creation of "+zoomedcard.getInlineDescription()+"\n") 
                    elif zoomedcard :  # should be only None left
                        print "unknown type ?"    
                # Clicked on end button
                if self.game.endturn_button.rect.collidepoint(pos):
                    self.deselection()
                    if not self.ending :
                        if soc : soc.send("End your turn\n")
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
        
    def playCard(self,card) :
        if self.verbose>4 : print " appel de playCard "
        #print "play card"
        if card.content.pv ==0 :
            card.show()
        self.nb_invocation_done_this_turn+=1
        self.mana-=self.actualCost(card)
        self.hand.remove(card)
        self.game.effect_list.append([10,self.id,"createCreature",[card]])
        if isinstance(card,CardInHand) :
            pos0=card.getPosition()
            phase0=([(pos0[0]+self.game.width/2)/2,(pos0[1]+self.game.height/2)/2],10,None)    
            #print "card  position ",card.name,"init",pos0," to end ",phase0[0]
            Animation(card,[phase0],True)

        
    def createCreature(self,card) :
        AnimatedCreature(card,card.content,self,triggerPlayingEffect=True)
        # the card is removed from hand and added to army at end of animation
        #origin.kill()
#    def playCard(self,card) :
#        if self.verbose>3 : print " "*4*(2-self.nv)+"appel de playCard for simulationcomputer ",self.name," ",card.name
#        if card.pv >=0 :
#            self.nb_invocation_done_this_turn+=1
#        self.mana-=self.actualCost(card) # avant effet carte car sinon fausse evalation lorsquelle est issue du choix de la cible
#        self.hand.remove(card) # pour que si il faut choisir cible au moment de l invocation
#        # le hand.remove soit bien pris en compte dans l evaluation
#        #print "after remove ",len(self.hand)
#        Creature(card,self,is_invocation = False,triggerPlayingEffect=True)
    
    
    def endTurn(self):
        #print "player end Turn"
        if self.verbose>4 : print "         appel de endTurn "
        #print "endTurn"
        self.ending=True
        limo = [m for m in self.army]# la boucle avec reversed sur un OrderedUpdate a pose probleme au moins une fois
        for cr in limo: # si un mort, pas d erreur d indice
            if cr.max_pv>0 : cr.endTurn()
        self.game.waitEndOfEffects()
        while self.spell_pending or self.game.animations : 
            #print "end Turn spell pending"
            self.game.update()
            self.game.waitEndOfEffects()
            #self.game.mouse.update()
            #self.update(pygame.event.get())  # on attends que le sort precedent soit lance
        self.ending=False
        #if hasattr(self,"verify_value") :
        #    del self.verify_value
        self.game.changePlayer()
        #print "fin player end Turn"
    def attack_targets(self,monster):
        if self.verbose>4 : print "         appel de attack_targets "
        #print "%%%%%% attack_targets  !"
        targets=[]
        for mons in self.adv.army :
            if mons.pv > 0 :
                targets.append(mons)
        targets.append(self.adv)
        for mons in self.adv.army :
            if mons.pv > 0 :
               for b in mons.bonus :
                  targets=b.modifyDefenseChoice(targets)
        for mons in self.army :
            if mons.pv > 0 and not (mons is monster) :
                targets.append(mons)
        for b in monster.bonus :
            targets=b.modifyAttackChoice(targets)
        if self.verbose>4 : print "       fin attack_targets ",len(targets)
        return targets
    def spell_targets(self,monster,spell) :
        #print "monster-spell",monster.name,spell.__class__.__name__
        #if self.verbose>4 : print "         appel de spell_targets "
        #print "%%%%%% spell_targets  !",spell.__class__.__name__
        if isinstance(spell,AuChoix) : # pas bien : devrait pas utiliser nom specifique de pouvoir
            targets= [m for m in self.army if "choix1"==m.name or "choix2"==m.name  ]
            return targets
        targets=[]
        if spell.positive :
            for mons in self.army :
                if mons.pv>0 and mons.max_pv>0 : targets.append(mons)
            for mons in self.adv.army :
                if mons.pv>0 and mons.max_pv>0 : targets.append(mons)
        else :
            for mons in self.adv.army :
                if mons.pv>0 and mons.max_pv>0 : targets.append(mons)
            for mons in self.army :
                if mons.pv>0 and mons.max_pv>0 : targets.append(mons)       
        if isinstance(spell,Degat) or isinstance(spell,Guerison) :
            targets.append(self.adv)
        targets.append(self)
        for mons in reversed(targets) :
            if not (mons is self) and not (mons is self.adv) and mons.pv>0 :
                for i in mons.bonus :
                    targets=i.modifySpellTargetChoice(targets)
        #if 'simu' not in self.name :
        #print "for player ",self.name,self.id," spell_targets =",[t.name for t in targets]
        return targets
    def castSpellAnimation(self) :
        pass
    def orderArmy(self,add=0):
        #print self.name," orderArmy "
        i=0
        #print "order army ",[(m.name,m.id,m.pv,m.max_pv) for m in self.army ]
        for c in self.army :
            if c.pv>0:
                c.index=i
                #print c.name,"orderArmy takes index",i
                c.takePlace(add=add)
                i+=1
#        for j,c in enumerate([s for s in self.army if s.max_pv==0]) :
#            c.index=i+j+1
#            c.takePlace(add=add)
            
        
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
#        print "computer play"
#        if "simu" not in self.name :
#            print [(c.name , len(c.content.bonus)) for c in self.hand]
        if self.verbose>4 : print " "*4*(2-self.nv)+" computer ",self.name," plays "       
        # verification of situation let by previous action
        #self.verifySituation()
        # now next action ?
        while self.adv.spell_pending :
            print "spell pending"
            pass
        poss=[]
        poss.append((self.endTurn,"End your turn",self))
        for mons in self.army :
                if mons.ready and mons.pv>0 :
                    if (any([isinstance(b,NePeutPasAttaquer) for b in mons.bonus]) 
                        and not any([isinstance(b,ALaPlaceDeLAttaque) for b in mons.bonus]) ) :
                            continue
                    poss.append((partial(self.select_attack_target,mons),"Attack with "+mons.name+" "+str(mons.id),mons))
        for c in self.hand :
            if hasattr(c,"content") :
                content=c.content
            else :
                content=c
            if not isinstance(c,SimulationComputer.NotPlayableCard) :
                if self.actualCost(c)<=self.mana and self.nb_invocation_done_this_turn<5 :
                    if "Creation of "+content.getInlineDescription() not in [p[1] for p in poss] :
                        poss.append((partial(self.playCard,c),"Creation of "+content.getInlineDescription(),content))
        choice=self.getChoice(poss)
        #print "computer ",self.name, " has chosen ",choice[1]
        choice[0]() 
        #if isinstance(self,SimulationComputer) : # action is  instant only for simulation computer
        #    self.verifySituation()
        self.orderArmy()
        #print "end of computer play"
    def select_attack_target(self,monster) :
        if self.verbose>4 : print " "*4*(2-self.nv)+"computer ",self.name," select attack target "       
        #print "attack choice !"
        targets=self.attack_targets(monster)
        #print "for computer , target is ",targets
        if targets :
            poss=[(monster,"Attack "+m.name[:6]+" "+str(m.id),m) for m in targets if isinstance(m,Creature)]
            if self.adv in targets :
                poss.append((monster,"Attack opponent "+str(self.adv.id),self.adv))
                # ttttt
            choice=self.getChoice(poss)
            if choice :
                if self.verbose>1 : print " "*4*(2-self.nv)+"attack target for",monster.name," choice =",choice[2].name,choice[2].id
                target=choice[2]
                monster.combatAnim(target)
            else :
                print "dans le else de select attack target"
        else :
            monster.ready=False
            monster.updateImage()
        #if isinstance(self,SimulationComputer) : # action is  instant only for simulation computer
        #    self.verifySituation()

    def launch(self,origin,spell) :
        if self.verbose>1 : print " "*4*(2-self.nv)+"computer ",self.name," launch",spell.getInlineDescription()," from ",origin.name,origin.id
        #if hasattr(self,"verify_value") : del self.verify_value # le sort va modifier l etat du jeu
        origin.castSpellAnimation()
        target=spell.getTarget(origin)
        #print "for computer launch , target=",target
        if target=="choose" :
            targets=self.spell_targets(origin,spell)
            #print " launch choose de computer",self.name,len(targets)," poss "
#            if 'simu' not in self.name :
#                   print "in launch (choose), targets =", [t.name for t in targets]
            if not targets :
                print " no available target for ",spell.getInlineDescription()
                if origin.pv <=0 :
                    origin.is_dead=True
                    origin.die()
                return 
            poss=[(origin,"aim at "+m.name[:6]+" "+str(m.id),m,spell) for m in targets if isinstance(m,Creature)]
            if self.adv in targets :
                poss.append((origin,"aim at opponent "+str(self.adv.id),self.adv,spell))
            if self in targets :
                poss.append((origin,"aim on you "+str(self.id),self,spell))
            choice=self.getChoice(poss)
            if choice :
               target=[choice[2]]
            else :
                target=None
#            if 'simu' not in self.name :
            #print "           choosen target for spell of",self.name," is ",target[0].name,"  ",target[0].id
#                end
        if target :
            #print self.name,"spell effect"
            self.spellEffect(spell,origin,target)
            #if isinstance(self,SimulationComputer) : # action is  instant only for simulation computer
            #    self.verifySituation()

        #if not (origin in self.army) : print " spell not in army"
        if (origin.card.pv==0) or (origin.pv<1 and not origin.is_dead)  :
            origin.is_dead=True
            #print " player ",self.name," has launched ",spell.__class__.__name__," from ",origin.name,origin.id," and it dies"
            #print " armee ",[o.name for o in self.army]
            #print "p l",origin,self
            self.game.effect_list.append([20,origin.id,"die",[]])

    def update(self,events):
        if self.verbose>4 : print " "*4*(2-self.nv)+"computer ",self.name," update "       
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
        #if self.verbose>4 : print " "*4*(2-self.nv)+"appel de evaluateSituation for computer ",self.name
        armyval=map(lambda x:int(x*100)/100.,[3*i.getValue() for i in player1.army if i.pv>0 ])
        #if verbose and self.verbose>0 : print " "*4*(2-self.nv),len(player1.army)," monstres  ",[i.name for i in player1.army if i.pv>0 ]," de valeur ",armyval 
        armyval2=map(lambda x:int(x*100)/100., [3*i.getValue() for i in player2.army if i.pv>0 ])
        if verbose and self.verbose>2 : print " "*4*(2-self.nv)+"eval monstres",'-'.join([i.name[:3] for i in player1.army if i.pv>0 ]),"val=",armyval," contre ",'-'.join([i.name[:3] for i in player2.army if i.pv>0 ]),"val=",armyval2
        if len(armyval)>5 :
            armyval.sort(reverse=True)
            armyval=armyval[0:5]+[armyval[5]*0.5]+map(lambda x:x*0.1,armyval[6:])
            if verbose and self.verbose>3 : print " "*4*(2-self.nv)+"too big army reduced to",armyval
        if self.verbose>2 and verbose and (player1.pv<1 or player2.pv<1) :
            print " "*4*(2-self.nv)+"one dead player in evaluation"
        if any([not hasattr(c,"costint") for c in player1.hand]) :
            for c in player1.hand :
                print c,c.name,hasattr(c,"costint")
        val=sum(armyval)-sum(armyval2)+(player1.pv+(player1.pv<8)*(player1.pv-8)*2+(player1.pv>0)*100)*1.5-(player2.pv+(player2.pv<8)*(player2.pv-8)*1.5+(player2.pv>0)*100)*1.5+sum([2+c.costint+c.starcost*2 for i,c in enumerate(player1.hand) if i<12])-5*len(player2.hand)-player1.mana*0.5
        if verbose and self.verbose>2 : print " "*4*(2-self.nv),'sum',sum(armyval),-sum(armyval2),'pv',(player1.pv+(player1.pv<8)*(player1.pv-8)*2+(player1.pv>0)*100)*1.5,-(player2.pv+(player2.pv<8)*(player2.pv-8)*1.5+(player2.pv>0)*100)*1.5,'card',sum([2+c.costint+c.starcost*2 for i,c in enumerate(player1.hand) if i<12]),-5*len(player2.hand),'mana',-player1.mana*0.5,"=",val
        #if verbose and self.verbose>0 : print " "*4*(2-self.nv)+" val cartes = ",[2+c.costint+c.starcost*2 for c in player1.hand],"contre 3*",len(player2.hand), " ; diff de ",player1.pv*3-player2.pv*3,";-",player1.mana,"mana -  total=",val
        h=[c.name for c in player1.hand if not isinstance(c,SimulationComputer.NotPlayableCard)]
        if len(set(h))<len(h)-3 :
            val-=(len(h)-len(set(h)))*12
            #if self.verbose>2 :  print "penalite main avec trop de cartes identiques",(len(h)-len(set(h)))*12
        return val
    
#    def evaluateCreature(self,i):
#        value = 0.5
#        value += i.att*math.sqrt(i.pv)+max(i.pv,0.5)*(1+3*i.starcost)+0.1*(i.max_pv - i.pv)
#        value += sum([m[0] for m in i.marks.values()])
#        bonus = []
#        for b in i.bonus:
#            if not(b in bonus) :
#                value += 0.8*b.getCost(i)
#        return value
    
    def getChoice(self,poss):
        if "simu" not in self.name :
            print poss
#            print "avant get choice ",[(c.name , len(c.content.bonus)) for c in self.hand]
        #if self.verbose>1 : print " "*4*(2-self.nv)+"appel de getChoice for computer ",self.name
        if self.verbose<-15 : raise "bad verbose" 
        poss.sort(key=lambda colonnes: colonnes[1])
        if self.action!=None :
            #if self.verbose>2 : print " "*4*(2-self.nv)+"choice ordered"
            action=self.action[0]
            if self.action[1]!=len(poss) or self.action[2]!=poss[action][1] :
                print " "*4*(2-self.nv)+"action decidee, poss are ",[(p[1],p[2].name) for p in poss]
                if len(poss[0])>3 or isinstance(poss[0][0],Creature) : # simulation d attaque
                    if len(poss[0])>3 :
                        print " for spell ",poss[0][3].__class__.__name__, "from ",poss[0][0].name,poss[0][0].id
                    else :
                        print " for attack of ",poss[0][0].name,poss[0][0].id
                print 
                if self.action[1]!=len(poss) :
                    print "erreur dans player.getChoice (action decidee), devrait avoir ",self.action[1]," possibilites et en a ",len(poss)
                else :
                    print " erreur dans player.getChoice (action decidee) :", self.action[2]," n est pas ",poss[action][1]
        
                print "army1 is ",[(a.name,a.ready,a.pv,a.marks.keys(),a.id) for a in self.army]
                print "army2 is ",[(a.name,a.ready,a.pv,a.marks.keys(),a.id) for a in self.adv.army]
                #print "mana=",self.mana
                print "erreur sur le nombre ou nom de poss : la simu a comme possibilite ",[p[1] for p in poss]
                if len(poss[0])>2 : print "pour ",poss[0][2].name,poss[0][2].ready,poss[0][2].marks.keys(),poss[0][2].bonus
                print "Ne peut pas faire ",self.action[2]
                if self.verbose>0 : raise "erreur player.getChoice"
                print "A la place fait poss[-1]\n"
                raise "error"
                print "peut quand meme faire ",self.action[2],"\n"
                return poss[[p[1] for p in poss].index(self.action[2])]
            if self.verbose>1 : print " "*4*(2-self.nv)+"I have to try action ",action,"on",poss[action][2].name," ( ",len(poss)," possibilities ) "
            self.action=None
            return poss[action]
        elif self.nv < 0 :
            if len(poss[0][1])>3 and self.verbose>-1 : print " "*4*(2-self.nv)+"on prend choix 0 sans reflexion ",poss[0][3].__class__.__name__,poss[0][1]
            elif self.verbose>-1 : print " "*4*(2-self.nv)+"on prend choix 0 sans reflexion ",poss[0][1]          
            return poss[0]
        else :
            if len(poss[0])>3 or isinstance(poss[0][0],Creature) : # choix target pour attaq ou sort
                playing_monster=poss[0][0]
                if self.verbose>1 : print " "*4*(2-self.nv)+"choice of a target (",len(poss),") for the attack or spell",playing_monster.name
            else :
                playing_monster=None
            if len(poss)>1 :
                from CardGame import SimulationGame
                best,best_val=0,-300
                if self.nv>0 : print " "
                if playing_monster :
                    if len(poss[0])>3 :
                      if self.verbose>-1 : print " "*4*(2-self.nv)+"** I am ",self.name,' and I must evaluate ',len(poss),' targets for',poss[0][3].__class__.__name__,'from ',playing_monster.name,playing_monster.id
                    else :
                      if self.verbose>-1 : print " "*4*(2-self.nv)+"** I am ",self.name,' and I must evaluate ',len(poss),' targets for',playing_monster.name
                else :
                    if self.verbose>-1 : print " "*4*(2-self.nv)+"** I am ",self.name,' and I must evaluate ',len(poss), "options"
                if self.nv>-1 and self.game.effect_list : print " "*4*(2-self.nv)+"with effect list ",[e[2] for e in self.game.effect_list if e[0]>0]
                if self.nv>-1 : print " "*4*(2-self.nv)+"with ids ",[(m.name[:3],m.id) for m in self.army],[(m.name[:3],m.id) for m in self.adv.army]," and deads ",[(m.name[:3],m.id) for m in self.game.dead_monsters]
                if self.verbose>5 : print " "*4*(2-self.nv)+"before getChoice, situation is ",
                Sit_init=self.evaluateSituation(self,self.adv,verbose=(self.verbose>3))
                #print " "*4*(2-self.nv)+"poss are ",[(p[1],p[2].name) for p in poss]
                if playing_monster :
                    if hasattr(playing_monster,"name") :
                        if self.verbose>1 :  print " "*4*(2-self.nv)+"playing monster is",playing_monster.name
                    else :
                        print " "*4*(2-self.nv)+"playing monster is unamed ",playing_monster
#                    if playing_monster in self.army :
#                        pmid=self.army.index(playing_monster)
#                    else :
#                        if self.verbose>3 : print playing_monster.name," not in army"
#                        #if self.verbose>3 : print "origin of spell will be added to army"
#                        pmi=len(self.army)
                for i in range(len(poss)) :
#                    if "simu" not in self.name :
#                        print "avant test ",i,[(c.name , len(c.content.bonus)) for c in self.hand]
                    if i>0 and poss[i][2].equivalentto(poss[i-1][2]) :
                        if self.nv>-1 : print " "*4*(2-self.nv)+"skip poss ",i,poss[i][1]
                        continue
#                    else :
#                        print poss[i][2].name ,"different de ",poss[i-1][2].name
                    if self.verbose>5 : print " "*4*(2-self.nv)+"still with effect list ",[e[2] for e in self.game.effect_list if e[0]>0] 
                    if self.verbose>0 : print " "*4*(2-self.nv)+"* evaluation of poss ",i,poss[i][1],poss[i][2].name
                    if self.nv>1  or poss[i][1] != "End your turn" : # pour le lvl 1  le end turn s evalue plus facilement
                        # creation d'une simugame
                        #print " avant crea silu game ",self.name," objects list ",[str(k)+self.game.objects[k].name for k in self.game.objects.keys()]
#                        if playing_monster :
#                            print "att from ",playing_monster.name,playing_monster.id," poss avant simugame",poss
                        simugame=SimulationGame(self.game,self,[i,len(poss),poss[i][1]])
                        comp1=simugame.player
                        comp2=comp1.adv
                        if self.verbose>2 : print " "*4*(2-self.nv)+"avant actions de debut,",poss[i][1],", army de simulation ",comp1.name,"=",[c.name[0:6] for c in comp1.army]
                        # maintenant on joue la simugame :
                        if playing_monster : # simulation d attaque
                            inarmy=[m for m in comp1.army if m.id==playing_monster.id]
                            if not inarmy :
                                inarmy=[m for m in comp1.adv.army if m.id==playing_monster.id]
                            if inarmy :
                                #print comp1.name,"cas special 1"
                                playmo=inarmy[0]                         
#                                print "%%",pmi,playing_monster.name,playing_monster.id,playmo.name,playmo.id
#                                print "%%",[m.id for m in self.army],[m.id for m in comp1.army]
                            else :
                                #print comp1.name,"cas special 2"
#                                playmo=CreatureCopy(playing_monster,comp1) # usually a spell card
#                                playmo.pv=0
#                                comp1.army.append(playmo)
#                                comp1.game.objects[playmo.id]=playmo
#                                comp1.game.effect_list.append([1,playmo.id,"die",None])
                                print ('army is ',[(m.name[:5],m.id) for m in comp1.army ])
                                for m in simugame.dead_monsters :
                                    if m.id==playing_monster.id :
                                        playmo=m
                                        break
                                else :
                                    print "origin of spell not here",playing_monster.name,playing_monster.id
                                    print "deads are in siugame",[m.id for m in simugame.dead_monsters]
                                    print "deads are in real game",[m.id for m in self.game.dead_monsters]
                                    raise
                            if len(poss[0])>3 :
                                comp1.launch(playmo,poss[0][3]) 
                            else :
                                comp1.select_attack_target(playmo)
                        else :  # au niveau 1 : une seule action
                            comp1.play()
                        #print "toto simu effect list ",simugame.effect_list
                        if comp2.pv <= 0 :
                            if self.nv>1 and not ("-simu"  in self.name) : print "ordi pense gagner directement contre ",self.adv.name," avec ",poss[i][1]
                            return poss[i]
                        if self.nv>-6 :
                            simugame.waitEndOfEffects()
                        if comp2.pv <= 0 :
                            if self.nv>1 and not ("-simu"  in self.name) : print "ordi pense gagner apres effet contre ",self.adv.name," avec ",poss[i][1]
                            return poss[i]
                        verify_value=self.evaluateSituation(comp1,comp2,verbose=((self.verbose>3)and(self.nv>1)))                    
                        if self.verbose>5 : print " "*4*(2-self.nv)+"j evalue toujours ",poss[i][1]
                        if self.nv>1 and not self.ending :
                            realmana=comp1.mana # le mana qui compte dans eval ne doit pas considerer la suite des evenements
                            while simugame.player is comp1 and comp2.pv>0:
                                if self.verbose>3 : print " "*4*(2-self.nv)+"+comp1 replays"
                                comp1.play()
                                simugame.waitEndOfEffects()
                                if comp2.pv <= 0 :
                                    if self.nv>1 and not ("-simu"  in self.name) : print "ordi pense gagner contre ",self.adv.name," avec ",poss[i][1]
                                    return poss[i]
                            if self.verbose>4 : print " "*4*(2-self.nv)+"at end of my turn armies (pv) are",[(m.name[:5],m.pv) for m in comp1.army],"contre",[(m.name[:5],m.pv) for m in comp2.army],[m.id for m in comp1.army]+[m.id for m in comp2.army]
                            while simugame.player is comp2 and comp2.pv>0 and comp1.pv>0:
                                if self.verbose>4 : print " "*4*(2-self.nv)+"+comp2 plays"
                                comp2.play()
                                simugame.waitEndOfEffects()
                            if self.verbose>2 :print " "*4*(2-self.nv)+"at end of both turns armies are",[(m.name[:5],m.pv) for m in comp1.army],"contre",[(m.name[:5],m.pv) for m in comp2.army]
                            comp1.mana=realmana
                        val=self.evaluateSituation(comp1,comp2,verbose=True)+verify_value/25.
                        if poss[i][1] == "End your turn" :
                            val+=0.3
                            #if self.nv>1 : 0/0
                        if self.verbose>0 : print " "*4*(2-self.nv)+"poss",i,poss[i][1],"  val=",val
                    else :
                        #verify_value=Sit_init
                        val=Sit_init*(1.+1./25.)+1.-self.nv/2.  # evaluation tres rapide du fin du tour pour un level 1
                        if self.verbose>0 : print " "*4*(2-self.nv)+"poss",i,poss[i][1],"  val=",val                        
                    if val>best_val :
                        best=i ; best_val=val
                        #if self.game.player is self : # ordi est en train de jouer
                        #    self.verify_value=verify_value
                if self.verbose>-2 or (self.verbose>-2 and ("-simu" not in self.name)) : print " "*4*(2-self.nv)+"** Best is ",poss[best][1]," with val=",best_val
                if self.nv==2 and self.mana>=self.game.turn and len(poss)>2 and poss[best][1]=="End your turn" :
                    self.mana=int(self.mana/2.1)  # on evite ici que le nv 2 renonce a jouer de peur que nv 1 invoque une betise
                    if self.verbose>1 : print "fin trop anticipee on recommence la reflexion avec mana reduit"
                    self.play()
                    return [str]  # to do nothing
                if best_val< -190 and not ("-simu" in self.name):
                    for i in self.hand :
                        i.show()
                    print "ordi pense avoir perdu"
                    self.hide_cards = False  # avoue sa defaite
                #if not isinstance(self.game,SimulationGame) and (self.game.player is self) :
                #    if len(self.game.all_animations)>0 and hasattr(self,"verify_value") :
                #        del self.verify_value # incapable d evaluer l effet des animations
                #print "poss[best]",poss[best]
#                if "simu" not in self.name :
                return poss[best]
            else :
                if self.verbose>-2 : print " "*4*(2-self.nv)+"**ordi ",self.name,": une seule action possible (",poss[0][1],")"
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
    verbose = 0
    class NotPlayableCard :
        costint=5
        starcost=0
        pv=2
        name="NotPlayableCard"
        def getCost(self):
            return 5  # doit correspondre a la valeur dans evaluate situation
#    def playCard(self,card) :
#        if self.verbose>3 : print " "*4*(2-self.nv)+"appel de playCard for simulationcomputer ",self.name," ",card.name
#        if card.pv >=0 :
#            self.nb_invocation_done_this_turn+=1
#        self.mana-=self.actualCost(card) # avant effet carte car sinon fausse evalation lorsquelle est issue du choix de la cible
#        self.hand.remove(card) # pour que si il faut choisir cible au moment de l invocation
#        # le hand.remove soit bien pris en compte dans l evaluation
#        #print "after remove ",len(self.hand)
#        Creature(card,self,is_invocation = False,triggerPlayingEffect=True)

        #self.army.append(c) - would be too late here because creature.__init__ can already kill the monster
        #print c,c.name,"appended to army"
        #origin.kill()
    def drawCard(self,n=1,defined=None) :
        if self.verbose>4 : print " "*4*(2-self.nv)+"appel de simulation drawCard for",self.name
        if not(defined):
            self.hand+=self.deck[:n]           
            self.deck=self.deck[n:]
        else:
            self.hand+=defined
    def spellEffectAnimation(self,origin,t) :
        pass
    def sufferDamage(self,damage) :
        #self.sufferDamage
        for c in self.army:
            if c.max_pv>0 and c.pv>0 : # on exclue la carte sort 
                for b in c.bonus:
                    damage = b.modifyPlayerSuffer(self,damage)
        self.pv-=damage       
    def createCreature(self,card) :
        Creature(card.content,self,triggerPlayingEffect=True)
        
    def orderArmy(self,add=0) :
        pass
    
    def updateImage(self) :
        pass

class HostedPlayer(Computer0) :
    def __init__(self,game) :
        self.game = game
        self.hand=pygame.sprite.OrderedUpdates()
        self.army= pygame.sprite.OrderedUpdates() # includes weapons and unbunded permanent spells
        self.max_pv = self.pv=30       
        self.player=self
        self.att=0            
        self.bonus=[]
        self.Attacker_selected = None
        self.spell_pending = None
        self.mana=0
        self.ending=False
        self.hide_cards = True
        print "Hosted player is ok"
        self.remains=""
    
    def receiveDeck(self) :
        print "try to receive deck"
        import time
        time.sleep(0.5) # pour que le send en face soit fini
        mess=self.game.soc.recv(1024*16)
        try :
            name,cards=mess.split("\n")
            self.name=name
        except :
            print "got message ",mess
            print "should have name\ndeck"
            raise
        from Card import evalCard,all_monsters
        try :
            self.deck=evalCard(cards) # le jeu est deja melange
        except :
          print "error with",cards
          for c in cards.strip().strip("[]").split("Card(").strip(",") :
            try :
                evalCard("Card("+c) # all_monsters contient des instances
            except :
                print "problem with ",c
        print "opponent name ",name
        #print "deck",deck
        asking=set()
        for c in self.deck :
            c.costint=int(floor(c.getCost()))
            c.starcost=c.getStars()
            print "c.constructor()",c.constructor()
            for name in c.constructor().split('Card("')[1:] :
                #print "nam brut",name
                name=name.split('"')[0]
                #print "name modif",name
                if name not in all_monsters or c.getInlineDescription()!=all_monsters[c.name].getInlineDescription() :
                    asking.add(name)
        for name in asking :
            self.game.soc.send(name)
            print "asking for image ",name
            tailleImage = self.game.soc.recv(8)
            #On convertit la taille de l'image en entier (en octets)
            tailleImage = int(tailleImage.decode())
            #Contenu loaded
            contenuTelecharge = 0
            #Le fichier qui va contenir l'image
            from outils import name2file
            filename=name2file("",name,".png")
            fichierImage = open(filename,"wb")               
            #On continue la lecture up to th end
            while contenuTelecharge < tailleImage:
                #On lit les 1024 octets suivant
                contenuRecu = self.game.soc.recv(1024)
                #On enregistre dans le fichier
                fichierImage.write(contenuRecu)
                contenuTelecharge += len(contenuRecu)
            fichierImage.close()
            c.image = pygame.image.load(filename)
            print "ok for one"
        for c in self.deck :  # si l image est nouvelle on l affecte a la carte 
            if c.name in asking :
                filename=name2file("",c.name,".png")
                c.image=pygame.image.load(filename)
        print "net player cards are received"
        self.game.soc.send('Thanks')  # echo
        
    def getChoice(self,poss):
        #print "get choice from distant player"
        print "try to receive"
        mess=""
        while (not mess) and (not self.remains) :
            mess=self.game.soc.recv(1024*2).strip()
        if self.remains :
            mess=self.remains+'\n'+mess
        if "\n" in mess :
            print "received in total ",mess
            mess,self.remains=mess.split("\n",1)
        else :
            self.remains=""
        mess=mess.strip()
        print "got ",mess
        for p in poss :
            if mess.strip()==p[1] :
                break
        else :
            if mess.strip()!="None" :
                print "error actions does not correspond"
                for i,p in enumerate(poss) :
                    print i,":",p[1]
            p=None
        return p


