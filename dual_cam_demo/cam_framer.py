"""A PubSub utility.

Framing events and publish it out.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

import numpy as np
from time import time

from pyaer.comm import PubSuber
from pyaer.comm import Publisher
from pyaer.comm import AERSubscriber
from pyaer.utils import get_nanotime


def dvs_hist_framer(events):
    """Use returned histogram as framer."""
    dvs_frame = events[..., 1]-events[..., 0]

    dvs_frame = np.clip(dvs_frame, -3, 3)

    return ((dvs_frame+3)*42.5).astype(np.uint8)


def dvs_framer(events, histrange, height, width):
    """Accumulate event frame from an array of events.
    # Arguments
    events: np.ndarray
        an [N events x 4] array
    # Returns
    event_frame: np.ndarray
        an event frame
    """
    pol_on = (events[:, 3] == 1)
    pol_off = np.logical_not(pol_on)

    img_on, _, _ = np.histogram2d(
            events[pol_on, 2], events[pol_on, 1],
            bins=(height, width), range=histrange)
    img_off, _, _ = np.histogram2d(
            events[pol_off, 2], events[pol_off, 1],
            bins=(height, width), range=histrange)

    img = np.clip(img_on-img_off, -3, 3)

    return ((img+3)*42.5).astype(np.uint8)


class CamFramer(PubSuber):
    def __init__(self, url, pub_port, pub_topic, pub_name,
                 sub_port, sub_topic, sub_name):
        super(CamFramer, self).__init__(
            url=url, pub_port=pub_port, pub_topic=pub_topic,
            pub_name=pub_name, sub_port=sub_port,
            sub_topic=sub_topic, sub_name=sub_name)

        self.subscriber = AERSubscriber(url=self.url, port=self.sub_port,
                                        topic=self.sub_topic,
                                        name=self.sub_name)
        self.publisher = Publisher(url=self.url, port=self.pub_port,
                                   master_topic=self.pub_topic,
                                   name=self.pub_name)

        # define height and width of the frame
        #  self.height, self.width = 480, 640
        #  self.histrange = np.asarray(
        #      [(0, v) for v in (self.height, self.width)],
        #      dtype=np.int64)

    def run(self, verbose=False):
        sum_time = 0
        n_round = 0
        while True:
            try:
                # receive data
                data = self.subscriber.socket.recv_multipart()
                timestamp = get_nanotime()

                # unpack, framing data
                data_id, polarity_events = \
                    self.subscriber.unpack_array_data_by_name(data)

                if polarity_events is not None:
                    s_time = time()
                    dvs_frame = dvs_hist_framer(polarity_events)

                    #  dvs_frame = dvs_framer(
                    #      polarity_events, self.histrange,
                    #      self.height, self.width)

                    sum_time += time()-s_time
                    n_round += 1

                    dvs_frame_data = self.publisher.pack_data_by_topic(
                        "dvs_frame",
                        timestamp,
                        self.publisher.pack_np_array(dvs_frame))

                    self.publisher.socket.send_multipart(dvs_frame_data)

                    del polarity_events, dvs_frame

            except KeyboardInterrupt:
                self.logger.info("Average Time: {}ms".format(
                    sum_time/n_round*1000))
