from tkinter import *
#import pickle
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from tkinter.messagebox import showinfo

from functools import partial
import glob
#import Card
import re
from outils import file2name
from PIL import Image
from PIL.ImageTk import PhotoImage
#os.chdir('C:\Users\test\Documents\Programmation\MCB2')

from Card import readMonsters,all_monsters
#all_cards={}
#for f in glob.glob("CardFiles/*_monsters.sav"):
#    #print "load cards in ",f
#    try :
#        d = readMonsters(f)
#    except Exception,e :
#        print "#### ERROR with ",f
#        raise e
#    all_cards.update(d)

#all_deks={}
#for f in glob.glob("Decks/*.dek"):
#    #print "load cards in ",f
#    d = pickle.load( open(f, "r" ))
#    all_deks.update(d)

#print "all_cards = ",all_cards
#print "all_deks = ",all_deks
#all_cards = pickle.load( open( "all_monsters.sav", "rb" ))
#all_decks=pickle.load( open( "all_decks.sav", "rb" ))



def getBlockedCreatures(blocked_decks) :
    blocked_creature=[]
    for i in blocked_decks :
        df=os.path.join("Decks",i.replace(" ","_")+".dek")
        try :
            m=""
            with open(df,"r") as fil: 
                deck = eval(fil.read())
                for m in deck.keys() :
                    if "Avatar" not in m :
                        c=all_monsters[m].getCost()
                        if c-int(c)<0.5 and all_monsters[m].pv>0 :
                            print( "revoir ",m,all_monsters[m].monster_type)
                blocked_creature=blocked_creature+deck.keys()
        except Exception as e :
            print( "in",i,"pb with",m)
            try :
                all_monsters[m].getCost()
                print( "ERROR ",df," not found",m,all_monsters[m].monster_type)
            except Exception as e :
                print( e)
    return blocked_creature 

class DeckCreator():
    def __init__(self,fenetre,blocdeck):
        self.blocked_decks=blocdeck
        self.blocked_creature=getBlockedCreatures(self.blocked_decks)
        self.galeries = []
        from Card import readMonsters
        self.all_cards_open = readMonsters("CardFiles/human_monsters.sav")
        self.refreshCardSelector(fenetre)
        
        self.deck={}
        self.ima=[]
        self.fenetre1=Toplevel(master=fenetre)
        self.fenetre1.title("Clic to remove a card from deck")


        #self.listbox = Listbox(master, yscrollcommand=scrollbar.set)
        self.deck_widg=Canvas(master=self.fenetre1)
        
        self.name = StringVar()
        self.firstline=PanedWindow(master=self.fenetre1, orient=HORIZONTAL)
        self.name_wid=Entry(master=self.firstline, width=30,textvariable=self.name)
        
        self.name.set("default")   
        self.deck_stars=Label(master=self.firstline, text="0")
        self.firstline.add(self.deck_stars)
        self.firstline.add( self.name_wid)
        self.firstline.pack()
        self.loadDeck(os.path.join("Decks","default"))
       # def choose():
         #   canvas.create_image(b,0 , anchor=NW, image = p)
        #canvas = Canvas(fenetre, width=189, height=277)
    def refreshCardSelector(self,fenetre):
        self.fenetre = fenetre
        self.im=[]
        nb_Carte_p_ligne=0
        self.ligne=1
        self.frame = Frame(fenetre)        
        vscrollbar = Scrollbar(self.frame, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self.frame, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth(),height=180*4)
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width(),height=180*4)
        canvas.bind('<Configure>', _configure_canvas)
        
        self.frame.pack()
        galerie1=PanedWindow(self.interior, orient=HORIZONTAL)
        #self.stars=[]
        #print( self.all_cards_open)
        lisk=list(self.all_cards_open.keys())
        for a in lisk :
            if a in self.blocked_creature :
                continue
            #self.stars.append(a)
            #self.all_cards_open[a].getCost()
            #♦self.stars.append(self.all_cards_open[a].getStars())
            self.filename=a.replace(" ","_")+'.png'
            print( self.filename)
            try :
               image = Image.open("Cards/"+self.filename).resize((120,180), Image.ANTIALIAS)
               p  = PhotoImage(image,master=galerie1)
               self.im.append(p)
            except :
                print( "pb avec image ","Cards/"+self.filename)
                print( "in deck ",self.all_cards_open[a].monster_type)
                print("Card must be redefined")
                continue
            b=Button(galerie1,  command=partial(self.addCard,a))
            b.configure(image =p,width=120,height=180)
            galerie1.add(b)
            nb_Carte_p_ligne+=1
            if nb_Carte_p_ligne>9 or a==lisk[-1]:
                nb_Carte_p_ligne=0
                #b.pack()
                self.galeries.append(galerie1)
                galerie1.pack()
                galerie1=PanedWindow(self.interior, orient=HORIZONTAL)     
        
    def addCard(self,card_name) :
        print( "addCard",card_name)
        # print self.deck
        if card_name not in self.deck: 
            self.deck[card_name]=1
        else:
            self.deck[card_name]+=1
        self.showDeck()
    def removeCard(self,card_name) :
        print( "removeCard",card_name)
        self.deck[card_name]-=1
        if self.deck[card_name]<1:
            del self.deck[card_name]
        self.showDeck()
    def save(self):
        if self.stars > 15:
                showinfo("Careful...","Your deck have too much stars to be used in the Campaign (limit is 15)")
        name=self.name.get().strip().replace(" ","_")+".dek"
        import os
        #lv = max(eval(open("progression2","r").read()).values())
        if os.path.basename(self.name.get()) in self.blocked_decks :
            print( "deck protege pour la campagne")
            return
        if not name.startswith("Decks"):
                print( "deck put in Decks/")
                name=os.path.join("Decks",name)
        print( "save in",name)
        import os.path
        if self.loaded and self.loaded!=os.path.basename(name) and self.loaded!=name and self.loaded.replace('\\','/')!=name.replace('\\','/') and os.path.isfile(name) or (not(self.loaded) and os.path.isfile(name)):
                print( "loaded ",self.loaded,"  cannot overwrite",name," !")
                showinfo("Impossible","You cannot overwrite an existing deck")
                return
            #name=self.name_wid.get()
        open( name, "wb" ).write(repr(self.deck).encode('utf-8'))
        print( self.deck," saved")
        self.deck={} ; self.name.set("") ; self.loaded=None
        self.showDeck()        
