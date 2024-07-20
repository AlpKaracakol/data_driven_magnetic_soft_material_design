import pandas as pd
from glob import glob
import pickle
import numpy as np
import math
import time
import sys
if sys.version_info[1] > 6:
    import ezdxf
    from ezdxf.addons.drawing import matplotlib
    from ezdxf import units
import subprocess as sub
import os
import cv2
from PIL import Image
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.proj3d import proj_transform
from matplotlib.patches import FancyArrowPatch
from matplotlib import cm
from scipy.spatial import ConvexHull

from tools.utils import natural_sort, draw3Dshapev2, drawInitShapeRGB, draw3Dshape_videoFrame, getDesiredShape
from src.base import Sim, Env
from tools.read_write_voxelyze import write_voxelyze_file, write_magnetic_profile, xml2npArray, write_magnetic_field
from tools.control_fields import get_magnetic_control_field



""" functions """

def load_pickle_at(path_to_pickle):
    with open(path_to_pickle, 'rb') as f:
        out = pickle.load(f)
    return out

def pickle_at(pickle_this, at):
    with open(at, "wb") as handle:
        pickle.dump(pickle_this, handle)

def sync_run_args(run_args):
    run_args.voxel_color = [0., 0., 0., 0.9]
    run_args.create_history = 0
    run_args.record_video = 0
    run_args.KinEThreshold = 1e-15
    run_args.history_bandwidth = 0 
    run_args.history_sim_time = 0
    run_args.video_bandwidth = 0
    run_args.isFixedFromTop = 0
    run_args.isFixedFromBottom = 0

    run_args.CaseMaxMinPosZ = 0
    
    return run_args


def plot_morphologies(path_to_files, path_to_save, dim_size = (20,20), dpiValue = 600):
    """ Plots the morpholgoy of the designed individuals in a combined figure """

    # get the morph and M profile data for each individual
    pickled_inds = glob(path_to_files + "/*/design_parameters.pkl")
    ordered_pickled_inds = natural_sort(pickled_inds, reverse=False)    

    index_x = 0
    index_y = 0
    xlimit, ylimit = dim_size
    materialStacked = []
    saving_counter = 0
    ind_last = None
    displayMatrix = None

    for i in range(len(ordered_pickled_inds)):
        ind2load = ordered_pickled_inds[i]
        with open(ind2load, 'rb') as handle:
            ind_dict = pickle.load(handle)
            args = ind_dict["args"]
            design_params = ind_dict["indDesignParams"]
            voxel_map = design_params["material"].astype(int)
            voxel_map = voxel_map[:,:,0]
            Mphi = design_params["Mphi"]
            Mtheta = design_params["Mtheta"]

            voxel_map = np.pad(voxel_map, ((1, 1), (1, 1)), 'constant', constant_values=(0,))

            if index_x == 0:
                materialStacked.append(voxel_map)
                index_x += 1
            elif index_x < xlimit:
                materialStacked[index_y] = np.hstack((materialStacked[index_y], voxel_map))
                index_x += 1
            
            if index_x > (xlimit-1):
                index_y += 1
                index_x = 0
            
            if index_y > (ylimit-1):
                 
                for j in range(len(materialStacked)):
                    if displayMatrix is not None:
                        displayMatrix = np.vstack((displayMatrix,materialStacked[j]))
                    else: 
                        displayMatrix = materialStacked[j]
                # Display matrix
                plt.matshow(displayMatrix, cmap = "binary",  vmin=0, vmax=1)
                plt.axis('off')

                if ind_last is None:
                    ind_start = 0
                ind_last = i
                plt.savefig(path_to_save + "/finalStructure_Ind_" + str(ind_start) + "_to_" + str(ind_last) + ".png", bbox_inches='tight',pad_inches = 0, dpi=dpiValue, )
                ind_start = ind_last+1
                
                index_x = 0
                index_y = 0
                materialStacked = []
                displayMatrix = None
                saving_counter += 1
                plt.close()

    # plot the left over inds as well
    if displayMatrix is None:
        displayMatrix = materialStacked[0]
    elif len(materialStacked) > 0:
        if materialStacked[index_y].shape[1] < displayMatrix.shape[0]:
            materialStacked[index_y] = np.hstack((materialStacked[index_y], np.zeros(displayMatrix.shape[0]-materialStacked[index_y].shape[1], materialStacked[index_y].shape[1])))
        displayMatrix = np.vstack((displayMatrix,materialStacked[index_y]))
    
    if ind_last is None:
        ind_start = 0
    ind_last = i
    plt.matshow(displayMatrix, cmap = "binary",  vmin=0, vmax=1)
    plt.axis('off')

    ind_last = i
    plt.savefig(path_to_save + "/finalStructure_Ind_" + str(ind_start) + "_to_" + str(ind_last) + ".png", bbox_inches='tight',pad_inches = 0, dpi=dpiValue, )
    print("Plotting Morphologies is done")
    plt.close()
    
def plot_morphologiesRGB(path_to_files, path_to_save, dim_size = (20,20), dpiValue = 600):
    """ Plots the morpholgoy of the designed individuals in a combined figure """

    # get the morph and M profile data for each individual
    pickled_inds = glob(path_to_files + "/*/design_parameters.pkl")
    ordered_pickled_inds = natural_sort(pickled_inds, reverse=False)    

    index_x = 0
    index_y = 0
    xlimit, ylimit = dim_size
    materialStacked = []
    saving_counter = 0
    ind_last = None
    displayMatrix = None
    # im=[]

    for i in range(len(ordered_pickled_inds)):
        ind2load = ordered_pickled_inds[i]
        with open(ind2load, 'rb') as handle:
            ind_dict = pickle.load(handle)
            args = ind_dict["args"]
            design_parameters = ind_dict["indDesignParams"]


            materialMatrix = design_parameters["material"]
            Mtheta = design_parameters["Mtheta"]
            Mphi = design_parameters["Mphi"]

            im = np.zeros((materialMatrix.shape[0],materialMatrix.shape[1],4))
            #normalize the desin params
            im[:,:,0]= (materialMatrix[:,:,0]+0)*1/1
            im[:,:,1]= (Mtheta[:,:,0]+math.pi)*1/(2*math.pi)
            im[:,:,2]= (Mphi[:,:,0]+0)*1/(math.pi)

            # alpha value for the empty voxels, set it to transperant
            im[:,:,3]= (materialMatrix[:,:,0]+0)*1/1   

            im = np.pad(im, ((1, 1), (1, 1),(0, 0)), 'constant', constant_values =1)

            voxel_map = im

            if index_x == 0:
                materialStacked.append(voxel_map)
                index_x += 1
            elif index_x < xlimit:
                materialStacked[index_y] = np.concatenate((materialStacked[index_y], voxel_map), axis=1, out=None)
                index_x += 1
            
            if index_x > (xlimit-1):
                index_y += 1
                index_x = 0
            
            if index_y > (ylimit-1):
                 
                for j in range(len(materialStacked)):
                    if displayMatrix is not None:
                        displayMatrix = np.concatenate((displayMatrix,materialStacked[j]), axis=0, out=None)
                    else: 
                        displayMatrix = materialStacked[j]
                
                # Display matrix
                
                # plt.matshow(displayMatrix, cmap = "binary",  vmin=0, vmax=1)
                # plt.axis('off')

                if ind_last is None:
                    ind_start = 0
                ind_last = i
                # plt.savefig(path_to_save + "/finalStructure_Ind_" + str(ind_start) + "_to_" + str(ind_last) + ".png", bbox_inches='tight',pad_inches = 0, dpi=dpiValue, )
                filePath2save = path_to_save + "/finalStructure_Ind_" + str(ind_start) + "_to_" + str(ind_last) + "RGB"
                plt.imsave(filePath2save+".png", displayMatrix, dpi=dpiValue)
                ind_start = ind_last+1
                
                index_x = 0
                index_y = 0
                materialStacked = []
                displayMatrix = None
                saving_counter += 1

    # plot the left over inds as well
    if displayMatrix is None:
        displayMatrix = materialStacked[0]
    elif len(materialStacked) > 0:
        if materialStacked[index_y].shape[1] < displayMatrix.shape[0]:
            materialStacked[index_y] = np.concatenate((materialStacked[index_y], np.zeros(displayMatrix.shape[0]-materialStacked[index_y].shape[1], materialStacked[index_y].shape[1])), axis=1, out=None)
        displayMatrix =  np.concatenate((displayMatrix,materialStacked[index_y]), axis=1, out=None)
    
    if ind_last is None:
        ind_start = 0
    ind_last = i
    filePath2save = path_to_save + "/finalStructure_Ind_" + str(ind_start) + "_to_" + str(ind_last) + "RGB"
    plt.imsave(filePath2save+".png", displayMatrix, dpi=dpiValue)
    print("Plotting Morphologies in RGB is done")


def write_position_to_excel(args, robot, positions, excelFileName=None):

    excelFileName = excelFileName + '.xlsx'

    # Prepare data
    data_df = pd.DataFrame(positions)

    # Change the index of the table
    data_df.columns = ['x (mm)','y (mm)','z (mm)']  

    # Write the file into the excel table
    writer = pd.ExcelWriter(excelFileName)  
    data_df.to_excel(writer,'page_1',float_format='%f') 
    writer.save()
    writer.close()

    print("Data saved to excel file at: " + excelFileName)
    return 1


def NN_dataset_generator(args, path_to_files, path_to_save):
    # get the morph and M profile data for each individual
    inds_folders = glob(path_to_files + "/*/id*.pickle")
    ordered_ind_folder= natural_sort(inds_folders, reverse=False)


    f = open(path_to_save, "w")
    

    # read each ind and get the input and output for NN
    for i in range(len(ordered_ind_folder)):
        ind2load = ordered_ind_folder[i]
        with open(ind2load, 'rb') as handle:
            ind_dict = pickle.load(handle)
            ind=ind_dict["individual"]
            # get the data
            id = ind.id
            voxel_map = ind.designParameters["material"]
            Mtheta = ind.segmentedMprofile["Mtheta"]
            Mphi = ind.segmentedMprofile["Mphi"]
            fitness = ind.fitness

            voxel_map1D = voxel_map.flatten()
            Mtheta1D = Mtheta.flatten()
            Mphi1D= Mphi.flatten()


            # write it into txt file
            f.write(str(id)+";")
            np.savetxt(f, [voxel_map1D], delimiter=',', fmt='%-2.5f', newline="")
            f.write(";")
            np.savetxt(f, [Mtheta1D], delimiter=',', fmt='%-2.5f',newline="")
            f.write(";")
            np.savetxt(f, [Mphi1D], delimiter=',', fmt='%-2.5f',newline="")
            f.write(";")
            f.write(str(fitness)+";\n")

    f.close()


#process inds2process folder for experiments
def get_robots_ready_for_experiment(path_to_files, path_to_save=None, render_desiredShape=1, prep_3Dfabrication = 1, convert_to_dxf=1, print_mag_profile=1, draw_robots=1, render_robots=1,render_final=1, render_holder = 1):
    
    processed_path_to_save=path_to_save

    # get the morph and M profile data for each individual
    pickled_inds = glob(path_to_files + "/*")
    ordered_pickled_inds = natural_sort(pickled_inds, reverse=False)


    for ind_file in ordered_pickled_inds:
        
        design_param_file=ind_file+"/"+ind_file[-10:]+".pickle"
        init_shape_file=ind_file+"/initShapeTOP2.png"
        path_to_save=ind_file
        path_to_run_setting = ind_file + "/" + "run_settings.pickle"
        
        
        if render_final:
            render_final_shape(path_to_run_setting, design_param_file, path_to_save=path_to_save, draw_holder = render_holder)

        # render the desired shape
        if render_desiredShape:
            sub.call("mkdir " + path_to_save + "/desired_shape" + " 2>/dev/null", shell=True)

            render_desired_shape(path_to_run_setting, path_to_save=(path_to_save + "/desired_shape"), draw_as_spheres=0, draw_as_voxels=0, draw_as_curve=1, draw_holder=render_holder)


        # get it ready for fabrication and programming
        if convert_to_dxf:
            if os.path.isfile(init_shape_file):
                morphology_to_DXF(design_param_file, init_shape_file=init_shape_file, path_to_save=path_to_save, voxel_map_file=None)

            else: # init shape does not exist get the voxel map and build from there
                morphology_to_DXF(init_shape_file=None, path_to_save=path_to_save, voxel_map_file=design_param_file)
                raise NotImplementedError
        if print_mag_profile:
            magnetic_profile_to_txt(design_param_file=design_param_file, path_to_save=path_to_save)
        
        if prep_3Dfabrication:
            generate_fabrication_map(design_param_file, path_to_run_setting, path_to_save=path_to_save)

        if draw_robots:
            draw_schematic_morphology_and_mag_profile(design_param_file=design_param_file, path_to_save=path_to_save)
        if render_robots:
            draw_schematic_morphology_and_mag_profilev2(design_param_file=design_param_file, path_to_save=path_to_save, arrow_color_str="yellow")

        if processed_path_to_save is not None:
            sub.call("cp -r " + ind_file+ " " + processed_path_to_save+"/"+ind_file[-15:], shell=True)

    print("Inds are processed!")

