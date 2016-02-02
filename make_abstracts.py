#!/usr/bin/env python

"""
run processes to create Nature abstracts corpus
"""

import logging as log
from tempfile import TemporaryDirectory

from argh import dispatch, arg
from py2neo.ext import neobox

from baleen.arghconfig import setup, add_commands, docstring, run_commands
from baleen.neo4j import setup_neo4j_box, vars_to_csv, neo4j_import, \
    postproc_graph
from baleen.vars import add_offsets

from nature.abstract import extract_abstracts
from nature.bibtex import lookup_bibtex
from nature.soa import convert_to_soa
from nature.scnlp import CoreNLP
from nature.sent import split_sent
from nature.brat import make_brat_files, rank_brat_files
from nature.parse import extract_parse_trees, extract_lemmatized_parse_trees
from nature.vertical import convert_abs_to_vertical_format
from nature.vars import extract_vars, prune_vars

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


@arg('-r', '--resume', help='toggle default value for resuming soa process')
@docstring(convert_to_soa)
def soa(python2, nxml2txt, xml_dir, soa_dir, resume=False):
    convert_to_soa(python2, nxml2txt, xml_dir, soa_dir, resume)


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


def trees(scnlp_dir, word_parse_dir, lemma_parse_dir):
    """Extract lexicalized and lemmatized parse trees"""
    extract_parse_trees(scnlp_dir, word_parse_dir)
    extract_lemmatized_parse_trees(scnlp_dir, lemma_parse_dir)


@docstring(extract_vars)
def extvars(extract_vars_exec, trees_dir, vars_file):
    extract_vars(extract_vars_exec, trees_dir, vars_file)


@docstring(prune_vars)
def prunevars(prune_vars_exec, vars_file, pruned_file,
              options=None):
    prune_vars(prune_vars_exec, vars_file, pruned_file, options or "")


@docstring(add_offsets)
def offsets(in_vars_file, scnlp_dir, out_vars_file):
    add_offsets(in_vars_file, scnlp_dir, out_vars_file)


@arg('--max-n-vars', type=int)
@docstring(vars_to_csv)
def tocsv(vars_file, scnlp_dir, sent_dir, bib_dir, nodes_dir,
          relations_dir, max_n_vars=None):
    vars_to_csv(vars_file, scnlp_dir, sent_dir, bib_dir, nodes_dir,
                relations_dir, max_n_vars)


@docstring(neo4j_import)
def toneo(neobox_home, neobox_name, nodes_dir, relations_dir, options=None):
    neo4j_import(neobox_home, neobox_name, nodes_dir, relations_dir,
                 options=None)


@docstring(postproc_graph)
def ppgraph(neobox_home, neobox_name, neobox_username, neobox_password):
    postproc_graph(neobox_home, neobox_name, neobox_username, neobox_password)


pipeline = [extract, soa, split, parse, trees, extvars, prunevars, offsets,
            tocsv, toneo, ppgraph]


def run_all():
    run_commands(pipeline)


run_all.__doc__ = "Run complete  pipeline: {}".format(
    " --> ".join(s.__name__ for s in pipeline))


# -----------------------------------------------------------------------------
# Optional steps   
# -----------------------------------------------------------------------------


@docstring(setup_neo4j_box)
def setup_neo4j(neobox_home, box_name, edition, version, password):
    setup_neo4j_box(neobox_home, box_name, edition, version, password)


def startserver(neobox_home, box_name):
    """start neo4j server"""
    neobox.Warehouse(neobox_home).box(box_name).server.start()


def stopserver(neobox_home, box_name):
    """stop neo4j server"""
    neobox.Warehouse(neobox_home).box(box_name).server.stop()


@docstring(lookup_bibtex)
def bibtex(xml_dir, bib_dir):
    lookup_bibtex(xml_dir, bib_dir)


def brat(results_file, sent_dir, brat_dir, brat_rank_dir):
    """Create ranked Brat files for annotation"""
    make_brat_files(sent_dir, brat_dir)
    rank_brat_files(results_file, brat_dir, brat_rank_dir)


@docstring(convert_abs_to_vertical_format)
def vertical(scnlp_dir, records_dir, vert_dir):
    convert_abs_to_vertical_format(scnlp_dir, records_dir, vert_dir)


optional = [setup_neo4j, startserver, stopserver, bibtex, vertical]

# -----------------------------------------------------------------------------
# Argh
# -----------------------------------------------------------------------------

functions = pipeline + optional + [run_all]

add_commands(arg_parser, functions, config, section, prefix=True)

dispatch(arg_parser, argv=left_args)
