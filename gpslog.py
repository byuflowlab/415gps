#! /usr/bin/env python

# import modules
import serial
import sys
import time
import warnings
import math

# import GPS driver
import libnmea_navsat_driver.driver

# import GPS and SIK radio configuration routine
sys.path.insert(0, './gps-and-radio-config/')
import configure

# parse arguments
if len(sys.argv) < 2:
    print 'Please specify the port (e.g. python gpslog.py /dev/ttyUSB0)'
else:
    serial_port = sys.argv[1]

# set up port reading
GPS = serial.Serial(port=serial_port, baudrate=57600, timeout=2)
driver = libnmea_navsat_driver.driver.NMEADriver()

# set filename and open file
timestr = time.strftime("%Y%m%d-%H%M%S.csv")
f = open(timestr, "w")
f.write("time,fix,NumSat,latitude,longitude,altitude,speed,ground_course,covariance\n")
# set time to zero
t0 = time.time()

try:
    while True:
        data = GPS.readline().strip()
        try:
            out = driver.add_sentence(data, time.time()-t0)
            if out != False:
                print out
                if not (math.isnan(out[3]) or math.isnan(out[4]) or math.isnan(out[5])):
                    f.write(str(out[0])+","+str(out[1])+","+str(out[2])+","+ \
                        str(out[3])+","+str(out[4])+","+str(out[5])+","+ \
                        str(out[6])+","+str(out[7])+","+str(out[8])+"\n")
        except ValueError as e:
            warnings.warn("Value error, likely due to missing fields in the NMEA message. Error was: %s. Please report this issue at github.com/ros-drivers/nmea_navsat_driver, including a bag file with the NMEA sentences that caused it." % e)
except KeyboardInterrupt:
    GPS.close() #Close GPS serial port
    f.close()
