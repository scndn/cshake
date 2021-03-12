#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------
                    Fetch Metadata
--------------------------------------------------------
Fetch available metadata from CyberShake SQL server giv-
en list of Run_IDs, Source_IDs, and Rupture_IDs
"""

# Built-in/Generic Imports
import os
import numpy as np
import pandas as pd
import mysql.connector as mysql
from tabulate import tabulate
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

def query_var_id(run_id,src_id,rup_id):
    
    SELECT = "select V.Source_ID, V.Rupture_ID, max(V.Rup_Var_ID)"
    FROM   = "from Rupture_Variations V, CyberShake_Runs CR"
    WHERE  = "where CR.Run_ID={run_id}"
    AND1   = "and CR.ERF_ID=V.ERF_ID"
    AND2   = "and V.Rup_Var_Scenario_ID=CR.Rup_Var_Scenario_ID"
    AND3   = "and V.Source_ID={src_id} and V.Rupture_ID={rup_id};"
    
    temp = [SELECT,FROM,WHERE,AND1,AND2,AND3]
    temp = " ".join(map(str, temp))
    query = temp.format(run_id=run_id,src_id=src_id,rup_id=rup_id)
    
    return(query)

def meta_query(run_id,src_id,rup_id,var_id):
    query = "select CR.Run_ID, R.Source_ID, R.Rupture_ID, V.Rup_Var_ID, R.Source_Name, R.Mag, R.Prob, V.Hypocenter_Lat, V.Hypocenter_Lon, V.Hypocenter_Depth, CS.CS_Site_ID, CS.CS_Short_Name, CS.CS_Site_Lat, CS.CS_Site_Lon, CR.Model_Vs30, CR.Z1_0, CR.Z2_5 from CyberShake_Runs CR, Ruptures R, CyberShake_Sites CS, Rupture_Variations V where CR.ERF_ID=36 and CR.ERF_ID=R.ERF_ID and V.ERF_ID=CR.ERF_ID and CR.Rup_Var_Scenario_ID=6 and CS.CS_Site_ID=CR.Site_ID and CR.Run_ID={run} and R.Source_ID={source} and R.Rupture_ID={rupture} and V.Rup_Var_ID={rup_var} and CR.Rup_Var_Scenario_ID=V.Rup_Var_Scenario_ID and V.Source_ID=R.Source_ID and R.Rupture_ID=V.Rupture_ID;".format(run=run_id, source=src_id, rupture=rup_id, rup_var=var_id)
    return(query)
    
def execute_query(query):
    
    connection = mysql.connect(
        host = 'focal.usc.edu',
        user = 'cybershk_ro',
        password = 'CyberShake2007',
        database = 'CyberShake')
    
    # create cursor with mysql connection
    try:
        cursor = connection.cursor()
    except:
        print("(could not create cursor)")
            
    # execute sql query with cursor
    try:
        cursor.execute(query)
    except:
        print("(could not execute query)")
        
    # get results with fetchall
    try:
        results = cursor.fetchall()
    except:
        print("(could not fetchall)")
            
    # get headers from fetchall
    try:
        head = []
        for i in cursor.description:
            head.append(i[0])
    except:
        print("(could not get headers)")
    
    return(results, head)
    
    
# dependent functions ----------------------------------

def select_sources(all_rsr,outfile,times):
    """
    Select sources with greater than 50 sites.
    """
    # remove if file exists
    if os.path.exists(outfile):
        os.remove(outfile)
    
    # select source ids
    # load all_rsr get unique sources
    all_srcs = all_rsr["Source_ID"].unique()
    
    # empty target source array
    target_srcs = []
    
    # loop through all_rsr to find src_ids with greater than 50 run_ids
    for i in range(len(all_srcs)):
        temp_rsr = all_rsr[all_rsr["Source_ID"] == all_srcs[i]]
        all_runs = temp_rsr["Run_ID"].unique()
        if len(all_runs) >= 50:
            target_srcs.append(all_srcs[i])
            
    # sort srcs array get length
    target_srcs = sorted(target_srcs)
    n = len(target_srcs)
    
    # open outfile
    with open(outfile,'w') as fout:
    
        # loop over all target srcs
        for i in range(n):
            
            # assign temp src_id
            src_id = target_srcs[i]
            
            # get all rows with src_id[i]
            temp = all_rsr[all_rsr['Source_ID'] == src_id].copy()
            temp = temp.reset_index()
            n_temp = len(temp)
            
            # choose random run_id, rup_id
            j = np.random.randint(n_temp)
            rup_id = temp.loc[j,'Rupture_ID']
            run_id = temp.loc[j,'Run_ID']
            
            # find var_id
            temp_query = query_var_id(run_id,src_id,rup_id)
            results, head = execute_query(temp_query)
            temp_df = pd.DataFrame(results,columns=head)
            n_var = temp_df.iloc[0]['max(V.Rup_Var_ID)']
            
            # select random int from 0 to n_var
            var_id = np.random.randint(n_var)
            
            temp_line = [run_id,
                        src_id,
                        rup_id,
                        var_id]
        
            line = " ".join(map(str, temp_line))
            fout.write(line+'\n')
            print(line)
            
            # loop for how many sites we want
            for k in range(times-1):
                
                # choose random run_id
                j = np.random.randint(n_temp)
                run_id = temp.loc[j,'Run_ID']
            
                temp_line = [run_id,
                        src_id,
                        rup_id,
                        var_id]
            
                line = " ".join(map(str, temp_line))
                fout.write(line+'\n')
                print(line)
    fout.close()
    
    
# main program -----------------------------------------

def main():
    
    outfile = 'example_metadata'
    eventfile = 'example_events'
    
    # load run_ids, src_ids, and rup_ids from 15.4
    all_rsr = pd.read_csv('example_output',sep='\s+')

    # fetch event ids
    select_sources(all_rsr,eventfile,50)
    event = pd.read_csv(eventfile,sep=' ',header=None)
    n_event = len(event)
    
    # remove if file exists
    if os.path.exists(outfile):
        os.remove(outfile)
        
    # fetch metadata
    with open(outfile,'w') as fout:
        
        for i in range(1):
            
            run_id = event.loc[i,0]
            src_id = event.loc[i,1]
            rup_id = event.loc[i,2]
            var_id = event.loc[i,3]
            
            # execute query
            query = meta_query(run_id,src_id,rup_id,var_id)
            temp, head = execute_query(query)
            
            # format and write
            if temp == []:
                pass
            else:
                rout = list(temp[0])
                rout[4] = rout[4].replace(',',';')
    
                # join string
                head = ",".join(map(str, head))
                line = ",".join(map(str, rout))
    
                # write out
                fout.write(head+"\n")
                fout.write(line+"\n")
                print(line)
            
        for i in range(1,n_event):
            
            run_id = event.loc[i,0]
            src_id = event.loc[i,1]
            rup_id = event.loc[i,2]
            var_id = event.loc[i,3]
    
            # execute query
            query = meta_query(run_id,src_id,rup_id,var_id)
            temp, head = execute_query(query)
            
            # format and write
            if temp == []:
                pass
            else:
                rout = list(temp[0])
                rout[4] = rout[4].replace(',',';')
    
                # join string
                head = ",".join(map(str, head))
                line = ",".join(map(str, rout))
                
                # write out
                fout.write(line+"\n")
                print(line)
    fout.close()


# execute main -----------------------------------------

if __name__=='__main__':
    main()
