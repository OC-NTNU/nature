#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

import logging as log
from os.path import join

from argh import dispatch, arg

from baleen.arghconfig import setup, add_commands, docstring

from nature.download import download_webpages
from nature.full import extract_content
from nature.soa import convert_to_soa
from nature.scnlp import CoreNLP
from nature.parse import extract_parse_trees, extract_lemmatized_parse_trees
from nature.vertical import convert_full_to_vertical_format
from nature.vars import extract_vars, prune_vars

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
@arg('--resume', action='store_true')
@docstring(download_webpages)
def download(results_file, htm_dir, max_n_htm=None, resume=False,
             cache_dir=None):
    download_webpages(results_file, htm_dir, max_n_htm, resume, cache_dir)


@docstring(extract_content)
def extract(htm_dir, xml_dir):
    extract_content(htm_dir, xml_dir)


@docstring(convert_to_soa)
def soa(nxml2txt, xml_dir, soa_dir):
    convert_to_soa(nxml2txt, xml_dir, soa_dir)


@arg('--threads', type=int)
@arg('--resume', action='store_true')
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
                 resume=True
                 )


def trees(scnlp_dir, word_parse_dir, lemma_parse_dir):
    """Extract lexicalized and lemmatized parse trees"""
    extract_parse_trees(scnlp_dir, word_parse_dir)
    extract_lemmatized_parse_trees(scnlp_dir, lemma_parse_dir)


@docstring(extract_vars)
def extvars(extract_vars_exec, trees_dir,
            vars_file):
    extract_vars(extract_vars_exec, trees_dir, vars_file)


@docstring(prune_vars)
def prunevars(prune_vars_exec, vars_file, pruned_file,
              options=None):
    prune_vars(prune_vars_exec, vars_file, pruned_file, options or "")


pipeline = [download, extract, soa, parse, trees, extvars, prunevars]


def run_all():
    for step in pipeline: step()


run_all.__doc__ = "Run complete  pipeline: {}".format(
        " --> ".join(s.__name__ for s in pipeline))


# -----------------------------------------------------------------------------
# Optional steps   
# -----------------------------------------------------------------------------

@docstring(convert_full_to_vertical_format)
def vertical(scnlp_dir, records_dir, vert_dir):
    convert_full_to_vertical_format(scnlp_dir, records_dir, vert_dir)


optional = [vertical]

# -----------------------------------------------------------------------------
# Argh
# -----------------------------------------------------------------------------

functions = pipeline + optional + [run_all]

add_commands(arg_parser, functions, config, section, prefix=True)

dispatch(arg_parser, argv=left_args)
