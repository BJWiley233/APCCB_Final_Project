#!/usr/local/bin/python3

# import mysql.connector
# from mysql.connector import errorcode
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
    open(uniprot_fetch_log, 'w').close()
    
    for up_id in up_ids:
        try:
            xml_req = requests.get('https://www.uniprot.org/uniprot/{}.xml'.format(up_id))
            xml_req.raise_for_status()
            #print("good")
            
            # we are good so create the subfolder
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
                db_json["Fetch_Failed"].append("No DrugBank IDs for "+up_id)
            else:
                 ## after getting DB ids load into mysql the json blast rows plus json array column of DrugBank IDs
                 # TODO: insert in MySQL if we have time
                for drug in drugBankIDs:
                    try:
                         db_req = requests.get('https://go.drugbank.com/structures/small_molecule_drugs/{}.sdf'.format(drug['DrugBank ID']))
                         db_req.raise_for_status()
                         # we are good. add to "Fetch_Succeeded"
                         db_json["Fetch_Succeeded"].append(drug)
                         with open(up_folder + "/"+ drug['DrugBank ID'] + ".sdf", "w") as fw:
                             fw.write(db_req.text)
                    except requests.exceptions.HTTPError as e:
                         db_json["Fetch_Failed"].append(drug)
            with open(uniprot_drugbank_fetch_json, 'w') as jw:
                jw.write(json.dumps(db_json, indent=4))
                                    
        except requests.exceptions.HTTPError as e:
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
    print(template.render(data=data,
                          up_ids=up_ids))
    # print(template.render(data=data,
    #                       up_ids=up_ids,
    #                       file=data['file'].value,
    #                       final_tar=final_tar))
    
    
    
    
    
if __name__ == '__main__':
    main()




