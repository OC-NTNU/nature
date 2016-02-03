#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

import logging as log
from os.path import join

from argh import dispatch, arg

from baleen.arghconfig import setup, add_commands, docstring, run_commands

from nature.download import download_webpages
from nature.full import extract_content
from nature.scnlp import CoreNLP

from make import setupserver, startserver, stopserver, vertical, soa, trees, \
    extvars, prepvars, prunevars, offsets, toneo, ppgraph, tocsv

DEFAULT_CONFIG_FILENAME = 'nature-corpus.ini'
DEFAULT_SECTION = 'FULL'

arg_parser, config, section, left_args = setup(DEFAULT_CONFIG_FILENAME,
                                               DEFAULT_SECTION)

log.basicConfig(
    level=config.get(section, "LOG_LEVEL", fallback="WARNING"))


# -----------------------------------------------------------------------------
# Pipeline steps   
# -----------------------------------------------------------------------------

@arg('--max-n-htm', type=int)
@arg('--resume', help='toggle default for resuming process')
@docstring(download_webpages)
def download(results_file, htm_dir, max_n_htm=None, resume=False,
             cache_dir=None):
    download_webpages(results_file, htm_dir, max_n_htm, resume, cache_dir)


@docstring(extract_content)
def extract(htm_dir, xml_dir):
    extract_content(htm_dir, xml_dir)


@arg('--threads', type=int)
@arg('--resume', help='toggle default for resuming process')
def parse(soa_dir, scnlp_dir, corenlp_home, corenlp_ver,
          memory='3g',
          threads=1,
          resume=False):
    """Parse sentences"""
    core_nlp = CoreNLP(corenlp_home, corenlp_ver)
    core_nlp.run(join(soa_dir, "*.txt"),
                 scnlp_dir,
                 annotators="tokenize,ssplit,pos,lemma,parse",
                 memory=memory,
                 threads=threads,
                 options=" -ssplit.newlineIsSentenceBreak always -parse.model edu/stanford/nlp/models/srparser/englishSR.beam.ser.gz",
                 resume=resume
                 )


pipeline = [download, extract, soa, parse, trees, extvars, offsets, prepvars,
            prunevars, tocsv, toneo, ppgraph]


def run_all():
    run_commands(pipeline)


run_all.__doc__ = "Run complete  pipeline: {}".format(
    " --> ".join(s.__name__ for s in pipeline))

# -----------------------------------------------------------------------------
# Optional steps   
# -----------------------------------------------------------------------------

optional = [setupserver, startserver, stopserver, vertical]

# -----------------------------------------------------------------------------
# Argh
# -----------------------------------------------------------------------------

functions = pipeline + optional + [run_all]

add_commands(arg_parser, functions, config, section, prefix=True)

dispatch(arg_parser, argv=left_args)
