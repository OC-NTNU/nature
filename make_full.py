#!/usr/bin/env python

"""
run processes to create Nature full corpus
"""

from baleen.pipeline import script
from baleen.steps import core_nlp, lemma_trees, ext_vars, \
    offsets, prep_vars, prune_vars

from nature.steps import download, ext_full, soa, tocsv, toneo, ppgraph, \
    setupserver, startserver, stopserver, vertical

script(steps=[download,
              ext_full,
              soa,
              core_nlp,
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
           vertical],
       default_cfg_fnames=['nature-corpus.ini', 'local.ini'],
       default_section='FULL')
