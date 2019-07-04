"""0MQ based server for tossing messages.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import print_function, absolute_import

import time
import zmq
from random import randrange

# create a context
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

# control loop
while True:
    zipcode = randrange(1, 100000)
    temperature = randrange(-80, 135)
    relhumidity = randrange(10, 60)

    socket.send_string("%i %i %i" % (zipcode, temperature, relhumidity))
