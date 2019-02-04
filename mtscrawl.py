from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import threading


class MtsCrawl:
    def __init__(self,_code):
        self.code = _code
        self.URL = 'https://finance.naver.com/item/fchart.nhn?code='+self.code
        self.mtsResult = ''
        thread = threading.Thread(target=self.requestData)
        thread.start()

    def set_code(self,arg):
        self.code=arg
        self.URL='https://finance.naver.com/item/fchart.nhn?code='+self.code

    def requestData(self):
        while 1:
            html=urlopen(self.URL)
            result1=BeautifulSoup(html.read(),"html.parser")
            result2=result1.find("dl",{"class":"blind"})
            company=result2.dt.next_sibling.next_sibling.next_sibling.next_sibling.string
            price=result2.dt.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.string
            self.mtsResult= company+ " : "+price
            time.sleep(10)

    def returnRDD(self):
        return self.mtsResult


