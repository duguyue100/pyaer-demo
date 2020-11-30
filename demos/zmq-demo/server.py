"""0MQ based server for tossing messages.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import print_function, absolute_import

import argparse
from random import randrange

from pyaer.utils import expandpath, import_custom_module
from pyaer.comm import EventPublisher


parser = argparse.ArgumentParser()
parser.add_argument("--custom_pub", type=expandpath,
                    default="",
                    help="path to the custom publisher class")
parser.add_argument("--custom_class", type=str,
                    default="",
                    help="custom publisher class name")


args = parser.parse_args()

# define publisher
if args.custom_pub == "":
    # fall back to the default publisher
    publisher = EventPublisher(device=None, port=5556)
    print("Use default publisher")
else:
    # use custom publisher
    print("Use custom publisher {}".format(args.custom_class))
    CustomPublisher = import_custom_module(args.custom_pub, args.custom_class)
    publisher = CustomPublisher(device=None, port=5556)

# Start sending data
publisher.send_data()
