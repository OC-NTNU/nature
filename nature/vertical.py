from lxml.etree import ElementTree
from json import load

from os.path import basename, join

from nature.utils import make_dir, file_list, new_name, strip_xml

import logging
log = logging.getLogger(__name__)



def convert_to_vertical_format(scnlp_files, records_dir, vert_dir):
    """
    convert abstracts to vertical format of Sketch Engine
    """
    make_dir(vert_dir)
    
    for scnlp_fname in file_list(scnlp_files, "*.xml"):
        rec_fname = join(records_dir, 
                         "#".join(basename(scnlp_fname).split("#")[:2]) + ".json")
        record = load(open(rec_fname, "rt")) 
        head = record["sru:recordData"]["pam:message"]["pam:article"]["xhtml:head"]
        
        title = strip_xml(head["dc:title"])
        authors = ", ".join(head["dc:creator"] or [""])
        genre = head["prism:genre"]
        journal = head["prism:publicationName"]
        year = head["prism:publicationDate"].split("-")[0]
        url = head["prism:url"]
        
        header = '<doc\n title="{}"\n authors="{}"\n journal="{}"\n year="{}"\n genre="{}"\n url="{}"\n>\n'.format(
                title,
                authors,
                journal,
                year,
                genre,
                url)

        vert_fname = new_name(scnlp_fname, vert_dir, ".vert", strip_ext=["xml"])
        log.info("writing " + vert_fname)
        
        with open(vert_fname, "wt") as vert_file:            
            vert_file.write(header)
            tree = ElementTree(file=scnlp_fname)
            
            for n, sent in enumerate(tree.findall(".//tokens")):
                if n == 0:
                    vert_file.write("<title>\n")
                elif n == 1:
                    vert_file.write("<description>\n")

                vert_file.write("<s>\n")
                    
                for tok in sent.findall("token"):
                    word = tok.find("word").text
                    lemma = tok.find("lemma").text
                    pos = tok.find("POS").text
                    vert_file.write("{}\t{}\t{}\n".format(word, lemma, pos))
                vert_file.write("</s>\n")   
                
                if n == 0:
                    vert_file.write("</title>\n")           
                
            vert_file.write("</description>\n</doc>")        
    
    
    
    
    