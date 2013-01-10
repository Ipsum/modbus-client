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
import Comissioning

OFFSET = 40001
fc = dict()
reg = dict()

def setup(master,s,data):
    """Set commisioning registers"""
    try:
        if util.JMP:
            writeReg(s,fc['set'],int(reg['set baudrate']),data['baudrate'])
            master.update()
            writeReg(s,fc['set'],reg['set slave id'],data['slave id'])
            master.update()
            writeReg(s,fc['set'],reg['set parity'],data['parity'])
            master.update()
        util.JMP = 1
        writeReg(s,fc['set'],reg['set flow rate units'],data['flow rate units'])
        master.update()
        writeReg(s,fc['set'],reg['set energy rate units'],data['energy rate units'])
        master.update()
        writeReg(s,fc['set'],reg['set mass flow rate units'],data['mass flow rate units'])
        master.update()
        writeReg(s,fc['set'],reg['set flow total units'],data['flow total units'])
        master.update()
        writeReg(s,fc['set'],reg['set energy total units'],data['energy total units'])
        master.update()
        writeReg(s,fc['set'],reg['set mass total units'],data['mass total units'])
        master.update()
        writeReg(s,fc['set'],reg['select pulse output'],data['pulse output'])
        master.update()
        writeReg(s,fc['set'],reg['select temperature units'],data['temperature units'])
        master.update()
        writeReg(s,fc['set'],reg['select media type'],data['media type'])
        master.update()
        writeReg(s,fc['set'],reg['select per cent'],data['per cent'])
        master.update()
        return True
    except:
        return False
        
def getUnits(s):
    """Retrieve Units"""
    resp = readReg(s,fc['read'],reg['pulse flow units'],5,h=1)
    if not resp:
        return False
    else:
        return resp
    return
        
def getData(s):
    resp = readReg(s,fc['read'],reg['flow rate'],18)
    if not resp:
        return False
    else:
        return resp

def openConn(s):
    """open serial connection and return the connection object""" 
    #open serial conn with default params
    ser = serial.Serial(port=None)
    ser.stopbits = serial.STOPBITS_TWO #always 2 sb
    ser.port = s['port']
    if not util.JMP: #if no jumper, use user settings
        print 'modded br: '+str(util.BAUDRATE)+' par: '+util.PARITY
        ser.baudrate = util.BAUDRATE
        ser.parity = util.PARITY
        util.JMP = 1
    else:
        ser.baudrate = 9600
        ser.parity = serial.PARITY_NONE
    try:
        ser.open()
    except Exception, e:
        print e
        ser.close()
        util.err('The COM port could not be opened. Check that it is not already in use and the correct COM port is selected.')
        return False   
    return ser
    
def writeSerial(ser,data):
    """Write data to serial connection"""
    try:
        if not ser.writable(): #check port still available
            util.err('The serial port could not be written to. Check that it is not already in use.')
            return False
        v = ser.write(data) #simply write the data
        print data.encode('hex_codec')
        if not v==8: #check all bits written
            util.err('There was a problem writing to the serial port')
            return False    
    except: #something happened??
        util.err('A serial communications error has occurred')
        return False
    return True     

def writeReg(ser,m_fc,m_reg,m_data):
    """Write a single comissioning setting"""
    util.trys=0
    ser.flushInput()
    ser.flushOutput()
    m_reg -= OFFSET #MODBUS registers are offset
    print str(m_fc)+"::"+str(m_reg)+"::"+str(m_data)
    packet = struct.pack('>BBHH',util.DEVICE_ID,m_fc,m_reg,m_data) #build data packet
    packet += struct.pack('>H',util.calc_crc(packet)) #append crc
    sucess = writeSerial(ser,packet)
    if not sucess:
        print "write err"
        raise NameError('WriteErr')
        return False
    sucess = readResponse(ser,packet)
    if not sucess:
        print "Resp error"
        raise NameError('WriteErr')
        return False
    time.sleep(1)
    return True
    
def readReg(ser,fc,sreg,numreg,h=0):
    """Requests data from a register"""
    print ":::"+str(util.DEVICE_ID) + ":::"
    util.trys=0
    sreg -= OFFSET
    packet = struct.pack('>BBHH',util.DEVICE_ID,fc,sreg,numreg)
    packet += struct.pack('>H',util.calc_crc(packet))
    sucess = writeSerial(ser,packet)
    if not sucess:
        return False
    data = readResponse(ser,regs=numreg,hex=h)
    time.sleep(1)
    return data

def readResponse(ser,sent=0,regs=1,hex=0):
    """Read the response to a message"""
    ser.timeout = 2
    dsize=regs*2+6 #compute the expected message size
    if not sent: #If reading a reg
        try:
            response = ser.read(size=dsize-1)
            print "Response: "+response.encode('hex_codec')
        except serial.SerialException,serial.SerialTimeoutException:
            if util.trys>2:
                util.err('There was no response from the meter, please check all connections')
                return False
            else:
                readResponse(ser,sent,regs,hex)
        #check crc
        if not len(response)==(dsize-1):
            print "wrong len: "+str(len(response))
            if len(response)==0:
                if util.errlvl>=3:
                    util.errlvl+=1
                    util.err('There was no response from the meter. Please check that the meter is powered and the jumper is correctly set')
                    return False
                else:
                    util.errlvl+=1
                    print "errlvl+1"
                    return False
            util.err('The response from the meter was incorrect. Please check that the jumper correctly set.')
            return False
        util.errlvl=0
        print " hex: "+str(hex)+"\n"
        if hex: #return output in hex instead of array - retrieve units
            return response.encode('hex_codec')
        baseresp = struct.unpack('>BBB'+str(regs/2)+'fH',response)
        return baseresp #return an array of the response vars
        
    else: #setting a reg
        try:
            response = ser.read(size=dsize) #check size
            print "response: " + response.encode('hex_codec')
        except serial.SerialException,serial.SerialTimeoutException:
            util.err('There was no response from the meter, please check all connections')
            return False   
        if sent == response: #response should be echo of data written
            return True
        else:
            if util.trys<=2: #automatic retrying of failed writes
                util.trys+=1
                writeSerial(ser,sent)
                return readResponse(ser,sent)
            else: #after 3 failed, throw an error
                if len(response)==0:
                    util.err('There was no response from the meter. Please check that the meter is powered and the jumper is correctly set')
                    return False
                util.err('The response from the meter was incorrect. Please check that the jumper correctly set.')
                return False
            
if __name__=="__main__":
    writeReg(s,1,6,250,9600)
