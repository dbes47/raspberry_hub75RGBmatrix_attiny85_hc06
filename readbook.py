class TxtFileCrawl:
    def __init__(self):
        self.daily_contents=[]
        self.flag=True
        self.filename=''
        self.amount=''
        self.to=''

    def read_txt_line(self,filename,_from,_amount=1):
        self.flag=True
        file=open(filename,'r')
        self.filename=filename
        self.amount=_amount
        self.start_point=_from
        _to=_from+_amount
        self.to=_to
        self.daily_contents=[]
        self.daily_contents_pre=[]
        while self.flag==True:
            for i in range(_to):
                temp=file.readline()
                if((self.start_point-1)<=i and i<(_to-1)):
                    self.daily_contents.append(temp.replace("\n","")[7:])
                    self.daily_contents_pre.append(temp.replace("\n","")[:7])
                elif(i==(_to-1)):
                    self.flag=False            
        #print(self.daily_contents)
                    
    def set_start_point(self,arg):
        self.read_txt_line(self.filename,arg,self.amount)
        #print('start_point has been changed %s'%arg)
    
        
    def get_msg(self):
        temp=''
        if(self.daily_contents):
            for msg in self.daily_contents:
                temp+=msg+" "
        else:
            temp='loading text file'
        #print(temp)
        return temp
    def get_msg_pre(self):
        temp=''
        if(self.daily_contents):
            for msg in self.daily_contents_pre:
                temp+=msg
        else:
            temp='loading text file'
            
        if(temp[0:1]==temp[14:15]):
            if(temp[2:3]==temp[16:17]):
                return (temp[0:6]+'~'+temp[18:20])
        return temp[0:6]+"~"+temp[15:20]        
    
    def go_next(self):
        #print('every line has been displayed. now go next part!!')
        self.read_txt_line(self.filename,self.to,self.amount)