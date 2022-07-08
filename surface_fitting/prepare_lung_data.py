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


def get_lung_node_coords(file, node_num):
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
                # identify the row and column of each value from the the exnode format
                #zpos = [2*math.ceil(nvers*4/5.) + math.ceil((nvers*4-3)/5.), (nvers*4-3)%5-1]
                xrow = int(0*math.ceil(nvers*4/5.) + math.ceil((nvers*4-3)/5.))
                yrow = int(1*math.ceil(nvers*4/5.) + math.ceil((nvers*4-3)/5.))
                zrow = int(2*math.ceil(nvers*4/5.) + math.ceil((nvers*4-3)/5.))
                col = (nvers*4-3)%5-1
                # retrieve the values
                xval = float(lines_n[ln+xrow].split()[col])
                yval = float(lines_n[ln+yrow].split()[col])
                zval = float(lines_n[ln+zrow].split()[col])
    file_n.close()
    return [xval, yval, zval]

###
def generate_rotation_matrix(U,V):
    W=np.cross(U,V)
    A=np.array([U,W,np.cross(U,W)]).T
    B=np.array([V,W,np.cross(V,W)]).T
    return np.dot(B,np.linalg.inv(A))
    
###
def rotate_in_x(vector_1, ang):
    rotmat_x = [[ 1,           0,            0],
                [ 0, np.cos(ang), -np.sin(ang)],
                [ 0, np.sin(ang),  np.cos(ang)]]
    vector_2 = np.matmul(rotmat_x, vector_1)                
    return vector_2
    
    
###
def rotate_in_y(vector_1, ang):
    rotmat_y = [[  np.cos(ang), 0, np.sin(ang)],
                [            0, 1,           0],
                [ -np.sin(ang), 0, np.cos(ang)]]
    vector_2 = np.matmul(rotmat_y, vector_1)
    return vector_2
    

###
def rotate_in_z(vector_1, ang):
    rotmat_z = [[ np.cos(ang), -np.sin(ang), 0],
                [ np.sin(ang),  np.cos(ang), 0],
                [ 0,        0,               1]]
    vector_2 = np.matmul(rotmat_z, vector_1)
    return vector_2
    

###
def do_transform(unit_normal_vector, in_vector):

    # align to median plane
    angle_a = np.arctan(unit_normal_vector[2]/unit_normal_vector[0])
    vector_a = rotate_in_y(in_vector, angle_a)
    angle_b = -np.arcsin(unit_normal_vector[1]/1)
    vector_b = rotate_in_z(vector_a, angle_b)
    
    # correct z-direction
    unit_z = [0, 0, 1]
    unit_z_a = rotate_in_y(unit_z, angle_a)
    unit_z_b = rotate_in_z(unit_z_a, angle_b)
    correction_angle = np.arctan(unit_z_b[1]/unit_z_b[2])
    #unit_z_c = rotate_in_x(unit_z_b, correction_angle)
    vector_c = rotate_in_x(vector_b, correction_angle)
    
    #print("in_vector:", in_vector)
    #print("vector_b:", vector_b)
    #print("vector_a:", vector_a, "\n")
    #print("correction_angle:", correction_angle)
    #print("unit_z_b:", unit_z_b) 
    #print("unit_z_c:", unit_z_c)
    #print("vector_c:", vector_c)
    
    return vector_c
    
    
###
def get_voxel_coordinates(indices, image_info):
    """
    """
    #unpack image info
    [d1, d2, d3, p1, p2, p3] = image_info
    # generate the coordinates   
    x_coord = p1/2 + p1*indices[0]
    y_coord = -(p2/2 + p2*indices[1]) + d2*p2
    z_coord = p3/2 + p3*indices[2] - d3*p3
    return [x_coord, y_coord, z_coord]
    

#for study in studies:
#    for subject in subjects:
#        for protocol in protocols:

