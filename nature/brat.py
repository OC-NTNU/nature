import logging
log = logging.getLogger(__name__)

from shutil import copy 
from os.path import join

import pandas as pd

from nature.utils import make_dir, file_list, new_name


def make_brat_files(sent_files, brat_dir): 
    make_dir(brat_dir)
            
    for sent_fname in file_list(sent_files, "*sent.txt"):
        txt_fname = new_name(sent_fname, brat_dir, "#brat.txt", strip_ext=["txt"])
        ann_fname = new_name(sent_fname, brat_dir, "#brat.ann", strip_ext=["txt"])
        log.info("creating Brat files {} and {}".format(txt_fname, ann_fname))
        copy(sent_fname, txt_fname )
        open(ann_fname, "wt")
        
        
def rank_brat_files(results_fname, brat_dir, rank_dir, min_n_sent=6):
    tab = pd.read_pickle(results_fname)
    make_dir(rank_dir)
    n = 0
    
    for doi in tab.index:
        try:
            prefix, suffix = doi.split("/")
        except ValueError:
            log.warn("Skipping ill-formed DOI: " + doi)
            continue
        
        from_fname_prefix = join(brat_dir, 
                                 "{}#{}#abs#sent#brat".format(prefix, suffix))
        txt_fname = from_fname_prefix + ".txt"
        
        try:
            txt_file = open(txt_fname)
        except IOError:
            log.debug("no file " + txt_fname)
            continue
        
        n_sent = len(txt_file.readlines())
        
        if n_sent < min_n_sent:
            continue
        
        n += 1
        to_fname_prefix = join(rank_dir,
                               "{:05d}#{}#{}#abs#sent#brat".format(n, 
                                                                       prefix, 
                                                                       suffix))
        
        for ext in ".txt", ".ann":
            log.info("creating ranked Brat file " + to_fname_prefix + ext)
            copy(from_fname_prefix + ext, to_fname_prefix + ext)
