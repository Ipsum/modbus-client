#*        File: util.py
#*              utilities for MODBUS communications
#*

import tkMessageBox
from datetime import datetime
root=0
trys=0
DEVICE_ID = 12
BAUDRATE = 9600
PARITY = 'N'
JMP = 1

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
    global root
    tkMessageBox.showerror(master=root,message=code,icon='error',title='ERROR')

def msg(code,ttl):
    """Function for displaying information popups"""
    global root
    tkMessageBox.showinfo(master=root,message=code,title=ttl)
    