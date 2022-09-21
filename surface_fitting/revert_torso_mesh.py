import os
import numpy as np
import argparse
import math
import pandas as pd
from sys import exit
   
#studies = ['Human_Aging']
#subjects = ['AGING006']
#protocols = ['EIsupine']

# cmd: python3 crop_torso_data.py


###
def generate_rotation_matrix(U,V):
    W=np.cross(U,V)
    A=np.array([U,W,np.cross(U,W)]).T
    B=np.array([V,W,np.cross(V,W)]).T
    return np.dot(B,np.linalg.inv(A))


#for study in studies:
#    for subject in subjects:
#        for protocol in protocols:


input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5), engine='openpyxl'))

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
            [study, subject, protocol] = input_list[i, 1:4]
            print("\tReverting... \t"+study+", \t"+subject+", \t"+protocol, end="\r")
            
            mesh_dir = os.path.join('output', subject, protocol, 'Torso')
            median_dir = '/hpc/mpag253/Ribs/median_plane/output/'+study+'/'+subject+'/'+protocol+'/Median_Plane'
   
            # Rotate the data using the median plane
            # load the median plane
            median_plane = np.load(median_dir + "/median_plane.npy")
            # calculate the correcting rotation matrix
            normal_vector = median_plane[:3]
            unit_vector = normal_vector/np.linalg.norm(median_plane[:3])
            rotmat = generate_rotation_matrix(unit_vector, [1,0,0])
            # (test) new_vector = np.dot(rotmat, unit_vector)
            inv_rotmat = np.linalg.inv(rotmat)
            # (test) revert_vector = np.dot(rotmat, [1,0,0])
 
              
            # EXNODE: 
            # Read data, modify points, and write new file
            file_data = open(mesh_dir + "/Torso_fitted.exnode", 'r')
            lines_data = file_data.readlines()
            file_data.close()
            
            for ln, line in enumerate(lines_data):
                if line.startswith(" Node:"):
                
                    # extract data point
                    xvals = [float(j) for j in lines_data[ln+1].split()]
                    yvals = [float(j) for j in lines_data[ln+2].split()]
                    zvals = [float(j) for j in lines_data[ln+3].split()]
                    
                    # transform vals
                    #print(np.vstack((xvals, yvals, zvals)))
                    vp = np.dot(inv_rotmat, np.vstack((xvals, yvals, zvals)))
                    #print(vp)
                    
                    # modify point
                    lines_data[ln+1] = '   {:>12.6f} {:>12.6f} {:>12.6f} {:>12.6f}\n'.format(vp[0,0], vp[0,1], vp[0,2], vp[0,3])
                    lines_data[ln+2] = '   {:>12.6f} {:>12.6f} {:>12.6f} {:>12.6f}\n'.format(vp[1,0], vp[1,1], vp[1,2], vp[1,3])
                    lines_data[ln+3] = '   {:>12.6f} {:>12.6f} {:>12.6f} {:>12.6f}\n'.format(vp[2,0], vp[2,1], vp[2,2], vp[2,3])
                        
            file_out = open(mesh_dir + "/Torso_fitted_TEST_ROTATE.exnode", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            
            # IPNODE: 
            # Read data, modify points, and write new file
            file_data = open(mesh_dir + "/Torso_fitted.ipnode", 'r')
            lines_data = file_data.readlines()
            file_data.close()

            for ln, line in enumerate(lines_data):
                if line.startswith(" Node number "):
                
                    # extract data point
                    vals = np.empty([3, 4])
                    for j in range(4):
                        vals[0, j] = float(lines_data[ln+2+j].split()[-1])
                        vals[1, j] = float(lines_data[ln+7+j].split()[-1])
                        vals[2, j] = float(lines_data[ln+12+j].split()[-1])
                                        
                    # transform point
                    vp = np.dot(inv_rotmat, vals)
                    
                    # modify point
                    for j in range(3):
                        lines_data[ln+(j*5+2)] = " The Xj({}) coordinate is [ 0.00000E+00]: {:>12.6f}".format(str(j+1), vp[j,0])
                        lines_data[ln+(j*5+3)] = " The derivative wrt direction 1 is [ 0.00000E+00]: {:>12.6f}".format(vp[j,1])
                        lines_data[ln+(j*5+4)] = " The derivative wrt direction 2 is [ 0.00000E+00]: {:>12.6f}".format(vp[j,2])
                        lines_data[ln+(j*5+5)] = " The derivative wrt directions 1 & 2 is [ 0.00000E+00]: {:>12.6f}".format(vp[j,3])
            file_out = open(mesh_dir + "/Torso_fitted_TEST_ROTATE.ipnode", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            print("\tReverting... \t"+subject+", \t"+protocol+"\tDone.")
            
            
            
            
            
            
            
            
            
            
            
                        