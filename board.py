#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import threading
import os
import readbook #open nwetestimony file and parsing through BS4.
import Bluetooth_DHT #getting bluetooth data(hum and temp) from attiny85 and dht22 via hc-06 module.


mybook=readbook.TxtFileCrawl()
mybook.read_txt_line('./newtestimony.txt',10,3)

class MsgControlTower:
    def __init__(self,interval=5):
        self.interval=interval
        self.localtime=TimeStr()
        self.telebot=Bot()
        self.phase=1
        self.msg=''
        phaseChanging=threading.Thread(target=self.thread_change_phase)
        phaseChanging.start()
    def get_msg(self):
        return {0:self.telebot.returnTeleMsgTop(),
                1:self.localtime.get_full_time(),
                2:self.telebot.bridge_to_get_humtemp(),
                3:mybook.get_msg_pre()}[self.phase]
        #self.telebot.returnTeleMsgTop()
        #self.localtime.get_full_time()
        #self.telepot.bridge_to_get_humtemp()
    def dimming(self):
        time=int(self.localtime.get_time())
        if(time>18 or time<7):
            return(3)
        else:
            return(8)
    def thread_change_phase(self):
        while 1:
            time.sleep(self.interval)
            self.phase+=1
            if(self.phase>3):
                self.phase=1
            self.dimming()
            #print(self.phase)



class Bot:
    def __init__(self):
        self.incommingText=[]
        self.bot = telepot.Bot(token='668860249:AAGJHbFjhqS_3wttBLjIMeEJ-ujp3iuU8To')
        MessageLoop(self.bot,{'chat':self.text_handle,'callback_query':self.query_handle}).run_as_thread()
        self.STATUS=0

        self.hum_temp=Bluetooth_DHT.Bluetooth_DHTxx()
        self.hum_temp.make_connection()



    def text_handle(self,msg):
        content_type,chat_type,chat_id=telepot.glance(msg)
        if(msg['text']=='메뉴' and self.STATUS==0):
            touchBtn = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='온습도', callback_data='온습도'),
                                                              InlineKeyboardButton(text='성경구절', callback_data='성경')],
                                                             [InlineKeyboardButton(text='리부팅',callback_data='리부팅'),
                                                              InlineKeyboardButton(text='셧다운', callback_data='셧다운')]])
            self.bot.sendMessage(chat_id,'원하는 메뉴를 선택하세요',reply_markup=touchBtn)
        elif(self.STATUS==1):
            self.mtsCall.set_code(msg['text'])
            print('주가종목변경됨->'+msg['text'])
            self.bot.sendMessage(chat_id, text='주가 정보가 '+msg['text']+'로 변경되었습니다^^')
            self.STATUS=0
        elif(self.STATUS==2):
            mybook.set_start_point(int(msg['text']))
            self.bot.sendMessage(chat_id,text='성경구절이 '+mybook.get_msg_pre()+'으로 변경되었습니다.\n'+mybook.get_msg())
            self.STATUS=0
        else:
            self.incommingText.append(msg['text'])
            if(content_type=='text' and len(self.incommingText)>3):
                self.incommingText.pop(0)
            self.bot.sendMessage(chat_id, '전광판에 반영된 내용은 \n'+str(self.incommingText))

    def query_handle(self,msg):
        self.STATUS=0
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if(msg['data']=='셧다운'):
            self.bot.answerCallbackQuery(query_id, text=msg['data'] + '잠시 후 전원이 꺼집니다.')
            os.system('shutdown')
            self.bot.sendMessage(from_id,text='약 1분 후에 전원이 완전히 종료됩니다.')
            #self.STATUS=1
        elif(msg['data']=='온습도'):
            if(float(self.hum_temp.get_hum())<40):
                temp='\n건조하네요! 가습이 필요합니다.'
            else:
                temp='\n습도가 적당합니다.'
            self.bot.sendMessage(from_id, text='현재 집안의 온습도는 '+self.bridge_to_get_humtemp()+'입니다^^'+temp)
            self.STATUS=0
        elif(msg['data']=='리부팅'):
            self.bot.sendMessage(from_id,text='재부팅을 시작합니다. 잠시 후에 다시 사용해주세요.')
            os.system('systemctl reboot -i')
        elif(msg['data']=='성경'):
            self.bot.sendMessage(from_id,text='현재 성경 구절은 '+ mybook.get_msg_pre()+'입니다.\n'+mybook.get_msg() +'입니다.\n 이동하고자 하는 라인수 를 입력해 주세요!')
            self.STATUS=2

    def bridge_to_get_humtemp(self):
        return self.hum_temp.get_data()

    def returnTeleMsgTop(self):
        if(self.incommingText):
            temp=''
        else:
            temp='No Message'
        for i in range(len(self.incommingText)):
            temp=temp+self.incommingText[i]+' / '
        return temp

    def returnTeleMsgBottom(self):
        if(self.mtsCall.returnRDD()):
            temp = '' + self.mtsCall.returnRDD()
        else:
            temp='주식정보 로딩중...'
        return temp

class TimeStr:
    def __init__(self):
        pass
    def get_time(self,arg=0):
        self.hms=[]
        self.hms.append('%02d'% time.localtime()[3])
        self.hms.append('%02d'% time.localtime()[4])
        self.hms.append('%02d'% time.localtime()[5])
        return(self.hms[arg])
    def get_full_time(self):
        self.get_time()
        return self.hms[0]+':'+self.hms[1]+':'+self.hms[2]


            
    
class RunText(SampleBase):
    def __init__(self, *args, **kwargs):

        super(RunText, self).__init__(*args, **kwargs)
        self.msgctrltower=MsgControlTower(20)

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
        textColorBtm =graphics.Color(10,30,0)
        posTop = 0
        posBtm = offscreen_canvas.width



        while True:
            offscreen_canvas.Clear()
            lengTop = graphics.DrawText(offscreen_canvas, fontUP, posTop, 12, textColorTop, self.msgctrltower.get_msg())
            lengBtm = graphics.DrawText(offscreen_canvas, fontDOWN, posBtm, 27, textColorBtm, mybook.get_msg())
            if(lengTop<offscreen_canvas.width):
                posTop=(offscreen_canvas.width-lengTop)/2
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
