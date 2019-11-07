# 415gps

This script is written for students in ME 415.  The script gpslog.py reads serial GPS data (NMEA messages) and writes the data to a time-stamped csv file.

## Before Class Setup

1. Install Python v3.  I recommend installing via Anaconda: <https://www.anaconda.com/distribution/>

2. Install the `pyserial` package.  From the command line ("Terminal" on mac/linux, "Anaconda Prompt" on windows), type `conda install pyserial`.  If you'd prefer a GUI you can do this in Anaconda Navigator, which was installed in the prior step.  See [here](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-packages/)

3. Download this package.  See the big green button above.

## Running the Script

1. Plug one of the radio transmitters into your computer via the USB port.  You should see a faint green light flashing showing you that it is powered on.  You now need to figure out what port the transmitter is connected to. Instructions for different operating systems are shown below.

**Windows**
* Open Device Manager, and expand the Ports (COM & LPT) list.
* Note the number on the USB Serial Port.
* Run script with (note this for step 4)
  ```
  python gpslog.py COM*
  ```
  where * is the number of your serial port

**Macintosh**
* Open a terminal and type: ls /dev/*.
* Note the port number listed for /dev/tty.usbmodem* or /dev/tty.usbserial*.
* Run the script with (note this for step 4)
  ```
  python gpslog.py /dev/tty.usbmodem*
  ```
  or 
  ```
  python gpslog.py /dev/tty.usbserial*
  ```
  where * is the number of your serial port

**Linux**
* Open a terminal and type: ls /dev/tty*.
* Note the port number listed for /dev/ttyUSB* or /dev/ttyACM*.
* Run the script with (note this for step 4)
  ```
  python gpslog.py /dev/ttyUSB*
  ```
  where * is the number of your serial port

2. Open up a command prompt ("Terminal" in Mac/Linux or "Anaconda Prompt" in Windows).  Navigate to the previously downloaded 415gps folder (using the command `cd`).

3. Connect your battery, via the ESC, to the GPS and to one of the radio transmitter.  For the three wires, make sure you match positive and negative (black to brown).  Be careful about how long you leave your battery attached to your ESC.  While the electronics power draw isn't large compared to the amount your motor will be using, over the course of an hour (if you leave it plugged in) you could end up draining the battery below acceptable levels, especially if you started with your battery being at storage voltage.  If you're expecting to have your electronics powered on for a while, it's a good idea to charge your battery some first.  Just remember to restore it to storage voltage if you won't be using it for a couple days so you don't degrade your battery's performance.

4. Run the script using the commands shown above.

5. You should see a bunch of timestamped data shown to screen.  If you are doing this in the classroom you will see a bunch of NaNs.  That is because you don't have a GPS fix.  Getting a GPS fix generally requires being outside.  The first time you are getting a fix may take up to a minute of the GPS being powered.  In our experience the GPS and radio need to be at least 4 inches apart to get a fix due to signal interference, even outdoors.

6. End the script by typing CTRL+c

## Using the Script

The script gpslog.py will record data into a time-stamped csv file.  Data is output only if the gps has a satellite fix.  An example csv output file can be found in the example_output directory.  The time entry in the CSV file corresponds to the time since the script was started.  I used http://www.hamstermap.com to plot the coordinates.

Inside the gpslog.py script you will need to modify `usrfun` to allow real time data processing.
