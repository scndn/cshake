#!/usr/bin/env python

import sys
import os
import os.path
from os import path

def main():

    print "...starting"

    f = open("events","r")

    root = '/home/rcf-104/CyberShake2007/ruptures/Ruptures_erf36/'

    try:

        for x in f:
            search_parameters = x.split()
            n_parameters = len(search_parameters)

            if n_parameters == 4:

                run_id = int(search_parameters[0])
                source_id = int(search_parameters[1])
                rupture_id = int(search_parameters[2])
                rup_var_id = int(search_parameters[3])

                if run_id==None or source_id==None or rupture_id==None or rup_var_id==None:
                    print "...missing id"
                    sys.exit(-1)

                try:
                    text_file = str(source_id) + '_' + str(rupture_id) + '.txt'
                    indir = root + str(source_id) + '/' + str(rupture_id) + '/' + text_file
                    outdir = "./source/" + text_file
                    cursor = "cp " + indir + " " + outdir
                    if path.exists(outdir) == False:
                        os.system(cursor)
                        print cursor
                    else:
                        pass

                except:
                    print "...error copying file"
    except:
        print "...no input file"

if __name__=='__main__':
        main()

