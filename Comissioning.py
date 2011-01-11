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
import warnings

import modbus
import util

s=dict(id=1, port=1, baud=9600, parity='N', stopbits=2)
port=0
class toplevels:

    def comset(self, master):
        
        #setup a tabbed interface
        n = Notebook(master)
        w1 = Frame(n)
        w2 = Frame(n)
        n.add(w1, text='Comm Settings')
        n.add(w2, text='Unit Settings')
        
        Label(w1, text="Device ID").grid(row=0, column=0, pady=(10,20))
        self.id = IntVar()
        self.did = Spinbox(w1, from_=1, to=248, increment=1, width=5, validate="focusout",textvariable=self.id, wrap=True, justify=CENTER)
        self.did['vcmd'] = self.didf
        
        self.did.grid(row=0, column=1, pady=(10,20))

        Label(w1, text="Baud Rate").grid(row=2, column=0, padx=40,sticky=S)
        self.br = IntVar()
        self.br.set(0)
        Radiobutton(w1, text="9600", variable=self.br, value=0).grid(row=2, column=1)
        Radiobutton(w1, text="19200", variable=self.br, value=1).grid(row=3, column=1, sticky=N)

        Label(w1, text="Stop Bits").grid(row=4, column=0,pady=(20,0))
        self.sb = IntVar()
        self.sb.set(2)
        Radiobutton(w1, text="1", variable=self.sb, value=1).grid(row=4, column=1,pady=(20,0))
        Radiobutton(w1, text="2", variable=self.sb, value=2).grid(row=5, column=1)

        Label(w1, text="Parity").grid(row=6, column=0,pady=(20,0))
        self.par = StringVar()
        self.par.set("NONE")
        self.parity = Combobox(w1,textvariable=self.par)
        self.parity['values'] = ("NONE","ODD","EVEN")
        self.parity.grid(row=6,column=1,pady=(20,0))
