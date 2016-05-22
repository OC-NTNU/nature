from argh import arg
from py2neo.ext import neobox

from baleen.arghconfig import docstring
from baleen.neo4j import vars_to_csv, neo4j_import, postproc_graph, \
    setup_neo4j_box

from nature.abstract import extract_abstracts
from nature.sent import extract_sent
from nature.brat import make_brat_files, rank_brat_files
from nature.soa import convert_to_soa
from nature.vertical import convert_abs_to_vertical_format
from nature.download import download_webpages
from nature.full import extract_content


@arg('--match-min-n', type=int,
     help='required minimal number of matching keywords')
@arg('--abs-max-n', type=int, help='maximum number of abstracts')
@docstring(extract_abstracts)
def ext_abs(results_file, records_dir, xml_dir,
            match_min_n=None,
            abs_max_n=None):
    extract_abstracts(results_file, records_dir, xml_dir, match_min_n,
                      abs_max_n)


@docstring(extract_sent)
def ext_sent(txt_files, scnlp_dir, sent_dir):
    extract_sent(txt_files, scnlp_dir, sent_dir)


def brat(results_file, sent_dir, brat_dir, brat_rank_dir):
    """Create ranked Brat files for annotation"""
    make_brat_files(sent_dir, brat_dir)
    rank_brat_files(results_file, brat_dir, brat_rank_dir)


@arg('-r', '--resume', help='toggle default value for resuming soa process')
@docstring(convert_to_soa)
def soa(python2, nxml2txt, xml_dir, soa_dir, resume=False):
    convert_to_soa(python2, nxml2txt, xml_dir, soa_dir, resume)


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


@arg('--max-n-htm', type=int)
@arg('--resume', help='toggle default for resuming process')
@docstring(download_webpages)
def download(results_file, htm_dir, max_n_htm=None, resume=False,
             cache_dir=None):
    download_webpages(results_file, htm_dir, max_n_htm, resume, cache_dir)


@docstring(extract_content)
def ext_full(htm_dir, xml_dir):
    extract_content(htm_dir, xml_dir)
