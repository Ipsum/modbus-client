#TODO
#-Remove stopbits
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
import subprocess
from Tkinter import *
from ttk import *
import ConfigParser
import warnings

import modbus
import util

util.DEVICE_ID=1
s=dict(port=1, baud=9600, parity='N', stopbits=2) #current sets
ds=dict(id=1, port=1, baud=9600, parity='N', stopbits=2) #default sets
default = dict()
port=0
class toplevels:

    def comset(self, master):
        
        #setup a tabbed interface
        self.master = master
        self.n = Notebook(self.master)
        menubar = Menu(self.master)
        self.master['menu'] = menubar
        w1 = Frame(self.n)
        w2 = Frame(self.n)
        w3 = Frame(master)
        #w4 = Labelframe(w1,text='Current Meter Settings')
        self.n.add(w1, text='Comm Settings')
        self.n.add(w2, text='Unit Settings')
#Disabled for production
        #setup menubar
#        self.logEnbled = StringVar()
#        menu_file = Menu(menubar)
#        menu_logging = Menu(menubar)
#        menu_help = Menu(menubar)
#        menubar.add_cascade(menu=menu_file, label='File')
#        menubar.add_cascade(menu=menu_logging, label='Logging')
#        menubar.add_cascade(menu=menu_help, label='Help')
#        
#        menu_file.add_command(label='Exit', command=self.exitcmd)
#        menu_logging.add_checkbutton(label='Log!', variable=self.logEnbled, onvalue=1, offvalue=0)
#        menu_logging.add_command(label='Settings...', command=self.logSettings)
#        menu_help.add_command(label='Contents', command=self.help)
#        menu_help.add_command(label='About', command=self.about)
#
        Label(w1, text="COM Port: ").grid(row=0,column=0,pady=(10,20))
        self.com = StringVar()
        self.com.set("COM1")
        self.comp = Combobox(w1,textvariable=self.com,justify=CENTER,width=10)
        self.comp['values'] = ("COM1","COM2","COM3","COM4")
        self.comp.grid(row=0,column=1,pady=(10,20))
        self.comp['state'] = 'readonly'
        
        port =self.comp['values'].index(self.com.get())
        
        Label(w1, text="Device ID").grid(row=1, column=0, padx=40)
        self.id = IntVar()
        self.id.set(default["id"])
        self.did = Spinbox(w1, from_=1, to=248, increment=1, width=5, validate="focusout",textvariable=self.id, wrap=True, justify=CENTER)
        self.did['vcmd'] = self.didf
        self.did.grid(row=1, column=1, pady=(10,20))

        Label(w1, text="Baud Rate").grid(row=2, column=0, padx=40,sticky=S)
        self.br = IntVar()
        self.br.set(default["br"])
        Radiobutton(w1, text="9600", variable=self.br, value=0).grid(row=2, column=1)
        Radiobutton(w1, text="19200", variable=self.br, value=1).grid(row=3, column=1, sticky=N)

        #Label(w1, text="Stop Bits").grid(row=4, column=0,pady=(20,0))
        #self.sb = IntVar()
        #self.sb.set(2)
        #Radiobutton(w1, text="1", variable=self.sb, value=1).grid(row=4, column=1,pady=(20,0))
        #Radiobutton(w1, text="2", variable=self.sb, value=2).grid(row=5, column=1)

        Label(w1, text="Parity").grid(row=6, column=0,pady=(20,0))
        self.par = StringVar()
        self.parity = Combobox(w1,textvariable=self.par,justify=CENTER,width=10)
        self.parity['values'] = ("NONE","ODD","EVEN")
        self.par.set(self.parity['values'][default["pa"]])
        self.parity.grid(row=6,column=1,pady=(20,0))
        self.parity['state'] = 'readonly'
        
        self.jmprButton = Button(w1, text="Jumper is ON", command=self.jmpr)
        self.jmprButton.grid(row=7,column=0,columnspan=2,pady=(30,0),padx=(40,0))
        
        #Label(w4, text="Device ID").grid(row=0, column=0, pady=(10,20))
        #self.idNow = IntVar()
        #self.idNow.set(default["id"])
        #self.didNow = Spinbox(w4, from_=1, to=248, increment=1, width=5, validate="focusout",textvariable=self.idNow, wrap=True, justify=CENTER)
        #self.didNow['vcmd'] = self.didf
        #self.didNow.grid(row=0, column=1, pady=(10,20))
        
        #Label(w4, text="Baud Rate").grid(row=2, column=0, padx=40,sticky=S)
        #self.brNow = IntVar()
        #self.brNow.set(default["br"])
        #Radiobutton(w4, text="9600", variable=self.brNow, value=0).grid(row=2, column=1)
        #Radiobutton(w4, text="19200", variable=self.brNow, value=1).grid(row=3, column=1, sticky=N)

        #Label(w4, text="Stop Bits").grid(row=4, column=0,pady=(20,0))
        #self.sbNow = IntVar()
        #self.sbNow.set(2)
        #Radiobutton(w4, text="1", variable=self.sbNow, value=1).grid(row=4, column=1,pady=(20,0))
        #Radiobutton(w4, text="2", variable=self.sbNow, value=2).grid(row=5, column=1)

        #Label(w4, text="Parity").grid(row=6, column=0,pady=(20,0))
        #self.parNow = StringVar()
        #self.parityNow = Combobox(w4,textvariable=self.parNow,justify=CENTER,width=10)
        #self.parityNow['values'] = ("NONE","ODD","EVEN")
        #self.parNow.set(self.parityNow['values'][default["pa"]])
        #self.parityNow.grid(row=6,column=1,pady=(20,0))
        #self.parityNow['state'] = 'readonly'
