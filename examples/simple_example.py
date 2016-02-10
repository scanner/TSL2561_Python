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
    tsl = TSL2561()

    while True:
        print "{}".format(datetime.now())
        print "TSL id: {}, {}".format(*tsl.get_id())
        print "Raw values - broadband: {}, IR: {}".format(*tsl.get_raw_data())
        print "Luminosity (auto-gain): broadband: {}, IR: {}".format(*tsl.get_luminosity())
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
