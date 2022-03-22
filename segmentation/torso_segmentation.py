import natsort
import os
import nibabel as nib
import numpy as np
import dicom2nifti
import matplotlib.pyplot as plt
from PIL import Image
import skimage
import skimage.measure
from scipy import ndimage

from shutil import copyfile
#from openpyxl import load_workbook
import pandas as pd


def run_torso_segmentation(input_info, path_nifti, save_masks=True, use_bed_mask=False, troubleshooting_images=[False, False]):

    [cohort, subject, condition, path_dicom] = input_info
    threshold = -320
    #[path_dicom, path_nifti] = paths
    print("\tRunning torso segmentation...\t", subject, end="\r")
    
    # Define the filepaths
    if cohort == "Human_Lung_Atlas":
        path_dicom_specific = os.path.join(path_dicom, cohort, subject, condition, "Raw", "")
    elif cohort == "Human_Aging":
        #  + "_oldformat"
        # , "Archive"
        path_dicom_specific = os.path.join(path_dicom, cohort, subject, condition, "Raw")

    # Check if the dicom directory exists and contains files, then run segmentation
    if not os.path.exists(path_dicom_specific):
        print("\tRunning torso segmentation...\t", subject, "\tFailed. Directory not found: ", path_dicom_specific)
    elif len(os.listdir(path_dicom_specific) ) == 0:
        print("\tRunning torso segmentation...\t", subject, "\tFailed. Directory is empty: ", path_dicom_specific)
    else:
        path_output = os.path.join(path_nifti, cohort, subject, condition, "Torso")
        path_nifti_specific = os.path.join(path_output, subject + ".nii")
        if not os.path.exists(path_output):
            os.makedirs(path_output)
               
        # Convert dicom to nifti and load the nifti
        if not os.path.isfile(path_nifti_specific):
            convert_dicoms(subject, cohort, path_dicom_specific, path_nifti_specific)
        
        if os.path.isfile(path_nifti_specific):
            image = load_nifti(path_nifti_specific)
            # image = image_filter(image, intensity=6000)  # FILTER !!!
            if use_bed_mask:
                bed_mask = generate_bed_mask(image, -31, threshold)
                #bed_mask[:,:,0:-168] = 0 # eliminate selected layers from being masked
            else:
                bed_mask = None

            # Generate surface mask and save as TIFF image
            binary_image = segment_lung_mask(image, subject, bed_mask, threshold=threshold, troubleshooting_images=troubleshooting_images)
            surface_mask(binary_image, subject, path_output, save_masks=save_masks)

            print("\tRunning torso segmentation...\t", subject, "\tDone.")


def image_filter(image, intensity=0):

    im_cropped = np.copy(image)
    im_cropped[im_cropped > 0] = 0
    band_highpass = ndimage.gaussian_filter(im_cropped, 2)
    band_lowpass = ndimage.gaussian_filter(im_cropped, 1.5)  # 1.5
    bandpass = -(band_lowpass - band_highpass)
    bandpass_normd = (bandpass - np.amin(bandpass)) / (np.amax(bandpass) - np.amin(bandpass))
    bandpass_trans = np.power(bandpass_normd, 1.5)
    filter = -intensity*(bandpass_trans - np.median(bandpass_trans)) #-300*(bandpass_normd - np.median(bandpass_normd))
    im_filtered = image + filter

    # # Plot the images
    # fig, axs = plt.subplots(1, 3)
    # im1 = axs[0].imshow(image[400:700, 50:250, 0], vmin=np.amin(im_filtered), vmax=np.amax(im_filtered)) #[400:700, 50:250])
    # plt.colorbar(im1, ax=axs[0], orientation='horizontal')
    # im2 = axs[1].imshow(filter[400:700, 50:250, 0]) #[400:700, 50:250])
    # plt.colorbar(im2, ax=axs[1], orientation='horizontal')
    # im3 = axs[2].imshow(im_filtered[400:700, 50:250, 0], vmin=np.amin(im_filtered), vmax=np.amax(im_filtered))  # [400:700, 50:250])
    # plt.colorbar(im3, ax=axs[2], orientation='horizontal')
    # plt.show()

    # # Plot the images - thresholds
    # fig, axs = plt.subplots(1, 4)
    # threshold_1 = np.zeros(np.shape(image))
    # threshold_1[im_filtered > -320] = 1
    # threshold_2 = np.zeros(np.shape(image))
    # threshold_2[im_filtered > -150] = 1
    # threshold_3 = np.zeros(np.shape(image))
    # threshold_3[im_filtered > -0] = 1
    # im1 = axs[0].imshow(image[:, :, 0])
    # im1 = axs[0].imshow(threshold_1[:, :, 0])
    # im2 = axs[1].imshow(threshold_2[:, :, 0])
    # im3 = axs[2].imshow(threshold_3[:, :, 0])
    # plt.show()

    return im_filtered


