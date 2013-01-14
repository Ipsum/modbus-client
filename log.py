import sys
import os
import util
from datetime import datetime
import tkFileDialog

PATH = "C:\\clarklog.csv"
LOGEN = 0
REEN = 0
TYPE = 'csv'

def enablelog():
    "Redirects stdout to a logfile"
    global LOGEN
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
        util.err("Could not create or open log file",1)
        return 1
    l.close()
    LOGEN = 1
    return
    
def disablelog():
    """called to disable logging"""
    global LOGEN
    LOGEN = 0
    return
    
def log(message):
    "write data to log"
    d = datetime.now()
    try:
        l = open(PATH,'a')
        l.write(d.strftime("%H:%M:%S,")+message+","+"\n")
        l.close()
        return True
    except:
        util.err("Log file unwritable - check that it is not opened by another program",1)
        return False
    
def set_path(root):
    "allows user to chose log path"
    global PATH
    oldPATH=PATH
    options = {}
    options['filetypes'] = [('comma seperated values', '.csv')]
    options['defaultextension'] = '.csv'
    options['initialfile'] = PATH
    options['master'] = root
    PATH = tkFileDialog.asksaveasfilename(**options)
    if not PATH:
        PATH = oldPATH
    print PATH
    return PATH