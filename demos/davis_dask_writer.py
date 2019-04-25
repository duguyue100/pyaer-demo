"""Demonstrate the use of Dask to render and write.

Author: Yuhuang Hu
Email : yuhuang.hu@ini.uzh.ch
"""

from __future__ import print_function, absolute_import

from dask.distributed import Client
import dask.array as da
import time

import h5py

from pyaer.davis import DAVIS


# Camera


#  def data_fetch():
#      global device
#      (pol_events, num_pol_event,
#       special_events, num_special_event,
#       frames_ts, frames, imu_events,
#       num_imu_event) = device.get_event("events_hist")
#
#      print(pol_events.shape)
#
#      return pol_events


def write_data(data_obj):
    data = h5py.File("test.h5", "a")
    ds = data.create_dataset("/"+str(data_obj[0, 0]), shape=data_obj.shape,
                             dtype="int64")
    x = da.from_array(data_obj, chunks=(1, 1))
    da.store(x, ds)
    print("writing")
    data.close()
    #  print("-"*50, str(data_obj[0, 0]))
    #  da.to_hdf5("test.h5", {"/"+str(data_obj[0, 0]): x})

    return data_obj.shape


def join(x, y):
    return x+y


def main():
    """Central function"""

    # writing file object
    #  db = h5py.File("test.h5", "w")
    #  db.create_dataset(
    #      name="events",
    #      shape=(0, 4),
    #      maxshape=(None, 4),
    #      dtype="int64")

    # Camera
    device = DAVIS()
    device.start_data_stream()
    print("Device ID:", device.device_id)
    if device.device_is_master:
        print("Device is master.")
    else:
        print("Device is slave.")
    print("Device Serial Number:", device.device_serial_number)
    print("Device String:", device.device_string)
    print("Device USB bus Number:", device.device_usb_bus_number)
    print("Device USB device address:", device.device_usb_device_address)
    print("Device size X:", device.dvs_size_X)
    print("Device size Y:", device.dvs_size_Y)
    print("Logic Version:", device.logic_version)

    client = Client()

    while True:
        start = time.time()
        (pol_events, num_pol_event,
         special_events, num_special_event,
         frames_ts, frames, imu_events,
         num_imu_event) = device.get_event()
        #  dvs_data = client.submit(data_fetch)
        #  pol_events = client.scatter(pol_events)
        write_flag_1 = client.submit(write_data, pol_events)
        #  write_flag_2 = client.submit(write_data, pol_events)
        #  joined = client.submit(join, write_flag_1, write_flag_2)

        #  print("Outside", joined.result())
        #  print("Time = ", time.time()-start)
        #  print("Outside", write_flag_2.result())


if __name__ == "__main__":
    main()
