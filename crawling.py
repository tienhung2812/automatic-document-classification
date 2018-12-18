import urllib.request
import time
import pandas as pd
from bs4 import BeautifulSoup
from readability import Document
import sys

targetData = 5000

class NewsCrawler:
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
            print("getLinkList Error")
    def getLinkList(self,url):
        print("Fetching "+url+" ...")
        result = []
        try:
          page_source = urllib.request.urlopen(url)
          html = page_source.read()
          bsObj = BeautifulSoup(html,"html.parser")
          links = bsObj.find_all('a')
          for link in links:
            result.append(link['href'])
            
            #Check crawled?
            shouldAdd = True
            if link['href'].find("https://www.bbc")<0 and link['href'].find("http://www.bbc")<0 :
              shouldAdd = False
            if link['href'].find("www.bbc")<0:
              shouldAdd = False
            if link['href'] in self.crawledList:
              shouldAdd = False
            if link['href'] in self.waitingList:
              shouldAdd = False
            # if self.findCate(link['href']) is None:
            #   shouldAdd = False
            if shouldAdd:
              self.waitingList.append(link['href'])
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
          
          title = str(doc.title)
          # content = 
          # bsObj.find('div', attrs={'class':'story-body__inner'})
          #Process Text

          text = str(bsObj.text)
          text = text.replace("Image copyright","")
          text = text.replace("  ","")
          text = text.replace("\n\n","")
          # text = text.replace("(function() {","")
          # text = text.replace("if (window.bbcdotcom && bbcdotcom.adverts && bbcdotcom.adverts.slotAsync) {","")
          # text = text.replace("bbcdotcom.adverts.slotAsync(\'mpu\', [1,2,3]);","")
          # text = text.replace("}","")
          # text = text.replace("})();","")
          # text = text.replace("/**/","")
          # text = text.replace(")();","")
          # text = text[:text.find('Search\n@-moz-keyframes gel-spin')]+text[text.rfind('initFullFatApplication(initConfig);\n);')+len('initFullFatApplication(initConfig);\n);'):]
          # print(title+"\n\n"+text)
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
        for i in data[:]:
          if i in self.crawledList:
              data.remove(i)
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
            self.ExportFile()
            
        print("Bu\tEn\tPo\tTe\tSp")
        print(str(self.bu)+"\t"+str(self.en)+"\t"+str(self.po)+"\t"+str(self.te)+"\t"+str(self.sp))
        print("Rate: "+str(self.sucess)+"/"+str(maxval))
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
        self.waitingList = ["https://www.bbc.co.uk/","http://www.bbc.com/","https://edition.cnn.com/"]
        self.crawledList = []
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
          self.getLinkList(self.waitingList.pop(0))
          print(self.waitingList)
          self.crawling(self.waitingList)
        self.ExportFile()

bbc = NewsCrawler()