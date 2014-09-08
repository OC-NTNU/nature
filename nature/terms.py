import pandas as pd
import sys

import logging
log = logging.getLogger(__name__)


def get_terms(csv_fname, terms_fname, n_terms=None):
    """
    Extract search terms from spreadsheet in csv format with checked terms
    
    csv_fname: str 
        spread sheet with checked terms in comma-separated format
    terms_fname: str
        output file for terms
        
    n_terms: int
        max number of terms
    """
    log.info("reading checked terms from speadsheet " + csv_fname)
    terms_tab = pd.read_csv(csv_fname)
    search_terms = terms_tab[terms_tab["Search term?"] == "y"]["Term"]
    log.info("writing {} terms to {}".format(n_terms or len(search_terms),
                                             terms_fname))
    open(terms_fname, "wt", encoding="utf-8").write("\n".join(search_terms[:n_terms]))

