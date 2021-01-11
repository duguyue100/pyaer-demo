"""DVXplorer Publisher for this demo.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

from pyaer.utils import get_nanotime
from pyaer.comm import AERPublisher


class DVXPublisher(AERPublisher):
    def __init__(self, device, url="tcp://127.0.0.1",
                 port=5100, master_topic="", name=""):
        """DVXPublisher."""
        super(DVXPublisher, self).__init__(
            device=device, url=url, port=port, master_topic=master_topic,
            name=name)

    def run(self):
        while True:
            try:
                data = self.device.get_event("events_hist")
                timestamp = get_nanotime()
                if data is not None:
                    # send polarity events
                    #  polarity_data = self.pack_polarity_events(
                    #      timestamp,
                    #      self.pack_np_array(data[0]))
                    #  self.socket.send_multipart(polarity_data)

                    polarity_data = self.pack_data_by_topic(
                        "polarity_events",
                        timestamp,
                        self.pack_np_array(data[0]))
                    self.socket.send_multipart(polarity_data)

            except KeyboardInterrupt:
                self.logger.info("Shutting down publisher {}".format(
                    self.name))
                self.close()
                break