#units
        Label(w2, text="Flow Rate Units").grid(row=0, column=0,sticky=W)
        self.fru = StringVar()
        self.fr = Combobox(w2,textvariable=self.fru,width=10)
        self.fr['values'] = ("Gal/min","L/min","L/sec")
        self.fru.set(self.fr['values'][0])
        self.fr.grid(row=0,column=1,sticky=E+W)
        
        Label(w2, text="Energy Rate Units").grid(row=1, column=0,sticky=W)
        self.eru = StringVar()
        self.er = Combobox(w2,textvariable=self.eru)
        self.er['values'] = ("BTU/min","kBTU/min","kBTU/hr","kW")
        self.eru.set(self.er['values'][0])
        self.er.grid(row=1,column=1,sticky=E+W)        

        Label(w2, text="Mass Rate Units").grid(row=2, column=0,sticky=W)
        self.mfru = StringVar()
        self.mf = Combobox(w2,textvariable=self.mfru)
        self.mf['values'] = ("lbs/min","Kg/min")
        self.mfru.set(self.mf['values'][0])
        self.mf.grid(row=2,column=1,sticky=E+W)

        Label(w2, text="Flow Total Units").grid(row=3, column=0,sticky=W)
        self.ftu = StringVar()
        self.ft = Combobox(w2,textvariable=self.ftu)
        self.ft['values'] = ("Gal","Liters","Cubic Meters")
        self.ftu.set(self.ft['values'][0])
        self.ft.grid(row=3,column=1,sticky=E+W)

        Label(w2, text="Energy Total Units").grid(row=4, column=0,sticky=W)
        self.etu = StringVar()
        self.et = Combobox(w2,textvariable=self.etu)
        self.et['values'] = ("kBTU","W-hrs","kW-hrs")
        self.etu.set(self.et['values'][0])
        self.et.grid(row=4,column=1,sticky=E+W)   
        
        Label(w2, text="Mass Total Units").grid(row=5, column=0,sticky=W)
        self.mtu = StringVar()
        self.mt = Combobox(w2,textvariable=self.mtu)
        self.mt['values'] = ("lbs","Kg")
        self.mtu.set(self.mt['values'][0])
        self.mt.grid(row=5,column=1,sticky=E+W)

        Label(w2, text="Pulse Output Type").grid(row=6, column=0,sticky=W)
        self.pot = StringVar()
        self.po = Combobox(w2,textvariable=self.pot)
        self.po['values'] = ("FLOW","ENERGY","MASS")
        self.pot.set(self.po['values'][0])
        self.po.grid(row=6,column=1,sticky=E+W)

        Label(w2, text="Temp Output Units").grid(row=7, column=0,sticky=W)
        self.tou = StringVar()
        self.to = Combobox(w2,textvariable=self.tou)
        self.to['values'] = ("F","C")
        self.tou.set(self.to['values'][0])
        self.to.grid(row=7,column=1,sticky=E+W)
     
        Label(w2, text="% Ethylene Glycol").grid(row=8, column=0,sticky=W)
        self.peg = IntVar()
        self.esb = Spinbox(w2,from_=0,to=30,increment=1,width=1,textvariable=self.peg,validate='focusout',wrap=True, justify=CENTER)
        self.esb['vcmd'] = self.pegf
        self.esb.grid(row=8,column=1,sticky=E+W)
        
        Label(w2, text="% Propylene Glycol").grid(row=9, column=0,sticky=W)
        self.ppg = StringVar()
        self.didi = Spinbox(w2,from_=0,to=30,increment=1,width=1,textvariable=self.ppg,validate='focusout',wrap=True, justify=CENTER)
        self.didi['vcmd'] = self.ppgf
        self.didi.grid(row=9,column=1,sticky=E+W)    
        
        n.grid(row=0,column=0)
        Button(master, text="Apply Changes", command=self.apply).grid(row=10, columnspan=2,sticky=E+W)
    
    def didf(self):
        try:
            self.id.get()
        except:
            self.id.set(1)
        if 1<=self.id.get()<=248:
            pass
        elif self.id.get()>248:
            self.id.set(248)
        else:
            self.id.set(1)
        self.did['validate'] = 'focusout'
        return True
            
    def pegf(self):
        try:
            self.peg.get()
        except:
            self.peg.set('0')
        if 0<=int(self.peg.get())<=30:
            pass
        elif int(self.peg.get())>30:
            self.peg.set('30')
        else:
            self.peg.set('0')
        self.esb['validate'] = 'focusout'
        return True
        
    def ppgf(self):
        if not self.ppg.get():
            self.ppg.set('0')
        elif 0<=int(self.ppg.get())<=30:
            pass
        elif int(self.ppg.get())>30:
            self.ppg.set('30')
        else:
            self.ppg.set('0')   
        self.didi['validate'] = 'focusout'
        return True
    
    def validate(self):
        pass
        
    def apply(self):
        data = dict()
        data['baudrate'] = long(self.br.get())
        data['slave id'] = long(self.did.get())
        data['parity'] = self.parity['values'].index(self.par.get())
        data['stop bits'] = long(self.sb.get())
        
        s['port'] = int(self.com.get()[-1])-1
        print "sport:::"+str(s['port'])
        print 'ID: '+str(self.did.get()) + ' COM: '+ str(s['port']) + ' Baud: '+str(self.br.get()) + ' Stop: '+str(self.sb.get()) +' Parity: '+str(self.par.get())
        ser = modbus.openConn(s)
        if ser:
            modbus.setup(ser,data)
            ser.close()
        
    def read(self,master):
        
        Label(master, text="Volume Flow Rate").grid(row=1,column=0,sticky=W)
        Label(master, text="Mass Flow Rate").grid(row=2,column=0,sticky=W)
        Label(master, text="Energy Rate").grid(row=3,column=0,sticky=W)
        Label(master, text="Local Temperature").grid(row=4,column=0,sticky=W,pady=(15,0))
        Label(master, text="Remote Temperature").grid(row=5,column=0,sticky=W)
        Label(master, text="Volume Flow Total").grid(row=6,column=0,sticky=W,pady=(15,0))
        Label(master, text="Mass Flow Total").grid(row=7,column=0,sticky=W)
        Label(master, text="Heating Energy Total").grid(row=8,column=0,sticky=W)
        Label(master, text="Cooling Energy Total").grid(row=9,column=0,sticky=W)
        Label(master, text="Energy Total").grid(row=10,column=0,sticky=W)
        
        self.volr = StringVar()
        self.massr = StringVar()
        self.energyr = StringVar()
        self.ltemp = StringVar()
        self.rtemp = StringVar()
        self.vftotal = StringVar()
        self.mftotal = StringVar()
        self.hetotal = StringVar()
        self.cetotal = StringVar()
        self.etotal = StringVar()
        #init values so screen looks ok
        self.volr.set("0.000")
        self.massr.set("0.000")
        self.energyr.set("0.000")
        self.ltemp.set("0.000")
        self.rtemp.set("0.000")
        self.vftotal.set("0.000")
        self.mftotal.set("0.000")
        self.hetotal.set("0.000")
        self.cetotal.set("0.000")
        self.etotal.set("0.000")
        
        Label(master, textvariable=self.volr).grid(row=1,column=1,padx=10)
        Label(master, textvariable=self.massr).grid(row=2,column=1,padx=10)
        Label(master, textvariable=self.energyr).grid(row=3,column=1,padx=10)
        Label(master, textvariable=self.ltemp).grid(row=4,column=1,padx=10,pady=(15,0))
        Label(master, textvariable=self.rtemp).grid(row=5,column=1,padx=10)
        Label(master, textvariable=self.vftotal).grid(row=6,column=1,padx=10,pady=(15,0))
        Label(master, textvariable=self.mftotal).grid(row=7,column=1,padx=10)
        Label(master, textvariable=self.hetotal).grid(row=8,column=1,padx=10)
        Label(master, textvariable=self.cetotal).grid(row=9,column=1,padx=10)
        Label(master, textvariable=self.etotal).grid(row=10,column=1,padx=10)
        
        Button(master, text="Reset", command=self.resetvf).grid(row=6,column=2,pady=(15,0))
        Button(master, text="Reset", command=self.resetmf).grid(row=7,column=2)
        Button(master, text="Reset", command=self.resethe).grid(row=8,column=2)
        Button(master, text="Reset", command=self.resetce).grid(row=9,column=2)
        Button(master, text="Reset", command=self.resete).grid(row=10,column=2)
        
        Button(master, text="Get Data", command=self.getdata).grid(row=11,column=0,columnspan=2,sticky=E+W)
    
    def resetvf(self):
        pass
    
    def resetmf(self):
        pass
      
    def resethe(self):
        pass
        
    def resetce(self):
        pass
        
    def resete(self):
        pass
    
    def getdata(self):
        self.volr.set("20")
        self.massr.set("6")
        self.energyr.set("5")
        self.ltemp.set("60")
        self.rtemp.set("65")
        self.vftotal.set("789.5")
        self.mftotal.set("236.9")
        self.hetotal.set("96.7")
        self.cetotal.set("100.7")
        self.etotal.set("197.4")

    
