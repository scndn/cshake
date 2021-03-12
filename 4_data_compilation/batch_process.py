#!/usr/bin/env python

import matplotlib
matplotlib.use("AGG", warn=False)
from pylab import *
import sys
import os
from os import listdir
import struct

'''struct seisheader {
  char version[8];
  char site_name[8];
  //in case we think of something later
  char padding[8];
  int source_id;
  int rupture_id;
  int rup_var_id;
  float dt;
  int nt;
  int comps;
  float det_max_freq;
  float stoch_max_freq;
  };'''

class Seismogram:

        def __init__(self, filename, label):
                self.filename = filename
                self.label = label
                self.nt = 0
                self.dt = 0.0

        def createTimesteps(self):
                self.timesteps = []
                for i in range(0, self.nt):
                        self.timesteps.append(i*self.dt)

        def parseHeader(self, header_str):
                #dt is bytes 36-40, nt is 40-44
                self.header_str = header_str
                self.dt = struct.unpack("f", header_str[36:40])[0]
                self.nt = struct.unpack("i", header_str[40:44])[0]
                print "Using nt=%d, dt=%f for file %s" % (self.nt, self.dt, self.filename)

        def readData(self):
                fp_in = open(self.filename, "r")
                header_str = fp_in.read(56)
                self.parseHeader(header_str)
                data_str = fp_in.read(4*self.nt)
                self.x_data = struct.unpack("%df" % self.nt, data_str)
                data_str = fp_in.read(4*self.nt)
                self.y_data = struct.unpack("%df" % self.nt, data_str)
                fp_in.close()

        def convertToAcc(self):
                self.x_acc = [0.0]
                self.y_acc = [0.0]
                for i in range(1, self.nt):
                        self.x_acc.append((self.x_data[i]-self.x_data[i-1])/self.dt)
                        self.y_acc.append((self.y_data[i]-self.y_data[i-1])/self.dt)

        def writeAcc(self, out_file):
                with open(out_file, "wb") as fp_out:
                        fp_out.write(self.header_str)
                        x_str = struct.pack("%df" % self.nt, *self.x_acc)
                        fp_out.write(x_str)
                        y_str = struct.pack("%df" % self.nt, *self.y_acc)
                        fp_out.write(y_str)
                        fp_out.close()

def velo_to_csv(fin,fout_csv):
        with open(fin, "rb") as fp_in:
        #Get dt from header
            header_str = fp_in.read(56)
            dt = struct.unpack("f", header_str[36:40])[0]
            nt = struct.unpack("i", header_str[40:44])[0]
            x_data = struct.unpack("%df" % (nt), fp_in.read(4*nt))
            y_data = struct.unpack("%df" % (nt), fp_in.read(4*nt))
            with open(fout_csv, "w") as fp_out:
                fp_out.write("time,X velocity(cm/s),Y velocity(cm/s)\n")
                for i in range(0, nt):
                    fp_out.write("%.2f,%.4f,%.4f\n" % (dt*i, x_data[i], y_data[i]))
                fp_out.flush()
                fp_out.close()
            fp_in.close()

def acc_to_csv(fin,fout_csv):
        with open(fin, "rb") as fp_in:
        #Get dt from header
            header_str = fp_in.read(56)
            dt = struct.unpack("f", header_str[36:40])[0]
            nt = struct.unpack("i", header_str[40:44])[0]
            x_data = struct.unpack("%df" % (nt), fp_in.read(4*nt))
            y_data = struct.unpack("%df" % (nt), fp_in.read(4*nt))
            with open(fout_csv, "w") as fp_out:
                fp_out.write("time,X acceleration(cm/s^2),Y acceleration(cm/s^2)\n")
                for i in range(0, nt):
                    fp_out.write("%.2f,%.4f,%.4f\n" % (dt*i, x_data[i], y_data[i]))
                fp_out.flush()
                fp_out.close()
            fp_in.close()

def find_csv_filenames( path_to_dir, suffix=".grm" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

def main():
    indir = "./seis/"
    filenames = find_csv_filenames(indir)
    outdir = "./post/"
    for fin in filenames:
        # out files
        infile = indir + fin
        name = fin.rsplit(".", 1)[0] 
        acc_out = outdir + name + "_acc" + ".grm"
        fout_png = outdir + name + ".png"
        fout_csv = outdir + name + ".csv"
        fout_acc_png = outdir + name + "_acc" + ".png"
        fout_acc_csv = outdir + name + "_acc" + ".csv"
        
        if os.path.exists(fout_csv):
            pass
        else:
            # read seis write csv
            velo_to_csv(infile,fout_csv)

        if os.path.exists(acc_out):
            pass
        else:
            # convert velo to acc
            s = Seismogram(infile,name)
            s.readData()
            s.convertToAcc()
            s.writeAcc(acc_out)

        if os.path.exists(fout_acc_csv):
            pass
        else:
            # read seis acc write csv
            acc_to_csv(acc_out,fout_acc_csv)

        if os.path.exists(fout_png):
            pass
        else:
            # plot seis
            seismograms = []
            seismograms.append(Seismogram(infile,name))
            output_filename = fout_png
            plot_title = name

            num_seis = len(seismograms)

            max_y = 0.0
            min_y = 0.0

            for seis in seismograms:
                seis.readData()
                seis.createTimesteps()
                max_y = max([max_y, max(seis.x_data), max(seis.y_data)])
                min_y = min([min_y, min(seis.x_data), min(seis.y_data)])

            max_y = 1.1*max_y
            min_y = 1.1*min_y

            clf()
            subplot(211, title="X component (cm/s)")
            for seis in seismograms:
                plot(seis.timesteps, seis.x_data, label=seis.label)
            #xlim(0, seis.timesteps[-1])
            xlim(0, 200)
            #ylim(-80, 80)
            ylim(min_y, max_y)
            legend(loc="upper right", prop={'size': 10})
            subplot(212, title="Y component (cm/s)")
            for seis in seismograms:
                plot(seis.timesteps, seis.y_data, label=seis.label)
            #xlim(0, seis.timesteps[-1])
            xlim(0, 200)
            #ylim(-80, 80)
            ylim(min_y, max_y)
            legend(loc="upper right", prop={'size': 10})
            suptitle(plot_title)
            gcf().set_size_inches(14, 7)
            savefig(output_filename, format="png")

if __name__=='__main__':
        main()
