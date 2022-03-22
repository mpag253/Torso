import os
import numpy as np
import pandas as pd

input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(25), engine='openpyxl'))

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        [study, subject, protocol] = input_list[i, 1:4]
        [adj_code_a, adj_code_p] = input_list[i, -2:]
        print("\nRunning... \t'centreap' for: \t"+study+", \t"+subject+", \t"+protocol)
        #print(adj_code_a)
        #print(adj_code_p)
        
        ### CENTREAP
        if adj_code_a != adj_code_a:
            adj_a = 0.
        else:
            adj_a = float(adj_code_a[2:])
            if adj_code_a[1] == "R":
                adj_a *= -1
        
        if adj_code_p != adj_code_p:
            adj_p = 0.
        else:
            adj_p = float(adj_code_p[2:])
            if adj_code_p[1] == "R":
                adj_p *= -1            
        
        adj_code = ",{:+.2f},{:+.2f}".format(adj_a,adj_p)
        cmd = "python surface_fit_torso.py -s "+study+" -c "+subject+" -p "+protocol+" -t centreap -a "+adj_code
        #print(cmd)
        os.system(cmd)
              
print("\n")

# in surface fitting venv
# python3 loop_adjust.py
