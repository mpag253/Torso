import numpy as np
import pandas as pd
import os


input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5), engine='openpyxl'))

scale_factors = [ 1.25, 1.25, 1.25]  # 761./512.*0.5/

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        [study, subject, protocol] = input_list[i, 1:4]
        print("\tScaling... \t"+study+", \t"+subject+", \t"+protocol)
        
        lung_dir = os.path.join(study, subject, protocol, 'Lung')
        torso_dir = os.path.join(study, subject, protocol, 'Torso')
    
        print(torso_dir + "/surface_Torsotrimmed.exdata")
        file_data = open(torso_dir + "/surface_Torsotrimmed.exdata", 'r')
        lines_data = file_data.readlines()
        for ln, line in enumerate(lines_data):
            if line.startswith(" Node:"):
                lines_data[ln+1] = "{:14.6e}\n".format(float(lines_data[ln+1])*scale_factors[0])
                lines_data[ln+2] = "{:14.6e}\n".format(float(lines_data[ln+2])*scale_factors[1])
                lines_data[ln+3] = "{:14.6e}\n".format(float(lines_data[ln+3])*scale_factors[2])
        f = open(torso_dir + "/surface_Torsotrimmed_scaled.exdata", "w")
        f.writelines(lines_data)
        f.close()
                
        print(torso_dir + "/surface_Torsotrimmed.ipdata")
        file_data = open(torso_dir + "/surface_Torsotrimmed.ipdata", 'r')
        lines_data = file_data.readlines()
        for ln, line in enumerate(lines_data):
            if not line.startswith(" converted"):
                line_data = line.split()
                line_data[1] = "{:.6e}".format(float(line_data[1])*scale_factors[0])
                line_data[2] = "{:.6e}".format(float(line_data[2])*scale_factors[1])
                line_data[3] = "{:.6e}".format(float(line_data[3])*scale_factors[2])
                lines_data[ln] = " {}\n".format(" ".join([i for i in line_data]))
        f = open(torso_dir + "/surface_Torsotrimmed_scaled.ipdata", "w")
        f.writelines(lines_data)
        f.close()