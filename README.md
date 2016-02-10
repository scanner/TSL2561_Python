# TSL2561_Python
Python library to read data from the TSL2561 luminosity sensor using the Adafruit GPIO library.

The code itself is cribbed from the Adafruit Arduino library for
accessing the device: https://github.com/adafruit/Adafruit_TSL2561

To install, download the library by clicking the download zip link to the right and unzip the archive somewhere on your Raspberry Pi or Beaglebone Black.  Then execute the following command in the directory of the library:

````
sudo python setup.py install
````

Make sure you have internet access on the device so it can download the required dependencies.

See examples of usage in the examples folder.

Simple usage:

>>> from TSL2561.TSL2561 import TSL2561
>>> tsl = TSL2561()
>>> broadband, ir = tsl.get_raw_data()
>>> print "Raw values - broadband: {}, IR: {}".format(broadband, ir)
>>> broadband, ir = tsl.get_luminosity()
>>> print "Luminosity (auto-gain): broadband: {}, IR: {}".format(broadband, ir)
>>> print "Lux: {}".format(tsl.get_lux())
