import urllib.request
import time
import pandas as pd
import glob
from bs4 import BeautifulSoup
from readability import Document
import sys
import os, shutil

targetData = 5000

def wipeFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

class BBCNewsCrawler:
    def saveToTxt(self,content,cate):
        id = len(glob.glob("bbcnews/"+cate+"/*.txt"))
        print("Save "+str(id)+".txt in "+cate)
        file = open("bbcnews/"+str(cate)+"/"+str(id)+".txt", "w") 
        file.write(content) 
        file.close() 
    def getRssLinkList(self,url):
          print("Fetching "+url+" ...")
          
          try:
            page_source = urllib.request.urlopen(url)
            html = page_source.read().decode("utf8")
            bsObj = BeautifulSoup(html,"html.parser")
            for item in bsObj.find_all("item"):
                text = item.text.splitlines()
                self.waitingList.append(text[3])
            return result
          except:
            print("getLinkRssList Error "+ url)
    def getLinkList(self,url):
        print("Fetching "+url+" ...")
        #         ["https://www.bbc.co.uk/","http://www.bbc.com/","https://edition.cnn.com/","","https://www.wsj.com/","https://www.nytimes.com/"]
        
        try:
          
          page_source = urllib.request.urlopen(url)
          html = page_source.read()
          bsObj = BeautifulSoup(html,"html.parser")
          links = bsObj.find_all('a')
          added = 0
          for link in links:
            #Check crawled?
            shouldAdd = True
            
            if link['href'].find("https://")!=0 and link['href'].find("http://")!=0 :
              if url.find("https://edition.cnn.com/")==0:
                link['href'] = url + link['href'][1:]
              elif url.find("https://www.nytimes.com/")==0:
                link['href'] = url + link['href'][1:]
              else:
                shouldAdd = False
            if link['href'].find("https://www.bbc")!=0 and link['href'].find("http://www.bbc")!=0 :
              shouldAdd = False
            if link['href'] in self.crawledList:
              shouldAdd = False
            if link['href'] in self.waitingList:
              shouldAdd = False
            if shouldAdd:
              added +=1
              self.waitingList.append(link['href'])
          print("Added "+ str(added))
          return result
        except:
          return
      
    def getContent(self,url,cate):
#         print("Fetching "+url+" ...")
      try:
          page_source = urllib.request.urlopen(url)
          self.crawledList.append(url)
          html = page_source.read().decode("utf8")
          doc = Document(html)
          bsObj = BeautifulSoup(doc.summary(),"html.parser")
          
          title = str(doc.title())
          # content = 
          # bsObj.find('div', attrs={'class':'story-body__inner'})
          #Process Text

          text = str(bsObj.text)
          text = text.replace("Image copyright","")
          
          text = text.replace("  ","")
          text = text.replace("\n\n","")
          text = text.replace("- BBC News","")
          #Save text
          #Category
          if(cate is 'business'):
              self.category.append('business')
              self.bu+=1
          if(cate is 'entertainment'):
              self.category.append('entertainment')
              self.en+=1
          if(cate is 'politics'):
              self.category.append('politics')
              self.po+=1
          if(cate is 'sport'):
              self.category.append('sport')
              self.sp+=1
          if(cate is 'tech'):
              self.category.append('tech')
              self.te+=1
          #Filename
          filename = url[url.rfind("/")+1:]
          self.filename.append(filename)
          #Title
          self.title.append(title)
          #content
          self.content.append(text)
          self.getLinkList(url)
          self.saveToTxt(title+"\n\n"+text,cate)
          self.sucess+=1
          return 1
      except Exception as error:
          print(error)
    def findCate(self,link):
      cate = None
      if link.find('business')>-1:
        cate = 'business'
      if link.find('entertainment')>-1:
        cate = 'entertainment'
      if link.find('politics')>-1:
        cate = 'politics'
      if link.find('technology')>-1:
        cate = 'tech'
      if link.find('sport')>-1:
        cate = 'sport'
      return cate
    def ExportFile(self):
      print("Crawling in %s seconds" % (time.time() - self.start_time))
      print("Cate\tFile\tTitle\tContent")
      print(str(len(self.category))+"\t"+str(len(self.filename))+"\t"+str(len(self.title))+"\t"+str(len(self.content)))

      #Importing data
      print("Importing data...")
      dataSet = list(zip(self.category,self.filename,self.title,self.content))
      df = pd.DataFrame(data = dataSet, columns=['category', 'filename','title','content'])
      print("Exporting data...")
      df.to_csv('crawled.csv',index=False,header=True)
      sys.exit()
    def crawling(self,data):
               
        maxval = len(data)
        print("Data: "+ str(maxval))
        #Filtering Data

        cate = ''
