import bluetooth

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

    def get_hum(self):
        return self.hum

    def get_temp(self):
        return self.temp

    def get_data(self):
        return self.cooked_data
