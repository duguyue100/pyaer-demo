"""0MQ based server for tossing messages.

Author: Yuhuang Hu
Email : duguyue100@gmail.com
"""

from __future__ import print_function, absolute_import

import argparse
import json

from pyaer.davis import DAVIS
from pyaer.dvs128 import DVS128
from pyaer.utils import expandpath, import_custom_module
from pyaer.comm import EventPublisher


parser = argparse.ArgumentParser()
parser.add_argument("--custom_pub", type=expandpath,
                    default="",
                    help="path to the custom publisher class")
parser.add_argument("--custom_class", type=str,
                    default="",
                    help="custom publisher class name")
parser.add_argument("--device", type=str,
                    default="DAVIS",
                    help="Currently supported options: DAVIS, DVS")
parser.add_argument("--noise_filter", action="store_true",
                    help="Add option to enable noise filter.")
parser.add_argument("--bias_file", type=expandpath,
                    default=None,
                    help="Optional bias file")

args = parser.parse_args()

# print all options
print(json.dumps(args.__dict__, indent=4, sort_keys=True))

# open the device
if args.device == "DAVIS":
    device = DAVIS(noise_filter=args.noise_filter)
elif args.device == "DVS":
    device = DVS128(noise_filter=args.noise_filter)

device.start_data_stream()
if args.bias_file is not None:
    device.set_bias_from_json(args.bias_file)

# define publisher
if args.custom_pub == "":
    # fall back to the default publisher
    publisher = EventPublisher(device=device, port=5556)
    print("Use default publisher")
else:
    # use custom publisher
    print("Use custom publisher {}".format(args.custom_class))
    CustomPublisher = import_custom_module(args.custom_pub, args.custom_class)
    publisher = CustomPublisher(device=device, port=5556)

# Start sending data
publisher.send_data()
