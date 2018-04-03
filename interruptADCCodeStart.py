#!/usr/bin/python
#!/usr/bin/env python2.7
# original script by Alex Eames http://RasPi.tv
# http://RasPi.tv/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
# additional code added from ipDisplay.py by cut and paste
# modified ADC0832 to use BMC numbering rather than BOARD

import time
import RPi.GPIO as GPIO
import ADC0832 as ADC
import subprocess
import Adafruit_CharLCD as LCD

lcd = LCD.Adafruit_CharLCDPlate()
GPIO.setmode(GPIO.BCM)


# GPIO 23 & 17 set up as inputs, pulled up to avoid false detection.
# Both ports are wired to connect to GND on button press.
# So we'll be setting up falling edge detection for both
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ADC setup code
#This is where you change the pins for the ADC if needed
ADC.setup(cs=24, clk=25, dio=8)

#get IP and Host name (from ipDisplay.py)
while True:
    IPaddr = subprocess.check_output(['hostname', '-I'])
    if len(IPaddr) > 8:
        break
    else:
        time.sleep(2)
Name = subprocess.check_output(['hostname']).strip()
displayText = IPaddr + Name

# now we'll define two threaded callback functions
# these will run in another thread when our events are detected


def my_callbackADC(channel):
    global ADCSelect
    ADCSelect = True


def my_callbackIP(channel):
    global ADCSelect
    ADCSelect = False

# initializing variables and constants for the callbacks and loops
ADCSelect = False
oldprintLCDString = None
MAXVOLTAGE = 3.3
MAXADCVALUE = 255
LOOPDELAY = 0.2

# when a falling edge is detected on port 17, regardless of whatever
# else is happening in the program, the function my_callback will be run
GPIO.add_event_detect(17, GPIO.FALLING, callback=my_callbackADC, bouncetime=300)
GPIO.add_event_detect(23, GPIO.FALLING, callback=my_callbackIP, bouncetime=300)


def ADCread():
    """ This function reads the ADC and returns a string that
    is sutible for pumping directly into a message function for
    the LCD panel
    There are no arguments for this function
    """
    result = ADC.getResult(0)
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
GPIO.cleanup()           # clean up GPIO on normal exit