def morphology_to_DXF(design_param_file, init_shape_file=None, path_to_save=None, voxel_map_file=None):
    """ Converts morpholgoy of the robot to a dxf file for the laser cutter """
    contour_file=path_to_save+"/contours.jpg"
    dxf_file=path_to_save+"/morphology_dxf2018.dxf"
    dxf_jpg_file=path_to_save+"/morphology_dxf2018.jpg"
    layer_name='MyLines'


    # convert Mtheta and Mphi for magnetic profile
    with open(design_param_file, 'rb') as f:
        out = pickle.load(f)

    robot = out['individual']
    material=robot.designParameters["material"]
    robot_size = material.shape

    if init_shape_file is not None:
        im = cv2.imread (init_shape_file)

        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)

        # Outline extraction
        contours, hierarchy = cv2.findContours (thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [np.squeeze (cnt, axis = 1) for cnt in contours]

        size = im.shape
        h = size [0]
        w = size [1]

        
        imgnew = np.zeros ((h, w, 3), np.uint8)
        for i in range(len(contours)-1):
            cnt = contours[i+1]
            img2 = cv2.drawContours(imgnew, [cnt], 0, (0,215,255), 3)
        # img2 = cv2.drawContours (imgnew, contours, -1, 	(0,215,255), 3)

        # print ("contours =", len (contours),"hierarchy =", len (hierarchy))
        # print (contours [1])
        
        cv2.imwrite (contour_file, img2)

        imgray=cv2.flip(imgray, 0)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        # Outline extraction
        contours, hierarchy = cv2.findContours (thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [np.squeeze (cnt, axis = 1) for cnt in contours]

        dwg = ezdxf.new ('R2010') # create a new DXF R2010 drawing, official DXF version name: 'AC1024'
        msp = dwg.modelspace () # add new entities to the model space
        dwg.layers.new (name = 'MyLines', dxfattribs = {'color': 3}) # 3 = Green
        dwg.header['$INSUNITS'] = units.MM  # units set to mm
      
            
        if h==w:
            if robot_size[0] ==30 and robot_size[1] ==30:
                contour_scale = 0.03428579265
            if robot_size[0] ==50 and robot_size[1] ==50:
                contour_scale = 0.055555555555555
        else:
            if robot_size[2] == 45 and robot_size[1] == 5:
                contour_scale = 0.015
            elif robot_size[0] == 18 and robot_size[1] == 7:
                contour_scale = 0.01147540983
            elif robot_size[0] == 30 and robot_size[1] == 5:
                contour_scale = 0.0103
            elif robot_size[0] == 9 and robot_size[1] == 7:
                contour_scale = 0.01146496815
            else:
                contour_scale = 0.02

        for i in range(len(contours)-1):
            ctr=contours[i+1]*contour_scale  # scale the contours, 1 pixel is 0.02mm
            for i in range (len (ctr)):
                n = i + 1
                if n>= len (ctr):
                    n = 0
                msp.add_line (ctr [i], ctr [n], dxfattribs = {'layer': layer_name}) # add a LINE entity
                print (ctr [i], '->', ctr [n])
        dwg.saveas (dxf_file)

        # Exception handling left out for compactness:
        matplotlib.qsave(msp, dxf_jpg_file)

    else:
        raise NotImplementedError

def magnetic_profile_to_txt(design_param_file=None, path_to_save=None):
    """ Converts morphology of the robot to a dxf file for the laser cutter """
    # convert Mtheta and Mphi for magnetic profile
    with open(design_param_file, 'rb') as f:
        out = pickle.load(f)

    robot = out['individual']
    Mtheta=robot.segmentedMprofile["Mtheta"]
    Mphi=robot.segmentedMprofile["Mphi"]


    # draw the 3D shape in high-quality
    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/finalShape3D_drawn"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)
    
    filePath2save=folderPath2save+"/finalShape3D_"
    positions=robot.voxel_dict["position"]
    voxelStrainEnergy=robot.voxel_dict["strainEnergy"]
    args=None
    draw3Dshapev2(positions, voxelStrainEnergy, filePath2save, highQuality = 1)
    filePath2save=path_to_save+"/initshapeRGB_highQ"
    drawInitShapeRGB(args, robot.designParameters, filePath2save, highQuality = 1)
    
    # write it all on to a txt file
    txt_file=path_to_save+"/magnetic_profile.txt"
        
    fileTXT = open(txt_file, "w")
    # write the first line with the info column
    # write it into .txt file
    fileTXT.write("[Mtheta"+",")
    fileTXT.write("Mphi;]\n")
    fileTXT.write("[ ")

    if Mtheta.shape[0]>Mtheta.shape[2]:

        for j in range(Mtheta.shape[1]):  
            for i in range(Mtheta.shape[0]):        
                fileTXT.write(str(Mtheta[i,j,0]/math.pi*180)+" ,"+str(Mphi[i,j,0]/math.pi*180))
                if (i == Mtheta.shape[0]-1) and (j == Mtheta.shape[1]-1):
                    pass
                else:
                    fileTXT.write(" ;\n")
    elif Mtheta.shape[2]>Mtheta.shape[0]:
        for j in range(Mtheta.shape[1]):  
            for i in range(Mtheta.shape[2]):        
                fileTXT.write(str(Mtheta[0,j,i]/math.pi*180)+" ,"+str(Mphi[0,j,i]/math.pi*180))
                if (i == Mtheta.shape[2]-1) and (j == Mtheta.shape[1]-1):
                    pass
                else:
                    fileTXT.write(" ;\n")
    else:
        raise NotImplementedError
    
    fileTXT.write(" ]")
    fileTXT.close()


def get_list_of_required_voxels(material_names, mat_map, magnetic_map, mag_mat_nums, mag_direction_map):
    
    # count the material occurances
    mat_counts = np.zeros((len(material_names)+1))
    for _mat_num in range(len(material_names)+1):
        mat_counts[_mat_num] = np.count_nonzero(mat_map == _mat_num)

    is3D = True if mat_map.ndim == 3 else False
    if not is3D:
        mat_map = np.reshape(mat_map, (mat_map.shape[0], mat_map.shape[1], 1))
        magnetic_map = np.reshape(magnetic_map, (magnetic_map.shape[0], magnetic_map.shape[1], 1))

    # count the material occurances
    mag_detail_counts = {}
    for _mag_num in mag_mat_nums:
        mag_detail_counts[material_names[_mag_num-1]] = {}
        for _direction in mag_direction_map:
            mag_detail_counts[material_names[_mag_num-1]][mag_direction_map[_direction]] = 0
    
    map_size = magnetic_map.shape

    # this step could be optimized with np -- only matrix manipulations --but don't care
    for _k in range(map_size[2]):
        for _j in range(map_size[1]):
            for _i in range(map_size[0]):
                mat_type = mat_map[_i,_j,_k]
                if mat_type in mag_mat_nums: # it is magnetic
                    _direction = magnetic_map[_i,_j,_k]
                    mag_detail_counts[material_names[mat_type-1]][mag_direction_map[_direction]] += 1

    return mat_counts, mag_detail_counts

def extract_voxel_types_to_txt(material_names, material_map, magnetic_map, mag_mat_nums, mag_direction_map, txt_save_path):
    
    # write it all on to a txt file
    fileTXT = open(txt_save_path, "w")
    # write the first line with the info column
    # write it into .txt file
    fileTXT.write("Required voxels for the overall fabrication: \n\n\n")

    mat_counts, mag_detail_counts = get_list_of_required_voxels(material_names, material_map, magnetic_map, mag_mat_nums, mag_direction_map)

    def write_voxel_numbers(fileTXT, material_names, mat_counts, mag_detail_counts):
        for _mat_num in range(len(material_names)+1):
            if _mat_num ==0:
                mat_name = "Empty"
            else: 
                mat_name = material_names[_mat_num-1]
            fileTXT.write("\t"+ mat_name +" voxels: " + str(mat_counts[_mat_num]) + "\n")
        
        fileTXT.write("\n\tRequired magnetic materials\n")
        for _mag_mat_name in mag_detail_counts:
            fileTXT.write("\n\t\t"+ _mag_mat_name +" voxels: ")
            for _mag_direction in mag_detail_counts[_mag_mat_name]:
                fileTXT.write(_mag_direction + ":\t"+str(mag_detail_counts[_mag_mat_name][_mag_direction])+ "\t")



    
    write_voxel_numbers(fileTXT, material_names, mat_counts, mag_detail_counts)
    fileTXT.write("\n\t\tTotal number of voxels to fabricate: " + str(np.sum(mat_counts[1:])))

    fileTXT.write("\n\n\n")
    fileTXT.write("Required voxels for each layers: \n\n")

    for layer_num in range(material_map.shape[2]):
        layer_mat_map = material_map[:,:,layer_num]
        layer_magnetic_map= magnetic_map[:,:,layer_num]
        mat_counts, mag_detail_counts = get_list_of_required_voxels(material_names, layer_mat_map, layer_magnetic_map, mag_mat_nums, mag_direction_map)

        fileTXT.write("\n\n\n\tLayer " + str(layer_num)+ "\n\n")

        write_voxel_numbers(fileTXT, material_names, mat_counts, mag_detail_counts)
    
    fileTXT.write("\n\n\t\t *****END***** \n\n")
    fileTXT.close()

def draw_layer(material_names, mat_map, magnetic_map, mag_mat_nums, layer_num, padding, scale_factor, mat_color_map, mag_direction_map, save_path):
    # Create a white canvas
    map_size = mat_map.shape
    padding_scaled = padding*scale_factor

    fig, ax = plt.subplots()
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_xlim(0, map_size[0]*scale_factor+2*padding_scaled)  # Adjust the x-axis limits according to your desired size
    ax.set_ylim(0, map_size[1]*scale_factor+2*padding_scaled)  # Adjust the y-axis limits according to your desired size
    plt.axis('off')  # Turn off the axis

    # Set the default font size
    plt.rcParams['font.size'] = 12

    text_x = map_size[0]*scale_factor/2
    text_y = padding_scaled/2
    ax.text(text_x, text_y, "Layer: " +str(layer_num), ha='left', va='center', fontsize=16, color='black') 


    for _j in range(map_size[1]):
        for _i in range(map_size[0]):

            square_size = scale_factor  # Adjust the size of the square based on the scaling factor
            color = mat_color_map[mat_map[_i, _j]]  # Map the number to a color using the colormap

            x = padding_scaled + _i*square_size
            y = padding_scaled + _j*square_size
            
            edge_color = (0.5, 0, 0.25)
            rectangle = plt.Rectangle((x, y), square_size, square_size, fc=color, ec=edge_color)  # Use the color for the face of the square
            ax.add_patch(rectangle)
            
            if mat_map[_i, _j] in mag_mat_nums:
                # Add text in the middle of the square
                text_x = x + square_size / 2
                text_y = y + square_size / 2
                direction = mag_direction_map[magnetic_map[_i, _j]]
                
                ax.text(text_x, text_y, direction, ha='center', va='center', fontsize=7, color='white')  # Display the number as text

    
    plt.savefig(save_path, bbox_inches='tight', dpi=1200)  # Save the plot to an image file

def get_simplified_magnetic_directions(mag_Mtheta, mag_Mphi):

    map_size = mag_Mtheta.shape
    magnetic_map = np.zeros((map_size[0], map_size[1], map_size[2]))

    # M = np.array([math.cos(Mtheta) * math.sin(Mphi), math.sin(Mtheta) * math.sin(Mphi), math.cos(Mphi)])
    # direction_map = {
    #     1: "North",   # positive y-direction
    #     2: "East",   # positive x-direction
    #     3: "South",   #  negative y-direction
    #     4: "West",   # negative x-direction
    #     5: "Up",    # positive z-direction
    #     6: "Down"    # negative z-direction
    # }
    for _k in range(map_size[2]):
        for _j in range(map_size[1]):
            for _i in range(map_size[0]):
                theta = mag_Mtheta[_i,_j,_k]
                phi = mag_Mphi[_i,_j,_k]

                M = np.array([math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi), math.cos(phi)])

                if phi ==0:
                    magnetic_map[_i,_j,_k] = 5
                elif phi == math.pi:
                    magnetic_map[_i,_j,_k] = 6
                elif phi == math.pi/2:
                    if theta ==0:
                        magnetic_map[_i,_j,_k] = 2
                    elif theta ==math.pi/2:
                        magnetic_map[_i,_j,_k] = 1
                    elif theta ==math.pi:
                        magnetic_map[_i,_j,_k] = 4
                    elif theta == -math.pi:
                        magnetic_map[_i,_j,_k] = 4
                    elif theta ==-math.pi/2:
                        magnetic_map[_i,_j,_k] = 3
                    else:
                        raise NotImplementedError
                else:
                    raise NotImplementedError
    return magnetic_map

def layer_fabrication_jig_DXF(mat_map, voxel_size, save_path):
    """ Converts morpholgoy of the robot to a dxf file for the laser cutter """
    # dwg = ezdxf.new ('R2010') # create a new DXF R2010 drawing, official DXF version name: 'AC1024'
    # dwg.layers.new (name = 'MyLines', dxfattribs = {'color': 3}) # 3 = Green
    # dwg.header['$INSUNITS'] = units.MM  # units set to mm


    def find_square_corners(matrix):
        rows = len(matrix)
        if rows == 0:
            return []

        cols = len(matrix[0])
        corners = []

        for i in range(rows):
            for j in range(cols):
                if matrix[i][j] != 0:
                    top_left = (i, j+1)
                    top_right = (i+1, j+1)
                    bottom_right = (i + 1, j)
                    bottom_left = (i, j)
                    pts = (top_left, top_right, bottom_left, bottom_right)
                    for pt in pts:
                        corners.append(pt)

        return corners
    
    def create_jigs_dxf(convex_hull_points, size, padding, voxel_size, output_file, shift_x = [0],shift_y = [0]):

        doc = ezdxf.new("R2010")  # Create a new DXF document
        doc.header['$INSUNITS'] = units.MM  # units set to mm
        msp = doc.modelspace()  # Get the modelspace layout
        
        for _idx, convex_hull_point in enumerate(convex_hull_points):
            # Add polyline entity for the convex hull points
            polyline = msp.add_polyline2d(convex_hull_point)

            # add the surronding part
            corners = []
            x_max = 2*padding + size[0]*voxel_size + shift_x[_idx]
            y_max = 2*padding + size[1]*voxel_size + shift_y[_idx]
            x_min = 0 + shift_x[_idx]
            y_min = 0 + shift_y[_idx]
            top_left = (x_min, y_max)
            top_right = (x_max, y_max)
            bottom_right = (x_max, y_min)
            bottom_left = (x_min, y_min)
            pts = (top_left, top_right, bottom_left, bottom_right)
            for pt in pts:
                corners.append(pt)
            corners.append(corners[0])

            # Create a ConvexHull object with the points
            hull = ConvexHull(corners)

            # Access the vertices of the convex hull
            convex_hull_point = hull.points[hull.vertices]
            convex_hull_point = np.vstack((convex_hull_point, convex_hull_point[0]))

            corners_outside = msp.add_polyline2d(convex_hull_point)
            

            # add holes to fix jigs
            hole_centers = []
            hole_shift = 5
            top_left = (x_min + hole_shift, y_max-hole_shift)
            top_right = (x_max-hole_shift, y_max-hole_shift)
            bottom_right = (x_max-hole_shift, y_min + hole_shift)
            bottom_left = (x_min + hole_shift, y_min + hole_shift)
            pts = (top_left, top_right, bottom_left, bottom_right)
            for pt in pts:
                hole_centers.append(pt)

            hole_radius = 3
            for center in hole_centers:
                circle = msp.add_circle(center=center, radius=hole_radius)
                circle.dxf.layer = "Holes"  # Specify the layer name for the circles


            # Set polyline properties
            polyline.dxf.layer = "Jig"  # Specify the layer name for the polyline
            corners_outside.dxf.layer = "Jig"

        # Save the DXF document to a file
        doc.saveas(output_file)
        return msp
    
    # single layers
    scaled_pts_all = []
    for layer_num in range(mat_map.shape[2]):
        layer_mat_map = mat_map[:,:,layer_num]

        layer_all_corners = find_square_corners(layer_mat_map)

        if np.sum(layer_all_corners) ==0:
            continue
        # Create a ConvexHull object with the points
        hull = ConvexHull(layer_all_corners)

        # Access the vertices of the convex hull
        convex_hull_points = hull.points[hull.vertices]
        convex_hull_points = np.vstack((convex_hull_points, convex_hull_points[0]))
        

        # turn into dxf file
        output_file = save_path+"/layer_" + str(layer_num) + "_jigs.dxf"
        padding = 10 # mm
        scaled_pts = convex_hull_points*voxel_size+padding

        scaled_pts_all.append(scaled_pts)
        msp = create_jigs_dxf([scaled_pts], layer_mat_map.shape, padding, voxel_size, output_file)


        dxf_jpg_file = save_path+"/layer_" + str(layer_num) + "_jigs.png"
        matplotlib.qsave(msp, dxf_jpg_file)

    # draw all layers into one single dxf file
    def find_numbers_with_smallest_difference(num):
        if num % 2==1:
            num +=1
        sqrt_num = math.isqrt(num)  # Get the square root of the number
        
        factors = []  # List to store pairs of factors
        min_diff = float('inf')  # Initialize the minimum difference to infinity

        for i in range(sqrt_num, 0, -1):
            if num % i == 0:
                factor1 = i
                factor2 = num // i
                diff = abs(factor1 - factor2)

                if diff < min_diff:
                    factors = [factor1, factor2]
                    min_diff = diff

        return factors

    scaled_pts_arranged = []
    x_shifts = []
    y_shifts = []
    page_layout_size = find_numbers_with_smallest_difference(len(scaled_pts_all))
    for i, scaled_pts in enumerate(scaled_pts_all):

        row = i // page_layout_size[0]  # Calculate the row index
        col = i % (page_layout_size[1]-1)   # Calculate the column index

        x_shift = (3*padding + layer_mat_map.shape[0]*voxel_size)*col
        y_shift = (3*padding + layer_mat_map.shape[1]*voxel_size)*row

        x_shifts.append(x_shift)
        y_shifts.append(y_shift)

        for _pts_idx in range(len(scaled_pts)):
            scaled_pts[_pts_idx][0] = scaled_pts[_pts_idx][0] + x_shift
            scaled_pts[_pts_idx][1] = scaled_pts[_pts_idx][1] + y_shift

        scaled_pts_arranged.append(scaled_pts)


    output_file = save_path+"/layers_all_jigs.dxf"
    msp = create_jigs_dxf(scaled_pts_arranged, layer_mat_map.shape, padding, voxel_size, output_file, x_shifts, y_shifts)
    dxf_jpg_file = save_path+"/layers_all_jigs.png"
    matplotlib.qsave(msp, dxf_jpg_file)


def get_color_map(material_names):
    # mat_color_map = {
    #         0: "#FFFFFF",   # White
    #         1: "#000000",   # Black
    #         2: "#808080",    # Gray
    #         3: "#40E0D0",    # Turquoise
    #         4: "#FFD700"    # Golden yellow
    #         5: "#5F021F",    # Red
    #         6: "#228c22"    # Froest Green
    #     }

    mat_color_map = {0: "#FFFFFF"}
    mat_color_map[material_names.index("E30")+1] = "#FFD700"
    mat_color_map[material_names.index("N108E30")+1] = "#808080"
    mat_color_map[material_names.index("N157DS30")+1] = "#000000"
    mat_color_map[material_names.index("SS960")+1] = "#40E0D0"
    try:
        mat_color_map[material_names.index("smpMAG")+1] = "#5F021F"
        mat_color_map[material_names.index("smpPAS")+1] = "#228c22"
        return mat_color_map
    except:
        return mat_color_map


def get_magnetic_mat_nums(material_names):
    magnetic_nums = []
    magnetic_nums.append(material_names.index("N108E30")+1)
    magnetic_nums.append(material_names.index("N157DS30")+1)
    try:
        magnetic_nums.append(material_names.index("smpMAG")+1)
        return magnetic_nums
    except:
        return magnetic_nums


def generate_fabrication_map(design_param_path, path_to_run_setting, path_to_save=None):
    
    # convert Mtheta and Mphi for magnetic profile
    with open(design_param_path, 'rb') as f:
        out = pickle.load(f)

    with open(path_to_run_setting, 'rb') as f:
        args = pickle.load(f)

    robot = out['individual']
    material_map=robot.designParameters["material"]
    mag_Mtheta=robot.designParameters["Mtheta"]
    mag_Mphi=robot.designParameters["Mphi"]
    
    magnetic_map = get_simplified_magnetic_directions(mag_Mtheta, mag_Mphi)

    robot_size = material_map.shape

    # mat_color legend
    # mat_color_map = {
    #         0: "#FFFFFF",   # White
    #         1: "#000000",   # Black
    #         2: "#808080",    # Gray
    #         3: "#40E0D0",    # Turquoise
    #         4: "#FFD700"    # Golden yellow
    #     }

    mat_color_map = get_color_map(args.material_names)
    
    # magnetic direction legend
    mag_direction_map = {
            1: "North",   # positive y-direction
            2: "East",   # positive x-direction
            3: "South",   #  negative y-direction
            4: "West",   # negative x-direction
            5: "Up",    # positive z-direction
            6: "Down"    # negative z-direction
        }

    mag_mat_nums = get_magnetic_mat_nums(args.material_names)
    padding = 1
    scaling_factor = 8 # Example scaling factor

    layer_folder = path_to_save + "/fabrication_layers"
    sub.call("mkdir " + layer_folder + " 2>/dev/null", shell=True)

    # get the required number of voxels for each layers and total
    txt_save_path = layer_folder + "/voxel_numbers_and_types.txt"
    extract_voxel_types_to_txt(args.material_names, material_map, magnetic_map, mag_mat_nums, mag_direction_map, txt_save_path)

    if robot.id == 177380: #max force case, only for visual purposes
        for layer_num in range(robot_size[1]):
            # material_map.take(layer_num, axis=1)
            layer_mat_map = material_map.take(layer_num, axis=1)
            layer_magnetic_map= magnetic_map.take(layer_num, axis=1)
            save_path_image = layer_folder + "/layer_" + str(layer_num) + ".png"

            scaling_factor = 24*10

            draw_layer(args.material_names, layer_mat_map, layer_magnetic_map, mag_mat_nums, layer_num, padding, scaling_factor, mat_color_map, mag_direction_map, save_path_image)      

    else:

        # arrange the layers
        for layer_num in range(robot_size[2]):
            layer_mat_map = material_map[:,:,layer_num]
            layer_magnetic_map= magnetic_map[:,:,layer_num]
            save_path_image = layer_folder + "/layer_" + str(layer_num) + ".png"

            draw_layer(args.material_names, layer_mat_map, layer_magnetic_map, mag_mat_nums, layer_num, padding, scaling_factor, mat_color_map, mag_direction_map, save_path_image)
            

    # final arrange for print ready layers
    page_layout_size = (2,3)
    page_layout_size = (1,5)
    max_layer_per_page = page_layout_size[0]*page_layout_size[1]
    layer_counter = 0

    def create_layer_layout_image(page_layout_size, layer_images, output_file):
       
        # Create a blank canvas for the segmented image
        canvas_width = layer_images[0].width * page_layout_size[0]
        canvas_height = layer_images[0].height * page_layout_size[1]
        canvas = Image.new('RGB', (canvas_width, canvas_height), color='white')
        
        # Assemble the images into the segmented order
        for i, image in enumerate(layer_images):
            row = i // page_layout_size[0]  # Calculate the row index
            col = i % (page_layout_size[1]-1)   # Calculate the column index
            
            # Calculate the position to paste the current image
            paste_x = col * image.width
            paste_y = row * image.height
            
            # Paste the image onto the canvas
            canvas.paste(image, (paste_x, paste_y))
        
        # Save the segmented image
        canvas.save(output_file)

    for _page_num in range(math.ceil(robot_size[2]/max_layer_per_page)):
        layer_images = []
        while len(layer_images)<max_layer_per_page and layer_counter < robot_size[2]:
            layer_image_path = layer_folder + "/layer_" + str(layer_counter) + ".png"
            layer_images.append(Image.open(layer_image_path))
            layer_counter +=1

        output_file = layer_folder + "/layout_page_" + str(_page_num) + ".png"
        create_layer_layout_image(page_layout_size, layer_images, output_file)
    
    # create the layer jigs
    voxel_size = args.lattice_dim*1e3 # in mm
    dxf_save_path = layer_folder + "/dxf_layers"
    sub.call("mkdir " + dxf_save_path + " 2>/dev/null", shell=True)

    layer_fabrication_jig_DXF(material_map, voxel_size, dxf_save_path)


def run_simulation(args, robot, print2screen=False): # runs a single simulation with debugging option
    if not print2screen:
        sub.Popen("./voxelyze -f " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(robot.id).zfill(args.max_ind_1ex) + ".vxa" + " -B_ext " + str(args.quasi_static_B_magnitude) ,shell=True)
    else:
        sub.Popen("./voxelyze -p -f " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(robot.id).zfill(args.max_ind_1ex) + ".vxa" + " -B_ext " + str(args.quasi_static_B_magnitude) ,shell=True)
    
    print("Call sent to C++ sim")
    return 1

def get_simulation_result(args, robot, step_number): # waits for the simulation to write results, copy, return results
    """This functions waits for the next simulation file while simulation is runnning, 
        reads it and 
        returns the 
        voxelpositions, strain energy, current time of the simulation"""
    all_done = False
    redo_attempts = 1

    eval_start_time = time.time()
    if step_number:
        fileName =  args.run_directory + "/fitnessFiles/" + args.run_name + "--id_" + str(robot.id).zfill(args.max_ind_1ex) + "_"+ str(step_number) +".xml"
    else:
        fileName =  args.run_directory + "/fitnessFiles/" + args.run_name + "--id_" + str(robot.id).zfill(args.max_ind_1ex) + ".xml"
    

    while not all_done:

        time_waiting_for_eval = time.time() - eval_start_time

        # Abort if the maximum evaluation time has passed --> meaning the simulation diverged
        if time_waiting_for_eval> args.max_eval_time:
            print ("Simulation diverged for robot: ", robot.id)
            return None, None, None

        # check to see if simulation run is finished
        if os.path.isfile(fileName):
            ls_check = fileName
            ls_check = ls_check.split("/")[-1]
            if (args.run_name + "--id_") in ls_check:
                this_id = int(ls_check.split("_")[1].split(".")[0])

                if this_id == robot.id:

                    if step_number:
                        fitnessSaveFile = args.run_directory + "/fitnessFiles/" + args.run_name + "--id_" + str(robot.id).zfill(args.max_ind_1ex) + "_"+ str(step_number) +".xml"
                    else:
                        fitnessSaveFile = args.run_directory + "/fitnessFiles/" + args.run_name + "--id_" + str(robot.id).zfill(args.max_ind_1ex) + ".xml"
                    
                    try:
                        vox_dict = xml2npArray(fitnessSaveFile, args.ind_size, 0, args)
                        all_done = True
                    except:
                        all_done = False

            # wait a second and try again
            else:
                time.sleep(0.1)
        else:
            time.sleep(0.1)

    return vox_dict


def run_simulation_save_position(my_robot, run_args):

    isControllerSet = 0
    if run_args.controller_type != "quasi-static":
        run_args, my_controller = get_magnetic_control_field(run_args)
        run_args.video_sim_time = run_args.sim_time
        isControllerSet = 1
        
    # set up the sim & env
    my_sim = Sim(dt_frac=run_args.dt_frac, simulation_time=run_args.sim_time, fitness_eval_init_time=run_args.init_time, equilibrium_mode = run_args.equilibrium_mode)
    my_env = Env(floor_enabled=0, floor_slope=0.0, lattice_dimension = run_args.lattice_dim, sticky_floor=0, time_between_traces=0)


    # crate the folders required for the sim
    sub.call("rm -r " + run_args.run_directory + "/voxelyzeFiles 2> /dev/null", shell=True)
    sub.call("rm -r " + run_args.run_directory + "/tempFiles 2> /dev/null", shell=True)
    sub.call("rm -r " + run_args.run_directory + "/fitnessFiles 2> /dev/null", shell=True)
    
    sub.call("mkdir " + run_args.run_directory + "/voxelyzeFiles 2> /dev/null", shell=True)
    sub.call("mkdir " + run_args.run_directory + "/tempFiles 2> /dev/null", shell=True)
    sub.call("mkdir " + run_args.run_directory + "/fitnessFiles 2> /dev/null", shell=True)

        
    # write the voxelyze, M profile files
    my_robot.md5 = write_voxelyze_file(run_args, my_sim, my_env, my_robot, run_args.run_directory, run_args.run_name)
    write_magnetic_profile(run_args, my_robot, run_args.run_directory, run_args.run_name)

    if isControllerSet:
        write_magnetic_field(run_args, my_robot, run_args.run_directory, run_args.run_name, my_controller)
        
    # start the sim
    run_args.debug = False
    print2screen = True if run_args.debug else False # simulation print2screen for debugging purposes

    
    run_simulation(run_args, my_robot, print2screen = print2screen)  

    # detect the end of sim
    if run_args.record_video:
        total_step_num = int(run_args.video_bandwidth*run_args.video_sim_time)
        if (run_args.desired_shape == "max_COM_z" and run_args.controller_type == "quasi-static") or run_args.desired_shape == "max_COM_z_symmetry":
            total_step_num = total_step_num * 2
    else:
        total_step_num = 1

    vox_dict= get_simulation_result(run_args, my_robot, total_step_num-1)

    return vox_dict


# generate the video output for the desired robots
def get_robots_dynamic_video(args, path_to_robots, path_to_run_setting=None, path_to_save=None):


    # get the robot pickle path
    pickled_inds = glob(path_to_robots + "/*/id*.pickle")
    ordered_pickled_inds = natural_sort(pickled_inds, reverse=False)


    for robot_file in ordered_pickled_inds:
        # handle the paths
        path_to_robot = robot_file      
        path_to_run_setting = path_to_robot[:-17] + "run_settings.pickle"

        path_to_save =  path_to_robot[:-17] + "video"
        sub.call("mkdir " + path_to_save + "/" + " 2>/dev/null", shell=True)
        path_to_save = path_to_robot[:-17] + "video/"+ path_to_robot[-17:-7]
        

        # load robot & run settings
        my_robot = load_pickle_at(path_to_robot)['individual']
        run_args = load_pickle_at(path_to_run_setting)

        try:
            if run_args.isFixedFromBothEnd == 1:
                run_args.isFixedFromBothEnd = 1
        except: 
            run_args.isFixedFromBothEnd = 0

        run_args.run_directory = path_to_robot[:-18]

        run_args.voxel_color = args.voxel_color

        # video settings
        if not run_args.controller_type == "open-loop":

            run_args.record_video = args.record_video
            run_args.video_bandwidth = args.video_bandwidth
            run_args.video_speed_wrt_RT = args.video_speed_wrt_RT
            run_args.video_sim_time = args.video_sim_time
            run_args.video_quality = args.video_quality

                
            if args.record_video: 
                # run the simulation longer for a nicer video without a stop
                run_args.sim_time = run_args.video_sim_time
                run_args.KinEThreshold = 0
                run_args.save_orientation = 1

                if run_args.fitness_calc_type=='max_broad_jump' or run_args.desired_shape=='max_COM_z' :
                    run_args.isJumper = 1
        else:
            run_args.record_video = args.record_video
            run_args.video_bandwidth = args.video_bandwidth
            run_args.video_speed_wrt_RT = args.video_speed_wrt_RT
            run_args.video_sim_time = run_args.sim_time
            run_args.video_quality = args.video_quality

            if args.record_video: 
                # run the simulation longer for a nicer video without a stop
                # run_args.sim_time = run_args.video_sim_time
                run_args.KinEThreshold = 0
                run_args.save_orientation = 1


        # create a history file or not?
        
        run_args.create_history = args.create_history
        run_args.history_bandwidth = args.history_bandwidth
        if args.create_history:
            # run the simulation longer for a nicer video without a stop
            run_args.sim_time = args.history_sim_time
            run_args.KinEThreshold = 0
            run_args.save_orientation = 1

        if run_args.fitness_calc_type=="multi_func_walkNjump":
            run_args.desired_shape = "max_COM_x"
            
        run_simulation_save_position(my_robot, run_args)

        if args.record_video:
            if args.view_type[0] == "all":
                args.view_type = ["isometric", "sideXZ", "topXY", "frontYZ"]

            for view_perspective in args.view_type:
                get_robot_dynamic_video(my_robot, run_args, path_to_save=path_to_save, view_type=view_perspective)

        if run_args.fitness_calc_type=="multi_func_walkNjump":
            run_args.desired_shape = "max_COM_z"

            # crate the folders required for the sim
            sub.call("rm -r " + run_args.run_directory + "/voxelyzeFiles 2> /dev/null", shell=True)
            sub.call("rm -r " + run_args.run_directory + "/tempFiles 2> /dev/null", shell=True)
            sub.call("rm -r " + run_args.run_directory + "/fitnessFiles 2> /dev/null", shell=True)


            run_simulation_save_position(my_robot, run_args)
            

            if args.record_video:
                if args.view_type[0] == "all":
                    args.view_type = ["isometric", "sideXZ", "topXY", "frontYZ"]

                sub.call("rm -r " + run_args.run_directory + "/video/frames 2> /dev/null", shell=True)
                path_to_save = path_to_save + "_2_"
                for view_perspective in args.view_type:
                    get_robot_dynamic_video(my_robot, run_args, path_to_save=path_to_save, view_type=view_perspective)

        


def get_robot_dynamic_video(my_robot, run_args, path_to_save=None, view_type="isometric"):
    
    total_step_num = int(run_args.video_bandwidth*run_args.video_sim_time)
    if (run_args.desired_shape == "max_COM_z" and run_args.controller_type == "quasi-static")  or run_args.desired_shape == "PI" or run_args.desired_shape == "max_COM_z_symmetry":
        total_step_num = total_step_num * 2

    # make the video
    if run_args.video_quality == 0:
        video_dpi = 50
    elif run_args.video_quality > 0:
        video_dpi = 300*run_args.video_quality
    else:
        raise NotImplementedError
    
    sub.call("mkdir " + run_args.run_directory + "/video/frames 2> /dev/null", shell=True)
    frames = []
    for frame_num in range(total_step_num):
    
        # read the robot pos.
        vox_dict= get_simulation_result(run_args, my_robot, frame_num)
        voxelPositions=vox_dict["position"]
        voxelStrainEnergy=vox_dict["strainEnergy"]

        # create the frame
        filePath2save = run_args.run_directory + "/video/frames/" + "frame_" +str(frame_num)
        frame_path =  draw3Dshape_videoFrame(voxelPositions, voxelStrainEnergy, filePath2save, view_type=view_type, dpiValue = video_dpi)
        # frame = cv2.imread(frame_path)

        # add it to the video
        frames.append(frame_path)

    fps = run_args.video_bandwidth * run_args.video_speed_wrt_RT
    video_path = path_to_save+"_"+view_type+".mp4"

    # make the video
    sub.call("ffmpeg -r "+str(fps)+ " -i "+run_args.run_directory+"/video/frames/frame_%d_"+str(view_type)+".jpg -vcodec mpeg4 -pix_fmt yuv420p -s 1920x1920 -y "+video_path, shell=True)

    if run_args.fitness_calc_type=='max_broad_jump' or run_args.fitness_calc_type=='max_velZv8':
        video_path = path_to_save+"_"+view_type+"_25xslower.mp4"
        sub.call("ffmpeg -r "+str(fps/25)+ " -i "+run_args.run_directory+"/video/frames/frame_%d_"+str(view_type)+".jpg -vcodec mpeg4 -pix_fmt yuv420p -s 1920x1920 -y "+video_path, shell=True)

    isDone = True


def explode(data):
    size = np.array(data.shape)*2
    data_e = np.zeros(size - 1, dtype=data.dtype)
    data_e[::2, ::2, ::2] = data
    return data_e

class Arrow3D(FancyArrowPatch):

    def __init__(self, x, y, z, dx, dy, dz, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._xyz = (x, y, z)
        self._dxdydz = (dx, dy, dz)

    def draw(self, renderer):
        x1, y1, z1 = self._xyz
        dx, dy, dz = self._dxdydz
        x2, y2, z2 = (x1 + dx, y1 + dy, z1 + dz)

        xs, ys, zs = proj_transform((x1, x2), (y1, y2), (z1, z2), self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

def _arrow3D(ax, x, y, z, dx, dy, dz, *args, **kwargs):
    '''Add an 3d arrow to an `Axes3D` instance.'''

    arrow = Arrow3D(x, y, z, dx, dy, dz, *args, **kwargs)
    ax.add_artist(arrow)

def draw_schematic_morphology_and_mag_profile(design_param_file=None, path_to_save=None):
    highQuality=1
    # convert Mtheta and Mphi for magnetic profile
    with open(design_param_file, 'rb') as f:
        out = pickle.load(f)

    robot = out['individual']
    Mtheta=robot.segmentedMprofile["Mtheta"]
    Mphi=robot.segmentedMprofile["Mphi"]
    voxel_map=robot.designParameters['material']

    segments=Mtheta.shape
    ind_size=voxel_map.shape

    draw_arrows=1
    draw_voxels=1


    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/finalDesign_drawed"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)

    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111, projection='3d')
    ax.axis('off')
    ax.view_init(elev=0., azim=270)

    # draw the arrows
    if draw_arrows:
        segment_size=np.divide(ind_size,segments)
        arrow_length=3
        max_size =max(ind_size)
        ax.set_xlim3d(0, max_size)
        ax.set_ylim3d(0, max_size)
        ax.set_zlim3d(-max_size, max_size)

        for i in range(segments[0]):
            for j in range(segments[1]):
                for k in range(segments[2]):
                    theta=Mtheta[i,j,k]
                    phi=Mphi[i,j,k]

                    xMid=segment_size[0]/2.+segment_size[0]*(i)
                    yMid=segment_size[1]/2.+segment_size[1]*(j)
                    zMid=segment_size[2]/2.+segment_size[2]*(k)

                    dx=arrow_length/2*math.sin(phi)*math.cos(theta)
                    dy=arrow_length/2*math.sin(phi)*math.sin(theta)
                    dz=arrow_length/2*math.cos(phi)

                    print(theta*180/math.pi)
                    print(phi*180/math.pi)

                    print([xMid, yMid, zMid, dx, dy, dz])

                    print("length: ", math.sqrt((2*dx)**2+(2*dy)**2+(2*dz)**2))

                    print([xMid-dx,yMid-dy,zMid-dz,dx*2,dy*2,dz*2])


                    _arrow3D(ax, xMid-dx,yMid-dy,zMid-dz,
                            dx*2,dy*2,dz*2,
                            mutation_scale=10,
                            ec ='yellow',
                            fc='yellow',
                            linewidth=5)


    # draw the rectangles of the voxels
    if draw_voxels:
        n_voxels = np.zeros(ind_size, dtype=bool)
        n_voxels= voxel_map>0

        facecolors = np.where(n_voxels, '#444548', '#FFFFFF00')
        edgecolors = np.where(n_voxels, '#191919', '#FFFFFF00')
        filled = np.ones(n_voxels.shape)

        # upscale the above voxel image, leaving gaps
        filled_2 = explode(filled)
        fcolors_2 = explode(facecolors)
        ecolors_2 = explode(edgecolors)


        # Shrink the gaps
        x, y, z = np.indices(np.array(filled_2.shape) + 1).astype(float) // 2
        x[0::2, :, :] += 0.02
        y[:, 0::2, :] += 0.02
        z[:, :, 0::2] += 0.02
        x[1::2, :, :] += 0.98
        y[:, 1::2, :] += 0.98
        z[:, :, 1::2] += 0.98


        max_size =max(ind_size)
        ax.set_xlim3d(0, max_size)
        ax.set_ylim3d(0, max_size)
        ax.set_zlim3d(-max_size, max_size)
        ax.voxels(x, y, z, filled_2, facecolors=fcolors_2, edgecolors=ecolors_2, linewidth=0.2)
        fig.tight_layout()
    

    # save
    filePath2save=folderPath2save+"/design_"
    dpiValue = 50
    if highQuality:
        dpiValue = 300

    if (filePath2save[-4]) =='.':
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save, dpi=dpiValue)
    else:
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save+"isometric.jpg", dpi=dpiValue, bbox_inches='tight')
        ax.view_init(elev=40., azim=300)
        plt.savefig(filePath2save+"isometric3.jpg", dpi=dpiValue, bbox_inches='tight')
        ax.view_init(elev=60., azim=300)
        plt.savefig(filePath2save+"isometric2.jpg", dpi=dpiValue, bbox_inches='tight')
        ax.view_init(elev=0., azim=270)
        plt.savefig(filePath2save+"sideXZ.jpg", dpi=dpiValue, bbox_inches='tight')
        ax.view_init(elev=0., azim=90)
        plt.savefig(filePath2save+"side2XZ.jpg", dpi=dpiValue, bbox_inches='tight')
        ax.view_init(elev=90., azim=180)
        plt.savefig(filePath2save+"topXY.jpg", dpi=dpiValue, bbox_inches='tight')
        ax.view_init(elev=0., azim=180)
        plt.savefig(filePath2save+"topYZ.jpg", dpi=dpiValue, bbox_inches='tight')



