#! /usr/bin/env python

# import modules
import serial
import sys
import time
import warnings
import math

# user defined function


def usrfun(time, fix, NumSat, lat, lon, alt, speed, ground_course, covariance):

    # modify the contents of this function to fit your needs

    if usrfun.counter%10 == 0:  # print the titles every 10 iterations
        print("time,fix,NumSat,lat,lon,alt,speed,ground_course,covariance")

    print(time,fix,NumSat,lat,lon,alt,speed,ground_course,covariance)

    usrfun.counter += 1

    return

# you can define variables outside of your function like this and use them inside
usrfun.counter = 0

# --- DO NOT MODIFY ANYTHING BELOW THIS LINE --- #

# import GPS driver
import libnmea_navsat_driver.driver

# parse arguments
if len(sys.argv) < 2:
    print('Please specify the port (e.g. python gpslog.py /dev/ttyUSB0)')
    sys.exit(0)
else:
    serial_port = sys.argv[1]

# set up port reading
GPS = serial.Serial(port=serial_port, baudrate=57600, timeout=2)
driver = libnmea_navsat_driver.driver.NMEADriver()

# set filename and open csv file
timestr = time.strftime("%Y%m%d-%H%M%S.csv")
csvfile = open(timestr, "w")
csvfile.write("time,fix,NumSat,latitude,longitude,altitude,speed,ground_course,covariance\n")

# set time to zero
t0 = time.time()

try:
    while True:
        data = GPS.readline().strip()
        try:
            out = driver.add_sentence(data.decode(), time.time()-t0)
            if out != False:
                usrfun(*out)
                if not (math.isnan(out[3]) or math.isnan(out[4]) or math.isnan(out[5])):
                    csvfile.write(str(out[0])+","+str(out[1])+","+str(out[2])+","+ \
                        str(out[3])+","+str(out[4])+","+str(out[5])+","+ \
                        str(out[6])+","+str(out[7])+","+str(out[8])+"\n")
        except ValueError as e:
            warnings.warn("Value error, likely due to missing fields in the NMEA message. Error was: %s. Please report this issue at github.com/ros-drivers/nmea_navsat_driver, including a bag csvfile with the NMEA sentences that caused it." % e)
except KeyboardInterrupt:
    GPS.close() #Close GPS serial port
    csvfile.close() # Close CSV file
