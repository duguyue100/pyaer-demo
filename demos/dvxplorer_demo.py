"""DAVIS Demo based on RoShamBo.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import threading

import numpy as np
from glumpy import app, gloo, gl

from pyaer import libcaer
from pyaer.dvxplorer import DVXPLORER

from timer import Timer

# open DVS model
device = DVXPLORER()

print("Device ID:", device.device_id)
if device.device_is_master:
    print("Device is master.")
else:
    print("Device is slave.")
print("Device Serial Number:", device.device_serial_number)
print("Device String:", device.device_string)
print("Device USB bus Number:", device.device_usb_bus_number)
print("Device USB device address:", device.device_usb_device_address)
print("Device size X:", device.dvs_size_X)
print("Device size Y:", device.dvs_size_Y)
print("Logic Version:", device.logic_version)

data_stream = False

lock = threading.Lock()

clip_value = None

vertex = """
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        gl_Position = vec4(position, 0.0, 1.0);
        v_texcoord = texcoord;
    }
"""

fragment = """
    uniform sampler2D texture;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(texture, v_texcoord);
    }
"""

window = app.Window(width=1280, height=960, aspect=1, title="DVXplorer Demo")

img_array = (np.random.uniform(
    0, 1, (480, 640, 3))*250).astype(np.uint8)
event_array = np.zeros((480, 640, 2), dtype=np.int64)
black_frame = np.zeros((480, 640, 3), dtype=np.int8)
gray_frame = np.ones((480, 640, 3), dtype=np.int8)*128

break_time = 15
break_idx = 1
fs = 3

factor = 255/(fs*2)
#  display_event = True


@window.event
def on_key_press(key, modifiers):
    global fs, factor
    if key == app.window.key.UP:
        fs = fs+1 if fs < 255 else 255
        factor = 255/(fs*2)
    elif key == app.window.key.DOWN:
        fs = fs-1 if fs > 1 else 1
        factor = 255/(fs*2)


@window.event
def on_close():
    global device

    print("Shutting down the device")
    device.shutdown()
    del device


@window.event
def on_draw(dt):
    global img_array, event_array, data_stream, device, fs, display_frame, \
        black_frame, factor
    window.clear()

    if data_stream is False:
        device.start_data_stream()
        # setting bias after data stream
        device.set_bias_from_json("./configs/dvxplorer_config.json")
        data_stream = True

    lock.acquire()

    with Timer("Time to fetch data"): 
        (pol_events, num_pol_event,
         special_events, num_special_event,
         imu_events, num_imu_event) = \
            device.get_event("events_hist")

    with Timer("Time to prepare plotting"):
        #  if frames.shape[0] != 0:
        if num_pol_event != 0:
            img_array = black_frame

            img = pol_events[..., 1]-pol_events[..., 0]
            img = np.clip(img, -fs, fs)
            img = ((img+fs)*factor).astype(np.uint8)

            img_array[..., 0] = img
            img_array[..., 1] = img
            img_array[..., 2] = img
        else:
            img_array = gray_frame 

        #  #  if display_event is True:
        #  # On events
        #  img_array = img_array.astype(np.int16)
        #  event_img_pos = event_array[..., 1]
        #  event_img_pos[event_img_pos > fs] = fs
        #  event_img_pos = event_img_pos*(-255//fs)
        #  event_img_pos = event_img_pos[..., np.newaxis].repeat(3, axis=2)
        #  event_img_pos[..., 0] *= -1
        #  #  event_img_pos[..., 1] *= 2
        #
        #  event_img_neg = event_array[..., 0]
        #  event_img_neg[event_img_neg > fs] = fs
        #  event_img_neg = event_img_neg*(-255//fs)
        #  event_img_neg = event_img_neg[..., np.newaxis].repeat(3, axis=2)
        #  event_img_neg[..., 1] *= -1
        #  event_img_neg[..., 0] *= 2
        #
        #  img_array += event_img_pos
        #  img_array += event_img_neg
        #  img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        # clear event array
        #  event_array = np.zeros((480, 640, 2), dtype=np.int64)
        #  else:
        #  if num_pol_event != 0:
        #      event_array += pol_events

    quad["texture"] = img_array
    quad.draw(gl.GL_TRIANGLE_STRIP)
    lock.release()


quad = gloo.Program(vertex, fragment, count=4)
quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
quad['texcoord'] = [(0, 1), (0, 0), (1, 1), (1, 0)]
quad['texture'] = img_array
app.run(framerate=400)
