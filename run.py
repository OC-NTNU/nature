#!/usr/bin/env python

import logging as log
log.basicConfig(level=log.INFO)
#log.basicConfig(level=log.DEBUG)

from tempfile import TemporaryDirectory
from os import getenv

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
from nature.vertical import convert_abs_to_vertical_format, convert_full_to_vertical_format
from nature.full import extract_content
from nature.parse import extract_parse_trees

NXML2TXT = getenv("NXML2TXT", "./nxml2txt_py2")

CORE_NLP = CoreNLP()

TERMS_FILE = "terms.txt"
RESULTS_FILE = "search_results.pkl"
RECORDS_DIR = "records"
HTM_RESULTS_FILE = "search_results.html"

ABS_XML_DIR = "abstracts/xml"
ABS_SOA_DIR = "abstracts/soa"
ABS_SCNLP_DIR = "abstracts/scnlp"
ABS_SENT_DIR = "abstracts/sent"
ABS_BRAT_DIR = "abstracts/brat"
ABS_RANK_DIR = "abstracts/rank"
ABS_PARSE_DIR = "abstracts/parse"
ABS_MATCH_MIN_N = 3

TMP_SCNLP_DIR = "tmp"

FULL_HTM_DIR = "full/htm"
FULL_MAX_N = 10000
FULL_XML_DIR = "full/xml"
FULL_SOA_DIR = "full/soa"
FULL_SCNLP_DIR = "full/scnlp"

BIB_DIR = "bib"

ABS_VERT_DIR = "abstracts/vert"
FULL_VERT_DIR = "full/vert"



def get_text(debug=False, clean=False):
    if debug:        
        n_terms = 3
        max_records = 3 
    else:
        n_terms = None
        max_records = 20000
        
    if clean:
        remove_any(TERMS_FILE,
               RESULTS_FILE,
               RECORDS_DIR,
               HTM_RESULTS_FILE)
        
    get_terms("checked_terms.csv", TERMS_FILE, n_terms=n_terms)
    search_npg(RESULTS_FILE, RECORDS_DIR, TERMS_FILE, max_records=max_records)
    rank_results(RESULTS_FILE)
    results_to_html(RESULTS_FILE, RECORDS_DIR, HTM_RESULTS_FILE)
    
    
def preproc_full(clean=False):
    if clean:
        remove_any(FULL_HTM_DIR)    
        
    ##download_webpages(RESULTS_FILE, FULL_HTM_DIR, FULL_MAX_N)
    ##extract_content(FULL_HTM_DIR, FULL_XML_DIR)
    ##convert_to_soa(NXML2TXT, FULL_XML_DIR, FULL_SOA_DIR)
    CORE_NLP.run(FULL_SOA_DIR + "/*.txt", 
                 FULL_SCNLP_DIR,
                 annotators="tokenize,ssplit,pos,lemma,parse",
                 ##memory="64g",
                 ##threads=16,
                 options=" -ssplit.newlineIsSentenceBreak always",
                 resume=True
                 )
    

    
def preproc_abstracts(clean=False, debug=False):
    if debug:
        abs_max_n=10
    else:
        abs_max_n=None
        
    if clean:
        remove_any(ABS_XML_DIR,
                   BIB_DIR,
                   ABS_SOA_DIR,
                   ABS_SCNLP_DIR,
                   TMP_SCNLP_DIR,
                   ABS_SENT_DIR,
                   ABS_BRAT_DIR,
                   ABS_RANK_DIR)
        
    #extract_abstracts(RESULTS_FILE, RECORDS_DIR, ABS_XML_DIR,
    #                  ABS_MATCH_MIN_N, abs_max_n)
    #lookup_bibtex(ABS_XML_DIR, BIB_DIR)
    #convert_to_soa(NXML2TXT, ABS_XML_DIR, ABS_SOA_DIR)
    CORE_NLP.ssplit(ABS_SOA_DIR + "/*.txt", TMP_SCNLP_DIR)
    split_sent(ABS_SOA_DIR, TMP_SCNLP_DIR, ABS_SENT_DIR)
    CORE_NLP.parse(ABS_SENT_DIR, ABS_SCNLP_DIR)
    make_brat_files(ABS_SENT_DIR, ABS_BRAT_DIR)
    rank_brat_files(RESULTS_FILE, ABS_BRAT_DIR, ABS_RANK_DIR)
    
    
 
def make_vertical_corpus():
    #convert_abs_to_vertical_format(ABS_SCNLP_DIR, RECORDS_DIR, ABS_VERT_DIR)
    convert_full_to_vertical_format(FULL_SCNLP_DIR, RECORDS_DIR, FULL_VERT_DIR)
    
def make_parse_trees():    
    extract_parse_trees(ABS_SCNLP_DIR, ABS_PARSE_DIR)

 
if __name__ == "__main__":
    # in case of rerun:
    # TERMS_FILE = None
    # get_text() #debug=True)
    
    #results_to_html(RESULTS_FILE, RECORDS_DIR, HTM_RESULTS_FILE, None)
    
    preproc_abstracts(clean=False, debug=False)
    #make_vertical_corpus()
    #FULL_HTM_FILES = "full/htm/10.1038#nature*"
    #preproc_full()
    #make_parse_trees()




