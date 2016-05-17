"""
commands shared between abs and full
"""
from argh import arg
from py2neo.ext import neobox

from baleen.arghconfig import docstring
from baleen.neo4j import setup_neo4j_box, neo4j_import, postproc_graph, \
    vars_to_csv
from baleen.vars import add_offsets, extract_vars, preproc_vars, prune_vars
from baleen.scnlp import extract_parse_trees, extract_lemmatized_parse_trees
from nature.soa import convert_to_soa
from nature.vertical import convert_abs_to_vertical_format


# -----------------------------------------------------------------------------
# Pipeline steps
# -----------------------------------------------------------------------------

@arg('-r', '--resume', help='toggle default value for resuming soa process')
@docstring(convert_to_soa)
def soa(python2, nxml2txt, xml_dir, soa_dir, resume=False):
    convert_to_soa(python2, nxml2txt, xml_dir, soa_dir, resume)


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


@docstring(preproc_vars)
def prepvars(trans_exec, in_vars_file, out_vars_file, trans_file, prep_file):
    preproc_vars(trans_exec, in_vars_file, out_vars_file, trans_file, prep_file)


@docstring(add_offsets)
def offsets(in_vars_file, scnlp_dir, out_vars_file):
    add_offsets(in_vars_file, scnlp_dir, out_vars_file)


@docstring(neo4j_import)
def toneo(neobox_home, neobox_name, nodes_dir, relations_dir, options=None):
    neo4j_import(neobox_home, neobox_name, nodes_dir, relations_dir,
                 options=None)


@docstring(postproc_graph)
def ppgraph(neobox_home, neobox_name, neobox_username, neobox_password):
    postproc_graph(neobox_home, neobox_name, neobox_username, neobox_password)


@arg('--max-n-vars', type=int)
@docstring(vars_to_csv)
def tocsv(vars_file, scnlp_dir, sent_dir, bib_dir, nodes_dir,
          relations_dir, max_n_vars=None):
    vars_to_csv(vars_file, scnlp_dir, sent_dir, bib_dir, nodes_dir,
                relations_dir, max_n_vars)


# -----------------------------------------------------------------------------
# Optional steps
# -----------------------------------------------------------------------------

@docstring(setup_neo4j_box)
def setupserver(neobox_home, box_name, edition, version, password):
    setup_neo4j_box(neobox_home, box_name, edition, version, password)


def startserver(neobox_home, box_name):
    """start neo4j server"""
    neobox.Warehouse(neobox_home).box(box_name).server.start()


def stopserver(neobox_home, box_name):
    """stop neo4j server"""
    neobox.Warehouse(neobox_home).box(box_name).server.stop()


@docstring(convert_abs_to_vertical_format)
def vertical(scnlp_dir, records_dir, vert_dir):
    convert_abs_to_vertical_format(scnlp_dir, records_dir, vert_dir)
