import os
import numpy as np
import argparse
import math
import pandas as pd
   
#studies = ['Human_Aging']
#subjects = ['AGING006']
#protocols = ['EIsupine']

# cmd: python3 fix_bed_in_torso_data.py

input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5), engine='openpyxl'))

bbox = [-1e6, 1e6, 175, 1e6, -141, -101]  # [xmin, xmax, ymin, ymax, zmin, zmax]

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
            [study, subject, protocol] = input_list[i, 1:4]
            print("\tCutting out bed... \t"+study+", \t"+subject+", \t"+protocol)
            
            torso_dir = os.path.join(study, subject, protocol, 'Torso')
   
            # EXDATA: Read data, eliminate points outside limits, and write new file
            #print('EXDATA:')
            file_data = open(torso_dir + "/surface_Torsotrimmed_crop.exdata", 'r')
            lines_data = file_data.readlines()
            file_data.close()
            remove_bed_count = 0
            for ln, line in enumerate(lines_data):
                if line.startswith(" Node:"):
                    xval = float(lines_data[ln+1])
                    yval = float(lines_data[ln+2])
                    zval = float(lines_data[ln+3])
                    if (xval > bbox[0]) and (xval < bbox[1]):
                        if (yval > bbox[2]) and (yval < bbox[3]):
                            if (zval > bbox[4]) and (zval < bbox[5]):
                                lines_data[ln+0] = ''
                                lines_data[ln+1] = ''
                                lines_data[ln+2] = ''
                                lines_data[ln+3] = ''
                                remove_bed_count += 1
            print(subject+': Removed {:d} data points within bounding box from exdata.'.format(remove_bed_count))     
            file_out = open(torso_dir + "/surface_Torsotrimmed_crop_cut.exdata", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            # IPDATA: Read data, eliminate points outside limits, and write new file
            #print('IPDATA:')
            file_data = open(torso_dir + "/surface_Torsotrimmed_crop.ipdata", 'r')
            lines_data = file_data.readlines()
            file_data.close()
            remove_bed_count = 0
            for ln, line in enumerate(lines_data):
                if not line.startswith(" converted"):
                    xval = float(line.split()[1])
                    yval = float(line.split()[2])
                    zval = float(line.split()[3])
                    if (xval > bbox[0]) and (xval < bbox[1]):
                        if (yval > bbox[2]) and (yval < bbox[3]):
                            if (zval > bbox[4]) and (zval < bbox[5]):
                                lines_data[ln] = ''
                                remove_bed_count += 1
            print(subject+': Removed {:d} data points within bounding box from ipdata.'.format(remove_bed_count))     
            file_out = open(torso_dir + "/surface_Torsotrimmed_crop_cut.ipdata", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            
            
            
            
            
            
            
            
            
            
            
            
                        