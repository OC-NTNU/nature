import logging
log = logging.getLogger(__name__)
# silence request logging
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)

import pandas as pd
from requests import get
from os.path import join, exists
from os import makedirs
from shutil import copyfile

def download_webpages(results_fname, out_dir, 
                      max_n_downloads=None, 
                      resume=False, 
                      cache_dir=None):
    """
    download html source of article webpages
    """
    tab = pd.read_pickle(results_fname)
    n_downloads = 0
    
    if not exists(out_dir):
        makedirs(out_dir)
    
    for doi in tab.index:
        out_basename = doi.replace("/","#") + "#full.htm"
        out_fname = join(out_dir, out_basename)
        cached_fname = join(cache_dir or "", out_basename)
                
        if cache_dir and exists(cached_fname):
            log.info("copying cached file " + cached_fname)
            copyfile(cached_fname, out_fname)
        elif resume and exists(out_fname):
            log.info("skipping existing file " + out_fname)
        else:
            url = "http://dx.doi.org/" + doi
            response = get(url)
            if response.ok:
                # response.text is utf-8 encoded
                with open(out_fname, 'w') as outf:
                    log.info("writing file " + out_fname)
                    outf.write(response.text)
            else:
                log.warn("{0.url} returned {0.status_code} {0.reason}".
                         format(response))
                continue
            
        n_downloads += 1
        
        if n_downloads == max_n_downloads:
            log.info("max number of downloads ({}) reached".
                     format(max_n_downloads))
            break
            
            
            
    
    
    
    
