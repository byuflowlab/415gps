# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Eric Perko
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the names of the authors nor the names of their
#    affiliated organizations may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import math
import warnings
import logging
logger = logging.getLogger('out')

from libnmea_navsat_driver.checksum_utils import check_nmea_checksum
import libnmea_navsat_driver.parser

class NMEADriver(object):
    def __init__(self):
        self.use_RMC = False
        self.speed = 0.0
        self.ground_course = 0.0

    # Returns True if we successfully did something with the passed in
    # nmea_string
    def add_sentence(self, nmea_string, timestamp):

        time = 0.0
        fix = False
        NumSat = 0
        latitude = 0.0
        longitude = 0.0
        altitude = 0.0
        speed = 0.0
        ground_course = 0.0
        covariance = 0.0

        if not check_nmea_checksum(nmea_string):
            logger.debug("Received a sentence with an invalid checksum. " +
                          "Sentence was: %s" % repr(nmea_string))
            return False

        parsed_sentence = libnmea_navsat_driver.parser.parse_nmea_sentence(nmea_string)
        if not parsed_sentence:
            logger.debug("Failed to parse NMEA sentence. Sentece was: %s" % nmea_string)
            return False

        if 'RMC' in parsed_sentence:
            data = parsed_sentence['RMC']
            if data['fix_valid']:
                self.speed = data['speed']
                if not math.isnan(data['true_course']):
                    self.ground_course = data['true_course']

        if not self.use_RMC and 'GGA' in parsed_sentence:
            data = parsed_sentence['GGA']
            gps_qual = data['fix_type']
            if gps_qual > 0:
                fix = True
                NumSat = data['num_satellites']

            time = timestamp

            latitude = data['latitude']
            if data['latitude_direction'] == 'S':
                latitude = -latitude
            latitude = latitude

            longitude = data['longitude']
            if data['longitude_direction'] == 'W':
                longitude = -longitude
            longitude = longitude

            hdop = data['hdop']
            covariance = hdop ** 2
            # position_covariance[4] = hdop ** 2
            # position_covariance[8] = (2 * hdop) ** 2  # FIXME
            # position_covariance_type = \

            # Altitude is above ellipsoid, so adjust for mean-sea-level
            altitude = data['altitude'] + data['mean_sea_level']
            altitude = altitude

            speed = self.speed
            ground_course = self.ground_course

            return (time, fix, NumSat, latitude, longitude,
                altitude, speed, ground_course, covariance)

        elif 'RMC' in parsed_sentence:
            data = parsed_sentence['RMC']

            # Only publish a fix from RMC if the use_RMC flag is set.
            if self.use_RMC:
                time = timestamp
                fix = True
                NumSat = data['num_satellites']


                latitude = data['latitude']
                if data['latitude_direction'] == 'S':
                    latitude = -latitude
                latitude = latitude

                longitude = data['longitude']
                if data['longitude_direction'] == 'W':
                    longitude = -longitude
                longitude = longitude

                altitude = float('NaN')

                # position_covariance_type = \
                if data['fix_valid']:
                    speed = data['speed']
                    if not math.isnan(data['true_course']):
                        ground_course = data['true_course']
                    else:
                        ground_course = self.ground_course

                return (time, fix, NumSat, latitude, longitude,
                    altitude, speed, ground_course, covariance)
            return False

        else:
            return False
