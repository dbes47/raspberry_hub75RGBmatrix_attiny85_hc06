import bluetooth
import time
import threading
from bs4 import BeautifulSoup

class Bluetooth_DHTxx:
    def __init__(self):
        self.mac='98:D3:31:90:48:73'
        self.incomming='receving...'
        self.hum=''
        self.temp=''
        self.work1=threading.Thread(target=self.parcing_data)
        
    def make_connection(self):
        try:
            self.sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)            
            self.sock.connect((self.mac,1))
            print('bluetooth has been connected('+self.mac+')')
            self.work1.start()
        except:
            print('fail to make a connection. try again')
            self.make_connection()
            
    def parcing_data(self):
        print('parcing thread start')
        while 1:
            data=self.sock.recv(1024)
            temp=data.decode('utf-8')
            temp=BeautifulSoup(temp,"html.parser")
            _hum=temp.find('hum')
            _temp=temp.find('temp')
            if(_hum!=None and _temp!=None):
                self.hum=round(float(_hum.string))
                self.temp=round(float(_temp.string))
                self.incomming=str(self.temp)+ "'C "+str(self.hum)+"%"
            time.sleep(3)
    def get_data(self):
        return self.incomming
    def get_temp(self):
        return self.temp
    def get_hum(self):
        return self.hum

# Main function
#if __name__ == "__main__":
#    bluetooth_dht=Bluetooth_DHT()
#    if (not bluetooth_dht.make_connection()):
#        print('please run <make_connection> method')