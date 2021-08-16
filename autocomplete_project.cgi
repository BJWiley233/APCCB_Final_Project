#!/usr/local/bin/python3

import cgi, json
import os
import mysql.connector

def main():
    print("Content-Type: application/json\n\n")
    form = cgi.FieldStorage()

    uniprot_search = form.getvalue('uniprot_id')
    conn = mysql.connector.connect(user='bwiley4', password='s3kr1t', host='localhost', database='bwiley4')
    cursor = conn.cursor()
    
    qry = """
          SELECT uniprot_id, gene_name, protein_name, organism_scientific
          FROM bwiley4.unprot_fasta 
          WHERE uniprot_id LIKE %s or gene_name LIKE %s or protein_name LIKE %s
          LIMIT 100; 
    """
    cursor.execute(qry, ('%'+uniprot_search+'%', '%'+uniprot_search+'%', '%'+uniprot_search+'%'))

    results = []
    for (product) in cursor:
        # results.append({'label': product[0],'value': product[0]})
        results.append({'label': "{} : {} ({}) : {}".format(product[0], product[1], product[3], product[2]),
                        'value': product[0]})

    conn.close()
    print(json.dumps(results))


if __name__ == '__main__':
    main()
