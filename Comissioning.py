#TODO
#-Check Responses to writes
#-implement logging
#-implement config file
#-implement cli
#-implement debug interface

import os
from Tkinter import *

import modbus

s=dict(id=1, port=0, baud=9600, parity='N', stopbits=2)

class toplevels:

    def comset(self, master):

        Label(master, text="New Device ID").grid(row=0, columnspan=2)
        self.did = Spinbox(master, from_=1, to=248, increment=1, justify=CENTER)
        self.did.grid(row=1, columnspan=2)

        Label(master, text="Baud Rate").grid(row=2, column=0)
        self.br = IntVar()
        self.br.set(9600)
        Radiobutton(master, text="9600", variable=self.br, value=9600).grid(row=3, column=0)
        Radiobutton(master, text="19200", variable=self.br, value=19200).grid(row=4, column=0)

        Label(master, text="Stop Bits").grid(row=2, column=1)
        self.sb = IntVar()
        self.sb.set(2)
        Radiobutton(master, text="1", variable=self.sb, value=1).grid(row=3, column=1)
        Radiobutton(master, text="2", variable=self.sb, value=2).grid(row=4, column=1)

        Label(master, text="Parity").grid(row=5,column=0)
        self.optionList = ("NONE","ODD","EVEN")
        self.par = StringVar()
        self.par.set(self.optionList[0])
        self.parity = OptionMenu(master,self.par,*self.optionList)
        self.parity.grid(row=5,column=0,columnspan=2,sticky=E)

        Button(master, text="Apply Changes", command=self.apply).grid(row=7, columnspan=2)
        

    def apply(self):
        
        print 'ID: '+str(self.did.get()) + ' Baud: '+str(self.br.get()) + ' Stop: '+str(self.sb.get()) +' Parity: '+str(self.par.get())
        modbus.writeReg(s,1,6,250,long(self.br.get()))
        modbus.writeReg(s,1,6,251,long(self.did.get()))
        modbus.writeReg(s,1,6,252,self.optionList.index(self.par.get()))
        modbus.writeReg(s,1,6,253,long(self.sb.get()))

    
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
        
class Mainmenu(toplevels):

    def __init__(self,master):
        """Setup main menu"""

        Button(master,text="Application Settings",command=self.appset).grid(row=1,ipadx=7,ipady=5,sticky=E+W)
        Button(master,text="Meter Communications Settings",command=self.comset).grid(row=2,ipady=5,sticky=E+W)
        Button(master,text="Meter General Settings",command=self.mset).grid(row=3,ipady=5,sticky=E+W)
        Button(master,text="Read Meter Data",command=self.read).grid(row=4,ipady=5,sticky=E+W)

    def appset(self):
        """Configure settings for this application"""
        
        apps = Toplevel(bd=10)
        apps.title("Application Settings")
        toplevels.appset(self,apps)
        
        root.withdraw()
        apps.focus_force()
        apps.wait_window(apps)
        root.deiconify()
        
    def comset(self):
        """Configure settings on device"""
    
        appc = Toplevel(bd=10)
        appc.title("Meter Settings")
        toplevels.comset(self,appc)
        
        root.withdraw()
        appc.focus_force()
        appc.wait_window(appc)
        root.deiconify()
        
    def mset(self):
        pass #TODO
    def read(self):
        pass #TODO


if __name__ == "__main__":        
    root = Tk()
    root.option_add("*Font", "Helvetica 15 bold")
    root.option_add("*Button*Relief", "raised")
    root.title("Clark Sonic")
    Mainmenu(root)
    root.mainloop()
