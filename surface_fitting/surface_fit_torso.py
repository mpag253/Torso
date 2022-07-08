#!/usr/bin/env python
import os
import numpy as np
import argparse
import math

from aether.diagnostics import set_diagnostics_on
from aether.indices import define_problem_type
from aether.geometry import define_data_geometry,define_elem_geometry_2d,define_node_geometry_2d,import_node_geometry_2d,write_node_geometry_2d #,enclosed_volume
from aether.exports import export_data_geometry,export_elem_geometry_2d,export_node_geometry_2d 
from aether.surface_fitting import fit_surface_geometry,initialise_fit_mesh

from sys import exit

def get_ellipse_y(x, a, b):
    if np.abs(x-a) < 1e-6:
        y = 0
    else:
        y = b*math.sqrt(1 - (x/a)**2)
    return y


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


def initialise_torso_mesh(torso_dir, lung_dir, output_dir, template_dir, landmarks_dir):

    # Read the mesh template .exnode file
    file_exn = open(template_dir+'/templatetorso.exnode', 'r')
    lines_exn = file_exn.readlines()
    file_exn.close()
    n_data = np.empty((0, 13))
    for ln, line in enumerate(lines_exn):
        if line.startswith(" Node:"):
            node_id = int(line.split()[-1])
            temp1 = lines_exn[ln+1].split()
            temp2 = lines_exn[ln+2].split()
            temp3 = lines_exn[ln+3].split()
            temp = np.concatenate(([node_id], temp1, temp2, temp3))
            n_data = np.append(n_data, [temp], axis=0)
    n_data = n_data[n_data[:, 0].astype(int).argsort()]
    
    # Get landmarks from the corresponding fitted lung mesh
    # (lung nodes - old)
    #lung_rn = lung_dir + "/SurfaceFEMesh/Right_fitted.exnode"
    #minmax_nodes = [56, 96, 7, 49]  # [min_left, max_left, min_right, max_right]
    #lung_r_zmin = get_lung_node_z(lung_rn, minmax_nodes[2])
    #lung_r_zmax = get_lung_node_z(lung_rn, minmax_nodes[3])
    # spine landmarks - new
    landmarks = np.loadtxt(landmarks_dir+'/landmarks.txt')
    [landmark_zmin, landmark_zmax, landmark_centre] = landmarks
    
    ## Retrieve torso data and evaluate the z-bounds
    torso_data = np.loadtxt(torso_dir+"/surface_Torsotrimmed_crop_tf.ipdata", skiprows=1)
    z_min = np.min(torso_data[:, 3])
    z_max = np.max(torso_data[:, 3])
    #z_rng = z_max - z_min
    
    # Evaluate scaling parameters for the mesh
    # (old)
    #tol = 20.0
    #mask = (torso_data[:, 3] < (z_min + tol))
    #bot_ring = torso_data[mask, :]
    #bot_min_x = np.min(bot_ring[:, 1])
    #bot_max_x = np.max(bot_ring[:, 1])
    #bot_min_y = np.min(bot_ring[:, 2])
    #bot_max_y = np.max(bot_ring[:, 2])
    #centre = [(bot_min_x + bot_max_x)/2, (bot_min_y + bot_max_y)/2]
    #boxdim = [(bot_max_x - bot_min_x)/2, (bot_max_y - bot_min_y)/2]  # [a, b] for ellipse
    # (new)
    x_max = np.max(torso_data[:, 1])
    x_min = np.min(torso_data[:, 1])
    y_max = np.max(torso_data[:, 2])
    y_min = np.min(torso_data[:, 2])
    centre = [landmark_centre, (y_max + y_min)/2]
    boxdim = [(x_max - x_min)/2, (y_max - y_min)/2]
    
    # Define node groups for constraints
    nrings = 7
    nod_rings = np.empty((nrings,16))
    for i in range(nrings):
        nod_rings[i, :] = np.arange(i*16+1, i*16+17)
    nod_cols = np.empty((16, nrings))
    for i in range(16):
        nod_cols[i, :] = np.arange(i+1, 113, 16)
    
    # Define x/a, y-dir for each node column
    nod_col_vals = np.empty((16, 2))
    #nod_col_vals[0, :] = [-0.95, -1]
    #nod_col_vals[1, :] = [-0.70, -1]
    #nod_col_vals[2, :] = [-0.35, -1]
    #nod_col_vals[3, :] = [+0.00, -1]
    #nod_col_vals[4, :] = [+0.35, -1]
    #nod_col_vals[5, :] = [+0.70, -1]
    #nod_col_vals[6, :] = [+0.95, -1]
    #nod_col_vals[7, :] = [+0.95, +1]
    #nod_col_vals[8, :] = [+0.75, +1]
    #nod_col_vals[9, :] = [+0.45, +1]
    #nod_col_vals[10, :] = [+0.20, +1]
    #nod_col_vals[11, :] = [+0.00, +1]
    #nod_col_vals[12, :] = [-0.20, +1]
    #nod_col_vals[13, :] = [-0.45, +1]
    #nod_col_vals[14, :] = [-0.75, +1]
    #nod_col_vals[15, :] = [-0.95, +1]
    nod_col_vals[0, :] = [-0.85, -1]
    nod_col_vals[1, :] = [-0.50, -1]
    nod_col_vals[2, :] = [-0.20, -1]
    nod_col_vals[3, :] = [+0.00, -1]
    nod_col_vals[4, :] = [+0.20, -1]
    nod_col_vals[5, :] = [+0.50, -1]
    nod_col_vals[6, :] = [+0.85, -1]
    nod_col_vals[7, :] = [+1.00, +1]
    nod_col_vals[8, :] = [+0.85, +1]
    nod_col_vals[9, :] = [+0.50, +1]
    nod_col_vals[10, :] = [+0.20, +1]
    nod_col_vals[11, :] = [+0.00, +1]
    nod_col_vals[12, :] = [-0.20, +1]
    nod_col_vals[13, :] = [-0.50, +1]
    nod_col_vals[14, :] = [-0.85, +1]
    nod_col_vals[15, :] = [-1.00, +1]
    
    # Calculate and store new node coordinates
    for c in range(np.shape(nod_cols)[0]):
        nx = centre[0] + nod_col_vals[c, 0]*boxdim[0]
        ny = centre[1] + get_ellipse_y(nx-centre[0], boxdim[0], boxdim[1])*nod_col_vals[c, 1]
        # ndydx = get_ellipse_dydx(nx-centre[0], boxdim[0], boxdim[1])
        for i, n in enumerate(nod_cols[c, :].astype(int)):
            n_data[n-1, 1:] = 0.
            n_data[n-1, 1] = nx
            n_data[n-1, 5] = ny
    # (old)
    #z_ht = lung_r_zmax - lung_r_zmin
    #z_buffer_1 = z_ht*0.10
    #z_buffer_2 = z_ht*0.15
    #z_buffer_3 = z_ht*0.10
    #z_buffer_4 = z_ht*0.05
    #for r in range(nrings):
    #    for i, n in enumerate(nod_rings[r, :].astype(int)):
    #        if r == nrings-1: # bottom
    #            n_data[n-1, 9] = lung_r_zmin - z_buffer_1
    #        elif r == 0: # top
    #            n_data[n - 1, 9] = lung_r_zmax + z_buffer_2
    #        elif r == nrings-2: # second bottom
    #            n_data[n - 1, 9] = lung_r_zmin + z_buffer_3
    #        elif r == 1: # second top
    #            n_data[n - 1, 9] = lung_r_zmax - z_buffer_4
    #        else:
    #            n_data[n - 1, 9] = lung_r_zmax - z_buffer_4 - (z_ht - z_buffer_3 - z_buffer_4)/(nrings-3)*(r-1)
    # (new)
    for r in range(nrings):
        for i, n in enumerate(nod_rings[r, :].astype(int)):
            n_data[n - 1, 9] = landmark_zmin + ((r-1.6)*0.25)*(landmark_zmax - landmark_zmin)
    
    if z_min < np.min(n_data[:, 9].astype(float)):
        print('WARNING: Data exists below mesh. Consider larger z_buffer or cropping data.')
    if z_max > np.max(n_data[:, 9].astype(float)):
        print('WARNING: Data exists above mesh. Consider larger z_buffer or cropping data.')
    
    # Write to file
    for ln, line in enumerate(lines_exn):
        if line.startswith(" Group name:"):
            lines_exn[ln] = " Group name: preparedTorso\n"
        if line.startswith(" Node:"):
            node_id = int(line.split()[-1])
            new_data = n_data[node_id-97, 1:].astype(float)
            lines_exn[ln+1] = "  {:>13.6f}{:>13.6f}{:>13.6f}{:>13.6f}\n".format(new_data[0], new_data[1], new_data[2], new_data[3])
            lines_exn[ln+2] = "  {:>13.6f}{:>13.6f}{:>13.6f}{:>13.6f}\n".format(new_data[4], new_data[5], new_data[6], new_data[7])
            lines_exn[ln+3] = "  {:>13.6f}{:>13.6f}{:>13.6f}{:>13.6f}\n".format(new_data[8], new_data[9], new_data[10], new_data[11])
    file_out = open(output_dir+'/Torso_prepared.exnode', 'w')
    file_out.writelines(lines_exn)
    file_out.close()   
    
    
