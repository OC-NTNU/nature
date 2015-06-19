#!/usr/bin/env python

"""
run initial steps to create Nature corpus
"""

import logging as log
from tempfile import TemporaryDirectory

from argh import add_commands, dispatch, arg

from nature.config import get_parser_and_config, get_option, get_option_int
from nature.utils import copy_doc
from nature.terms import get_terms
from nature.search import search_npg, rank_results, results_to_html


DEFAULT_CONFIG_FNAME = "nature-corpus.ini"

parser, cfg = get_parser_and_config(DEFAULT_CONFIG_FNAME)

log.basicConfig(level=cfg.get("ABSTRACTS", "LOG_LEVEL", fallback="WARNING"))


DEFAULT_SECTION = "DEFAULT"

def _(option):
    return get_option(cfg, DEFAULT_SECTION, option)
    
def _i(option):
    return get_option_int(cfg, DEFAULT_SECTION, option)
    

  
@arg("--terms-n", type=int)
def terms(terms_csv_file = _("TERMS_CSV_FILE"), 
          terms_file = _("TERMS_FILE"), 
          terms_n = _i("TERMS_N")):
    
    get_terms(terms_csv_file, terms_file, terms_n)
    
copy_doc(get_terms, terms)


@arg("--max-n-records", type=int)
def search(results_file = _("RESULTS_FILE"),
           records_dir = _("RECORDS_DIR"),
           terms_file = _("TERMS_FILE"),
           max_n_records = _i("MAX_N_RECORDS")):
    search_npg(results_file, records_dir, terms_file, max_n_records)

copy_doc(search_npg, search)


def rank(results_file = _("RESULTS_FILE")):
    rank_results(results_file)
    
copy_doc(rank_results, rank)
    

def html(results_file = _("RESULTS_FILE"),
         records_dir = _("RECORDS_DIR"),
         html_result_file = _("HTML_RESULTS_FILE"),
         html_max_n_records = _i("HTML_MAX_N_RECORDS")):
    results_to_html(results_file, records_dir, html_result_file,
                    html_max_n_records)

copy_doc(results_to_html, html)

steps = [terms, search, rank, html]


def run_all():
    for step in steps: step()
    
run_all.__doc__ = "Run complete  pipeline: {}".format(
    " --> ".join(s.__name__ for s in steps))

    
add_commands(parser, steps + [run_all] )

dispatch(parser)