"""DYNAPSE Demo.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function
import threading

import numpy as np

from glumpy import app
from glumpy.graphics.collections import PointCollection

from pyaer.dynapse import DYNAPSE


# define dynapse
device = DYNAPSE()

print ("Device ID:", device.device_id)
if device.device_is_master:
    print ("Device is master.")
else:
    print ("Device is slave.")
print ("Device Serial Number:", device.device_serial_number)
print ("Device String:", device.device_string)
print ("Device USB bus Number:", device.device_usb_bus_number)
print ("Device USB device address:", device.device_usb_device_address)
print ("Logic Version:", device.logic_version)
print ("Logic Clock:", device.logic_clock)
print ("Chip ID:", device.chip_id)
print ("AER has statistics:", device.aer_has_statistics)
print ("MUX has statistics:", device.mux_has_statistics)

device.send_default_config()
device.start_data_stream()

# define glumpy window
xdim = 64
ydim = 64
sizeW = 1024
timeMul = 10e-6

window = app.Window(sizeW, sizeW, color=(0, 0, 0, 1))
points = PointCollection("agg", color="local", size="local")

lock = threading.Lock()


@window.event
def on_close():
    global device
    device.shutdown()
    print("closed thread ")


@window.event
def on_draw(dt):
    global dtt, device
    window.clear()

    lock.acquire()
    (events, num_events) = device.get_event()

    timestamp = events[:, 0]
    neuron_id = events[:, 1]
    core_id = events[:, 2]
    chip_id = events[:, 3]

    timestamp = np.diff(timestamp)
    timestamp = np.insert(timestamp, 0, 0.0001)

    if(num_events > 1):
        for i in range(num_events):
            dtt += float(timestamp[i])*timeMul

            if(dtt >= 1.0):
                dtt = -1.0
                del points[...]
            y_c = 0
            if(chip_id[i] == 0):
                y_c = (neuron_id[i])+(core_id[i]*256)+((chip_id[i])*1024)
                y_c = float(y_c)/(1024*2.0)
            elif(chip_id[i] == 2):
                y_c = (neuron_id[i])+(core_id[i]*256)+((chip_id[i])*1024)
                y_c = (float(y_c)/(1024*4.0))*2-((sizeW*0.5)/sizeW)
            elif(chip_id[i] == 1):
                y_c = (neuron_id[i])+(core_id[i]*256)+((chip_id[i])*1024)
                y_c = -(float(y_c)/(1024*2.0))
            elif(chip_id[i] == 3):
                y_c = (neuron_id[i])+(core_id[i]*256)+((chip_id[i])*1024)
                y_c = -(float(y_c)/(1024*2.0))+((sizeW*0.5)/sizeW)*3
            if(core_id[i] == 0):
                col = (1, 0, 1, 1)
            elif(core_id[i] == 1):
                col = (1, 0, 0, 1)
            elif(core_id[i] == 2):
                col = (0, 1, 1, 1)
            elif(core_id[i] == 3):
                col = (0, 0, 1, 1)
            y_c = round(y_c, 6)

            points.append([dtt, y_c, 0], color=col, size=3)
    points.draw()
    lock.release()


dtt = -1.0
window.attach(points["transform"])
window.attach(points["viewport"])
app.run(framerate=150)
