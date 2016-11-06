import os


def localpath (name):
    if os.path.sep == '/':
        return name.replace('\\','/')
    return name.replace('/','\\')


def file2name (fname,extension=''):
    return localpath(os.path.basename(fname)[:-len(extension)].replace("_"," "))


def name2file (folder,name,extension=''):
    return localpath(os.path.join(folder,name+extension).replace(" ","_"))


def localopen (name,*args):
    import glob
    print localpath(name)
    print glob.glob(name)
    print glob.glob(localpath(name))
    return open(localpath(name),*args)
