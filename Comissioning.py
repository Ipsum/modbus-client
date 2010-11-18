#TODO
#-Check Responses to writes
#-implement exceptions
#-implement logging
#-implement config file
#-implement cli
#-implement debug interface
#-add help menu
'''
Default mode: 
When jumper on the device is set to default mode, the device has:
 * An ID of 1
 * Baud Rate of 9600
 * no parity
 * 2 stop bits
 '''
 
import os
from Tkinter import *
from ttk import *
import ConfigParser

import modbus
import util

s=dict(id=1, port=0, baud=9600, parity='N', stopbits=2)
port=0
class toplevels:

    def comset(self, master):
        
        #setup a tabbed interface
        n = Notebook(master)
        w1 = Frame(n)
        w2 = Frame(n)
        n.add(w1, text='Comm Settings')
        n.add(w2, text='Unit Settings')
        
        Label(w1, text="Device ID").grid(row=0, column=0)
        self.check = IntVar()
        self.did = Spinbox(w1, from_=1, to=248, increment=1, width=5, validate="focus",textvariable=self.check, validatecommand=self.validate, wrap=True, justify=CENTER)
        self.did.grid(row=0, column=1)

        Label(w1, text="Baud Rate").grid(row=1, column=0)
        self.br = IntVar()
        self.br.set(0)
        Radiobutton(w1, text="9600", variable=self.br, value=0).grid(row=1, column=1,sticky=W)
        Radiobutton(w1, text="19200", variable=self.br, value=1).grid(row=2, column=1,sticky=W)

        Label(w1, text="Stop Bits").grid(row=3, column=0)
        self.sb = IntVar()
        self.sb.set(2)
        Radiobutton(w1, text="1", variable=self.sb, value=1).grid(row=3, column=1,sticky=W)
        Radiobutton(w1, text="2", variable=self.sb, value=2).grid(row=4, column=1,sticky=W)

        Label(w1, text="Parity").grid(row=5, column=0)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w1,self.par,*self.optionList)
        self.parity.grid(row=5,column=1,sticky=E+W)
#units
        Label(w2, text="Flow Rate Units").grid(row=0, column=0,sticky=W)
        self.optionList = ("Gal/min","L/min","L/sec")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=0,column=1,sticky=E+W)
        
        Label(w2, text="Energy Rate Units").grid(row=1, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=1,column=1,sticky=E+W)        

        Label(w2, text="Mass Flow Rate Units").grid(row=2, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=2,column=1,sticky=E+W)

        Label(w2, text="Flow Total Units").grid(row=3, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=3,column=1,sticky=E+W)

        Label(w2, text="Energy Total Units").grid(row=4, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=4,column=1,sticky=E+W)   
        
        Label(w2, text="Mass Total Units").grid(row=5, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=5,column=1,sticky=E+W)

        Label(w2, text="Pulse Output Type").grid(row=6, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=6,column=1,sticky=E+W)

        Label(w2, text="Temp Output Units").grid(row=7, column=0,sticky=W)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(w2,self.par,*self.optionList)
        self.parity.grid(row=7,column=1,sticky=E+W)
     
        
            
        
        n.grid(row=0,column=0)
        Button(master, text="Apply Changes", command=self.apply).grid(row=6, columnspan=2,sticky=E+W)
        

    def validate(self):
    
        if 1<self.check.get()<248:
            print 'true'
            return True
        else:
            print 'false'
            return False
        pass
        
    def apply(self):
        data = dict()
        data['baudrate'] = long(self.br.get())
        data['slave id'] = long(self.did.get())
        data['parity'] = self.optionList.index(self.par.get())
        data['stop bits'] = long(self.sb.get())
        
        s['port'] = self.comList.index(self.com.get())
        print 'ID: '+str(self.did.get()) + ' COM: '+ str(s['port']) + ' Baud: '+str(self.br.get()) + ' Stop: '+str(self.sb.get()) +' Parity: '+str(self.par.get())
        ser = modbus.openConn(s)
        if ser:
            modbus.setup(ser,data)
            ser.close()
        
    def read(self,master):
        
        Label(master, text="Flow Rate").grid(row=1,column=0,sticky=E)
        Label(master, text="Energy Rate").grid(row=2,column=0,sticky=E)
        Label(master, text="Local Temperature").grid(row=3,column=0,sticky=E)
        Label(master, text="Remote Temperature").grid(row=4,column=0,sticky=E)
        Label(master, text="Flow Total").grid(row=5,column=0,sticky=E)
        Label(master, text="Energy Total").grid(row=6,column=0,sticky=E)
        
        self.flowr = StringVar()
        self.energyr = StringVar()
        self.ltemp = StringVar()
        self.rtemp = StringVar()
        self.ftotal = StringVar()
        self.etotal = StringVar()
        
        Label(master, textvariable=self.flowr).grid(row=1,column=1)
        Label(master, textvariable=self.energyr).grid(row=2,column=1)
        Label(master, textvariable=self.ltemp).grid(row=3,column=1)
        Label(master, textvariable=self.rtemp).grid(row=4,column=1)
        Label(master, textvariable=self.ftotal).grid(row=5,column=1)
        Label(master, textvariable=self.etotal).grid(row=6,column=1)
        
        Button(master, text="Reset", command=self.resetf).grid(row=5,column=2)
        Button(master, text="Reset", command=self.resete).grid(row=6,column=2)
        
        Button(master, text="Get Data", command=self.getdata).grid(row=7,column=0,columnspan=2,sticky=E+W)
    
    def resetf():
        pass
      
    def resete():
        pass
    def getdata(self):
        self.flowr.set("0.000")
        #self.energyr = StringVar()
        #self.ltemp = StringVar()
        #self.rtemp = StringVar()
        #self.ftotal = StringVar()
        #self.etotal = StringVar()