def generate_bed_mask(image, slice_index, threshold):

    # Identify a slice for the mask and threshold
    slice = image[:, :, slice_index]
    # fig, axs = plt.subplots(1, 3)
    # axs[0].imshow(slice)
    bed_mask = np.array(slice > threshold, dtype=np.int8) + 1  # air=1, torso=2 --- original threshold=-320

    # Identify the background (retaining the bad)
    labels = skimage.measure.label(bed_mask)
    background_labels = np.unique((labels[0, 0], labels[-1, 0]))
    bed_mask[np.isin(labels, background_labels)] = 0  # bg=0, air=1, torso=2
    # axs[1].imshow(bed_mask)

    # Merge air and torso
    bed_mask[bed_mask > 0] = 1  # bg=0, air/torso=1
    # axs[2].imshow(bed_mask)

    # Remove the torso
    #labels = skimage.measure.label(bed_mask)
    #background_labels = np.unique((labels[20, 20], labels[-20, 20]))
    #bed_mask[np.invert(np.isin(labels, background_labels))] = 0  # bg=0, air=1, torso=2
    bed_mask = np.logical_not(bed_mask).astype(int)
    # axs[1].imshow(bed_mask)
    
    # Shift mask N pixels towards torso
    N = 12
    bed_mask[:, N:] = bed_mask[:, :-N]
    # axs[2].imshow(bed_mask)

    bed_mask = np.tile(bed_mask, (np.shape(image)[2], 1, 1))
    bed_mask = np.moveaxis(bed_mask, 0, -1)

    # plt.show()

    return bed_mask



def convert_dicoms(subject, cohort, dicom_path, nifti_path):
      
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


def load_nifti(nifti_path):
    ct_im_nii = nib.load(nifti_path)
    ct_im = np.asarray(ct_im_nii.get_fdata())  # note: changed to get_fdata to prevent deprecation warn
    return ct_im
    
    
def generate_img_fig(binary_img, filename, print_string, troubleshooting_images):
    if troubleshooting_images:
        plt.figure()
        plt.imshow(binary_img)
        plt.savefig(filename+".tiff")
        print("\t\tSaved... "+filename+".tiff: "+print_string)
        #print("\t\tShowing... "+filename+".tiff: "+print_string)
        #plt.show()
        

def largest_label_volume(im, bg=-1):
    vals, counts = np.unique(im, return_counts=True)

    counts = counts[vals != bg]
    vals = vals[vals != bg]

    if len(counts) > 0:
        return vals[np.argmax(counts)]
    else:
        return None


