#!/usr/bin/env python

"""
run processes to create Nature abstracts corpus
"""

import logging as log
from tempfile import TemporaryDirectory

from argh import add_commands, dispatch, arg

from nature.config import get_parser_and_config, get_option, get_option_int
from nature.abstract import extract_abstracts
from nature.bibtex import lookup_bibtex
from nature.soa import convert_to_soa
from nature.scnlp import CoreNLP
from nature.sent import split_sent
from nature.utils import copy_doc
from nature.brat import make_brat_files, rank_brat_files
from nature.parse import extract_parse_trees, extract_lemmatized_parse_trees
from nature.vertical import convert_abs_to_vertical_format
from nature.vars import extract_vars,prune_vars



DEFAULT_CONFIG_FNAME = "nature-corpus.ini"

parser, cfg = get_parser_and_config(DEFAULT_CONFIG_FNAME)



DEFAULT_SECTION = "ABSTRACTS"    

log.basicConfig(level=cfg.get(DEFAULT_SECTION, "LOG_LEVEL",
                              fallback="WARNING"))

def _(option):
    return get_option(cfg, DEFAULT_SECTION, option)
    
def _i(option):
    return get_option_int(cfg, DEFAULT_SECTION, option)
      
    

#-----------------------------------------------------------------------------    
# Pipeline steps   
#-----------------------------------------------------------------------------    
    
@arg('--match-min-n', type=int, 
     help='required minimal number of matching keywords')
@arg('--abs-max-n', type=int, 
     help='maximum number of abstracts')
def extract(results_fname=_("RESULTS_FILE"),
            rec_dir = _("RECORDS_DIR"),
            abs_dir = _("XML_DIR"),
            match_min_n = _i("MATCH_MIN_N"), 
            abs_max_n = _i("ABS_MAX_N")):
    extract_abstracts(results_fname, rec_dir, abs_dir, match_min_n,
                      abs_max_n)
    
copy_doc(extract_abstracts, extract)
        
    
def soa(nxml2txt=_("NXML2TXT"), 
        xml_dir=_("XML_DIR"), 
        soa_dir=_("SOA_DIR")):
    convert_to_soa(nxml2txt, xml_dir, soa_dir) 
    
copy_doc(convert_to_soa, soa)
    
    
# TODO: pass in other corenlp params
def split(soa_dir=_("SOA_DIR"), 
          sent_dir=_("SENT_DIR"),
          tmp_dir=_("TMP_DIR")):
    if not tmp_dir: 
        td = TemporaryDirectory()
        tmp_dir = td.name
    core_nlp = CoreNLP(lib_dir=_("CORENLP_HOME"),
                       lib_ver=_("CORENLP_VER"))
    core_nlp.ssplit(soa_dir + "/*.txt", tmp_dir)
    split_sent(soa_dir, tmp_dir, sent_dir)
    
copy_doc(split_sent, split)


def parse(sent_dir=_("SENT_DIR"),
          scnlp_dir = _("SCNLP_DIR")): 
    """
    Parse sentences
    """
    core_nlp = CoreNLP(lib_dir=_("CORENLP_HOME"),
                       lib_ver=_("CORENLP_VER"))
    core_nlp.parse(sent_dir, scnlp_dir)

    
def trees(scnlp_dir = _("SCNLP_DIR"),
          word_parse_dir = _("WORD_PARSE_DIR"),
          lemma_parse_dir = _("LEMMA_PARSE_DIR")):
    """
    Extract lexicalized and lemmatized parse trees
    """
    extract_parse_trees(scnlp_dir, word_parse_dir)
    extract_lemmatized_parse_trees(scnlp_dir, lemma_parse_dir)
    
    
def vars(extract_vars_exec=_("EXTRACT_VARS_EXEC"), 
         trees_dir=_("LEMMA_PARSE_DIR"), 
         vars_file=_("VARS_FILE")):
    extract_vars(extract_vars_exec, trees_dir, vars_file)
    
copy_doc(extract_vars, vars)

    
def prune(prune_vars_exec=_("PRUNE_VARS_EXEC"), 
          prune_opts=_("PRUNE_OPTS"),
          vars_file=_("VARS_FILE"),
          pruned_file=_("PRUNED_VARS_FILE"),
          options=_("PRUNE_OPTS")):
    prune_vars(prune_vars_exec, vars_file, pruned_file, prune_opts or "")

copy_doc(prune_vars, prune)


    
steps = [ extract, soa, split, parse, trees, vars, prune]   
    
def run_all():
    for step in steps: step()
    
run_all.__doc__ = "Run complete  pipeline: {}".format(
    " --> ".join(s.__name__ for s in steps))
    
    
#-----------------------------------------------------------------------------    
# Optional steps   
#-----------------------------------------------------------------------------    
    
def bibtex(xml_dir=_("XML_DIR"), 
           bib_dir=_("BIB_DIR")):
    lookup_bibtex(xml_dir, bib_dir)

copy_doc(lookup_bibtex, bibtex)


def brat(results_fname=_("RESULTS_FILE"),
         sent_dir=_("SENT_DIR"),
         brat_dir=_("BRAT_DIR"),
         brat_rank_dir=_("BRAT_RANK_DIR")):
    """
    Create ranked Brat files for annotation
    """
    make_brat_files(sent_dir, brat_dir)
    rank_brat_files(results_fname, brat_dir, brat_rank_dir)
    

    
def vertical(scnlp_dir = _("SCNLP_DIR"),
             records_dir = _("RECORDS_DIR"),
             vert_dir = _("VERT_DIR"),):
    convert_abs_to_vertical_format(scnlp_dir, records_dir, vert_dir)
    
copy_doc(convert_abs_to_vertical_format, vertical)    
    

optional = [brat, bibtex, vertical]



#-----------------------------------------------------------------------------
# Argh
#-----------------------------------------------------------------------------

add_commands(parser, steps + optional + [run_all] )

dispatch(parser)


    
    