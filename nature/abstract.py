
from glob import glob

import json

import pandas as pd

import logging
log = logging.getLogger(__name__)

from nature.utils import make_dir, file_list, new_name


template = ('<?xml version="1.0" encoding="UTF-8"?>'
            "<abstract>\n"
            "<title>\n{title}\n</title>\n"
            "<description>\n{description}\n</description>\n"
            "</abstract>\n" )


def extract_abstracts(rec_files, abs_dir):
    """
    Extract abstracts (title + description) from publication records
    
    rec_files: list or str
        list of filenames, glob pattern or directory containing publications 
        records in json format 
        
    abs_dir: str
        directory for writing abstracts in xml format

    Outputs xml including original html markup, utf-8 encoded.
    """
    make_dir(abs_dir)
        
    for rec_fname in file_list(rec_files, "*.json"):
        entry = json.load(open(rec_fname, "rt"))
        head = entry["sru:recordData"]["pam:message"]["pam:article"]["xhtml:head"]
        title = head["dc:title"]
        description = head["dc:description"]    
        
        if title and description:
            abs_fname = new_name(rec_fname, abs_dir, "#abs.xml")
            with open(abs_fname, "wt") as f:
                log.info("writing abstract to " + abs_fname)
                f.write(template.format(title=title, description=description))
        else:
            log.warn("skipping ill-formed abstract from {}".format(rec_fname))
    
    

    
    
