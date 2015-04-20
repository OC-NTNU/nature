"""
Stanford CoreNLP parse trees
"""

from lxml.etree import ElementTree

from nature.utils import make_dir, file_list, new_name

import logging
log = logging.getLogger(__name__)


def extract_parse_trees(scnlp_files, parse_dir):
    """
    extract parse trees (PTB labeled bracket structures) from Stanford
    CoreNLP XML ouput
    """
    make_dir(parse_dir)
        
    for scnlp_fname in file_list(scnlp_files, "*.xml"):
        nlp_doc = ElementTree(file=scnlp_fname)
        
        parse_fname = new_name(scnlp_fname, parse_dir, ".parse",
                               strip_ext=["xml"])
        log.info("writing " + parse_fname)
        
        with open(parse_fname, "wt", encoding="utf-8") as parse_file:
            for parse_elem in nlp_doc.findall(".//parse"):
                parse_file.write(parse_elem.text + "\n")


def extract_lemmatized_parse_trees(scnlp_files, parse_dir):
    """
    extract lemmatzied parse trees (PTB labeled bracket structures) from
    Stanford CoreNLP XML ouput
    """
    make_dir(parse_dir)
        
    for scnlp_fname in file_list(scnlp_files, "*.xml"):
        nlp_doc = ElementTree(file=scnlp_fname)
        
        parse_fname = new_name(scnlp_fname, parse_dir, ".parse",
                               strip_ext=["xml"])
        log.info("writing " + parse_fname)
        
        with open(parse_fname, "wt", encoding="utf-8") as parse_file:
            for sentence_elem in nlp_doc.iterfind(".//sentence"):
                lemmas = sentence_elem.iterfind("tokens/token/lemma")
                word_parse = sentence_elem.find("parse").text
                lemma_parse = " ".join( _lemmatized_node(node, lemmas)
                                        for node in word_parse.split() )
                parse_file.write(lemma_parse + "\n")    


def _lemmatized_node(node, lemmas):
    if node.startswith("("):
        # non-terminal node
        return node
    else:
        # terminal
        brackets = "".join(node.partition(")")[1:])
        return next(lemmas).text + brackets