#units
        Label(w2, text="Flow Rate Units").grid(row=0, column=0,sticky=W)
        self.fru = StringVar()
        self.fr = Combobox(w2,textvariable=self.fru,justify=CENTER,width=15)
        self.fr['values'] = ("Gal/min","L/min","L/sec")
        self.fru.set(self.fr['values'][default["fr"]])
        self.fr.grid(row=0,column=1)
        self.fr['state'] = 'readonly'
        
        Label(w2, text="Energy Rate Units").grid(row=1, column=0,sticky=W)
        self.eru = StringVar()
        self.er = Combobox(w2,textvariable=self.eru,justify=CENTER,width=15)
        self.er['values'] = ("BTU/min","kBTU/min","kBTU/hr","kW")
        self.eru.set(self.er['values'][default["er"]])
        self.er.grid(row=1,column=1)
        self.er['state'] = 'readonly'        

        Label(w2, text="Mass Rate Units").grid(row=2, column=0,sticky=W)
        self.mfru = StringVar()
        self.mf = Combobox(w2,textvariable=self.mfru,justify=CENTER,width=15)
        self.mf['values'] = ("lbs/min","Kg/min")
        self.mfru.set(self.mf['values'][default["mf"]])
        self.mf.grid(row=2,column=1)
        self.mf['state'] = 'readonly'

        Label(w2, text="Flow Total Units").grid(row=3, column=0,sticky=W)
        self.ftu = StringVar()
        self.ft = Combobox(w2,textvariable=self.ftu,justify=CENTER,width=15)
        self.ft['values'] = ("Gal","Liters","Cubic Meters")
        self.ftu.set(self.ft['values'][default["ft"]])
        self.ft.grid(row=3,column=1)
        self.ft['state'] = 'readonly'

        Label(w2, text="Energy Total Units").grid(row=4, column=0,sticky=W)
        self.etu = StringVar()
        self.et = Combobox(w2,textvariable=self.etu,justify=CENTER,width=15)
        self.et['values'] = ("kBTU","W-hrs","kW-hrs")
        self.etu.set(self.et['values'][default["et"]])
        self.et.grid(row=4,column=1)
        self.et['state'] = 'readonly'        
        
        Label(w2, text="Mass Total Units").grid(row=5, column=0,sticky=W)
        self.mtu = StringVar()
        self.mt = Combobox(w2,textvariable=self.mtu,justify=CENTER,width=15)
        self.mt['values'] = ("lbs","Kg")
        self.mtu.set(self.mt['values'][default["mt"]])
        self.mt.grid(row=5,column=1)
        self.mt['state'] = 'readonly'

        Label(w2, text="Pulse Output Type").grid(row=6, column=0,sticky=W)
        self.pot = StringVar()
        self.po = Combobox(w2,textvariable=self.pot,justify=CENTER,width=15)
        self.po['values'] = ("FLOW","ENERGY","MASS")
        self.pot.set(self.po['values'][default["po"]])
        self.po.grid(row=6,column=1)
        self.po['state'] = 'readonly'

        Label(w2, text="Temp Output Units").grid(row=7, column=0,sticky=W)
        self.tou = StringVar()
        self.to = Combobox(w2,textvariable=self.tou,justify=CENTER,width=15)
        self.to['values'] = ("F","C")
        self.tou.set(self.to['values'][default["to"]])
        self.to.grid(row=7,column=1)
        self.to['state'] = 'readonly'
        
        Label(w2, text="Media Type").grid(row=8, column=0,sticky=W)
        self.met = StringVar()
        self.me = Combobox(w2,textvariable=self.met,justify=CENTER,width=15)
        self.me['values'] = ("Water","Ethylene (92%)","Ethylene (95.5%)","Propylene (94%)","Propylene (96%)")
        self.met.set(self.me['values'][default["me"]])
        self.me.grid(row=8,column=1)
        self.me.bind('<<ComboboxSelected>>', self.mediaf)
        self.me['state'] = 'readonly'
        
        Label(w2, text="% Ethylene Glycol").grid(row=9, column=0,sticky=W)
        self.peg = IntVar()
        self.peg.set(default["peg"])
        self.esb = Spinbox(w2,from_=10,to=60,increment=5,width=5,textvariable=self.peg,validate='focusout',wrap=True, justify=CENTER)
        self.esb['vcmd'] = self.pegf
        self.esb.grid(row=9,column=1)
        self.esb['state'] = 'disabled'
    
        Label(w2, text="% Propylene Glycol").grid(row=10, column=0,sticky=W)
        self.ppg = StringVar()
        self.ppg.set(default["ppg"])
        self.didi = Spinbox(w2,from_=10,to=60,increment=5,width=5,textvariable=self.ppg,validate='focusout',wrap=True, justify=CENTER)
        self.didi['vcmd'] = self.ppgf
        self.didi.grid(row=10,column=1)   
        self.didi['state'] = 'disabled'
        
        self.n.grid(row=0,column=0)
        self.applyButton = Button(master, text="Apply Settings", command=self.apply)
        self.applyButton.grid(row=10,column=0,sticky=E+W)
        
        self.pbar = Progressbar(master,orient="horizontal",maximum=20,mode="determinate")
        self.pbar.grid(row=10, columnspan=2, sticky=E+W)
        self.pbar.grid_remove()
    
        Label(w3, text="Volume Flow Rate").grid(row=1,column=0,sticky=W)
        Label(w3, text="Mass Flow Rate").grid(row=2,column=0,sticky=W)
        Label(w3, text="Energy Rate").grid(row=3,column=0,sticky=W)
        Label(w3, text="Local Temperature").grid(row=4,column=0,sticky=W,pady=(15,0))
        Label(w3, text="Remote Temperature").grid(row=5,column=0,sticky=W)
        Label(w3, text="Volume Flow Total").grid(row=6,column=0,sticky=W,pady=(15,0))
        Label(w3, text="Mass Flow Total").grid(row=7,column=0,sticky=W)
        Label(w3, text="Heating Energy Total").grid(row=8,column=0,sticky=W)
        Label(w3, text="Cooling Energy Total").grid(row=9,column=0,sticky=W)
        
        self.blank = StringVar()
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
        self.blank.set("  ")
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
        
        Label(w3, textvariable=self.blank).grid(row=0,column=0,padx=10)
        Label(master, textvariable=self.blank).grid(row=0,column=1,padx=10)
        Label(w3, textvariable=self.volr).grid(row=1,column=1,padx=10)
        Label(w3, textvariable=self.massr).grid(row=2,column=1,padx=10)
        Label(w3, textvariable=self.energyr).grid(row=3,column=1,padx=10)
        Label(w3, textvariable=self.ltemp).grid(row=4,column=1,padx=10,pady=(15,0))
        Label(w3, textvariable=self.rtemp).grid(row=5,column=1,padx=10)
        Label(w3, textvariable=self.vftotal).grid(row=6,column=1,padx=10,pady=(15,0))
        Label(w3, textvariable=self.mftotal).grid(row=7,column=1,padx=10)
        Label(w3, textvariable=self.hetotal).grid(row=8,column=1,padx=10)
        Label(w3, textvariable=self.cetotal).grid(row=9,column=1,padx=10)
        #Label(w3, textvariable=self.etotal).grid(row=10,column=1,padx=10)
        
        Button(w3, text="Reset", command=self.resetvf).grid(row=6,column=2,pady=(15,0))
        Button(w3, text="Reset", command=self.resetmf).grid(row=7,column=2)
        Button(w3, text="Reset", command=self.resethe).grid(row=8,column=2)
        Button(w3, text="Reset", command=self.resetce).grid(row=9,column=2)
        #Button(w3, text="Reset", command=self.resete).grid(row=10,column=2)
        
        self.gdb = Button(master, text="Get Data", command=self.getdata)
        self.gdb.grid(row=10,column=2,sticky=E+W)
        #w3['relief'] = 'raised'
        w3.grid(row=0,column=2)
        #w4.grid(row=8,column=0)
        
        self.jmp = 0
