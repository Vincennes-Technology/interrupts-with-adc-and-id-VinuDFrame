#!/usr/bin/python
#!/usr/bin/env python2.7
# original script by Alex Eames http://RasPi.tv
# http://RasPi.tv/ ###Had to split the URL onto two lines###
# how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3

# Modified by DFrame:
# additional code added from ipDisplay.py by cut and paste
# modified ADC0832 to use BMC numbering rather than BOARD numbering
# Added functions for reading and converting ADC into strings for LCD display
# Edited to be PEP-8 complient

# initializing variables and constants for the callbacks and loops
ADCSelect = False
oldprintLCDString = None
MAXVOLTAGE = 3.3
MAXADCVALUE = 255
LOOPDELAY = 0.2
ADC_INTERRUPT = 17
ID_INTERRUPT = 23
DEBOUNCE_TIME = 300
ADC_CHANNEL = 0


import time
import RPi.GPIO as GPIO
import ADC0832 as ADC
import subprocess
import Adafruit_CharLCD as LCD

# LCD setup code
lcd = LCD.Adafruit_CharLCDPlate()
GPIO.setmode(GPIO.BCM)


# GPIO ID_INTERRUPT & ADC_INTERRUPT set up as inputs,
# pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(ID_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ADC_INTERRUPT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ADC setup code
#This is where you change the pins for the ADC if needed
ADC.setup(cs=24, clk=25, dio=8)

#get IP and Host name (from ipDisplay.py)
MIN_IP_ADDRESS_LENGTH = 8
IP_ADDRESS_WAIT = 2
while True:
    IPaddr = subprocess.check_output(['hostname', '-I'])
    if len(IPaddr) > MIN_IP_ADDRESS_LENGTH:
        break
    else:
        time.sleep(IP_ADDRESS_WAIT)
Name = subprocess.check_output(['hostname']).strip()
displayText = IPaddr + Name

# now we'll define two threaded callback functions
# these will run in another thread when our events are detected
# They both modify the global variable ADCSelect


def my_callbackADC(channel):
    """ Threaded callback function for when the ADC button is pressed"""
    global ADCSelect
    ADCSelect = True


def my_callbackIP(channel):
    """ Threaded callback function for when the ID button is pressed"""
    global ADCSelect
    ADCSelect = False


# when a falling edge is detected on port ADC_INTERRUPT or ID_INTERRUPT,
# regardless of whatever else is happening in the program, the call back
# function will be run
# each button is "debounced" by disabling the function for DEBOUNCE_TIME ms
    #lint:disable
GPIO.add_event_detect(ADC_INTERRUPT, GPIO.FALLING,
     callback=my_callbackADC, bouncetime=DEBOUNCE_TIME)
GPIO.add_event_detect(ID_INTERRUPT, GPIO.FALLING,
     callback=my_callbackIP, bouncetime=DEBOUNCE_TIME)
    #lint:enable


def ADCread():
    """ This function reads the ADC and returns a string that
    is sutible for pumping directly into a message function for
    the LCD panel
    There are no arguments for this function
    """
    result = ADC.getResult(ADC_CHANNEL)
    voltage = result * MAXVOLTAGE / MAXADCVALUE
    return "Current Voltage = \n %1.3f" % voltage


def IPandHost():
    """ This function returns the string for the IP Address and Hostname
    This string is suitable for directly displaying on the LCD screen.
    """
    return displayText

# This loop will constantly check the ADC or display the IP/Hostname
# Escape from it with a <CTL C> at the terminal window
try:
    while True:
        if ADCSelect:
            printLCDString = ADCread()
        else:
            printLCDString = IPandHost()
        #check to see if the LCD needs an update.
        if (oldprintLCDString == printLCDString):
            pass
        else:
            lcd.clear()
            lcd.message(printLCDString)
            oldprintLCDString = printLCDString
        time.sleep(LOOPDELAY)
except KeyboardInterrupt:
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
GPIO.cleanup()           # ensures the clean up of GPIO on normal exit