def render_design(design_param_file, path_to_save=None, render_perspectives= ["isometric"], render_M_arrow=1, arrow_color_str="yellow",render_morphology=1, highQuality=1):
    
    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/rendered_design"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)

    # get the dowload dir for rendering via vpython
    downloadDir = sub.check_output(["xdg-user-dir", "DOWNLOAD"])
    downloadDir = downloadDir.decode("utf-8")
    downloadDir = downloadDir[:-1]


    # convert Mtheta and Mphi for magnetic profile
    with open(design_param_file, 'rb') as f:
        out = pickle.load(f)

    robot = out['individual']

    try:
        Mtheta=robot.segmentedMprofile["Mtheta"]
        Mphi=robot.segmentedMprofile["Mphi"]
    except:
        Mtheta=robot.designParameters["Mtheta"][:,0]
        Mphi=robot.designParameters["Mphi"][:,0]
    voxel_map=robot.designParameters['material']

    segments=Mtheta.shape
    ind_size=voxel_map.shape

    scene_width = ind_size[0] * 100
    scene_height = ind_size[1] * 100

    scene_width = 3840*3/2
    scene_height = 3840*3/2

    scene_width = 3840/2
    scene_height = 3840/2

    scene=canvas(center=vector(ind_size[0]/2,0,0), background=color.white,  width=scene_width, height=scene_height)

    scene.range = ind_size[0]/2+5
    scene.center= vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(0, -1, -1)
    scene.autoscale = True

    # scene.lights = []
    scene.ambient=color.gray(0.5)

    draw_arrows=render_M_arrow
    draw_voxels=1

    voxel_color = vector(68, 69, 72)/255
    voxel_size = vector(1, 1, 1)*1
    voxel_opacity = 0.8

    if arrow_color_str=="red":
        arrow_color = vector(166,25,46)/255      # red
    elif arrow_color_str=="yellow":
        arrow_color = vector(252,181,20)/255      # penguins yellow


    arrow_length = 2
    arrow_shaftwidth = arrow_length*0.1   # default
    arrow_headwidth = 3*arrow_shaftwidth
    arrow_headlength = arrow_length*0.3

    arrow_shift_inZ = arrow_length/3+2

    # render morphology only top view
    # draw the rectangles of the voxels
    if draw_voxels:
        # get the filled voxels
        n_voxels = np.zeros(ind_size, dtype=bool)
        n_voxels= voxel_map>0

        # get the augmented positions of the voxels
        nx, ny = (ind_size[0], ind_size[1])
        x = np.linspace(0, 1*(nx-1), nx)
        y = np.linspace(0, 1*(ny-1), ny)

        # adjust the coord frame of vpython to voxelyze
        z= -y

        # draw the boxes
        for j in range (ny):
            for i in range (nx):
                # draw only if filled
                if n_voxels[i,j]:
                    box(pos = vector(x[i], 0, z[j]), 
                        size = voxel_size,
                        color = voxel_color,
                        opacity=voxel_opacity)
    

    if render_morphology:
        render_completed = 0
        while not render_completed:
            fileName = "designScene_top_onlyMorph"
            copy_from = downloadDir+"/"+fileName+".png"
            filePath2save=folderPath2save+"/" + fileName+".png"

            if os.path.isfile(copy_from):
                sub.call("rm " + copy_from, shell=True)
                time.sleep(0.2)

            scene.range = scene.range + 10
            scene.center=vector(ind_size[0]/2,0,0)
            scene.forward = vector(0, -1, 0)
            scene.autoscale = True
            scene.capture(fileName)
            time.sleep(1)

            # save
            for i in range(60):
                if not os.path.isfile(copy_from):
                    time.sleep(1)
                else:
                    if os.path.getsize(copy_from) > 0:
                        render_completed = 1

        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)


    # draw the arrows for magnetic profile
    if draw_arrows:

        segment_size=np.divide(ind_size[0:2], segments[0:2])

        # get the augmented positions of the segments
        nx_arrow, ny_arrow = (segments[0], segments[1])
        x_arrow = np.linspace(0, 1*(nx-segment_size[0]), nx_arrow)+segment_size[0]/2-0.5
        y_arrow = np.linspace(0, 1*(ny-segment_size[1]), ny_arrow)+segment_size[1]/2-0.5

        # adjust the coord frame of vpython to voxelyze
        z_arrow = -y_arrow

        # draw the arrow
        for j in range (ny_arrow):
            for i in range (nx_arrow):
                
                if  (i % 2 ==1):
                    continue
                try:
                    theta=Mtheta[i,j,0]
                    phi=Mphi[i,j,0]

                except:
                    theta=Mtheta[i,j]
                    phi=Mphi[i,j]

                dx=arrow_length/2*math.sin(phi)*math.cos(theta)
                dy=arrow_length/2*math.sin(phi)*math.sin(theta)
                dz=arrow_length/2*math.cos(phi)
                
                # adjust the coordinate system voxelyze to vpython
                dy = -dy

                AXIS=vector(dx,dz,dy)

                arrow(pos=vector(x_arrow[i]-dx, 0-dz+arrow_shift_inZ, z_arrow[j]-dy), axis=AXIS, color = arrow_color, round = True, length=arrow_length, shaftwidth=arrow_shaftwidth, headwidth=arrow_headwidth, headlength=arrow_headlength, shininess = 1.0, emissive = True)
    

    if "60degree" in render_perspectives:
        fileName = "designScene_60degree"
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
        scene.forward = vector(0, -1*sqrt(3), -1)
        scene.autoscale = True
        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)


    if "side" in render_perspectives:
        fileName = "designScene_side_"+ arrow_color_str
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
        scene.forward = vector(0, 0, -1)
        scene.autoscale = True
        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)


    if "iso" in render_perspectives:
        fileName = "designScene_iso"+ arrow_color_str
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
        scene.forward = vector(-1, -1/sqrt(3), -1)
        scene.autoscale = True
        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)


    if "isometric" in render_perspectives:
        # expISO

        render_completed = 0
        while not render_completed:

            fileName = "designScene_isoEXP"+ arrow_color_str
            copy_from = downloadDir+"/"+fileName+".png"
            filePath2save=folderPath2save+"/" + fileName+".png"

            if os.path.isfile(copy_from):
                sub.call("rm " + copy_from, shell=True)
                time.sleep(0.2)


            scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
            scene.forward = vector(-1, -1/sqrt(3), -1)
            scene.range = ind_size[0]/2 + 5

            # new iso settings
            scene.fov = 26*pi/180
            scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
            scene.camera.axis = vector(-sqrt(3),-1,-sqrt(3))
            scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
            scene.range = ind_size[0]/2+15
            # scene.camera.axis = vector(0,-1,0)
            # rot_angles= vector(-30,45,0)*pi/180
            # scene.camera.rotate(angle=rot_angles)

            scene.autoscale = True
            scene.userzoom = False
            scene.userspin = False
            scene.range = ind_size[0]/2+0

            scene.capture(fileName)
            time.sleep(1)

            # save
            for i in range(60):
                if not os.path.isfile(copy_from):
                    time.sleep(1)
                else:
                    if os.path.getsize(copy_from) > 0:
                        render_completed = 1

        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)

    if "iso2" in render_perspectives:
        #iso2
        fileName = "designScene_iso2"+ arrow_color_str
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
        scene.forward = vector(-1, -1, -1)
        scene.range = ind_size[0]/2 +15

        # new iso settings
        scene.fov = 26*pi/180
        scene.camera.pos = vector(35,35,35)*2.5
        scene.camera.axis = vector(-1,-1,-1)
        scene.camera.pos = vector(35,35,35)*2.5
        scene.range = ind_size[0]/2 +15
        # scene.camera.axis = vector(0,-1,0)
        # rot_angles= vector(-30,45,0)*pi/180
        # scene.camera.rotate(angle=rot_angles)

        scene.autoscale = True
        scene.userzoom = False
        scene.userspin = False
        scene.range = ind_size[0]/2 +15

        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)

    scene.delete()
    pass

