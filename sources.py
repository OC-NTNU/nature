#!/usr/bin/env python

from collections import Counter

import json

import pandas as pd

from nature.utils import new_name



def sources(results_fname, rec_dir, max_n=10000):
    tab = pd.read_pickle(results_fname)
    counts = Counter()
    
    for doi in tab.index[:max_n]:
        doi = doi.replace("/", "#")
        rec_fname = new_name(doi, rec_dir, ".json", strip_ext=[""])
        entry = json.load(open(rec_fname, "rt"))
        head = entry["sru:recordData"]["pam:message"]["pam:article"]["xhtml:head"]
        publication = head["prism:publicationName"]
        date = head["prism:publicationDate"].split("-")[0]
        genre = str(head["prism:genre"])
        key = ", ".join([publication, genre, date])
        counts[key] += 1
        
    for key, count in counts.most_common():
        print("{}, {}".format(count, key))
        
        
        
sources("search_results.pkl", "records")#, max_n=100)
        
    