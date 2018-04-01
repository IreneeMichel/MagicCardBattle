from math import floor
#from pygame import image
import pygame
import re
UP=re.compile('(?=[A-Z])')
import os
#import pickle
import shutil
from Tkinter import PanedWindow,Label,StringVar,Entry,OptionMenu,Button,Spinbox
from tkMessageBox import askyesno,showinfo
from Tkinter import TOP,VERTICAL,HORIZONTAL,BOTH,CENTER,E,W
#import tkFont
from PIL import Image, ImageTk
import glob
#from tkMessageBox import rr
#os.chdir("C:\\Users\\Test\\Documents\\programmation\\MCB2")

#import cardPowers
from Bonus import getBonusMenu
import Spell 

from outils import file2name,name2file
from outils import localopen

def readMonsters(filename) :
    monsters={}
    with open(filename,"r") as filepickle :
        for m in filepickle :
            try :
                c=evalCard(m)                
                monsters[c.name]=c
            except :
                print "in file ",filename
                print "ERROR reading line :",m
                raise
    return monsters

def evalCard(str1) : # fonctionne sur carte comme sur liste de cartes
    import cardPowers
    import Target
    import Level
    return eval(str1)    

def centerText(screen,position,text,fontSize,color,bg=None) :
    font = pygame.font.SysFont("Calibri Bold",fontSize)
    try:
        textImage = font.render(text,False, color)
    except:
        print "problem with color ",color,"- black (0,0,0)  is taken"
        textImage = font.render(text,False, (0,0,0))
    #textImage = font.render(text,False, (0,0,0),background=bg)
    x,y=textImage.get_size()
    screen.blit(textImage,(position[0]-x/2.,position[1]-y/2.))

#def remove_widget(o,max_depth=8) :
#    if max_depth==8 : print "debut remove widget"
#    for at in ("parent","master","card") :
#        if hasattr(o,at) :
#            delattr(o,at)
#    if max_depth==8 : print "1 remove widget"
#    for at in ("add_target","addTarget_wid", "widget","content","value","value2",
#          "level_wid","level_wid2","stars","cost","card_win","opening","category",
#          "image","delete","spellContainer","spell_list","restrict" ) :
#       if hasattr(o,at) :
#           #print '  '*(8-max_depth)+' '+at+'  removed'
#           delattr(o,at)
#    if max_depth==8 : print "2 remove widget"
#    for o2n in dir(o) :
#        o2=getattr(o,o2n)
#        cn=o2.__class__.__name__
#        if not (cn  in ["instancemethod"]) and not ("__"  in o2n) and (not hasattr(o2.__class__,o2n)):
#            print '  '*(8-max_depth)+o2n+ '    '+cn
#        if type(o2)==type([]) :
#            #print o2n," is list",o2
#            for o3 in o2 :
#                if type(o3)==type(Card("Troll gris",4,4)) and max_depth>0 :
#                    remove_widget(o3,max_depth-1)
#        if type(o2)==type(Card("Troll gris",4,4)) and max_depth>0 and o2n!="card" :
#            remove_widget(o2,max_depth-1)
#    if max_depth==8 : print "fin remove widget"
 
               
class Card :
    def __init__(self,name="Nom monstre",att=1,pv=1,bonus=None,photo='',monster_type="unknown") :
        self.name=name
        self.att = att
        self.pv = pv
        if not bonus :
            bonus=[] # a cause du fonctionnement etrange de python pour les valeurs d arguments [] par defaut
        self.bonus=bonus
        self.is_spell=(pv<1)
        self.photofile=photo
        self.dumping_file = os.path.join("CardFiles",monster_type+"_monsters.sav")
        self.monster_type = monster_type
        #global all_monsters
        name=self.name.replace(" ","_")
        self.content=self
