"""Custom Publisher and Subscriber.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import time
from pyaer.comm import EventPublisher, EventSubscriber


class CustomPublisher(EventPublisher):

    def __init__(self, device, port):
        super().__init__(device, port)

    def send_data(self):
        while True:
            try:
                t = time.localtime()
                curr_time = time.strftime("%H:%M:%S", t)
                msg = "hello, a custom data {}".format(curr_time)
                self.socket.send_multipart(
                    [self.topic, bytes(msg, "utf-8")])

                print("Publishing {}".format(msg))
            except KeyboardInterrupt:
                break


class CustomSubscriber(EventSubscriber):

    def __init__(self, port):
        super().__init__(port)

    def recv_data(self):
        """Subscribe data main loop.

        Reimplement to your need.
        """
        while True:
            topic, data = self.socket.recv_multipart()

            print("Received data: {}".format(data))
