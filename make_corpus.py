#!/usr/bin/env python

"""
run initial steps to create Nature corpus
"""

import logging as log

from argh import dispatch, arg

from baleen.arghconfig import setup, add_commands, docstring
from nature.terms import get_terms
from nature.search import search_npg, rank_results, results_to_html

DEFAULT_CONFIG_FILENAME = 'nature-corpus.ini'
DEFAULT_SECTION = 'DEFAULT'

arg_parser, config, section, left_args = setup(DEFAULT_CONFIG_FILENAME,
                                               DEFAULT_SECTION)

log.basicConfig(
        level=config.get(section, "LOG_LEVEL", fallback="WARNING"))


# -----------------------------------------------------------------------------
# Pipeline steps
# -----------------------------------------------------------------------------

@arg("--max-n-records", type=int)
@docstring(search_npg)
def search(results_file, records_dir, terms_file,
           max_n_records=None,
           resume=False):
    search_npg(results_file, records_dir, terms_file, max_n_records, resume)


@docstring(rank_results)
def rank(results_file):
    rank_results(results_file)


@arg("--max-n-records", type=int)
@docstring(results_to_html)
def html(search_results_file, records_dir, results_file,
         max_n_records=None):
    results_to_html(search_results_file, records_dir, results_file,
                    max_n_records)


pipeline = [search, rank, html]


def run_all():
    for step in pipeline: step()


run_all.__doc__ = "Run complete  pipeline: {}".format(
        " --> ".join(s.__name__ for s in pipeline))


# -----------------------------------------------------------------------------
# Optional steps
# -----------------------------------------------------------------------------


@arg("--max-n", type=int)
@docstring(get_terms)
def terms(csv_file, results_file, max_n=None):
    get_terms(csv_file, results_file, max_n)


optional = [terms]

# -----------------------------------------------------------------------------
# Argh
# -----------------------------------------------------------------------------

functions = pipeline + optional + [run_all]

add_commands(arg_parser, functions, config, section, prefix=True)

dispatch(arg_parser, argv=left_args)
