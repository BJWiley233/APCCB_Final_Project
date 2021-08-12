#!/usr/local/bin/python3

from Bio import SeqIO
from io import StringIO
import tempfile
from Bio.SeqIO.FastaIO import FastaWriter
import re
import pandas as pd
import subprocess, os
import jinja2
import cgi
from Bio import Entrez
import json


'''
>CXCL6_HUMAN C-X-C motif chemokine 6 OS=Homo sapiens OX=9606 GN=CXCL6 PE=1 SV=4
MSLPSSRAARVPGPSGSLCALLALLLLLTPPGPLASAGPVSAVLTELRCTCLRVTLRVNP
KTIGKLQVFPAGPQCSKVEVVASLKNGKQVCLDPEAPFLKKVIQKILDSGNKKN
'''


def main():
    
    form = cgi.FieldStorage()
    if form.getvalue('fasta_entered'):
        search_entry = form.getvalue('fasta_entered')
        fasta_io = StringIO(search_entry)
        fasta = SeqIO.parse(fasta_io, "fasta")
        fa = [record for record in fasta][0] ## to get name for fasta
        #fasta_io = StringIO(search_entry)
        #fasta = SeqIO.parse(fasta_io, "fasta")
        if form.getvalue("job_title"):
            job_title = form.getvalue("job_title") # to name fasta file
        else:
            job_title = None
    else:
        search_entry = ">CXCL6_HUMAN C-X-C motif chemokine 6 OS=Homo sapiens OX=9606 GN=CXCL6 PE=1 SV=4\n\
            MSLPSSRAARVPGPSGSLCALLALLLLLTPPGPLASAGPVSAVLTELRCTCLRVTLRVNP\
            KTIGKLQVFPAGPQCSKVEVVASLKNGKQVCLDPEAPFLKKVIQKILDSGNKKN"
        fasta_io = StringIO(search_entry)
        fasta = SeqIO.parse(fasta_io, "fasta")
        fa = [record for record in fasta][0]
        if form.getvalue("job_title"):
            job_title = form.getvalue("job_title") # to name fasta file
        else:
            job_title = None
 
 
    job_title = form.getvalue("job_title")
     # Search by Uniprot ID will only run if no text entry is given
    if form.getvalue("uniprot_id") and not form.getvalue('fasta_entered'):
        # https://stackoverflow.com/questions/52569622/protein-sequence-from-uniprot-protein-id-python
        import requests
        baseUrl="http://www.uniprot.org/uniprot/"
        uniprot_id = form.getvalue("uniprot_id")
        # remove decimal for version
        uniprot_id.split(".")[0]
        currentUrl=baseUrl + uniprot_id + ".fasta"
        response = requests.post(currentUrl)
        search_entry = response.text
        #cData=''.join(response.text)
        fasta_io = StringIO(search_entry)
        fasta = SeqIO.parse(fasta_io, "fasta")
        fa = [record for record in fasta][0] ## to get name for fasta
        job_title = None # will be name of Uniprot "entry_name" field

        start = 0
        end = len(fa.seq)
        if form.getvalue("start_resi"):
            start = form.getvalue("start_resi") - 1
        if form.getvalue("end_resi"):
            end = form.getvalue("end_resi")
        fa.seq = fa.seq[start:end]
    
    tax_arg = ""
    tax_filter = ""
    organisms = form.getlist("organisms")
    if organisms:
        tax_arg = "-taxids"
        tax_filter = ",".join([str(i) for i in organisms])
    # override selections!
    if form.getvalue("taxid_manual"):
        tax_arg = "-taxids"
        organisms = form.getvalue("taxid_manual")
        tax_filter = organisms.replace(" ","")
    if not organisms:
        # organisms = [9606, 10090, 10116, 10029, 83333, 559292, 3702, 7227, 9913, 9598]
        organisms = None

    # fasta_io = StringIO(search_entry)
    # fasta = SeqIO.parse(fasta_io, "fasta")
    # fa = [record for record in fasta][0]
    # fasta_io = StringIO(search_entry)
    # fasta = SeqIO.parse(fasta_io, "fasta")


    with tempfile.TemporaryDirectory() as tmpdirname:
        fa_file = tmpdirname + "/" + fa.id.split("|")[-1] + ".fasta"
        # fa_file = "/Users/brian/JHU_Summer/final_project/test/test.fasta"
        try: 
            # handle = open(fa_file , "w")
            # writer = FastaWriter(handle)
            # writer.write_file(fasta)
            # handle.close()
            SeqIO.write(fa, fa_file, format="fasta")
            test1 = "ok"
        except Exception as e1:
            test1 = e1

        ## blast
        header = re.compile("^#")
        Fields = re.compile("# Fields")
        # https://www.biostars.org/p/88944/
        my_env = os.environ.copy()
        ## for path to blastp
        my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]
        ## for access to taxonomy database: taxdb
        my_env["BLASTDB"] = "/Users/brian/uniprot_dbs"
        
  
        COMMAND = "/usr/local/bin/blastp -outfmt {} -query {} -db ~/uniprot_dbs/swissprot \
                    -evalue {} -parse_deflines {} {} > {}\
                    ".format('"7 std staxids qseq sseq sscinames scomnames stitle"',
                    fa_file, 0.001, tax_arg, tax_filter, tmpdirname + "/results.txt")     
        subprocess.run(COMMAND, shell=True, env=my_env)
        # subprocess.run("cp {} {}".format(tmpdirname + "/results", "/Users/brian/JHU_Summer/final_project/test/results"), shell=True, env=my_env)

    
        hit_list = []
        # with open("/Users/brian/JHU_Summer/final_project/test/results") as f:
        with open(tmpdirname + "/results.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if header.match(line) and not Fields.search(line):
                    continue
                elif Fields.search(line):
                    #line = line.replace(b"# Fields: ", b'').rstrip()
                    line = line.replace("# Fields: ", '').rstrip()
                    #colnames = [i.decode("utf-8").replace(" ", "_") for i in line.split(b", ")]
                    colnames = [i.replace(" ", "_") for i in line.split(", ")]
                    colnames = [i.replace(".", "") for i in colnames]
                else:
                    hit_list.append(line)
    



    # https://stackoverflow.com/questions/54102980/convert-a-tab-and-newline-delimited-string-to-pandas-dataframe
    # https://stackoverflow.com/questions/29815129/pandas-dataframe-to-list-of-dictionaries/29816143#29816143
    # https://stackoverflow.com/questions/34584426/nested-for-loop-in-jinja2
    # df = pd.DataFrame([x.decode("utf-8").split('\t') for x in hit_list], columns=colnames).to_dict('records')
    df = pd.DataFrame([x.split('\t') for x in hit_list], columns=colnames).to_dict('records')
    colnames.remove("subject_sci_names")
    colnames.insert(2,"subject_sci_names")
    colnames.remove("subject_title")
    colnames.insert(3,"subject_title")

    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('project.html')
    print("Content-Type: text/html\n\n")
    # print(test1)
    print(template.render(final_df=df,
                          final_cols=colnames,
                          data=search_entry))
   
   
      
    
if __name__ == '__main__':
    main()