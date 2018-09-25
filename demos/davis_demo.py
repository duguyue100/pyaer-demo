"""DAVIS Demo based on RoShamBo.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import threading

import numpy as np
from glumpy import app, gloo, gl

from pyaer.davis import DAVIS


# Load Keras Model
#  model = load_model(filepath="./res/roshambo_model_and_weights.hdf5")

#  model.summary()

# open DVS model
device = DAVIS()

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

window = app.Window(width=2048, height=1536, aspect=1, title="DAVIS Demo")

img_array = (np.random.uniform(
    0, 1, (180, 240, 3))*250).astype(np.uint8)
event_array = np.zeros((180, 240, 2), dtype=np.int64)

symbol_list = ["paper", "scissors", "rock", "no sign"]
robot_list = ["scissors", "rock", "paper", "no sign"]
break_time = 15
break_idx = 1


@window.event
def on_close():
    global device

    print ("Shutting down the device")
    device.shutdown()
    del device


@window.event
def on_draw(dt):
    global img_array, event_array, data_stream, device
    window.clear()

    if data_stream is False:
        device.start_data_stream()
        # setting bias after data stream
        device.set_bias_from_json("./configs/davis240c_config.json")
        data_stream = True

    lock.acquire()

    (pol_events, num_pol_event,
     special_events, num_special_event,
     frames_ts, frames, imu_events,
     num_imu_event) = device.get_event("events_hist")

    if frames.shape[0] != 0:
        img_array[..., 0] = frames[0]
        img_array[..., 1] = frames[0]
        img_array[..., 2] = frames[0]

        # On events
        img_array = img_array.astype(np.int16)
        event_img_pos = (event_array[..., 1] > 0).astype(np.int16)*-255
        event_img_pos = event_img_pos[..., np.newaxis].repeat(3, axis=2)
        event_img_pos[..., 0] *= -1

        event_img_neg = (event_array[..., 0] > 0).astype(np.int16)*-255
        event_img_neg = event_img_neg[..., np.newaxis].repeat(3, axis=2)
        event_img_neg[..., 1] *= -1

        img_array += event_img_pos
        img_array += event_img_neg
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        # clear event array
        event_array = np.zeros((180, 240, 2), dtype=np.int64)
    else:
        if num_pol_event != 0:
            event_array += pol_events

    quad["texture"] = img_array
    quad.draw(gl.GL_TRIANGLE_STRIP)
    lock.release()


quad = gloo.Program(vertex, fragment, count=4)
quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
quad['texcoord'] = [(0, 1), (0, 0), (1, 1), (1, 0)]
quad['texture'] = img_array
app.run(framerate=150)
