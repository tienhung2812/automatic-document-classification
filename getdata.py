import urllib.request
import time
import pandas as pd
from google.colab import files
from bs4 import BeautifulSoup
from google.colab import auth
auth.authenticate_user()
from googleapiclient.discovery import build
drive_service = build('drive', 'v3')
from IPython.display import HTML, display
def progress(value, max):
    return HTML("""
        <progress
            value='{value}'
            max='{max}',
            style='width: 100%'
        >
            {value}
        </progress>
    """.format(value=value, max=max))
    # print(str(text.find("http"))+" " + str(text.find("</link>")))
class BBCCrawler:
    def getLinkList(self,url):
        print("Fetching "+url+" ...")
        result = []
        try:
          page_source = urllib.request.urlopen(url)
          html = page_source.read().decode("utf8")
          bsObj = BeautifulSoup(html,"html.parser")
          for item in bsObj.find_all("item"):
              text = item.text.splitlines()
              result.append(text[3])
          return result
        except:
          print("getLinkList Error")
      
    def getContent(self,url,cate):
#         print("Fetching "+url+" ...")
        try:
          page_source = urllib.request.urlopen(url)
          html = page_source.read().decode("utf8")
          bsObj = BeautifulSoup(html,"html.parser")
          title = bsObj.find('h1', attrs={'class':'story-body__h1'}).text
          content = bsObj.find('div', attrs={'class':'story-body__inner'})
          #Process Text
          text = content.text
          text = text.replace("(function() {","")
          text = text.replace("if (window.bbcdotcom && bbcdotcom.adverts && bbcdotcom.adverts.slotAsync) {","")
          text = text.replace("bbcdotcom.adverts.slotAsync(\'mpu\', [1,2,3]);","")
          text = text.replace("}","")
          text = text.replace("})();","")
          text = text.replace("/**/","")
          text = text.replace(")();","")
          text = text.replace("  ","")
          text = text.replace("\n\n","")
          text = text.replace("Image copyright","")
          result = title+"\n\n"+text
          #Save text
          #Category
          if(cate is 'business'):
              self.category.append('business')
          if(cate is 'entertainment'):
              self.category.append('entertainment')
          if(cate is 'politics'):
              self.category.append('politics')
          if(cate is 'sport'):
              self.category.append('sport')
          if(cate is 'tech'):
              self.category.append('tech')
          #Filename
          filename = url[url.rfind("/")+1:]
          self.filename.append(filename)
          #Title
          self.title.append(title)
          #content
          self.content.append(text)
          self.sucess+=1
          return(result)
        except:
            print("getContent Error: "+url)
    def crawling(self,data,cate):
        self.sucess = 0
        maxval = len(data)
        out = display(progress(0, maxval), display_id=True)
        i=0
        for link in data:
          self.getContent(link,cate)
          i+=1
          out.update(progress(i, maxval))
        print("Crawled: "+str(self.sucess)+"/"+str(maxval))
    def __init__(self):
        
        start_time = time.time()
        en = "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
        te = "http://feeds.bbci.co.uk/news/technology/rss.xml"
        bu = "http://feeds.bbci.co.uk/news/business/rss.xml"
        po = "http://feeds.bbci.co.uk/news/politics/rss.xml"
        sp = "http://feeds.bbci.co.uk/sport/rss.xml"

        enlist = self.getLinkList(en)
        telist = self.getLinkList(te)
        bulist = self.getLinkList(bu)
        polist = self.getLinkList(po)
        splist = self.getLinkList(sp)
        self.category = []
        self.filename =[]
        self.title = []
        self.content = []
        print("En\tTe\tBu\tPo\tSp")
        print(str(len(enlist))+"\t"+str(len(telist))+"\t"+str(len(bulist))+"\t"+str(len(polist))+"\t"+str(len(splist))+"\t")

        #Crawling Entertainment
        print("Crawling Entertainment")
        self.crawling(enlist,"entertainment")
        
        #Crawling Tech
        print("Crawling tech")
        self.crawling(telist,"tech")
        
        #Crawling Buss
        print("Crawling business")
        self.crawling(bulist,"business")
        
        #Crawling poli
        print("Crawling politics")
        self.crawling(polist,"politics")
        
        #Crawling Sport
        print("Crawling sport")
        self.crawling(splist,"sport")
        

        print("Crawling in %s seconds" % (time.time() - start_time))
        print("Cate\tFile\tTitle\tContent")
        print(str(len(self.category))+"\t"+str(len(self.filename))+"\t"+str(len(self.title))+"\t"+str(len(self.content)))

        #Importing data
        print("Importing data...")
        dataSet = list(zip(self.category,self.filename,self.title,self.content))
        df = pd.DataFrame(data = dataSet, columns=['category', 'filename','title','content'])
        print("Exporting data...")
        df.to_csv('data.csv',index=False,header=True)
        from googleapiclient.http import MediaFileUpload

        file_metadata = {
          'name': 'data.csv',
          'mimeType': 'text/plain'
        }
        media = MediaFileUpload('data.csv', 
                                mimetype='text/plain',
                                resumable=True)
        created = drive_service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields='id').execute()
        print('File ID: {}'.format(created.get('id')))
        print("Done")
        

bbc = BBCCrawler()