#! /usr/bin/env python

# import modules
import serial
import sys
import time
import warnings
from math import pi, isnan
import numpy as np
import libnmea_navsat_driver.driver


class gpslogger:
    
    def __init__(self):
 
        self.initializevariables()
        self.startgpslog()


# -------- Don't change anything above this line -----------

    def initializevariables(self):
        """
        FOR YOU: Define any constants or class variables you want in your function.
        This function is only called once at initialization.
        """

        # a counter
        self.counter = 0

        # define boundary ellipse
        self.bdy_center = [40.2672305, -111.635524]
        self.bdy_R = [98.353826748828595, 127.49653449395105]
        self.bdy_theta = -15*pi/180.0

        # define waypoint
        self.wp_start = [40.267641059243935, -111.63587333726502]
        self.wp_finish = [40.26678857, -111.63552403]
        self.wp_tolerance = 10.0  # m


    def usrfun(self, time, fix, NumSat, lat, lon, alt, speed, ground_course, covariance):
        """
        FOR YOU: Define any logic you need for processing GPS data here.
        This function is called every time a new GPS packet is received.
        """

        # ---- print GPS state -----
        if self.counter%10 == 0:  # reprint the titles every 10 iterations
            print("time,fix,NumSat,lat,lon,alt,speed,ground_course,covariance")

        print(time,fix,NumSat,lat,lon,alt,speed,ground_course,covariance)


        # ---- boundary checks ----

        ell = self.ellipse([lat, lon])
        if ell > 1.0:
            print "ALERT!  Out of bounds! Return immediately!"
            return
        elif ell > 0.7:
            print "WARNING!  Close to boundary! Ready pilot."
            return

        # --- update counter ---
        self.counter += 1


 # -------- Don't change anything below this line -----------       

    def distance(self, pt1, pt2):
        """pt = [lat, long]"""
        EARTH_RADIUS = 6371000.0
        distN = EARTH_RADIUS*(pt2[0] - pt1[0])*pi/180.0
        distE = EARTH_RADIUS*np.cos(pt1[0]*pi/180.0)*(pt2[1] - pt1[1])*pi/180.0
        return distE, distN, np.linalg.norm([distN, distE])


    def ellipse(self, pt):
        """check if point is outside of boundary ellipse (ell > 1)"""

        center = self.bdy_center
        R = self.bdy_R
        theta = self.bdy_theta

        dx, dy, _ = self.distance(center, pt)
        ct = np.cos(theta)
        st = np.sin(theta)
        ell = ((dx*ct + dy*st)/R[0])**2 + ((dx*st - dy*ct)/R[1])**2

        return ell


    def startgpslog(self):

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
                        self.usrfun(*out)
                        if not (isnan(out[3]) or isnan(out[4]) or isnan(out[5])):
                            csvfile.write(str(out[0])+","+str(out[1])+","+str(out[2])+","+ \
                                str(out[3])+","+str(out[4])+","+str(out[5])+","+ \
                                str(out[6])+","+str(out[7])+","+str(out[8])+"\n")
                except ValueError as e:
                    warnings.warn("Value error, likely due to missing fields in the NMEA message. Error was: %s. Please report this issue at github.com/ros-drivers/nmea_navsat_driver, including a bag csvfile with the NMEA sentences that caused it." % e)
        except KeyboardInterrupt:
            GPS.close() #Close GPS serial port
            csvfile.close() # Close CSV file


if __name__ == '__main__':
    gpslogger()