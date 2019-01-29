#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


import threading
from bs4 import BeautifulSoup
from urllib.request import urlopen
import serial
import bluetooth
import readbook
import Bluetooth_DHT


mybook=readbook.TxtFileCrawl()
mybook.read_txt_line('./newtestimony.txt',10,3)

class RemoteSwitch:
    def __init__(self):
        self.send_data=''
        self.mac='00:21:13:01:37:2C'
        
    def make_connection(self):
        try:
            self.sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)            
            self.sock.connect((self.mac,1))
            print('bluetooth has been connected('+self.mac+')')
        except:
            print('No bluetooth device')
            
    def set_send_data(self,arg):
        self.send_data=arg
        self.sock.send(self.send_data)

    def get_status(self):
        return self.sock.getpeer()

    def kill_connection(self):
        self.sock.close()




class HumTempSerial:
    def __init__(self):
        #bluetooth class
        self.rs=RemoteSwitch()
        self.rs.make_connection()
        #call serial comm start
        self.cooked_data='Loading...'
        flag=True
        while flag:
            self.arduino = serial.Serial("/dev/ttyACM0", timeout=1)
            if(self.arduino):
                flag=False

        thread_1=threading.Thread(target=self.read_serial_data)
        thread_1.start()


    def read_serial_data(self):
        while 1:
            temp=self.arduino.readline()
            obj = BeautifulSoup(temp, "html.parser")
            temp=obj.find("temp")
            hum=obj.find("hum")
            if(temp!=None and hum!=None):
                self.temp=round(float(temp.string))
                self.hum=round(float(hum.string))
                self.cooked_data=str(self.temp)+"'C "+str(self.hum)+"%"
            #sending bluetooth signal according to hum&temp info
                _hum=float(self.hum)
                if(_hum<40):
                    try:
                        self.rs.set_send_data('1')
                        self.rs.set_send_data('3')
                    except:
                        print('retry to make connection')
                        self.rs.make_connection()
                elif(_hum>=40):
                    try:
                        self.rs.set_send_data('0')
                        self.rs.set_send_data('4')
                    except:
                        print('retry to make connection')
                        self.rs.make_connection()
            time.sleep(3)

    def get_hum(self):
        return self.hum

    def get_temp(self):
        return self.temp

    def get_data(self):
        return self.cooked_data


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



class Bot:
    def __init__(self):
        self.incommingText=[]
        self.bot = telepot.Bot(token='668860249:AAGJHbFjhqS_3wttBLjIMeEJ-ujp3iuU8To')
        MessageLoop(self.bot,{'chat':self.text_handle,'callback_query':self.query_handle}).run_as_thread()
        self.STATUS=0

        self.hum_temp=Bluetooth_DHT.Bluetooth_DHTxx()
        self.hum_temp.make_connection()
        self.mtsCall=MtsCrawl('005930')


    def text_handle(self,msg):
        content_type,chat_type,chat_id=telepot.glance(msg)
        if(msg['text']=='메뉴' and self.STATUS==0):
            touchBtn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='온습도', callback_data='온습도'),
                                                              InlineKeyboardButton(text='주가', callback_data='주가')]])
            self.bot.sendMessage(chat_id,'원하는 메뉴를 선택하세요',reply_markup=touchBtn)
        elif(self.STATUS==1):
            self.mtsCall.set_code(msg['text'])
            print('주가종목변경됨->'+msg['text'])
            self.bot.sendMessage(chat_id, text='주가 정보가 '+msg['text']+'로 변경되었습니다^^')
            self.STATUS=0
        else:
            self.incommingText.append(msg['text'])
            if(content_type=='text' and len(self.incommingText)>3):
                self.incommingText.pop(0)
            self.bot.sendMessage(chat_id, '전광판에 반영된 내용은 \n'+str(self.incommingText))

    def query_handle(self,msg):
        self.STATUS=0
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if(msg['data']=='주가'):
            self.bot.answerCallbackQuery(query_id, text=msg['data'] + '을 선택하셨습니다. 주식 종목번호를 알려주세요!')
            self.bot.sendMessage(from_id,text='주식 종목 고유번호를 입력하세요.')
            self.STATUS=1
        elif(msg['data']=='온습도'):
            if(float(self.hum_temp.get_hum())<40):
                temp='\n건조하네요! 가습이 필요합니다.'
            else:
                temp='\n습도가 적당합니다.'
            self.bot.sendMessage(from_id, text='현재 집안의 온습도'+self.bridge_to_get_humtemp()+'입니다^^'+temp)
            self.STATUS=0

    def bridge_to_get_humtemp(self):
        return self.hum_temp.get_data()

    def returnTeleMsgTop(self):
        if(self.incommingText):
            temp=''
        else:
            temp=''
        for i in range(len(self.incommingText)):
            temp=temp+self.incommingText[i]+' / '
        return temp

    def returnTeleMsgBottom(self):
        if(self.mtsCall.returnRDD()):
            temp = '' + self.mtsCall.returnRDD()
        else:
            temp='주식정보 로딩중...'
        return temp


class RunText(SampleBase):
    def __init__(self, *args, **kwargs):

        super(RunText, self).__init__(*args, **kwargs)

    def run(self):
        runThread=threading.Thread(target=self.runThreadFunc)
        runThread.start()


    def runThreadFunc(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        fontUP = graphics.Font()
        fontDOWN = graphics.Font()
        fontUP.LoadFont("../rpi-rgb-led-matrix/fonts/korean2.bdf")
        fontDOWN.LoadFont("../rpi-rgb-led-matrix/fonts/korean2.bdf")
        textColorTop = graphics.Color(20, 10, 0)
        textColorBtm =graphics.Color(0,10,0)
        posTop = 0
        posBtm = offscreen_canvas.width

        self.telebot=Bot()

        while True:
            offscreen_canvas.Clear()
            lengTop = graphics.DrawText(offscreen_canvas, fontUP, posTop, 12, textColorTop, self.telebot.bridge_to_get_humtemp()+" "+self.telebot.returnTeleMsgTop())
            lengBtm = graphics.DrawText(offscreen_canvas, fontDOWN, posBtm, 27, textColorBtm, mybook.get_msg())

            if(lengTop>=offscreen_canvas.width):
                posTop -= 1
            if (posTop + lengTop < 0):
                posTop = offscreen_canvas.width

            posBtm -= 1
            if (posBtm + lengBtm<0):
                posBtm = offscreen_canvas.width
                mybook.go_next()

            time.sleep(0.03)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)





# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
