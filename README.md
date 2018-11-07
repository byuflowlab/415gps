# 415gps

The script gpslog.py reads serial GPS data (NMEA messages) and writes the data to a time-stamped csv file.

## Example Usage (from command line):
```
python gpslog.py /dev/ttyUSB0
```
You will need to replace '/dev/ttyUSB0' with the path to your port.

When called, the script gpslog.py will record data into a time-stamped csv file.  Data is output only if the gps has a satellite fix.  You can stop the script by typing CTRL+C.

An example csv output file can be found in the example_output directory.  The time entry in the CSV file corresponds to the time since the script was started.  I used http://www.hamstermap.com to plot the coordinates.

## Finding Your Serial Port
### Windows
* Open Device Manager, and expand the Ports (COM & LPT) list.
* Note the number on the USB Serial Port.
* Run script with 
  ```
  python gpslog.py COM*
  ```
  where * is the number of your serial port

### Macintosh
* Open a terminal and type: ls /dev/*.
* Note the port number listed for /dev/tty.usbmodem* or /dev/tty.usbserial*.
* Run the script with
  ```
  python gpslog.py /dev/tty.usbmodem*
  ```
  or 
  ```
  python gpslog.py /dev/tty.usbserial*
  ```
  where * is the number of your serial port

### Linux
* Open a terminal and type: ls /dev/tty*.
* Note the port number listed for /dev/ttyUSB* or /dev/ttyACM*.
* Run the script with
  ```
  python gpslog.py /dev/ttyUSB*
  ```
  where * is the number of your serial port

## Using GPS data in real time
Inside the gpslog.py script the function `usrfun` can be modified to allow real time data processing.
