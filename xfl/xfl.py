#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
XFL - XML File List v0.06 2008-02-06 - Philippe Lagadec

A module to store directory trees and file information in XML
files, and to track changes in files and directories.

Project website: http://www.decalage.info/python/xfl

License: CeCILL v2, open-source (GPL compatible)
         see http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
"""

#------------------------------------------------------------------------------
# CHANGELOG:
# 2006-08-04 v0.01 PL: - 1st version
# 2006-06-08 v0.03 PL
# 2007-08-15 v0.04 PL: - improved dir callback
# 2007-08-15 v0.05 PL: - added file callback, added element to callbacks
# 2008-02-06 v0.06 PL: - first public release

#------------------------------------------------------------------------------
# TODO:
# + store timestamps with XML-Schema dateTime format
# - options to store owner
# + add simple methods like isfile, isdir, which take a path as arg
# + handle exceptions file-by-file and store them in the XML
# ? replace callback functions by DirTree methods which may be overloaded ?
# - allow callback functions for dirs and files (path + object)
# - DirTree options to handle owner, hash, ...

#--- IMPORTS ------------------------------------------------------------------
import logging
import sys

# path module to easily handle files and dirs:
try:
    from path import path
except:
    raise ImportError("the path module is not installed: "
                      "see http://www.jorendorff.com/articles/python/path/")

### import LXML for pythonic XML:
##try:
##    import lxml.etree as ET
##except:
##    raise ImportError, "You must install lxml: http://codespeak.net/lxml"

# ElementTree for pythonic XML:
try:
    if sys.hexversion >= 0x02050000:
        # ElementTree is included in the standard library since Python 2.5
        import xml.etree.ElementTree as ET
    else:
        # external ElemenTree for Python <=2.4
        import elementtree.ElementTree as ET
except:
    raise ImportError, "the ElementTree module is not installed: " \
                       + "see http://effbot.org/zone/element-index.htm"

#--- CONSTANTS ----------------------------------------------------------------

# XML tags
TAG_DIRTREE = "dirtree"
TAG_DIR = "dir"
TAG_FILE = "file"

# XML attributes
ATTR_NAME = "name"
ATTR_TIME = "time"
ATTR_MTIME = "mtime"
ATTR_SIZE = "size"
ATTR_OWNER = "owner"
ATTR_HASH = 'hash'

#Hash consts
BLOCKSIZE = 65536

#--- CLASSES ------------------------------------------------------------------


class DirTree:
    """
    class representing a tree of directories and files,
    that can be written or read from an XML file.
    """

    def __init__(self, rootpath=""):
        """
        DirTree constructor.
        """
        self.rootpath = path(rootpath)

    def read_disk(self, rootpath=None, callback_dir=None, callback_file=None, hasher=None):
        """
        to read the DirTree from the disk.
        """
        # creation of the root ElementTree:
        self.et = ET.Element(TAG_DIRTREE)
        if rootpath:
            self.rootpath = path(rootpath)
            # name attribute = rootpath
        self.et.set(ATTR_NAME, self.rootpath)
        # time attribute = time of scan
        #self.et.set(ATTR_TIME, str(time.time()))
        self._scan_dir(self.rootpath, self.et, callback_dir, callback_file, hasher)

    def _scan_dir(self, directory, parent, callback_dir=None, callback_file=None, hasher=None):
        """
        to scan a directory on the disk (recursive scan).
        (this is a private method)
        """
        if callback_dir:
            callback_dir(directory, parent)
        for f in directory.files():
            e = ET.SubElement(parent, TAG_FILE)
            e.set(ATTR_NAME, f.name)
            e.set(ATTR_SIZE, str(f.getsize()))

            if hasher is not None:
                e.set(ATTR_HASH, self._get_file_hash(f, hasher))

            try:
                e.set(ATTR_OWNER, f.get_owner())
            except:
                pass
            if callback_file:
                callback_file(f, e)
        for d in directory.dirs():
            #print d
            e = ET.SubElement(parent, TAG_DIR)
            e.set(ATTR_NAME, d.name)
            self._scan_dir(d, e, callback_dir, callback_file, hasher)

    def write_file(self, filename, encoding="utf-8"):
        """
        to write the DirTree in an XML file.
        """
        indent(self.et)
        tree = ET.ElementTree(self.et)
        tree.write(filename, encoding)

    def read_file(self, filename):
        """
        to read the DirTree from an XML file.
        """
        tree = ET.parse(filename)
        self.et = tree.getroot()
        self.rootpath = self.et.get(ATTR_NAME)

    def pathdict(self):
        """
        to create a dictionary which indexex all objects by their paths.
        """
        self.dict = {}
        self._pathdict_dir(path(""), self.et)

    def _pathdict_dir(self, base, et):
        """
        (private method)
        """
        dirs = et.findall(TAG_DIR)
        for d in dirs:
            dpath = base / d.get(ATTR_NAME)
            self.dict[dpath] = d
            self._pathdict_dir(dpath, d)
        files = et.findall(TAG_FILE)
        for f in files:
            fpath = base / f.get(ATTR_NAME)
            self.dict[fpath] = f


    def _get_file_hash(self, file_name, hasher):
        """

        :param file_name:
        :param hasher:
        :return:
        """
        with open(file_name, 'rb') as current_file:
            buf = current_file.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = current_file.read(BLOCKSIZE)

        return hasher.hexdigest()


#--- FUNCTIONS ----------------------------------------------------------------

def compare_files(et1, et2):
    """
    to compare two files or dirs.
    returns True if files/dirs information are identical,
    False otherwise.
    """
    if et1.tag != et2.tag:
        return False
    if et1.tag == TAG_DIR:
        if et1.get(ATTR_NAME) != et2.get(ATTR_NAME):
            print ("Directory name verification failed: {0} != {1}".format(et1.get(ATTR_NAME), et2.get(ATTR_NAME)))
            return False
        else:
            return True
    elif et1.tag == TAG_FILE:
        if et1.get(ATTR_NAME) != et2.get(ATTR_NAME):
            #Compare names
            print ("File name verification failed: {0} != {1}".format(et1.get(ATTR_NAME), et2.get(ATTR_NAME)))
            return False
        if et1.get(ATTR_SIZE) != et2.get(ATTR_SIZE):
            #Compare sizes
            print ("File {0} failed size verification".format(et1.get(ATTR_NAME)))
            return False
        if et1.get(ATTR_HASH) != et2.get(ATTR_HASH):
            #Compare file hash (if the one has a hash and the other does not, it'll return false)
            print ("File {0} failed hash verification".format(et1.get(ATTR_NAME)))
            return False
        else:
            return True
    else:
        raise TypeError


def comp_filesv2(tree1, tree2, values=None, log=None):
    """
    Compares 2 tree elements.

    :param tree1:
    :param tree2:
    :param values: List of what to check.
        Default: ATTR_NAME, ATTR_HASH, ATTR_SIZE
    :param log: Logger. Defaults to logging.getLogger(__name__)
    :return:
    """
    if log is None:
        #Default to root logger.
        log = logging.getLogger()

    if values is None:
        #Default to checking name, size, and hash.
        values = [ATTR_NAME, ATTR_HASH, ATTR_SIZE]
    else:
        for value in values:
            #Check to make sure that the list of values is valid.
            if value not in [ATTR_SIZE, ATTR_HASH, ATTR_NAME, ATTR_MTIME, ATTR_OWNER, ATTR_TIME]:
                raise TypeError("Checking value %s is INVALID" % value)

    if tree1.tag != tree2.tag:
        return False

    if tree1.tag == TAG_DIR:
        #Means this is a directory, compare names.
        if tree1.get(ATTR_NAME) != tree2.get(ATTR_NAME):
            log.info("Directory name verification failed: %s != %s", tree1.get(ATTR_NAME), tree2.get(ATTR_NAME))
            return False
        else:
            return True
    elif tree1.tag == TAG_FILE:
        #Tagged as a file
        ret_value = True
        for value in values:
            #If any one of these checks fails, the whole thing fails.
            if tree1.get(value) != tree2.get(value):
                log.info("%s verification failed: %s != %s", value, tree1.get(value), tree2.get(value))
                ret_value = False

        return ret_value


def compare_DT(dirTree1, dirTree2, values=None, log=None):
    """
    to compare two DirTrees, and report which files have changed.
    returns a tuple of 4 lists of paths: same files, different files,
    files only in dt1, files only in dt2.
    """
    same = []
    different = []
    only1 = []
    only2 = []
    dirTree1.pathdict()
    dirTree2.pathdict()
    paths1 = dirTree1.dict.keys()
    paths2 = dirTree2.dict.keys()
    for p in paths1:
        if p in paths2:
            # path is in the 2 DT, we have to compare file info
            f1 = dirTree1.dict[p]
            f2 = dirTree2.dict[p]
            if comp_filesv2(f1, f2, values, log):
                # files/dirs are the same
                same.append(p)
            else:
                different.append(p)
            paths2.remove(p)
        else:
            only1.append(p)
            # now paths2 should contain only files and dirs that weren't in paths1
    only2 = paths2
    return same, different, only1, only2


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def callback_dir_print(dir, element):
    """
    sample callback function to print dir path.
    """
    print dir


def callback_file_print(file, element):
    """
    sample callback function to print file path.
    """
    print " - " + file


#--- MAIN ---------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print __doc__
        print "usage: python %s <root path> <xml file> [previous xml file]" % path(sys.argv[0]).name
        sys.exit(1)
    d = DirTree()
    d.read_disk(sys.argv[1], callback_dir_print, callback_file_print)
    d.write_file(sys.argv[2])
    if len(sys.argv) > 3:
        d2 = DirTree()
        d2.read_file(sys.argv[3])
        same, different, only1, only2 = compare_DT(d, d2)
        ##    print "\nSAME:"
        ##    for f in sorted(same):
        ##        print "  "+f
        print "\nDIFFERENT:"
        for f in sorted(different):
            print "  " + f
        print "\nNEW:"
        for f in sorted(only1):
            print "  " + f
        print "\nDELETED:"
        for f in sorted(only2):
            print "  " + f



