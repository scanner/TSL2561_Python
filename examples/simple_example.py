#!/usr/bin/env python
#
# File: $Id$
#
"""
Simple example to test the code for the TSL2561 luminosity sensor
on a raspberry pi or beaglebone black
"""

# system imports
#
from datetime import datetime
import time

# 3rd party imports
#
from TSL2561.TSL2561 import TSL2561


#############################################################################
#
def main():
    tsl = TSL2561(gain=TSL2561.GAIN_16X)
    print "TSL id: {}, {}".format(*tsl.get_id())

    while True:
        print "{}".format(datetime.now())
        broadband, ir = tsl.get_raw_data()
        print "Raw values - broadband: {}, IR: {}".format(broadband, ir)
        broadband, ir = tsl.get_luminosity()
        print "Luminosity (auto-gain): broadband: {}, IR: {}".format(broadband,
                                                                     ir)
        print "Lux: {}".format(tsl.get_lux())
        print ""
        time.sleep(5)

############################################################################
############################################################################
#
# Here is where it all starts
#
if __name__ == '__main__':
    main()
#
############################################################################
############################################################################
