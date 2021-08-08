#!/usr/local/bin/python3

# import mysql.connector
# from mysql.connector import errorcode
import jinja2
import cgi,cgitb 
cgitb.enable() 



def main():
    # conn = mysql.connector.connect(user='bwiley4', password='s3kr1t',
    #                                host='localhost', database='bwiley4_chado')
    # column_names=['f.uniquename', 'product', 'f.feature_id', 'cv.name', 'cv.term_id', 'cv.definition'] 
    
    data = cgi.FieldStorage()

    templateLoader = jinja2.FileSystemLoader( searchpath="./templates" )
    env = jinja2.Environment(loader=templateLoader)
    template = env.get_template('summary_and_save_location.html')
    print("Content-Type: text/html\n\n")
    print(template.render(data=data))
    
    
    
    
if __name__ == '__main__':
    main()




