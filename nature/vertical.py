from lxml.etree import ElementTree
from json import load

from os.path import basename, join

from nature.utils import make_dir, file_list, new_name, strip_xml

import logging
log = logging.getLogger(__name__)

UNESCAPE = {
    '-lrb-': '(',
    '-rrb-': ')',
    '-rsb-': '[',
    '-rsb-': ']',
    '-lcb-': '{',
    '-rcb-': '}'
}

def undo_escape(s):
    """
    undo PTB-style escape of brackets
    """
    return UNESCAPE.get(s.lower(), s)


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
        
        title = strip_xml(head["dc:title"]).replace("\n", " ")
        authors = ", ".join(head["dc:creator"] or [""]).replace("\n", "")
        genre = head["prism:genre"]
        journal = head["prism:publicationName"]
        year = head["prism:publicationDate"].split("-")[0]
        url = head["prism:url"]
        doi = head["prism:doi"]
        
        header = '<doc doi="{}" title="{}" authors="{}" journal="{}" year="{}" genre="{}" url="{}">\n'.format(
                doi,
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

                vert_file.write("<s>\n")
                last_end = None
                    
                for tok in sent.findall("token"):
                    begin = tok.find("CharacterOffsetBegin").text
                    if begin == last_end:
                        # insert special marker that indicates no space
                        # between preceding and current token
                        vert_file.write("<g/>\n")                        
                    word = undo_escape(tok.find("word").text)
                    lemma = undo_escape(tok.find("lemma").text)
                    pos = undo_escape(tok.find("POS").text)
                    vert_file.write("{}\t{}\t{}\n".format(word, lemma, pos))
                    begin = tok.find("CharacterOffsetBegin").text
                    last_end = tok.find("CharacterOffsetEnd").text
                    
                vert_file.write("</s>\n")   
                
                if n == 0:
                    vert_file.write("</title>\n<description>\n")           
                
            vert_file.write("</description>\n</doc>\n")        
    
    
    
    
    
