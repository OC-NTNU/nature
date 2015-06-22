"""
Extract and prune variables
"""

import logging
log = logging.getLogger(__name__)

from os.path import dirname
from subprocess import check_output, STDOUT


from nature.utils import make_dir



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


