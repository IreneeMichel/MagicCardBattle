import os


def localpath (name):
    if os.path.sep == '/':
        return name.replace('\\','/')
    return name.replace('/','\\')


def file2name (fname,extension=''):
    return localpath(os.path.basename(fname)[:-len(extension)].replace("_"," "))


def name2file (folder,name,extension=''):
    out=localpath(os.path.join(folder,name+extension).replace(" ","_"))
    if not os.path.exists(out) :
        print (out+" does not exist")
    return out

def localopen (name,*args):
    import glob
    print ("outils",localpath(name))
    print ("outils",glob.glob(name))
    print ("outils",glob.glob(localpath(name)))
    return open(localpath(name),*args)