def draw_schematic_morphology_and_mag_profilev2(design_param_file=None, path_to_save=None, arrow_color_str="red"):
    
    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/finalDesign_rendered"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)

    downloadDir = sub.check_output(["xdg-user-dir", "DOWNLOAD"])
    downloadDir = downloadDir.decode("utf-8")
    downloadDir = downloadDir[:-1]


    highQuality=1
    # convert Mtheta and Mphi for magnetic profile
    with open(design_param_file, 'rb') as f:
        out = pickle.load(f)

    robot = out['individual']
    Mtheta=robot.segmentedMprofile["Mtheta"]
    Mphi=robot.segmentedMprofile["Mphi"]
    voxel_map=robot.designParameters['material']

    segments=Mtheta.shape
    ind_size=voxel_map.shape

    scene_width = ind_size[0] * 100
    scene_height = ind_size[1] * 100

    scene_width = 3840*3/2
    scene_height = 3840*3/2

    scene=canvas(center=vector(ind_size[0]/2,0,0), background=color.white,  width=scene_width, height=scene_height)

    scene.range = ind_size[0]/2+10
    scene.center= vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(0, -1, -1)
    scene.autoscale = True

    # scene.lights = []
    scene.ambient=color.gray(0.5)

    draw_arrows=1
    draw_voxels=1

    voxel_color = vector(68, 69, 72)/255
    voxel_size = vector(1, 1, 1)*1
    voxel_opacity = 0.8

    arrow_color = vector(255, 223, 0)/255
    arrow_color = vector(255, 182, 18)/255    # steelers yellow

    arrow_color = vector(252,181,20)/255      # penguins yellow

    arrow_color = vector(166,25,46)/255      # red
    
    if arrow_color_str=="red":
        arrow_color = vector(166,25,46)/255      # red
    elif arrow_color_str=="yellow":
        arrow_color = vector(252,181,20)/255      # penguins yellow


    arrow_length = 2.5
    arrow_shaftwidth = arrow_length*0.1   # default
    arrow_headwidth = 3*arrow_shaftwidth
    arrow_headlength = arrow_length*0.3

    # arrow_shift_inZ = arrow_length/3+2
    arrow_shift_inZ = arrow_length/3


    # draw the rectangles of the voxels
    if draw_voxels:
        # get the filled voxels
        n_voxels = np.zeros(ind_size, dtype=bool)
        n_voxels= voxel_map>0

        # get the augmented positions of the voxels
        nx, ny = (ind_size[0], ind_size[1])
        x = np.linspace(0, 1*(nx-1), nx)
        y = np.linspace(0, 1*(ny-1), ny)

        # adjust the coord frame of vpython to voxelyze
        z= -y

        # draw the boxes
        for j in range (ny):
            for i in range (nx):
                # draw only if filled
                if n_voxels[i,j]:
                    box(pos = vector(x[i], 0, z[j]), 
                        size = voxel_size,
                        color = voxel_color,
                        opacity=voxel_opacity)
    

        
    fileName = "designScene_top_onlyMorph"
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.range = scene.range + 10
    scene.center=vector(ind_size[0]/2,0,0)
    scene.forward = vector(0, -1, 0)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)




    # draw the arrows
    if draw_arrows:

        segment_size=np.divide(ind_size, segments)

        # get the augmented positions of the segments
        nx_arrow, ny_arrow = (segments[0], segments[1])
        x_arrow = np.linspace(0, 1*(nx-segment_size[0]), nx_arrow)+segment_size[0]/2-0.5
        y_arrow = np.linspace(0, 1*(ny-segment_size[1]), ny_arrow)+segment_size[1]/2-0.5

        # adjust the coord frame of vpython to voxelyze
        z_arrow = -y_arrow

        # draw the arrow
        for j in range (ny_arrow):
            for i in range (nx_arrow):

                theta=Mtheta[i,j,0]
                phi=Mphi[i,j,0]

                dx=arrow_length/2*math.sin(phi)*math.cos(theta)
                dy=arrow_length/2*math.sin(phi)*math.sin(theta)
                dz=arrow_length/2*math.cos(phi)
                
                # adjust the coordinate system voxelyze to vpython
                dy = -dy

                AXIS=vector(dx,dz,dy)

                arrow(pos=vector(x_arrow[i]-dx, 0-dz+arrow_shift_inZ, z_arrow[j]-dy), axis=AXIS, color = arrow_color, round = True, length=arrow_length, shaftwidth=arrow_shaftwidth, headwidth=arrow_headwidth, headlength=arrow_headlength)
    
    fileName = "designScene_60degree"
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(0, -1*sqrt(3), -1)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)



    fileName = "designScene_side_"+ arrow_color_str
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(0, 0, -1)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)


    fileName = "designScene_iso"+ arrow_color_str
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(-1, -1/sqrt(3), -1)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)


    # expISO
    fileName = "designScene_isoEXP"+ arrow_color_str
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)


    scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(-1, -1/sqrt(3), -1)
    scene.range = ind_size[0]/2 +15

    # new iso settings
    scene.fov = 26*pi/180
    scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
    scene.camera.axis = vector(-sqrt(3),-1,-sqrt(3))
    scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
    scene.range = ind_size[0]/2+15

    scene.autoscale = True
    scene.userzoom = False
    scene.userspin = False
    scene.range = ind_size[0]/2+15

    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)



    #iso2
    fileName = "designScene_iso2"+ arrow_color_str
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center=vector(ind_size[0]/2,0,-ind_size[1]/2)
    scene.forward = vector(-1, -1, -1)
    scene.range = ind_size[0]/2 +15

    # new iso settings
    scene.fov = 26*pi/180
    scene.camera.pos = vector(35,35,35)*2.5
    scene.camera.axis = vector(-1,-1,-1)
    scene.camera.pos = vector(35,35,35)*2.5
    scene.range = ind_size[0]/2 +15

    scene.autoscale = True
    scene.userzoom = False
    scene.userspin = False
    scene.range = ind_size[0]/2 +15

    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)


