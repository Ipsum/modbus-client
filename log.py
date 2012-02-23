import sys
from datetime import datetime
import tkFileDialog

PATH = "C:\\"
LOGEN = 0
TYPE = 'csv'

def enablelog():
    "Redirects stdout to a logfile"
    global LOGEN
    d = datetime.now()
    filename = d.strftime("%m-%d-%y_%H%M%S")
    filepath = PATH+filename+".csv"
    try:
        sys.stderr = open(filepath,"w")
    except:
        util.err("Could not create log file")
        return
    LOGEN = 1

    if TYPE == 'csv':
        header="Time,Volume Rate,Energy Rate,Mass Rate,Volume Total," \
            "Heating Total,Cooling Total,Mass Total,Local Temp,Remote Temp,"
        print >> sys.stderr, header
    return
    
def log(message):
    "write data to log"
    d = datetime.now()
    print >> sys.stderr, d.strftime("%H:%M:%S,")+message+","
    
def set_path():
    "allows user to chose log path"
    PATH = tkFileDialog.askdirectory(parent=root,initialdir=PATH) 