def adjust_nodes(file_lines, nodes, dim, val):
    #n_data = np.empty((0, 13))
    for ln, line in enumerate(file_lines):
        #if line.startswith(" Group name:"):
        #    file_lines[ln] = " Group name: editedTorso"
        if line.startswith(" Node:"):
            node_id = int(line.split()[-1])
            if node_id in nodes:
                dim_vals = np.array(file_lines[ln+dim].split()).astype(float)
                dim_vals[0] += val
                file_lines[ln+dim] = "  {:>13.6f}{:>13.6f}{:>13.6f}{:>13.6f}\n".format(dim_vals[0], dim_vals[1], dim_vals[2], dim_vals[3])
    return file_lines
    
    
def get_node_val(file_lines, node, dim, deriv):
    # dim: (x,y,z) --> (1,2,3); (coord,dds1,dds2,d2ds1s2) --> (0,1,2,3)
    for ln, line in enumerate(file_lines):
        if line.startswith(" Node:"):
            node_id = int(line.split()[-1])
            if node_id == node:
                dim_vals = np.array(file_lines[ln+dim].split()).astype(float)
    return dim_vals[deriv]


def centre_ap(template_path, output_dir, adjust_val):
    
    # fractional adjust values - need to convert using node locations
    adjust_val_a = float(adjust_val.split(",")[-2])
    adjust_val_p = float(adjust_val.split(",")[-1])
    
    # Read the fitted .exnode file
    file_exn = open(os.path.join(output_dir,'Torso_fitted.exnode'), 'r')
    lines_exn = file_exn.readlines()
    file_exn.close()
    
    # Convert fractional adjust values to absolute (mm) using node values
    if adjust_val_a < 0.:
        xC = get_node_val(lines_exn, 100, 1, 0)  # x coord of centre node (100)
        xR = get_node_val(lines_exn,  99, 1, 0)  # x coord of node right of centre (99)
        adjust_val_a = adjust_val_a*abs(xC-xR)
    else:
        xC = get_node_val(lines_exn, 100, 1, 0)  # x coord of centre node (100)
        xL = get_node_val(lines_exn, 101, 1, 0)  # x coord of node left of centre (101)
        adjust_val_a = adjust_val_a*abs(xL-xC)  

    if adjust_val_p < 0.:
        xC = get_node_val(lines_exn, 108, 1, 0)  # x coord of centre node (108)
        xR = get_node_val(lines_exn, 109, 1, 0)  # x coord of node right of centre (109)
        adjust_val_p = adjust_val_p*abs(xC-xR)
    else:
        xC = get_node_val(lines_exn, 108, 1, 0)  # x coord of centre node (108)
        xL = get_node_val(lines_exn, 107, 1, 0)  # x coord of node left of centre (107)
        adjust_val_p = adjust_val_p*abs(xL-xC)    
    
    # Do adjustments
    if adjust_val_a != 0.:
        print (" ===Centre anterior nodes=== ")
        nodes_anterior = [ 98,  99, 100, 101, 102, 
                          114, 115, 116, 117, 118, 
                          130, 131, 132, 133, 134,
                          146, 147, 148, 149, 150,
                          162, 163, 164, 165, 166,
                          178, 179, 180, 181, 182,
                          194, 195, 196, 197, 198]               
        lines_exn = adjust_nodes(lines_exn, nodes_anterior, 1, adjust_val_a)
        print (" -----nodes exported (anterior)")
    if adjust_val_p != 0.:    
        print (" ===Centre posterior nodes=== ")
        nodes_posterior = [105, 106, 107, 108, 109, 110, 111,
                           121, 122, 123, 124, 125, 126, 127,
                           137, 138, 139, 140, 141, 142, 143,
                           153, 154, 155, 156, 157, 158, 159,
                           169, 170, 171, 172, 173, 174, 175,
                           185, 186, 187, 188, 189, 190, 191,
                           201, 202, 203, 204, 205, 206, 207]  
                          
        lines_exn = adjust_nodes(lines_exn, nodes_posterior, 1, adjust_val_p)
        
    # Write to file
    file_out = open(output_dir+'/Torso_edited.exnode', 'w')
    file_out.writelines(lines_exn)
    file_out.close() 
    print (" -----nodes exported (posterior)")
    import_node_geometry_2d(os.path.join(template_path, 'templatetorso'))
    define_elem_geometry_2d(os.path.join(template_path, 'templatetorso'), 'unit')
    export_elem_geometry_2d(os.path.join(output_dir, 'Torso_edited'), 'fittedTorso', 0, 0)
    print (" -----elements exported")