def render_selected_frames(args, path_to_frame_folders = None):

    if path_to_frame_folders == None:
        path_to_frame_folders = "../data/frames2render"

    # get the frame folders
    frame_folders = glob(path_to_frame_folders + "/*")
    ordered_frame_folders = natural_sort(frame_folders, reverse=False)



    for frame_folder in ordered_frame_folders:

        # handle the paths
        path_to_robot = frame_folder

        path_to_run_setting = path_to_robot + "/run_settings.pickle"

        frames = glob(frame_folder + "/*.xml")
        if not frames:
            print("No frames detected in the following folder: ", frame_folder)
            print("\n...Moving to the next folder...\n")
            continue
        ordered_frames = natural_sort(frames, reverse=False)

        # load run settings
        run_args = load_pickle_at(path_to_run_setting)
        run_args.save_orientation = 1

        if run_args.desired_shape =="max_COM_z" or run_args.desired_shape =="max_COM_z_symmetry":
            draw_holder = 0
            draw_floor = 1
        else:
            draw_holder = 1
            draw_floor = 0
        
        strainUpperLimit = get_strainUpperLimit(run_args, ordered_frames)
        
        # write this value to a text file
        txt_file = frame_folder + "/strainMax.txt"
        fileTXT = open(txt_file, "w")
        fileTXT.write("Maximum strain value is: " + str(strainUpperLimit))
        fileTXT.write("\n")
        fileTXT.close()
        
        folder_to_save = frame_folder + "/" + "rendered_frames"
        sub.call("mkdir " + folder_to_save + " 2>/dev/null", shell=True)

        for i in range(len(ordered_frames)):
            frame = ordered_frames[i]
            frame_num = frame.split("_")[-1][:-4]

            # folder_to_save = frame_folder + "/" + str(frame_num)
            # sub.call("mkdir " + folder_to_save + " 2>/dev/null", shell=True)
            path_to_save = folder_to_save
        
            voxel_dict = xml2npArray(frame, run_args.ind_size, 0, run_args)

            render_from_VoxDict(voxel_dict, run_args, path_to_save, draw_holder=draw_holder, draw_floor=draw_floor, strainUpLim=strainUpperLimit, frame_number=frame_num)

    print("rendering selected frames is done")

def get_strainUpperLimit(run_args, ordered_frames):

    upperLimitMax = 0
    for i in range(len(ordered_frames)):
        frame = ordered_frames[i]
        voxel_dict = xml2npArray(frame, run_args.ind_size, 0, run_args)
        voxelStrainEnergy=voxel_dict["strainEnergy"]

        cMapVals = voxelStrainEnergy/np.nanmax(voxelStrainEnergy)
        upperLimit = np.nanmean(cMapVals)*3


        voxelCountLimit = 15
        voxelHigherUpperLim = (cMapVals>upperLimit).sum()
        while voxelHigherUpperLim > voxelCountLimit:
            upperLimit = upperLimit + upperLimit/10.
            voxelHigherUpperLim = (cMapVals>upperLimit).sum()

        while voxelHigherUpperLim < (voxelCountLimit-5):
            upperLimit = upperLimit - upperLimit/25.
            voxelHigherUpperLim = (cMapVals>upperLimit).sum()

        upperLimitStrain = upperLimit*np.nanmax(voxelStrainEnergy)
        if upperLimitStrain>upperLimitMax:
            upperLimitMax = upperLimitStrain
    
    return upperLimitMax

