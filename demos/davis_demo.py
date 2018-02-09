"""DAVIS Demo based on RoShamBo.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

from keras.models import load_model
import threading

import numpy as np
from skimage.transform import resize
from glumpy import app, gloo, gl

from pyaer.dvs128 import DVS128


# Load Keras Model
model = load_model(filepath="./res/roshambo_model_and_weights.hdf5")

model.summary()

# open DVS model
device = DVS128()

print ("Device ID:", device.device_id)
if device.device_is_master:
    print ("Device is master.")
else:
    print ("Device is slave.")
print ("Device Serial Number:", device.device_serial_number)
print ("Device String:", device.device_string)
print ("Device USB bus Number:", device.device_usb_bus_number)
print ("Device USB device address:", device.device_usb_device_address)
print ("Device size X:", device.dvs_size_X)
print ("Device size Y:", device.dvs_size_Y)
print ("Logic Version:", device.logic_version)

data_stream = False

lock = threading.Lock()

clip_value = 16
histrange = [(0, v) for v in (128, 128)]

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

window = app.Window(width=1024, height=1024, aspect=1, title="RoShamBo")

img_array = (np.random.uniform(
    0, 1, (128, 128, 3))*250).astype(np.uint8)

symbol_list = ["paper", "scissors", "rock", "no sign"]
robot_list = ["scissors", "rock", "paper", "no sign"]
break_time = 10
break_idx = 1


@window.event
def on_close():
    global device

    print ("Shutting down the device")
    device.shutdown()
    del device


@window.event
def on_draw(dt):
    global data_stream, device, event_list, break_idx, break_time
    window.clear()

    if data_stream is False:
        device.start_data_stream()
        # setting bias after data stream
        device.set_bias_from_json("./configs/dvs128_config.json")
        data_stream = True

    lock.acquire()
    (pol_events, num_pol_event,
     special_events, num_special_event) = \
        device.get_event()

    if num_pol_event != 0:
        pol_on = (pol_events[:, 3] == 1)
        pol_off = np.logical_not(pol_on)
        img_on, _, _ = np.histogram2d(
                pol_events[pol_on, 2], pol_events[pol_on, 1],
                bins=(128, 128), range=histrange)
        img_off, _, _ = np.histogram2d(
                pol_events[pol_off, 2], pol_events[pol_off, 1],
                bins=(128, 128), range=histrange)
        if clip_value is not None:
            integrated_img = np.clip(
                (img_on-img_off), -clip_value, clip_value)
        else:
            integrated_img = (img_on-img_off)
        if break_idx % break_time == 0:
            predict_array = resize(
                integrated_img, (64, 64))[np.newaxis, :, :, np.newaxis]
            prediction = model.predict(predict_array)
            print ("\033[93mYou:\033[0m", symbol_list[np.argmax(prediction)],
                   "\t",
                   "\033[92mMe:\033[0m", robot_list[np.argmax(prediction)])
            break_idx = 1
        else:
            break_idx += 1

        img_array = ((integrated_img+clip_value)/float(
            clip_value*2)*255).astype(np.uint8)
        img_array = img_array[..., np.newaxis].repeat(3, axis=2)
    else:
        img_array = (np.random.uniform(
            0, 1, (128, 128, 3))*250).astype(np.uint8)

    quad["texture"] = img_array
    quad.draw(gl.GL_TRIANGLE_STRIP)
    lock.release()


quad = gloo.Program(vertex, fragment, count=4)
quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
quad['texcoord'] = [(0, 1), (0, 0), (1, 1), (1, 0)]
quad['texture'] = img_array
app.run(framerate=150)
