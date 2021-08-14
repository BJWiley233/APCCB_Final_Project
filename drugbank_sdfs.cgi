#!/usr/local/bin/python3

import mysql.connector
from mysql.connector import errorcode
import jinja2
import json
import cgi,cgitb 
import requests
import numpy as np
import json
import xml.etree.ElementTree as ET
import re
cgitb.enable() 



def main():

    user='bwiley4'
    password='s3kr1t'
    host='127.0.0.1'
    db_name = "bwiley4"

    cnx = mysql.connector.connect(user=user, 
                                  password=password,
                                  host=host,
                                  database=db_name)
    cursor = cnx.cursor()

    data = cgi.FieldStorage()
    # https://stackoverflow.com/questions/16527259/accessing-fields-with-python-cgi-fieldstorage-from-a-jquery-ajax-call
    # needs <storgae>.value
    # https://stackoverflow.com/questions/10973614/convert-json-array-to-python-list/10973648
    up_ids = [id.split(".")[0] for id in json.loads(data['up_ids'].value)]
    mysql_rows = json.loads(data['rows'].value)
    
    
    # https://github.com/BJWiley233/Practical-Computer-Concepts-Files/blob/master/Database_Project/fill_protein_table_uniprot.py
    uniprot_url = "https://www.uniprot.org/uniprot/{}.xml"
    ## for XML namespace for alt names and pdbs
    ns = {'up': 'http://uniprot.org/uniprot'}
    
    
    ## for appending must create
   
    # make results folder to tar up.  this folder will include a subfolder for each UniProt ID
    # which will contain sdf files for each DrugBank ID associated with that UniProt ID.
    # the final cgi page will allow user to move this directory to one of their choice
    import subprocess
    # first remove last search
    subprocess.run('if [ -d {} ]; then rm -Rf {}; fi'.format("/tmp/bwiley4/final", "/tmp/bwiley4/final"), shell=True)
    subprocess.run("mkdir /tmp/bwiley4/final", shell=True)
    
    # keep a log of failed Uniprot IDs which will go under the main tar folder
    uniprot_fetch_log = "/tmp/bwiley4/final/uniprot_fetch_errors.log"
    sql_log_file = "logs/sql_not_entered.log"
    open(uniprot_fetch_log, 'w').close()
    open(sql_log_file, 'w').close()

    good_uniprot_fetch_count = 0
    bad_uniprot_fetch_count = 0
    good_drugbank_fetch_count = 0
    bad_drugbank_fetch_count = 0
    
    
    #for up_id in up_ids:
    for key, val in mysql_rows.items():
        up_id = val[1].split(".")[0]
        try:
            xml_req = requests.get('https://www.uniprot.org/uniprot/{}.xml'.format(up_id))
            xml_req.raise_for_status()
            
            # we are good so create the subfolder
            good_uniprot_fetch_count += 1
            up_folder = "/tmp/bwiley4/final/"+up_id
            subprocess.run("mkdir -p "+up_folder, shell=True)
            
            # add json to the UniProt folder for failed and succeeded DrugBank ID fetches
            # this is because mAB drugs are not going to have sdf files 
            # (mostly because mAB drugs are "fairly new" + these drugs are proprietary)
            uniprot_drugbank_fetch_json = "/tmp/bwiley4/final/"+up_id+"/drugbank_fetch.json"
            open(uniprot_drugbank_fetch_json, 'w').close()
            db_json = {"Fetch_Succeeded": [], "Fetch_Failed": []}
            
            tree = ET.fromstring(xml_req.content)
           
            drugBankIDs = [i.attrib['id'] for i in tree.findall("./up:entry/up:dbReference[@type='DrugBank']", ns)]
            drugBankIDs = []
            for db_node in tree.findall("./up:entry/up:dbReference[@type='DrugBank']", ns):
                id_ = db_node.attrib['id']
                name_ = db_node.find("./up:property", ns).attrib['value']
                drugBankIDs.append({"DrugBank ID": id_, "Generic Name": name_})
            
            if len(drugBankIDs) == 0:
                ## part of summary at end. just printing the json to screen and adding to each
                ## UniProt ID folder as I ran out of time
                db_json["Fetch_Failed"].append("No DrugBank IDs for "+up_id)
                ## add search selection to database but NULL for drugbank_ids
                try:
                    cursor.execute(
                        "REPLACE INTO peptide_searches VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7],
                         val[8],val[9],val[10],val[11],val[12],val[13],val[14],val[15],
                         val[16],val[17], None))
                    cnx.commit()
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
                    with open(sql_log_file, 'a') as f:
                        f.write(f"{val}\n\n")
                
            else:
                
                ## after getting DB ids load into mysql the json blast rows plus json array column of DrugBank IDs
                # TODO: insert in MySQL if we have time
                # Adding JSON types are best for Databases like MongoDB and those that have JSON object query languages
                try:
                    cursor.execute(
                        "REPLACE INTO peptide_searches VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7],
                         val[8],val[9],val[10],val[11],val[12],val[13],val[14],val[15],
                         val[16],val[17], json.dumps(drugBankIDs)))
                    cnx.commit()
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
                    with open(sql_log_file, 'a') as f:
                        f.write(f"{val, json.dumps(drugBankIDs)}\n\n")
                
                
                for drug in drugBankIDs:
                    ## try to get .sdf files. DrugBank only has sdf files for small molecules not mAB drugs
                    try:
                         db_req = requests.get('https://go.drugbank.com/structures/small_molecule_drugs/{}.sdf'.format(drug['DrugBank ID']))
                         db_req.raise_for_status()
                         # we are good. add to "Fetch_Succeeded"
                         good_drugbank_fetch_count += 1
                         db_json["Fetch_Succeeded"].append(drug)
                         with open(up_folder + "/"+ drug['DrugBank ID'] + ".sdf", "w") as fw:
                             fw.write(db_req.text)
                    except requests.exceptions.HTTPError as e:
                        bad_drugbank_fetch_count += 1
                        db_json["Fetch_Failed"].append(drug)
            with open(uniprot_drugbank_fetch_json, 'w') as jw:
                jw.write(json.dumps(db_json, indent=4))
                                    
        except requests.exceptions.HTTPError as e:
            bad_uniprot_fetch_count += 1
            with open(uniprot_fetch_log, 'a') as f:
                f.write("Error getting XML for {}\n".format(up_id))

    ## add fasta to folder if checked
    if data['include_search'].value:
        subprocess.run("cp {} /tmp/bwiley4/final".format(data['file'].value), shell=True)
    final_tar = "/tmp/bwiley4/final.tar.gz"
    subprocess.run("tar -zcvf {} /tmp/bwiley4/final".format(final_tar), shell=True)

    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('summary_and_save_location.html')
    print("Content-Type: text/html\n\n")
    # print(template.render(final_tar=final_tar,
    #                       final_folder="/tmp/bwiley4/final"))
    print(template.render(rows=mysql_rows,
                          rows_type=mysql_rows.items()))
    # print(template.render(data=data,
    #                       up_ids=up_ids,
    #                       file=data['file'].value,
    #                       final_tar=final_tar))
    
    
    
    
    
if __name__ == '__main__':
    main()




