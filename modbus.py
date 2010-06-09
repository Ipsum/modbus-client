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

OFFSET=1

def writeSerial(s,data):
    ser = serial.Serial()
    ser.port = s['port']
    ser.baudrate = s['baud']
    ser.parity = s['parity']
    ser.stopbits = s['stopbits']
    try:
        ser.open()
    except serial.SerialException,serial.ValueError:
        print 'ERROR OPENING PORT'
        return False

    if not ser.isOpen():
        print 'SERIAL PORT NOT OPEN'
        return False

    ser.flushInput()
    ser.flushOutput()
    ser.sendBreak(util.rtu_delay(s[1]))
    v = ser.write(data)
    if not v==len(data):
        print 'WRITE ERROR'
        return False
    ser.sendBreak(util.rtu_delay(s[1]))
    return True
    
def writeReg(s,address,fc,reg,data):
    reg -= OFFSET #MODBUS registers are offset
    packet = struct.pack('>BBHH',address,fc,reg,data)
    packet += struct.pack('>H',util.calc_crc(packet))

    print packet.encode('hex_codec')
    return writeSerial(s,packet)

if __name__=="__main__":
    s=dict(port=0, baud=9600, parity='N', stopbits=2)
    writeReg(s,1,6,250,9600)
    
