"""DAVIS Demo based on RoShamBo.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function

import argparse
import pickle

import threading

import numpy as np
import cv2
from glumpy import app, gloo, gl

from pyaer.davis import DAVIS

# parse model
parser = argparse.ArgumentParser()
parser.add_argument("--num-frames", "-n", type=int, default=20,
                    help="number of frames taken")
parser.add_argument("--undistort", "-u", action="store_true")
args = parser.parse_args()

# open DVS model
device = DAVIS()

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

WIDTH = device.dvs_size_X
HEIGHT = device.dvs_size_Y

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

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = int(WINDOW_WIDTH*(HEIGHT/WIDTH))

window = app.Window(width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                    aspect=1, title="DAVIS Calibration")

img_array = (np.random.uniform(
    0, 1, (HEIGHT, WIDTH, 3))*250).astype(np.uint8)
event_array = np.zeros((HEIGHT, WIDTH, 2), dtype=np.int64)

# for calibration
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
GRID_X = 5
GRID_Y = 4
obj_p = np.zeros((GRID_X*GRID_Y, 3), np.float32)
obj_p[:, :2] = np.mgrid[0:GRID_X, 0:GRID_Y].T.reshape(-1, 2)

obj_points = []  # 3D points in the real world
img_points = []  # 2D points in image plane
num_images_saved = 0
TAKE_SHOT = False
SHOTS_COUNTER = 0
DO_CALIBRATION = False

if args.undistort is True:
    with open("calibration_matrix.pkl", "rb") as f:
        calibrations = pickle.load(f)
        f.close()
    print("Loaded Calibration information.")


@window.event
def on_key_press(key, modifiers):
    global TAKE_SHOT, DO_CALIBRATION
    if key == app.window.key.UP:
        TAKE_SHOT = True
    elif key == app.window.key.DOWN:
        DO_CALIBRATION = True


@window.event
def on_close():
    global device

    print("Shutting down the device")
    device.shutdown()
    del device


@window.event
def on_draw(dt):
    global img_array, event_array, data_stream, device, img_points, \
        obj_points, num_images_saved, TAKE_SHOT, SHOTS_COUNTER, \
        DO_CALIBRATION
    window.clear()

    if data_stream is False:
        device.start_data_stream()
        # setting bias after data stream
        #  device.set_bias_from_json("./configs/davis346_config.json")
        data_stream = True

    lock.acquire()

    (pol_events, num_pol_event,
     special_events, num_special_event,
     frames_ts, frames, imu_events,
     num_imu_event) = device.get_event("events_hist")

    if frames.shape[0] != 0:
        candidate_image = frames[0]
        img_array[..., 0] = frames[0]
        img_array[..., 1] = frames[0]
        img_array[..., 2] = frames[0]

        if args.undistort is False:
            if num_images_saved < args.num_frames \
                    and DO_CALIBRATION is True:
                ret, corners = cv2.findChessboardCorners(
                    candidate_image, (GRID_X, GRID_Y), None)
                if ret is True:
                    obj_points.append(obj_p)

                    corners2 = cv2.cornerSubPix(
                        candidate_image, corners, (11, 11),
                        (-1, -1), criteria)
                    img_points.append(corners2)

                    cv2.drawChessboardCorners(
                        img_array, (GRID_X, GRID_Y), corners2, ret)
                    num_images_saved += 1
                    DO_CALIBRATION = False
                    print("Captured %i Frames" % (num_images_saved))
            elif num_images_saved == args.num_frames and \
                    DO_CALIBRATION is False:
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                    obj_points, img_points, candidate_image.shape[::-1],
                    None, None)
                with open("calibration_matrix.pkl", "wb") as f:
                    pickle.dump([mtx, dist, rvecs, tvecs], f)
                    f.close()
                print("Calibration completed, close the program")
        else:
            h, w = frames[0].shape[:2]
            new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(
                calibrations[0], calibrations[1],
                (w, h), 1, (w, h))
            img_array = cv2.undistort(
                img_array, calibrations[0], calibrations[1],
                None, new_camera_mtx)
            x, y, w, h = roi
            img_array[y, x, :] = [255, 0, 0]
            img_array[y, x+w, :] = [255, 0, 0]
            img_array[y+h, x, :] = [255, 0, 0]
            img_array[y+h, x+w, :] = [255, 0, 0]

        if TAKE_SHOT is True:
            shot_name = "shot_{}.png".format(SHOTS_COUNTER)
            cv2.imwrite(shot_name, img_array)
            print("Shot %s is taken" % (shot_name))

            SHOTS_COUNTER += 1
            TAKE_SHOT = False

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
