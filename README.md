# 415gps

libnmea_navsat_driver contains the driver for reading NMEA strings

gps_and_radio_config contains routines for reconfiguring the radios and gps's.  They should only need to be configured once, but I need to test this, our last gps's wouldn't save their parameters.  I have a script that is moderately robust for doing this automatically, that we can use if necessary.

When called, the script gpslog.py will record data into a time-stamped csv file.  Data is output only if the gps has a satellite fix.  The script takes the port name as a command line argument.  Students will need to make sure that they can read serial data through their usb port.  Currently, I also print to the terminal the GPS output regardless of whether or not there is a GPS fix.

Example Usage (from command line):
```
python gpslog.py /dev/ttyUSB0
```

An example csv output file can be found in the example_output directory.  The time entry in the CSV file corresponds to the time since the script was started.

I still need to grab the licenses for the driver files and the atcommander files and put them in here.
