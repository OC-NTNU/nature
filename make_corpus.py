#!/usr/bin/env python

"""
run initial steps to create Nature corpus
"""

from argh import arg

from baleen.arghconfig import docstring
from baleen.pipeline import script
from baleen.steps import clean

from nature.terms import get_terms
from nature.search import search_npg, rank_results, results_to_html
from nature.bibtex import lookup_bibtex


# -----------------------------------------------------------------------------
# Pipeline steps
# -----------------------------------------------------------------------------

@arg("--max-n-records", type=int)
@docstring(search_npg)
def search(results_file, records_dir, terms_file,
           max_n_records=None,
           resume=False):
    search_npg(results_file, records_dir, terms_file, max_n_records, resume)


@docstring(lookup_bibtex)
@arg('--resume', help='toggle default value for resuming')
def bibtex(records_dir, bib_dir, resume=False):
    lookup_bibtex(records_dir, bib_dir, resume=resume)


@docstring(rank_results)
def rank(results_file):
    rank_results(results_file)


@arg("--max-n-records", type=int)
@docstring(results_to_html)
def html(search_results_file, records_dir, results_file,
         max_n_records=None):
    results_to_html(search_results_file, records_dir, results_file,
                    max_n_records)


# -----------------------------------------------------------------------------
# Optional steps
# -----------------------------------------------------------------------------

@arg("--max-n", type=int)
@docstring(get_terms)
def terms(csv_file, results_file, max_n=None):
    get_terms(csv_file, results_file, max_n)


script(steps=[search, bibtex, rank, html],
       optional=[terms, clean],
       default_cfg_fnames=['nature-corpus.ini'])