#        try :
#            self.image = image.load(os.path.join("Card",name+".png"))
#        except :
#            self.image=None
    def equivalentto(self,other) :
        return self==other
    def show(self) :
        pass
    def constructor(self) :
        return ('Card("'+self.name+'",'+str(self.att)+","+str(self.pv)+
            ",["+",".join([p.constructor() for p in self.bonus])+"],"+
             repr(self.photofile)+",'"+self.monster_type+"')")
    def takePlace(self,*ar1,**ars) :
        pass
    def addBonus(self,bonus) :
        self.bonus.append(bonus)
    def getCost(self) :
        if self.pv > 0 :
            cost=self.att/2.+self.pv/2.+sum([p.getCost(self) for p in self.bonus])
        else :
            #print self.bonus
            #if self.bonus :
            #print self.bonus[0].getCost
            #print self.bonus[0].getCost()           
            if len(self.bonus)>1 : print "** anomalie **"
            cost=sum([p.getCost() for p in self.bonus])+0.5*(len(self.bonus)-1)
        if cost < 0:            cost = 0
        if hasattr(self,"cost") and self.cost!=None :
            # pour les monstres du save, l attribut cost est None        
            print "cout=",cost," so ",int(floor(cost))
            self.cost.set(int(floor(cost)))
            self.getStars()
        return cost
    def getStars(self):
        stars = sum([p.getStars() for p in self.bonus])
        if stars>2 : stars=(stars-1)*2
        if hasattr(self,"stars")  and self.stars != None :
            # pour les monstres du save, l attribut stars existe = None
            self.stars.set('* '*stars)
        #print "stars=",stars
        return stars
    def getDescription(self):
        for b in reversed(self.bonus) :
            try :
                b.getDescription()
            except Exception :
                self.bonus.remove(b)
        return self.name +" ("+str(self.att)+"  "+str(self.pv)+'\n'*bool(self.bonus)+'\n'.join(
            [b.getDescription() for b in self.bonus]) +" )"
    def getInlineDescription(self):
        for b in reversed(self.bonus) :
            try :
                b.getInlineDescription()
            except Exception :
                self.bonus.remove(b)
        return self.name +" ("+str(self.att)+"  "+str(self.pv)+' '.join(
            [b.getInlineDescription() for b in self.bonus]) +" )"
    def postAndSave(self,*args):
        if self.name=="nom monstre" or self.name=="change name" or self.name in Card.blocked_creature :
            self.name="change name"
            self.refreshWidget()
            return
        if not self.verifyBonus() :
            return            
        self.deleteCreature(self.name)
        temp=self.category.get()
        pygame.init()
        fenetre=self.card_win.master
        self.card_win.pack_forget()
        self.save(None)
        

        done=False
        while not done :
            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    done=True
        pygame.display.quit()
        self = Card("nom monstre",1,1)
        #card.pack_forget()
        self.initWidget(fenetre)
        self.category.set(temp)
        self.setFile("dummy_arg")

    def verifyBonus(self) :
        nb=[b.__class__.__name__ for b in self.bonus]
        if len(set(nb))!=len(nb) :
            showinfo("Not Allowed","You can't have twice the same bonus")
            return False
        for b1,b2 in [("Insaisissable","Provocation"),("Insaisissable","Inciblable"),
                      ("Camouflage","Provocation"),("Camouflage","ChaqueTour"),("NePeutPasAttaquer","ALaPlaceDeLAttaque"),
                    ("GardienDeVie","QuandIlEstBlesse"),("Charge","NePeutPasRisposter"),("Furie","ALaPlaceDeLAttaque"),
                    ("NePeutPasRiposter","NePeutPasAttaquer"),("NePeutPasRiposter","CoutReduit"),
                    ("Charge","CriDeGuerrre"),("Insaisissable","InsensibleALaMagie"),("Charge","Errant"),("CriDeGuerre","Errant"),
                    ("BonusParEnnemi","Determine"),("QuandIlEstBlesse","Incassable"),("Souffrant","QuandIlEstBlesse") ] :
            if b1 in nb and b2 in nb :
                showinfo("Not Allowed","You can't have this combination of powers: {0} and {1}".format(b1,b2))
                return False
        total=self.constructor()
        if "QuandUnAllieEstTue" in nb and (("Spell.Invocation" in total) or ("CopieMain"  in total) or ("PlaceCarteDansMain" in total)):
            showinfo("Not Allowed","You can't have anything to do with Invocation or card creation if you have QuandUnAllieEstTue")
            return False
        return True
 
    def save(self,*args):

        image = self.createImage()
        
        print "apres createImage"
        name=self.name.replace(" ","_")
        pygame.image.save(image,"Cards/"+name+".png")
        print "save image done"
        # now new monster
        loaded_monsters=readMonsters(self.dumping_file)
        #print "Monsters from file = ",file_monsters
        #remove_widget(self)
        loaded_monsters[self.name] = self
        #print "Monsters from file (after) = ",file_monsters
        global all_monsters
        all_monsters.update(loaded_monsters)
        #print "window reinit done"
        with open(self.dumping_file,"wb") as savefile :
            savefile.write("\n".join([m.constructor() for k,m in sorted(loaded_monsters.items())]))
