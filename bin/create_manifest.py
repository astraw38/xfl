#!/usr/local/bin/python
import os
from xfl import DirTree
from os import sys

import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file",
                        dest="filename",
                        help="Write to specific XML file",
                        default="{0}_file_digest.xml".format(sys.platform))
    parser.add_argument("-p", "--path",
                        dest="path",
                        help="Specific path to parse out, defaults to current directory",
                        default=os.getcwd())
    parser.add_argument("--hash",
                        dest="hash_type",
                        help="Choose a hashing mode (leave blank for none): MD5 or SHA1",
                        default=None)

    args = parser.parse_args()

    hasher = None
    if args.hash_type is None:
        hasher = None
    else:
        import hashlib
        if args.hash_type.upper() == 'SHA1':
            hasher = hashlib.sha1()
        if args.hash_type.upper() == 'MD5':
            hasher = hashlib.md5()

    dt = DirTree()
    print "Creating directory list: {0}".format(args.path)
    dt.read_disk(args.path, hasher=hasher)
    print "Writing to file: %s" % (args.filename)
    dt.write_file(args.filename)
    print "Done!"
    del dt
