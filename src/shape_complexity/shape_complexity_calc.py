#!/usr/bin/env python
"""

ToDo:

explanation for the what this code does?

"""

# External imports
import matplotlib
matplotlib.use('Agg')
import numpy as np
import os
import sys
import argparse
import time
import matplotlib.pyplot as plt
import pickle
from glob import glob
import seaborn as sns
from matplotlib import cm
import pandas as pd
import cv2
from skimage.morphology import skeletonize
from skimage import img_as_ubyte

# Appending repo's root dir in the python path to enable subsequent imports
sys.path.append(os.getcwd() + "/..")



def parse_arguments():
    """
    A

    -Alp
    """
    parser = argparse.ArgumentParser(description='trial', fromfile_prefix_chars="@")

    parser.add_argument('--debug', type=int, default=0, help="")

    # calculate_shape_complexity_score
    parser.add_argument('--calculate_shape_complexity_score', type=int, default=1, help="")


    # params
    parser.add_argument('--target_width', type=int, default=360, help="")

    parser.add_argument('--node_number', type=int, default=-1, help="")
    parser.add_argument('--edge_length', type=int, default=0.1, help=" in mm")


    parser.add_argument('--window_size', type=int, default=3, help="")
    parser.add_argument('--poly_order', type=int, default=1, help="")


    parser.add_argument('--path_shape2calculate', type=str, default="/..", help="")


    parser.add_argument('--path_2save', type=str, default="/..", help="")



    return parser.parse_args()


"getting the shape profile and positions from image"


def draw_frame_N_points(args, shape_name, frame, frame_processed, frame_cropped, beam_sliced, beam_profile_interp, ref_point_wrt_original, x_start, y_start, file_path=None):
    fig, axes = plt.subplots(2, 2, figsize=(8, 8), sharex=False, sharey=False)
    ax = axes.ravel()

    ax[0].imshow(frame, cmap=plt.cm.gray)
    ax[0].set_title('original')
    ax[0].axis('off')

    ax[1].imshow(frame_processed, cmap=plt.cm.gray)
    ax[1].set_title('thresholded')
    ax[1].axis('off')

    ax[2].imshow(frame_cropped, cmap=plt.cm.gray)
    ax[2].scatter(beam_sliced[:,5]-x_start, beam_sliced[:,4]-y_start, c="red", s = 1)
    ax[2].set_title('detected')
    ax[2].axis('off')

    ax[3].imshow(frame_cropped, cmap=plt.cm.gray)
    ax[3].scatter(beam_profile_interp[:,0]-x_start+ref_point_wrt_original[1], beam_profile_interp[:,1]-y_start+ref_point_wrt_original[0], c="red", s = 1)

    ax[3].set_title("beam profile")
    ax[3].axis('off')

    fig.tight_layout()
    if file_path is None:
        file_path = args.path_2save + "/"  + shape_name + "_shape_processed.jpg"

    plt.savefig(file_path, dpi=150)
    plt.close()

def get_neighbouring_indices(idx, w, max):

    upper_idx = idx+w
    lower_idx = idx-w

    neighbouring_indices = np.linspace(lower_idx, upper_idx, 2*w+1).astype(int)

    for index in range(neighbouring_indices.shape[0]):
        if neighbouring_indices[index] >= max:
            neighbouring_indices[index] = neighbouring_indices[index]-max
        if neighbouring_indices[index] < 0:
            neighbouring_indices[index] = neighbouring_indices[index]+max

    return neighbouring_indices

