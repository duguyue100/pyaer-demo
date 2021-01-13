"""A viewer.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

from time import time
import numpy as np
from glumpy import app, gloo, gl

from pyaer.comm import Subscriber


class CamViewer(Subscriber):
    def __init__(self, url, port, topic, name, **kwargs):
        super(CamViewer, self).__init__(
            url=url, port=port, topic=topic, name=name)

        self.height, self.width = kwargs["height"], kwargs["width"]
        self.black_frame = np.zeros(
            (self.height, self.width, 3), dtype=np.uint8)
        self.gray_frame = np.ones(
            (self.height, self.width, 3), dtype=np.uint8)*128
        self.title = kwargs["title"]

    def run(self):
        #  sum_time = 0
        #  n_round = 0
        #
        #  msg_counter = 0
        #  msg_thr = 2

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

        window = app.Window(width=self.width, height=self.height, aspect=1,
                            title=self.title)

        img_array = (np.random.uniform(
            0, 1, (self.height, self.width, 3))*250).astype(np.uint8)

        @window.event
        def on_draw(dt):
            #  global black_frame, gray_frame
            window.clear()

            data = self.socket.recv_multipart()

            data_id, dvs_frame = \
                self.unpack_array_data_by_name(data)

            #  if frames.shape[0] != 0:
            if dvs_frame is not None:

                #  dvs_frame = dvs_frame[..., 1]-dvs_frame[..., 0]
                #  dvs_frame = np.clip(dvs_frame, -3, 3)
                #  dvs_frame = ((dvs_frame+3)*42.5).astype(np.uint8)

                img_array = self.black_frame

                img_array[..., 0] = dvs_frame
                img_array[..., 1] = dvs_frame
                img_array[..., 2] = dvs_frame
            else:
                img_array = self.gray_frame

            quad["texture"] = img_array
            quad.draw(gl.GL_TRIANGLE_STRIP)

        quad = gloo.Program(vertex, fragment, count=4)
        quad['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
        quad['texcoord'] = [(0, 1), (0, 0), (1, 1), (1, 0)]
        quad['texture'] = img_array

        app.run(framerate=300)
