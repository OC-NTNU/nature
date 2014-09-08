from os.path import exists, join, dirname
from os import makedirs

import requests
import json

import pandas as pd

import logging
log = logging.getLogger(__name__)
# silence request logging
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)


# It seems that restricting search to dc.title or dc.description gives a
# recall much lower than expected, so use cql.keywords instead.
# Publications after 1997, because before that much is in PDF.

query_template =  """
cql.keywords = "{term}" AND
( prism.publicationName = "Nature" OR
  prism.publicationName = "Nature Chemistry" OR
  prism.publicationName = "Nature Chemical Biology" OR
  prism.publicationName = "Nature Climate Change" OR 
  prism.publicationName = "Nature Communications" OR
  prism.publicationName = "Nature Geoscience" OR
  prism.publicationName = "Nature Methods" OR
  prism.publicationName = "Nature Protocols" OR
  prism.publicationName = "Scientific American" OR
  prism.publicationName = "Scientific Reports" OR
  prism.publicationName = "Nature Reviews Microbiology" OR
  prism.publicationName = "The ISME Journal"
  ) AND
prism.publicationDate > {after_year} 
"""

def search_npg(results_fname, 
           records_dir,
           terms_fname=None, 
           max_records=5000,
           url = 'http://api.nature.com/content/opensearch/request',
           after_year = 1997):
    """
    Retrieve records from Nature publications matching search terms.  
    
    For each search term, a separate search is conducted through the nature API 
    (See http://www.nature.com/developers/documentation/api-references/opensearch-api/). 
    Records of matching documents are stored in JSON format, 
    using the DOI as filename. In addition, a [DOI x search terms] matrix records 
    the matching terms for each DOI, stored as a pickle file containing a 
    Pandas DataFrame.

    results_fname: str
        file for matrix with search results (.pkl)

    records_dir: str
        output directory for records

    terms_fname: str
        file containing search terms; only required for a new search, 
        otherwise search process will continue with terms as stored in 
        results_fname 
    
    max_records: int
        limit on number of result records per query (search term)
    """    
    
    if terms_fname:
        # new search
        search_terms = open(terms_fname).read().strip().split("\n")        
        results_tab = pd.DataFrame(columns=search_terms, dtype=bool)
    else:
        # continue search
        results_tab = pd.read_pickle(results_fname)
        # derive search terms from still empty columns  
        search_terms = list(results_tab.columns[~results_tab.any()])  
        

    if not exists(records_dir):
        log.info("creating dir " + records_dir)
        makedirs(records_dir)             

    for n_term, term in enumerate(search_terms):
        try:
            n_records = 0
            query = query_template.format(term=term,
                                          after_year=after_year)
            params = {
                'queryType': 'cql',
                'httpAccept': 'application/json',
                'query': query,
                'startRecord': 1,
                'maximumRecords': 100
            }
            
            while n_records < max_records:
                response = requests.get(url, params=params)
                result = response.json()    
                
                for entry in result["feed"]["entry"]:
                    head =entry['sru:recordData']['pam:message']['pam:article']['xhtml:head']
                    n_records += 1
                    doi = head["prism:doi"]
                    log.debug(u"\n#{}\nJOURNAL: {}\n\TITLE: {}\nDATE: {}\nDESCR: {}".format(
                        n_records,
                        head['prism:publicationName'],
                        head['dc:title'],
                        head['prism:publicationDate'],
                        head['dc:description']))
                    results_tab.loc[doi, term] = True
                    
                    record_fname = join(records_dir, doi.replace('/','#') + ".json")
                    
                    if not exists(record_fname):  
                        string = json.dumps(entry, check_circular=False, indent=4)
                        log.debug("writing " + record_fname)
                        open(record_fname, "wt").write(string)
    
                    if n_records == max_records:
                        log.warn(u'reached max number of records ({}) for term "{}"'.format(
                            n_records,
                            term))
                        break
                else:
                    try:
                        # More records on next page?
                        params["startRecord"] = result["feed"]["sru:nextRecordPosition"]
                    except KeyError:
                        # No more records
                        break
            
            log.info("#{}/{} '{}': {} records".format(n_term + 1, 
                                                      len(search_terms), 
                                                      term, 
                                                      n_records))
            # save intermediary results
            log.info("saving results to " + results_fname)
            results_tab.to_pickle(results_fname)        
            
        except Exception as err:
            log.error(response.content)
            log.error(str(err))
            log.error(u'Skipped term: "{}"'.format(term))
        


def rank_results(results_fname):
    """
    rank results from most to least number of matching search terms  
    """
    tab = pd.read_pickle(results_fname)
    totals = tab.sum(axis=1)
    totals.sort(ascending=False)    
    dois = totals.keys()
    tab = tab.ix[dois]
    pd.to_pickle(tab, results_fname)
    log.info("ranked search results in " + results_fname)
    
            
            
header = """
<!DOCTYPE html>
<html>
<body>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head>
<h1>NPG publications for Ocean-Certain</h1>

<p>Below is the result of a search in the following publications from
Nature Publishing Group:</p>

<ol>
<li>Nature</li>
<li>Nature Chemistry</li>
<li>Nature Chemical Biology</li>
<li>Nature Climate Change</li>
<li>Nature Communications</li>
<li>Nature Geoscience</li>
<li>Nature Methods</li>
<li>Nature Protocols</li>
<li>Scientific American</li>
<li>Scientific Reports</li>
<li>Nature Reviews Microbiology</li>
<li>The ISME Journal</li>
</ol>

<p>for articles after 1997 matching any of the 305
predefined <a href="terms.txt">search terms</a>. Search was conducted
using NPG's search API. Results are ranked according to the number of
matching search terms in descending order. Only the top 5000 results
from the total of matching 60,156 articles are shown.</p>

<hr>

"""

template = """
<p>
{}) {} <br>
<a href="{}">{}</a> <br>
In: <i>{}</i>, {}
<i>{}</i>
<b>{}</b> search term matches: {} <br>
</p>
<hr>
"""

trailer =  """
</body>
</html>
"""

def results_to_html(results_fname, records_dir, html_fname):    
    tab = pd.read_pickle(results_fname)
    with open(html_fname, "wt") as outf:
        outf.write(header)
        
        for n, doi in enumerate(tab.index):
            fname = join(records_dir, doi.replace("/", "#") + ".json")
            if not exists(fname):
                log.warn("no record for " + doi)
                continue
            
            entry = json.load(open(fname, "rt"))
            head = entry['sru:recordData']['pam:message']['pam:article']['xhtml:head']
            select = tab.ix[doi] == True
            try:
                creator = ", ".join(head['dc:creator'])
            except:
                creator = head['dc:creator'] or ""
            outf.write(template.format(
                n + 1,
                creator,
                entry["link"],
                head["dc:title"],
                head['prism:publicationName'],
                head['prism:publicationDate'],
                head["dc:description"],
                tab.ix[doi].sum(),
                ", ".join(tab.ix[doi][select].index) ))
        
        outf.write(trailer)
    
    
    
