#
# @file    sdk/python/MotionSDK.py
# @version 2.6
#
# Copyright (c) 2018, Motion Workshop
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
import argparse
import sys
from xml.etree.ElementTree import XML

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
    xml_string = \
        "<?xml version=\"1.0\"?>" \
        "<configurable inactive=\"1\">" \
        "<Lq/>" \
        "<c/>" \
        "</configurable>"

    if not client.writeData(xml_string):
        raise RuntimeError(
            "failed to send channel list request to Configurable service")

    num_frames = 0
    xml_node_list = None
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
                    "Lqw", "Lqx", "Lqy", "Lqz",
                    "cw", "cx", "cy", "cz"
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

                out.write(
                    ",".join(["{}".format(v) for v in flat_list]))

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

        out.write(
            ",".join(["{}".format(round(v, 8)) for v in flat_list]))

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
