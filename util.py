#*        File: util.py
#*              utilities for MODBUS communications
#*

import tkMessageBox
from datetime import datetime

DEVICE_ID = 12

def rtu_delay(baudrate):
    """calculates the interchar delay from the baudrate"""
    if baudrate <= 19200:
        return 11.0 / baudrate
    else:
        return 0.0005

def swap_bytes(word_val):
    """swap lsb and msb of a word"""
    msb = word_val >> 8
    lsb = word_val % 256
    return (lsb << 8) + msb

def calc_crc(data):
    """Calculate the CRC16 of a datagram"""
    crc = 0xFFFF
    for i in data:
        crc = crc ^ ord(i)        
        for j in xrange(8):
            tmp = crc & 1
            crc = crc >> 1
            if tmp:
                crc = crc ^ 0xA001
    return swap_bytes(crc)
    
def err(code):
    """Function for catching errors"""
    #TODO: Make a popup
    #for now, just print error to std out
    print 'ERROR---> '+str(code)
    tkMessageBox.showerror(message=code,icon='error',title='ERROR')
    
def logcreate(path):
     l = open(path,'w')
     header="Time,Volume Rate,Energy Rate,Mass Rate,Local Temp,Remote Temp,Volume Total,Mass Total,Heating Total,Cooling Total,Energy Total\n"
     l.write(header)
     l.close()
     
def log(path,data):
    """Datalogging Functionality"""
    #logger = log("excel")
    d = datetime.now()
    t = d.strftime("%H:%M:%S")
    datastr=""
    try:
        l = open(path, 'a')
    except:
        err("Could not open log file")
    for d in data:
        datastr+=","+str(d)
        
    l.write(t+datastr+"\n")
    l.close()
    #TODO: FILEPATH = date+time.csv
    #TODO: formats: csv, txt
    #TODO: user picks file loc
    #f = open(FILEPATH, "w")
    