"""Client software that receives the data.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""
from __future__ import print_function, absolute_import

import socket
try:
    import cPickle as pickle
except:
    import pickle
import zlib

import cv2

buffer_size = 2**17

IP_address = "172.19.11.178"
port = 8080
address = (IP_address, port)
data_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_receiver.bind(address)

while True:
    try:
        data, address = data_receiver.recvfrom(buffer_size)
        frame_data, event_data = pickle.loads(zlib.decompress(data))

        if frame_data is not None:
            cv2.imshow("frame", frame_data)

        if event_data is not None:
            cv2.imshow("event", event_data)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except KeyboardInterrupt:
        data_receiver.close()
        break