def render_from_VoxDict(voxel_dict, run_args, path_to_save, draw_holder = 1, draw_floor = 0, strainUpLim = None, name_tag="", perspectives=["side"]):
    """render the 3D shape in high-quality"""

    positions=voxel_dict["position"]
    voxelStrainEnergy=voxel_dict["strainEnergy"]
    orientations=voxel_dict["orientation"]

    cmap = cm.get_cmap('plasma')

    if strainUpLim is None:
        cMapVals = voxelStrainEnergy/np.nanmax(voxelStrainEnergy)
        upperLimit = np.nanmean(cMapVals)*3


        voxelCountLimit = 15
        voxelHigherUpperLim = (cMapVals>upperLimit).sum()
        while voxelHigherUpperLim > voxelCountLimit:
            upperLimit = upperLimit + upperLimit/10.
            voxelHigherUpperLim = (cMapVals>upperLimit).sum()

        while voxelHigherUpperLim < (voxelCountLimit-5):
            upperLimit = upperLimit - upperLimit/25.
            voxelHigherUpperLim = (cMapVals>upperLimit).sum()

        cMapVals = cMapVals/upperLimit

        print(run_args.desired_shape)
        print("max strain: ", np.nanmax(voxelStrainEnergy))
        print("upper limit: ", upperLimit)
        print("upper limit: ", upperLimit*np.nanmax(voxelStrainEnergy))
        print("mean strain: ", np.nanmean(voxelStrainEnergy))
        print("median strain: ", np.nanmedian(voxelStrainEnergy))
        
        for i in range(np.shape(cMapVals)[0]):
            if cMapVals[i]>1:
                cMapVals[i]=1.0
        
        cMap_norm = cMapVals

    else:
        cMapVals = voxelStrainEnergy/strainUpLim

        for i in range(np.shape(cMapVals)[0]):
            if cMapVals[i]>1:
                cMapVals[i]=1.0
        
        cMap_norm = cMapVals


    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/finalShape3D_rendered"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)

    # scale it for unit of 1
    pos = positions*5*1e3

    # adjust the coord frame of voxelyze to vpython
    x_pos = pos[:,0]
    y_pos = pos[:,2]
    z_pos = -pos[:,1]


    # scene settings
    draw_as_voxels = 1
    # draw_holder = 1
    draw_as_spheres= 0
    draw_as_curve = 0
    scene_width = 3840/2
    scene_height = 3840/2

    limitX = np.nanmax(pos[:,0])

    scene=canvas(center=vector(limitX/2,0,0), background=color.white,  width=scene_width, height=scene_height)

    scene.range = limitX/2+5
    scene.center= vector(limitX/2,0,0)
    scene.forward = vector(0, -1, -1)
    scene.autoscale = True

    # scene.lights = []
    scene.ambient=color.gray(0.5)

    # distant_light(direction=vector(-1,-1,0), color=color.gray(0.8))

    voxel_color = vector(68, 69, 72)/255
    lattice_size = 1
    voxel_size = vector(lattice_size, lattice_size, lattice_size)*1.05
    voxel_opacity = 0.9
    voxel_shininess  = 0.8
    voxel_emissive = False 

    sphere_color = vector(240,94,35)/255
    sphere_size = 0.5
    sphere_opacity = 0.8


    curve_radius = 0.5

    if draw_floor:
        floor_size  = vector(3*lattice_size*50,lattice_size*2,3*lattice_size*50)
        
        maxDim = np.max(run_args.ind_size)
        floor_size  = vector(4*lattice_size*maxDim,lattice_size*2,4*lattice_size*maxDim)
        
        floor_color = vector(170,184,194)/255
        floor_color = vector(101, 119, 134)/255
        floor_color = vector(190, 196, 204)/255
        floor_opacity = 1
        floor_emissive = 1


        box(pos = vector(run_args.ind_size[0]/2*lattice_size,-floor_size.y/2,-run_args.ind_size[1]/2*lattice_size),
            size = floor_size,
            color = floor_color,
            opacity = floor_opacity,
            emissive = 1
            )


    if draw_holder:
        
        holder_size  = vector(lattice_size*2,lattice_size*5,lattice_size*10)
        holder_color = vector(170,184,194)/255
        holder_color = vector(101, 119, 134)/255
        
        holder_opacity = 1
        box(pos = vector(-holder_size.x/2,lattice_size/2,-run_args.ind_size[1]/2),
            size = holder_size,
            color = holder_color,
            opacity = holder_opacity)


    # draw the rectangles of the voxels
    if draw_as_voxels:
        fileTag = "voxels"
        # draw the boxes
        for j in range (run_args.ind_size[1]):
            for i in range (run_args.ind_size[0]):
                idx = i + j*run_args.ind_size[0]
                if not idx>=len(pos) and not np.isnan(x_pos[idx]):

                    
                    ANGLE = orientations[idx][0]
                    # ANGLE = np.linalg.norm(orientations[idx])
                    if ANGLE < 1e-5:
                        ANGLE = 0
                        AXIS = vector(1, 0, 0)
                    else:
                        axis = orientations[idx]
                        AXIS = vector(axis[1],axis[3],-axis[2])

                    # vox_color = cmap(cMapVals[idx], bytes=True)
                    vox_color = cmap(cMap_norm[idx])
                    obj = box(pos = vector(x_pos[idx],y_pos[idx],z_pos[idx]),
                                axis = vector(1, 0, 0),
                                size = voxel_size,
                                color = vector(vox_color[0][0],vox_color[0][1],vox_color[0][2]),
                                opacity = voxel_opacity,
                                shininess = voxel_shininess
                                )


                    obj.rotate(angle=ANGLE/180.0*math.pi, axis=AXIS)

        
    # draw the sphere
    elif draw_as_spheres:
        fileTag = "spheres"
        # draw the arrow
        for i in range (np.shape(desVoxPos_scaled)[0]):
            sphere(pos = vector(x_pos[i],y_pos[i],z_pos[i]), 
                   radius = sphere_size,
                   color = sphere_color,
                   opacity=sphere_opacity)

    # draw the curve
    elif draw_as_curve:
        fileTag = "curve"
        POSs_curve = []
        for i in range (np.shape(desVoxPos_scaled)[0]):
            POSs_curve.append((x_pos[i],y_pos[i],z_pos[i]))

        curve(pos=POSs_curve,
               radius = curve_radius,
               color = sphere_color,
               opacity=sphere_opacity/4.)
    

    downloadDir = sub.check_output(["xdg-user-dir", "DOWNLOAD"])
    downloadDir = downloadDir.decode("utf-8")
    downloadDir = downloadDir[:-1]


    if "side" in perspectives:

        render_completed = 0
        while not render_completed:
            # side
            fileName = name_tag + "_scene_side"+"_"+fileTag
            copy_from = downloadDir+"/"+fileName+".png"
            filePath2save=folderPath2save+"/" + fileName+".png"

            if os.path.isfile(copy_from):
                sub.call("rm " + copy_from, shell=True)
                time.sleep(0.2)

            scene.center = vector(limitX/2,0,0)
            scene.forward = vector(0, 0, -1)
            scene.autoscale = True
            scene.capture(fileName)
            time.sleep(1)

            # save
            for i in range(60):
                if not os.path.isfile(copy_from):
                    time.sleep(1)
                else:
                    if os.path.getsize(copy_from) > 0:
                        render_completed = 1
                        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
                        time.sleep(0.2)
                        # delete the downloaded png
                        sub.call("rm " + copy_from, shell=True)


    if "isometric" in perspectives:
        render_completed = 0
        while not render_completed:

            #iso2
            fileName = name_tag + "_scene_isometric"+"_"+fileTag
            copy_from = downloadDir+"/"+fileName+".png"
            filePath2save=folderPath2save+"/" + fileName+".png"

            if os.path.isfile(copy_from):
                sub.call("rm " + copy_from, shell=True)
                time.sleep(0.2)

            scene.center= vector(limitX/2,0,0)
            scene.forward = vector(-1, -1, -1)
            scene.range = limitX/2+10

            # new iso settings
            scene.fov = 26*pi/180
            scene.camera.pos = vector(35,35,35)*2.5
            scene.camera.axis = vector(-1,-1,-1)
            scene.camera.pos = vector(35,35,35)*2.5
            scene.range = limitX/2

            scene.autoscale = True
            scene.userzoom = False
            scene.userspin = False
            scene.range = limitX/2

            scene.capture(fileName)
            time.sleep(1)

            # save
            for i in range(60):
                if not os.path.isfile(copy_from):
                    time.sleep(1)
                else:
                    if os.path.getsize(copy_from) > 0:
                        render_completed = 1
                        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
                        time.sleep(0.2)
                        # delete the downloaded png
                        sub.call("rm " + copy_from, shell=True)

    scene.delete()

def render_final_shape(path_to_run_setting, design_param_file=None, path_to_save=None, draw_holder = 1, voxel_dict=None, render_perspectives= ["isometric"]):
    """render the 3D shape in high-quality"""


    # load robot & run settings
    my_robot = load_pickle_at(design_param_file)['individual']
    run_args = load_pickle_at(path_to_run_setting)

    run_args.run_directory = design_param_file[:-18]
    run_args.voxel_color = [0., 0., 0., 0.9]
    run_args.create_history = 0
    run_args.record_video = 0
    run_args.KinEThreshold = 1e-21
    run_args.history_bandwidth = 0 
    run_args.history_sim_time = 0
    run_args.video_bandwidth = 0
    run_args.save_orientation = 1

    # re-run the simulation to get orientation as well
    if voxel_dict is None:
        run_simulation_save_position(my_robot, run_args)

        voxel_dict = get_simulation_result(run_args, my_robot, 0)

    positions=voxel_dict["position"]
    voxelStrainEnergy=voxel_dict["strainEnergy"]
    orientations=voxel_dict["orientation"]

    cmap = cm.get_cmap('plasma')
    cMapVals = voxelStrainEnergy/np.nanmax(voxelStrainEnergy)
    upperLimit = np.nanmean(cMapVals)*3


    voxelCountLimit = 15
    voxelHigherUpperLim = (cMapVals>upperLimit).sum()
    while voxelHigherUpperLim > voxelCountLimit:
        upperLimit = upperLimit + upperLimit/10.
        voxelHigherUpperLim = (cMapVals>upperLimit).sum()

    while voxelHigherUpperLim < (voxelCountLimit-5):
        upperLimit = upperLimit - upperLimit/25.
        voxelHigherUpperLim = (cMapVals>upperLimit).sum()

    cMapVals = cMapVals/upperLimit

    print(run_args.desired_shape)
    print("max strain: ", np.nanmax(voxelStrainEnergy))
    print("upper limit: ", upperLimit)
    print("upper limit: ", upperLimit*np.nanmax(voxelStrainEnergy))
    print("mean strain: ", np.nanmean(voxelStrainEnergy))
    print("median strain: ", np.nanmedian(voxelStrainEnergy))


    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/finalShape3D_rendered"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)

    # write this value to a text file
    txt_file = path_to_save+"/finalShape3D_rendered/strainMax.txt"
    fileTXT = open(txt_file, "w")
    fileTXT.write("Maximum strain value is: " + str(upperLimit*np.nanmax(voxelStrainEnergy)))
    fileTXT.write("\n")
    fileTXT.close()
    
    for i in range(np.shape(cMapVals)[0]):
        if cMapVals[i]>1:
            cMapVals[i]=1.0
    
    cMap_norm = cMapVals


    # scale it for unit of 1
    pos = positions*5*1e3

    # adjust the coord frame of voxelyze to vpython
    x_pos = pos[:,0]
    y_pos = pos[:,2]
    z_pos = -pos[:,1]


    # scene settings
    draw_as_voxels = 1
    # draw_holder = 1
    draw_as_spheres= 0
    draw_as_curve = 0

    scene_width = 3840*3/2
    scene_height = 3840*3/2

    scene_width = 3840
    scene_height = 3840

    scene_width = 3840/2
    scene_height = 3840/2

    limitX = np.nanmax(pos[:,0])

    scene=canvas(center=vector(limitX/2,0,0), background=color.white,  width=scene_width, height=scene_height)

    scene.range = limitX/2+10
    scene.center= vector(limitX/2,0,0)
    scene.forward = vector(0, -1, -1)
    scene.autoscale = True

    # scene.lights = []
    scene.ambient=color.gray(0.5)


    voxel_color = vector(68, 69, 72)/255
    lattice_size = 1
    voxel_size = vector(lattice_size, lattice_size, lattice_size)*1.05
    voxel_opacity = 0.9
    voxel_shininess  = 0.8
    voxel_emissive = False 

    sphere_color = vector(240,94,35)/255
    sphere_size = 0.5
    sphere_opacity = 0.8

    curve_radius = 0.5


    if draw_holder:
        holder_size  = vector(lattice_size*2,lattice_size*5,lattice_size*10)
        holder_color = vector(170,184,194)/255
        holder_color = vector(101, 119, 134)/255

        
        
        holder_opacity = 1
        box(pos = vector(-holder_size.x/2,lattice_size/2,-run_args.ind_size[1]/2),
            size = holder_size,
            color = holder_color,
            opacity = holder_opacity)


    # draw the rectangles of the voxels
    if draw_as_voxels:
        fileTag = "voxels"
        # draw the boxes
        for j in range (run_args.ind_size[1]):
            for i in range (run_args.ind_size[0]):
                idx = i + j*run_args.ind_size[0]
                if not idx>=len(pos) and not np.isnan(x_pos[idx]):

                    ANGLE = orientations[idx][0]
                    if ANGLE < 1e-5:
                        ANGLE = 0
                        AXIS = vector(1, 0, 0)
                    else:
                        axis = orientations[idx]
                        AXIS = vector(axis[1],axis[3],-axis[2])

                    vox_color = cmap(cMap_norm[idx])
                    obj = box(pos = vector(x_pos[idx],y_pos[idx],z_pos[idx]),
                                axis = vector(1, 0, 0),
                                size = voxel_size,
                                color = vector(vox_color[0][0],vox_color[0][1],vox_color[0][2]),
                                opacity = voxel_opacity,
                                shininess = voxel_shininess
                                )

                    obj.rotate(angle=ANGLE/180.0*math.pi, axis=AXIS)
                   
        
    # draw the sphere
    elif draw_as_spheres:
        fileTag = "spheres"
        # draw the arrow
        for i in range (np.shape(desVoxPos_scaled)[0]):
            sphere(pos = vector(x_pos[i],y_pos[i],z_pos[i]), 
                   radius = sphere_size,
                   color = sphere_color,
                   opacity=sphere_opacity)

    # draw the curve
    elif draw_as_curve:
        fileTag = "curve"
        POSs_curve = []
        for i in range (np.shape(desVoxPos_scaled)[0]):
            POSs_curve.append((x_pos[i],y_pos[i],z_pos[i]))


        curve(pos=POSs_curve,
               radius = curve_radius,
               color = sphere_color,
               opacity=sphere_opacity/4.)
    

    downloadDir = sub.check_output(["xdg-user-dir", "DOWNLOAD"])
    downloadDir = downloadDir.decode("utf-8")
    downloadDir = downloadDir[:-1]

    time.sleep(1)


    if "side" in render_perspectives:
        # side
        fileName = "finalShape_scene_side"+"_"+fileTag
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        scene.center = vector(limitX/2,0,0)
        scene.forward = vector(0, 0, -1)
        scene.autoscale = True
        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)

    if "top" in render_perspectives:
    
        #top
        fileName = "finalShape_scene_top"+"_"+fileTag
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        limitY = np.nanmin(pos[:,1])
        scene.range = scene.range + 10
        scene.center= vector(limitX/2,0,0)
        scene.forward = vector(0, -1, 0)
        scene.autoscale = True
        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)

    if "front" in render_perspectives:
        #front
        fileName = "finalShape_scene_front"+"_"+fileTag
        copy_from = downloadDir+"/"+fileName+".png"
        filePath2save=folderPath2save+"/" + fileName+".png"

        if os.path.isfile(copy_from):
            sub.call("rm " + copy_from, shell=True)
            time.sleep(0.2)

        
        
        maxZ = np.nanmax(y_pos)
        minZ = np.nanmin(y_pos)
        scene.center= vector(limitX/2,(maxZ+minZ)/2,-run_args.ind_size[1]/2)
        scene.range = scene.range + 10 
        scene.forward = vector(-1, 0, 0)
        scene.autoscale = True
        scene.capture(fileName)
        time.sleep(1)

        # save
        for i in range(60):
            if not os.path.isfile(copy_from):
                time.sleep(1)
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)

    if "isometric" in render_perspectives:
        render_completed = 0
        while not render_completed:
            #iso
            fileName = "finalShape_scene_iso"+"_"+fileTag
            copy_from = downloadDir+"/"+fileName+".png"
            filePath2save=folderPath2save+"/" + fileName+".png"

            if os.path.isfile(copy_from):
                sub.call("rm " + copy_from, shell=True)
                time.sleep(0.2)

            scene.center= vector(limitX/2,0,0)
            scene.forward = vector(-1, -1/sqrt(3), -1)
            scene.range = limitX/2+10

            # new iso settings
            scene.fov = 26*pi/180
            scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
            scene.camera.axis = vector(-sqrt(3),-1,-sqrt(3))
            scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
            scene.range = limitX/2+10


            scene.autoscale = True
            scene.userzoom = False
            scene.userspin = False
            scene.range = limitX/2+10

            scene.capture(fileName)
            time.sleep(1)

            # save
            for i in range(60):
                if not os.path.isfile(copy_from):
                    time.sleep(1)
                else:
                    if os.path.getsize(copy_from) > 0:
                        render_completed = 1
        sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
        time.sleep(0.2)
        # delete the downloaded png
        sub.call("rm " + copy_from, shell=True)

    scene.delete()

