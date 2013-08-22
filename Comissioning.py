#TODO
#-implement cli
#-implement debug interface
'''
Default mode: 
When jumper on the device is set to default mode, the device has:
 * An ID of 1
 * Baud Rate of 9600
 * no parity
 * 2 stop bits
 '''

import os
import sys
import subprocess
from Tkinter import *
from ttk import *
import ConfigParser
import warnings
import time
from threading import Thread

import modbus
import util
import log

__version__ = '2.5.0'
__author__ = 'David Tyler'

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
        w4 = Frame(self.n)
        self.n.add(w1, text='Comm Settings')
        self.n.add(w2, text='Unit Settings')
        self.n.add(w4, text='Logging')
        #create menubar
        menu_file = Menu(menubar)
        menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_help, label='Help')       
        menu_file.add_command(label='Exit', command=self.exitcmd)
        menu_help.add_command(label='Contents', command=self.help)
        menu_help.add_command(label='About', command=self.about)
        #1st tab elements
        Label(w1, text="COM Port: ").grid(row=0,column=0,pady=(10,20))
        self.com = StringVar()
        self.com.set("COM1")
        self.comp = Combobox(w1,textvariable=self.com,justify=CENTER,width=10)
        self.comp['values'] = ("COM1","COM2","COM3","COM4")
        self.comp.grid(row=0,column=1,pady=(10,20))
        self.comp['state'] = 'readonly'
        #grab com port
        port=self.comp['values'].index(self.com.get())
        
        Label(w1, text="Device ID").grid(row=1, column=0, padx=40)
        self.id = IntVar()
        self.id.set(default["id"])
        self.did = Spinbox(w1, from_=1, to=248, increment=1, width=5, validate="focusout",textvariable=self.id, wrap=True, justify=CENTER)
        self.did['vcmd'] = self.didf
        self.did.grid(row=1, column=1, pady=(10,20))

        #baud rate selection box
        Label(w1, text="Baud Rate").grid(row=2, column=0, padx=40,sticky=S)
        self.br = IntVar()
        self.br.set(default["br"])
        self.rb1 = Radiobutton(w1, text="9600", variable=self.br, value=0)
        self.rb2 = Radiobutton(w1, text="19200", variable=self.br, value=1)
        self.rb1.grid(row=2, column=1)
        self.rb2.grid(row=3, column=1, sticky=N)
        self.rb1.bind('<1>', self.rb9600) #trigger of left mouse button
        self.rb2.bind('<1>', self.rb19200)
        util.BAUDRATE = [9600,19200][default["br"]]

        Label(w1, text="Parity").grid(row=6, column=0,pady=(20,0))
        self.par = StringVar()
        self.parity = Combobox(w1,textvariable=self.par,justify=CENTER,width=10)
        self.parity['values'] = ("NONE","ODD","EVEN")
        self.par.set(self.parity['values'][default["pa"]])
        self.parity.grid(row=6,column=1,pady=(20,0))
        self.parity['state'] = 'readonly'
        self.parity.bind('<Leave>', self.parglobal) #trigger on mouse-over
        util.PARITY = self.par.get()[0]
        
        Label(w1, text="Jumper").grid(row=7, column=0,pady=(20,0))
        self.jmprButton = Button(w1, text="ON", command=self.jmpr,width=5)
        self.jmprButton.grid(row=7,column=1,pady=(20,0))       
        #units - 2nd tab
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
        self.et['values'] = ("kBTU","W-hrs","kW-hrs","BTU")
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
        
        Label(w2, text="Pulse Output Source").grid(row=7, column=0,sticky=W)
        self.pos = StringVar()
        self.pulos = Combobox(w2,textvariable=self.pos,justify=CENTER,width=15)
        self.pulos['values'] = ("BOTH","HEATING","COOLING")
        self.pos.set(self.pulos['values'][default["pulos"]])
        self.pulos.grid(row=7,column=1)
        self.pulos['state'] = 'readonly'
        
        Label(w2, text="Temp Output Units").grid(row=8, column=0,sticky=W)
        self.tou = StringVar()
        self.to = Combobox(w2,textvariable=self.tou,justify=CENTER,width=15)
        self.to['values'] = ("F","C")
        self.tou.set(self.to['values'][default["to"]])
        self.to.grid(row=8,column=1)
        self.to['state'] = 'readonly'
        
        Label(w2, text="Media Type").grid(row=9, column=0,sticky=W)
        self.met = StringVar()
        self.me = Combobox(w2,textvariable=self.met,justify=CENTER,width=15)
        self.me['values'] = ("Water","Ethylene (92%)","Ethylene (95.5%)","Propylene (94%)","Propylene (96%)")
        self.met.set(self.me['values'][default["me"]])
        self.me.grid(row=9,column=1)
        self.me.bind('<<ComboboxSelected>>', self.mediaf) #on item selection, activate correct % scrollbox
        self.me['state'] = 'readonly'
        
        Label(w2, text="% Ethylene Glycol").grid(row=10, column=0,sticky=W)
        self.peg = IntVar()
        self.peg.set(default["peg"])
        self.esb = Spinbox(w2,from_=10,to=60,increment=5,width=5,textvariable=self.peg,validate='focusout',wrap=True, justify=CENTER)
        self.esb['vcmd'] = self.pegf
        self.esb.grid(row=10,column=1)
        self.esb['state'] = 'disabled'
    
        Label(w2, text="% Propylene Glycol").grid(row=11, column=0,sticky=W)
        self.ppg = StringVar()
        self.ppg.set(default["ppg"])
        self.didi = Spinbox(w2,from_=10,to=60,increment=5,width=5,textvariable=self.ppg,validate='focusout',wrap=True, justify=CENTER)
        self.didi['vcmd'] = self.ppgf
        self.didi.grid(row=11,column=1)   
        self.didi['state'] = 'disabled'
        #Retrieve Units button
        self.retreive = Button(w2, text="Retrieve Settings", command=self.readunits)
        self.retreive.grid(row=12,columnspan=2,sticky=E+W,pady=5) #UNCOMMENT WHEN FIXED
        #logging - 3rd tab
        Label(w4, text="Logging").grid(row=0,column=0,padx=40,pady=(20,0))
        self.logButton = Button(w4, text="Disabled", command=self.logB)
        self.logButton.grid(row=0,column=1,pady=(20,0))
        
        Label(w4, text="Logging Path").grid(row=2,column=0,columnspan=2,pady=(30,10))
        self.logPathButton = Button(w4, text="C:\\clarklog.csv", command=self.logP,width=22)
        self.logPathButton.grid(row=3,columnspan=2,sticky=E+W,padx=5)
        
        Label(w4, text="Repeat").grid(row=4,column=0,padx=40,pady=(40,0))
        self.repeatButton = Button(w4, text="Off", command=self.repeatB)
        self.repeatButton.grid(row=4,column=1,pady=(40,0))
        
        Label(w4, text="Repeat time").grid(row=5,column=0,pady=(20,0))
        self.rtimev = StringVar()
        self.rtimev.set("5 sec")
        self.repeatTime = Combobox(w4,textvariable=self.rtimev,justify=CENTER,width=10)
        self.repeatTime['values'] = ("5 sec", "10 sec", "30 sec", "1 min", "5 min", "30 min", "1 hr")
        self.repeatTime.grid(row=5,column=1,pady=(20,0))
        self.repeatTime['state'] = 'readonly'
        self.repeatTime.bind('<<ComboboxSelected>>', self.repeat)
        
        #master
        self.n['width']=300
        self.n.grid(row=0,column=0)
        self.applyButton = Button(master, text="Apply Settings", command=self.apply)
        self.applyButton.grid(row=10,column=0,sticky=E+W)
        
        self.pbar = Progressbar(master,orient="horizontal",maximum=20,mode="determinate")
        self.pbar.grid(row=10, columnspan=2, sticky=E+W)
        self.pbar.grid_remove()
        #Read Data Interface
        Label(w3, text="Volume Flow Rate").grid(row=1,column=0,sticky=W)
        Label(w3, text="Mass Flow Rate").grid(row=2,column=0,sticky=W)
        Label(w3, text="Energy Rate").grid(row=3,column=0,sticky=W)
        Label(w3, text="Local Temperature").grid(row=4,column=0,sticky=W,pady=(15,0))
        Label(w3, text="Remote Temperature").grid(row=5,column=0,sticky=W)
        Label(w3, text="Volume Flow Total").grid(row=6,column=0,sticky=W,pady=(15,0))
        Label(w3, text="Mass Flow Total").grid(row=7,column=0,sticky=W)
        Label(w3, text="Heating Energy Total").grid(row=8,column=0,sticky=W)
        Label(w3, text="Cooling Energy Total").grid(row=9,column=0,sticky=W)
        #init ttk vars
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
        #grid labels
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
        #setup reset buttons
        self.rvf=Button(w3, text="Reset", command=self.resetvf)
        self.rvf.grid(row=6,column=2,pady=(15,0))
        self.rmf=Button(w3, text="Reset", command=self.resetmf)
        self.rmf.grid(row=7,column=2)
        self.rthe=Button(w3, text="Reset", command=self.resethe)
        self.rthe.grid(row=8,column=2)
        self.rce=Button(w3, text="Reset", command=self.resetce)
        self.rce.grid(row=9,column=2)
        #get data button
        self.gdb = Button(master, text="Get Data", command=self.getdata)
        self.gdb.grid(row=10,column=2,sticky=E+W)
        w3.grid(row=0,column=2)
        self.jmp = 0
    def exitcmd(self):
        """closes program"""
        os._exit(99) #unconditional shutdown signal
    def help(self):
        """opens help file in seperate thread"""
        subprocess.Popen("hh.exe res\comissioning.chm")
    def about(self):
        """prints about message in popup"""
        util.msg('''
clark Sonic Commissioning Software

Clark Solutions
Hudson, MA 01749
www.clarksol.com
        
Version: {0}
By: {1}'''.format(__version__,__author__),'About')
        return
        
    def readunits(self):
        """retrieves unit settings from meter"""
        util.errlvl=4
        self.retreive['state'] = 'disabled' #prevent multiple presses
        self.master.update() #prob extranious
        resp = 0
        if not self.jmprButton['text'][-1]=="N": #jumper status
            util.DEVICE_ID = long(self.did.get())
            util.JMP = 0
        else:
            util.DEVICE_ID = ds['id']
        s['port'] = int(self.com.get()[-1])-1 #COM port num
        ser = modbus.openConn(s)
        if ser:
            print "getting units.."
            resp = modbus.getUnits(ser)
            ser.close()
        if resp:
            units = resp[7:24:2]+resp[24:26] #every other num in hex+last 2
            print "units: "+str(units)
            self.pot.set(self.po['values'][int(units[6])%3])
            self.fru.set(self.fr['values'][int(units[0])%3])
            self.eru.set(self.er['values'][(int(units[1])-3)%4])
            self.mfru.set(self.mf['values'][(int(units[2])-7)%2])
            self.ftu.set(self.ft['values'][(int(units[3],16)-9)%3])
            selection = (int(units[4],16)-12)
            if selection==5:
                self.etu.set(self.et['values'][3])
            self.etu.set(self.et['values'][(selection%3])
            self.mtu.set(self.mt['values'][(int(units[5],16)-15)%2])
            self.tou.set(self.to['values'][int(units[7])%2])
            self.met.set(self.me['values'][int(units[8])])
            per=str(int(units[9:],16)) #since 2 digits must specify hex
            self.peg.set(per)
            self.ppg.set(per)
            self.mediaf(util.root)
        if not resp:
            print "units failed"
            
        self.retreive['state'] = 'enabled'
    def repeat(self,master):
        """enable/disable repeat logging"""
        print "\nrepeat function: "
        rtime = self.repeatTime.get()
        if rtime=="Never":
            util.repeat=0
        elif rtime=="5 sec":
            util.repeat=5
        elif rtime=="10 sec":
            util.repeat=10
        elif rtime=="30 sec":
            util.repeat=30
        elif rtime=="1 min":
            util.repeat=60
        elif rtime=="5 min":
            util.repeat=60*5
        elif rtime=="30 min":
            util.repeat=60*30
        elif rtime=="1 hr":
            util.repeat=60*60
        print "util.repeat="+str(util.repeat)
        
    def repeatB(self):
        """repeat enable/disable button"""
        if log.REEN:
            log.REEN = 0
            self.repeatButton['text'] = "Off"
        else:
            log.REEN = 1
            self.repeatButton['text'] = "On"
            
    def logB(self):
        """logging enable/disable button"""
        if log.LOGEN:
            log.disablelog()
            self.logButton['text'] = "Disabled"
        else:
            fail = log.enablelog()
            if fail:
                self.logButton['text'] = "Disabled"
            else:
                self.logButton['text'] = "Enabled"
     
    def logP(self):
        """logging path button"""
        p=log.set_path(self.master)
        self.logPathButton['text']=p
        if log.LOGEN:
            fail = log.enablelog()
            if fail:
                self.logButton['text'] = "Disabled"
            
    def mediaf(self,master):
        """media selection function"""
        media = self.me.get()[0]
        if media=="W": #water
            self.esb['state'] = 'disabled'
            self.didi['state'] = 'disabled'
        elif media=="E": #ethyl
            self.esb['state'] = 'normal'
            self.didi['state'] = 'disabled'
        elif media=="P": #prop
            self.esb['state'] = 'disabled'
            self.didi['state'] = 'normal'
        
    def didf(self):
        """device id bounding"""
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
        """percent ethyl"""
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
        """percent prop glycol"""
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
        """handle jumper button toggle"""
        if self.jmprButton['text'][-1]=="N":
            self.jmprButton['text'] = "OFF"
            util.DEVICE_ID = long(self.did.get())
            #disable reset buttons
            self.rvf['state'] = 'disabled'
            self.rmf['state'] = 'disabled'
            self.rthe['state'] = 'disabled'
            self.rce['state'] = 'disabled'
        else:
            self.jmprButton['text'] = "ON"
            util.DEVICE_ID = ds['id']
            #enable reset buttons
            self.rvf['state'] = 'enabled'
            self.rmf['state'] = 'enabled'
            self.rthe['state'] = 'enabled'
            self.rce['state'] = 'enabled'
            
    def apply(self):
        
        util.errlvl=4
        data = dict()
        data['baudrate'] = long(self.br.get())
        data['slave id'] = long(self.did.get())
        data['parity'] = self.parity['values'].index(self.par.get())
        data['flow rate units'] = self.fr['values'].index(self.fru.get())
        data['energy rate units'] = self.er['values'].index(self.eru.get())+3
        data['mass flow rate units'] = self.mf['values'].index(self.mfru.get())+7
        data['flow total units'] = self.ft['values'].index(self.ftu.get())+9
        data['energy total units'] = self.et['values'].index(self.etu.get())+12
        if data['energy total units']==15:
            data['energy total units'] = 17
        data['mass total units'] = self.mt['values'].index(self.mtu.get())+15
        data['pulse output'] = self.po['values'].index(self.pot.get())
        data['pulse output source'] = self.pulos['values'].index(self.pos.get())
        data['temperature units'] = self.to['values'].index(self.tou.get())
        data['media type'] = self.me['values'].index(self.me.get())
        if self.esb["state"]=="normal":
            data['per cent'] = long(self.peg.get())
        elif self.didi["state"]=="normal":
            data['per cent'] = long(self.ppg.get())
        else:
            data['per cent'] = 10
        
        #Check for jumper and setup comm
        if not self.jmprButton['text'][-1]=="N":
            util.DEVICE_ID = data['slave id']
            #util.PARITY = 'NOE'[data['parity']]
            #util.BAUDRATE = data['baudrate']
            util.JMP = 0
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
        defaults.set("Settings","pulos",str(self.pulos['values'].index(self.pulos.get())))
        defaults.set("Settings","to",str(self.to['values'].index(self.tou.get())))
        defaults.set("Settings","me",str(default["me"]))
        defaults.set("Settings","peg",str(default["peg"]))
        defaults.set("Settings","ppg",str(default["ppg"]))
        
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            #setup to write
            self.pbar.grid() #place progress bar where apply button is
            self.applyButton.grid_remove() #hide apply button
            self.pbar.start(50)
            self.retreive['state'] = 'disabled' #grey out all buttons b/c not threadsafe
            self.rvf['state'] = 'disabled'
            self.rmf['state'] = 'disabled'
            self.rthe['state'] = 'disabled'
            self.rce['state'] = 'disabled'
            self.gdb['state'] = 'disabled'
            self.logPathButton['state'] = 'disabled'
            if not self.jmprButton['text'][-1]=="N": 
                util.JMP = 0 #if jumper off,use custom comm settings
            self.master.update()
            modbus.setup(self.master,ser,data)
            ser.close()
            self.pbar.stop() #restore gui
            self.pbar.grid_remove()
            self.applyButton.grid()
            self.retreive['state'] = 'enabled'
            self.rvf['state'] = 'enabled'
            self.rmf['state'] = 'enabled'
            self.rthe['state'] = 'enabled'
            self.rce['state'] = 'enabled'
            self.gdb['state'] = 'enabled'
            self.logPathButton['state'] = 'enabled'
            
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
        
        self.rvf=Button(master, text="Reset", command=self.resetvf).grid(row=6,column=2,pady=(15,0))
        self.rmf=Button(master, text="Reset", command=self.resetmf).grid(row=7,column=2)
        self.rthe=Button(master, text="Reset", command=self.resethe).grid(row=8,column=2)
        self.rce=Button(master, text="Reset", command=self.resetce).grid(row=9,column=2)
        #Button(master, text="Reset", command=self.resete).grid(row=10,column=2)
        
        self.gdb = Button(master, text="Get Data", command=self.getdata)
        self.gdb.grid(row=11,column=0,columnspan=2,sticky=E+W)
    def rb9600(self,master):
        util.BAUDRATE = 9600
        return
    def rb19200(self,master):
        util.BAUDRATE = 19200
        return
    def parglobal(self,master):
        util.PARITY = self.par.get()[0]
        return
    def resetvf(self):
        """reset volume flow"""
        util.errlvl=4 #error on first error
        resp = 0
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            try:
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
        """reset mass flow"""
        util.errlvl=4 #error on first error
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
        """reset heating energy"""
        util.errlvl=4 #error on first error
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
        """Reset cooling energy"""
        util.errlvl=4 #error on first error
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
        
    def sleeptimer(self,secs):
        """sleep thread for secs seconds"""
        time.sleep(secs)
        
    def getdata(self):
        """Read the whole set of data registers once"""
        sl = self
        self.gdb['state'] = 'disabled' #disable button while reading
        self.master.update()
        resp = 0
        if not self.jmprButton['text'][-1]=="N": #check for jumper
            util.DEVICE_ID = long(self.did.get())
            util.JMP = 0
        else:
            util.DEVICE_ID = ds['id']
        s['port'] = int(self.com.get()[-1])-1
        ser = modbus.openConn(s)
        if ser:
            resp = modbus.getData(ser)
            ser.close()
        if resp:
            util.errlvl=1
            print resp
            self.volr.set("%.2f"%resp[3]) #read and split response
            self.energyr.set("%.3f"%resp[4])
            self.massr.set("%.2f"%resp[5])
            self.vftotal.set("%.0f"%resp[6])
            self.hetotal.set("%.0f"%resp[7])
            self.cetotal.set("%.0f"%resp[8])
            self.mftotal.set("%.0f"%resp[9])
            self.ltemp.set("%.2f"%resp[10])
            self.rtemp.set("%.2f"%resp[11])
            print ":::"
            print str(log.LOGEN)
            if log.LOGEN == 1: #log?
                print "logging!"
                l = log.log(str(resp[3:12])[1:-1].strip())
                if not l:
                    self.logB()
                    log.REEN = 0
                    self.repeatButton['text'] = "Off"
        else:
            #if util.repeat and log.REEN:
            #    self.getdata()
            if util.errlvl<=3:
                util.errlvl+=1
                self.getdata()
            else:
                self.gdb['state'] = 'normal' #restore get button
                return False
                
        if util.repeat and log.REEN and util.errlvl<4: #repeat this function every util.repeat sec if cont log
            print "sleeping for" + str(util.repeat)
            thread = Thread(target=self.sleeptimer,args=(util.repeat,))
            thread.start() #spawn thread for util.repeat secs
            while thread.is_alive(): #while thread is alive, do nothing
                self.master.update()
                if not log.REEN: #if repeat turned off, stop right away
                    break
            if log.REEN: #once thread ends, if still logging, take getdata
                self.getdata()
            
        self.gdb['state'] = 'normal'
    
class Mainmenu(toplevels):
    def __init__(self,master):
        """Setup main menu"""
        self.comset()            
    def comset(self):
        """Configure settings on device in default mode"""
        util.root.withdraw() #hide root window
        try:
            self.appc.deiconify()
            self.appc.focus_force() #bring our gui to the front
        except:
            self.appc = Toplevel(bd=10)
            self.appc.title("clark Sonic Energy Meter")
            self.appc.iconbitmap(r'res/favicon.ico')
            toplevels.comset(self,self.appc)
            self.appc.group(util.root)
            self.appc.focus_force()
            self.appc.wait_window(self.appc)
            #write default settings
            with open(r'res/settings.cfg','w') as defaultwriter: #read in defaults
                defaults.write(defaultwriter)
            for item in defaults.items('Settings'):
                default[item[0]]=int(item[1])

            util.root.destroy()

if __name__ == "__main__":

    #add this to supress error on program close
    cfgpath=os.environ['appdata']+'\\clark Sonic\\'
    #sys.stdout = open(cfgpath+"run.log", "w")
    #sys.stderr = open(cfgpath+"error.log", "w")
    sys.setrecursionlimit(8000) #makes my horrible use of tail 
                                 #recursion work
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
        util.err('Error Reading Config File',1)
    try:
        defaults = ConfigParser.ConfigParser()
        cfgpath=os.environ['appdata']+'\\clark Sonic\\'
        #open file for both reading and writing
        #defaultwriter = open(r'res/settings.cfg')
        if not (os.path.isfile(cfgpath+'settings.cfg')):
            raise ConfigParser.Error
        defaults.readfp(open(cfgpath+'settings.cfg'))
        for item in defaults.items('Settings'):
            default[item[0]]=int(item[1])
        if not default.has_key("pulos"): #cfg changed so make new file on install
            raise ConfigParser.Error
    except ConfigParser.Error:
        print "error"
        if not os.path.exists(cfgpath):
            os.makedirs(cfgpath)
            print "dir made"
        with open(cfgpath+'settings.cfg','w') as defaultwriter:
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
            defaults.set("Settings","pulos","0")
            defaults.set("Settings","to","0")
            defaults.set("Settings","me","0")
            defaults.set("Settings","peg","30")
            defaults.set("Settings","ppg","30")
            defaults.write(defaultwriter)
            for item in defaults.items('Settings'):
                default[item[0]]=int(item[1])
    except:
        util.err('Error Reading Config File',1)
    log.disablelog()    
    #init gui
    util.root = Tk()
    sty = Style()
    #s.theme_use('xpnative')
    sty.configure('.', font='helvetica 15')
    sty.configure('Tab', font='helvetica 8 bold')
    util.root.title("clark Sonic")
    util.root.iconbitmap(r'res/favicon.ico')
    util.root.option_add('*tearOff', FALSE)
    Mainmenu(util.root)
    util.root.mainloop()
