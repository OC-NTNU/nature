import logging
log = logging.getLogger(__name__)

from lxml import etree

from nature.utils import make_dir, file_list, new_name



def extract_sent(txt_files, scnlp_dir, sent_dir):
    """
    Extract sentences from stand-off annotation text files using boundaries
    from CoreNLP sentence splitting
    """
    make_dir(sent_dir)
    
    for txt_fname in file_list(txt_files, "*.txt"):
        txt = open(txt_fname).read()

        # use split-sent with stamp=false for this to work
        scnlp_fname = new_name(txt_fname, scnlp_dir, ".xml", strip_ext=["txt"])
        tree = etree.ElementTree(file=scnlp_fname)

        sent_fname = new_name(txt_fname, sent_dir, "#sent.txt", strip_ext=["txt"])
        log.info("writing sentences to " + sent_fname)
        
        with open(sent_fname, "wt") as sent_file:        
            for tokens in  tree.findall("//tokens"):
                begin = int(tokens[0].find(".//CharacterOffsetBegin").text)
                end = int(tokens[-1].find(".//CharacterOffsetEnd").text)
                sent_file.write(txt[begin:end] + "\n")