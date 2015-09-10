__author__ = 'ratcave'

from pypixxlib import _libdpx
import time


def start_frame_sync_signal():
    """
    This demo opens the device, stops any current running schedule,
    sets the ram/buffer for our update synchronization on video signal,
    and starts right away.

    Originally created by Danny Michaud Landry.
    """

    # Select Propixx Controller
    _libdpx.DPxOpen()
    _libdpx.DPxSelectDevice('PROPixx Ctrl')
    _libdpx.DPxStopDoutSched()
    _libdpx.DPxUpdateRegCache()

    # Set up Digital Out signal schedule
    base_address = _libdpx.DPxGetDoutBuffBaseAddr()
    #buffer_dout = [0xFFFF, 0]  # 2**16 - 1, means will fire on all 16 pins: 0b1111111111111111
    buffer_dout = [1, 0]  # Only on pin 1: 0b0000000000000001
    _libdpx.DPxSetDoutBuff(base_address, 4)
    _libdpx.DPxWriteRam(base_address, buffer_dout)

    """DPxSetDoutSched(onset, rateValue, rateUnits, count) are as follow:
        Onset: 0, starts current_time.
        Rate: 2, on/off happens once per frame.
        Units: 'video', per video frame.
        Duration: 0, lasts until the schedule is stopped.
    """
    _libdpx.DPxSetDoutSched(0, 2, 'video', 0)
    _libdpx.DPxUpdateRegCache()
    _libdpx.DPxStartDoutSched()

    # Update Propixx Controller to start running new settings
    _libdpx.DPxUpdateRegCache()

    time.sleep(1)  # Wait for equipment to finish the reset before continuing (usually takes a second or so)

def start_motive_recording():
    """
    This demo opens the device, stops any current running schedule,
    sets the ram/buffer for our update synchronization on video signal,
    and starts right away.

    Originally created by Danny Michaud Landry.
    """

    # Select Propixx Controller
    _libdpx.DPxOpen()
    _libdpx.DPxSelectDevice('PROPixx Ctrl')
    _libdpx.DPxStopDoutSched()
    _libdpx.DPxUpdateRegCache()

    # Set up Digital Out signal schedule
    base_address = _libdpx.DPxGetDoutBuffBaseAddr()
    #buffer_dout = [0xFFFF, 0]  # 2**16 - 1, means will fire on all 16 pins: 0b1111111111111111
    buffer_dout = [2, 0]  # Only on pin 1: 0b0000000000000001
    _libdpx.DPxSetDoutBuff(base_address, 4)
    _libdpx.DPxWriteRam(base_address, buffer_dout)

    """DPxSetDoutSched(onset, rateValue, rateUnits, count) are as follow:
        Onset: 0, starts current_time.
        Rate: 2, on/off happens once per frame.
        Units: 'video', per video frame.
        Duration: 0, lasts until the schedule is stopped.
    """
    _libdpx.DPxSetDoutSched(0, 2, 'Hz', 2)
    _libdpx.DPxUpdateRegCache()
    _libdpx.DPxStartDoutSched()

    # Update Propixx Controller to start running new settings
    _libdpx.DPxUpdateRegCache()