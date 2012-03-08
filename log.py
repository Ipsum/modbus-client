import sys
from datetime import datetime
import tkFileDialog

PATH = "C:\\"
FULLPATH = ""
LOGEN = 0
TYPE = 'csv'

def enablelog():
    "Redirects stdout to a logfile"
    global LOGEN
    global FULLPATH
    d = datetime.now()
    filename = d.strftime("%m-%d-%y_%H%M%S")
    filepath = PATH+filename+".csv"
    try:
        l = open(filepath,"w")
        FULLPATH = filepath
    except:
        util.err("Could not create log file")
        return
    LOGEN = 1

    if TYPE == 'csv':
        header="Time,Volume Rate,Energy Rate,Mass Rate,Volume Total," \
            "Heating Total,Cooling Total,Mass Total,Local Temp,Remote Temp,"
        l.write(header)
    l.close()
    return
    
def disablelog():
    global LOGEN
    LOGEN = 0
    return
def log(message):
    "write data to log"
    d = datetime.now()
    l = open(FULLPATH,'a')
    l.write(d.strftime("%H:%M:%S,")+message+",")
    l.close()
    
def set_path(root):
    "allows user to chose log path"
    global PATH
    PATH = tkFileDialog.askdirectory(parent=root,initialdir=PATH) 