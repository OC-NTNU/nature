"""
Extract and prune variables
"""

import logging
import json

from os.path import dirname
from subprocess import check_output, STDOUT

from nature.utils import make_dir

log = logging.getLogger(__name__)


def extract_vars(extract_vars_exec, trees_dir, vars_file):
    """
    Extract variables in change/increase/decrease events
    """
    make_dir(dirname(vars_file))
    cmd = "{} {} {}".format(extract_vars_exec, trees_dir, vars_file)
    log.info("\n" + cmd)
    # universal_newlines=True is passed so the return value will be a string
    # rather than bytes
    ret = check_output(cmd, shell=True, stderr=STDOUT, universal_newlines=True)
    log.info("\n" + ret)


def preproc_vars(trans_exec, in_vars_file, out_vars_file, trans_file,
                 prep_file):
    """
    Preprocess variables

    Deletes determiners (DT), personal/possessive pronouns (PRP or PRP$) and
    list item markers (LS or LST).
    """
    make_dir(dirname(out_vars_file))
    cmd = ' '.join([trans_exec, in_vars_file, out_vars_file, trans_file])
    log.info("\n" + cmd)
    # universal_newlines=True is passed so the return value will be a string
    # rather than bytes
    ret = check_output(cmd, shell=True, universal_newlines=True)
    log.info("\n" + ret)
    records = json.load(open(out_vars_file))
    # Remove any var that has descendents (i.e. from which a node was deleted)
    # Also remove empty vars
    prep_records = [rec for rec in records
                    if rec['subStr'] and not 'descendants' in rec]
    json.dump(prep_records, open(prep_file, 'w'), indent=0)


def prune_vars(prune_vars_exec, vars_file, pruned_file, options=""):
    """
    Prune variables in change/increase/decrease events
    """
    make_dir(dirname(pruned_file))
    cmd = "{} {} {} {}".format(prune_vars_exec, options, vars_file,
                               pruned_file)
    log.info("\n" + cmd)
    # universal_newlines=True is passed so the return value will be a string
    # rather than bytes
    ret = check_output(cmd, shell=True, stderr=STDOUT, universal_newlines=True)
    log.info("\n" + ret)
