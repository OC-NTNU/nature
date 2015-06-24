import logging
log = logging.getLogger(__name__)
# silence request logging
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)

import pandas as pd
from requests import get
from os.path import join, exists
from os import makedirs

def download_webpages(results_fname, out_dir, 
                      max_n_downloads=None, resume=False):
    """
    download html source of article webpages
    """
    tab = pd.read_pickle(results_fname)
    n_downloads = 0
    
    if not exists(out_dir):
        makedirs(out_dir)
    
    for doi in tab.index:        
        out_fname = join(out_dir, doi.replace("/","#") + "#full.htm")
        if not resume or not exists(out_fname):    
            url = "http://dx.doi.org/" + doi
            response = get(url)
            if response.ok:
                # response.text is utf-8 encoded
                with open(out_fname, 'w') as outf:
                    log.info("writing " + out_fname)
                    outf.write(response.text)
                    n_downloads += 1
            else:
                log.warn("{0.url} returned {0.status_code} {0.reason}".
                         format(response))
        else:
            log.info("skipping existing " + out_fname)
        if n_downloads == max_n_downloads:
            log.info("max number of downloads ({}) reached".
                     format(max_n_downloads))
            break
            
            
            
    
    
    
    