torso_path = "/hpc/mpag253/Torso/"
input_list = np.array(pd.read_excel(torso_path+"landmarks/torso_landmarks.xlsx", skiprows=0, usecols=range(18), engine='openpyxl'))

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
            [study, subject, protocol] = input_list[i, 1:4]
            print("\tTransfoming... \t"+study+", \t"+subject+", \t"+protocol)
            
            lung_dir = os.path.join(study, subject, protocol, 'Lung')
            median_dir = '/hpc/mpag253/Ribs/median_plane/output/'+study+'/'+subject+'/'+protocol+'/Median_Plane'
   
            # Rotate the data using the median plane
            # load the median plane
            median_plane = np.load(median_dir + "/median_plane.npy")
            # calculate the reorientation vector
            normal_vector = median_plane[:3]
            unit_normal_vector = normal_vector/np.linalg.norm(median_plane[:3])   
            
            ## (test) 
            #test_vector = do_transform(unit_normal_vector, unit_normal_vector)
            #print("test vector:", test_vector)
            #exit(0)
            
            # EXNODE: Read data, eliminate points outside limits, and write new file
            #print('EXNODE:')
            for lung in ['Right', 'Left']:
                file_data = open(lung_dir + "/SurfaceFEMesh/"+lung+"_fitted.exnode", 'r')
                lines_data = file_data.readlines()
                file_data.close()
                remove_gt_count = 0
                remove_lt_count = 0
                for ln, line in enumerate(lines_data):
                
                    # current number of versions
                    if line.startswith("   z.  Value"):
                        line_split = line.split()
                        if line_split[-2] == '#Versions=':
                            n_vers = int(line_split[-1])
                        else:
                            n_vers = 1
                
                    if line.startswith(" Node:"):
                    
                        # number of columns in file
                        n_cols = 5
                        # number of values for each direction
                        n_vals = n_vers*4
                        # number of rows for each direction
                        n_rows = int(np.ceil(n_vals/n_cols))
                        # number of remaining values in final row
                        n_rem = n_vals%n_cols
                        #print(n_vers, n_cols, n_vals, n_rows, n_rem)
                        
                        # assemble data for each direction
                        data = np.empty([3, n_vers, 4])
                        for d in range(3):
                            data_str = lines_data[ln+d*n_rows+1].split()
                            for j in range(1, n_rows):
                                data_str += lines_data[ln+d*n_rows+j+1].split()
                            data_float = [float(v) for v in data_str]
                            data[d] = np.reshape(data_float, [n_vers, 4])
                    
                        # transform data
                        data_tf = np.empty(np.shape(data))
                        for ver in range(n_vers):
                            for deriv in range(4):
                                [xval, yval, zval] = data[:, ver, deriv]
                                [xp, yp, zp] = do_transform(unit_normal_vector, [xval, yval, zval])
                                data_tf[:, ver, deriv] = [xp, yp, zp]
                                      
                        # disassemble data for write
                        for d in range(3):
                            # data transformed 
                            dtff = data_tf[d].flatten()
                            # enter data for all lines except final
                            for j in range(n_rows-1):
                                format_str = " {:24e} {:24e} {:24e} {:24e} {:24e}\n"
                                k = j*5
                                lines_data[ln+d*n_rows+j+1] = format_str.format(dtff[k+0], dtff[k+1], dtff[k+2], dtff[k+3], dtff[k+4])
                        
                            # enter data for final line
                            k = (n_rows-1)*5
                            if n_rem == 0:
                                format_str = " {:24e} {:24e} {:24e} {:24e} {:24e}\n"
                                lines_data[ln+d*n_rows+n_rows] = format_str.format(dtff[k+0], dtff[k+1], dtff[k+2], dtff[k+3], dtff[k+4])
                            elif n_rem == 1:
                                format_str = " {:24e}\n"
                                lines_data[ln+d*n_rows+n_rows] = format_str.format(dtff[k+0])
                            elif n_rem == 2:
                                format_str = " {:24e} {:24e}\n"
                                lines_data[ln+d*n_rows+n_rows] = format_str.format(dtff[k+0], dtff[k+1])
                            elif n_rem == 3:
                                format_str = " {:24e} {:24e} {:24e}\n"
                                lines_data[ln+d*n_rows+n_rows] = format_str.format(dtff[k+0], dtff[k+1], dtff[k+2])
                            elif n_rem == 4:
                                format_str = " {:24e} {:24e} {:24e} {:24e}\n"
                                lines_data[ln+d*n_rows+n_rows] = format_str.format(dtff[k+0], dtff[k+1], dtff[k+2], dtff[k+3])
                            
                            # add whitespace to first line of each direction
                            lines_data[ln+d*n_vers+1] = "  "+lines_data[ln+d*n_vers+1]
                            
                file_out = open(lung_dir + "/SurfaceFEMesh/"+lung+"_fitted_tf.exnode", 'w')
                file_out.writelines(lines_data)
                file_out.close() 
            
           
            ## IPNODE: Read data, eliminate points outside limits, and write new file
            ##print('IPNODE:')
            #file_data = open(torso_dir + "/SurfaceFEMesh/Left_fitted_tf.ipnode", 'r')
            #lines_data = file_data.readlines()
            #file_data.close()
            #remove_gt_count = 0
            #remove_lt_count = 0
            #for ln, line in enumerate(lines_data):
            #    if not line.startswith(" converted"):
            #    
            #        # extract data point
            #        line_array = line.split()
            #        x = float(line_array[1])
            #        y = float(line_array[2])
            #        z = float(line_array[3])
            #                            
            #        # transform point
            #        [xp, yp, zp] = do_transform(unit_normal_vector, [x, y, z])
            #        
            #        # crop point
            #        if zp > data_lim_max:
            #            #print('\t'+subject+': Data removed with z = {:.3f} ( > limit of {:.3f})'.format(zval, data_lim_max))
            #            lines_data[ln] = ''
            #            remove_gt_count += 1
            #        elif zp < data_lim_min:
            #            #print('\t'+subject+': Data removed with z = {:.3f} ( < limit of {:.3f})'.format(zval, data_lim_min))
            #            lines_data[ln] = ''
            #            remove_lt_count += 1
            #        else:
            #            # e.g. format " 8.170801e+01"
            #            lines_data[ln] = " {} {:12.6e} {:12.6e} {:12.6e} {} {} {}\n".format(line_array[0], xp, yp, zp, line_array[4], line_array[5], line_array[6])
            #print(subject+': Removed {:d} points from ipdata ( {:>5d} < {:.3f}, {:d} > {:.3f})'.format(
            #      remove_lt_count+remove_gt_count, remove_lt_count, data_lim_min, remove_gt_count, data_lim_max))    
            #file_out = open(torso_dir + "/surface_Torsotrimmed_crop_tf.ipdata", 'w')
            #file_out.writelines(lines_data)
            #file_out.close() 
            
            
            
            
            
            
            
            
            
            
            
            
            
                        