#!/usr/bin/env python

"""
run processes to create Nature abstracts corpus
"""

import logging as log
from tempfile import TemporaryDirectory

from argh import dispatch, arg

from baleen.arghconfig import setup, add_commands, docstring, run_commands
from make import setupserver, startserver, stopserver, vertical, soa, trees, \
    extvars, prunevars, offsets, toneo, ppgraph, tocsv
from nature.abstract import extract_abstracts
from nature.brat import make_brat_files, rank_brat_files
from nature.scnlp import CoreNLP
from nature.sent import split_sent

DEFAULT_CONFIG_FILENAME = 'nature-corpus.ini'
DEFAULT_SECTION = 'ABSTRACTS'

arg_parser, config, section, left_args = setup(DEFAULT_CONFIG_FILENAME,
                                               DEFAULT_SECTION)

log.basicConfig(
    level=config.get(section, "LOG_LEVEL", fallback="WARNING"))


# -----------------------------------------------------------------------------
# Pipeline steps   
# -----------------------------------------------------------------------------

@arg('--match-min-n', type=int,
     help='required minimal number of matching keywords')
@arg('--abs-max-n', type=int, help='maximum number of abstracts')
@docstring(extract_abstracts)
def extract(results_file, records_dir, xml_dir,
            match_min_n=None,
            abs_max_n=None):
    extract_abstracts(results_file, records_dir, xml_dir, match_min_n,
                      abs_max_n)


@docstring(split_sent)
def split(soa_dir, sent_dir, corenlp_home, corenlp_ver, tmp_dir=None):
    if not tmp_dir:
        td = TemporaryDirectory()
        tmp_dir = td.name
    core_nlp = CoreNLP(corenlp_home, corenlp_ver)
    core_nlp.ssplit(soa_dir + "/*.txt", tmp_dir)
    split_sent(soa_dir, tmp_dir, sent_dir)


def parse(sent_dir, scnlp_dir, corenlp_home, corenlp_ver):
    """Parse sentences"""
    core_nlp = CoreNLP(corenlp_home, corenlp_ver)
    core_nlp.parse(sent_dir, scnlp_dir)


pipeline = [extract, soa, split, parse, trees, extvars, prunevars, offsets,
            tocsv, toneo, ppgraph]


def run_all():
    run_commands(pipeline)


run_all.__doc__ = "Run complete  pipeline: {}".format(
    " --> ".join(s.__name__ for s in pipeline))

# -----------------------------------------------------------------------------
# Optional steps   
# -----------------------------------------------------------------------------

def brat(results_file, sent_dir, brat_dir, brat_rank_dir):
    """Create ranked Brat files for annotation"""
    make_brat_files(sent_dir, brat_dir)
    rank_brat_files(results_file, brat_dir, brat_rank_dir)


optional = [setupserver, startserver, stopserver, vertical, brat]

# -----------------------------------------------------------------------------
# Argh
# -----------------------------------------------------------------------------

functions = pipeline + optional + [run_all]

add_commands(arg_parser, functions, config, section, prefix=True)

dispatch(arg_parser, argv=left_args)