def slice_beam(contour):

    beam_sliced = np.empty((contour.shape[0], 8))
    beam_sliced[:] = np.nan

    # get the distances among the points at the counters
    dists = np.zeros((contour.shape[0],contour.shape[0]))
    dists_diff = np.zeros((contour.shape[0],contour.shape[0]))

    dists_diff_sign_diff = np.zeros((contour.shape[0],contour.shape[0]))

    # get the grad & hessian for distances among the points at the counters
    for i in range(contour.shape[0]):
        point_a = contour[i,:]
        for j in range(contour.shape[0]):
            point_b = contour[j,:]
            dist = np.linalg.norm(point_a-point_b)
            dists[i,j] = dist

        dists_diff[i,:] = np.ediff1d(dists[i,:], to_begin=dists[i,0])

    dists_diff_abs = np.abs(dists_diff)
    dists_diff_sign = np.sign(dists_diff)
    for i in range(contour.shape[0]):
        dists_diff_sign_diff[i,:] = np.ediff1d(dists_diff_sign[i,:], to_begin=dists_diff_sign[i,0])

    dists_avg = np.median(dists, axis=1)


    for i in range(contour.shape[0]):

        neighbouring_indices = get_neighbouring_indices(i, 5, contour.shape[0])

        matching_pt_index = None
        indices = []
        while np.argmax(dists_diff_sign_diff[i,:])>0:

            index = np.argmax(dists_diff_sign_diff[i,:])

            if dists_diff_sign_diff[i,index] > 0.0 and not (index in neighbouring_indices) and dists[i,index] < dists_avg[i] :
                indices.append(index)

            dists_diff_sign_diff[i,index] = -5

        shortest_dist = 1e5
        for j in range(len(indices)):
            temp_dist = dists[i, (indices[j]-1)]
            if temp_dist < shortest_dist:
                shortest_dist = temp_dist
                matching_pt_index = (indices[j]-1)

        if matching_pt_index is not None:
            mid_point = (contour[matching_pt_index,:]+contour[i,:])/2
            tot_dist = 0
            for k in range(neighbouring_indices.shape[0]):
                pt_b = contour[neighbouring_indices[k],:]
                dist = np.linalg.norm(mid_point-pt_b)
                if dist < dists[i, matching_pt_index]/2 :
                    matching_pt_index=None
                    break
                tot_dist +=dist
            avg_dist = tot_dist/neighbouring_indices.shape[0]

            if matching_pt_index is not None and avg_dist < dists[i, matching_pt_index]/2 :
                matching_pt_index=None

        if matching_pt_index is not None:
            beam_sliced[i,0:2] = contour[i,:]
            beam_sliced[i,2:4] = contour[matching_pt_index,:]
            beam_sliced[i,4:6] = (contour[matching_pt_index,:]+contour[i,:])/2
            beam_sliced[i,6] = 180/np.pi*np.arctan((beam_sliced[i,3]-beam_sliced[i,1])/(beam_sliced[i,2]-beam_sliced[i,0]))
            beam_sliced[i,7] = dists[i, matching_pt_index]

    return beam_sliced