def segment_lung_mask(image, subject, bed_mask, threshold=-320, troubleshooting_images=[False, False]):

    # Parameters for troubleshooting images
    [ts_images_1, ts_images_2] = troubleshooting_images
    if ts_images_1:
        print("\n", end="\r")
    case_name = "troubleshooting_image_"
    if np.shape(image)[2] > 100:
        smpl_slc = -85 #np.shape(image)[2]/2
    else:
        smpl_slc = 0    

    # Threshold 3d image to create pseudo-binary image
    # not actually binary, but 1 and 2 (for air and torso, respectively)
    # 0 will be treated as background, which we do not want
    generate_img_fig(image[:,:,smpl_slc], case_name+"1", "initial image", ts_images_1)
    binary_image = np.array(image > threshold, dtype=np.int8) + 1  # air=1, torso=2; original threshold=-320
    if bed_mask is not None:
        binary_image[bed_mask == 1] = 1   
    generate_img_fig(binary_image[:,:,smpl_slc], case_name+"2", "thresholded", ts_images_1)

    # Keep only the largest solid structure (in each slice)
    binary_image = np.moveaxis(binary_image, -1, 0) # switch axes to enumerate easily
    for i, axial_slice in enumerate(binary_image):
        axial_slice = axial_slice - 1 # converts to pseudo-binary: air=0, torso=1
        labels = skimage.measure.label(axial_slice) #, connectivity=1)
        l_max = largest_label_volume(labels, bg=0)
        binary_image[i][labels != l_max] = 1  # air=1, torso=2
    generate_img_fig(binary_image[smpl_slc, :, :], case_name+"3", "retain torso", ts_images_1)
    binary_image = np.moveaxis(binary_image, 0, -1)  # switch axes back to normal

    # # Keep only the largest solid structure (in the whole volume)
    # temp_image = binary_image - 1
    # labels = skimage.measure.label(temp_image) #, connectivity=1)
    # l_max = largest_label_volume(labels, bg=0)
    # #if l_max is not None:  # This slice contains some lung
    # binary_image[labels != l_max] = 1  # air=1, torso=2
    # generate_img_fig(binary_image[:,:,smpl_slc], case_name+"3", "retain torso", ts_images_1)
    # generate_img_fig(binary_image[:,:,0], case_name+"3b", "retain torso", ts_images_1)

    # Identifying the background (in each slice)
    binary_image = np.moveaxis(binary_image, -1, 0) # switch axes to enumerate easily
    for i, axial_slice in enumerate(binary_image):
        labels = skimage.measure.label(axial_slice)
        background_labels = np.unique( (labels[ 0,  0], labels[-1,  0], labels[ 0, -1], labels[-1, -1]) )
        binary_image[i][np.isin(labels, background_labels)] = 0  # bg=0, air=1, torso=2
    generate_img_fig(binary_image[smpl_slc,:,:], case_name+"4", "identify background", ts_images_1)
    binary_image = np.moveaxis(binary_image, 0, -1)  # switch axes back to normal

    # Identifying the background (as one operation for whole volume)
    #labels = skimage.measure.label(binary_image)
    #background_labels = np.concatenate( (labels[ 0,  0, :], labels[-1,  0, :], labels[ 0, -1, :], labels[-1, -1, :]) )
    #background_labels = np.unique(background_labels)
    #binary_image[np.isin(labels, background_labels)] = 0  # bg=0, air=1, torso=2
    #generate_img_fig(binary_image[:,:,smpl_slc], case_name+"4", "identify background", ts_images_1)

    # Showing transverse slice
    # fig, axs = plt.subplots(1)
    # axs.imshow(binary_image[int(np.shape(binary_image)[0]/2), :, :])
    # plt.show()

    # Make the image actual binary and invert it, torso is now 1
    binary_image[binary_image > 0] = 1  # bg=0, air/torso=1 
    binary_image = 1 - binary_image     # bg=1, air/torso=0
    generate_img_fig(binary_image[:,:,smpl_slc], case_name+"5", "convert and invert", ts_images_1)

    # # Count area of each axial slice
    # counts = [np.sum((1-binary_image[:, :, i]) == 0) for i in range(np.shape(binary_image)[2])]
    # counts = np.flip(counts)
    # deviation = [counts[i]-((counts[i+1]+counts[i-1])/2) for i in range(1, np.shape(binary_image)[2]-1)]
    # fig = plt.figure()
    # plt.plot(range(1, np.shape(binary_image)[2]-1), deviation, linestyle='solid')
    # plt.xlabel("Mask Number")
    # plt.ylabel("Deviation in Torso Area")
    # plt.title("Validation: "+subject)
    # plt.savefig("./Validation/smoothness_deviation_" + subject + ".tiff")
    # # plt.show()
    # plt.close(fig)

    return binary_image


