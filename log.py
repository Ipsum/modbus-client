import sys
import os
import util
from datetime import datetime
import tkFileDialog

PATH = "C:\\clarklog.csv"
LOGEN = 0
TYPE = 'csv'

def enablelog():
    "Redirects stdout to a logfile"
    global LOGEN
    #d = datetime.now()
    #filename = d.strftime("%m-%d-%y_%H%M%S")
    #filepath = PATH+filename+".csv"
    try:
        if not os.path.isfile(PATH):
            l = open(PATH,"w")
            if TYPE == 'csv':
                header="Time,Volume Rate,Energy Rate,Mass Rate,Volume Total," \
                    "Heating Total,Cooling Total,Mass Total,Local Temp,Remote Temp\n"
                l.write(header)
        else:
            l = open(PATH,"a")
    except:
        util.err("Could not create or open log file")
        return
    l.close()
    LOGEN = 1
    return
    
def disablelog():
    global LOGEN
    LOGEN = 0
    return
def log(message):
    "write data to log"
    d = datetime.now()
    l = open(PATH,'a')
    l.write(d.strftime("%H:%M:%S,")+message+","+"\n")
    l.close()
    
def set_path(root):
    "allows user to chose log path"
    global PATH
    oldPATH=PATH
    PATH = tkFileDialog.asksaveasfilename(master=root,defaultextension=".csv",initialfile=PATH)
    if not PATH:
        PATH = oldPATH
    print PATH
    return PATH