#    def openDeck(self) :
#        from tkFileDialog import askopenfilename
#        #Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
#        filename = askopenfilename(defaultextension=".dek",filetypes=[('Deck file','*.dek')]) # show an "Open" dialog box and return the path to the selected file
#        self.name.set(filename[0:-3].replace("_"," "))
#        self.load()

    def openDeck(self,*args) :
        name = self.opening.get()
        if (file2name(name) in self.blocked_decks) or " (not available)" in name:
            lv = max(eval(open("progression2","r").read()).values())
            print( "La campagne est au niveau ",lv," /8")
            if lv >= 8:
                self.loadDeck(name)
            else:
                print( "Deck is not accessible")
        else:
            name=self.opening.get()
            self.loadDeck(name)
        #self.opening.set("open another deck")
    
    def changeFile(self,*args):
        
        name = self.files.get()
        self.all_cards_open = readMonsters(name)
        for galerie in self.galeries:
            galerie.pack_forget()
        self.galeries = []
        self.frame.pack_forget()
#        self.scrollbar.pack_forget()
#        self.cardGalery.pack_forget()
        self.refreshCardSelector(self.fenetre)
    
    def changeAvatar(self,*args):
        name = self.avatars.get()
        self.deck["AvatarImage"]=name
        print( "avatar image is now ",self.deck["AvatarImage"])
        self.showDeck()
        
    def loadDeck(self,name) :
        print( "load",name)
        self.name.set(name)
        name=name.replace(" ","_")+".dek"   
        self.loaded=name
        print( " load ",name)
        try :
            deck= eval(open(name).read())
            print( "deck is",deck)
        except :
            if "Decks" not in name :
                deck= eval(open(os.path.join("Decks",name)).read())
            else:
                deck={}
        self.deck=deck
        self.showDeck()
