import serial, sys, argparse, time
from pexpect import fdpexpect

class UBXConfig(object):
    ''' Configures GPS to the UBX command set '''

    ### UBX Command Constants ###
    UBX_ACK_ACK='b5620501'
    UBX_ACK_NAK='b5620500'
    UBX_PREAMBLE='b5 62'

    def __init__(self, device, baudrate=9600, debug=False,
                 dsrdtr=False, rtscts=False, xonxoff=False):
        self.read_timeout = 5

        logfile=None
        if debug:
            logfile=sys.stdout

        # Initialize the serial connection
        self.device = device
        self.port = serial.Serial(device, baudrate=baudrate, timeout=0,
                                  dsrdtr=dsrdtr, rtscts=rtscts, xonxoff=xonxoff)
        self.ser = fdpexpect.fdspawn(self.port.fileno(), logfile=logfile)

    # Send text to GPS
    def __send(self, text):
        if (self.port is None) or (self.ser is None):
            return False

        try:
            res = self.ser.send(text)
            time.sleep(0.5)
            return res
        except:
            return False

    # Look for 'pattern' (string RE) and return MatchObject if seen before read_timeout
    def __expect(self, pattern_list):
        if (self.port is None) or (self.ser is None):
            return False

        try:
            self.ser.expect(pattern_list, timeout=self.read_timeout)
            res = self.ser.match
            time.sleep(0.5)  # Let the serial line catch up
            return res
        except:
            return False

    # Send command, then look for pattern
    def __query(self, command, pattern):
        if not self.__send(command):
            return False
        val = self.__expect(pattern)
        return val

     # sends message
    def send_ubx(self, arg, response=True):
        arg = self.ubx_chksum(arg)
        arg = arg.replace(" ","")
        arg = arg.decode("hex")
        self.__send(arg)
        if response:
            ubx_response = self.__expect([self.UBX_ACK_ACK.decode("hex"), self.UBX_ACK_NAK.decode("hex")])
            if ubx_response == False:
                fail = True
            else:
                ubx_response = int(ubx_response.group(0).encode('hex'), 16)
                if ubx_response == int(self.UBX_ACK_ACK, 16):
                    print "ACKNOWLEDGED"
                    fail = False
                elif ubx_response == int(self.UBX_ACK_NAK, 16):
                    print "REJECTED"
                    fail = True
                else:
                    print "FAILED"
                    fail = True
            return fail
        else:
            return None

    ###Fletcher checksum calculator adapted from: http://www.aeronetworks.ca/2014/07/fletcher-checksum-calculator-in-bash.html###
    def ubx_chksum(self, arg):
        sum=0
        fletcher=0
        j=0
        mystr = ''

        mystr += self.UBX_PREAMBLE + ' '

        for i in str.split(arg):
            j = int(i, 16)
            mystr += "%02x " %j
            sum += j
            sum %= 256

            fletcher += sum
            fletcher %= 256
        mystr += '%02x ' %sum
        mystr += '%02x' %fletcher
        return mystr
