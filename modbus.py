#modbus.py
'''
    Modbus RTU Frame controller::

        [ Start Wait ] [Address ][ Function Code] [ Data ][ CRC/LRC ][  End Wait  ]
          3.5 chars     1b         1b               Nb      2b         3.5 chars
        
    Wait refers to the amount of time required to transmist at least x many
    characters.  In this case it is 3.5 characters.  Also, if we recieve a
    wait of 1.5 characters at any point, we must trigger an error message.
    Also, it appears as though this message is little endian. The logic is
    simplified as the following::
        
        block-on-read:
            read until 3.5 delay
            check for errors
            decode

    The following table is a listing of the baud wait times for the specified
    baud rates::
        
        --------------------------------------------------------------------------#
         Baud  1.5c (18 bits)   3.5c (38 bits)
        --------------------------------------------------------------------------#
         1200   13333.3 us       31666.7 us
         4800    3333.3 us        7916.7 us
         9600    1666.7 us        3958.3 us
        19200     833.3 us        1979.2 us
        38400     416.7 us         989.6 us
        --------------------------------------------------------------------------#
        1 Byte = start + 8 bits + parity + stop = 11 bits
        (1/Baud)(bits) = delay seconds
'''
import struct
import util
import serial
import ConfigParser
import time
from Tkinter import *
from ttk import *

DEVICE_ID = 1
OFFSET = 40001
fc = dict()
reg = dict()

def setup(win,s,data):
    """Set commisioning registers"""
    writeReg(s,fc['set'],int(reg['set baudrate']),data['baudrate'])
    print "fc:"+str(fc['set'])+"reg:"+str(reg['set slave id'])+"data:"+str(data['slave id'])
    writeReg(s,fc['set'],reg['set slave id'],data['slave id'])
    writeReg(s,fc['set'],reg['set parity'],data['parity'])
    #writeReg(s,fc['set'],reg['set stop bits'],data['stop bits'])
    
    writeReg(s,fc['set'],reg['set flow rate units'],data['flow rate units'])
    writeReg(s,fc['set'],reg['set energy rate units'],data['energy rate units'])
    writeReg(s,fc['set'],reg['set mass flow rate units'],data['mass flow rate units'])
    writeReg(s,fc['set'],reg['set flow total units'],data['flow total units'])
    writeReg(s,fc['set'],reg['set energy total units'],data['energy total units'])
    writeReg(s,fc['set'],reg['set mass total units'],data['mass total units'])
    writeReg(s,fc['set'],reg['select pulse output'],data['pulse output'])
    writeReg(s,fc['set'],reg['select temperature units'],data['temperature units'])
    writeReg(s,fc['set'],reg['select media type'],data['media type'])
    writeReg(s,fc['set'],reg['select per cent'],data['per cent'])
    
    return True
def getData(s):
    resp = readReg(s,fc['read'],reg['flow rate'],18)
    if not resp:
        return False
    else:
        return resp

def openConn(s):
    """open serial connection and return the connection object""" 
    #open serial conn
    ser = serial.Serial(port=None)
    ser.port = s['port']
    ser.baudrate = 9600
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_TWO
    print ser.getSettingsDict()
    try:
        ser.open()
    except Exception, e:
        print e
        util.err('Cannot open serial port')
        return False

    #ser.sendBreak(util.rtu_delay(s['baud']))
    
    return ser
    
def writeSerial(ser,data):
    """Write data to serial connection"""

    try:
        if not ser.writable():
            util.err('SERIAL PORT NOT OPEN')
            return False

        #ser.sendBreak(util.rtu_delay(ser.baudrate))
        v = ser.write(data)
        print data.encode('hex_codec')
        if not v==8:
        if not v==8:
            util.err('WRITE ERROR')
            return False    
    except:
        util.err('ERROR WRITING DATA')
        return False
    return True     

def writeReg(ser,m_fc,m_reg,m_data):
    """Write a single comissioning setting"""
    ser.flushInput()
    ser.flushOutput()
    m_reg -= OFFSET #MODBUS registers are offset
    packet = struct.pack('>BBHH',DEVICE_ID,m_fc,m_reg,m_data)
    packet += struct.pack('>H',util.calc_crc(packet))
    sucess = writeSerial(ser,packet)
    if not sucess:
        return False
    readResponse(ser,packet)
    time.sleep(1)
    
def readReg(ser,fc,sreg,numreg):
    sreg -= OFFSET
    packet = struct.pack('>BBHH',DEVICE_ID,fc,sreg,numreg)
    packet += struct.pack('>H',util.calc_crc(packet))
    sucess = writeSerial(ser,packet)
    if not sucess:
        return False
    data = readResponse(ser,regs=18)
    time.sleep(1)
    return data

def readResponse(ser,sent=0,regs=1):
    ser.timeout = 1
    dsize=regs*2+6
    if not sent:
        try:
            response = ser.read(size=dsize-1)
            print "Response: "+response.encode('hex_codec')
        ser.flushInput()
        except serial.SerialException,serial.SerialTimeoutException:
            util.err('ERROR READING RESPONSE')
            return False
        #check crc
        #TODO: check for error response
        if not len(response)==(dsize-1):
            print "wrong len: "+str(len(response))
            util.err('INVALID RESPONSE')
            return False
        baseresp = struct.unpack('>BBB'+str(regs/2)+'fH',response)
        return baseresp
        
    else:
        try:
            response = ser.read(size=dsize)
            print "response: " + response.encode('hex_codec')
        except serial.SerialException,serial.SerialTimeoutException:
            util.err('ERROR READING RESPONSE')
            return False   
        if sent == response:
            return True
        else:
            util.err('CRC MISMATCH')
            return False
            
if __name__=="__main__":
    writeReg(s,1,6,250,9600)
