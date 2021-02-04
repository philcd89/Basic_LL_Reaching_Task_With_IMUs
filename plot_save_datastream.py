# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 14:01:07 2021

@author: philc

This code is a first attempt at piping MotionNode data from the path into a txt file, while also graphically representing data.
"""

import argparse
import sys
from xml.etree.ElementTree import XML

import numpy as np
import matplotlib.pyplot as plt

import MotionSDK


def parse_name_map(xml_node_list):
    name_map = {}

    tree = XML(xml_node_list)

    # <node key="N" id="Name"> ... </node>
    list = tree.findall(".//node")
    for itr in list:
        name_map[int(itr.get("key"))] = itr.get("id")

    return name_map

def stream_data_to_csv(args, out):
    client = MotionSDK.Client(args.host, args.port)

    #
    # Request the channels that we want from every connected device. The full
    # list is available here:
    #
    #   https://www.motionshadow.com/download/media/configurable.xml
    #
    # Select the local quaternion (Lq) and positional constraint (c)
    # channels here. 8 numbers per device per frame. Ask for inactive nodes
    # which are not necessarily attached to a sensor but are animated as part
    # of the Shadow skeleton.
    #
    
    # ADDING linear acceleration (la) and euler angle (r) set!!!!  This should add 6 more numbers per device per frame.
    xml_string = \
        "<?xml version=\"1.0\"?>" \
        "<configurable inactive=\"1\">" \
        "<la/>" \
        "<r/>" \
        "</configurable>"

    if not client.writeData(xml_string):
        raise RuntimeError(
            "failed to send channel list request to Configurable service")

    num_frames = 0
    sample = 1
    xml_node_list = None   
    
    # plotWindow = 3 #seconds: sampling rate of sensors is 100 Hz
    # RShank_lax = np.zeros(plotWindow*100) # initialize empty vectors for plotting at 100 Hz
    # RShank_lay = np.zeros(plotWindow*100)
    # RShank_laz = np.zeros(plotWindow*100)
    
    # fig = plt.figure()
    # plt.axis([0, 300, -100, 100])
    
    while True:
        
        # Block, waiting for the next sample.
        data = client.readData()
        if data is None:
            raise RuntimeError("data stream interrupted or timed out")
            break

        if data.startswith(b"<?xml"):
            xml_node_list = data
            continue

        container = MotionSDK.Format.Configurable(data)

        #
        # Consume the XML node name list. If the print header option is active
        # add that now.
        #
        if xml_node_list:
            if args.header:
                ChannelName = [
                    "lax", "lay", "laz",
                    "rx", "ry", "rz"
                ]

                name_map = parse_name_map(xml_node_list)

                flat_list = []
                for key in container:
                    if key not in name_map:
                        raise RuntimeError(
                            "device missing from name map, unable to print "
                            "header")

                    item = container[key]
                    if len(ChannelName) != item.size():
                        raise RuntimeError(
                            "expected {} channels but found {}, unable to "
                            "print header".format(
                                len(ChannelName), item.size()))

                    name = name_map[key]
                    for channel in ChannelName:
                        flat_list.append("{}.{}".format(name, channel))

                if not len(flat_list):
                    raise RuntimeError(
                        "unknown data format, unabled to print header")

                headerOut = ",".join(["{}".format(v) for v in flat_list])
                headerOut = "sampleNum," + headerOut + "\n"
                out.write(headerOut)
                
                # out.write(
                #     ",".join(["{}".format(v) for v in flat_list]))

            xml_node_list = None

        #
        # Make an array of all of the values, in order, that are part of one
        # sample. This is a single row in the output.
        #
        flat_list = []
        for key in container:
            item = container[key]
            for i in range(item.size()):
                flat_list.append(item.value(i))

        if not len(flat_list):
            raise RuntimeError("unknown data format in stream")

        dataOut = ",".join(["{}".format(round(v, 8)) for v in flat_list])
        dataOut = str(sample) + "," + dataOut + "\n"
        out.write(dataOut)

        # out.write(
        #     ",".join(["{}".format(round(v, 8)) for v in flat_list]))

        

        # ------------------- THIS IS MY NEW CODE -----------------------
        
        #Create a 300 sample vector of x linear acceleration (lax) on right shank node (Node3)
        # RShank_lax[0:len(RShank_lax)-2] = RShank_lax[1:len(RShank_lax)-1]
        # RShank_lax[len(RShank_lax)-1] = flat_list[19]
            
        # plt.scatter(range(0,300), RShank_lax)




        sample += 1

        if args.frames > 0:
            num_frames += 1
            if num_frames >= args.frames:
                break
            
def main(argv):
    parser = argparse.ArgumentParser(
        description="")

    parser.add_argument(
        "--file",
        help="output file",
        default="")
    parser.add_argument(
        "--frames",
        help="read N frames",
        type=int, default=0)
    parser.add_argument(
        "--header",
        help="show channel names in the first row",
        action="store_true")
    parser.add_argument(
        "--host",
        help="IP address of the Motion Service",
        default="127.0.0.1")
    parser.add_argument(
        "--port",
        help="port number address of the Motion Service",
        type=int, default=32076)

    args = parser.parse_args()

    if args.file:
        with open(args.file, 'w') as f:
            stream_data_to_csv(args, f)
    else:
        stream_data_to_csv(args, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv))