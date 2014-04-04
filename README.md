xfl
===

Python directory and file manifests


Reads in directory information into an ElementTree, then you can compare it with another directory (or with an XML file you've created - either with DirTree().write_file() or create_manifest.py). 

Very useful if you want to verify installations against a baseline (like in a test environment). 

Requires: path.py, hashlib

Was originally from http://www.decalage.info/python/xfl, I've modified it a bit and added file hash support. 


create_manifest.py --help
usage: create_manifest.py [-h] [-f FILENAME] [-p PATH] [--hash HASH_TYPE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --file FILENAME
                        Write to specific XML file
  -p PATH, --path PATH  Specific path to parse out, defaults to current
                        directory
  --hash HASH_TYPE      Choose a hashing mode (optional): MD5 or
                        SHA1
