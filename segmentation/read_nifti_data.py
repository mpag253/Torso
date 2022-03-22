import nibabel as nib
import numpy as np
import pandas as pd
import os

def load_nifti(nifti_path):
    ct_im_nii = nib.load(nifti_path)
    ct_im = np.asarray(ct_im_nii.get_fdata())  # note: changed to get_fdata to prevent deprecation warn
    ct_info = ct_im_nii.header
    return ct_im, ct_info
    

def run_read_nifti_data(input_info, path_nifti):

    [cohort, subject, condition, path_dicom] = input_info
    print("\tReading NIfTI data...\t", subject, end="\r")

    path_output = os.path.join(path_nifti, cohort, subject, condition, "Torso")
    path_nifti_specific = os.path.join(path_output, subject + ".nii")
           
    
    if os.path.isfile(path_nifti_specific):
        [image, im_info] = load_nifti(path_nifti_specific)
        dims = np.shape(image)
        pixdims = im_info.get('pixdim')
        
        writeline = cohort+","+subject+","+condition+",{:d},{:d},{:d},{:17.8f},{:17.8f},{:17.8f}\n".format(
                      dims[0],dims[1],dims[2],pixdims[1],pixdims[2],pixdims[3])
        print("\tReading NIfTI data...\t", subject, "\tDone.")
        return writeline
    else:
        print("\tReading NIfTI data...\t", subject, "\tFailed. NIfTI does not exist.")
        writeline = cohort+","+subject+","+condition+"\n"
        return writeline
    
#############################################################################################################

#dicom_path = "/eresearch/lung/mpag253/Archive"
root = "/hpc/mpag253/Torso/segmentation"
#paths = [dicom_path, root, ]
input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5)))

#############################################################################################################

print("\n")
writelines = []
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        writeline = run_read_nifti_data(input_list[i, 1:5], root)
        writelines.append(writeline)
f = open("nifti_data.csv", "w")
f.writelines(writelines)
f.close()
print("\n")
