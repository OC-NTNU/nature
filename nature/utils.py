import logging
log = logging.getLogger(__name__)

from os.path import isdir, isfile, splitext, basename, dirname, join
from shutil import rmtree
from os import makedirs, remove
from glob import glob

from lxml.etree import fromstring, tostring


def remove_any(*files):
    """
    remove any file or directory - no questions asked
    """
    for f in files:
        if isfile(f):
            remove(f)
            log.info("removed file {!r}".format(f))
        elif isdir(f):
            rmtree(f)
            log.info("removed directory {!r}".format(f))
            

def make_dir(path):
    """
    make dir if it does not exists
    """
    if not isdir(path):
        log.info("creating dir {!r}".format(path))
        makedirs(path)
        
        
def file_name(path, max_ext_size=4, strip_ext=[]):
    """
    Return file's basename (i.e. without directory) and stripped of all
    extensions, optionally limited in size and/or to those in the list strip_ext
    """
    name = basename(path)
    parts = name.split(".")
    
    while parts:
        if strip_ext and parts[-1] not in strip_ext:
            break
        if len(parts[-1]) > max_ext_size:
            break
        parts.pop()
        
    return ".".join(parts)


def new_name(fname, new_dir=None, new_ext=None, 
             max_ext_size=4, strip_ext=[]):
    """
    E.g. new_name('/dir1/dir2/file.ext1.ext2', '/dir_3', 'ext3') returns
    '/dir3/file.ext3'
    """
    if new_ext:
        new_name = file_name(fname, max_ext_size, strip_ext) + new_ext
    else:
        new_name = basename(fname)
        
    return join(new_dir or dirname(fname), new_name)


def file_list(files, file_glob="*"):
    if isinstance(files, str):
        if isdir(files):
            files = join(files, file_glob)
        files = glob(files)
        
    return files


def strip_xml(s):
    """
    strip all xml tags 
    """
    return tostring(fromstring("<x>" + s + "</x>"), method="text", encoding=str)
    
    