import logging
log = logging.getLogger(__name__)

from os.path import join
from tempfile import NamedTemporaryFile, TemporaryDirectory
from os import getenv
from subprocess import check_output, STDOUT

from nature.utils import make_dir, file_list



class CoreNLP(object):
    
    def __init__(self,
                 lib_dir=getenv("CORENLP_HOME", "/Users/erwin/local/src/corenlp"),
                 lib_ver=getenv("CORENLP_VER", "3.4.1"),
                 corenlp_class="edu.stanford.nlp.pipeline.StanfordCoreNLP"):
        self.lib_dir = lib_dir
        self.lib_ver = lib_ver
        self.corenlp_class = corenlp_class
    
    
    def run(self,
            txt_files, 
            out_dir, 
            annotators="tokenize,ssplit,pos,lemma,ner,parse,dcoref",
            memory="3g",
            threads=1,
            replace_extension=True,
            output_extension=".xml",
            options="",
            stamp=True,
            ):
        """
    
        txt_files:
            a directory, a glob pattern, a single filename or a list of filenames
        """
        tmp_file = NamedTemporaryFile("wt", buffering=1)
        tmp_file.write("\n".join(file_list(txt_files)) + "\n")
        
        make_dir(out_dir)
            
        jars = ['joda-time.jar',
                'jollyday.jar',
                'stanford-corenlp-{}.jar'.format(self.lib_ver),
                'stanford-corenlp-{}-models.jar'.format(self.lib_ver),
                'xom.jar',
                'ejml-0.23.jar']
        class_path = ":".join(join(self.lib_dir, j) for j in jars)
        
        if stamp:
            replace_extension = True
            output_extension = '"#scnlp_v{}{}"'.format(self.lib_ver, 
                                                       output_extension)    
        if replace_extension:
            options += " -replaceExtension"
        if output_extension:
            options += " -outputExtension " + output_extension
                 
        cmd = ("java -Xmx{} -cp {} {} -annotators {} -filelist {} "
               "-outputDirectory {} -threads {} {}").format(
                   memory, class_path, self.corenlp_class, annotators, 
                   tmp_file.name, out_dir, threads, options)
        
        log.info("\n" + cmd)
        ret = check_output(cmd, shell=True, stderr=STDOUT, universal_newlines=True)
        log.info("\n" + ret)
    
    def ssplit(self,
               txt_files, 
               out_dir=None, 
               annotators="tokenize,ssplit",
               memory="3g",
               threads=1,
               options=" -ssplit.newlineIsSentenceBreak always",
               stamp=False 
               ):
        log.info("start splitting sentences")
        self.run(txt_files, 
                 out_dir, 
                 annotators,
                 memory=memory,
                 threads=threads,
                 options=options,
                 stamp=stamp
                 )
        
    def parse(self,
               txt_files, 
               out_dir=None, 
               annotators="tokenize,ssplit,pos,lemma,parse",
               memory="3g",
               threads=1,
               options=" -ssplit.eolonly"
               ):
        log.info("start parsing sentences")
        self.run(txt_files, 
                 out_dir, 
                 annotators,
                 memory=memory,
                 threads=threads,
                 options=options
                 )
        


    
    
    