def surface_mask(binary_image, subject, output_dir, save_masks=True):

    #extract surface mesh from the binary image
    vertices, faces, normals, values = skimage.measure.marching_cubes(binary_image)

    #separate vertices into axes arrays
    xverts = np.array([vert[0] for vert in vertices]).astype(np.int64)
    yverts = np.array([vert[1] for vert in vertices]).astype(np.int64)
    zverts = np.array([vert[2] for vert in vertices]).astype(np.int64)

    torso_mask = np.zeros(binary_image.shape).astype(np.uint8)
    torso_mask[yverts, xverts, zverts] = 255

    # Eliminate extraneous pixels
    # switch axes and enumerate for speed
    for i in range(0, torso_mask.shape[2]):
        mask_i = torso_mask[:, :, i]
        labels_i = skimage.measure.label(mask_i+1, connectivity=1)
        torso_label = labels_i[int(np.shape(labels_i)[0]/2), int(np.shape(labels_i)[1]/2)]
        torso_i = np.array(labels_i == torso_label, dtype=np.int8)
        dilation = ndimage.binary_dilation(torso_i).astype(torso_i.dtype)
        torso_mask[:, :, i] = (dilation - torso_i)*255
        # opening = ndimage.binary_opening(torso_i, structure=np.ones((5, 5))).astype(torso_i.dtype)
        # dilation = ndimage.binary_dilation(opening.astype(opening.dtype))
        # torso_mask[:, :, i] = (dilation - opening)*255

    # # Count area of each axial slice
    # counts = [np.sum((torso_mask[:, :, i]) == 255) for i in range(np.shape(torso_mask)[2])]
    # counts = np.flip(counts)
    # deviation = [counts[i]-((counts[i+1]+counts[i-1])/2) for i in range(1, np.shape(torso_mask)[2]-1)]
    # fig = plt.figure()
    # plt.plot(range(1, np.shape(binary_image)[2]-1), deviation, linestyle='solid')
    # plt.xlabel("Mask Number")
    # plt.ylabel("Deviation in Outline Pixels")
    # plt.title("Validation: "+subject)
    # plt.savefig("./Validation/smoothness_deviation_TEST_" + subject + ".tiff")
    # # plt.show()
    # plt.close(fig)

    # # Showing transverse slice
    # fig, axs = plt.subplots(1)
    # axs.imshow(torso_mask[int(np.shape(torso_mask)[0]/2), :, :])
    # plt.show()

    # Align torso mask along the same axes as dicoms
    # original was: np.flipud(torso_mask), np.flip(torso_mask, axis=2)
    #torso_mask = np.flipud(torso_mask) # flips AP?
    torso_mask = np.flip(torso_mask, axis=2) # flips z

    if save_masks:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for i in range(0, torso_mask.shape[2]):
            #print(type(np.uint8(torso_mask[:, :, i])), np.unique(np.uint8(torso_mask[:, :, i])))
            img = Image.fromarray(np.uint8(torso_mask[:, :, i]))
            img.save(output_dir+"/torso_mask" + '{:04d}'.format(i) + ".tiff")


def check_masks(cohort, subject, condition, path_nifti):
    
    mask_path = os.path.join(path_nifti, cohort, subject, condition, "Torso") 
    if not os.path.exists(mask_path):
        #print("Can't find images for:\t"+subject)
        pass
    elif len(os.listdir(mask_path) ) < 2:
        #print("Can't find images for:\t"+subject)
        pass
    else:
        all_dir_files = os.listdir(mask_path)
        mask_files = [f for f in all_dir_files if f.endswith(".tiff")]
        mask_files = natsort.natsorted(mask_files)
        #print("Showing images for:\t"+subject)
        to_show = [0, int(len(mask_files)/2), -1]
        for i, j in enumerate(to_show):
            copyfile(mask_path+"/"+mask_files[j],
                     "./Mask Checks/"+subject+"_check{}.tiff".format(i+1))
        #print("Saved images for:\t"+subject)    


#############################################################################################################

#dicom_path = "/eresearch/lung/mpag253/Archive"
root = "/hpc/mpag253/Torso/segmentation"
#paths = [dicom_path, root, ]
input_list = np.array(pd.read_excel("/hpc/mpag253/Torso/torso_checklist.xlsx", skiprows=0, usecols=range(5)))

#############################################################################################################

print("\n")
for i in range(np.shape(input_list)[0]):
    if input_list[i, 0] == 1:
        run_torso_segmentation(input_list[i, 1:5], root, save_masks=True, use_bed_mask=True,
                               troubleshooting_images=[True, False])
        # check_masks(cohort, subject, condition, root)
print("\n")







