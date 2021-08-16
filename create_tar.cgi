#!/usr/local/bin/python3


import jinja2
import cgi,cgitb 
cgitb.enable() 
import tarfile
import os.path
import json
import subprocess
from subprocess import Popen, PIPE


import tempfile

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def main():
 
    data = cgi.FieldStorage()
    path = data['path'].value
    ## add "tmp/" so the tars will be in a tmp folder relative to APCCB_Final_Project folder
    ## and not cluttering up the project folder
    make_tarfile("tmp/"+path, "/export/home/bwiley4/tmp/final")

        
    ## Error checking at console
    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    ## For testing at console
    template = env.get_template('print_success.html')
    print("Content-Type: text/html\n\n")
    # print(template.render(path=COMMAND))
     
    
    
if __name__ == '__main__':
    main()