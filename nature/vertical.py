from lxml.etree import ElementTree
from json import load

from os.path import basename, join, exists

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


def convert_abs_to_vertical_format(scnlp_files, records_dir, vert_dir):
    """
    convert abstracts to vertical format of Sketch Engine
    """
    convert_to_vertical_format(scnlp_files, records_dir, vert_dir, write_abs_body)


def convert_full_to_vertical_format(scnlp_files, records_dir, vert_dir):
    """
    convert full text to vertical format of Sketch Engine
    """
    convert_to_vertical_format(scnlp_files, records_dir, vert_dir, write_full_body)
    
    

def convert_to_vertical_format(scnlp_files, records_dir, vert_dir,
                               write_body, resume=False):
    """
    convert to vertical format of Sketch Engine
    """
    make_dir(vert_dir)
    
    for scnlp_fname in file_list(scnlp_files, "*.xml"):
        vert_fname = new_name(scnlp_fname, vert_dir, ".vert", strip_ext=["xml"])
            
        if resume and exists(vert_fname):                
            log.info("skipping existing " + vert_fname)
        else:
            try:
                with open(vert_fname, "wt") as vert_file:
                    write_header(vert_file, records_dir, scnlp_fname)
                    tree = ElementTree(file=scnlp_fname)            
                    write_body(vert_file, tree)
                    # close header
                    vert_file.write("</doc>\n")    
            except Exception:
                # catch any weird errors (e.g. ill-formed XML in record's title) 
                # and just continue
                log.exception("Something went wrong...")
                log.error("Skipped file " + scnlp_fname)
            else:
                log.info("wrote " + vert_fname)
    

def write_abs_body(vert_file, tree):
    for n, sent in enumerate(tree.findall(".//tokens")):
        if n == 0:
            vert_file.write("<title>\n")

        write_sent(vert_file, sent)
        
        if n == 0:
            vert_file.write("</title>\n<description>\n")                           
    vert_file.write("</description>\n")    
    

def write_full_body(vert_file, tree):
    # no internal doc structure yet
    for n, sent in enumerate(tree.findall(".//tokens")):
        write_sent(vert_file, sent)

            
def write_header(vert_file, records_dir, scnlp_fname):
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

    vert_file.write(header)            
            

def write_sent(vert_file, sent):
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
    
    
    
    
    
