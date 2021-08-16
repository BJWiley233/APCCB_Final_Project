### About
This is my project for which there are two options to run [blastp](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE=Proteins)
in on the SwissProt/UniProt Database.  From there the user will be
able to select hits of protein accession IDs to submit for obtaining
all the [SDF](https://en.wikipedia.org/wiki/Chemical_table_file#SDF) files
of [DrugBank]https://go.drugbank.com/) drugs associated with those
proteins selected
#### Source code can be obtained from [here](https://github.com/BJWiley233/APCCB_Final_Project/releases/tag/0.0.1):


### Requirements
* For the autocomplete functionality for UniProt protein search option
you must create the MySQL database and load the `unprot_fasta` table with 
all entries from the fasta file.  
* The [Reviewed (Swiss-Prot)](https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz) fasta download is also required for this step.
* Download of the [taxonomy database] for utilizing the organism tax search functionality
* Both SwissProt and Tax database should be located in a folder on the home directory named `uniprot_dbs/`
* You must create the local SwissProt database with the code:
```sh
makeblastdb -in uniprot_sprot.fasta -title swissprot -out uniprot_dbs/swissprot -dbtype prot
```
* The taxonmy archive file must be untarred in the same directory
<br>

### Detailed Usage
For both options you can filter by organism using the drop drop for the main
model organisms as well as enter a comma separated list of taxids such as:
```sh
9606,559292,10090,10029
```
Even if you add spaces they will be trimmed.  This also overrides the [multiselect](http://davidstutz.github.io/bootstrap-multiselect/#examples) dropdown.

**Search Option 1:**
<br>
Option 1 the left side of [search.html](https://github.com/BJWiley233/APCCB_Final_Project/blob/main/search.html)
* Using this option you can enter your peptide sequence manually as if it came right off the Mass Spectrometer.  You have to input a valide fasta sequence include a name line starting with `>` as well as line break for your sequence.  There are checks for both and you will be prompted to update any invalid input.  You can also incude a job name for the fasta sequence just like NCBI has an input fro [Job Title](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome)
<br>

**Search Option 2:**
<br>
Option 2 on the right side allows you to also enter a UniProtID like in NCBI except that NCBI does this in the same input.  This was easier to separate.  You can start typing in the `Enter a UniProt(SwissProt) ID:` input and there will be an autocomplete search while you type that contains a description of all 565,254 UniProt entries from their [Reviewed (Swiss-Prot)](https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz) fasta download.  The description is in the format:
```sh
uniprot_id : gene_name (organism_scientific) : protein_name
```
You can also select a start and end residue for your search like on the NCBI blastp interface.

**Blastp Submission**
After click the blast button there will be a slight delay while the blastp program
is running.  This is expedited by having a local database.

On the blast results page you will see a table of the results.  The entire table is filterable as well as each column.  Normally you may be interested in filter for the species.  To obtain the SDF files associated with each hit check the box of the line for that hit.  You may select the check all box as well filter by a column and the select all will be maintained for that filter.

**DrugBank SDF fetches**
Click the `Get Drug Bank .sdf files` button after you have selected all your hits.  Upon select 10 or more lines you will be warned this can take a while.  After clicking fetch button there will be a loading wheel that appears until all the protein Accessions and DrugBank drug fetches have been completed and SDF files are ready to download.

**Results saving**
After the fetches have been completed you will be brought to a page that will allow you to input a name for the




### Files included

#### HTML Files
1. Search page [search.html](https://github.com/BJWiley233/APCCB_Final_Project/blob/main/search.html)
2. [Templates](https://github.com/BJWiley233/APCCB_Final_Project/tree/main/templates)

#### CGI Files
1. Blastp [project_blast.cgi](https://github.com/BJWiley233/APCCB_Final_Project/blob/main/project_blast.cgi)
2. DrugBank SDF [drugbank_sdfs.cgi](https://github.com/BJWiley233/APCCB_Final_Project/blob/main/drugbank_sdfs.cgi)
3. Download [download.cgi](https://github.com/BJWiley233/APCCB_Final_Project/blob/main/download.cgi)
4. Tar file creation for search [create_tar.cgi](https://github.com/BJWiley233/APCCB_Final_Project/blob/main/create_tar.cgi)

#### Python 
1. [Files](https://github.com/BJWiley233/APCCB_Final_Project/tree/main/python) for creating database and tables and loading autocomplete table.

#### [Javascript](https://github.com/BJWiley233/APCCB_Final_Project/tree/main/js), [CSS](https://github.com/BJWiley233/APCCB_Final_Project/tree/main/css), and [img](https://github.com/BJWiley233/APCCB_Final_Project/tree/main/img)

#### Path to final project directory on the BFX3 server with the start `search.html` page:
`/var/www/html/bwiley4/APCCB_Final_Project`