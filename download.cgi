#!/usr/local/bin/python3

# import mysql.connector
# from mysql.connector import errorcode
import jinja2
import cgi,cgitb 
cgitb.enable() 



def main():
 
    
    data = cgi.FieldStorage()

    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('summary_and_save_location.html')
    print("Content-Type: text/html\n\n")
    ## Doesn't work
    # Need to be able tp pass "summary_json" from drugbank_sdfs.cgi to download.cgi
    # print(template.render(summary_json=summary_json))
    print(template.render(data=data))

    
    
    
    
if __name__ == '__main__':
    main()