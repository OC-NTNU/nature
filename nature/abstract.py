
from glob import glob

import json

import pandas as pd

import logging
log = logging.getLogger(__name__)

from nature.utils import make_dir, new_name


template = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<abstract>\n"
            "<title>\n{title}\n</title>\n"
            "<description>\n{description}\n</description>\n"
            "</abstract>\n" )


def extract_abstracts(results_fname, rec_dir, abs_dir, abs_max_n):
    """
    Extract abstracts (title + description) from publication records
    
    results_fname: str
        file with search results (.pkl)    
    
    rec_dir: str
        directory containing publication records json format
        
    abs_dir: str
        directory for writing abstracts in xml format
        
    abs_max_n: int
        maximum number of abstracts

    Outputs xml including original html markup, utf-8 encoded.
    """    
    make_dir(abs_dir)
    tab = pd.read_pickle(results_fname)  
    
    for doi in tab.index[:abs_max_n]:
        doi = doi.replace("/", "#")
        rec_fname = new_name(doi, rec_dir, ".json", max_ext_size=0)
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
    
    

    
    