def process_frame(args, frame, shape_name):

    frame_gray=frame
    if len(frame.shape)==3:
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


    ret,thresh2 = cv2.threshold(frame_gray,210,255,cv2.THRESH_BINARY_INV)
    # thresholded to get the morphology
    blur = cv2.GaussianBlur(thresh2,(5,5),0)
    ret4,th4 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    blur = cv2.GaussianBlur(th4,(5,5),0)
    ret4,th4 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    blur = cv2.GaussianBlur(th4,(5,5),0)
    ret4,th4 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    frame_thresh = th4


    # do coupleof mor times thresholding, dilation and erosion to get rid of nay noise left
    kernel = np.ones((5,5),np.uint8)
    th4_dilated = cv2.dilate(th4,kernel,iterations = 1)

    blur = cv2.GaussianBlur(th4_dilated,(5,5),0)
    th4_eroded = cv2.erode(blur,kernel,iterations = 1)
    blur = cv2.GaussianBlur(th4_eroded,(5,5),0)
    kernel = np.ones((5,5),np.uint8)
    th4_dilated = cv2.dilate(blur,kernel,iterations = 1)

    blur = cv2.GaussianBlur(th4_dilated,(5,5),0)
    th4_eroded = cv2.erode(blur,kernel,iterations = 1)

    ret4,th4_dilated = cv2.threshold(th4_eroded,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Define a kernel size
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Apply morphological operations
    opened_image = cv2.morphologyEx(th4_dilated, cv2.MORPH_OPEN, kernel)
    closed_image = cv2.morphologyEx(opened_image, cv2.MORPH_CLOSE, kernel)


    frame_processed= closed_image

    if args.debug:
        file_path = args.path_2save + "/"  + shape_name + "_frame_frame_th4.jpg"
        cv2.imwrite(file_path,th4)

        file_path = args.path_2save + "/"  + shape_name + "_frame_frame_th4_thresh2.jpg"
        cv2.imwrite(file_path,thresh2)

        file_path = args.path_2save + "/"  + shape_name + "_frame_frame_frame_processed.jpg"
        cv2.imwrite(file_path,frame_processed)

    return frame_processed

def detect_robot_profile(args, frame, frame_processed, shape_name):


    # Apply skeletonization
    skeleton = skeletonize(frame_processed)

    # Convert skeleton to uint8 format
    skeleton = img_as_ubyte(skeleton)

    # Extract edge points from the skeleton
    points = np.argwhere(skeleton > 0)

    points = points[~np.isnan(points).any(axis=1), :]
    points = np.unique(points, axis=0)


    if args.debug:
        file_path = args.path_2save + "/"  + shape_name + "_frame_frame_frame_skeleton.jpg"
        cv2.imwrite(file_path,skeleton)


    beam_profile = points.copy()

    ref_index = np.argmin(beam_profile[:,1])


    # wrt init position
    ref_point_wrt_original = beam_profile[ref_index,:]
    beam_profile = beam_profile[:] - ref_point_wrt_original


    # sort them out
    dists_all = np.ones((beam_profile.shape[0],beam_profile.shape[0]))*99999
    dists = np.zeros((beam_profile.shape[0],1))+99999
    for i in range(beam_profile.shape[0]):
        dists[i] = (np.linalg.norm(beam_profile[i,:]))
    beam_profile = beam_profile[np.argsort(dists[:,0]),:]

    # get the distances among the points at the counters
    for i in range(beam_profile.shape[0]):
        point_a = beam_profile[i,:]
        for j in range(beam_profile.shape[0]):
            if i == j:
                continue
            point_b = beam_profile[j,:]
            dist = np.linalg.norm(point_a-point_b)
            dists_all[i,j] = dist

    shortest_path_idxs = [0]
    path_length = []


    for i in range(beam_profile.shape[0]-1):

        this_pt_idx = shortest_path_idxs[-1]
        next_pt_idx = np.argmin(dists_all[this_pt_idx,:])
        shortest_path_idxs.append(next_pt_idx)

        path_length.append(dists_all[this_pt_idx, next_pt_idx])

        dists_all[:, this_pt_idx] = 99999
        dists_all[this_pt_idx, next_pt_idx] = 99999

    shortest_path_idxs = np.array(shortest_path_idxs)
    beam_profile_sorted = beam_profile[shortest_path_idxs,:]

    idxs=detect_sudden_changes(path_length)
    if not idxs.shape[0] == 0:
        beam_profile_sorted = beam_profile_sorted[0:idxs[0]]


    return beam_profile_sorted, path_length, ref_point_wrt_original

def interpolate_robot_profile(beam_profile_sorted, path_length, profile_div_N):
    beam_profile_positions = beam_profile_sorted.copy()
    beam_length = 0.
    abs_length = np.zeros((beam_profile_positions.shape[0],))

    for i in range(beam_profile_positions.shape[0]):
        if not i == 0:
            beam_length = beam_length + path_length[i-1]
            abs_length[i] = beam_length.copy()

    dist_steps = np.linspace(0,abs_length[-1], profile_div_N)
    xn = np.interp(dist_steps, abs_length, beam_profile_positions[:,1])
    yn = np.interp(dist_steps, abs_length, beam_profile_positions[:,0])

    beam_profile_interp = np.column_stack((xn,yn))

    return beam_profile_interp

def draw_results(args, shape_name, frame, frame_processed, beam_profile_interp, ref_point_wrt_original, file_path=None):
    fig, axes = plt.subplots(1, 2, figsize=(8, 8), sharex=False, sharey=False)
    ax = axes.ravel()

    ax[0].imshow(frame, cmap=plt.cm.gray)
    ax[0].set_title('Original')
    ax[0].axis('off')


    ax[1].imshow(frame_processed, cmap=plt.cm.gray)
    ax[1].scatter(beam_profile_interp[:,0]+ref_point_wrt_original[1], beam_profile_interp[:,1]+ref_point_wrt_original[0], c="red", s = 1)

    ax[1].set_title("Detected")
    ax[1].axis('off')

    fig.tight_layout()
    if file_path is None:
        file_path = args.path_2save + "/"  + shape_name + "_shape_processed.jpg"

    plt.savefig(file_path, dpi=300)
    plt.close()

    if args.debug:
        point_sizes = np.linspace(0.5, 15, beam_profile_interp.shape[0])


        fig, axes = plt.subplots(1, 2, figsize=(8, 8), sharex=False, sharey=False)
        ax = axes.ravel()

        ax[0].imshow(frame, cmap=plt.cm.gray)
        ax[0].set_title('Original')
        ax[0].axis('off')


        ax[1].imshow(frame_processed, cmap=plt.cm.gray)
        ax[1].scatter(beam_profile_interp[:,0]+ref_point_wrt_original[1], beam_profile_interp[:,1]+ref_point_wrt_original[0], c="red", s = point_sizes)

        ax[1].set_title("Detected")
        ax[1].axis('off')

        fig.tight_layout()
        file_path = args.path_2save + "/"  + shape_name + "_shape_processed_debug.jpg"

        plt.savefig(file_path, dpi=300)
        plt.close()

def smooth_cartesian_points(args, points, window_size, poly_order):

    from scipy.signal import savgol_filter

    def savitzky_golay(data, window_size, poly_order):
        return savgol_filter(data, window_size, poly_order)

    def smooth_cartesian_points_savgol(x, y, window_size, poly_order):
        smoothed_x = savitzky_golay(x, window_size, poly_order)
        smoothed_y = savitzky_golay(y, window_size, poly_order)
        return smoothed_x, smoothed_y

    x = points[:,0]
    y = points[:,1]
    smoothed_x, smoothed_y = smooth_cartesian_points_savgol(x, y, window_size, poly_order)

    points_smoothned = np.transpose(np.vstack((np.transpose(smoothed_x), np.transpose(smoothed_y))))

    return points_smoothned


def resize_frame(frame, target_width):
    # Get the original dimensions
    original_height, original_width = frame.shape[:2]

    # Calculate the aspect ratio
    aspect_ratio = original_height / original_width

    # Calculate the new height based on the aspect ratio
    new_height = int(target_width * aspect_ratio)

    # Resize the frame
    resized_frame = cv2.resize(frame, (target_width, new_height))

    return resized_frame



def get_shape_profile_from_frame(args, frame_path=None, frame=None, debug=None, profile_div_N = 100, edge_length = None, shape_length = None):
    """
    input:
    path to the frame or frame itself
    node number
    shape length for scaling calculations

    output:
    returns the robot profile positions
    scale
    """

    # get the frame
    if frame is None:
        if frame_path is None:
            raise NotImplementedError("you need to provide either frame or a frame path")
        else:
            frame_bgr = cv2.imread(frame_path)
            frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            frame_resized = resize_frame(frame, args.target_width) # ensuring all the frames are the same width
            frame = frame_resized

            shape_name = frame_path.split("/")[-1].split(".")[0]
            shape_length = int(frame_path.split("/")[-1].split(".")[0].split("_")[-1].split("mm")[0])


    # process the frame
    frame_processed = process_frame(args, frame, shape_name)


    # detect the robot
    robot_profile, robot_length, ref_point_wrt_original = detect_robot_profile(args, frame, frame_processed, shape_name)


    # get the scale of the robot
    robot_length_pixels = np.sum(np.array(robot_length))
    scale_mm = (robot_length_pixels)/shape_length


    # interpolate among the points to get equidistant points

    if profile_div_N < 0:
        profile_div_N = int(shape_length/edge_length)
        print(profile_div_N)

        args.window_size =  np.clip(int(profile_div_N/100)+1, 2, None)

        print(args.window_size )
        print(robot_profile.shape[0])

    window_size = int(profile_div_N/20)
    # print (window_size)
    window_size =  np.clip(window_size, 5, None)
    poly_order = args.poly_order

    robot_profile = smooth_cartesian_points(args, robot_profile, window_size, poly_order)


    robot_profile_interp = interpolate_robot_profile(robot_profile, robot_length, profile_div_N)

    window_size = args.window_size
    poly_order = args.poly_order

    robot_profile_interp = smooth_cartesian_points(args, robot_profile_interp, window_size, poly_order)

    # draw the original, and detected and interpolated
    file_path = args.path_2save + "/"  + shape_name + "_shape_processed_final.jpg"
    draw_results(args, shape_name, frame, frame_processed, robot_profile_interp, ref_point_wrt_original, file_path)

    scale = dict(length = scale_mm)

    return robot_profile_interp, scale, shape_length, shape_name



" shape complexity score calculation "

def angle_between_vectors(a, b):
    # Ensure the vectors are numpy arrays
    a = np.array(a)
    b = np.array(b)

    # Calculate the dot product
    dot_product = np.dot(a, b)

    # Calculate the magnitudes (norms) of the vectors
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Calculate the cosine of the angle
    cos_theta = dot_product / (norm_a * norm_b)

    # Clip the value to the range [-1, 1] to avoid NaN from arccos due to the Floating-point Precision Errors
    if cos_theta>1 or cos_theta< -1:
        cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # Use arccos to get the angle in radians
    angle_radians = np.arccos(cos_theta)

    # Optional: convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)

    return angle_radians, angle_degrees

def get_angles_differences(shape_positions):

    # shape_positions = np.vstack((np.array((-1, 0)), shape_positions))

    angle_dif = np.zeros(shape_positions.shape[0])
    angle = np.zeros(shape_positions.shape[0])
    for _i in range (shape_positions.shape[0]-2):
        previous_node_pos = shape_positions[_i]
        this_node_pos = shape_positions[_i+1]
        next_node_pos = shape_positions[_i+2]

        this_vector = this_node_pos - previous_node_pos
        next_vector = next_node_pos - this_node_pos

        angle_radians, angle_degrees = angle_between_vectors(this_vector, next_vector)

        angle_dif[_i+1] = angle_degrees

    return angle_dif

def calculate_shape_complexity_score(args, shape_positions, shape_length):

    angle_dif = get_angles_differences(shape_positions)

    complexity_score = np.sum(np.abs(angle_dif))
    complexity_score_normalized = complexity_score/shape_length

    return angle_dif, complexity_score, complexity_score_normalized

"utility function"
def create_folder_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def detect_sudden_changes(array):
    """
    Detect indices where there is a sudden change in values in the array.

    Parameters:
    array (np.array): Input array of values.
    threshold (float): Threshold value for detecting sudden changes.

    Returns:
    list: List of indices where the sudden change occurs.
    """
    # Calculate the differences between consecutive elements
    differences = np.diff(array)
    threshold = np.mean(array)*2

    # Find indices where the absolute difference exceeds the threshold
    sudden_change_indices = np.where(np.abs(differences) > threshold)[0]

    # Return the indices (we add 1 because np.diff reduces the array size by 1)
    return sudden_change_indices + 1


def main(args):

    # get the shapes
    shapes_files = glob(args.path_shape2calculate + "/*")


    results = dict(shape_name = [],
                   robot_profile_interp_mm = [],
                   angle_dif = [],
                   complexity_score = [],
                   complexity_score_normalized = [],
                   shape_length = []
                   )

    # get robot profle positions
    for shape_file in shapes_files:
        start_time_eval = time.time()

        print("Working on shape: ", shape_file)

        robot_profile_interp, scale_dict, shape_length, shape_filename = get_shape_profile_from_frame(args, frame_path=shape_file, frame=None, debug=args.debug, profile_div_N=args.node_number, edge_length = args.edge_length)
        robot_profile_interp_mm = robot_profile_interp*scale_dict["length"]

        if args.calculate_shape_complexity_score:
            angle_dif, complexity_score, complexity_score_normalized = calculate_shape_complexity_score(args, robot_profile_interp_mm, shape_length)

        print(complexity_score)
        print(complexity_score_normalized)
        print(scale_dict["length"])
        print("**")

        # collect the results
        results["shape_name"].append(shape_filename)
        results["robot_profile_interp_mm"].append(robot_profile_interp_mm)
        results["angle_dif"].append(angle_dif)
        results["complexity_score"].append(complexity_score)
        results["complexity_score_normalized"].append(complexity_score_normalized)
        results["shape_length"].append(shape_length)

        end_time_eval = time.time()
        time_passed = end_time_eval - start_time_eval
        print("Robot evaluation is completed")
        print("it took: ", time_passed)

    # save on an excel file
    data = {
        'Shape file': results["shape_name"],
        'Complexity score': results["complexity_score"],
        'Shape length': results["shape_length"],
        'Complexity score normalized': results["complexity_score_normalized"]
    }

    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file
    file_path = args.path_2save + "/complexity_results.xlsx"
    df.to_excel(file_path, index=False)

    #pickle the results as well
    file_path = args.path_2save + "/complexity_results_raw.pickle"
    with open(file_path, "wb") as handle:
        pickle.dump(results, handle)


def draw_final_Result_bar_plot(args):

    # results
    # Dataset:
    SC = [42.2429549123523,
            29.9925746208284,
            39.9410661727684,
            25.8298450280913,
            22.9592299972691,
            29.1696414632232,
            20.8164464096434,
            3.58483240900652,
            2.42892277183337,
            2.88611224888015
            ]
    Fig_name= ["Fig. 1G",
               "Fig. 2A",
               "Fig. 2B",
               "Fig. 2C",
               "Fig. S7A",
               "Fig. S7B",
               "G.Z.Lum et al.",
               "S. Wu et al.",
               "L. Wang et al.",
               "P. Lloyd et al."
                ]


    data = {'Fig_name': Fig_name,
            'SC': SC
            }

    colors = sns.color_palette("deep")
    hex_codes = colors.as_hex()

    # Define a color map for each data point
    color_map = {"Fig. 1G": hex_codes[1] ,
                "Fig. 2A": hex_codes[1],
                "Fig. 2B": hex_codes[1],
                "Fig. 2C": hex_codes[1],
                "Fig. S7A": hex_codes[1],
                "Fig. S7B": hex_codes[1],
                "G.Z.Lum et al.": hex_codes[2],
                "S. Wu et al.": hex_codes[5],
                "L. Wang et al.": hex_codes[6],
                "P. Lloyd et al.": hex_codes[7]
                }


    _df_results= pd.DataFrame(data)

    # Map the colors to the DataFrame
    _df_results['Color'] = _df_results['Fig_name'].map(color_map)

    # Create a palette using the color column
    palette = _df_results.set_index('Fig_name')['Color'].to_dict()


    # plot settings
    dpi_value = 1200
    plt.rcParams['font.size'] = 14
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.tick_params(top=False, bottom=True, left=True, right=False,
                    labelleft=True, labelbottom=True)

    path_to_save = args.path_2save + "/final_bar_plot.png"



    # boxplot
    sns_plot = sns.barplot(x="Fig_name", y="SC",  data=_df_results, palette=palette)
    # plot_errorbars("sd")

    # plt.locator_params(axis="x", nbins=6)
    plt.xticks(rotation=45, ha='center', va='center', y=-0.12)
    plt.tick_params(axis='both', which='major', labelsize=14)
    sns_plot.set_ylim((0, 105/100*np.max(_df_results).SC))
    plt.locator_params(axis="y", nbins=4)
    # sns_plot.set_xlabel('Generations', fontsize =16, fontweight='bold')
    sns_plot.set_ylabel('Shape complexity normalized', fontsize =16, fontweight='bold')
    sns_plot.set(xlabel=None)

    sns_fig = sns_plot.get_figure()
    sns_fig.savefig(path_to_save, bbox_inches='tight', dpi=dpi_value)
    plt.close()


if __name__ == "__main__":
    code_start_time=time.time()
    "Parse the arguments"
    args = parse_arguments()

    # args.debug = 1

    create_folder_if_not_exists(args.path_2save)


    draw_final_Result_bar_plot(args)
    main(args)

    print("\n\n\n\n\n")
    print("DONE\n")
    code_end_time=time.time()-code_start_time
    print("Completed in: ", code_end_time)
