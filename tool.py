#!/usr/bin/env python3

"""
MIT License

Copyright (c) 2023 MINETA "m10i" Hiroki & Ragnarok Online Japan デベロッパー

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import gzip
import json
import os
import struct
import sys


parser = argparse.ArgumentParser(description='Extract Ragnarok GZ(rgz) file')

parser.add_argument("-j", "--json-output",
                    action="store_true",
                    default=False,
                    help="Output STDOUT JSON formant")

parser.add_argument("-f", "--filename",
                    action="store",
                    default=None,
                    help="File name")

parser.add_argument("-e", "--extract-filepath",
                    action="store",
                    default=None,
                    help="Extract file path")

parser.add_argument("rgzfile",
                    action="store",
                    default=None,
                    type=str,
                    help="Ragnarok GZ file")

args = parser.parse_args()

def main(args):
    raw_contents = None

    with gzip.open(args.rgzfile, mode="rb") as fp:
        raw_contents = fp.read()

    raw_contents_length: int = len(raw_contents)

    if raw_contents_length == 0:
        return

    idx: int = 0
    directory: str = None
    filename: str = None

    output_json: list = []

    while idx < (raw_contents_length -1):
        data = "{:X}".format(struct.unpack_from("<B", raw_contents[idx:(idx+1)])[0])
        if data == "64":
            # Flag:d = Directory
            length: int = int(struct.unpack_from("<B", raw_contents[(idx+1):(idx+2)])[0])
            #print(f"Flag:Directory, length:{length:d}")

            directory: str = str(raw_contents[(idx+2):(idx+2+length)], encoding="shift-jis", errors="ignore").split("\0")[0]
            #print(f"directory:{directory}")

            idx += (2+length)

        elif filename is None and data == "66":
            # Flag:f = File
            length: int = int(struct.unpack_from("<B", raw_contents[(idx+1):(idx+2)])[0])
            #print(f"Flagh:File, length:{length:d}")

            filename: str = str(raw_contents[(idx+2):(idx+2+length)], encoding="shift-jis", errors="ignore").split("\0")[0]
            filename = filename.replace("\\","/")
            if args.json_output == True:
                output_json.append(filename)
            elif args.filename is None:
                print(f"filename:{filename}")

            idx += (2+length)

        elif filename is None and data == "65":
            # Flag:e = End
            length: int = int(struct.unpack_from("<B", raw_contents[(idx+1):(idx+2)])[0])
            #print(f"Flagh:End, length:{length:d}")

            filename: str = str(raw_contents[(idx+2):(idx+2+length)], encoding="shift-jis", errors="ignore").split("\0")[0]
            filename = filename.replace("\\","/")
            #print(f"filename:{filename}")

            # Initialize
            directory = None
            filename = None
            break

        elif directory is not None and filename is not None:
            length: int = int(struct.unpack_from("<I", raw_contents[idx:(idx+4)])[0])
            #print(f"length:{length:,d}")

            if filename == args.filename and args.extract_filepath is not None:
                filepath = os.path.abspath(args.extract_filepath)

                if os.path.exists(filepath) == True:
                    print("[ERROR]", "file is exists.")
                    sys.exit(1)

                dirpath: str = os.path.dirname(filepath)
                if os.path.isdir(dirpath) == False:
                    print("[ERROR]", "extract failed.")
                    sys.exit(1)

                with open(filepath, mode="wb") as fp:
                    fp.write(raw_contents[(idx+4):(idx+4+length)])

            idx += (4+length)

            # Initialize
            filename = None

        else:
            idx += 1

    if args.json_output == True:
        print(json.dumps(output_json))

if __name__ == '__main__':
    main(args)
