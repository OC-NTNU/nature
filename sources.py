#!/usr/bin/env python

from collections import Counter

import json

import pandas as pd

from nature.utils import new_name



def sources(results_fname, rec_dir, max_n=10000):
    tab = pd.read_pickle(results_fname)
    counters = { "publication": Counter(),
                 "publication + genre": Counter(),
                 "publication + genre + date": Counter(),
                 }
    
    for doi in tab.index[:max_n]:
        doi = doi.replace("/", "#")
        rec_fname = new_name(doi, rec_dir, ".json", strip_ext=[""])
        entry = json.load(open(rec_fname, "rt"))
        head = entry["sru:recordData"]["pam:message"]["pam:article"]["xhtml:head"]
        publication = head["prism:publicationName"]
        date = head["prism:publicationDate"].split("-")[0]
        genre = str(head["prism:genre"])
        key = ", ".join([publication, genre, date])
        counters["publication + genre + date"][key] += 1
        key = ", ".join([publication, genre])
        counters["publication + genre"][key] += 1
        key = ", ".join([publication])
        counters["publication"][key] += 1

    for name, counter in counters.items():
        print(80*"-")
        print(name)
        print(80*"-")
        for key, count in counter.most_common():
            print("{}, {}".format(count, key))
        
        
        
sources("search_results.pkl", "records")#, max_n=100)
        
    