#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------
            Query CyberShake SQL Database
--------------------------------------------------------
General purpose script to query the CybeShake SQL
    server for simulation metadata and save outputs
"""

# Built-in/Generic Imports
import os
import sys
import json
from tabulate import tabulate
import mysql.connector as mysql
# […]

__author__     = "Scott Condon"
__copyright__  = "Copyright 2021"
__credits__    = ["Scott Condon"]
__license__    = "MIT"
__version__    = "1.0.0"
__maintainer__ = "Scott Condon"
__email__      = "scott@scondon.com"
__status__     = "Stable"


# independent functions --------------------------------

def read_input():
    content = []
    while True:
        line = input()
        if line:
            content.append(line)
        else:
            break
    output = '\n'.join(content)
    return(output)

def print_results(results,head):
    print(tabulate(results, headers=head, tablefmt='psql'))
    print()
    
def test_connection():
    print("(testing connection...)")
    try:
        connection = mysql.connect(
            host = 'focal.usc.edu',
            user = 'cybershk_ro',
            password = 'CyberShake2007',
            database = 'CyberShake')
        
        # create cursor with mysql connection
        cursor = connection.cursor()
        # execute sql query with cursor
        cursor.execute("show tables;")
        print("(connected to focal.usc.edu)")
        return(True)
    except:
        print("(could not connect to focal.usc.edu)")
        return(False)
    

# dependent functions ----------------------------------

def get_query(count):
    tmp = "query " + str(count) + ":\n"
    print(tmp)
    query = read_input()
    return(query)

def ask_write():
    print("write(y/n):")
    tmp = read_input()
    if tmp == 'y' or tmp == 'Y':
        tmp = True
    else:
        tmp = False
    return(tmp)

def write_table(results,head):
    print("outfile name:")
    tmp = read_input()
    try:
        fout = open(tmp,"w")
        fout.write(tabulate(results, headers=head, tablefmt="plain"))
    except:
        print("(could not write file)")

def execute_query(query):
    try:
        connection = mysql.connect(
            host = 'focal.usc.edu',
            user = 'cybershk_ro',
            password = 'CyberShake2007',
            database = 'CyberShake')
    
        # create cursor with mysql connection
        cursor = connection.cursor()
        # execute sql query with cursor
        cursor.execute(query)
        # get results with fetchall
        results = cursor.fetchall()
        # get headers from fetchall
        head = []
        for i in cursor.description:
            head.append(i[0])
        # return results and headers
        return(results, head)
    except:
        print("(mysql query not valid)")


# main program -----------------------------------------

def main():
    count = 1
    print("start")
    flag = test_connection()
    while flag == True:
        query = get_query(count)
        count += 1
        if query == '':
            break
        else:
            try:
                results,head = execute_query(query)
                print_results(results,head)
                if ask_write() == True:
                    write_table(results,head)
                else:
                    pass
            except:
                pass
    print("end")


# execute main -----------------------------------------

if __name__=='__main__':
    main()
