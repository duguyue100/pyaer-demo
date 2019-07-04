"""0MQ based client for tossing messages.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import print_function, absolute_import

import zmq

context = zmq.Context()

print("Connecting to hello world server ...")
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5556")

zip_filter = "10001"

socket.setsockopt_string(zmq.SUBSCRIBE, zip_filter)

total_temp = 0
for update_nbr in range(20):
    string = socket.recv_string()
    zipcode, tempature, relhuminity = string.split()
    print(update_nbr)

    total_temp += int(tempature)

print("Average temperature for zipcode '%s' was %dF" % (
    zip_filter, total_temp / (update_nbr + 1)))