def render_desired_shape(path_to_run_setting=None, path_to_save=None, draw_as_spheres=1, draw_as_voxels=0, draw_as_curve=0, draw_holder=1):
    
    highQuality=1
    # convert Mtheta and Mphi for magnetic profile
    run_args = load_pickle_at(path_to_run_setting)

    desVoxPos = getDesiredShape(run_args, drawShape=0)

    # if it is a functional case --> pass
    if len(desVoxPos) == 0: 
        return
    
    # scale it for unit of 1
    desVoxPos_scaled = desVoxPos*5

    if run_args.magnetization_direction == "2D" and draw_as_curve:
        start = run_args.ind_size[0]*int(run_args.ind_size[1]/2)
        end = start + run_args.ind_size[0]
        desVoxPos_scaled = desVoxPos_scaled[start:end]

    # adjust the coord frame of voxelyze to vpython
    x_pos = desVoxPos_scaled[:,1]
    y_pos = desVoxPos_scaled[:,3]
    z_pos = -desVoxPos_scaled[:,2]

    
    scene_width = 3840*3/2
    scene_height = 3840 *3/2

    limitX = np.amax(desVoxPos[:,1])*5

    scene=canvas(center=vector(limitX/2,0,0), background=color.white,  width=scene_width, height=scene_height)

    scene.range = limitX/2+10
    scene.center= vector(limitX/2,0,0)
    scene.forward = vector(0, -1, -1)
    scene.autoscale = True

    # scene.lights = []
    scene.ambient=color.gray(0.5)

    # distant_light(direction=vector(-1,-1,0), color=color.gray(0.8))

    voxel_color = vector(68, 69, 72)/255
    lattice_size = 1
    voxel_size = vector(lattice_size, lattice_size, lattice_size)*1
    voxel_opacity = 0.8

    sphere_color = vector(126, 164, 179)/255
    sphere_size = 0.5
    sphere_opacity = 0.8
    sphere_shininess  = 0.8
    sphere_emissive = False 

    curve_radius = 0.5


    if draw_holder:
        holder_size  = vector(lattice_size*2,lattice_size*5,lattice_size*10)
        holder_color = vector(170,184,194)/255
        holder_color = vector(101, 119, 134)/255


        holder_opacity = 1
        box(pos = vector(-holder_size.x/2,lattice_size/2,-run_args.ind_size[1]/2),
            size = holder_size,
            color = holder_color,
            opacity = holder_opacity)

    # draw the rectangles of the voxels
    if draw_as_voxels:
        fileTag = "voxels"
        # draw the boxes
        for j in range (run_args.ind_size[1]):
            for i in range (run_args.ind_size[0]):
                idx = i + j*run_args.ind_size[0]
                if not idx>=len(desVoxPos):
                    if i == 0 :
                        AXIS = vector(1,0,0)
                    elif i == run_args.ind_size[0] or (idx+1)>(len(desVoxPos)-1):
                        AXIS = vector(x_pos[idx],y_pos[idx],z_pos[idx]) - vector(x_pos[idx-1],y_pos[idx-1],z_pos[idx-1])
                    else: 
                        AXIS = vector(x_pos[idx+1],y_pos[idx+1],z_pos[idx+1]) - vector(x_pos[idx-1],y_pos[idx-1],z_pos[idx-1])

                    box(pos = vector(x_pos[idx],y_pos[idx],z_pos[idx]),
                        axis = AXIS,
                        size = voxel_size,
                        color = voxel_color,
                        opacity = voxel_opacity)
        
    # draw the sphere
    elif draw_as_spheres:
        fileTag = "spheres"
        # draw the arrow
        for i in range (np.shape(desVoxPos_scaled)[0]):
            sphere(pos = vector(x_pos[i],y_pos[i],z_pos[i]), 
                   radius = sphere_size,
                   color = sphere_color,
                   opacity=sphere_opacity,
                   shininess = sphere_shininess)

    # draw the curve
    elif draw_as_curve:
        fileTag = "curve"
        POSs_curve = []
        for i in range (np.shape(desVoxPos_scaled)[0]):
            POSs_curve.append((x_pos[i],y_pos[i],z_pos[i]))

        curve(pos=POSs_curve,
               radius = curve_radius,
               color = sphere_color,
               opacity=sphere_opacity/4.0,
               shininess = sphere_shininess)
    

    # create a folder for the rendered shapes
    folderPath2save=path_to_save+"/desiredShape_rendered"
    if not os.path.isdir(folderPath2save):
        sub.call("mkdir " + folderPath2save, shell=True)
        time.sleep(0.2)


    downloadDir = sub.check_output(["xdg-user-dir", "DOWNLOAD"])
    downloadDir = downloadDir.decode("utf-8")
    downloadDir = downloadDir[:-1]

    # side
    fileName = "desiredShape_scene_side"+"_"+fileTag
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center= vector(limitX/2,0,0)
    scene.forward = vector(0, 0, -1)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)



    #top
    fileName = "desiredShape_scene_top"+"_"+fileTag
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center= vector(limitX/2,0,0)
    scene.forward = vector(0, -1, 0)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)



    #front
    fileName = "desiredShape_scene_front"+"_"+fileTag
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)
    
    maxZ = np.nanmax(y_pos)
    minZ = np.nanmin(y_pos)
    scene.center= vector(limitX/2,(maxZ+minZ)/2,-run_args.ind_size[1]/2)
    scene.forward = vector(-1, 0, 0)
    scene.autoscale = True
    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)



    #iso
    fileName = "desiredShape_scene_iso"+"_"+fileTag
    copy_from = downloadDir+"/"+fileName+".png"
    filePath2save=folderPath2save+"/" + fileName+".png"

    if os.path.isfile(copy_from):
        sub.call("rm " + copy_from, shell=True)
        time.sleep(0.2)

    scene.center= vector(limitX/2,0,0)
    scene.forward = vector(-1, -1/sqrt(3), -1)
    scene.range = limitX/2+10

    # new iso settings
    scene.fov = 26*pi/180
    scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
    scene.camera.axis = vector(-sqrt(3),-1,-sqrt(3))
    scene.camera.pos = vector(36.7, 24.9, 32.7)*2.5
    scene.range = limitX/2+10

    scene.autoscale = True
    scene.userzoom = False
    scene.userspin = False
    scene.range = limitX/2+10

    scene.capture(fileName)
    time.sleep(1)

    # save
    for i in range(60):
        if not os.path.isfile(copy_from):
            time.sleep(1)
    sub.call("cp " + copy_from+ " " + filePath2save, shell=True)
    time.sleep(0.2)
    # delete the downloaded png
    sub.call("rm " + copy_from, shell=True)


def cart2sph(x,y,z):
    XsqPlusYsq = x**2 + y**2
    r = math.sqrt(XsqPlusYsq + z**2)               # r
    phi = math.atan2(math.sqrt(XsqPlusYsq), z)     # phi
    theta = math.atan2(y,x)                        # theta
    return r, theta, phi

def sph2cart(r, theta, phi):
    dx=r*math.sin(phi)*math.cos(theta)
    dy=r*math.sin(phi)*math.sin(theta)
    dz=r*math.cos(phi)
    return dx,dy,dz


"Visualization of the map-elites archive"
def wrap_up_archive(grid_num, archive_path, path_pickledPops, elites_path, save_path, inds_path):

    # path arrangements
    elites_path = elites_path + "/"

    if not os.path.isdir(save_path):
        sub.call("mkdir " + save_path, shell=True)
        time.sleep(0.2)


    # load the archive
    if archive_path is None:

        pickled_pops = glob(path_pickledPops+"/*")
        last_gen = natural_sort(pickled_pops, reverse=True)[0]
        with open(last_gen, 'rb') as handle:
            [optimizer, random_state, numpy_random_state] = pickle.load(handle)

        archive = optimizer.BC_archive

    else:
        with open(archive_path, 'rb') as f:
            out = pickle.load(f)
        archive = out['archive']


    # params
    # params2set
    grid_size = np.array((grid_num, grid_num), dtype=int)

    archive_size = archive.nb_cells_per_dimension
    cell_id_map = archive.cell_ids
    perf_map = archive.map_perf
    args = archive.args

    # regions
    cell_regions = cell_id_map.reshape((grid_size[0], int(archive_size[1]/grid_size[1]), grid_size[1], int(archive_size[0]/grid_size[0])  ))
    cell_regions = cell_regions.swapaxes(1,2)

    perf_regions = perf_map.reshape((grid_size[0], int(archive_size[1]/grid_size[1]), grid_size[1], int(archive_size[0]/grid_size[0])  ))
    perf_regions = perf_regions.swapaxes(1,2)

    # params to fill
    best_cell_ids = np.zeros((grid_size), dtype=int)
    best_ind_ids = np.zeros((grid_size), dtype=int)
    best_inds_perf = np.zeros((grid_size))

        
    # find the best cell ids
    for _i in range(grid_size[0]):
        for _j in range(grid_size[1]):
            if not args.fitness_maximize:
                # index = np.nanargmin(perf_regions[_i, _j], keepdims=True)
                # best_cell_ids[_i, _j] = cell_regions[index[0], index[1]]
                if np.isnan(perf_regions[_i, _j].flatten()).all():
                    best_cell_ids[_i, _j] = -1
                else:    
                    _index = np.nanargmin(perf_regions[_i, _j])
                    index = np.unravel_index(_index, perf_regions[_i, _j].shape)
                    best_cell_ids[_i, _j] = cell_regions[_i, _j][index]

            else:
                raise NotImplementedError


    # find the corresponding ind Ids
    for _i in range(grid_size[0]):
        for _j in range(grid_size[1]):
            if best_cell_ids[_i, _j] == -1:
                best_ind_ids[_i, _j] = -1
                best_inds_perf[_i, _j] = -1
            else:    
                # load the cell_ind
                elite_path = elites_path + str(best_cell_ids[_i, _j]) + ".pickle"
                with open(elite_path, 'rb') as f:
                    out = pickle.load(f)

                individual = out['individual']
                # assert np.nanmin(perf_regions[_i, _j]) == out['performance']
                best_ind_ids[_i, _j] = individual.id
                best_inds_perf[_i, _j] = individual.fitness


    # save the data into related folder
    # deduce the name of the archive
    archive_name = archive_path.split('/')[-1]
    archive_name = archive_name.split('.')[0]
    
    # pickle data
    save_path_archive = save_path + "/" + archive_name
    if not os.path.isdir(save_path_archive):
        sub.call("mkdir " + save_path_archive, shell=True)
        time.sleep(0.2)

    data_file = save_path_archive + "/visualization_data.pickle"

    to_save = dict()
    to_save.update( grid_size=grid_size,
                    best_cell_ids=best_cell_ids,
                    best_ind_ids=best_ind_ids,
                    best_inbest_inds_perfds_map =best_inds_perf
                    )
    
    with open(data_file, "wb") as handle:
        pickle.dump(to_save, handle)

    # copy the archieve
    sub.call("cp " + archive_path + " " + save_path_archive, shell=True)

    # copy inds
    save_path_best_inds = save_path_archive + "/inds"
    if not os.path.isdir(save_path_best_inds):
        sub.call("mkdir " + save_path_best_inds, shell=True)
        time.sleep(0.2)

    for ind_id in best_ind_ids.flatten():
        if ind_id ==-1:
            pass
        else:
            ind_path = inds_path + "/Ind--id_"+str(ind_id).zfill(7)
            copy_path_ind = save_path_best_inds + "/Ind--id_"+str(ind_id).zfill(7)
            
            sub.call("cp -r " + ind_path + " " + copy_path_ind , shell=True)
            time.sleep(0.2)

def render_archive_inds(path_save, render_morphology=1, render_finalShape=1, render_perspectives=["isometric"]):

    # find the archives to visualize
    archives = glob(path_save+"/*")
    ordered_archives = natural_sort(archives, reverse=False)    

    for archive in ordered_archives:
        # create the visualization folder
        save_path_visualization = archive + "/visualization"
        if not os.path.isdir(save_path_visualization):
            sub.call("mkdir " + save_path_visualization, shell=True)
            time.sleep(0.2)

        save_path_inds_rendered = archive + "/rendered_inds"
        if not os.path.isdir(save_path_inds_rendered):
            sub.call("mkdir " + save_path_inds_rendered, shell=True)
            time.sleep(0.2)

        # get the inds
        inds = glob(archive+"/inds/*")
        ordered_inds = natural_sort(inds, reverse=False)

        # render each cell/ind
        for ind_folder in ordered_inds:
            # render design
            design_param_file=ind_folder + "/" + ind_folder[-10:] + ".pickle"
            path_save_ind_rendered = save_path_inds_rendered + "/" + ind_folder[-15:]
            if not os.path.isdir(path_save_ind_rendered):
                sub.call("mkdir " + path_save_ind_rendered, shell=True)
                time.sleep(0.2)
            
            if os.path.isfile(design_param_file):

                if render_morphology:
                    render_design(design_param_file, path_to_save=path_save_ind_rendered, render_perspectives= render_perspectives, render_M_arrow=0)

                if render_finalShape:
                    # render isometric view shape
                    path_to_run_setting = archive + "/run_settings.pickle"            
                    render_final_shape(path_to_run_setting, design_param_file, path_to_save=path_save_ind_rendered, draw_holder = 1)
            
            else:
                print("Cannot find the required file for: "+ind_folder[-10:])
                print("Passed")
                pass

def get_cmap_value(grid_size, best_inds_perf):

    perfRange = [0,1]

    best_inds_perf_array = best_inds_perf.flatten()
    
    perfRange[0] = np.nanmin(best_inds_perf_array)
    cMapVals = best_inds_perf - perfRange[0]
    perfRange[1] = np.nanmean(best_inds_perf_array)*3
    perfRange[1] = 1.0

    for _i in range(np.shape(cMapVals)[0]):
        for _j in range(np.shape(cMapVals)[1]):
            if cMapVals[_i,_j]>1:
                cMapVals[_i,_j]>=1.0

    # flip perf matrix
    cMapVals = cMapVals - 1
    cMapVals = np.abs(cMapVals)

    return cMapVals

def get_best_inds_perf(archive, best_cell_ids, grid_size):
    path_archive = archive
    archive_name = path_archive.split('/')[-1]
    path_archivePickle = path_archive+ "/" + archive_name + ".pickle"
    # load the archive
    with open(path_archivePickle, 'rb') as f:
        out = pickle.load(f)
    archive = out['archive']

    best_inds_perf = np.zeros((grid_size[0],grid_size[1]))
    perf_map = archive.map_perf

    for _i in range(grid_size[0]):
        for _j in range(grid_size[1]):
            best_inds_perf[_i,_j] = perf_map.flatten()[best_cell_ids[_i,_j]]

    return best_inds_perf

def convertImage(path_image, path_to_save):
    quality_value = 100
    img = Image.open(path_image)
    img = img.convert("RGBA")
  
    datas = img.getdata()
    newData = []
  
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
  
    img.putdata(newData)

    img_cropped = img.crop(img.getbbox())
    img_cropped.save(path_to_save, "PNG", quality=quality_value)

def fillBackground_image(path_image, path_to_save, background_RGB, alpha):
    quality_value = 100
    img = Image.open(path_image)
    img = img.convert("RGBA")

    new_image = Image.new("RGBA", img.size, "WHITE") # Create a white rgba background
    new_image.paste(img, (0, 0), img)  

    img = new_image
  
    datas = img.getdata()
    newData = []
  
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((int(background_RGB[0]*255), int(background_RGB[1]*255), int(background_RGB[2]*255), int(background_RGB[3]*255)))
        else:
            newData.append(item)
  
    img.putdata(newData)

    img_cropped = img.crop(img.getbbox())
    img_cropped.save(path_to_save, "PNG", quality=quality_value)

