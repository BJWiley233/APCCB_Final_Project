#!/usr/local/bin/python3
#!/Users/brian/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 14:04:13 2021

@author: brian
"""

###############################################################
# This initial db is just for autocomplete for the 2nd entry
# option to select an existing protein id with option start
# and end residue positions
###############################################################

import create_mysql_db
from create_mysql_db import *

import pandas as pd
from io import StringIO
import requests
import numpy as np
import json
import xml.etree.ElementTree as ET
import re
import os




up_tbl_cols = ["id", "entry name", "reviewed", "protein names", "genes(PREFERRED)",
               "genes(ALTERNATIVE)", "genes" , "interactor", "organism-id", "organism", 
               "families", "length", "database(MEROPS)"]


user='bwiley4'
password='s3kr1t'
host='127.0.0.1'
db_name = "peptide_to_drugs"

cnx = connect(user, password, host)
cnx = mysql.connector.connect(user=user, 
                                  password=password,
                                  host=host)
cursor = cnx.cursor()
# =============================================================================
# conn = mysql.connector.connect(user='bwiley4', password='s3kr1t',
# =============================================================================


create_database(cursor, db_name)
use_database(cnx, cursor, db_name)



from Bio import SeqIO

records = SeqIO.parse(os.path.expanduser("~/uniprot_dbs/uniprot_sprot.fasta"), "fasta")
domains = list(records)[0:100]
first = domains[0]
first.id
first.name
first.description
first.
## fasta format from Uniprot/SwissProt
## >db|UniqueIdentifier|EntryName ProteinName OS=OrganismName OX=OrganismIdentifier [GN=GeneName ] PE=ProteinExistence SV=SequenceVersion
protein_existence_dict = {
    1: "Experimental evidence at protein level",
    2: "Experimental evidence at transcript level",
    3: "Protein inferred from homology",
    4: "Protein predicted",
    5: "Protein uncertain"
}
uniprot_id, entry_name, protein_name, organism_scientific, organism_taxid, gene_name (GN=FV3-001R), 
protein_existence_id, protein_existence_value, sequence_version
# https://stackoverflow.com/questions/7124778/how-to-match-anything-up-until-this-sequence-of-characters-in-a-regular-expres
## description is everything after id/name to OS=OrganismName
prot_name = re.compile(".+?(?=OS=)")

for record in records:
    id_name = record.id.split("|")
    uniprot_id = id_name[1]
    entry_name = id_name[2]
    record.description
    ## not sure why biopython add the id into the description
    description = record.description.replace(record.id + " ","")
    protein_name = prot_name.search(description)
    
    

TABLES = {}
TABLES['proteinsUniprot'] = (
    "CREATE TABLE IF NOT EXISTS unprot_fasta ("
    "	 uniProtID CHAR(15) NOT NULL PRIMARY KEY,"
    "    entryName VARCHAR(45) NOT NULL,"
    "    reviewed BOOL NOT NULL,"
    "    proteinName MEDIUMTEXT NOT NULL,"
    "    alternateNames JSON DEFAULT NULL,"
    "    geneNamePreferred VARCHAR(45),"
    "    geneNamesAlternative JSON DEFAULT NULL,"
    "    geneNamesAll JSON DEFAULT NULL,"
    "    interactsWith JSON DEFAULT NULL,"
    "    taxid INT,"
    "    organism VARCHAR(100),"
    "    organismCommon MEDIUMTEXT,"
    "    proteinFamilies VARCHAR(255),"
    "    length INT,"
    "    meropsID VARCHAR(8) DEFAULT NULL,"
    "    headProteinFamily VARCHAR(45) NOT NULL"
    ") ENGINE=InnoDB"
);

TABLES['pdb'] = (
    "CREATE TABLE pdb ("
    "	 pdbID CHAR(5) NOT NULL PRIMARY KEY,"
    "    method VARCHAR(45) NOT NULL"
    ") ENGINE=InnoDB"
);