def main():

    parser = argparse.ArgumentParser(description='Fitting a lung surface mesh')
    parser.add_argument('-s','--study_code', help='Input study name (e.g. HA, HLA)',required=True)
    parser.add_argument('-c','--subject_code', help='Input subject coding',required=True)
    # parser.add_argument('-l','--lung', help='Input lung (left/right)',required=True)
    parser.add_argument('-p','--protocol', help='Input protocol (e.g. EIsupine)',required=True)
    parser.add_argument('-t','--type', help='Input fitting stage (prepare/initial/centrea/centrep/final)',required=True)
    parser.add_argument('-a','--adjust_val', help='Value for adjust operation',required=False)
    parser.add_argument('-d','--diagnostics', help='Diagnostics (True/False)',type=bool,required=False,default=False)

    args = parser.parse_args()
    study = args.study_code
    # lung = args.lung
    subject = args.subject_code
    protocol = args.protocol
    fit_type = args.type
    adjust_val = str(args.adjust_val)
    set_diagnostics_on(args.diagnostics)
    
    if study == "HA":
        study = "Human_Aging"
    elif study == "HLA":
        study = "Human_Lung_Atlas"

    print(study, subject, protocol, fit_type)
    
    template_path = 'template'
    # /hpc/mpag253/Torso/surface_fitting/input/AGING003/EIsupine/
    torso_directory = os.path.join(study, subject, protocol, 'Torso')
    lung_directory = os.path.join(study, subject, protocol, 'Lung')
    output_directory = os.path.join('output', subject, protocol, 'Torso')
    landmarks_directory = os.path.join('../landmarks', study, subject, protocol)

    # make_ipdata_lungs(input_directory, output_directory, lung)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
  
    # PREPARE
    if fit_type.lower() in ['prepare', 'pre']:
        print (" ===Move and scale an initial template mesh=== ")
        initialise_torso_mesh(torso_directory, lung_directory, output_directory, template_path, landmarks_directory)
        print (" -----mesh prepared")
        print (" -----transformed nodes exported")
        import_node_geometry_2d(os.path.join(template_path, 'templatetorso'))
        print (" -----initial nodes read")
        define_elem_geometry_2d(os.path.join(template_path, 'templatetorso'), 'unit')
        print (" -----initial elements read")
        export_elem_geometry_2d(os.path.join(output_directory, 'Torso_prepared'), 'preparedTorso', 0, 0)
        print (" -----elements exported")
        
    # CENTRE ANTERIOR/POSTERIOR
    elif fit_type.lower() in ['centreap', 'cap']:
        centre_ap(template_path, output_directory, adjust_val)
    
    # OTHER
    else:

        # Read in template node data
        if fit_type.lower() in ['init', 'initial' ]:
            print (" ===Read initial 2D torso geometry and surface data=== ")
            import_node_geometry_2d(os.path.join(output_directory, 'Torso_prepared'))
            print (" -----initial nodes read")
        if fit_type.lower() in ['upd', 'update', 'fin', 'final']:
            print (" ===Read updated 2D torso geometry and surface data=== ")
            import_node_geometry_2d(os.path.join(output_directory, 'Torso_edited' ))
            print (" -----edited nodes read")

        # Read in template element data
        define_elem_geometry_2d(os.path.join(template_path, 'templatetorso'), 'unit')
        print (" -----initial elements read")

        # Read in subject data
        # define_data_geometry(os.path.join(output_directory, 'surface_Torsotrimmed'))
        define_data_geometry(os.path.join(torso_directory, 'surface_Torsotrimmed_crop_tf'))
        print (" -----data read")
        
        # Run fit
        print (" ===Fitting surface to data=== ")
        group_name = 'prefitTorso'
        export_node_geometry_2d(os.path.join(output_directory, 'Torso_prefit'), group_name, 0)
        print (" -----nodes exported")
        export_elem_geometry_2d(os.path.join(output_directory, 'Torso_prefit'), group_name, 0, 0)
        print (" -----elements exported")
        niterations = 10
        if fit_type.lower() in ['init', 'initial']:
            fit_surface_geometry(niterations, os.path.join(template_path, 'torso_fix_initial'))  # 'torso_fix_none' 
        if fit_type.lower() in ['upd', 'update']:
            fit_surface_geometry(niterations, os.path.join(template_path, 'torso_fix_initial'))
        if fit_type.lower() in ['fin', 'final']:
            fit_surface_geometry(niterations, os.path.join(template_path, 'torso_fix_coords'))

        # Write results
        group_name = 'fittedTorso'
        export_node_geometry_2d(os.path.join(output_directory, 'Torso_fitted'), group_name, 0)
        print (" -----nodes exported")
        export_elem_geometry_2d(os.path.join(output_directory, 'Torso_fitted'), group_name, 0, 0)
        print (" -----elements exported")
        export_data_geometry(os.path.join(output_directory, 'Torso_fitted'), group_name, 0)
        write_node_geometry_2d(os.path.join(output_directory, 'Torso_fitted'))
        if fit_type.lower() in ['fin', 'final']:    
            export_node_geometry_2d(os.path.join(output_directory, subject + '_Torso_fitted'), group_name, 0)
            export_elem_geometry_2d(os.path.join(output_directory, subject + '_Torso_fitted'), group_name, 0, 0)

        print (" ===Fitting complete=== ")
            
            
if __name__ == '__main__':
    main()

