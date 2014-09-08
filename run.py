#!/usr/bin/env python

import logging as log
log.basicConfig(level=log.INFO)
#log.basicConfig(level=log.DEBUG)

from tempfile import TemporaryDirectory

from nature.terms import get_terms
from nature.search import search_npg, rank_results, results_to_html
from nature.abstract import extract_abstracts
from nature.download import download_webpages
from nature.utils import remove_any
from nature.soa import convert_to_soa
from nature.scnlp import CoreNLP
from nature.sent import split_sent
from nature.brat import make_brat_files, rank_brat_files
from nature.bibtex import lookup_bibtex

NXML2TXT = '/Users/erwin/Projects/OCEAN-CERTAIN/nature2/nxml2txt_py2'

CORE_NLP = CoreNLP()

TERMS_FILE = "terms.txt"
RESULTS_FILE = "search_results.pkl"
RECORDS_DIR = "records"
HTM_RESULTS_FILE = "search_results.html"

ABS_XML_DIR = "abstracts/xml"
ABS_BIB_DIR = "abstracts/bib"
ABS_SOA_DIR = "abstracts/soa"
ABS_SCNLP_DIR = "abstracts/scnlp"
ABS_SENT_DIR = "abstracts/sent"
ABS_BRAT_DIR = "abstracts/brat"
ABS_RANK_DIR = "abstracts/rank"
ABS_MAX_N = 10000

TMP_SCNLP_DIR = "tmp"

FULL_HTM_DIR = "full/htm"



def get_text(debug=False, clean=False):
    if debug:        
        n_terms = 3
        max_records = 3 
    else:
        n_terms = max_records = None
        
    if clean:
        remove_any(TERMS_FILE,
               RESULTS_FILE,
               RECORDS_DIR,
               HTM_RESULTS_FILE)
        
    get_terms("checked_terms.csv", TERMS_FILE, n_terms=n_terms)
    #search_npg(RESULTS_FILE, RECORDS_DIR, TERMS_FILE, max_records=max_records)
    rank_results(RESULTS_FILE)
    results_to_html(RESULTS_FILE, RECORDS_DIR, HTM_RESULTS_FILE)
    
    
def preproc_full(clean=False):
    if clean:
        remove_any(FULL_HTM_DIR)    
        
    download_webpages(RESULTS_FILE, FULL_HTM_DIR)
    

    
def preproc_abstracts(clean=False, debug=False):
    if debug:
        ABS_MAX_N=10
        
    if clean:
        remove_any(ABS_XML_DIR,
                   ABS_BIB_DIR,
                   ABS_SOA_DIR,
                   ABS_SCNLP_DIR,
                   TMP_SCNLP_DIR,
                   ABS_SENT_DIR,
                   ABS_BRAT_DIR,
                   ABS_RANK_DIR)
        
    extract_abstracts(RESULTS_FILE, RECORDS_DIR, ABS_XML_DIR, ABS_MAX_N)
    #lookup_bibtex(ABS_XML_DIR, ABS_BIB_DIR)
    #convert_to_soa(NXML2TXT, ABS_XML_DIR, ABS_SOA_DIR)
    #CORE_NLP.ssplit(ABS_SOA_DIR + "/*.txt", TMP_SCNLP_DIR)
    #split_sent(ABS_SOA_DIR, TMP_SCNLP_DIR, ABS_SENT_DIR)
    #CORE_NLP.parse(ABS_SENT_DIR, ABS_SCNLP_DIR)
    #make_brat_files(ABS_SENT_DIR, ABS_BRAT_DIR)
    #rank_brat_files(RESULTS_FILE, ABS_BRAT_DIR, ABS_RANK_DIR)
    
    
    

#get_text(debug=True)
preproc_abstracts(clean=False, debug=True)




