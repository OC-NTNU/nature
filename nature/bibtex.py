#!/usr/bin/env python

import logging
log = logging.getLogger(__name__)

from requests import get
from glob import glob
from os.path import basename, join, exists

from nature.utils import make_dir, file_list

headers = {'Accept': 'text/bibliography; style=bibtex'}


def lookup_bibtex(xml_files, bib_dir):
    """
    Lookup bibtex citation for abstracts, using CrossRef web service
    
    See http://labs.crossref.org/citation-formatting-service/
    """
    make_dir(bib_dir)   
     
    for fname in file_list(xml_files):
        doi =  basename(fname).split("#")[:2]
        bib_fname = join(bib_dir, "{}#{}.bib".format(*doi))
        
        if not exists(bib_fname):
            r = get('http://dx.doi.org/{}/{}'.format(*doi), headers=headers)
            log.info("writing " + bib_fname)
            # although r.encoding == "ISO-8859-1"", r.content is in fact UTF-8 
            open(bib_fname, "wb").write(r.content)
