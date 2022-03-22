import os
import numpy as np
import argparse
import math
import pandas as pd
   
#studies = ['Human_Aging']
#subjects = ['AGING006']
#protocols = ['EIsupine']

# cmd: python3 crop_torso_data.py


def get_lung_node_z(file, node_num):
    file_n = open(file, 'r')
    lines_n = file_n.readlines()
    for ln, line in enumerate(lines_n):
        if line.startswith("   z.  Value"):
            splitline = line.split()
            if splitline[-2] == "#Versions=":
                nvers = int(line.split()[-1])
            else:
                nvers = 1
        if line.startswith(" Node:"):
            if int(line.split()[-1]) == node_num:
                zpos = [2*math.ceil(nvers*4/5.) + math.ceil((nvers*4-3)/5.), (nvers*4-3)%5-1]
                #print(ln+int(zpos[0]), zpos[1])
                zval = float(lines_n[ln+int(zpos[0])].split()[zpos[1]])
    file_n.close()
    return zval


#for study in studies:
#    for subject in subjects:
#        for protocol in protocols:

input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5), engine='openpyxl'))

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
            [study, subject, protocol] = input_list[i, 1:4]
            print("\tCropping... \t"+study+", \t"+subject+", \t"+protocol)
            
            lung_dir = os.path.join(study, subject, protocol, 'Lung')
            torso_dir = os.path.join(study, subject, protocol, 'Torso')
   
            # Get landmarks from the corresponding fitted lung mesh
            lung_rn = lung_dir + "/SurfaceFEMesh/Right_fitted.exnode"
            minmax_nodes = [56, 96, 7, 49]  # [min_left, max_left, min_right, max_right]
            lung_r_zmin = get_lung_node_z(lung_rn, minmax_nodes[2])
            lung_r_zmax = get_lung_node_z(lung_rn, minmax_nodes[3])
            data_lim_max = lung_r_zmax + 0.10*(lung_r_zmax - lung_r_zmin)
            data_lim_min = lung_r_zmin - 0.05*(lung_r_zmax - lung_r_zmin)
            
            # EXDATA: Read data, eliminate points outside limits, and write new file
            #print('EXDATA:')
            file_data = open(torso_dir + "/surface_Torsotrimmed.exdata", 'r')
            lines_data = file_data.readlines()
            file_data.close()
            remove_gt_count = 0
            remove_lt_count = 0
            for ln, line in enumerate(lines_data):
                if line.startswith(" Node:"):
                    zval = float(lines_data[ln+3])
                    if zval > data_lim_max:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( > limit of {:.3f})'.format(zval, data_lim_max))
                        lines_data[ln+0] = ''
                        lines_data[ln+1] = ''
                        lines_data[ln+2] = ''
                        lines_data[ln+3] = ''
                        remove_gt_count += 1
                    if zval < data_lim_min:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( < limit of {:.3f})'.format(zval, data_lim_min))
                        lines_data[ln+0] = ''
                        lines_data[ln+1] = ''
                        lines_data[ln+2] = ''
                        lines_data[ln+3] = ''
                        remove_lt_count += 1
            print(subject+': Removed {:d} data points from exdata ( {:d} < limit of {:.3f}, {:d} > limit of {:.3f})'.format(
                  remove_lt_count+remove_gt_count, remove_lt_count, data_lim_min, remove_gt_count, data_lim_max))     
            file_out = open(torso_dir + "/surface_Torsotrimmed_crop.exdata", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            # IPDATA: Read data, eliminate points outside limits, and write new file
            #print('IPDATA:')
            file_data = open(torso_dir + "/surface_Torsotrimmed.ipdata", 'r')
            lines_data = file_data.readlines()
            file_data.close()
            remove_gt_count = 0
            remove_lt_count = 0
            for ln, line in enumerate(lines_data):
                if not line.startswith(" converted"):
                    zval = float(line.split()[3])
                    if zval > data_lim_max:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( > limit of {:.3f})'.format(zval, data_lim_max))
                        lines_data[ln] = ''
                        remove_gt_count += 1
                    if zval < data_lim_min:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( < limit of {:.3f})'.format(zval, data_lim_min))
                        lines_data[ln] = ''
                        remove_lt_count += 1
            print(subject+': Removed {:d} data points from ipdata ( {:d} < limit of {:.3f}, {:d} > limit of {:.3f})'.format(
                  remove_lt_count+remove_gt_count, remove_lt_count, data_lim_min, remove_gt_count, data_lim_max))    
            file_out = open(torso_dir + "/surface_Torsotrimmed_crop.ipdata", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            
            
            
            
            
            
            
            
            
            
            
            
                        