'''    
    def appset(self,master):
        
        Label(master, text="Current Device ID").grid(row=0, column=0)
        self.did = Spinbox(master, from_=1, to=248, increment=1, justify=CENTER)
        self.did.grid(row=0, column=1)
        
        Label(master, text="Computer COM Port").grid(row=1, column=0)
        self.comList = ("COM1","COM2","COM3","COM4")
        self.com = StringVar()
        self.com.set(self.comList[0])
        self.comp = OptionMenu(master,self.com,*self.comList)
        self.comp.grid(row=1,column=1,sticky=E+W)
        
        Label(master, text="Baud Rate").grid(row=2, column=0)
        self.br = IntVar()
        self.br.set(9600)
        Radiobutton(master, text="9600", variable=self.br, value=9600).grid(row=2, column=1,sticky=W)
        Radiobutton(master, text="19200", variable=self.br, value=19200).grid(row=3, column=1,sticky=W)
        
        Label(master, text="Stop Bits").grid(row=4, column=0)
        self.sb = IntVar()
        self.sb.set(2)
        Radiobutton(master, text="1", variable=self.sb, value=1).grid(row=4, column=1,sticky=W)
        Radiobutton(master, text="2", variable=self.sb, value=2).grid(row=5, column=1,sticky=W)
        
        Label(master, text="Parity").grid(row=6, column=0)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(master,self.par,*self.optionList)
        self.parity.grid(row=6,column=1,sticky=E+W)

        Button(master, text="Apply Changes", command=self.upapp).grid(row=7, columnspan=2,sticky=E+W)
    
    def upapp(self):
        
        s['port'] = self.comList.index(self.com.get())
        s['baud'] = self.br.get()
        s['party'] = self.par.get()[0]
        s['stopbits'] = self.sb.get()
        s['id'] = self.did.get()
'''        
class Mainmenu(toplevels):

    def __init__(self,master):
        """Setup main menu"""

        #Button(master,text="Application Settings",command=self.appset).grid(row=1,ipadx=7,ipady=5,sticky=E+W)
        Button(master,text="Device Setup",command=self.comset).grid(row=2,columnspan=2,ipady=5,sticky=E+W)
        #Button(master,text="Meter General Settings",command=self.mset).grid(row=3,ipady=5,sticky=E+W)
        Button(master,text="Read Device Data",command=self.read).grid(row=3,columnspan=2,ipady=5,sticky=E+W)

        Label(master, text="COM Port:").grid(row=1, column=0)
        self.comList = ("COM1","COM2","COM3","COM4")
        self.com = StringVar()
        self.com.set(self.comList[0])
        self.comp = OptionMenu(master,self.com,*self.comList)
        self.comp.grid(row=1,column=1,sticky=E+W)
        
        
        '''
    def appset(self):
        """Configure settings for this application"""
        
        apps = Toplevel(bd=10)
        apps.title("Application Settings")
        toplevels.appset(self,apps)
        
        root.withdraw()
        apps.focus_force()
        apps.wait_window(apps)
        root.deiconify()
'''        
    def comset(self):
        """Configure settings on device in default mode"""
        
        port =self.comList.index(self.com.get())
        
        appc = Toplevel(bd=10)
        appc.title("Device Setup")
        #appc.option_add("*Background","blue")
        toplevels.comset(self,appc)
        appc.group(root)
        
        #root.withdraw()
        appc.focus_force()
        appc.wait_window(appc)
        root.deiconify()
        

    def read(self):
        """Read in data from device in default mode"""
        
        port =self.comList.index(self.com.get())
        
        read = Toplevel(bd=10)
        read.title("Read Data")
        toplevels.read(self,read)
        read.group(root)
        
        #root.withdraw()
        read.focus_force()
        read.wait_window(read)
        root.deiconify()


if __name__ == "__main__":

    #first read in our config file to a dictionary
    try:
        config = ConfigParser.ConfigParser()
        config.read('modbus.cfg')
        #s = dict(config.items('Serial'))
        for item in config.items('Function Codes'):
            modbus.fc[item[0]] = int(item[1])
        for item in config.items('Registry Mappings'):
            modbus.reg[item[0]] = int(item[1])
    except ConfigParser.Error:
        util.err('Error Reading Config File')
    #init gui
    root = Tk()
    #root.option_add("*Font", "Helvetica 15 bold")
    #root.option_add("*Background","light blue")
    #root.option_add("*Button*Background", "gray")
    #root.option_add("*Button*Relief", "raised")
    s = Style()
    #s.theme_use('xpnative')
    s.configure('.', font='helvetica 15')
    s.configure('Tab', font='helvetica 8 bold')
    print s.layout('Tab')
    root.title("clark Sonic")
    Mainmenu(root)
    root.mainloop()
