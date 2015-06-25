#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

import logging as log
from os.path import join

from argh import add_commands, dispatch, arg

from nature.config import ( get_parser_and_config, get_option,
                            get_option_int, get_option_bool)
from nature.download import download_webpages
from nature.full import extract_content
from nature.soa import convert_to_soa
from nature.scnlp import CoreNLP
from nature.utils import copy_doc
from nature.parse import extract_parse_trees, extract_lemmatized_parse_trees
from nature.vertical import convert_full_to_vertical_format
from nature.vars import extract_vars,prune_vars



DEFAULT_CONFIG_FNAME = "nature-corpus.ini"


parser, cfg = get_parser_and_config(DEFAULT_CONFIG_FNAME)



DEFAULT_SECTION = "FULL"    

log.basicConfig(level=cfg.get(DEFAULT_SECTION, "LOG_LEVEL",
                              fallback="WARNING"))

def _(option):
    return get_option(cfg, DEFAULT_SECTION, option)
    
def _i(option):
    return get_option_int(cfg, DEFAULT_SECTION, option)
      
def _b(option):
    return get_option_bool(cfg, DEFAULT_SECTION, option)

    
#-----------------------------------------------------------------------------    
# Pipeline steps   
#----------------------------------------------------------------------------- 

def download(results_fname=_("RESULTS_FILE"),
             htm_dir=_("HTM_DIR"),
             max_n_htm=_i("MAX_N_HTM"),
             resume=_b("HTM_RESUME"),
             cache_dir=_("HTM_CACHE_DIR")):
    download_webpages(results_fname, htm_dir, max_n_htm, resume, cache_dir)
    
    
copy_doc(download_webpages, download)    
    
    
def extract(htm_dir=_("HTM_DIR"),
            xml_dir=_("XML_DIR")):    
    extract_content(htm_dir, xml_dir)
    
copy_doc(extract_content, extract)


def soa(nxml2txt=_("NXML2TXT"),         
        xml_dir=_("XML_DIR"),
        soa_dir=_("SOA_DIR")):
    convert_to_soa(nxml2txt, xml_dir, soa_dir)
    
copy_doc(convert_to_soa, soa)    


def parse(soa_dir=_("SOA_DIR"),
          scnlp_dir = _("SCNLP_DIR"),
          memory=_("CORENLP_MEMORY"),
          threads=_i("CORENLP_THREADS"),
          resume=_b("CORENLP_RESUME")): 
    """
    Parse sentences
    """
    core_nlp = CoreNLP(lib_dir=_("CORENLP_HOME"),
                       lib_ver=_("CORENLP_VER")) 
    core_nlp.run(join(soa_dir, "*.txt"), 
                 scnlp_dir,
                 annotators="tokenize,ssplit,pos,lemma,parse",
                 memory=memory,
                 threads=threads,
                 options=" -ssplit.newlineIsSentenceBreak always -parse.model edu/stanford/nlp/models/srparser/englishSR.beam.ser.gz",
                 resume=True
                 )


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


steps = [download, extract, soa, parse, trees, vars, prune]   
    
def run_all():
    for step in steps: step()
    
run_all.__doc__ = "Run complete  pipeline: {}".format(
    " --> ".join(s.__name__ for s in steps))


#-----------------------------------------------------------------------------    
# Optional steps   
#-----------------------------------------------------------------------------   
    
def vertical(scnlp_dir = _("SCNLP_DIR"),
             records_dir = _("RECORDS_DIR"),
             vert_dir = _("VERT_DIR"),):
    convert_full_to_vertical_format(scnlp_dir, records_dir, vert_dir)
    
copy_doc(convert_full_to_vertical_format, vertical)    

    
optional = [vertical]
            

#-----------------------------------------------------------------------------
# Argh
#-----------------------------------------------------------------------------
    
add_commands(parser, steps + optional + [run_all] )

dispatch(parser)