import numpy as np
import pandas as pd
import os


input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5), engine='openpyxl'))

sbj_minmax = np.empty([0,3])

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        [study, subject, protocol] = input_list[i, 1:4]
        print("\tReading z for... \t"+study+", \t"+subject+", \t"+protocol)
        
        lung_dir = os.path.join(study, subject, protocol, 'Lung')
        torso_dir = os.path.join(study, subject, protocol, 'Torso')
    
        print(torso_dir + "/surface_Torsotrimmed.exdata")
        file_data = open(torso_dir + "/surface_Torsotrimmed.exdata", 'r')
        lines_data = file_data.readlines()
        min_z = 1e6
        max_z = -1e6
        for ln, line in enumerate(lines_data):
            if line.startswith(" Node:"):
                z = float(lines_data[ln+3])
                if z < min_z:
                    min_z = z
                if z > max_z:
                    max_z = z
        
        sbj_minmax = np.vstack((sbj_minmax, [[min_z, max_z, max_z-min_z]]))
        
print(sbj_minmax)
np.savetxt("output_troubleshoot_z.csv", sbj_minmax, delimiter=",")
