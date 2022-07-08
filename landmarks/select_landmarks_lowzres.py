#import natsort
import os
import nibabel as nib
import numpy as np
#import dicom2nifti
import matplotlib.pyplot as plt
#from PIL import Image
#import skimage
#import skimage.measure
#from scipy import ndimage
import sparse
import pickle as pkl

#from shutil import copyfile
#from openpyxl import load_workbook
import pandas as pd
from sys import exit

def run_landmark_selection(input_info_ee, input_info_ei, root, path_nifti):
    """Main funcion to run a ribs segmentation. 
    Reads a dicom/nifti and outputs centroid locations of the ribs (sternum not ommitted).
    
    Arguments:
        input_info:    list of strings for [cohort, subject, condition, path_dicom]
        root:          string of root directory
        path_nifti:    string of path to directory containing nifti files
        save_results:  boolean, whether to save the resultant sparse array of rib centroids (default True)
        troubleshooting_images: boolean, whether to generate intermediate images for troubleshooting (default False)
    
    Returns:
        (nothing)
    """
    
    # Setup
    [cohort_ee, subject_ee, condition_ee, path_dicom_ee, _] = input_info_ee
    [cohort_ei, subject_ei, condition_ei, path_dicom_ei, T2_z_ei] = input_info_ei
    print("\tRunning landmark selection...\t", subject_ee, end="\n")

    # Define nifti path
    path_nifti_specific_ee = os.path.join(path_nifti, cohort_ee, subject_ee, condition_ee, "Torso", subject_ee + ".nii")
    path_nifti_specific_ei = os.path.join(path_nifti, cohort_ei, subject_ei, condition_ei, "Torso", subject_ei + ".nii")
            
    ## If nifti doesn't already exist, convert dicom to nifti and load the nifti
    #if not os.path.isfile(path_nifti_specific):
    #    convert_dicoms(subject, cohort, path_dicom_specific, path_nifti_specific)
     
    # Load the nifti, segment the ribs, and optionally save the results
    if not os.path.isfile(path_nifti_specific_ee):
        print("\tRunning median segmentation...\t", subject_ee, "\tFailed. Nifti does not exist: ", path_nifti_specific_ee)
    elif not os.path.isfile(path_nifti_specific_ei):
        print("\tRunning median segmentation...\t", subject_ei, "\tFailed. Nifti does not exist: ", path_nifti_specific_ei)
    else:
        image_ee = load_nifti(path_nifti_specific_ee)
        image_ei = load_nifti(path_nifti_specific_ei)
        
        # Plot slices to select coorindates that define median plane
        manually_select_landmarks(image_ee, subject_ee, condition_ee, image_ei, subject_ei, condition_ei, T2_z_ei)

        print("\tRunning landmark selection...\t", subject_ee, "\tDone.")



def convert_dicoms(subject, cohort, dicom_path, nifti_path):
    """Converts the dicoms files for a subject to a nifti file.
    """
      
    if cohort == "Human_Lung_Atlas":
        #dicom2nifti.common.is_slice_increment_inconsistent(dicom_path)
        # https://icometrix.github.io/dicom2nifti/readme.html?highlight=inconsistent
        # Disable the validation of the slice increment.
        # This allows for converting data where the slice increment is not consistent.
        # USE WITH CAUTION!
        # dicom2nifti.settings.disable_validate_slice_increment()

        try:
            dicom2nifti.dicom_series_to_nifti(dicom_path, nifti_path, reorient_nifti=True)   # changed to true
        except: # dicom2nifti.exceptions.ConversionValidationError:
            # subprocess.run(["plastimatch", "convert", "--input", dicom_path, "--output-img", nifti_path])
            #print("(", subject, "NIfTI error)", end=None)
            print("\tRunning torso segmentation...\t", subject, "\tFailed. NIfTI conversion error.")
            pass

    if cohort == "Human_Aging":
        try:
            dicom2nifti.dicom_series_to_nifti(dicom_path, nifti_path, reorient_nifti=True)
        except: # dicom2nifti.exceptions.ConversionValidationError:
            # subprocess.run(["plastimatch", "convert", "--input", dicom_path, "--output-img", nifti_path])
            #print("(", subject, "NIfTI error)", end=None)
            print("\tRunning torso segmentation...\t", subject, "\tFailed. NIfTI conversion error.")
            pass


###
def load_nifti(nifti_path):
    """Loads a nifti file given a specified path.
    """
    ct_im_nii = nib.load(nifti_path)
    ct_im = np.asarray(ct_im_nii.get_fdata())  # note: changed to get_fdata to prevent deprecation warn
    return ct_im
    
    
###
def load_sparse(fname):
    spmat = pkl.load(open(fname, 'rb'))
    mat = sparse.COO.todense(spmat) 
    return mat
    
 
###    
def centroids_of_labels_3d(im, bg=-1):
    """ Returns the centroid, in pixel indices, for each label in a labelled 3D image, 'im'.
        Excludes the background specified by 'bg'.
    """
    vals, counts = np.unique(im, return_counts=True)
    centroids = [[] for _ in range(len(vals))]
    for i in range(len(vals)):
        indices = np.nonzero(im==vals[i])
        centroids[i] = [int(np.mean(indices[0])), int(np.mean(indices[1])), int(np.mean(indices[2]))]
    return centroids, vals  
    
      
###
def manually_select_landmarks(image_ee, subject_ee, protocol_ee, image_ei, subject_ei, protocol_ei, T2_z_ei):

    # EI slice
    plt.close('all')
    fig_ei, ax_ei = plt.subplots()
    ax_ei.imshow(image_ei[:, :, int(T2_z_ei)])
    ax_ei.set_title("EI: "+subject_ei+" "+protocol_ei+", x="+str(T2_z_ei))
    print("\tShowing... "+subject_ei+" "+protocol_ei+", x="+str(T2_z_ei))
    
    # show plot
    fig_ei.show()

    # EE slices
    i = np.shape(image_ee)[2] - 1
    continue_plots = True
    while continue_plots:
        fig_ee, ax_ee = plt.subplots()
        ax_ee.imshow(image_ee[:, :, int(i)])
        ax_ee.set_title("EE: "+subject_ee+" "+protocol_ee+", x="+str(i))
        print("\tShowing... "+subject_ee+" "+protocol_ee+", x="+str(i))
            
        # show plot
        fig_ee.show()
        
        # prompt for continuation
        input1 = str(input("\t\tcontinue? (y/n/b, yes/no/back):"))
        fig_ee.clear()
        plt.close(fig_ee)
        if (input1 == "n") or (i <= -np.shape(image_ee)[2]):
            continue_plots = False
        elif input1 == "b":
            i += 1
        else:
            i -= 1
            
    plt.close('all')

    




#############################################################################################################

#dicom_path = "/eresearch/lung/mpag253/Archive"
root = "/hpc/mpag253/Ribs/median_plane"
path_nifti = "/hpc/mpag253/Torso/segmentation"
#paths = [dicom_path, root, ]
input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/landmarks/torso_landmarks.xlsx", skiprows=0, usecols=[0,1,2,3,4,15]))
#median_plane = np.array(pd.read_excel("/hpc/mpag253/Ribs/median_plane/points_for_median_plane.xlsx", skiprows=0, usecols=[13, 19, 25, 31]))

#############################################################################################################

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        run_landmark_selection(input_list[i, 1:6], input_list[i-83, 1:6], root, path_nifti)
print("\n")







