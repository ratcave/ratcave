__author__ = 'ratcave'


import serial
import serial.tools.list_ports as list_usb_ports



arduino_ports = [x[0] for x in list_usb_ports.comports() if 'Arduino' in x[1]]
arduino_ports = [''] if len(arduino_ports) == 0 else arduino_ports  # Really sloppy workaround for if no usb arduino devices connected.  Find a better solution!

class USB_TTL(object):

    def __init__(self, port=arduino_ports[0], baud=9600):
        """Auto-Searches for a connected USB device over the range COM1-COM9, through which ttl pulses can be sent to
                the indicated channel.
        """
        import sys
        assert sys.platform == 'win32', "USB_TTL only implemented for 32-bit Windows systems."

        self.serial = serial.Serial(port, baud)

    def send(self, channel):
        """Sends a ttl on the specified channel (integer)"""
        self.serial.write(str(channel)+'c')  # Adds a character onto the end of the integer so the Arduino stops reading and responds.
        assert channel < 10, "TTL channel number too high."






