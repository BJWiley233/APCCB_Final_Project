#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 14:04:13 2021

@author: brian
"""

###############################################################
# This initial db is just for autocomplete for the 2nd entry
# option to select an existing protein id with option start
# and end residue positions
# Code from https://github.com/BJWiley233/Practical-Computer-Concepts-Files/blob/master/Database_Project/fill_protein_table_uniprot.py
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
from Bio import SeqIO


user='bwiley4'
password='s3kr1t'
host='127.0.0.1'
#db_name = "peptide_to_drugs"
db_name = "bwiley4"

cnx = connect(user, password, host)
cursor = cnx.cursor()
# =============================================================================
# conn = mysql.connector.connect(user='bwiley4', password='s3kr1t',
# =============================================================================

#create_database(cursor, db_name)
use_database(cnx, cursor, db_name)

TABLES = {}
## organism_scientific can be long
TABLES['unprot_fasta'] = (
    "CREATE TABLE IF NOT EXISTS unprot_fasta ("
    "	 uniprot_id CHAR(15) NOT NULL PRIMARY KEY,"
    "    entry_name VARCHAR(45) NOT NULL,"
    "    protein_name MEDIUMTEXT NOT NULL,"
    "    organism_scientific VARCHAR(200) NOT NULL,"
    "    organism_taxid INT NOT NULL,"
    "    gene_name VARCHAR(45),"
    "    protein_existence VARCHAR(45),"    
    "    seq_version INT"
    ") ENGINE=InnoDB"
);


# for table in TABLES:
#     drop_table(cursor, db_name, table)


for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table: {}".format(table_name))
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table already exists")
        else:
            print(err.msg)



records = SeqIO.parse(os.path.expanduser("~/uniprot_dbs/uniprot_sprot.fasta"), "fasta")
records = list(records)
len(records[:5]) + len(records[5:]) == len(records)

## fasta format from Uniprot/SwissProt
## >db|UniqueIdentifier|EntryName ProteinName OS=OrganismName OX=OrganismIdentifier [GN=GeneName ] PE=ProteinExistence SV=SequenceVersion
protein_existence_dict = {
    '1': "Experimental evidence at protein level",
    '2': "Experimental evidence at transcript level",
    '3': "Protein inferred from homology",
    '4': "Protein predicted",
    '5': "Protein uncertain"
}
# =============================================================================
# uniprot_id, entry_name, protein_name, organism_scientific, organism_taxid, gene_name (GN=FV3-001R), 
# protein_existence_id, protein_existence_value, sequence_version
# =============================================================================
log_file = "logs/uniprot_not_entered.log"
# https://stackoverflow.com/questions/7124778/how-to-match-anything-up-until-this-sequence-of-characters-in-a-regular-expres
## description is everything after id/name to OS=OrganismName
prot_name = re.compile(".+?(?=\sOS=)")

## keep track of 565254 records
i=0
for record in records:
    print(i)
    # =============================================================================
    # uniprot_id, entry_name, protein_name, organism_scientific, & organism_taxid 
    # must be valide
    # =============================================================================
    try:
        id_name = record.id.split("|")
        uniprot_id = id_name[1]
        entry_name = id_name[2]
        ## not sure why biopython add the id into the description
        description = record.description.replace(record.id + " ","")
        protein_name = prot_name.search(description).group(0)
        # https://stackoverflow.com/questions/32680030/match-text-between-two-strings-with-regular-expression
        # some tags are missing such as gene_name for use \s[A-Z]{2}= for after matching tag
        organism_scientific = re.search('OS=(.*?)\s[A-Z]{2}=', description).group(1)
        organism_taxid = re.search('OX=(.*?)\s[A-Z]{2}=', description).group(1)
        
        try:
            gene_name = re.search('GN=(.*?)\s[A-Z]{2}=', description).group(1)
        except:
            gene_name = None
        try:
            protein_existence = protein_existence_dict[re.search('PE=(.*?)\s[A-Z]{2}=', description).group(1)]
        except:
            protein_existence = None
        try:
            seq_version = re.search('SV=(.*)', description).group(1)
        except:
            seq_version = None
    except:
        print("invalid fasta entry for " + str(i))
        i+=1
        next
        
    ## if valid enter in db
    try:
        cursor.execute(
            "REPLACE INTO unprot_fasta VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (uniprot_id, entry_name, protein_name, organism_scientific, organism_taxid,
             gene_name, protein_existence, seq_version))
        cnx.commit()
        i+=1
    except mysql.connector.Error as err:
        i+=1
        print("Something went wrong: {}".format(err))
        with open(log_file, 'a') as f:
            f.write(f"{record}\n\n")
        

    

