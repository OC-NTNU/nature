import logging
log = logging.getLogger(__name__)

import pandas as pd
from requests import get
from os.path import join, exists
from os import makedirs


def download_webpages(results_fname, out_dir, full_max_n):
    """
    download html source of article webpages
    """
    tab = pd.read_pickle(results_fname)
    
    if not exists(out_dir):
        makedirs(out_dir)
    
    for n, doi in enumerate(tab.index[:full_max_n]):
        out_fname = join(out_dir, doi.replace("/","#") + "#full.htm")
        if not exists(out_fname):    
            url = "http://dx.doi.org/" + doi
            response = get(url)
            # content is utf-8
            with open(out_fname, 'w') as outf:
                log.info("writing " + out_fname)
                outf.write(response.content)
        else:
            log.info("skipping existing " + out_fname)
