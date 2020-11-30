"""Custom Publisher and Subscriber.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import time
import json
import numpy as np
import cv2

from pyaer import libcaer
from pyaer.comm import EventPublisher, EventSubscriber


class CustomPublisher(EventPublisher):

    def __init__(self, device, port):
        super().__init__(device, port)

    def send_data(self):
        while True:
            try:
                data = self.device.get_event()

                if data is not None:
                    data = self.pack_data(data)

                    self.socket.send_multipart(data)

                    t = time.localtime()

                    curr_time = time.strftime("%H:%M:%S", t)

                    print("Publishing {}".format(curr_time))
            except KeyboardInterrupt:
                self.close()
                break


class CustomSubscriber(EventSubscriber):

    def __init__(self, port):
        super().__init__(port)

    def recv_data(self):
        """Subscribe data main loop.

        Reimplement to your need.
        """
        while True:
            data = self.socket.recv_multipart()
            data = self.unpack_data(data)

            if data[4] is not None:
                if data[4].shape[0] != 0:
                    cv2.imshow("frame", data[4][0])

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                print("Received events: {}, {}".format(
                        data[1].shape, data[4].shape))
