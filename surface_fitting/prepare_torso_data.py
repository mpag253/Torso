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
            print("\tPreparing... \t"+study+", \t"+subject+", \t"+protocol)
            
            lung_dir = os.path.join(study, subject, protocol, 'Lung')
            torso_dir = os.path.join(study, subject, protocol, 'Torso')
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
   
            # Get landmarks from the corresponding fitted lung mesh
            # get landmarks in transformed coordinates:
            # (old lung node landmarks)            
            #lung_rn = lung_dir + "/SurfaceFEMesh/Right_fitted.exnode"
            #minmax_nodes = [56, 96, 7, 49]  # [min_left, max_left, min_right, max_right]
            #lung_r_min = get_lung_node_coords(lung_rn, minmax_nodes[2])
            #lung_r_max = get_lung_node_coords(lung_rn, minmax_nodes[3])
            #lung_r_min_tf = do_transform(unit_normal_vector, lung_r_min)
            #lung_r_max_tf = do_transform(unit_normal_vector, lung_r_max)
            #lung_r_zmin_tf = lung_r_min_tf[2]
            #lung_r_zmax_tf = lung_r_max_tf[2]
            # get new landmarks
            landmark_T02_vx = input_list[i, [17, 16, 15]]  # in voxel indices
            landmark_T11_vx = input_list[i, [14, 13, 12]]  # in voxel indices
            image_info = input_list[i, 5:11]
            landmark_T02_mm = get_voxel_coordinates(landmark_T02_vx, image_info)  # in millimetres
            landmark_T11_mm = get_voxel_coordinates(landmark_T11_vx, image_info)  # in millimetres
            landmark_T02_tf = do_transform(unit_normal_vector, landmark_T02_mm)  # in transformed coordinates
            landmark_T11_tf = do_transform(unit_normal_vector, landmark_T11_mm)  # in transformed coordinates
            landmark_zmax_tf = landmark_T02_tf[2]
            landmark_zmin_tf = landmark_T11_tf[2]
            
            # Evalaute median plane location
            # define a point on the plane that gives transformed x-coordinate of median plane 
            mp_pt = landmark_T11_mm
            mp_pt[0] = -(median_plane[1]*mp_pt[1] + median_plane[2]*mp_pt[2] + median_plane[3])/median_plane[0]
            mp_pt_tf = do_transform(unit_normal_vector, mp_pt)            
            
            # save landmarks
            fname = torso_path+"landmarks/"+study+"/"+subject+"/"+protocol+"/landmarks.txt"
            os.makedirs(os.path.dirname(fname), exist_ok=True)
            with open(fname, "w") as f:
                f.writelines([str(landmark_zmin_tf)+"\n", 
                              str(landmark_zmax_tf)+"\n",
                              str(mp_pt_tf[0])+"\n"])
            
                        
            ## (comparing lung nodes and landmarks)
            #lung_ht = lung_r_zmax_tf - lung_r_zmin_tf
            #landmark_dist = landmark_zmax_tf - landmark_zmin_tf
            #meas_1 = (lung_r_zmin_tf - landmark_zmin_tf)/landmark_dist
            #meas_2 = (lung_r_zmax_tf - landmark_zmin_tf)/landmark_dist
            #print(subject, "\t", meas_1, "\t", meas_2)
            ##exit(0)
            
            # Define limits based on landmarks
            # (lung nodes - old)
            #data_lim_max = lung_r_zmax_tf + 0.10*(lung_r_zmax_tf - lung_r_zmin_tf)
            #data_lim_min = lung_r_zmin_tf - 0.05*(lung_r_zmax_tf - lung_r_zmin_tf)
            # landmarks - new
            landmark_dist = landmark_zmax_tf - landmark_zmin_tf
            data_lim_max = landmark_zmax_tf + 0.05*landmark_dist
            data_lim_min = landmark_zmin_tf - 0.35*landmark_dist
            #data_lim_max = np.inf
            #data_lim_min = -np.inf
            
            # EXDATA: Read data, eliminate points outside limits, and write new file
            #print('EXDATA:')
            file_data = open(torso_dir + "/surface_Torsotrimmed.exdata", 'r')
            lines_data = file_data.readlines()
            file_data.close()
            remove_gt_count = 0
            remove_lt_count = 0
            for ln, line in enumerate(lines_data):
                if line.startswith(" Node:"):
                
                    # extract data point
                    x = float(lines_data[ln+1])
                    y = float(lines_data[ln+2])
                    z = float(lines_data[ln+3])
                    
                    # transform point
                    [xp, yp, zp] = do_transform(unit_normal_vector, [x, y, z])
                    
                    # crop point
                    if zp > data_lim_max:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( > limit of {:.3f})'.format(zval, data_lim_max))
                        lines_data[ln+0] = ''
                        lines_data[ln+1] = ''
                        lines_data[ln+2] = ''
                        lines_data[ln+3] = ''
                        remove_gt_count += 1
                    elif zp < data_lim_min:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( < limit of {:.3f})'.format(zval, data_lim_min))
                        lines_data[ln+0] = ''
                        lines_data[ln+1] = ''
                        lines_data[ln+2] = ''
                        lines_data[ln+3] = ''
                        remove_lt_count += 1
                    else:
                        # e.g. format "  2.108375e+02"
                        lines_data[ln+1] = ' {:13.6e}\n'.format(xp)
                        lines_data[ln+2] = ' {:13.6e}\n'.format(yp)
                        lines_data[ln+3] = ' {:13.6e}\n'.format(zp)
                        
            print(subject+': Removed {:d} points from exdata ( {:>5d} < {:.3f}, {:d} > {:.3f})'.format(
                  remove_lt_count+remove_gt_count, remove_lt_count, data_lim_min, remove_gt_count, data_lim_max))     
            file_out = open(torso_dir + "/surface_Torsotrimmed_crop_tf.exdata", 'w')
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
                
                    # extract data point
                    line_array = line.split()
                    x = float(line_array[1])
                    y = float(line_array[2])
                    z = float(line_array[3])
                                        
                    # transform point
                    [xp, yp, zp] = do_transform(unit_normal_vector, [x, y, z])
                    
                    # crop point
                    if zp > data_lim_max:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( > limit of {:.3f})'.format(zval, data_lim_max))
                        lines_data[ln] = ''
                        remove_gt_count += 1
                    elif zp < data_lim_min:
                        #print('\t'+subject+': Data removed with z = {:.3f} ( < limit of {:.3f})'.format(zval, data_lim_min))
                        lines_data[ln] = ''
                        remove_lt_count += 1
                    else:
                        # e.g. format " 8.170801e+01"
                        lines_data[ln] = " {} {:12.6e} {:12.6e} {:12.6e} {} {} {}\n".format(line_array[0], xp, yp, zp, line_array[4], line_array[5], line_array[6])
            print(subject+': Removed {:d} points from ipdata ( {:>5d} < {:.3f}, {:d} > {:.3f})'.format(
                  remove_lt_count+remove_gt_count, remove_lt_count, data_lim_min, remove_gt_count, data_lim_max))    
            file_out = open(torso_dir + "/surface_Torsotrimmed_crop_tf.ipdata", 'w')
            file_out.writelines(lines_data)
            file_out.close() 
            
            
            
            
            
            
            
            
            
            
            
            
            
                        