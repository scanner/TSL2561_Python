#!/usr/bin/env python
#
# File: $Id$
#
"""
A module that uses the Adafruit GPIO library to read data from the
TSL2561 luminosity sensor over I2C on a Raspberry PI or Beagle Bone
Black.

Cribbed from the Arduino Adafruit TSL2561 code:
    https://github.com/adafruit/Adafruit_TSL2561
"""

# system imports
#
import time

# 3rd party imports
#
from Adafruit_GPIO import I2C


##################################################################
##################################################################
#
class TSL2561(object):
    """
    Read sensor values from the TLS2561 Luminosity sensor. Also
    supports different integration times, gain, and auto-scaling as
    well as conversion of data to lux values.

    Cribbed from the Arduino Adafruit TSL2561 code:

         https://github.com/adafruit/Adafruit_TSL2561

    Simple usage:

    >>> from TSL2561.TSL2561 import TSL2561
    >>> tsl = TSL2561()
    >>> broadband, ir = tsl.get_raw_data()
    >>> print "Raw values - broadband: {}, IR: {}".format(broadband, ir)
    >>> broadband, ir = tsl.get_luminosity()
    >>> print "Luminosity (auto-gain): broadband: {}, IR: {}".format(broadband, ir)
    >>> print "Lux: {}".format(tsl.get_lux())
    """
    VISIBLE = 2       # channel 0 - channel 1
    INFRARED = 1      # channel 1
    FULLSPECTRUM = 0  # channel 0

    # 3 i2c address options!
    #
    ADDR_LOW = 0x29
    ADDR_FLOAT = 0x39
    ADDR_HIGH = 0x49

    READBIT = 0x01

    COMMAND_BIT = 0x80  # Must be 1
    CLEAR_BIT = 0x40    # Clears any pending interrupt = write 1 to clear
    WORD_BIT = 0x20     # 1 = read/write word = rather than byte
    BLOCK_BIT = 0x10    # 1 = using block read/write

    CONTROL_POWERON = 0x03
    CONTROL_POWEROFF = 0x00

    LUX_LUXSCALE = 14           # Scale by 2^14
    LUX_RATIOSCALE = 9          # Scale ratio by 2^9
    LUX_CHSCALE = 10            # Scale channel values by 2^10
    LUX_CHSCALE_TINT0 = 0x7517  # 322/11 * 2^    LUX_CHSCALE
    LUX_CHSCALE_TINT1 = 0x0FE7  # 322/81 * 2^    LUX_CHSCALE

    # T, FN and CL package values
    #
    LUX_K1T = 0x0040  # 0.125 * 2^RATIO_SCALE
    LUX_B1T = 0x01f2  # 0.0304 * 2^LUX_SCALE
    LUX_M1T = 0x01be  # 0.0272 * 2^LUX_SCALE
    LUX_K2T = 0x0080  # 0.250 * 2^RATIO_SCALE
    LUX_B2T = 0x0214  # 0.0325 * 2^LUX_SCALE
    LUX_M2T = 0x02d1  # 0.0440 * 2^LUX_SCALE
    LUX_K3T = 0x00c0  # 0.375 * 2^RATIO_SCALE
    LUX_B3T = 0x023f  # 0.0351 * 2^LUX_SCALE
    LUX_M3T = 0x037b  # 0.0544 * 2^LUX_SCALE
    LUX_K4T = 0x0100  # 0.50 * 2^RATIO_SCALE
    LUX_B4T = 0x0270  # 0.0381 * 2^LUX_SCALE
    LUX_M4T = 0x03fe  # 0.0624 * 2^LUX_SCALE
    LUX_K5T = 0x0138  # 0.61 * 2^RATIO_SCALE
    LUX_B5T = 0x016f  # 0.0224 * 2^LUX_SCALE
    LUX_M5T = 0x01fc  # 0.0310 * 2^LUX_SCALE
    LUX_K6T = 0x019a  # 0.80 * 2^RATIO_SCALE
    LUX_B6T = 0x00d2  # 0.0128 * 2^LUX_SCALE
    LUX_M6T = 0x00fb  # 0.0153 * 2^LUX_SCALE
    LUX_K7T = 0x029a  # 1.3 * 2^RATIO_SCALE
    LUX_B7T = 0x0018  # 0.00146 * 2^LUX_SCALE
    LUX_M7T = 0x0012  # 0.00112 * 2^LUX_SCALE
    LUX_K8T = 0x029a  # 1.3 * 2^RATIO_SCALE
    LUX_B8T = 0x0000  # 0.000 * 2^LUX_SCALE
    LUX_M8T = 0x0000  # 0.000 * 2^LUX_SCALE

    # CS package values
    #
    LUX_K1C = 0x0043  # 0.130 * 2^RATIO_SCALE
    LUX_B1C = 0x0204  # 0.0315 * 2^LUX_SCALE
    LUX_M1C = 0x01ad  # 0.0262 * 2^LUX_SCALE
    LUX_K2C = 0x0085  # 0.260 * 2^RATIO_SCALE
    LUX_B2C = 0x0228  # 0.0337 * 2^LUX_SCALE
    LUX_M2C = 0x02c1  # 0.0430 * 2^LUX_SCALE
    LUX_K3C = 0x00c8  # 0.390 * 2^RATIO_SCALE
    LUX_B3C = 0x0253  # 0.0363 * 2^LUX_SCALE
    LUX_M3C = 0x0363  # 0.0529 * 2^LUX_SCALE
    LUX_K4C = 0x010a  # 0.520 * 2^RATIO_SCALE
    LUX_B4C = 0x0282  # 0.0392 * 2^LUX_SCALE
    LUX_M4C = 0x03df  # 0.0605 * 2^LUX_SCALE
    LUX_K5C = 0x014d  # 0.65 * 2^RATIO_SCALE
    LUX_B5C = 0x0177  # 0.0229 * 2^LUX_SCALE
    LUX_M5C = 0x01dd  # 0.0291 * 2^LUX_SCALE
    LUX_K6C = 0x019a  # 0.80 * 2^RATIO_SCALE
    LUX_B6C = 0x0101  # 0.0157 * 2^LUX_SCALE
    LUX_M6C = 0x0127  # 0.0180 * 2^LUX_SCALE
    LUX_K7C = 0x029a  # 1.3 * 2^RATIO_SCALE
    LUX_B7C = 0x0037  # 0.00338 * 2^LUX_SCALE
    LUX_M7C = 0x002b  # 0.00260 * 2^LUX_SCALE
    LUX_K8C = 0x029a  # 1.3 * 2^RATIO_SCALE
    LUX_B8C = 0x0000  # 0.000 * 2^LUX_SCALE
    LUX_M8C = 0x0000  # 0.000 * 2^LUX_SCALE

    # Auto-gain thresholds
    #
    AGC_THI_13MS = 4850    # Max value at Ti 13ms = 5047
    AGC_TLO_13MS = 100
    AGC_THI_101MS = 36000   # Max value at Ti 101ms = 37177
    AGC_TLO_101MS = 200
    AGC_THI_402MS = 63000   # Max value at Ti 402ms = 65535
    AGC_TLO_402MS = 500

    # Clipping thresholds
    #
    CLIPPING_13MS = 4900
    CLIPPING_101MS = 37000
    CLIPPING_402MS = 65000

    REG_CONTROL = 0x00
    REG_TIMING = 0x01
    REG_THRESHHOLDL_LOW = 0x02
    REG_THRESHHOLDL_HIGH = 0x03
    REG_THRESHHOLDH_LOW = 0x04
    REG_THRESHHOLDH_HIGH = 0x05
    REG_INTERRUPT = 0x06
    REG_CRC = 0x08
    REG_ID = 0x0A
    REG_CHAN0_LOW = 0x0C
    REG_CHAN0_HIGH = 0x0D
    REG_CHAN1_LOW = 0x0E
    REG_CHAN1_HIGH = 0x0F

    INTEG_TIME_13MS = 0x00     # 13.7ms
    INTEG_TIME_101MS = 0x01    # 101ms
    INTEG_TIME_402MS = 0x02    # 402ms

    VALID_INTEG_TIMES = (INTEG_TIME_13MS, INTEG_TIME_101MS, INTEG_TIME_402MS)

    GAIN_1X = 0x00     # No gain
    GAIN_16X = 0x10    # 16x gain

    VALID_GAINS = (GAIN_1X, GAIN_16X)

    # Lux calculations differ slightly depending on the package being used
    # in case you ever encounter the CS package type.
    #
    PACKAGE_T_FN_CL = 0
    PACKAGE_CS = 1

    ##################################################################
    #
    def __init__(self, integ_time=INTEG_TIME_101MS, gain=GAIN_1X,
                 address=ADDR_FLOAT, auto_gain=True, i2c_bus=None, **kwargs):
        """
        By default assumes the default I2C address.  If no I2C module is
        passed in it will use the default I2C bus on the host it is
        running on.
        """
        self.integ_time = integ_time
        self.gain = gain
        self.auto_gain = auto_gain
        self.package_type = self.PACKAGE_T_FN_CL

        if i2c_bus is None:
            i2c_bus = I2C
        self._device = i2c_bus.get_i2c_device(address, **kwargs)

        # Initialize and configure the sensor
        #
        reg_id = self._device.readU8(self.REG_ID)
        if 0x0a & reg_id == 0:
            raise RuntimeError("Unable to initialze. Register ID "
                               "returned: {}".format(reg_id))
        self.set_timing(self.integ_time)
        self.set_gain(self.gain)

    ####################################################################
    #
    def set_autogain(self, auto_gain):
        """
        If auto-gain is enabled we will automatically switch between 1x
        and 16x gain.

        Keyword Arguments:
        auto_gain --
        """
        self.auto_gain = auto_gain

    ##################################################################
    #
    def enable(self):
        """
        Turns on the luminosity sensor.
        """
        self._device.write8(self.COMMAND_BIT | self.REG_CONTROL,
                            self.CONTROL_POWERON)

    ##################################################################
    #
    def disable(self):
        """
        Turns off the luminosity sensor.
        """
        self._device.write8(self.COMMAND_BIT | self.REG_CONTROL,
                            self.CONTROL_POWEROFF)

    ##################################################################
    #
    def set_timing(self, integ_time=INTEG_TIME_101MS):
        """
        Update the integration value as supplied in the argument. If the
        'integration' argument is not supplied, use the already set value.

        Arguments:
        - `integration`:
        """
        if integ_time not in self.VALID_INTEG_TIMES:
            raise ValueError("{} not a valid integration time ({})".format(
                integ_time, self.VALID_INTEG_TIMES))
        self.enable()
        self._device.write8(self.COMMAND_BIT | self.REG_TIMING,
                            self.integ_time | self.gain)
        self.integ_time = integ_time
        self.disable()

    ##################################################################
    #
    def set_gain(self, gain=GAIN_1X):
        """
        Update the gain value as supplied in the argument. If the
        'gain' argument is not supplied, use the already set value.

        Arguments:
        - `gain`:
        """
        if gain not in self.VALID_GAINS:
            raise ValueError("{} is not a valid gain ({})".format(
                gain, self.VALID_GAINS))
        self.enable()

        self._device.write8(self.COMMAND_BIT | self.REG_TIMING,
                            self.integ_time | self.gain)
        self.disable()

    ##################################################################
    #
    def get_id(self):
        """
        Read the part number and silicon revision number for this device.
        It returns a tuple of (part number, revision number)
        """
        self.enable()
        id = self._device.readU8(self.COMMAND_BIT | self.REG_ID)
        self.disable()
        return ((id & 0xf0) >> 4, (id & 0x0f))

    ####################################################################
    #
    def get_lux(self):
        """
        Converts the raw sensor values to the standard SI lux equivalent.
        Returns 65536 if the sensor is saturated and the values are
        unreliable.
        """
        broadband, ir = self.get_luminosity()

        # Make sure the sensor isn't saturated!
        #
        if self.integ_time == self.INTEG_TIME_13MS:
            clip_threshold = self.CLIPPING_13MS
        elif self.integ_time == self.INTEG_TIME_101MS:
            clip_threshold = self.CLIPPING_101MS
        else:
            clip_threshold = self.CLIPPING_402MS

        # Return 65536 lux if the sensor is saturated
        #
        if broadband > clip_threshold or ir > clip_threshold:
            return 65536

        # Get the correct scale depending on the intergration time
        #
        if self.integ_time == self.INTEG_TIME_13MS:
            ch_scale = self.LUX_CHSCALE_TINT0
        elif self.integ_time == self.INTEG_TIME_101MS:
            ch_scale = self.LUX_CHSCALE_TINT1
        else:
            # No scaling ... integration time = 402ms
            #
            ch_scale = 1 << self.LUX_CHSCALE

        # Scale for gain (1x or 16x)
        #
        if self.gain == self.GAIN_16X:
            ch_scale = ch_scale << 4

        # Scale the channel values
        #
        channel0 = (broadband * ch_scale) >> self.LUX_CHSCALE
        channel1 = (ir * ch_scale) >> self.LUX_CHSCALE

        # Find the ratio of the channel values (Channel1/Channel0)
        #
        ratio1 = 0
        if channel0 != 0:
            ratio1 = (channel1 << (self.LUX_RATIOSCALE+1)) / channel0

        # round the ratio value
        #
        ratio = (ratio1 + 1) >> 1
        b = 0
        m = 0
        if self.package_type == self.PACKAGE_CS:
            if ratio >= 0 and ratio <= self.LUX_K1C:
                b = self.LUX_B1C
                m = self.LUX_M1C
            elif ratio <= self.LUX_K2C:
                b = self.LUX_B2C
                m = self.LUX_M2C
            elif ratio <= self.LUX_K3C:
                b = self.LUX_B3
                m = self.LUX_M3C
            elif ratio <= self.LUX_K4C:
                b = self.LUX_B4C
                m = self.LUX_M4C
            elif ratio <= self.LUX_K5C:
                b = self.LUX_B5C
                m = self.LUX_M5C
            elif ratio <= self.LUX_K6C:
                b = self.LUX_B6C
                m = self.LUX_M6C
            elif ratio <= self.LUX_K7C:
                b = self.LUX_B7C
                m = self.LUX_M7C
            elif ratio > self.LUX_K8C:
                b = self.LUX_B8C
                m = self.LUX_M8C
        else:
            if ratio >= 0 and ratio <= self.LUX_K1T:
                b = self.LUX_B1T
                m = self.LUX_M1T
            elif ratio <= self.LUX_K2T:
                b = self.LUX_B2T
                m = self.LUX_M2T
            elif ratio <= self.LUX_K3T:
                b = self.LUX_B3T
                m = self.LUX_M3T
            elif ratio <= self.LUX_K4T:
                b = self.LUX_B4T
                m = self.LUX_M4T
            elif ratio <= self.LUX_K5T:
                b = self.LUX_B5T
                m = self.LUX_M5T
            elif ratio <= self.LUX_K6T:
                b = self.LUX_B6T
                m = self.LUX_M6T
            elif ratio <= self.LUX_K7T:
                b = self.LUX_B7T
                m = self.LUX_M7T
            elif ratio > self.LUX_K8T:
                b = self.LUX_B8T
                m = self.LUX_M8T

        temp = (channel0 * b) - (channel1 * m)

        # Do not allow negative lux value
        #
        if temp < 0:
            temp = 0

        # Round lsb (2^(LUX_SCALE-1))
        #
        temp += 1 << (self.LUX_LUXSCALE-1)

        # Strip off fractional portion
        #
        return temp >> self.LUX_LUXSCALE

    ##################################################################
    #
    def get_luminosity(self):
        """
        Gets the broadband (mixed lighting) and IR only values from
        the TSL2561, adjusting gain if auto-gain is enabled.

        Returns a tuple of 'broadband, ir'.
        """
        # Enable the device by setting the control bit to 0x03
        #
        self.enable()

        # If autogain is disabled get a single sample at the currently
        # set gain and return.
        #
        if not self.auto_gain:
            return self.get_raw_data()

        # Read data until we find a valid range
        #
        auto_gain_check = False

        valid = False
        while True:
            it = self.integ_time

            # Get the hi/low threshold for the current integration time
            #
            if it == self.INTEG_TIME_13MS:
                hi = self.AGC_THI_13MS
                lo = self.AGC_TLO_13MS
            elif it == self.INTEG_TIME_101MS:
                hi = self.AGC_THI_101MS
                lo = self.AGC_TLO_101MS
            else:
                hi = self.AGC_THI_402MS
                lo = self.AGC_TLO_402MS

            broadband, ir = self.get_raw_data()
            # Run an auto-gain check if we haven't already done so ...
            #
            if auto_gain_check is False:
                if broadband < lo and self.gain == self.GAIN_1X:
                    # Increase the gain and try again
                    #
                    self.set_gain(self.GAIN_16X)
                    # Re-read the conversion results.
                    broadband, ir = self.get_raw_data()
                    # Set a flag to indicate we've adjusted the gain
                    #
                    auto_gain_check = True
                elif broadband > hi and self.gain == self.GAIN_16X:
                    # Drop gain to 1x and try again
                    #
                    self.set_gain(self.GAIN_1X)
                    # Re-read the conversion results
                    #
                    broadband, ir = self.get_raw_data()
                    # Set a flag to indicate we've adjusted the gain
                    #
                    auto_gain_check = True
                else:
                    # Nothing to look at here, keep moving ....  Reading
                    # is either valid, or we're already at the chips
                    # limits
                    #
                    valid = True
            else:
                # If we've already adjusted the gain once, just return
                # the new results. This avoids endless loops where a
                # value is at one extreme pre-gain, and the the other
                # extreme post-gain
                #
                valid = True

            if valid:
                break

        return (broadband, ir)

    ####################################################################
    #
    def get_raw_data(self):
        """
        Returns the raw data from channel0 and channel1 of the sensor.
        """
        self.enable()
        # Wait x ms for ADC to complete
        #
        if self.integ_time == self.INTEG_TIME_13MS:
            time.sleep(0.013)
        elif self.integ_time == self.INTEG_TIME_101MS:
            time.sleep(0.101)
        else:
            time.sleep(0.402)
        chan1 = self._device.readU16(self.COMMAND_BIT | self.WORD_BIT |
                                     self.REG_CHAN1_LOW)
        chan0 = self._device.readU16(self.COMMAND_BIT | self.WORD_BIT |
                                     self.REG_CHAN0_LOW)
        self.disable()
        return (chan0, chan1)
