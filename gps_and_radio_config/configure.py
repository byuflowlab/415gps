# include files
import ubxconfig
import atcommander
import sys
import time

def configure(port, gpsbaudrate=115200, radiobaudrate=57600, newbaudrate=57600, retries = 3):

    # Binary GPS Config Messages

    if newbaudrate == 57600:
        UBX_CFG_PRT='06 00 14 00 01 00 00 00 d0 08 00 00 00 e1 00 00 07 00 03 00 00 00 00 00'
    elif newbaudrate == 115200:
        UBX_CFG_PRT='06 00 14 00 01 00 00 00 d0 08 00 00 00 c2 01 00 07 00 03 00 00 00 00 00'
    else:
        raise ValueError('Baud rate message not defined')
    UBX_CFG_RATE='06 08 06 00 c8 00 01 00 01 00'
    UBX_CFG_NAV5='06 24 24 00 ff ff 08 03 00 00 00 00 10 27 00 00 05 00 fa 00 fa 00 64 00 5e 01 00 3c 00 00 00 00 00 00 00 00 00 00 00 00'
    UBX_CFG_CFG_SAVE='06 09 0d 00 00 00 00 00 ff ff 00 00 00 00 00 00 03'

    # Test baudrate and fix if necessary
    print 'Checking Baud Rate Settings...'
    for i in range(retries):
        ubx = ubxconfig.UBXConfig(port, baudrate=newbaudrate)
        fail = ubx.send_ubx(UBX_CFG_PRT)
        if not fail:
            break

    if fail:
        print 'Fixing baudrate'
        print '\tGetting baudrate of radio...'
        for baudrate in [9600, 57600, 115200]:
            at = atcommander.ATCommandSet(port, baudrate=baudrate)
            # at.leave_command_mode_force()
            at.enter_command_mode()
            correctbaudrate = at.get_radio_version()
            at.leave_command_mode()
            if correctbaudrate:
                radiobaudrate = int(baudrate)
                print '\tRadio baudrate is %f' % radiobaudrate
                break

        if radiobaudrate != gpsbaudrate:
            print '\tChanging radio baudrate to GPS baudrate'
            newradiobaudrate(port, radiobaudrate, gpsbaudrate)
            time.sleep(1.0)

        print '\tChanging GPS baud rate to new baudrate'
        ubx = ubxconfig.UBXConfig(port, baudrate=gpsbaudrate)
        for i in range(5):
            ubx.send_ubx(UBX_CFG_PRT, response=False)

        print '\tChanging radio baudrate to new GPS baudrate'
        remote_fail = newradiobaudrate(port, gpsbaudrate, newbaudrate)
        time.sleep(1.0)

        print '\tTesting GPS baud rate change'
        ubx = ubxconfig.UBXConfig(port, baudrate=newbaudrate)
        for i in range(5):
            fail = ubx.send_ubx(UBX_CFG_PRT)
            if fail:
                '\tBaudrate change failed'
            else:
                break

    # Test update rate and fix if necessary
    print 'Configuring GPS update rate...'
    for i in range(retries):
        fail1 = ubx.send_ubx(UBX_CFG_RATE)
        if not fail1:
            break

    # Test navigation mode and fix if necessary
    print 'Configuring GPS navigation mode...'
    for i in range(retries):
        fail2 = ubx.send_ubx(UBX_CFG_NAV5)
        if not fail2:
            break

    # Save settings to GPS
    print 'Saving GPS settings...'
    for i in range(retries):
        fail3 = ubx.send_ubx(UBX_CFG_CFG_SAVE)
        if not fail3:
            break

    fail = False
    if fail1 or fail2 or fail3:
        fail = True
        print 'Configuration Failed. Check to make sure the system is powered ' \
            'and the right port is specified'
    else:
        print "You're all set! GPS and radios are properly configured!"
    return fail


# function for changing radio baudrate
def newradiobaudrate(port, oldbaudrate, newbaudrate, retries = 3):
    at = atcommander.ATCommandSet(port, baudrate=oldbaudrate)
    # no failures yet
    local_fail = False
    remote_fail = False
    # we'll be setting the serial speed
    remote_set = {'SERIAL_SPEED': int(newbaudrate/1000)}
    local_set = {'SERIAL_SPEED': int(newbaudrate/1000)}
    # enter command mode
    # change radio baudrate, starting with remote radio
    for remote, radiofail in zip([True, False],[local_fail, remote_fail]):
        radio = "remote" if remote else "local"
        at.set_remote_mode(remote)
        for retry in range(retries):
            radiofail = False
            # try entering command mode
            at.enter_command_mode()
            # try changing remote baudrate
            if at.set_param('S1', int(newbaudrate/1000)):
                print "\t\tSet %s radio baudrate to %d" % (radio, newbaudrate)
            else:
                print "\t\tFailed to set %s radio baudrate to %d" % (radio, newbaudrate)
                radiofail = True
            if at.write_params():
                print "\t\tWrote parameters to EEPROM."
            else:
                radiofail = True
                print "\t\tFailed to write parameters to EEPROM."
            if at.reboot():
                print "\t\tCommanded reboot; changes should be in effect momentarily."
            else:
                radiofail = True
                print "\t\tFailed to command reboot."
            if radiofail and retry is not retries-1:
                "Baudrate configuration failed, trying again"
            else:
                break
    # leave command mode
    at.leave_command_mode()
    return local_fail, remote_fail

# parse arguments
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Please specify the port (e.g. python configure.py /dev/ttyUSB0)'
    else:
        serial_port = sys.argv[1]
        configure(serial_port)
