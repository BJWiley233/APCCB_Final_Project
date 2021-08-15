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

    # for adding searches to db
    user='bwiley4'
    password='s3kr1t'
    # host='localhost'
    host='127.0.0.1'
    db_name = "bwiley4"

    cnx = mysql.connector.connect(user=user, 
                                  password=password,
                                  host=host,
                                  database=db_name)
    cursor = cnx.cursor()

    data = cgi.FieldStorage()
    # https://stackoverflow.com/questions/16527259/accessing-fields-with-python-cgi-fieldstorage-from-a-jquery-ajax-call
    # needs <storage>.value
    # https://stackoverflow.com/questions/10973614/convert-json-array-to-python-list/10973648
    up_ids = [id.split(".")[0] for id in json.loads(data['up_ids'].value)] ## for summary json
    All_UniProt_IDs = [id for id in json.loads(data['up_ids'].value)]
    up_id_drugbank_json = {}
    mysql_rows = json.loads(data['rows'].value)
    
    
    # https://github.com/BJWiley233/Practical-Computer-Concepts-Files/blob/master/Database_Project/fill_protein_table_uniprot.py
    uniprot_url = "https://www.uniprot.org/uniprot/{}.xml"
    ## for XML namespace for alt names and pdbs
    ns = {'up': 'http://uniprot.org/uniprot'}
    
   
    # make results folder to tar up.  this folder will include a subfolder for each UniProt ID
    # which will contain sdf files for each DrugBank ID associated with that UniProt ID.
    # the final cgi page will allow user to move this directory to one of their choice
    import subprocess
    # THIS DOESN'T WORK NOW!!
    # tmp = "/tmp/bwiley4/final"
    # THIS WORKS because I have permissions
    tmp = "/export/home/bwiley4/tmp/final"
    # first remove last search "final" folder
    subprocess.run('if [ -d {} ]; then rm -r {}; fi'.format(tmp, tmp), shell=True)
    subprocess.run("mkdir {}".format(tmp), shell=True)
    summary_json_file = tmp + "/summary.json"
    
    # # keep a log of failed Uniprot IDs which will go under the main tar folder
    uniprot_fetch_log = tmp + "/uniprot_fetch_errors.log"
    sql_log_file = "logs/sql_not_entered.log"
    open(uniprot_fetch_log, 'w').close()
    open(sql_log_file, 'w').close()

    good_uniprot_fetch_count = 0
    bad_uniprot_fetch_count = 0
    good_drugbank_fetch_count = 0
    bad_drugbank_fetch_count = 0
    
    uniprot_fetches_json = {"Fetch_Succeeded": [], "Fetch_Failed": []} ## for summary
    drugbank_fetches_json = {"Fetch_Succeeded": [], "Fetch_Failed": []} ## for summary
    All_DrugBank_IDs = [] ## all DrugBankIDs for summary

    for key, val in mysql_rows.items():
        up_id_version = val[1]
        up_id_drugbank_json[up_id_version] = {} ## for summary
        ## to get XML url correct
        up_id = up_id_version.split(".")[0]
        try:
            xml_req = requests.get('https://www.uniprot.org/uniprot/{}.xml'.format(up_id))
            xml_req.raise_for_status()
            
            # we are good so create the subfolder
            good_uniprot_fetch_count += 1
            uniprot_fetches_json["Fetch_Succeeded"].append(up_id)
            up_folder = tmp + "/" + up_id
            subprocess.run("mkdir -p " + up_folder, shell=True)
            
            # add json to the UniProt folder for failed and succeeded DrugBank ID fetches
            # this is because mAB drugs are not going to have sdf files 
            # (mostly because mAB drugs are "fairly new" + these drugs are proprietary)
            uniprot_drugbank_fetch_json = tmp + "/" + up_id + "/drugbank_fetch.json"
            open(uniprot_drugbank_fetch_json, 'w').close()
            
            tree = ET.fromstring(xml_req.content)
           
            drugBankIDs = []
            for db_node in tree.findall("./up:entry/up:dbReference[@type='DrugBank']", ns):
                id_ = db_node.attrib['id']
                name_ = db_node.find("./up:property", ns).attrib['value']
                drugBankIDs.append({"DrugBank ID": id_, "Generic Name": name_})
            ## for summary will be blank [] if none but will have all successfull Uniprot fetches
            up_id_drugbank_json[up_id_version]['Drugs'] = drugBankIDs 
            
            if len(drugBankIDs) == 0:
                ## part of summary at end. just printing the json to screen and adding to each
                ## UniProt ID folder as I ran out of time
                db_json = {}
                db_json["Fetch_Failed"] = "No DrugBank IDs for " + up_id
                ## this will also be blank if no fetches
                up_id_drugbank_json[up_id_version]['Drug_Fetches'] = db_json
                ## add search selection to database but NULL for drugbank_ids
                try:
                    cursor.execute(
                        "REPLACE INTO peptide_drug_searches VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7],
                         val[8],val[9],val[10],val[11],val[12],val[13],val[14],val[15],
                         val[16],val[17], None))
                    cnx.commit()
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
                    with open(sql_log_file, 'a') as f:
                        f.write(f"{val}\n\n")
                
            else:
                db_json = {"Fetch_Succeeded": [], "Fetch_Failed": []}
                ## after getting DB ids load into mysql the json blast rows plus json array column of DrugBank IDs
                # TODO: insert in MySQL if we have time
                # Adding JSON types are best for Databases like MongoDB and those that have JSON object query languages
                try:
                    cursor.execute(
                        "REPLACE INTO peptide_drug_searches VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7],
                         val[8],val[9],val[10],val[11],val[12],val[13],val[14],val[15],
                         val[16],val[17], json.dumps(drugBankIDs)))
                    cnx.commit()
                except mysql.connector.Error as err:
                    print("Something went wrong: {}".format(err))
                    with open(sql_log_file, 'a') as f:
                        f.write(f"{val, json.dumps(drugBankIDs)}\n\n")
                
                
                for drug in drugBankIDs:
                    All_DrugBank_IDs.append(drug) ## Total DrugBank IDs for Summary
                    ## try to get .sdf files. DrugBank only has sdf files for small molecules not mAB drugs
                    ## not using their curl API so literally the sdf file links I have seen only contain
                    ## "small_molecule_drugs" as the entry point
                    try:
                         db_req = requests.get('https://go.drugbank.com/structures/small_molecule_drugs/{}.sdf'.format(drug['DrugBank ID']))
                         db_req.raise_for_status()
                         # we are good. add to "Fetch_Succeeded"
                         good_drugbank_fetch_count += 1
                         db_json["Fetch_Succeeded"].append(drug)
                         drugbank_fetches_json["Fetch_Succeeded"].append(drug)
                         with open(up_folder + "/"+ drug['DrugBank ID'] + ".sdf", "w") as fw:
                             fw.write(db_req.text)
                    except requests.exceptions.HTTPError as e:
                        bad_drugbank_fetch_count += 1
                        db_json["Fetch_Failed"].append(drug)
                        drugbank_fetches_json["Fetch_Failed"].append(drug)
                up_id_drugbank_json[up_id_version]['Drug_Fetches'] = db_json # for summary
            
            ## write up_id_drugbank_json[up_id_version] JSON to the UniProt subdirectory
            with open(uniprot_drugbank_fetch_json, 'w') as jw:
                jw.write(json.dumps(db_json, indent=4))
                                    
        except requests.exceptions.HTTPError as e:
            bad_uniprot_fetch_count += 1
            uniprot_fetches_json["Fetch_Failed"].append(up_id_version)
            with open(uniprot_fetch_log, 'a') as f:
                f.write("Error getting XML for {}\n".format(up_id))

    ## add fasta to folder if checked, yes by default
    if data['include_search'].value:
        subprocess.run("cp {} {}".format(data['file'].value, tmp), shell=True)
    
    ## Summary JSON is also included in final.tar.gz
    num_fetches_json = {
        "Number good Uniprot fetches": good_uniprot_fetch_count,
        "Number bad Uniprot fetches": bad_uniprot_fetch_count,
        "Number good DrugBank fetches": good_drugbank_fetch_count,
        "Number bad DrugBank fetches": bad_drugbank_fetch_count,
    }
    summary_json = {
        "Fetch_Summary": num_fetches_json,
        "UniProt_DrugBankIDs": up_id_drugbank_json,
        "All_Uniprot_IDs": All_UniProt_IDs,
        "All_DrugBank_IDs": All_DrugBank_IDs,
        "All UniProt_Fetches": uniprot_fetches_json,
        "All DrugBank_Fetches": drugbank_fetches_json
    }
    ## write sumary
    with open(summary_json_file, 'w') as jw:
        jw.write(json.dumps(summary_json, indent=4))

    ## doesn't work
    # final_tar = tmp + ".tar.gz"
    # subprocess.run("tar -zcvf {} {}".format(final_tar, tmp), shell=True)

    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('summary_and_save_location.html')
    print("Content-Type: text/html\n\n")
    
    ## want to transfer this to the download.cgi for display, needed more time
    # print(template.render(summary=json.dumps(summary_json, indent=4)))
    print(template.render())
    
    
    
if __name__ == '__main__':
    main()




