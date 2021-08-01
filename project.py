#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 19:47:58 2021

@author: coyote
"""
# =============================================================================
# from Bio.Blast import NCBIWWW
# import json
# import subprocess
# 
# sequence_data = open("Q14181_chg.fasta").read() 
# result_handle = NCBIWWW.qblast("blastp", "swissprot", sequence_data)
# fasta = "/home/coyote/JHU_Fall_2020/Summer/Q14181_chg.fasta"
# 
# with open('results.xml', 'w') as save_file: 
#     blast_results = result_handle.read() 
#     save_file.write(blast_results)
#     
# from Bio.Blast.Applications import NcbiblastpCommandline
# cline = NcbiblastpCommandline(query="Q14181_chg.fasta", db="~/Downloads/swissprot",
#                               evalue=0.001, remote=False, ungapped=True,
#                               comp_based_stats="F", outfmt=5, parse_seqids=True)
# 
# # humans, mouse, rat, chinese hamster, Escherichia coli, Saccharomyces cerevisiae, 
# # Arabidopsis, drosophila, bos tauras, pan troglodytes
# # 
# taxids = [9606, 10090, 10116, 10029, 83333, 559292, 3702, 7227, 9913, 9598]
# tax_filter = ",".join([str(i) for i in taxids])
# =============================================================================


from Bio import SeqIO
from io import StringIO
import tempfile
#from Bio.SeqIO.FastaIO import FastaWriter
import re
import pandas as pd
import subprocess, os
import jinja2
import cgi



def main():
    
    form = cgi.FieldStorage()
    # search_entry = form.getvalue("search_entry")
    search_entry = ">sp|P80162|CXCL6_HUMAN C-X-C motif chemokine 6 OS=Homo sapiens OX=9606 GN=CXCL6 PE=1 SV=4\
    MSLPSSRAARVPGPSGSLCALLALLLLLTPPGPLASAGPVSAVLTELRCTCLRVTLRVNP\
    KTIGKLQVFPAGPQCSKVEVVASLKNGKQVCLDPEAPFLKKVIQKILDSGNKKN"
    search_entry = ">CXCL6_HUMAN C-X-C motif chemokine 6 OS=Homo sapiens OX=9606 GN=CXCL6 PE=1 SV=4\n\
    MSLPSSRAARVPGPSGSLCALLALLLLLTPPGPLASAGPVSAVLTELRCTCLRVTLRVNP\
    KTIGKLQVFPAGPQCSKVEVVASLKNGKQVCLDPEAPFLKKVIQKILDSGNKKN"
    fasta_io = StringIO(search_entry)
    records = SeqIO.parse(fasta_io, "fasta")
    fa = [record for record in records][0]
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        #fa_file = tmpdirname + "/" + fa.id + ".fasta"
        fa_file = fa.id.split("|")[-1] + ".fasta"
        handle = open(fa_file , "w")
        SeqIO.write(fa, handle, "fasta")
    
    # organisms = form.getlist("organisms")
    organisms = [9606, 10090, 10116, 10029, 83333, 559292, 3702, 7227, 9913, 9598]
    tax_filter = ",".join([str(i) for i in organisms])
    
    
    ## blast
    header = re.compile(b"^#")
    Fields = re.compile(b"# Fields")
    # https://www.biostars.org/p/88944/
    # blastp -outfmt "7 std staxids" -query Q14181_chg.fasta -db swissprot -evalue 0.001 -taxids 9606,9913
    #export BLASTDB=~/uniprot_dbs/
    my_env = os.environ.copy()
    my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]
    my_env["BLASTDB"] = "/Users/brian/uniprot_dbs"
    proc = subprocess.Popen("blastp \
                            -outfmt {} \
                            -query {} \
                            -db ~/uniprot_dbs/swissprot \
                            -evalue {} \
                            -parse_deflines \
                            -taxids {}".format('"7 std staxids qseq sseq sscinames"',
                            fa_file, 0.001, tax_filter),
                           shell=True,
                           stdout=subprocess.PIPE,
                           env=my_env
                           )
    hit_list = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        if header.match(line) and not Fields.search(line):
            continue
        elif Fields.search(line):
            line = line.replace(b"# Fields: ", b'').rstrip()
            colnames = [i.decode("utf-8").replace(" ", "_") for i in line.split(b", ")]
            colnames = [i.replace(".", "") for i in colnames]
        else:
            hit_list.append(line)
            
    # https://stackoverflow.com/questions/54102980/convert-a-tab-and-newline-delimited-string-to-pandas-dataframe
    df = pd.DataFrame([x.decode("utf-8").split('\t') for x in hit_list], columns=colnames)
    
    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('project.html')
    print("Content-Type: text/html\n\n")


    print(template.render(final_df=df,
                          final_cols=colnames))
    
      
    
if __name__ == '__main__':
    main()
    



