import pygame
from copy import copy
from types import InstanceType,StringType 

img_hero = pygame.image.load("gameAnimationImages/hero_icon.png")
img_mouse_target = pygame.image.load("gameAnimationImages/target.png")
damage_icon= pygame.image.load("gameAnimationImages/damage.png")
img_end_turn = pygame.transform.scale(pygame.image.load("gameAnimationImages/End_Turn.png"),(300,200))
img_end_turn.set_colorkey((0,0,0))
img_opponent_turn = pygame.transform.scale(pygame.image.load("gameAnimationImages/Opponent_Turn.png"),(300,200))
img_opponent_turn.set_colorkey((0,0,0))
img_smash_effect  = pygame.transform.scale(pygame.image.load("gameAnimationImages/smash_effect.png"),(300,200))

#class phase():
#            def __init__(self,dest,time,size,effect):
#                self.dest = dest
#                self.time = float(time)
#                self.size = size
#                self.effect = effect               

def mousecollide(group1,mouse):
    pos=mouse.get_pos()
    c=[s for s in sprites if hasattr(s,"rect") and s.rect.collidepoint(pos)]
    if c :
        c=c[0]
        return c
    else :
        return None
#    if len(group) == 0:
#        return []                  
#    elif len(group) == 1:
#        return group.items()
#    elif any([c.__class__.__name__=="CardInHand" for c in group]):
#       minimum = (-1,0)
#       for c in group:
#           try :
#               if c.n > minimum[0]:
#                   minimum = (c.n,c)
#           except :
#               print "ERROR ___ creature with no variable n: ",c,"  ",type(c)
#       # en general on a des Player_copy.CardInHand, mais on trouve des fois des Player_copy.Creature
#       return [minimum[1]]
#    else:
#        return [group.items()[0]]
#    
class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((16,16))
        pygame.draw.circle(self.image,(155,0,0),(8,8),8)
        self.image.set_colorkey((0,0,0))
        
        self.mode = "normal"
        
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
    def update(self):
        if self.mode == "normal":
            self.image = pygame.Surface((16,16))
            pygame.draw.circle(self.image,(155,0,0),(8,8),8)
            self.image.set_colorkey((0,0,0))
        else:
            self.image = img_mouse_target
            self.image.set_colorkey((0,0,0))
        self.rect.x = pygame.mouse.get_pos()[0]
        self.rect.y = pygame.mouse.get_pos()[1]
        
class EndButton(pygame.sprite.Sprite):
    def __init__(self,screen):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = img_end_turn
                      
        self.rect = self.image.get_rect()
        self.rect.x =  screen[0]/2 -200 - self.image.get_size()[0]/2
        self.rect.y = screen[1] -100 - self.image.get_size()[1]/2
   
    def update(self,player):
        if player.__class__.__name__ == "Player":
            self.image = img_end_turn
        else:
            self.image = img_opponent_turn

class ZoomOn():
    def __init__(self,card):      
        if card:
            self.card = card
            sx,sy=self.card.graphism.get_size()
            self.image = pygame.transform.scale(self.card.graphism,(int(sx*0.75),int(sy*0.75)))
        else:
            self.card = None
       
class Sprite(pygame.sprite.Sprite) :
    def __init__(self,origin,image,size=None) :
        # si origin est une position, il faut donner ensuite une valeur a game
        pygame.sprite.Sprite.__init__(self)
        if type(image)==StringType :
            self.image = pygame.image.load(image)
            self.image.set_colorkey((255,255,255))
            self.image.convert_alpha()
        elif image :
            self.image=image
        else :
            print "call of Sprite with no image"
            self.image=copy(origin.image)
        if not(hasattr(self,"graphism")):
            self.graphism=copy(self.image)
        self.rect = self.image.get_rect()
        if size :
            self.size=size
        else :
            self.size = self.image.get_size()   
        #print "sprite from ",type(origin)
        if isinstance(origin,Sprite) :
            self.center =origin.center
            self.game=origin.game
            #print "copy of game to sprite from",origin.__class__.__name__
        else :
            self.center =origin
        self.setPosition(self.center)
        # ajouter aux sprites visibles
    def setPosition(self,pos) :
        self.center=pos ;
        self.rect.x = self.center[0]-self.size[0]/2
        self.rect.y = self.center[1]-self.size[1]/2
    def getPosition(self) :
        return self.center

class HeroButton(Sprite):
    def __init__(self,owner):      
        x = owner.game.width/2
        y = owner.position_y
        Sprite.__init__(self,(x,y),img_hero)       
        self.image.set_colorkey((0,0,0))
        avatar_image = pygame.transform.scale(owner.avatar_img,(200,200))
        avatar_image.convert_alpha()
        if owner.position_y < 200:
            self.image = pygame.transform.rotate(self.image,180)
            self.in_top=True
        else:
            self.in_top = False
        x = self.image.get_size()[0]/2 - avatar_image.get_size()[0]/2
        y = self.image.get_size()[1]/2 - avatar_image.get_size()[1]/2+(1-2*self.in_top)*(-30)
        self.image.blit(avatar_image,(x,y))
        self.graphism = self.image
        self.font = pygame.font.SysFont("Calibri",68)        
        self.owner = owner  
        self.update()
        
        #print owner.name +" at the "+("top","bottom")[self.in_top],avatar_image," .initialised",(x,y)
        
    def update(self):
        self.image = copy(self.graphism)
        text = self.font.render(str(self.owner.pv),False,(255,0,0))
        self.image.blit(text,(self.size[0]/2-36,self.size[1]/2+(1-2*self.in_top)*(-36)))
        
        