#         for i in data[:]:
#           if i in self.crawledList:
#               data.remove(i)
        print("Removed "+ str(maxval-len(data))+" conflicts")
        i=0
        for link in data:
          i+=1
          cate = self.findCate(link);
          if cate is not None:
            self.getContent(link,cate)
            
            print("Crawling: \t"+str(i)+"/"+str(len(data))+"\tCate: "+cate+"\tSucess: "+str(self.sucess)+"\tUrl: "+str(link))
          if self.sucess%10 == 0 and self.sucess>1:
            print("Bu\tEn\tPo\tTe\tSp")
            print(str(self.bu)+"\t"+str(self.en)+"\t"+str(self.po)+"\t"+str(self.te)+"\t"+str(self.sp))
          if(self.sucess>=targetData):
            self.ExportDriveFile()
            
        print("Bu\tEn\tPo\tTe\tSp")
        print(str(self.bu)+"\t"+str(self.en)+"\t"+str(self.po)+"\t"+str(self.te)+"\t"+str(self.sp))
        print("Rate: "+str(self.sucess)+"/"+str(maxval))
    def classifyPublisher(self,data):
#         ["https://www.bbc.co.uk/","http://www.bbc.com/","https://edition.cnn.com/","https://www.theguardian.com","https://www.wsj.com/","https://www.nytimes.com/"]
        bbc = 0
        cnn = 0
        theguardian=0
        wsj = 0
        nytimes = 0
        for url in data:
          if url.find("https://edition.cnn.com/")>-1:
            cnn+=1
          elif url.find("https://www.theguardian.com")>-1:
            theguardian+=1
          elif url.find("https://www.wsj.com/")>-1:
            wsj+=1
          elif url.find("https://www.nytimes.com/")>-1:
            nytimes+=1
          elif url.find("https://www.bbc")>-1 or url.find("http://www.bbc")>-1:
            bbc+=1
          else:
            print("Other: "+str(url))
        print("BBC\tCNN\tTheGuardian\tWJS\tNYT")
        print(str(bbc)+"\t"+str(cnn)+"\t"+str(theguardian)+"\t\t"+str(wsj)+"\t"+str(nytimes))
    def __init__(self):
        
        self.start_time = time.time()
        self.sucess = 0
        self.bu = 0
        self.te = 0
        self.po = 0
        self.sp = 0
        self.en = 0
        self.category = []
        self.filename =[]
        self.title = []
        self.content = []
        #Wipe Folder
        wipeFolder("bbcnews/business")
        wipeFolder("bbcnews/entertainment")
        wipeFolder("bbcnews/politics")
        wipeFolder("bbcnews/sport")
        wipeFolder("bbcnews/tech")
        #Crawling
        self.waitingList = ["https://www.bbc.co.uk/","http://www.bbc.com/"]
        for list in self.waitingList:
          self.getLinkList(list)
        self.crawledList = []
        #Get RSS
        en = "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
        te = "http://feeds.bbci.co.uk/news/technology/rss.xml"
        bu = "http://feeds.bbci.co.uk/news/business/rss.xml"
        po = "http://feeds.bbci.co.uk/news/politics/rss.xml"
        sp = "http://feeds.bbci.co.uk/sport/rss.xml"
        self.getRssLinkList(en)
        self.getRssLinkList(te)
        self.getRssLinkList(bu)
        self.getRssLinkList(po)
        self.getRssLinkList(sp)
        
        while len(self.waitingList)>0:
          print("Start crawling "+str(len(self.waitingList))+" urls")
          self.classifyPublisher(self.waitingList)
#           self.getLinkList(self.waitingList.pop(0))
          print(self.waitingList)
          self.crawling(self.waitingList)
        self.ExportFile()
    def ExportDriveFile(self):
      print("Crawling in %s seconds" % (time.time() - self.start_time))
      print("Cate\tFile\tTitle\tContent")
      print(str(len(self.category))+"\t"+str(len(self.filename))+"\t"+str(len(self.title))+"\t"+str(len(self.content)))

      #Importing data
      print("Importing data...")
      dataSet = list(zip(self.category,self.filename,self.title,self.content))
      df = pd.DataFrame(data = dataSet, columns=['category', 'filename','title','content'])
      print("Exporting data...")
      df.to_csv('crawled.csv',index=False,header=True)
      sys.exit()
bbc = BBCNewsCrawler()