#        with open(self.dumping_file+".old","rb") as filepickle :
#            print "now in file", self.dumping_file,":",pickle.load(filepickle).keys()
#            filepickle.close()
        with open(os.path.join("CardFiles","all_monsters.sav"), "wb" ) as f :
            f.write("\n".join([m.constructor() for m in all_monsters.values()]))
        recupfile=os.path.join("CardFiles","recup_monsters.sav")
        if (not os.path.isfile(recupfile)) or len(all_monsters)>=len(open(recupfile,'r').readlines()):
            with open(recupfile, "wb" ) as f :
                f.write("\n".join([m.constructor() for k,m in sorted(all_monsters.items())]))
            print "SAVED in all_monsters.sav and recup_monsters.sav"
        else:
            print "WARNING : Recup monster file bigger than all monsters file"

    def initWidget(self,fenetre) :
        #print "init"
        self.card_win = PanedWindow(fenetre, orient=VERTICAL)
        fenetre.child=self
        self.refreshWidget()
    def Open(self,*args) :
        print "open monster ",  self.opening.get()
        #deck_with_card =  self.deck_check(self.opening.get())
        lv = max(eval(localopen("progression2","r").read()).values())
        creature = Card.monster_list[self.opening.get()]
        if creature.monster_type != "all" and not(creature.monster_type != "unknown" and lv<8 and creature.name in Card.blocked_creature) :
            self.card_win.pack_forget()
            fenetre=self.card_win.master
            #for i in Card.monster_list.keys() :
            #    print i, Card.monster_list[i].getInlineDescription()
            self = Card.monster_list[self.opening.get()]
            print self.name +" loaded"
            if self.pv<1 :
                self.is_spell=True
            else :
                self.is_spell=False
            #self.card_win.pack_forget()
            for b in self.bonus:
                b.parent = self.bonus
                b.card = self
            self.initWidget(fenetre)
        else:
            showinfo("Sorry","You can't open this monsters because he comes from the campaign.")
         
    def clicDelete(self,*args) :
        #self.card_win.pack_forget()
        #fenetre=self.card_win.master
        """
        for i in all_monsters.keys() :
            print i, all_monsters[i].getInlineDescription()
            
        """
        
        creature= self.delete.get()
        if creature in Card.blocked_creature :
            print "not possible : creature in campaign"
            self.delete.set('delete')
            return
        if askyesno('Beware!', 'Confirm the deletion of '+creature+"?"):                
            self.deleteCreature(creature)
        self.card_win.pack_forget()
        #self.initWidget(fenetre)
        self.setFile(*args)
    

    def deleteCreature(self,creature) :
        dm=None
        global all_monsters
        if not creature in all_monsters :
            print creature," is not in all_monsters"
            try :
                fm=os.path.join("CardFiles",self.category.get()+"_monsters.sav")
                dm = readMonsters(fm)
            except:
                print "error reading file ",fm
        else :
            print "delete monster ",  creature
            try :
                fm = os.path.join("CardFiles",(all_monsters[creature].monster_type)+"_monsters.sav")
                dm = readMonsters(fm)
            except:
                print "ERROR : no type for ",creature, " or read error"
            del all_monsters[creature]
            fall=os.path.join("CardFiles","all_monsters.sav") 
            with open(fall,"wb") as savefile :
                savefile.write("\n".join([m.constructor() for m in all_monsters.values()]))            
            print "deletion of monster ",  creature, "done"
            shutil.copyfile(fall,"CardFiles/recup_monsters.sav")
        if dm and creature in dm :
            del dm[creature]
            with open(fm,"wb") as savefile :
                savefile.write("\n".join([m.constructor() for m in dm.values()]))
            print "deletion of monster ",  creature, " in ",fm," done"                
        else :
            print creature," not found in dedicated file"
            
            
        
    def choosePhoto(self,*args) :
        from tkFileDialog import askopenfilename
        #Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        filename = askopenfilename(defaultextension=".gif",filetypes=[('Jpg file','*.jpg'),('GIF file','*.gif')]) # show an "Open" dialog box and return the path to the selected file
        if filename:
            import os.path
            chem=os.path.dirname(os.path.realpath(__file__)).replace('\\','/')+'/'
            print chem
            if chem in filename :
                filename=filename.replace(chem,'')
                print "filename modif",filename
            try :
                Image.open(filename)
                #ImageTk.PhotoImage(monimage)
                self.photofile=filename
                print "photo choosen !"
            except Exception :
                print "echec ouverture"
        self.refreshWidget()

    def setFile(self,*args):
        self.dumping_file = os.path.join("CardFiles",self.category.get()+"_monsters.sav")
        print "Change dumping file to ",self.dumping_file
        self.monster_type = self.category.get()
        Card.monster_list=readMonsters(self.dumping_file)
        #from cardPowers import *
        self.refreshWidget()

    def refreshWidget(self) :
        #print "refresh"
        self.card_win.pack_forget()
        
        #Card window      
        self.card_win = PanedWindow(self.card_win.master, orient=VERTICAL)
        self.card_win.pack(side=TOP, expand=True, fill=BOTH, pady=2, padx=2)
        
        
        #Create the name zone
        name_zone=PanedWindow(self.card_win, orient=HORIZONTAL)
        name = StringVar() 
        name.set(self.name)
        def modifName(*args) :
            old = self.name in Card.blocked_creature
            self.name=name.get()
            if old or self.name in Card.blocked_creature :
                self.refreshWidget()
        name.trace("w", modifName)
        name_wid=Entry(name_zone, width=30,textvariable=name)
        name_wid.pack()
        name_zone.add(name_wid)
        #Create the cost ad star stringvar
        #print int(floor(self.getCost()))
        self.cost=StringVar()
        self.stars=StringVar()
        cost_wid=Label(None, textvariable=self.cost, background='red',width=5, anchor=W)
        star_wid=Label(None, textvariable=self.stars, background='blue', anchor=E)
        self.cost.set(str(int(floor(self.getCost()))))
        self.stars.set("*"*self.getStars())
        #Add them in name zone
        name_zone.add(cost_wid)
        name_zone.add(star_wid)
        
        
        #Create an Image Zone
        image_zone=Button(self.card_win,  command=self.choosePhoto)
        if hasattr(self,"photofile") and self.photofile :            
            print "Image: ",self.photofile
            try :
               img=Image.open(self.photofile)
            except :
               decomp=self.photofile.split('/')
               for i in range(1,6) :
                   try :
                       fname="/".join(decomp[-i:])
                       print "try to open",fname
                       img=Image.open(fname)
                       self.photofile=fname
                       break
                   except :
                       self.photofile=None
        if self.photofile :
            w, h = img.size
            if w>300 or h>200 :
               img=img.resize((w/2,h/2),Image.LINEAR)
            image_zone.image=ImageTk.PhotoImage(img)
            image_zone.config(image=image_zone.image)
            #print "IMAGE CHANGED"
        else :
            from os import path
            fname=self.name.replace(" ","_")
            if path.isfile("Cards/"+fname+".png") :
                image_zone.config(text='image can be taken from\n'+"Cards/"+fname+".png",background='white',anchor=CENTER)
            else :
                image_zone.config(text='clic to choose image',background='white',anchor=CENTER)

        image_zone.pack
        
        
        # POWER ZONE
        power_zone=PanedWindow(self.card_win, orient=VERTICAL)
        #fenetre=self.card_win.master
        def removePowerCreator(px) :
            def removePower(*args) :
                #print 'avant',list_pow
                self.bonus.remove(px)
                #print 'apres',list_pow
                #self.card_win.pack_forget()
                self.refreshWidget()
            return removePower
        for p in self.bonus :
            powline =  PanedWindow(self.card_win, orient=HORIZONTAL)
            pow_wid=p.initWidget(powline)
            powline.add(pow_wid)
            removepow=Button(powline, text="X", command=removePowerCreator(p), anchor=E)
            removepow.pack()
            powline.add(removepow)
            power_zone.add(powline) 
        def addPower(*args) :
            name=addBonus.get()
            print "added :",name
            import cardPowers
            self.bonus+=[eval('cardPowers.'+name+'()')]
            self.bonus[-1].parent=self.bonus
            self.bonus[-1].card=self
            #self.card_win.pack_forget()
            self.refreshWidget()
        #Add bonus Option menu
        addBonus = StringVar(power_zone)
        addBonus.set("add bonus") # default value
        if not self.pv:  addBonus_wid = Spell.getSpellMenu(power_zone, addBonus)
        else: addBonus_wid = getBonusMenu(power_zone, addBonus) 
        addBonus.trace('w', addPower)
        if self.pv>0 or len(self.bonus)==0 :
            addBonus_wid.pack()
            #Add this to power zone
            power_zone.add(addBonus_wid)
        
        #Create save zone
        save_zone = PanedWindow(self.card_win, orient=HORIZONTAL)
        lv = max(eval(localopen("progression2","r").read()).values())
        if self.monster_type != "all" and not(lv<8 and self.name in Card.blocked_creature) :
            save_wid = Button(save_zone, text="Save", command=self.postAndSave)
        elif self.monster_type != "all" : 
            save_wid = Button(save_zone, text="creature in campaign", command=None)
        else:
            save_wid = Button(save_zone, text="nead type", command=None)
        save_wid.pack()
        #Create the open button
        save_zone.pack()        
        if Card.monster_list.keys():
            self.opening = StringVar(save_zone)
            self.opening.set("Open")
            choice = [na for na in Card.monster_list.keys() if na not in Card.blocked_creature]
            choice.sort()
            #print all_monsters.keys()
            open_wid = OptionMenu(save_zone, self.opening,*choice)
            self.opening.trace('w', self.Open)
            open_wid.pack()
            save_zone.add(open_wid)
        
        if Card.monster_list.keys():
            self.delete = StringVar(save_zone)
            self.delete.set("Delete")
            choice = [na for na in Card.monster_list.keys() if na not in Card.blocked_creature]
            choice.sort()
            delete_wid = OptionMenu(save_zone, self.delete,*choice)
            self.delete.trace('w', self.clicDelete)
            delete_wid.pack()
            save_zone.add(delete_wid)
        
        #Create the type button
        self.category = StringVar(save_zone)
        self.category.set(self.monster_type)
        choice = [file2name(t,"_monsters.sav") for t in glob.glob("CardFiles/*_monsters.sav")]
        if "recup" in choice:
            choice.remove("recup")
        #print all_monsters.keys()
        category_wid = OptionMenu(save_zone, self.category,*choice)
        self.category.trace('w', self.setFile)
        
        
        
        category_wid.pack()
        
        #Add it to save zone
        save_zone.add(save_wid)
        save_zone.add(category_wid)
        
        #Create a new Strength zone for att and pv
        strength_zone=PanedWindow(self.card_win, orient=HORIZONTAL)
        att=StringVar()
        att.set(str(self.att))
        pv=StringVar() ; pv.set(str(self.pv))
        def modifiedAttPv(*args) :
            print "modifiedAttPv"
            self.pv=int(pv.get())
            if self.pv<1 and self.is_spell==False :
                if len(self.bonus)==0 :
                    self.is_spell=True
                    self.refreshWidget()
                else :
                    self.pv=1
                    self.refreshWidget()
            if self.pv>0 and self.is_spell==True :
                if len(self.bonus)==0 :
                    self.is_spell=False
                    self.refreshWidget()
                else :
                    self.pv=0
                    self.refreshWidget()            
            self.att=int(att.get())
            self.getCost()
        att_wid = Spinbox(strength_zone, from_=0, to=1000,textvariable=att,command=modifiedAttPv)
        att_wid.pack()
        strength_zone.add(att_wid)
        strength_zone.add(Label(strength_zone, text='       ', background='white', 
             anchor=CENTER))
        pv_wid = Spinbox(strength_zone, from_=0, to=1000,textvariable=pv,command=modifiedAttPv)
        pv_wid.pack()
        strength_zone.add(pv_wid)
        
        #Put it all in window
        self.card_win.add(name_zone)
        self.card_win.add(image_zone)
        self.card_win.add(power_zone)  
        self.card_win.add(strength_zone)
        self.card_win.add(save_zone)
        
        
        self.card_win.pack()                      

    def createImage(self,black=False):
        width=189*2; height=277*2
        screen = pygame.display.set_mode((width,height))

        print "Type = ",self.monster_type
        if self.monster_type in all_backgrounds.keys():
            try:
                bg = pygame.image.load(all_backgrounds[self.monster_type])
            except:
                print "error (? when load of bg"
        else:
            bg = pygame.image.load('gameAnimationImages/Card_face_avant.gif')
        #fond = PhotoImage(file =bg,master=fenetre)
        #ligne1 = canvas.create_line(75, 0, 75, 120)
        #ligne2 = canvas.create_line(0, 60, 150, 60)      
        if self.photofile and not black:
            try :
               img=pygame.image.load(self.photofile)
            except :
               decomp=self.photofile.split('/')
               for i in range(1,6) :
                   try :
                       fname="/".join(decomp[-i:])
                       print "try to open",fname
                       img=pygame.image.load(fname)
                       self.photofile=fname
                       break
                   except:
                       pass
            img = pygame.image.load(self.photofile)
            w, h = img.get_size()
            factor=max(140.*2./w,90.*2./h)
            img=pygame.transform.scale(img,(int(w*factor),int(h*factor)))
            #fenetre.photo=PhotoImage(file=self.photofile,master=canvas)
            #img=ImageTk.PhotoImage(img,master=fenetre)
            screen.blit(img,(width/2.-w*factor/2.,140.-h*factor/4.))
        else :
            try :
                name=self.name.replace(" ","_")
                img=pygame.image.load("Cards/"+name+".png")
                print "* Found for image ","Cards/"+name+".png"
                screen.blit(img,(0,0))
            except :
                pass
        screen.blit(bg,(0,0))    
        
        pygame.font.init()
        #print  pygame.font.get_fonts()
        if self.monster_type in white_font_types:
            color = (255,255,255)
        else:
            color = (0,0,0)
        centerText(screen,(width/2.+10.,33.*2.),self.name,36-(len(self.name)>11)*(len(self.name)-11)/3,color)
        #txt = canvas.create_text(101, 32, text=self.name, font=("Calibri",12-(len(self.name)>11)*(len(self.name)-11)/5,"bold"), anchor=CENTER)
        if not(self.is_spell):
            centerText(screen,(24*2.,258*2.),str(self.att),40,color)
            centerText(screen,(169*2.,255*2.),str(self.pv),40,color)
        else :
            centerText(screen,(width/2.,265*2.),"SPELL",30,color)
        #elif self.is_spell:
        #    txt = canvas.create_text(100,265, text="SPELL", anchor=CENTER, font=("Calibri",14,'bold'))
        #txt = canvas.create_text(22,35, text=int(floor(self.getCost())), anchor=CENTER, font=("Calibri",18,'bold'))
        centerText(screen,(22*2.,35*2.),str(int(floor(self.getCost()))),50,color)
        #txt1 = canvas.create_text(92,257, text='*'*self.getStars(), anchor=CENTER, font=("Calibri",26,'bold'))
        centerText(screen,(92*2.,257*2.),'*'*self.getStars(),60,color)
        if not(self.monster_type == "unknown"):
            if self.monster_type in all_type_colors:
                Color = all_type_colors[self.monster_type]
            else:
                Color = "human"
        else:
            Color = "human"
        centerText(screen,(95*2.,142*2.),self.monster_type.capitalize(),26,Color)
        
        if len(self.bonus)>0 :
            powers = "e%96".join([b.getDescription() for b in self.bonus])
            powers = [p.split("\n") for p in powers.split("e%96")]
            print "powers are ",powers
        else :
            powers =""
        #print "POWERS = ", powers
        if powers: 
            space=min([80., 160./sum([len(p)*3+2 for p in powers])])
            print "Space: ",space
        line = 0
        for i,b in enumerate(powers):
            size = min([36.,500./max([len(p) for p in b]) * 2.])
            for x,part in enumerate(b):
                centerText(screen,(90*2.,167*2.+line*space),part,int(size),color)
                line += 3
            line += 2
        #canvas.pack()
        #print "toto!"
        pygame.display.flip()
        return screen
      
    def init_as_invocation(self,master,spells=False):
        # monster widget in invocation widget        
        #print "monster init_as_invocation"
        self.content=StringVar()
        self.content.set(self.name)
        self.content.trace("w", self.is_changed_as_invocation)
        l = [ m for m in Card.monster_list.keys() if (spells or all_monsters[m].pv>0) and not(m in Card.blocked_creature)]
        """
        if self.parent.name in l:
            l.remove(self.parent.name)
        """
        self.widget=OptionMenu(master,self.content,*l)
        return self.widget
        
    def is_changed_as_invocation(self,*args):
        print "monster is_changed_as_invocation"
        if self.content.get()!= "Troll gris":
            new= Card.monster_list[self.content.get()]
        else:
            new = Card("Troll gris",4,4)

        #print self.content.get()
        if self.parent :
            #parent.spell=new
            #print "self.parent = True"
            self.parent.monster=new
            new.parent = self.parent
            new.card=self.card
        else :
            raise "ce cas existe ?! me dire comment"
            self.bonus[self.bonus.index(self)]=new
        #self.card_win.pack_forget()
        self.card.refreshWidget()

