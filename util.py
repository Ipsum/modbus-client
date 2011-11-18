#*        File: util.py
#*              utilities for MODBUS communications
#*

import tkMessageBox
import datetime

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
    
def log(format,data):
    """Datalogging Functionality"""
    #logger = log("excel")
    date = datetime.timetuple()
    l = open(PATH, 'a')
    if format=="excel":
        header="Time,
        for d in data:
            datastr+=","+str(d)
    else:
        for d in data:
            datastr+=" "+str(d)
        
    l.write(date[3]+":"+date[4]+":"+date[5]+datastr+"\n")
    #TODO: FILEPATH = date+time.csv
    #TODO: formats: csv, txt
    #TODO: user picks file loc
    #f = open(FILEPATH, "w")
    