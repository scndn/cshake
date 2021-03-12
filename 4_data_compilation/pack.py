#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------
                     Pack Metadata
--------------------------------------------------------
Compile existing and compute additional metadata using
the earthquake source rupture files
"""

# Built-in/Generic Imports
import io
import os
import pandas as pd
from os import listdir
from nvector import *
import nvector as nv]
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
        
def get_lines(Fin):
    """Read file, count and separate lines."""
    Lines = []
    with open(Fin) as f:
        Lines = f.readlines()
    nLines = len(Lines)
    return(nLines,Lines)

def strip_lines(Lines):
    """Read file strip leading and trailing characters."""
    for i in range(len(Lines)):
        Lines[i] = Lines[i].strip()
    return(Lines)
    
def find_csv_filenames( path_to_dir, suffix=".grm" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

# main program -----------------------------------------

def main():
    
    out = pd.read_csv('out',sep=",")

    indir = "./seis/"
    outdir = "./post/"
    srcdir = "./source/"
    outfile = "meta"

    # remove if file exists
    if os.path.exists(outfile):
        os.remove(outfile)

    filenames = find_csv_filenames(indir)

    with open(outfile,'w') as fout:
    
        tmp_line = ["run_id","src_id","rup_id","var_id","source_name","mag","site_id","site_name","rrup","vs30","ztor","z10","z25","rake","acc_path","vel_path","source_path"]
        line = ",".join(map(str, tmp_line))
        fout.write(line+"\n")
    
        for fin in filenames:
            # out files
            infile = indir + fin
            name = fin.rsplit(".", 1)[0]
            temp = name.rsplit("_")
            run_id = temp[2]
            src_id = temp[3]
            rup_id = temp[4]
            var_id = temp[5]
            acc_out = outdir + name + "_acc" + ".grm"
            fout_png = outdir + name + ".png"
            fout_csv = outdir + name + ".csv"
            fout_acc_png = outdir + name + "_acc" + ".png"
            fout_acc_csv = outdir + name + "_acc" + ".csv"
    
            # get source file
            source_file = srcdir + str(src_id) + "_" + str(rup_id) + ".txt"
            # does file exist
            if os.path.exists(source_file):
                pass
            else:
                print("file doesnt exist",source_file)
    
            # load source_file
            Fin = source_file
            nLines, Lines = get_lines(Fin)
            Lines = strip_lines(Lines)
            Lines = Lines[6:len(Lines)]
            Lines.insert(0, "Lat Lon Depth Rake Dip Strike")
            source_pd = pd.read_csv(io.StringIO('\n'.join(Lines)), delim_whitespace=True,header=0)
            
            temp_out = out[(out['Source_ID'] == int(src_id)) & (out['Run_ID'] == int(run_id)) & (out['Rupture_ID'] == int(rup_id)) & (out['Rup_Var_ID'] == int(var_id))]
    
            # outline
            lat1 = temp_out['CS_Site_Lat'].values[0]
            lon1 = temp_out['CS_Site_Lon'].values[0]
            z1 = 0
            Rrup = 999
            ztor = 999
    
            wgs84 = nv.FrameE(name='WGS84')
            pointA = wgs84.GeoPoint(latitude=lat1, longitude=lon1, z=z1, degrees=True)
    
            # compute things
            for i in range(len(source_pd)):
                lat2 = source_pd.loc[i,"Lat"]
                lon2 = source_pd.loc[i,"Lon"]
                z2 = source_pd.loc[i,"Depth"]*1000 # convert to meters
                pointB = wgs84.GeoPoint(latitude=lat2, longitude=lon2, z=z2, degrees=True)
                p_AB_N = pointB.delta_to(pointA)
                Rrup_temp = p_AB_N.length/1000
                if z2 < ztor:
                    ztor = z2
                if Rrup_temp < Rrup:
                    Rrup = Rrup_temp
                    
            
            # some average thing
            average = 0
            weight = (1/(len(source_pd)))
            for i in range(len(source_pd)):
                rake = source_pd.loc[i,"Rake"]
                average+= weight*rake
    
            distance = round(Rrup,2)
            ztors = round(ztor,2)
            rakes = round(rake)
    
            source_name = temp_out['Source_Name'].values[0]
            mag = temp_out['Mag'].values[0]
            site_id = temp_out['CS_Site_ID'].values[0]
            site_name = temp_out['CS_Short_Name'].values[0]
            z10 = temp_out['Z1_0'].values[0]
            z25 = temp_out['Z2_5'].values[0]
            vs30 = temp_out['Model_Vs30'].values[0]
    
            tmp_line = [run_id,src_id,rup_id,var_id,source_name,mag,site_id,site_name,distance,vs30,ztors,z10,z25,rakes,fout_acc_csv,fout_csv,source_file]
    
            line = ",".join(map(str, tmp_line))
        
            fout.write(line+"\n")
            print(line)
            
            
# execute main -----------------------------------------

if __name__ == "__main__":
    main()
