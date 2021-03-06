
from lxml import etree
from lxml.html import HTMLParser

from nature.utils import file_list, new_name, make_dir

import logging
log = logging.getLogger(__name__)



def extract_content(htm_files, xml_dir):
    """
    Extract article content from html
    
    This is a very rough extraction of the article content by stripping page
    headers, footers and side bars. Content is simply identified by either an
    <article> or <div id="content"> tag. The remainder still contains a lot
    of unintended info such a authors, affiliations, keywords, navigation
    links, references, comments, etc. However, the format of the websites of
    the different NPG publications over the years contains so much variation
    that it seems impossble to write general filtering rules.
    
    In addition, the HTML is often ill-formed, so this also converts to
    (syntactically) well-formed XML, suitable as input to nxml2txt.
    """
    make_dir(xml_dir)
    parser = HTMLParser(recover=True, remove_comments=True,
                        remove_pis=True, remove_blank_text=True)

    for htm_fname in file_list(htm_files):
        tree   = etree.parse(htm_fname, parser)

        if tree.getroot() is None:
            log.warning('skipping: no html content in ' + htm_fname)
            continue
        # check if license allows full text access
        meta_elem = tree.xpath("//meta[@name='Access' or @name='access']")
        if meta_elem is None:
            # If there is not meta tag, this means some technical error such as
            # DOI not found or server problems
            log.warning('skipping: no <meta name="access" ...> in ' + htm_fname)
            continue
        if meta_elem[0].get("content") not in ("Yes", "yes"):
            log.warning('skipping: no access rights to ' + htm_fname)
            continue

        # locate content  (cannot use: content = ... or ...)
        content = tree.find("//article")
        if content is None:
            tree.find("//{*}div[@id='content']")

        if content is None:
            log.warning('skipping: no <article> or <div id="content" ...> in ' +
                        htm_fname)
            continue

        # (cannot use: refs_elem = ... or ...)
        refs_elem = tree.find("//{*}div[@id='references']")
        if refs_elem is None:
            refs_elem =  tree.find("//{*}div[@id='References']")

        if refs_elem is not None:
            # remove references
            refs_elem.getparent().remove(refs_elem)

        xml_fname = new_name(htm_fname, new_dir=xml_dir, new_ext=".xml",
                             strip_ext=["htm"])
        log.info("writing content to " + xml_fname)
        # ommit tail text to prevent ill-formed xml doc
        xml = etree.tostring(content, pretty_print=True, with_tail=False,
                             xml_declaration=True, encoding="utf-8")
        open(xml_fname, "wb").write(xml)



