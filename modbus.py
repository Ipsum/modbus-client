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

DEVICE_ID = 1
OFFSET = 40001
fc = dict()
reg = dict()

def setup(s,data):
    """Set commisioning registers"""
    writeReg(s,int(fc['set']),int(reg['set baudrate']),data['baudrate'])
    print "fc:"+str(fc['set'])+"reg:"+str(reg['set slave id'])+"data:"+str(data['slave id'])
    writeReg(s,fc['set'],reg['set slave id'],data['slave id'])
    writeReg(s,fc['set'],reg['set parity'],data['parity'])
    #writeReg(s,fc['set'],reg['set stop bits'],data['stop bits'])
    
    return True

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

    ser.flushInput()
    ser.flushOutput()
    ser.sendBreak(util.rtu_delay(s['baud']))
    
    return ser
    
def writeSerial(ser,data):
    """Write data to serial connection"""

    try:
        if not ser.writable():
            util.err('SERIAL PORT NOT OPEN')
            return False

        ser.sendBreak(util.rtu_delay(ser.baudrate))
        v = ser.write(data)
        print data.encode('hex_codec')
        if not v==8:
            util.err('WRITE ERROR')
            return False    
    except:
        util.err('ERROR WRITING DATA')
        return False
    return True     

def writeReg(ser,m_fc,m_reg,m_data):
    """Write a single comissioning setting"""
    m_reg -= OFFSET #MODBUS registers are offset
    packet = struct.pack('>BBHH',DEVICE_ID,m_fc,m_reg,m_data)
    packet += struct.pack('>H',util.calc_crc(packet))
    sucess = writeSerial(ser,packet)
    if not sucess:
        return False
    ser.timeout = 1
    try:
        response = ser.read(size=8)
        print "response: " + response.encode('hex_codec')
        ser.flushInput()
    except serial.SerialException,serial.SerialTimeoutException:
        util.err('ERROR READING RESPONSE')
        return False   
    if packet == response:
        time.sleep(1)
        return True
    else:
        util.err('CRC MISMATCH')
        return False
    
def readReg(ser,address,sreg,numreg):
    fc = 3
    sreg -= OFFSET
    packet = struct.pack('>BBHH',address,fc,sreg,numreg)
    packet += struct.pact('>H',util.calc_crc(packet))
    print packet.encode('hex_codec')
    return writeSerial(ser,packet)

if __name__=="__main__":
    writeReg(s,1,6,250,9600)