all_monsters=None
troll=Card("Troll gris",4,4)
mouton = Card("Mouton",1,1)
#print os.getcwd()

#print glob.glob("CardFiles/*.sav")
#if __name__ == "__main__" :
#import pickle
if True:
    try :
        all_monsters=readMonsters(os.path.join("CardFiles","all_monsters.sav"))
    except :
        print "it exists",glob.glob("*/*monster*.sav")
        print "pas de fichier CardFiles/all_monsters.sav"
        try:
            #from cardPowers import *
            shutil.copyfile("CardFiles/recup_monsters.sav","CardFiles/all_monsters.sav")
            all_monsters=readMonsters("CardFiles/all_monsters.sav")
            print "recup all monsters"
        except:
            print " pas de recuperation"           
            all_monsters = {"Troll gris":troll}


Card.monster_list=all_monsters
if len(all_monsters)<1:
    all_monsters["Troll Gris"] = troll


all_backgrounds = {"shadow":"gameAnimationImages/Card_face_avant_black.gif","aqua":"gameAnimationImages/Card_face_avant_blue.gif"}
all_type_colors = {"aqua":(0,0,255),"demon":(255,0,0),"nature":(0,255,0),"hord":(100,100,50),"human":(120,155,120),"undead":(100,100,100),"shadow":(255,255,255)}
white_font_types = ['shadow']

    #for m in glob.glob("all*.sav"):
    #    f = pickle.load(localopen(m,"r"))
    #    all_monsters.update(f)
#import pickle
#import os
#os.chdir("C:\\Users\\Enfants\\Documents\\MCB_nov2016")
#a=pickle.load(open("CardFiles\\greek_monsters.sav","rb"))
#open("CardFiles\\greek_monsters.sav","w").write("\n".join([m.constructor() for m in a.values()]))