class Mainmenu(toplevels):
    def __init__(self,master):
        """Setup main menu"""
        Button(master,text="Device Setup",command=self.comset).grid(row=2,columnspan=2,ipady=5,sticky=E+W)
        Button(master,text="Read Device Data",command=self.read).grid(row=3,columnspan=2,ipady=5,sticky=E+W)

        Label(master, text="COM Port: ").grid(row=1, column=0)
        self.com = StringVar()
        self.com.set("COM1")
        self.comp = Combobox(master,textvariable=self.com,width=7)
        self.comp['values'] = ("COM1","COM2","COM3","COM4")
        self.comp.grid(row=1,column=1,sticky=E+W)
                   
    def comset(self):
        """Configure settings on device in default mode"""
        
        port =self.comp['values'].index(self.com.get())
        appc = Toplevel(bd=10)
        appc.title("clark Sonic Energy Meter")
        appc.iconbitmap(r'res/favicon.ico')
        toplevels.comset(self,appc)
        appc.group(root)
        appc.focus_force()
        appc.wait_window(appc)
        root.focus_force()
        
    def read(self):
        """Read in data from device in default mode"""
        
        port =self.comp['values'].index(self.com.get())
        
        read = Toplevel(bd=10)
        read.title("clark Sonic Energy Meter")
        read.iconbitmap(r'res/favicon.ico')
        toplevels.read(self,read)
        read.group(root)
        
        #root.withdraw()
        read.focus_force()
        read.wait_window(read)
        root.focus_force()
        #root.deiconify()

if __name__ == "__main__":

    #add this to supress error on program close
    #sys.stdout = open("run.log", "w")
    #sys.stderr = open("error.log", "w")
    
    #first read in our config file to a dictionary
    try:
        config = ConfigParser.ConfigParser()
        config.read(r'res/modbus.cfg')
        #s = dict(config.items('Serial'))
        for item in config.items('Function Codes'):
            modbus.fc[item[0]] = int(item[1])
        for item in config.items('Registry Mappings'):
            modbus.reg[item[0]] = int(item[1])
    except ConfigParser.Error:
        util.err('Error Reading Config File')
        
    #init gui
    root = Tk()
    sty = Style()
    #s.theme_use('xpnative')
    sty.configure('.', font='helvetica 15')
    sty.configure('Tab', font='helvetica 8 bold')
    root.title("clark Sonic")
    root.iconbitmap(r'res/favicon.ico')
    Mainmenu(root)
    root.mainloop()