#        try:
#            self.showDeck()
#        except:
#            print "error with showDeck"
#            self.verifyDeck()
        

    def showDeck(self) :
        print( "showDeck")
        if hasattr(self,"deck_widg") :
            self.deck_widg.pack_forget()
        self.deck_widg=PanedWindow(master=self.fenetre1, orient=VERTICAL)
        self.galerie_deck=PanedWindow(master=self.deck_widg, orient=VERTICAL)
        galerie1=PanedWindow(master=self.galerie_deck, orient=HORIZONTAL)
        galerie1.pack()
        galerie2=PanedWindow(master=self.galerie_deck, orient=HORIZONTAL)
        self.nb_card=0
        self.firstline.pack_forget()
        self.firstline=PanedWindow(master=self.fenetre1, orient=HORIZONTAL)
        print( "deck name:",self.name.get())
        self.name_wid=Entry(master=self.firstline, width=30,textvariable=self.name)
        self.stars=0
        for creature in self.deck :
            if (creature not in all_monsters) and creature!="AvatarImage":
                if creature.capitalize() in all_monsters :
                    self.deck[creature.capitalize()]=self.deck[creature]
                    del self.deck[creature]
                else :
                    print( 'ERROR : card not found : "'+creature+'" in ',all_monsters.keys())
        nbcoutreduit=0
        nbgainmana=0
        pouvoirslimites=["CoutReduit[(]","GainMana","CoutDesSortsReduit","CoutDesMonstresReduit"]
        limitregexp=[ re.compile(p) for p in pouvoirslimites]
        nbpoulimites=[0]*len(pouvoirslimites)
        for s,n in self.deck.items():
            if s != "AvatarImage":
                try:
                    all_monsters[s].getCost()
                    starcostint=all_monsters[s].getStars()
                    self.stars+=starcostint*n
                    if starcostint>0 :
                        print( n,"*",all_monsters[s].name,"(",starcostint,")")
                except:
                    print( "error with ",s,n)
                    del self.deck[s]
                for i in range(len(nbpoulimites)) :
                    nbpoulimites[i]+=len(limitregexp[i].findall(all_monsters[s].constructor()))*n
        print( [(p,nbpoulimites[i])  for i,p in enumerate(pouvoirslimites)])

        self.deck_stars=Label(master=self.firstline, text=self.stars)
        self.firstline.add(self.deck_stars)
        self.firstline.add( self.name_wid)
        self.firstline.pack()
        nb_card_in_line=0
        actual_zone=galerie1
        #self.ligne=1
        for c,n in self.deck.items():
            if c != "AvatarImage":
                nb_card_in_line+=1
                if nb_card_in_line==10:
                    actual_zone=galerie2
                    galerie2.pack()
              #     self.ligne+=1
                #print "list deck",c
                self.filename=c.replace(" ","_")+'.png'
                pilImage = Image.open("Cards/"+self.filename).resize((120,180), Image.ANTIALIAS)
                p = PhotoImage(pilImage)
                self.ima.append(p)
                card_zone = PanedWindow(master=actual_zone, orient=VERTICAL)
                #nb_zone = PanedWindow(master=self.galerie_deck, orient=VERTICAL)
                card_zone.add(Button(master=card_zone,  command=partial(self.removeCard,c),image =p,width=120,height=180))
                card_zone.add(Button(width=17,master=card_zone,  command= partial(self.removeCard,c) ,text=str(n)))
                self.nb_card+=n
                actual_zone.add(card_zone)
            #self.galerie_deck.add(nb_zone)
        self.deck_widg.add(self.galerie_deck)
        #self.deck_widg.add(self.nb_monstres)
        self.deck_widg.add(Button(master=self.deck_widg,  command= None ,text=self.nb_card))
        self.opening = StringVar(self.deck_widg)
        self.opening.set("Open another deck")
        choice = [os.path.basename(fname)[0:-4].replace("_"," ") for fname in glob.glob("Decks/*.dek")]
        if choice :
            choice=[name+" (not available)"*(name in self.blocked_decks) for name in choice]
            open_wid = OptionMenu(self.deck_widg, self.opening,*choice)
            open_wid.pack()
            self.deck_widg.add(open_wid)
        self.opening.trace('w', self.openDeck)
        
        self.files = StringVar(self.deck_widg)
        self.files.set("Take Monsters from Files")        
        file_wid = OptionMenu(self.deck_widg, self.files,*glob.glob("CardFiles/*_monsters.sav"))
        file_wid.pack()
        self.files.trace('w', self.changeFile)
        self.deck_widg.add(file_wid)
        
        self.avatars = StringVar(self.deck_widg)
        try:
            print( "avatar=",self.deck["AvatarImage"])
            self.avatars.set(self.deck["AvatarImage"])      
        except:
            self.avatars.set("Avatars/Chevalier_noir#.png ")
            self.deck["AvatarImage"] = "Avatars/Chevalier_noir#.png "
            print( "no atribute avatarimage")
        avatar_wid = OptionMenu(self.deck_widg, self.avatars,*glob.glob("Avatars/*#.png"))
        avatar_wid.pack()
        self.avatars.trace('w', self.changeAvatar)
        self.deck_widg.add(avatar_wid)
        
        
        if (self.nb_card>29 and all([n<7 for n in nbpoulimites])) or __name__=='__main__':
            if self.stars <= 15:
                self.deck_widg.add(Button(master=self.deck_widg,  command= self.save ,text='save deck'))
            else:
                self.deck_widg.add(Button(master=self.deck_widg,  command= self.save ,text='save deck (but beware there is too much stars)'))
        else :
            if self.nb_card<30:                
                self.deck_widg.add(Button(master=self.deck_widg,  command= None ,text='30 cards and 15 stars needed to save deck')) 
            else :
                self.deck_widg.add(Button(master=self.deck_widg,  command= None ,text='trop de '+' '.join([po for i,po in enumerate(pouvoirslimites) if nbpoulimites[i]>6])+". Pas de ca ici!"))
#            elif nbpoulimites[i]>6:                
#                self.deck_widg.add(Button(master=self.deck_widg,  command= None ,text=str(nbcoutreduit)+' couts reduits? Pas de ca ici.')) 
#            elif nbpoulimites[i]>6:                
#                self.deck_widg.add(Button(master=self.deck_widg,  command= None ,text=str(nbgainmana)+' gains mana, c\'est trop')) 
                
        print( "fin show")
        self.deck_widg.pack()
        self.firstline.pack()

           
     
#def checkSave(creaturename):
#        import os
#        decks = glob.glob(os.path.join("Decks","*.dek"))
#        content = []
#        for d in decks:
#            print "deck",d
#            with localopen(d,"r") as fil: # problem with python : I wanted to use "rb"
#                deck = pickle.load(fil)
#                if creature in deck.keys():
#                    content.append(d)
#        return content

if __name__=='__main__':
    fenetre = Tk()
    fenetre.title('Clic to add a monster to deck _ close this windows to end deck creation')
    a=DeckCreator(fenetre,[])
    fenetre.mainloop()
    

        
        
        
        
        
        
        
        
        
        
