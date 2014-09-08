import logging
log = logging.getLogger(__name__)

from os.path import isdir, isfile, splitext, basename, dirname, join
from shutil import rmtree
from os import makedirs, remove
from glob import glob


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
        
        
def file_name(path, max_ext_size=4, extensions=[]):
    """
    Return file's basename (i.e. without directory) and stripped of all
    extensions, optionally limited in size and to those in the list of
    extensions
    """
    name = basename(path)
    parts = name.split(".")
    
    while parts:
        if extensions and parts[-1] not in extensions:
            break
        if len(parts[-1]) > max_ext_size:
            break
        parts.pop()
        
    return ".".join(parts)


def new_name(fname, new_dir=None, new_ext=None, 
             max_ext_size=4, extensions=[]):
    """
    E.g. new_name('/dir1/dir2/file.ext1.ext2', '/dir_3', 'ext3') returns
    '/dir3/file.ext3'
    """
    if new_ext:
        new_name = file_name(fname, max_ext_size, extensions) + new_ext
    else:
        new_name = basename(fname)
        
    return join(new_dir or dirname(fname), new_name)


def file_list(files, file_glob="*"):
    if isinstance(files, str):
        if isdir(files):
            files = join(files, file_glob)
        files = glob(files)
        
    return files
