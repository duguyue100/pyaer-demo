"""DVXplorer Test.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import

import numpy as np
import cv2

from pyaer.dvxplorer import DVXPLORER
from timer import Timer

device = DVXPLORER()

print("Device ID:", device.device_id)
print("Device Serial Number:", device.device_serial_number)
print("Device USB bus Number:", device.device_usb_bus_number)
print("Device USB device address:", device.device_usb_device_address)
print("Device String:", device.device_string)
print("Device Firmware Version:", device.firmware_version)
print("Logic Version:", device.logic_version)
print("Device Chip ID:", device.chip_id)
if device.device_is_master:
    print("Device is master.")
else:
    print("Device is slave.")
print("MUX has statistics:", device.mux_has_statistics)
print("Device size X:", device.dvs_size_X)
print("Device size Y:", device.dvs_size_Y)
print("DVS has statistics:", device.dvs_has_statistics)
print("IMU Type:", device.imu_type)
print("EXT input has generator:", device.ext_input_has_generator)

clip_value = 3
histrange = [(0, v) for v in (device.dvs_size_Y, device.dvs_size_X)]

# load new config
device.set_bias_from_json("./configs/dvxplorer_config.json")
print(device.get_bias())
device.start_data_stream()

while True:
    try:
        with Timer("time to fetch data"):
            (pol_events, num_pol_event,
             special_events, num_special_event,
             imu_events, num_imu_event) = \
                device.get_event("events_hist")

        print("Number of events:", num_pol_event)

        if num_pol_event != 0:
            with Timer("time to prepare plotting"):
                img = pol_events[..., 1]-pol_events[..., 0]
                img = np.clip(img, -clip_value, clip_value)
                img = (img+clip_value)/float(clip_value*2)
            #  print("I'm here")
            #  pol_on = (pol_events[:, 3] == 1)
            #  pol_off = np.logical_not(pol_on)
            #  img_on, _, _ = np.histogram2d(
            #          pol_events[pol_on, 2], pol_events[pol_on, 1],
            #          bins=(device.dvs_size_Y, device.dvs_size_X),
            #          range=histrange)
            #  img_off, _, _ = np.histogram2d(
            #          pol_events[pol_off, 2], pol_events[pol_off, 1],
            #          bins=(device.dvs_size_Y, device.dvs_size_X),
            #          range=histrange)
            #  if clip_value is not None:
            #      integrated_img = np.clip(
            #          (img_on-img_off), -clip_value, clip_value)
            #  else:
            #      integrated_img = (img_on-img_off)
            #  img = integrated_img+clip_value

            with Timer("Time to plot"):
                cv2.imshow("image", img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    except KeyboardInterrupt:
        device.shutdown()
        break
