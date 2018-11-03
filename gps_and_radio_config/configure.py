# include files
import ubxconfig
import atcommander
import sys
import time

def configure(port, gpsbaudrate=9600, retries = 3):

    # Binary GPS Config Messages
    UBX_CFG_PRT='06 00 14 00 01 00 00 00 d0 08 00 00 00 e1 00 00 07 00 03 00 00 00 00 00'
    # UBX_CFG_PRT='06 00 14 00 01 00 00 00 d0 08 00 00 00 c2 01 00 07 00 03 00 00 00 00 00'
    UBX_CFG_RATE='06 08 06 00 c8 00 01 00 01 00'
    UBX_CFG_NAV5='06 24 24 00 ff ff 08 03 00 00 00 00 10 27 00 00 05 00 fa 00 fa 00 64 00 5e 01 00 3c 00 00 00 00 00 00 00 00 00 00 00 00'
    UBX_CFG_CFG_SAVE='06 09 0d 00 00 00 00 00 ff ff 00 00 00 00 00 00 03'

    # Test baudrate and fix if necessary
    print 'Checking Baud Rate Settings...'
    for i in range(retries):
        ubx = ubxconfig.UBXConfig(port, baudrate=57600)
        fail = ubx.send_ubx(UBX_CFG_PRT)
        if not fail:
            break

    if fail:
        print 'Fixing baudrate'
        print '\tGetting baudrate of radio...'
        radiobaudrate = 57600
        for baudrate in [115200, 57600, 9600]:
            at = atcommander.ATCommandSet(port, baudrate=baudrate)
            at.leave_command_mode_force()
            correctbaudrate = at.enter_command_mode()
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
        remote_failed = newradiobaudrate(port, gpsbaudrate, 57600)
        time.sleep(1.0)

        print '\tTesting GPS baud rate change'
        ubx = ubxconfig.UBXConfig(port, baudrate=57600)
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

    def _set_params(myset):
        fail = False
        for prm in myset:
            if at.set_param(atcommander.param_map[prm], myset[prm]):
                print "\t\tSet %s to %d" % (prm, myset[prm])
            else:
                fail = True
                return fail
        if at.write_params():
            print "\t\tWrote parameters to EEPROM."
        else:
            fail = True
            return fail
        if at.reboot():
            print "\t\tCommanded reboot; changes should be in effect momentarily."
        else:
            print "\t\tFailed to command reboot; please manually reboot the radio."
        return fail

    at.leave_command_mode_force()
    if not at.enter_command_mode():
        print "\t\tCould not enter command mode"
    remote_set = {'SERIAL_SPEED': int(newbaudrate/1000)}
    local_set = {'SERIAL_SPEED': int(newbaudrate/1000)}
    local_failed = False
    remote_failed = False
    at.set_remote_mode(True)
    if not at.get_radio_version:
        print "\tCould not contact remote radio, aborting without saving changes."
        remote_failed = True
    else:
        print "\tChanging settings on remote radio..."
        for i in range(retries):
            remote_failed = _set_params(remote_set)
            if not remote_failed:
                break
    at.set_remote_mode(False)
    if not remote_failed:
        print "\tChanging settings on local radio..."
        for i in range(retries):
            local_failed = _set_params(local_set)
            if not local_failed:
                break
    at.leave_command_mode()
    return remote_failed

# parse arguments
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Please specify the port (e.g. python configure.py /dev/ttyUSB0)'
    else:
        serial_port = sys.argv[1]
        configure(serial_port)
