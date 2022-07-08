import os
import numpy as np
import argparse
import math



def flip_nodes_in_dim(file_lines, dim, dim0):
    for ln, line in enumerate(file_lines):
        if line.startswith(" Node:"):
            #node_id = int(line.split()[-1])
            dim_vals = np.array(file_lines[ln+dim].split()).astype(float)
            dim_vals[0] = 2*dim0 - dim_vals[0]
            file_lines[ln+dim] = "  {:>13.6f}{:>13.6f}{:>13.6f}{:>13.6f}\n".format(dim_vals[0], dim_vals[1], dim_vals[2], dim_vals[3])
    return file_lines
    
def flip_derivs_in_dim(file_lines, dim):
    for ln, line in enumerate(file_lines):
        if line.startswith(" Node:"):
            dim_vals = np.array(file_lines[ln+dim].split()).astype(float)
            dim_vals[1:4] *= -1
            file_lines[ln+dim] = "  {:>13.6f}{:>13.6f}{:>13.6f}{:>13.6f}\n".format(dim_vals[0], dim_vals[1], dim_vals[2], dim_vals[3])
    return file_lines
    
    
# Parameters
subject = 'AGING015'
protocol = 'EIsupine'
output_dir = os.path.join('output', subject, protocol, 'Torso')

# Read the fitted .exnode file
file_exn = open(os.path.join(output_dir,'Torso_fitted.exnode'), 'r')
lines_exn = file_exn.readlines()
file_exn.close()

# Find centre y
for ln, line in enumerate(lines_exn):
    if line.startswith(" Node:"):
        node_id = int(line.split()[-1])
        if node_id == 112:
            y_vals = np.array(lines_exn[ln+2].split()).astype(float)
            y0 = y_vals[0]

# Do flip fix
lines_exn = flip_nodes_in_dim(lines_exn, 2, y0)
lines_exn = flip_derivs_in_dim(lines_exn, 2)
    
# Write to file
#file_out = open(output_dir+'/Torso_edited.exnode', 'w')
file_out = open(output_dir+'/Torso_fitted.exnode', 'w')
file_out.writelines(lines_exn)
file_out.close()