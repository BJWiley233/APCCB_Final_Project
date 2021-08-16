### About
This is my project for which there are two options to run blastp 
in on the SwissProt/UniProt Database.  From there the user will be
able to select hits of protein accession IDs to submit for obtaining
all the [SDF](https://en.wikipedia.org/wiki/Chemical_table_file#SDF) files
of [DrugBank]https://go.drugbank.com/) drugs associated with those
proteins selected

Source code can be obtained from here:
https://github.com/BJWiley233/APCCB_Final_Project/releases/tag/0.0.1
<br>

### Requirements
For the autocomplete functionality for UniProt protein search option
you must create the MySQL database and load the `unprot_fasta` table with 
all entries from the fasta file.  The [Reviewed (Swiss-Prot)](https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz) fasta download is also required for this step.
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
Option 2 on the right side allows you to also enter a UniProtID like in NCBI except that NCBI does this in the same input.  This was easier to separate.  You can start typing in the `Enter a UniProt(SwissProt) ID:` input and there will be an autocomplete search while you type that contains a description of all 565,254 UniProt entries from their [Reviewed (Swiss-Prot)](https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz) fasta download.  The description is in the format:
```sh
uniprot_id : gene_name (organism_scientific) : protein_name
```





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