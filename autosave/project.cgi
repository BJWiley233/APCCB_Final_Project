#!/Users/brian/anaconda3/bin/python



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
    # organisms = form.getlist("organisms")
    organisms = [9606, 10090, 10116, 10029, 83333, 559292, 3702, 7227, 9913, 9598]
    tax_filter = ",".join([str(i) for i in organisms])
    
    fasta_io = StringIO(search_entry)
    fasta = SeqIO.parse(fasta_io, "fasta")
    fa = [record for record in fasta][0]
 
    
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        fa_file = tmpdirname + "/" + fa.id.split("|")[-1] + ".fasta"
        fa_file = "/Users/brian/JHU_Summer/final_project/" + fa.id.split("|")[-1] + ".fasta"
        SeqIO.write(fa, fa_file, format="fasta")
        #record = SeqIO.read(fa_file, "fasta")
   
    
        ## blast
        header = re.compile(b"^#")
        Fields = re.compile(b"# Fields")
        # https://www.biostars.org/p/88944/
        # blastp -outfmt "7 std staxids" -query Q14181_chg.fasta -db swissprot -evalue 0.001 -taxids 9606,9913
        my_env = os.environ.copy()
        ## for path to blastp
        my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]
        ## for access to taxonomy database: taxdb
        my_env["BLASTDB"] = "/Users/brian/uniprot_dbs"
        
        COMMAND = "blastp -outfmt {} -query {} -db ~/uniprot_dbs/swissprot \
                   -evalue {} -parse_deflines -taxids {}\
                   ".format('"7 std staxids qseq sseq sscinames"',
                   fa_file, 0.001, tax_filter)
        proc = subprocess.Popen(COMMAND,
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
        # https://stackoverflow.com/questions/29815129/pandas-dataframe-to-list-of-dictionaries/29816143#29816143
        # https://stackoverflow.com/questions/34584426/nested-for-loop-in-jinja2
        df = pd.DataFrame([x.decode("utf-8").split('\t') for x in hit_list], columns=colnames).to_dict('records')
        #import json
        #df = [x.decode("utf-8").split('\t') for x in hit_list]
    
    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('project.html')
    print("Content-Type: text/html\n\n")


    print(template.render(final_df=df,
                          final_cols=colnames))
    
      
    
if __name__ == '__main__':
    main()
    