#  !Disabled for produciton     
#    def exitcmd(self):
#        pass
#    def logSettings(self):
#        pass
#    def help(self):
#        subprocess.Popen("hh.exe res\comissioning.chm")
#        #os.spawnl(os.P_WAIT,'res\comissioning.chm') 
#    def about(self,master):
#        pass

    def mediaf(self,master):
        media = self.me.get()[0]
        if media=="W":
            self.esb['state'] = 'disabled'
            self.didi['state'] = 'disabled'
        elif media=="E":
            self.esb['state'] = 'normal'
            self.didi['state'] = 'disabled'
        elif media=="P":
            self.esb['state'] = 'disabled'
            self.didi['state'] = 'normal'
        
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
            self.peg.set('10')
        if 10<=int(self.peg.get())<=60:
            pass
        elif int(self.peg.get())>60:
            self.peg.set('60')
        else:
            self.peg.set('10')
        self.esb['validate'] = 'focusout'
        return True
        
    def ppgf(self):
        if not self.ppg.get():
            self.ppg.set('10')
        elif 10<=int(self.ppg.get())<=60:
            pass
        elif int(self.ppg.get())>60:
            self.ppg.set('60')
        else:
            self.ppg.set('10')   
        self.didi['validate'] = 'focusout'
        return True
    
    def validate(self):
        pass
    def jmpr(self):
        if self.jmprButton['text'][-1]=="N":
            self.jmprButton['text'] = "Jumper is OFF"
            util.DEVICE_ID = long(self.did.get())
        else:
            self.jmprButton['text'] = "Jumper is ON"
            util.DEVICE_ID = ds['id']
            
        
    def apply(self):
        
        data = dict()
        data['baudrate'] = long(self.br.get())
        data['slave id'] = long(self.did.get())
        data['parity'] = self.parity['values'].index(self.par.get())
        data['flow rate units'] = self.fr['values'].index(self.fru.get())
        data['energy rate units'] = self.er['values'].index(self.eru.get())+3
        data['mass flow rate units'] = self.mf['values'].index(self.mfru.get())+7
        data['flow total units'] = self.ft['values'].index(self.ftu.get())+9
        data['energy total units'] = self.et['values'].index(self.etu.get())+12
        data['mass total units'] = self.mt['values'].index(self.mtu.get())+15
        data['pulse output'] = self.po['values'].index(self.pot.get())
        data['temperature units'] = self.to['values'].index(self.tou.get())
        data['media type'] = self.fr['values'].index(self.fru.get())
        if self.esb["state"]=="normal":
            data['per cent'] = long(self.peg.get())
        elif self.didi["state"]=="normal":
            data['per cent'] = long(self.ppg.get())
        else:
            data['per cent'] = 10
        
        #Check for jumper and setup comm
        if not self.jmprButton['text'][-1]=="N":
            util.DEVICE_ID = data['slave id']
            s['parity'] = data['parity']
            s['baud'] = data['baudrate']
        else:
            util.DEVICE_ID = ds['id']
            s['parity'] = ds['parity']
            s['baud'] = ds['baud']
            
        #set defaults
        defaults.set("Settings","id",str(self.did.get()))
        defaults.set("Settings","br",str(self.br.get()))
        defaults.set("Settings","pa",str(self.parity['values'].index(self.par.get())))
        defaults.set("Settings","fr",str(self.fr['values'].index(self.fru.get())))
        defaults.set("Settings","er",str(self.er['values'].index(self.eru.get())))
        defaults.set("Settings","mf",str(self.mf['values'].index(self.mfru.get())))
        defaults.set("Settings","ft",str(self.ft['values'].index(self.ftu.get())))
        defaults.set("Settings","et",str(self.et['values'].index(self.etu.get())))
        defaults.set("Settings","mt",str(self.mt['values'].index(self.mtu.get())))
        defaults.set("Settings","po",str(self.po['values'].index(self.pot.get())))
        defaults.set("Settings","to",str(self.to['values'].index(self.tou.get())))
        defaults.set("Settings","me",str(default["me"]))
        defaults.set("Settings","peg",str(default["peg"]))
        defaults.set("Settings","ppg",str(default["ppg"]))
        
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            self.pbar.grid()
            self.applyButton.grid_remove()
            self.pbar.start(50)
            self.master.update()
            modbus.setup(self.master,ser,data)
            ser.close()
            self.pbar.stop()
            self.pbar.grid_remove()
            self.applyButton.grid()
            
    def read(self,master):
        self.master = master
        Label(master, text="Volume Flow Rate").grid(row=1,column=0,sticky=W)
        Label(master, text="Mass Flow Rate").grid(row=2,column=0,sticky=W)
        Label(master, text="Energy Rate").grid(row=3,column=0,sticky=W)
        Label(master, text="Local Temperature").grid(row=4,column=0,sticky=W,pady=(15,0))
        Label(master, text="Remote Temperature").grid(row=5,column=0,sticky=W)
        Label(master, text="Volume Flow Total").grid(row=6,column=0,sticky=W,pady=(15,0))
        Label(master, text="Mass Flow Total").grid(row=7,column=0,sticky=W)
        Label(master, text="Heating Energy Total").grid(row=8,column=0,sticky=W)
        Label(master, text="Cooling Energy Total").grid(row=9,column=0,sticky=W)
        #Label(master, text="Energy Total").grid(row=10,column=0,sticky=W)
        
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
        #Label(master, textvariable=self.etotal).grid(row=10,column=1,padx=10)
        
        Button(master, text="Reset", command=self.resetvf).grid(row=6,column=2,pady=(15,0))
        Button(master, text="Reset", command=self.resetmf).grid(row=7,column=2)
        Button(master, text="Reset", command=self.resethe).grid(row=8,column=2)
        Button(master, text="Reset", command=self.resetce).grid(row=9,column=2)
        #Button(master, text="Reset", command=self.resete).grid(row=10,column=2)
        
        self.gdb = Button(master, text="Get Data", command=self.getdata)
        self.gdb.grid(row=11,column=0,columnspan=2,sticky=E+W)
        
    def resetvf(self):
        print "vf"
        resp = 0
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            try:
                print "ser=yes"
                resp = modbus.writeReg(ser,modbus.fc['reset'],int(modbus.reg['reset flow total']),0)
                ser.close()
            except Exception, e:
                print "exception: "+str(e)
                return False
        if resp:
            print "zeroed"
            self.vftotal.set("0.0")
        else:
            print "bad resp: "+str(resp)
            
    
    def resetmf(self):
        resp = 0
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            try:
                resp = modbus.writeReg(ser,modbus.fc['reset'],int(modbus.reg['reset mass total']),0)
                ser.close()
            except:
                return False
        if resp:
            self.mftotal.set("0.0")
      
    def resethe(self):
        resp = 0
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            try:
                resp = modbus.writeReg(ser,modbus.fc['reset'],int(modbus.reg['reset heating total']),0)
                ser.close()
            except:
                return False
        if resp:
            self.hetotal.set("0.0")
        
    def resetce(self):
        resp = 0
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            try:
                resp = modbus.writeReg(ser,modbus.fc['reset'],int(modbus.reg['reset cooling total']),0)
                ser.close()
            except:
                return False
        if resp:
            self.cetotal.set("0.0")
        
    def resete(self):
        pass
    
    def getdata(self):
        self.gdb['state'] = 'disabled'
        self.master.update()
        resp = 0
        if not self.jmprButton['text'][-1]=="N":
            util.DEVICE_ID = long(self.did.get())
        else:
            util.DEVICE_ID = ds['id']
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            resp = modbus.getData(ser)
            ser.close()
        if resp:
            print resp
            self.volr.set("%.2f"%resp[3])
            self.energyr.set("%.3f"%resp[4])
            self.massr.set("%.2f"%resp[5])
            self.vftotal.set("%.0f"%resp[6])
            self.hetotal.set("%.0f"%resp[7])
            self.cetotal.set("%.0f"%resp[8])
            self.mftotal.set("%.0f"%resp[9])
            self.ltemp.set("%.2f"%resp[10])
            self.rtemp.set("%.2f"%resp[11])
            #self.etotal.set("%.8s"%(resp[7]+resp[8]))
            if self.logEnbled:
                util.logcreate("c:\log.csv")
                util.log("c:\log.csv",resp[3:11])
        else:
            self.gdb['state'] = 'normal'
            return False
        self.gdb['state'] = 'normal'
    
