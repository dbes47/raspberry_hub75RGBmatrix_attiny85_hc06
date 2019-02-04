from bs4 import BeautifulSoup
import time
import serial
import threading

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