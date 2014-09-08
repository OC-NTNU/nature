import logging
log = logging.getLogger(__name__)

from glob import glob
from subprocess import check_output, STDOUT

from nature.utils import make_dir, file_list, new_name


# Conversion with xml2txt is currently messy.

# * znxml2txt is a patched version of nxml2txt that calls Python2 and performs
# a gunzip first.

# * nxml2txt/src/rewriteu2a.py is hacked to prevent an error msg

##--- a/src/rewriteu2a.py
##+++ b/src/rewriteu2a.py
##@@ -66,8 +66,15 @@ def read_mapping(f, fn="mapping data"):
         ##m = linere.match(l)
         ##assert m, "Format error in %s line %s: '%s'" % (fn, i+1, l.replace("\n","").encode("utf-8"))
         ##c, r = m.groups()
##+        
##+        
##+        # EM: hack to avoid
##+        # ValueError: unichr() arg not in range(0x10000) (narrow Python build)
##+        try:
##+            c = unichr(int(c, 16))
##+        except ValueError:
##+            continue
 
##-        c = unichr(int(c, 16))
         ##assert c not in mapping or mapping[c] == r, "ERROR: conflicting mappings for %.4X: '%s' and '%s'" % (ord(c), mapping[c], r)
 
         ### exception: literal '\n' maps to newline

# * The initial steps for math conversion are probably not needed for NPG pubs

# * Respacing should wrap tags occurring in NPG's html.



def convert_to_soa(nxml2txt, xml_files, soa_dir):
    make_dir(soa_dir)
    
    for xml_fname in file_list(xml_files):
        txt_fname = new_name(xml_fname, soa_dir, ".txt")
        soa_fname = new_name(xml_fname, soa_dir, ".soa")
        log.info("converting {} to {} and {}".format(
            xml_fname, txt_fname, soa_fname))
        ret = check_output([nxml2txt, xml_fname, txt_fname, soa_fname], 
                           stderr=STDOUT
                           )
        log.info(ret.decode("utf-8"))