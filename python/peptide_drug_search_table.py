#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 01:24:39 2021

@author: brian
"""

###############################################################
# Create table for enter searches into database
###############################################################

## helper functions
import create_mysql_db
from create_mysql_db import *

user='bwiley4'
password='s3kr1t' # standard fake password
host='127.0.0.1'
db_name = "bwiley4"
cnx = connect(user, password, host)
cursor = cnx.cursor()
use_database(cnx, cursor, db_name)

TABLES = {}

## primary key is both query and subject uniprot id
## as well as start and end residues for both query and subject uniprot id
## IMPORTANT: MariaDB does not use JSON datatype. https://mariadb.com/kb/en/json-data-type/
TABLES['peptide_drug_searches'] = (
    "CREATE TABLE IF NOT EXISTS peptide_drug_searches ("
    "	 Query_accession_version CHAR(15) NOT NULL,"
    "    Subject_accession_version CHAR(15) NOT NULL,"
    "    Subject_Scientific_Names MEDIUMTEXT NOT NULL,"
    "    Subject_Title LONGTEXT NOT NULL,"
    "    Percent_identity FLOAT NOT NULL,"
    "    Alignment_length INT NOT NULL,"
    "    mismatches INT NOT NULL,"
    "    gap_opens INT NOT NULL,"
    "    query_start INT NOT NULL,"
    "    query_end INT NOT NULL,"
    "    subject_start INT NOT NULL,"
    "    subject_end INT NOT NULL,"
    "    e_value FLOAT NOT NULL,"
    "    bit_score INT NOT NULL,"
    "    subject_tax_id INT NOT NULL,"
    "    Query_seq LONGTEXT NOT NULL,"
    "    Subject_seq LONGTEXT NOT NULL,"
    "    Subject_common_name VARCHAR(200) NOT NULL,"    
    "    drugbank_ids LONGTEXT DEFAULT NULL,"
    "    PRIMARY KEY (Query_accession_version, Subject_accession_version, query_start, query_end, subject_start, subject_end)"
    ") ENGINE=InnoDB"
);

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
            
            
# TABLES = ["genes", "organisms"]
# for table in TABLES:
#     drop_table(cursor, db_name, table)
    
