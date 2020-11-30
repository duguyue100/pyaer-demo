"""0MQ based client for tossing messages.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import print_function, absolute_import

import argparse

from pyaer.utils import expandpath, import_custom_module
from pyaer.comm import EventSubscriber

parser = argparse.ArgumentParser()
parser.add_argument("--custom_sub", type=expandpath,
                    default="",
                    help="path to the custom publisher class")
parser.add_argument("--custom_class", type=str,
                    default="",
                    help="custom publisher class name")


args = parser.parse_args()

# define publisher
if args.custom_sub == "":
    # fall back to the default publisher
    subscriber = EventSubscriber(port=5556)
    print("Use default subscriber")
else:
    # use custom publisher
    print("Use custom subscriber {}".format(args.custom_class))
    CustomSubscriber = import_custom_module(args.custom_sub, args.custom_class)
    subscriber = CustomSubscriber(port=5556)

# Start sending data
subscriber.recv_data()
