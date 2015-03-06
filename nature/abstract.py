
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


def extract_abstracts(results_fname, rec_dir, abs_dir, match_min_n=1, abs_max_n=None):
    """
    Extract abstracts (title + description) from publication records
    
    results_fname: str
        file with search results (.pkl)    
    
    rec_dir: str
        directory containing publication records json format
        
    abs_dir: str
        directory for writing abstracts in xml format
        
    match_min_n: int or None
        required minimal number of matching keywords
        
    abs_max_n: int or None
        maximum number of abstracts

    Outputs xml including original html markup, utf-8 encoded.
    """    
    make_dir(abs_dir)
    tab = pd.read_pickle(results_fname)
    
    for doi, row in tab[:abs_max_n].iterrows():
        if row.sum() < match_min_n:
            break
        
        doi = doi.replace("/", "#")
        rec_fname = new_name(doi, rec_dir, ".json", strip_ext=[""])
        entry = json.load(open(rec_fname, "rt"))
        head = entry["sru:recordData"]["pam:message"]["pam:article"]["xhtml:head"]
        title = head["dc:title"]
        description = head["dc:description"]    
        
        if title and description:
            abs_fname = new_name(rec_fname, abs_dir, "#abs.xml", strip_ext=["json"])
            with open(abs_fname, "wt") as f:
                log.info("writing abstract to " + abs_fname)
                f.write(template.format(
                    title=title, 
                    description=description))
        else:
            log.warn("skipping ill-formed abstract from {}".format(rec_fname))
    
    

    
    
