import glob
from pandas import DataFrame, read_csv

# General syntax to import a library but no functions: 
##import (library) as (give the library a nickname/alias)
#import matplotlib.pyplot as plt
import pandas as pd #this is how I usually import pandas
import sys #only needed to determine Python version number
#import matplotlib #only needed to determine Matplotlib version number

print("Getting files list...")
#Get file in business
bu = (glob.glob("data/bbc/business/*.txt"))

#Get file in entertainment
en = (glob.glob("data/bbc/entertainment/*.txt"))

#Get file in politics
po = (glob.glob("data/bbc/politics/*.txt"))

#Get file in sport
sp = (glob.glob("data/bbc/sport/*.txt"))

#Get file in tech
te = (glob.glob("data/bbc/tech/*.txt"))
category = []
filename =[]
title = []
content = []

def CreateData(cate):
    #Filter
    
    print("Creating "+cate+" data...")
    if(cate is 'business'):
        field = bu
    if(cate is 'entertainment'):
        field = en
    if(cate is 'politics'):
        field = po
    if(cate is 'sport'):
        field = sp
    if(cate is 'tech'):
        field = te
    for textfile in field:
        try :
            with open(textfile) as f:
                rawcontentarray = f.read().splitlines()
                rawcontent = ""
                title.append(rawcontentarray[0])
                for i in range(2,len(rawcontentarray)):
                    rawcontent+=rawcontentarray[i]
                content.append(rawcontent[:10])
                category.append(cate)
                filename.append(textfile[textfile.rfind('/')+1:])
        except Exception as error:
            print(cate)
            print(textfile)
            print(error)
    print("Cate\tFile\tTitle\tContent")
    print(str(len(category))+"\t"+str(len(filename))+"\t"+str(len(title))+"\t"+str(len(content)))

#main function
#Creating Data
CreateData("business")
CreateData("entertainment")
CreateData("politics")
CreateData("sport")
CreateData("tech")
#check Data
if(len(category)==len(filename)==len(title)==len(content)):
    print("Create data successfully")
else:
    print("Number of data is not equal\n"+str(len(category))+"\t"+str(len(filename))+"\t"+str(len(title))+"\t"+str(len(content)))

#Importing data
print("Importing data...")
dataSet = list(zip(category,filename,title,content))
df = pd.DataFrame(data = dataSet, columns=['category', 'filename','title','content'])
print("Exporting data...")
df.to_csv('data.csv',index=False,header=True)
print("Done")