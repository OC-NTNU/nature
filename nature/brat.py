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
            log.warn("no file " + txt_fname)
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
        
        
        
    
    
    
    

#import pandas as pd
#import re

#def abstracts_to_brat(results_fname, soa_dir, scnlp_dir, brat_dir, 
    #scnlp_ftemplate="{}#{}#abs#corenlp_v3.4.1.xml", 
    #min_n_sent=6):
    #tab = pd.read_pickle(results_fname)
    #n = 0
    
    #:
        #scnlp_fname = join(scnlp_dir,
                           #scnlp_ftemplate.format(doi.split("/")))
        
        #try:
            #scnlp_xml = open(scnlp_fname).read()
        #except FileNotFoundError:
            #log.error(scnlp_fname + " does not exists")
            #continue
            
        #n_sent = len(re.findall("<sentence", scnlp_dir))
        #log.debug("{} contains {} sentences".format(scnlp_fname, n_sent))
        
        #txt_fname = join("brat", doi.replace("/","#") + "#abs.txt")
        #if exists(txt_fname):
            #sent = open(txt_fname).read().split("\n\n")
            #sent = sent[0].split("\n") + sent[1:]
            #if len(sent) >= min_sent:
                #n += 1
                #out_fname = "{:05d}#".format(n) + doi.replace("/","#") + "#abs"
                #with open(join("manual", out_fname + ".txt"), "w") as f:
                    #f.write("\n\n".join(sent))
                #open(join("manual", out_fname + ".ann"), "w") 
                #continue
            
        #print "SKIPPING", txt_fname 
    
    
    
    
    
    