def visualize_archive(path_save):

    # find the archives to visualize
    archives = glob(path_save+"/*")
    ordered_archives = natural_sort(archives, reverse=False)    

    for archive in ordered_archives:
        # get the ind IDs for each tile
        path_visualization_data = archive + "/visualization_data.pickle"
        visualization_data = load_pickle_at(path_visualization_data)

        grid_size=visualization_data["grid_size"]
        best_cell_ids=visualization_data["best_cell_ids"]
        best_ind_ids=visualization_data["best_ind_ids"]

        options = [4]
        colored_background = 0

        if colored_background:
            if not "best_inds_perf" in visualization_data.keys():
                best_inds_perf=get_best_inds_perf(archive, best_cell_ids, grid_size)
            else:
                best_inds_perf=visualization_data["best_inds_perf"]

            background_color = get_cmap_value(grid_size, best_inds_perf)
            cmap = cm.get_cmap('Blues')
            transperancy = 0.5

        for option in options:
            tile_option = option
            tile_name = "tile_opt"+str(tile_option)

            # for each ind make a tile and save
            for ind_id in best_ind_ids.flatten():
                # paths for the images to load and save
                path_ind = archive + "/rendered_inds/Ind--id_"+str(ind_id).zfill(7)
                if os.path.isdir(path_ind):

                    path_morph = path_ind + "/rendered_design/designScene_top_onlyMorph.png"
                    path_design = path_ind + "/rendered_design/designScene_isoEXPyellow.png"
                    path_final_shape = path_ind + "/finalShape3D_rendered/finalShape_scene_iso_voxels.png"

                    path_morph_cleaned = path_morph[:-4]+"_cleaned.png"
                    path_design_cleaned = path_design[:-4]+"_cleaned.png"
                    path_final_shape_cleaned = path_final_shape[:-4]+"_cleaned.png"

                    # crop and clear background of the images 
                    if not os.path.isfile(path_morph_cleaned):  # pass if it's already done
                        convertImage(path_morph, path_morph_cleaned)
                        convertImage(path_design, path_design_cleaned)
                        convertImage(path_final_shape, path_final_shape_cleaned)

                    # create the tile
                    quality_value = 100
                    
                    # option 1
                    if tile_option == 1:
                        basewidth = 300*3
                        baseheight = basewidth

                        baseheight_top = int(baseheight/2)
                        baseheight_bot = int(baseheight-baseheight_top)
                        
                        # Upper side
                        # scale the design image
                        img_design = Image.open(path_design_cleaned)
                        wpercent = (basewidth/float(img_design.size[0]))*0.95
                        hsize = int((float(img_design.size[1])*float(wpercent)))
                        img_design_scaled = img_design.resize((int(basewidth*0.95), hsize), Image.ANTIALIAS)

                        # scale the design image
                        img_morph = Image.open(path_morph_cleaned)
                        # correcting the orientation
                        img_morph = img_morph.transpose(Image.FLIP_LEFT_RIGHT)
                        img_morph = img_morph.transpose(Image.FLIP_TOP_BOTTOM)
                        hpercent = (baseheight_top/5.5/float(img_morph.size[1]))
                        wsize = int((float(img_morph.size[0])*float(hpercent)))
                        img_morph_scaled = img_morph.resize((wsize,int(baseheight_top/5.5)), Image.ANTIALIAS)
                        
                        # combine design and morph
                        img_design_size = img_design_scaled.size
                        img_morph_size = img_morph_scaled.size

                        tile_top = Image.new('RGBA', (basewidth, baseheight_top))
                        tile_top.paste(img_design_scaled, (0, 0))
                        tile_top.paste(img_morph_scaled, (0,img_design_size[1]-img_morph_size[1]))

                        path_tile_top = path_ind + "/tile_top.png"
                        tile_top.save(path_tile_top, "PNG", quality=quality_value)

                        # scale the final shape
                        img_final_shape = Image.open(path_final_shape_cleaned)
                        
                        wpercent = (basewidth/float(img_final_shape.size[0]))
                        hpercent = (baseheight_bot/float(img_final_shape.size[1]))
                        percent = wpercent if hpercent>wpercent else hpercent
                        percent = percent*0.95

                        hsize = int((float(img_final_shape.size[1])*float(percent)))
                        wsize = int((float(img_final_shape.size[0])*float(percent)))
                        img_final_shape_scaled = img_final_shape.resize((wsize,hsize), Image.ANTIALIAS)

                        # final tile
                        tile = Image.new('RGBA', (basewidth, baseheight))
                        hpos = int((baseheight_top-tile_top.height)/2)
                        wpos = int((basewidth-tile_top.width)/2)
                        tile.paste(tile_top, (wpos, hpos))

                        hpos = int(baseheight_top+(baseheight_bot-img_final_shape_scaled.height)/2)
                        wpos = int((tile_top.width-img_final_shape_scaled.width)/2)
                        tile.paste(img_final_shape_scaled, (wpos, hpos))

                        path_tile = path_ind + "/"+tile_name+".png"
                        tile.save(path_tile, "PNG", quality=quality_value)
                    if tile_option == 2:
                        basewidth = 300*3
                        baseheight = int(basewidth/5*4)
                        baseheight_top = int(baseheight*2/3)
                        baseheight_bot = int(baseheight-baseheight_top)

                        # scale the design image
                        img_design = Image.open(path_design_cleaned)
                        wpercent = (basewidth/float(img_design.size[0]))*0.95
                        hsize = int((float(img_design.size[1])*float(wpercent)))
                        img_design_scaled = img_design.resize((int(basewidth*0.95), hsize), Image.ANTIALIAS)

                        # scale the morph image
                        img_morph = Image.open(path_morph_cleaned)
                        # correcting the orientation
                        img_morph = img_morph.transpose(Image.FLIP_LEFT_RIGHT)
                        img_morph = img_morph.transpose(Image.FLIP_TOP_BOTTOM)

                        wpercent = (basewidth/float(img_morph.size[0]))*0.95
                        hsize = int((float(img_morph.size[1])*float(wpercent)))
                        img_morph_scaled = img_morph.resize((int(basewidth*0.95), hsize), Image.ANTIALIAS)

                        # combine design and morph
                        img_design_size = img_design_scaled.size
                        img_morph_size = img_morph_scaled.size

                        tile = Image.new('RGBA', (basewidth, basewidth))
                        wpos = int((basewidth-img_design_size[0])/2)
                        hpos = int((baseheight_top-img_design_size[1])/2)

                        tile.paste(img_design_scaled, (wpos, hpos))
                        wpos = int((basewidth-img_morph_size[0])/2)
                        hpos = int((baseheight_top + (baseheight_bot-img_morph_size[1])/2))
                        tile.paste(img_morph_scaled, (wpos,hpos))

                        path_tile = path_ind + "/"+tile_name+".png"
                        tile.save(path_tile, "PNG", quality=quality_value)
                    if tile_option == 3:
                        basewidth = 300*3
                        baseheight = basewidth

                        baseheight_top = int(baseheight/2)
                        baseheight_bot = int(baseheight-baseheight_top)
                        
                        # Upper side
                        # scale the design image
                        img_design = Image.open(path_design_cleaned)
                        wpercent = (basewidth/float(img_design.size[0]))*0.95
                        hsize = int((float(img_design.size[1])*float(wpercent)))
                        img_design_scaled = img_design.resize((int(basewidth*0.95), hsize), Image.ANTIALIAS)

                        # scale the design image
                        img_morph = Image.open(path_morph_cleaned)
                        # correcting the orientation
                        img_morph = img_morph.transpose(Image.FLIP_LEFT_RIGHT)
                        img_morph = img_morph.transpose(Image.FLIP_TOP_BOTTOM)
                        hpercent = (baseheight_top/5.5/float(img_morph.size[1]))
                        wsize = int((float(img_morph.size[0])*float(hpercent)))
                        img_morph_scaled = img_morph.resize((wsize,int(baseheight_top/5.5)), Image.ANTIALIAS)
                        
                        # combine design and morph
                        img_design_size = img_design_scaled.size
                        img_morph_size = img_morph_scaled.size

                        tile_top = Image.new('RGBA', (basewidth, baseheight_top))
                        tile_top.paste(img_design_scaled, (0, 0))
                        # tile_top.paste(img_morph_scaled, (0,img_design_size[1]-img_morph_size[1]))

                        path_tile_top = path_ind + "/tile_top.png"
                        tile_top.save(path_tile_top, "PNG", quality=quality_value)

                        # scale the final shape
                        img_final_shape = Image.open(path_final_shape_cleaned)
                        
                        wpercent = (basewidth/float(img_final_shape.size[0]))
                        hpercent = (baseheight_bot/float(img_final_shape.size[1]))
                        percent = wpercent if hpercent>wpercent else hpercent
                        percent = percent*0.95

                        hsize = int((float(img_final_shape.size[1])*float(percent)))
                        wsize = int((float(img_final_shape.size[0])*float(percent)))
                        img_final_shape_scaled = img_final_shape.resize((wsize,hsize), Image.ANTIALIAS)

                        # final tile
                        tile = Image.new('RGBA', (basewidth, baseheight))
                        hpos = int((baseheight_top-tile_top.height)/2)
                        wpos = int((basewidth-tile_top.width)/2)
                        tile.paste(tile_top, (wpos, hpos))

                        hpos = int(baseheight_top+(baseheight_bot-img_final_shape_scaled.height)/2)
                        wpos = int((tile_top.width-img_final_shape_scaled.width)/2)
                        tile.paste(img_final_shape_scaled, (wpos, hpos))

                        path_tile = path_ind + "/"+tile_name+".png"
                        tile.save(path_tile, "PNG", quality=quality_value)            
                    if tile_option == 4:
                        basewidth = 300*3

                        baseheight = int(basewidth/5*4)
                        baseheight_bot = int(baseheight*7/9)
                        baseheight_top = int(baseheight-baseheight_bot)
                        
                        
                        # Upper side
                        # scale the design image
                        img_design = Image.open(path_design_cleaned)
                        wpercent = (basewidth/float(img_design.size[0]))*0.95
                        hsize = int((float(img_design.size[1])*float(wpercent)))
                        img_design_scaled = img_design.resize((int(basewidth*0.95), hsize), Image.ANTIALIAS)

                        # scale the design image
                        img_morph = Image.open(path_morph_cleaned)
                        # correcting the orientation
                        img_morph = img_morph.transpose(Image.FLIP_LEFT_RIGHT)
                        img_morph = img_morph.transpose(Image.FLIP_TOP_BOTTOM)

                        wpercent = (basewidth/float(img_morph.size[0]))*0.95
                        hsize = int((float(img_morph.size[1])*float(wpercent)))
                        img_morph_scaled = img_morph.resize((int(basewidth*0.95), hsize), Image.ANTIALIAS)

                        
                        # combine design and morph
                        img_design_size = img_design_scaled.size
                        img_morph_size = img_morph_scaled.size

                        tile_top = Image.new('RGBA', (basewidth, baseheight_top))
                        hpos = int((baseheight_top-img_morph_scaled.height)/2)
                        wpos = int((basewidth-img_morph_scaled.width)/2)
                        tile_top.paste(img_morph_scaled, (wpos, hpos))
                        # tile_top.paste(img_morph_scaled, (0,img_design_size[1]-img_morph_size[1]))

                        path_tile_top = path_ind + "/tile_top.png"
                        tile_top.save(path_tile_top, "PNG", quality=quality_value)

                        # scale the final shape
                        img_final_shape = Image.open(path_final_shape_cleaned)
                        
                        wpercent = (basewidth/float(img_final_shape.size[0]))
                        hpercent = (baseheight_bot/float(img_final_shape.size[1]))
                        percent = wpercent if hpercent>wpercent else hpercent
                        percent = percent*0.95

                        hsize = int((float(img_final_shape.size[1])*float(percent)))
                        wsize = int((float(img_final_shape.size[0])*float(percent)))
                        img_final_shape_scaled = img_final_shape.resize((wsize,hsize), Image.ANTIALIAS)

                        # final tile
                        tile = Image.new('RGBA', (basewidth, baseheight))
                        hpos = int((baseheight_top-tile_top.height)/2)
                        wpos = int((basewidth-tile_top.width)/2)
                        tile.paste(tile_top, (wpos, hpos))

                        hpos = int(baseheight_top+(baseheight_bot-img_final_shape_scaled.height)/2)
                        wpos = int((basewidth-img_final_shape_scaled.width)/2)
                        tile.paste(img_final_shape_scaled, (wpos, hpos))

                        path_tile = path_ind + "/"+tile_name+".png"
                        tile.save(path_tile, "PNG", quality=quality_value)
                    
            # connect all the tiles
            tile_spacing_w = int(basewidth*0.1)
            tile_spacing_h = int(baseheight*0.1)
            tile_final = Image.new('RGBA', (basewidth*grid_size[0]+(grid_size[0]-1)*tile_spacing_w,baseheight*grid_size[1]+(grid_size[1]-1)*tile_spacing_h))
            if colored_background:
                tile_final_colored = Image.new('RGBA', (basewidth*grid_size[0]+(grid_size[0]-1)*tile_spacing_w,baseheight*grid_size[1]+(grid_size[1]-1)*tile_spacing_h))

            for _i in range(grid_size[0]):
                for _j in range(grid_size[1]):
                    ind_id = best_ind_ids[_i,_j]
                    path_ind_tile = archive + "/rendered_inds/Ind--id_"+str(ind_id).zfill(7) + "/"+tile_name+".png"
                    if os.path.isfile(path_ind_tile):
                        img_ind_tile = Image.open(path_ind_tile)
                        tile_final.paste(img_ind_tile, (_i*(basewidth+tile_spacing_w), _j*(baseheight+tile_spacing_h)))
                        img_ind_tile.close()
                    
                    if colored_background:
                        path_to_save = archive + "/rendered_inds/Ind--id_"+str(ind_id).zfill(7) + "/"+tile_name+"_colored.png"
                        background_RGB = cmap(background_color[_i,_j])
                        fillBackground_image(path_ind_tile, path_to_save, background_RGB, transperancy)
                        img_ind_tile_colored = Image.open(path_to_save)
                        tile_final_colored.paste(img_ind_tile_colored, (_i*(basewidth+tile_spacing_w), _j*(baseheight+tile_spacing_h)))

            path_tile_final = archive + "/visualization/"+tile_name+"_final.png"
            tile_final.save(path_tile_final, "PNG", quality=quality_value)

            if colored_background:
                path_tile_final_colored = archive + "/visualization/"+tile_name+"_final_colored.png"
                tile_final_colored.save(path_tile_final_colored, "PNG", quality=quality_value)

def copy_random_inds(path_inds, random_ind_num, path_save):

    if not os.path.isdir(path_save):
        sub.call("mkdir " + path_save, shell=True)
        time.sleep(0.2)

    inds = glob(path_inds+"/*")
    tot_ind_num = len(inds)

    random_ind_ids = np.random.rand(random_ind_num)*tot_ind_num
    random_ind_ids = random_ind_ids.astype(int)

    for _i in range(random_ind_num):
        id = int(random_ind_ids[_i])


        # copy inds
        save_path_best_inds = path_save + "/random_inds"
        if not os.path.isdir(save_path_best_inds):
            sub.call("mkdir " + save_path_best_inds, shell=True)
            time.sleep(0.2)

        
        ind_path = path_inds + "/Ind--id_"+str(id).zfill(7)
        copy_path_ind = save_path_best_inds + "/Ind--id_"+str(id).zfill(7)
        

        sub.call("cp -r " + ind_path + " " + copy_path_ind , shell=True)
        time.sleep(0.2)


def main():
    pass


if __name__ == "__main__":

    main()