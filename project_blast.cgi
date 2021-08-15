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



def main():
    
    form = cgi.FieldStorage()
    if form.getvalue('fasta_entered'):
        search_entry = form.getvalue('fasta_entered')
        fasta_io = StringIO(search_entry)
        fasta = SeqIO.parse(fasta_io, "fasta")
        fa = [record for record in fasta][0] ## to get name for fasta
        start = 0
        end = len(fa.seq)
        if form.getvalue("job_title"):
            job_title = form.getvalue("job_title") # to name fasta file
        else:
            job_title = None
    else:
        ## make default search entry for fun so it doesn't error
        ## UPDATE: did error checking for no submission but still going to run as example
        search_entry = ">sp|P80162|CXCL6_HUMAN C-X-C motif chemokine 6 OS=Homo sapiens OX=9606 GN=CXCL6 PE=1 SV=4\n\
            MSLPSSRAARVPGPSGSLCALLALLLLLTPPGPLASAGPVSAVLTELRCTCLRVTLRVNP\
            KTIGKLQVFPAGPQCSKVEVVASLKNGKQVCLDPEAPFLKKVIQKILDSGNKKN"
        fasta_io = StringIO(search_entry)
        fasta = SeqIO.parse(fasta_io, "fasta")
        # fasta record
        fa = [record for record in fasta][0]
        start = 0
        end = len(fa.seq)
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
        # remove decimal version number if given as this can give a really old sequence?
        # for example https://www.uniprot.org/uniprot/O75616.2.fasta gives >TrEMBL|O75616|Release 9|01-Jan-1999
        uniprot_id.split(".")[0]
        currentUrl=baseUrl + uniprot_id + ".fasta"
        response = requests.post(currentUrl)
        search_entry = response.text
 
        fasta_io = StringIO(search_entry)
        fasta = SeqIO.parse(fasta_io, "fasta")
        # fasta record
        fa = [record for record in fasta][0] ## to get name for fasta
        job_title = None # will be name of Uniprot "entry_name" field

        start = 0
        end = len(fa.seq)
        if form.getvalue("start_resi"):
            start = int(form.getvalue("start_resi")) - 1
        if form.getvalue("end_resi"):
            end = int(form.getvalue("end_resi"))
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
        # will search all organisms
        organisms = None

    ## this needs to live longer for download of results so making /tmp/bwiley4 dir
    with tempfile.TemporaryDirectory() as tmpdirname:
        # DOESN'T WORK!!
        # tmpdirname = "/tmp/bwiley4"
        # DOESN'T WORK!!
        # tmpdirname = "/var/tmp/bwiley4"
        # Works because I have permissions
        tmpdirname = "/export/home/bwiley4/tmp"
        fa_file = tmpdirname + "/" + fa.id.split("|")[-1] + ".fasta"
        try: 
            output_handle = open(fa_file, "w")
            SeqIO.write(fa, fa_file, format="fasta")
            output_handle.close()
            test = "ok"
        except Exception as e1:
            test = e1

        ## blast
        header = re.compile("^#")
        Fields = re.compile("# Fields")
        # https://www.biostars.org/p/88944/
        my_env = os.environ.copy()
        ## for path to blastp
        # my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]
        ## for path to blastp on the BFX3 server
        my_env["PATH"] = "/usr/bin:" + my_env["PATH"]
        ## for access to taxonomy database: taxdb
        # my_env["BLASTDB"] = "/Users/brian/uniprot_dbs"
        ## for access to taxonomy database: taxdb on BFX3 server
        my_env["BLASTDB"] = "/export/home/bwiley4/uniprot_dbs"
        
        ## need to adjust for short queries. NCBI does <=30
        ## also need to remove e-value=0.001 and set -task 'blastp-short'
        # https://www.biostars.org/p/47203/
        if len(fa.seq) <= 30:
            COMMAND = "/usr/bin/blastp -outfmt {} -query {} -db /export/home/bwiley4/uniprot_dbs/swissprot \
                -task 'blastp-short' -parse_deflines {} {} > {}\
                ".format('"7 std staxids qseq sseq sscinames scomnames stitle"',
                fa_file, tax_arg, tax_filter, tmpdirname + "/results.txt")
        else: 
            COMMAND = "/usr/bin/blastp -outfmt {} -query {} -db /export/home/bwiley4/uniprot_dbs/swissprot \
                -evalue {} -parse_deflines {} {} > {}\
                ".format('"7 std staxids qseq sseq sscinames scomnames stitle"',
                fa_file, 0.001, tax_arg, tax_filter, tmpdirname + "/results.txt")   
        subprocess.run(COMMAND, shell=True, env=my_env)

        hit_list = []
        with open(tmpdirname + "/results.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if header.match(line) and not Fields.search(line):
                    continue
                elif Fields.search(line):
                    line = line.replace("# Fields: ", '').rstrip()
                    colnames = [i.replace(" ", "_") for i in line.split(", ")]
                    colnames = [i.replace(".", "") for i in colnames]
                else:
                    hit_list.append(line)
    
    # https://stackoverflow.com/questions/54102980/convert-a-tab-and-newline-delimited-string-to-pandas-dataframe
    # https://stackoverflow.com/questions/29815129/pandas-dataframe-to-list-of-dictionaries/29816143#29816143
    # https://stackoverflow.com/questions/34584426/nested-for-loop-in-jinja2
    df = pd.DataFrame([x.split('\t') for x in hit_list], columns=colnames).to_dict('records')
    colnames.remove("subject_sci_names")
    colnames.insert(2,"subject_sci_names")
    colnames.remove("subject_title")
    colnames.insert(3,"subject_title")

    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('project_blast.html')
    print("Content-Type: text/html\n\n")
    print(template.render(final_df=df,
                          final_cols=colnames,
                          data=fa.format("fasta"),
                          fa_file=fa_file))
 
   
   
if __name__ == '__main__':
    main()