class Mainmenu(toplevels):
    def __init__(self,master):
        """Setup main menu"""
       # Button(master,text="Device Setup",command=self.comset).grid(row=3,columnspan=2,ipady=5,sticky=E+W)
       # Button(master,text="Read Device Data",command=self.read).grid(row=4,columnspan=2,ipady=5,sticky=E+W)
        self.comset()
       # Label(master, text="COM Port: ").grid(row=1, column=0,sticky='w')
       # self.com = StringVar()
       # self.com.set("COM1")
       # self.comp = Combobox(master,textvariable=self.com,width=7)
       # self.comp['values'] = ("COM1","COM2","COM3","COM4")
       # self.comp.grid(row=1,column=1,sticky=E+W)
        
        #Label(master, text="MODBUS ID: ").grid(row=2, column=0,sticky='w')
        #self.mod = IntVar()
        #self.modid = Spinbox(master, from_=1, to=248, increment=1, width=5, validate="focusout",textvariable=self.mod, wrap=True, justify=CENTER)
        #self.modid['vcmd'] = self.didf
        #self.modid.grid(row=2,column=1,sticky=E+W)
                   
    def comset(self):
        """Configure settings on device in default mode"""
        root.withdraw()
        #port =self.comp['values'].index(self.com.get())
        try:
            self.appc.deiconify()
            self.appc.focus_force()
        except:
            self.appc = Toplevel(bd=10)
            self.appc.title("clark Sonic Energy Meter")
            self.appc.iconbitmap(r'res/favicon.ico')
            toplevels.comset(self,self.appc)
            self.appc.group(root)
            self.appc.focus_force()
            self.appc.wait_window(self.appc)
            #write default settings
            with open(r'res/settings.cfg','w') as defaultwriter:
                defaults.write(defaultwriter)
            for item in defaults.items('Settings'):
                default[item[0]]=int(item[1])
            #root.deiconify()    
            #root.focus_force()
            root.destroy()
            
    def read(self):
        """Read in data from device in default mode"""
        
        port =self.comp['values'].index(self.com.get())
        try:
            self.read.deiconify()
            self.read.focus_force()
        except:
            self.read = Toplevel(bd=10)
            self.read.title("clark Sonic Energy Meter")
            self.read.iconbitmap(r'res/favicon.ico')
            toplevels.read(self,self.read)
            self.read.group(root)
            self.read.focus_force()
            self.read.wait_window(self.read)
            root.deiconify() 
            root.focus_force()

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
    try:
        defaults = ConfigParser.ConfigParser()
        
        #open file for both reading and writing
        #defaultwriter = open(r'res/settings.cfg')
        defaults.read(r'res/settings.cfg')
        for item in defaults.items('Settings'):
            default[item[0]]=int(item[1])
    except ConfigParser.Error:
        with open(r'res/settings.cfg','w') as defaultwriter:
            defaults.add_section("Settings")
            defaults.set("Settings","id","1")
            defaults.set("Settings","br","0")
            defaults.set("Settings","pa","0")
            defaults.set("Settings","fr","0")
            defaults.set("Settings","er","0")
            defaults.set("Settings","mf","0")
            defaults.set("Settings","ft","0")
            defaults.set("Settings","et","0")
            defaults.set("Settings","mt","0")
            defaults.set("Settings","po","0")
            defaults.set("Settings","to","0")
            defaults.set("Settings","me","0")
            defaults.set("Settings","peg","30")
            defaults.set("Settings","ppg","30")
            defaults.write(defaultwriter)
            for item in defaults.items('Settings'):
                default[item[0]]=int(item[1])
    except:
        util.err('Error Reading Config File')
        
    #init gui
    root = Tk()
    sty = Style()
    #s.theme_use('xpnative')
    sty.configure('.', font='helvetica 15')
    sty.configure('Tab', font='helvetica 8 bold')
    root.title("clark Sonic")
    root.iconbitmap(r'res/favicon.ico')
    root.option_add('*tearOff', FALSE)
    Mainmenu(root)
    root.mainloop()
