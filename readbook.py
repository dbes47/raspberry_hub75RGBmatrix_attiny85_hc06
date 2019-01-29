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
        _to=_from+_amount
        self.to=_to
        self.daily_contents=[]
        while self.flag==True:
            for i in range(_to):
                temp=file.readline()
                if((_from-1)<=i and i<(_to-1)):
                    self.daily_contents.append(temp.replace("\n","")[7:])
                elif(i==(_to-1)):
                    self.flag=False            
        #print(self.daily_contents)
        
    def get_msg(self):
        temp=''
        if(self.daily_contents):
            for msg in self.daily_contents:
                temp+=msg+" "
        else:
            temp='loading text file'
        #print(temp)
        return temp
    
    def go_next(self):
        print('every line has been displayed. now go next part!!')
        self.read_txt_line(self.filename,self.to,self.amount)