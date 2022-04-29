import string
import random
import os
from PIL import Image

#approot = os.path.abspath(os.curdir)
filedir = os.path.dirname(os.path.abspath(__file__))


inputFolder = os.path.join(filedir, 'img_cache/inputfolder/')
outputFolder = os.path.join(filedir, 'img_cache/outputfolder/')

def helloworld():
    print('helloworld')

def newFolder():
    letters = string.ascii_letters
    ran_char = ''.join(random.choice(letters) for i in range(10))
    if not os.path.exists(ran_char):
        inputfolder = "".join([inputFolder, ran_char])
        outputfolder = "".join([outputFolder, ran_char])
        os.makedirs(inputfolder)
        os.makedirs(outputfolder)
        #os.makedirs(inputfolder+'/'+"100x")
        #os.makedirs(inputfolder+'/'+"400x")
        #os.makedirs(outputfolder+'/'+"100x")
        #os.makedirs(outputfolder+'/'+"400x")
        return ran_char

def resize(folder):
    imgNameList400x = [f for f in os.listdir(inputFolder + folder ) if os.path.isfile(os.path.join(inputFolder +  folder , f))]
    #NO LONGER SUPPORT 100X
    #imgNameList100x = [f for f in os.listdir(inputFolder + folder + '/100x') if os.path.isfile(os.path.join(inputFolder + "/" + folder + '/100x', f))]
    basewidth = 960
    if imgNameList400x != []:
        for file in imgNameList400x:
            path = inputFolder + folder + "/"  + file
            with Image.open(path) as img:
                wpercent = (basewidth/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
                img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                img.save(path) 
                img.close()
            
def getAllfiles(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
