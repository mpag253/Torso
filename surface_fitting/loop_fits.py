import os
import numpy as np
import pandas as pd

input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5), engine='openpyxl'))

action="prepare"
#action="initial"
#action="copy"
#action="update"
#action="copy"
#action="final"


print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        [study, subject, protocol] = input_list[i, 1:4]
        
        print("\nRunning... \t'"+action+"' for: \t"+study+", \t"+subject+", \t"+protocol)
        
        if action == "copy":
            ### COPY FITTED TO EDITED
            cmd = "cp output/"+subject+"/"+protocol+"/Torso/Torso_fitted.exnode output/"+subject+"/"+protocol+"/Torso/Torso_edited.exnode"
            #print(cmd)
            os.system(cmd)
        
        else:
            ### SURFACE FIT
            cmd = "python surface_fit_torso.py -s "+study+" -c "+subject+" -p "+protocol+" -t "+action
            ## print(cmd)
            os.system(cmd)
        

        
            ### COPY TORSO SURFACE FILES
            #dir_paste = study+"/"+subject+"/"+protocol+"/Torso"
            ##protocol = "EIsupine"
            #dir_copy = "/eresearch/lung/mpag253/"+study+"/"+subject+"/"+protocol+"/Torso/"
            #cmd1 = "mkdir -p "+dir_paste
            #cmd2 = "cp "+dir_copy+"* "+dir_paste
            ##print(cmd1)
            ##print(cmd2)
            #os.system(cmd1)
            #os.system(cmd2)
            ##os.system("rm -r "+dir_paste)        
            
            ### COPY LUNG FILES
            #dir_paste = study+"/"+subject+"/"+protocol+"/Lung/SurfaceFEMesh"
            ##protocol = "EEsupine"
            #dir_copy = "/eresearch/lung/mpag253/Archive/"+study+"/"+subject+"/"+protocol+"/Lung/SurfaceFEMesh/"
            #cmd1 = "mkdir -p "+dir_paste
            #cmd2 = "cp "+dir_copy+"* "+dir_paste
            ##print(cmd1)
            ##print(cmd2)
            #os.system(cmd1)
            #os.system(cmd2)
            ###os.system("rm -r "+dir_paste)        
        
print("\n")


# in surface fitting venv
# python3 loop_fits.py
