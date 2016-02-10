from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name='TSL2561',
      version='1.0.0',
      author='Scanner Luce',
      author_email='scanner@apricot.com',
      description=('Library for accessing the TSL2561 luminosity sensor on a '
                   'Raspberry Pi or Beaglebone Black.'),
      license='MIT',
      url='https://github.com/scanner/TSL2561_Python/',
      dependency_links=['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.9.3'],
      install_requires=['Adafruit-GPIO>=0.9.3'],
      packages=find_packages())
