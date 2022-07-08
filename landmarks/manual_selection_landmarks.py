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

def run_landmark_selection(input_info, median_plane_xp, root, path_nifti):
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
    [cohort, subject, condition, path_dicom] = input_info
    print("\tRunning landmark selection...\t", subject, end="\n")

    # Define the filepaths
    if cohort == "Human_Lung_Atlas":
        path_dicom_specific = os.path.join(path_dicom, cohort, subject, condition, "Raw", "")
    elif cohort == "Human_Aging":
        #  + "_oldformat"
        # , "Archive"
        path_dicom_specific = os.path.join(path_dicom, cohort, subject, condition, "Raw")

    # Check if the dicom directory exists and contains files, then run segmentation
    if not os.path.exists(path_dicom_specific):
        print("\tRunning median segmentation...\t", subject, "\tFailed. Directory not found: ", path_dicom_specific)
    elif len(os.listdir(path_dicom_specific) ) == 0:
        print("\tRunning median segmentation...\t", subject, "\tFailed. Directory is empty: ", path_dicom_specific)
    else:
        path_output = os.path.join(root, cohort, subject, condition, "Median")
        path_nifti_specific = os.path.join(path_nifti, cohort, subject, condition, "Torso", subject + ".nii")
        if not os.path.exists(path_output):
            os.makedirs(path_output)
               
        # If nifti doesn't already exist, convert dicom to nifti and load the nifti
        if not os.path.isfile(path_nifti_specific):
            convert_dicoms(subject, cohort, path_dicom_specific, path_nifti_specific)
        
        # Load the nifti, segment the ribs, and optionally save the results
        if os.path.isfile(path_nifti_specific):
            image = load_nifti(path_nifti_specific)
            # image = image_filter(image, intensity=6000)  # FILTER !!!
            
            # Plot slices to select coorindates that define median plane
            manually_select_landmarks(image, subject, condition, median_plane_xp)

            print("\tRunning landmark selection...\t", subject, "\tDone.")



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
def manually_select_landmarks(image, subject, protocol, slice_xs):

    # define the index to take the slice
    slice_idx = int(np.mean(slice_xs[~np.isnan(slice_xs)]))

    # Load the rib labels matrix - to overlay ribs on image, help identify vertebral levels
    #ribs_image = load_sparse('/hpc/mpag253/Ribs/segmentation/Rib_Labels/ribs_labelled_'+subject+'_'+protocol+'.pkl')
    ribs_image = load_sparse('/hpc/mpag253/Ribs/segmentation/Rib_Labels/ribs_segmented_'+subject+'_'+protocol+'.pkl')

    # Keep rib labels within a specific region relative to the slice plane
    keep_min = 75
    #keep_max = -75
    ribs_image[:(slice_idx+keep_min), :, :] = 0
    #ribs_image[(slice_idx+keep_max):, :, :] = 0
    ribs_projection = np.any(ribs_image, axis=0)
    ribs_indices = np.nonzero(ribs_projection)
    
    ## Image labels
    #imlabels = range(3,11)
    ##imlabels = range(15,23)
    #imlabel_coords = np.zeros((len(imlabels), 2))
    #for i, imlabel in enumerate(imlabels):
    #    imlabel_indices = np.nonzero(ribs_image==imlabel)
    #    imlabel_max_idx = np.argmax(imlabel_indices[1])
    #    imlabel_coords[i, :] = [imlabel_indices[1][imlabel_max_idx], imlabel_indices[2][imlabel_max_idx]]
        
        
    
    # centre slice
    plt.close('all')
    plt.figure()
    plt.imshow(image[slice_idx, :, :])
    plt.scatter(x=ribs_indices[1], y=ribs_indices[0], c='r', s=1)
    #for i, imlabel in enumerate(imlabels):
    #    plt.text(imlabel_coords[i, 1], imlabel_coords[i, 0], str(imlabel),
    #             horizontalalignment='center', verticalalignment='center',
    #             bbox=dict(facecolor='white', alpha=1.0))
    plt.title(subject+" "+protocol+", x="+str(slice_idx))
    print("\tShowing... "+subject+" "+protocol+", x="+str(slice_idx))
    #plt.show()
    
    ## right slice
    #slice_idx += 150
    #plt.figure()
    #plt.imshow(image[slice_idx, :, :])
    #plt.title(subject+" "+protocol+", x="+str(slice_idx))
    #print("\tShowing... "+subject+" "+protocol+", x="+str(slice_idx))
    
    # left slice
    #slice_idx -= 200
    #plt.figure()
    #plt.imshow(image[slice_idx, :, :])
    #plt.title(subject+" "+protocol+", x="+str(slice_idx))
    #print("\tShowing... "+subject+" "+protocol+", x="+str(slice_idx))
    
    # show plots
    plt.show()
    




#############################################################################################################

#dicom_path = "/eresearch/lung/mpag253/Archive"
root = "/hpc/mpag253/Ribs/median_plane"
path_nifti = "/hpc/mpag253/Torso/segmentation"
#paths = [dicom_path, root, ]
input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/landmarks/torso_landmarks.xlsx", skiprows=0, usecols=range(5)))
median_plane = np.array(pd.read_excel("/hpc/mpag253/Ribs/median_plane/points_for_median_plane.xlsx", skiprows=0, usecols=[13, 19, 25, 31]))

#############################################################################################################

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        run_landmark_selection(input_list[i, 1:5], median_plane[i, :], root, path_nifti)
print("\n")