class Animation :
    def __init__(self,subject,phases,new=False) :
        #print "init InGameCard"
        self.subject=subject
        self.anim_phases=phases
        self.anim_num=0
        subject.game.all_animations.append(self)
        if new :
            subject.game.temporary_sprites.add(subject)
        self.init_phase()
        #            def __init__(self,dest,time,size,effect):
    def animate(self):
        if self.pos :
            self.subject.setPosition(self.pos.pop())
            self.subject.size = (int(self.subject.size[0] + self.increase_size[0]), int(self.subject.size[1] + self.increase_size[1]))
            #print "self.subject.size",self.subject.size[0],self.increase_size[0],self.subject.size[1],self.increase_size[1]
            if hasattr(self.subject,"child"):
                for effect in self.subject.child:
                    effect.update()
            if any([s<0 for s in self.subject.size] ) :
                print "self.subject.size ",self.subject.size
                try :
                    print "ERROR with ",self.subject.name
                except :
                    print "ERROR with unnamed sprite"
            else :
                self.subject.image = pygame.transform.scale(self.subject.graphism,self.subject.size)
        self.phase_time += 1
        if self.phase_time == self.phase_end_time:
            self.anim_num += 1
            effect_pending=self.effect
            self.init_phase() # une animation finissant par un effet (sort) est enleve de la liste pour dire qu on peut agir
            if effect_pending : 
                effect_pending()
    def init_phase(self):
        if self.anim_num < len(self.anim_phases):
            self.phase_time = 0
            phase = self.anim_phases[self.anim_num]
            destination,delay,endsize,self.effect=phase             
            #self.actual_phase = phase
            if endsize :
                self.increase_size = ((endsize[0]-self.subject.size[0])/delay,(endsize[1]-self.subject.size[1])/delay)
            else :
                self.increase_size = (0,0)
            if destination :
                self.pos = [(self.subject.center[0]+i*(destination[0]-self.subject.center[0])/delay,self.subject.center[1]+i*(destination[1]-self.subject.center[1])/delay) for i in range(delay+1,0,-1)]
            else :
                self.pos = None
            self.phase_end_time=delay
            #print self.increase
            #print self.increase_size
        else:
            #print "fin animation",type(self.subject)
            #a=len(self.subject.game.all_animations)
            self.subject.game.all_animations.remove(self)
            if self.subject in self.subject.game.temporary_sprites :
                self.subject.game.temporary_sprites.remove(self.subject)
             #print "len ",a,"->",len(self.subject.game.all_animations)
            #self.subject.pos_x = self.destination_x
            #self.subject.pos_y = self.destination_y

class Attach_to_Creature(Sprite):
    def __init__(self,parent,image,pos_mod):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.updateImage(image)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.parent = parent
        self.pos_mod = pos_mod
        self.update()
    def update(self):
        #pos = self.parent.getPosition()
        self.rect.x = self.parent.rect.x + self.pos_mod[0]
        self.rect.y = self.parent.rect.y + self.pos_mod[1]
    def updateImage(self,image):
        return image

class CardInHand(Sprite) :
    def __init__(self,card,player,num,handlen,show,wait) :
        #if player.name=="toto" :
        #    print "__init__",card.name, "     wait=",wait
        self.content = card
        self.name=card.name
        if (not hasattr(card,"image") or not card.image) and show :
            import os
            name=card.name.replace(" ","_")
            card.image = pygame.image.load(os.path.join("Cards",name+".png"))
        if show:                 
            self.image = pygame.transform.scale(card.image,(163, 240))
            self.graphism = copy(card.image)
        else:
            image = pygame.image.load("gameAnimationImages/CardDosArgentum.png")
            self.graphism = image
            self.image = pygame.transform.scale(image,(163, 240))
        self.image.convert_alpha()
        Sprite.__init__(self,player.deck_pos,self.image)
        self.costint = card.costint
        self.starcost=card.starcost
        self.all_effects = {}
        self.game = player.game
        self.player=player

        #self.destination_y = 0
        #self.destination_x = 100 + (player.__class__.__name__=="Player")*(1200)
        time=3+3*(player.__class__.__name__=="Player")    
        phase0  = (self.center,wait+1,self.size,None)
        phase1 = ((self.game.width/2,450),time,(200,300),None)
        phase2 = ((self.game.width/2,450),time/2,(300,450),None)
        phase4 = (self.position(num,handlen),10, self.size,self.takePlace)
        anim_phases = [phase0,phase1,phase2,phase4]
        Animation(self,anim_phases)        
        #self.wait = wait
    #def update():
    #    pass
    def show(self) :
        #print "card is supposed to show"
        # CardInHand has image but it is actually the back
        card=self.content
        if not hasattr(card,"image") or not card.image :        
            name=self.content.name.replace(" ","_")
            image = pygame.image.load("Cards/"+name+".png")
        else :
            image=card.image
        self.image = pygame.transform.scale(image,(163, 240))

    def getCost(self):
        return self.content.getCost()

    def position(self,num,totaln) :
        return self.player.hand.position_x,self.game.height/2+50 - ((totaln-num) * 40-(totaln*2 *(totaln>6)))+totaln*20
        
    def takePlace(self,add=0):
        if self in self.player.hand :
            e=self.player.hand.index(self)
        else :
            e=len(self.player.hand)
        phase=(self.position(e,len(self.player.hand)+add),5, self.size,None)
        Animation(self,[phase]) # function de liste de liste 
        #print "ORGAANISE ",self.content.name
    
    def getInlineDescription(self):
        return self.content.getInlineDescription()
    
 
 
 

    
