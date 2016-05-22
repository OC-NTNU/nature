#!/usr/bin/env python

"""
run processes to create Nature abstracts corpus
"""

from baleen.pipeline import script
from baleen.steps import split_sent, parse_sent, lemma_trees, ext_vars, \
    offsets, prep_vars, prune_vars

from nature.steps import ext_abs, ext_sent, brat, soa, tocsv, toneo, ppgraph, \
    setupserver, startserver, stopserver, vertical

script(steps=[ext_abs,
              soa,
              split_sent,
              ext_sent,
              parse_sent,
              lemma_trees,
              ext_vars,
              offsets,
              prep_vars,
              prune_vars,
              tocsv,
              toneo,
              ppgraph],
       optional=[
           setupserver,
           startserver,
           stopserver,
           vertical,
           brat],
       default_cfg_fnames=['nature-corpus.ini', 'local.ini'],
       default_section='ABSTRACTS')
