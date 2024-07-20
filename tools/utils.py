import matplotlib
matplotlib.use('Agg')
import numpy as np
import itertools
import re
import scipy.ndimage as ndimage
import math
import subprocess as sub
import hashlib

import matplotlib.pyplot as plt
import matplotlib.image
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import copy

import cv2 as cv
from skimage.morphology import medial_axis, skeletonize
from sklearn.neighbors import NearestNeighbors
import networkx as nx
from numpy import linalg as LA

plt.rcParams['savefig.facecolor'] = 'white'

""" Population manipulations """
def add_pop2pop(pop2add, popOriginal):
    pop_temp = popOriginal
    population = pop2add
    for i in range(len(pop_temp)):
        population.append(pop_temp[i])
    return population

def cuboid_data(o, size=(1,1,1)):
    X = [[[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
         [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
         [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
         [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
         [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
         [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]]
    X = np.array(X).astype(float)
    for i in range(3):
        X[:,:,i] *= size[i]
    X += np.array(o)
    return X

def plotCubeAt(positions,sizes=None,colors=None, **kwargs):
    if not isinstance(colors,(list,np.ndarray)): colors=["C0"]*len(positions)
    if not isinstance(sizes,(list,np.ndarray)): sizes=[(1,1,1)]*len(positions)
    g = []
    for p,s,c in zip(positions,sizes,colors):
        g.append( cuboid_data(p, size=s) )
    return Poly3DCollection(np.concatenate(g),
                            facecolors=np.repeat(colors,6, axis=0), **kwargs)

def visualizeVoxels(args, positions):
    # visualizing the 3D structure with voxels given the positions
    # check matplotlib voxelSize
    # https://matplotlib.org/3.2.1/api/_as_gen/mpl_toolkits.mplot3d.axes3d.Axes3D.html#mpl_toolkits.mplot3d.axes3d.Axes3D.voxels

    voxels = positions[:,1:4]
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    colors = 'red'
    ax.voxels(voxels, facecolors=colors, edgecolor='k')


    figureFileName = "helloWorld.png"
    plt.savefig(figureFileName)


# Functions from @Mateen Ulhaq and @karlo
def set_axes_equal(ax: plt.Axes):
    """Set 3D plot axes to equal scale.

    Make axes of 3D plot have equal scale so that spheres appear as
    spheres and cubes as cubes.  Required since `ax.axis('equal')`
    and `ax.set_aspect('equal')` don't work on 3D.
    """
    limits = np.array([
        ax.get_xlim3d(),
        ax.get_ylim3d(),
        ax.get_zlim3d(),
    ])
    origin = np.mean(limits, axis=1)
    radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
    _set_axes_radius(ax, origin, radius)

def _set_axes_radius(ax, origin, radius):
    x, y, z = origin
    ax.set_xlim3d([x - radius, x + radius])
    ax.set_ylim3d([y - radius, y + radius])
    ax.set_zlim3d([z - radius, z + radius])

def rotate_via_numpy(xy, radians):
    """Use numpy to build a rotation matrix and take the dot product."""
    x, y = xy
    c, s = np.cos(radians), np.sin(radians)
    j = np.matrix([[c, s], [-s, c]])
    m = np.dot(j, [x, y])

    return float(m.T[0]), float(m.T[1])

def rotate3D_via_numpy(xyz, radians):
    """Use numpy to build a rotation matrix and take the dot product."""
    x, y, z = xyz
    c, s = np.cos(radians), np.sin(radians)
    j = np.matrix([[1, 0, 0], [0, c, s], [0, -s, c]])
    m = np.dot(j, [x, y, z])

    return float(m.T[0]), float(m.T[1]), float(m.T[2])

def rotate_origin_only(xy, radians):
    """Only rotate a point around the origin (0, 0)."""
    x, y = xy
    xx = x * math.cos(radians) + y * math.sin(radians)
    yy = -x * math.sin(radians) + y * math.cos(radians)

    return xx, yy

def rotate_around_point_lowperf(point, radians, origin=(0, 0)):
    """Rotate a point around a given point.

    I call this the "low performance" version since it's recalculating
    the same values more than once [cos(radians), sin(radians), x-ox, y-oy).
    It's more readable than the next function, though.
    """
    x, y = point
    ox, oy = origin

    qx = ox + math.cos(radians) * (x - ox) + math.sin(radians) * (y - oy)
    qy = oy + -math.sin(radians) * (x - ox) + math.cos(radians) * (y - oy)

    return qx, qy

def rotate_around_point_highperf(xy, radians, origin=(0, 0)):
    """Rotate a point around a given point.

    I call this the "high performance" version since we're caching some
    values that are needed >1 time. It's less readable than the previous
    function but it's faster.
    """
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

    return qx, qy


""" Visualization """
def drawMagDirSpace(args, filePath2save):
    # visualizes the possible magnetization directions within the segment of the material
    Msegments = np.zeros((args.discrete_M_max,3))

    if args.mag_dim =="2D":
        for i in range(args.discrete_M_max):
            i = i+1
            Mphi = (i-1)*args.discrete_angle_rad
            Msegments[i-1] = np.array([math.cos(Mphi), 0., math.sin(Mphi)])

        fig, ax = plt.subplots(figsize=(20,20))

        ax.set_title('sss')
        X = np.zeros((args.discrete_M_max,1))
        Y = np.zeros((args.discrete_M_max,1))
        U = Msegments[:,0]
        V = Msegments[:,2]
        Q = ax.quiver(X, Y, U, V, linewidth = 20, scale = 3)
        ax.set_xlim(-1.2,1.2)
        ax.set_ylim(-1.2,1.2)

        # Hide grid lines
        ax.grid(False)

        # Hide axes ticks
        ax.set_xticks([])
        ax.set_yticks([])

    if args.mag_dim =="3D":
        for i in range(args.discrete_M_max):
            i = i+1
            if i == args.discrete_M_max:
                Mtheta = 0.
                Mphi = 0.
            if i == (args.discrete_M_max-1):
                Mtheta = 0.
                Mphi = math.pi
            if i < (args.discrete_M_max-1):
                sliceNum = (i-1)//(args.discrete_angle_num-1)
                angleNum = (i-1)%(args.discrete_angle_num-1) + 1

                Mtheta = sliceNum*2*math.pi/args.slice_num
                Mphi = angleNum*args.discrete_angle_rad

            Msegments[i-1] = np.array([math.cos(Mtheta) * math.sin(Mphi), math.sin(Mtheta) * math.sin(Mphi), math.cos(Mphi)])

        fig = plt.figure(figsize=(20,20))
        ax = fig.add_subplot(111, projection='3d')

        ax.set_title('sss')
        X = np.zeros((args.discrete_M_max,1))
        Y = np.zeros((args.discrete_M_max,1))
        Z = np.zeros((args.discrete_M_max,1))
        U = Msegments[:,0]
        V = Msegments[:,1]
        W = Msegments[:,2]
        Q = ax.quiver(X, Y, Z, U, V, W, length=1, linewidth = 10, normalize=True)
        ax.set_xlim(-1.2,1.2)
        ax.set_ylim(-1.2,1.2)
        ax.set_zlim(-1.2,1.2)

        # Hide grid lines
        ax.grid(False)

        # Hide axes ticks
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

    # get the figures
    dpi_setting = 50 if args.debug else 300
    figureFileName = filePath2save + "2D_possibleMdirections.png"
    plt.savefig(figureFileName, dpi=dpi_setting)

    if args.mag_dim =="3D":
        ax.view_init(elev=30., azim=90)
        figureFileName = filePath2save + "3D_P_M_dir_El30_Az90.png"
        plt.savefig(figureFileName, dpi=300)
        ax.view_init(elev=30., azim=20)
        figureFileName = filePath2save + "3D_P_M_dir_El30_Az20.png"
        plt.savefig(figureFileName, dpi=300)
        ax.view_init(elev=30., azim=30)
        figureFileName = filePath2save + "3D_P_M_dir_El30_Az30.png"
        plt.savefig(figureFileName, dpi=300)
        ax.view_init(elev=20., azim=30)
        figureFileName = filePath2save + "3D_P_M_dir_El20_Az30.png"
        plt.savefig(figureFileName, dpi=300)

    plt.close()

def drawMprofile(args, indEA, savefile = None):

    Msegments = np.zeros((args.segmentNum, 3))
    for i in range(args.segmentNum):
        if indEA[i] == 0:
            Msegments[i] = np.array([0., 0., 0.])
        else:
            if args.mag_dim == "2D":
                Mphi = (indEA[i]-1)*args.discrete_angle_rad
                Msegments[i] = np.array([math.cos(Mphi), 0., math.sin(Mphi)])
            if args.mag_dim == "3D":
                # https://en.wikipedia.org/wiki/Spherical_coordinate_system
                if indEA[i] == args.discrete_M_max:
                    Mtheta = 0.
                    Mphi = 0.
                if indEA[i] == (args.discrete_M_max-1):
                    Mtheta = 0.
                    Mphi =  math.pi
                if indEA[i] < (args.discrete_M_max-1):
                    sliceNum = (indEA[i]-1)//(args.discrete_angle_num-1)
                    angleNum = (indEA[i]-1)%(args.discrete_angle_num-1) + 1

                    Mtheta = sliceNum*2*math.pi/args.slice_num
                    Mphi = angleNum*args.discrete_angle_rad

                Msegments[i] = np.array([math.cos(Mtheta) * math.sin(Mphi), math.sin(Mtheta) * math.sin(Mphi), math.cos(Mphi)])


    print(Msegments)
    X = np.zeros((args.segmentNum,1))
    Y = np.zeros((args.segmentNum,1))
    Z = np.zeros((args.segmentNum,1))
    U = np.zeros((args.segmentNum,1))
    V = np.zeros((args.segmentNum,1))
    W = np.zeros((args.segmentNum,1))

    for i in range(args.segmentNum):
        # shift the base X for each segment arrow
        X[i] = i

        # shift the arrow end X for each segment arrow
        U[i]= Msegments[i,0]
        V[i]= Msegments[i,1]
        W[i] = Msegments[i,2]

    # x-y plane
    fig, ax = plt.subplots(figsize=(20,20))


    ax.set_title('X-Y plane, top view')
    Q = ax.quiver(X, Y, U, V, linewidth = 20, pivot= 'middle')

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.set_aspect('equal')
    if savefile ==None:
        figureFileName = "trial_drawing/Mprofile_topview.png"
    else:
        figureFileName = savefile + "Mprofile_topview.png"

    dpi_setting = 50 if args.debug else 300

    plt.savefig(figureFileName, dpi=dpi_setting)

    plt.close()

    # x-z plane
    fig, ax = plt.subplots(figsize=(20,20))
    # ax = fig.add_subplot(111, projection='2d')

    ax.set_title('X-Y plane, top view')
    Q = ax.quiver(X, Z, U, W, linewidth = 20, pivot= 'middle')

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.set_aspect('equal')
    figureFileName = "trial_drawing/Mprofile_sideview.png"
    plt.savefig(figureFileName, dpi=dpi_setting)

    plt.close()


    fig, (ax1,ax2) = plt.subplots(2,1,figsize=(20,5))

    Q = ax1.quiver(X, Y, U, V, linewidth = 20, pivot= 'middle')


    # Hide grid lines
    ax1.grid(False)

    # Hide axes ticks
    ax1.set_xticks([])
    ax1.set_yticks([])

    Q = ax2.quiver(X, Z, U, W, linewidth = 20,  pivot= 'middle')

    # Hide grid lines
    ax2.grid(False)

    # Hide axes ticks
    ax2.set_xticks([])
    ax2.set_yticks([])
    if savefile == None:
        figureFileName = "trial_drawing/Mprofile_topNSidewotitle.png"
    else:
        figureFileName = savefile + "Mprofile_topNSidewotitle.png"

    plt.savefig(figureFileName, dpi=300)

    ax1.set_title('X-Y plane, top view', fontsize=20)
    ax2.set_title('X-Z plane, side view', fontsize=20)

    if savefile == None:
        figureFileName = "trial_drawing/Mprofile_topNSide_w_title.png"
    else:
        figureFileName = savefile + "Mprofile_topNSide_w_title.png"
    # figureFileName = "trial_drawing/Mprofile_topNSide_w_title.png"
    plt.savefig(figureFileName, dpi=300)
    plt.close()

    #
    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111, projection='3d')

    ax.set_title('M profile')

    Q = ax.quiver(X, Y, Z, U, V, W, length=1, linewidth = 10, normalize=True)

    # Hide grid lines
    ax.grid(False)
    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    figureFileName = "trial_drawing/Mprofile.png"
    plt.savefig(figureFileName, dpi=300)
    plt.close()

def drawInitShape(args, materialMatrix, filePath2save, highQuality = 0):
    """Draw the initial morphology of the structure utilizing openCV"""

    dpiValue = 50 if not highQuality else 300

    if not materialMatrix.shape[2]>1:  # means 2D single layer sheet structure
        # convert to black and white image
        materialMatrix = materialMatrix.astype(int)
        materialMatrix = materialMatrix[:,:,0]
        displayMatrix = np.pad(materialMatrix, ((1, 1), (1, 1)), 'constant', constant_values=(0,))

        plt.matshow(displayMatrix, cmap = "binary",  vmin=0, vmax=1)
        plt.axis('off')
        plt.savefig(filePath2save+"2.jpg", bbox_inches='tight',pad_inches = 0, dpi=dpiValue)
        plt.close()

    elif materialMatrix.shape[2]>1:
        if materialMatrix.shape[0]>1 and materialMatrix.shape[1]>1:  # means 3D structure
            raise NotImplementedError
        if materialMatrix.shape[0] == 1: # means fixed from top
            # convert to black and white image
            materialMatrix = materialMatrix.astype(int)
            materialMatrix = materialMatrix[0,:]
            displayMatrix = np.pad(materialMatrix, ((1, 1), (1, 1)), 'constant', constant_values=(0,))

            plt.matshow(displayMatrix, cmap = "binary",  vmin=0, vmax=1)
            plt.axis('off')
            plt.savefig(filePath2save+"2.png", bbox_inches='tight',pad_inches = 0, dpi=dpiValue)
            plt.close()

def drawInitShapeRGB(args, design_parameters, filePath2save, highQuality = 1):
    """Draw the initial morphology of the structure utilizing openCV"""

    dpiValue = 600 if not highQuality else 2400
    materialMatrix = design_parameters["material"]
    Mtheta = design_parameters["Mtheta"]
    Mphi = design_parameters["Mphi"]


    if not materialMatrix.shape[2]>1:  # means 2D single layer sheet structure

        im = np.zeros((materialMatrix.shape[0],materialMatrix.shape[1],4))

        #normalize the desin params
        im[:,:,0]= (materialMatrix[:,:,0]+0)*1/1
        im[:,:,1]= (Mtheta[:,:,0]+math.pi)*1/(2.*math.pi)
        im[:,:,2]= (Mphi[:,:,0]+0)*1/(math.pi)

        # alpha value for the empty voxels, set it to transperant
        im[:,:,3]= (materialMatrix[:,:,0]+0)*1/1
        im = np.pad(im, ((1, 1), (1, 1),(0, 0)), 'constant', constant_values =1)

        plt.imsave(filePath2save+".jpg", im,  dpi=dpiValue)
        plt.close()


    elif materialMatrix.shape[2]>1:       # means 3D structure
        if materialMatrix.shape[0]>1 and materialMatrix.shape[1]>1:  # means 3D structure
            raise NotImplementedError
        if materialMatrix.shape[0] == 1: # means fixed from top
            im = np.zeros((materialMatrix.shape[2],materialMatrix.shape[1],4))

            matMax = np.transpose(materialMatrix[0,:])
            #normalize the desin params
            im[:,:,0]= (matMax+0)*1/1
            im[:,:,1]= (Mtheta[:,:,0]+math.pi)*1/(2.*math.pi)
            im[:,:,2]= (Mphi[:,:,0]+0)*1/(math.pi)

            # alpha value for the empty voxels, set it to transperant
            im[:,:,3]= (matMax+0)*1/1

            im = np.pad(im, ((1, 1), (1, 1),(0, 0)), 'constant', constant_values =1)

            plt.imsave(filePath2save+".jpg", im,  dpi=dpiValue)
            plt.close()

def draw3Dshape(args, positions, voxelStrainEnergy, filePath2save, highQuality = 0):

    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111, projection='3d')

    if max(voxelStrainEnergy) ==0 :
        cMap = voxelStrainEnergy+0.1
    else:
        cMap = voxelStrainEnergy/max(voxelStrainEnergy)

    ax.scatter(positions[:,0], positions[:,1], positions[:,2], c=np.squeeze(cMap), cmap = 'plasma',  marker= "o", s=200, alpha = 1)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    set_axes_equal(ax) # IMPORTANT - this is also required

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

    dpiValue = 25
    if highQuality:
        dpiValue = 300

    if (filePath2save[-4]) =='.':
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save, dpi=dpiValue)
    else:
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save+"isometric.png", dpi=dpiValue)
        ax.view_init(elev=60., azim=300)
        plt.savefig(filePath2save+"isometric2.png", dpi=dpiValue)
        ax.view_init(elev=0., azim=270)
        plt.savefig(filePath2save+"sideXZ.png", dpi=dpiValue)
        ax.view_init(elev=0., azim=90)
        plt.savefig(filePath2save+"side2XZ.png", dpi=dpiValue)
        ax.view_init(elev=90., azim=180)
        plt.savefig(filePath2save+"topXY.png", dpi=dpiValue)
        ax.view_init(elev=0., azim=180)
        plt.savefig(filePath2save+"topYZ.png", dpi=dpiValue)

    plt.close()

def draw3Dshapev2(positions, voxelStrainEnergy, filePath2save, highQuality = 0):

    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111, projection='3d')

    cMap = voxelStrainEnergy/max(voxelStrainEnergy)

    ax.scatter(positions[:,0], positions[:,1], positions[:,2], c=cMap, cmap = 'plasma',  marker= "o", s=200, alpha = 1)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    # plt.axis('square')
    ax.set_box_aspect([1,1,1]) # IMPORTANT - this is the new, key line
    set_axes_equal(ax) # IMPORTANT - this is also required

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # Hide axes
    ax.axis('off')

    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

    dpiValue = 25
    if highQuality:
        dpiValue = 300

    if (filePath2save[-4]) =='.':
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save, dpi=dpiValue)
    else:
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save+"isometric.jpg", dpi=dpiValue)
        ax.view_init(elev=60., azim=300)
        plt.savefig(filePath2save+"isometric2.jpg", dpi=dpiValue)
        ax.view_init(elev=30., azim=315)
        plt.savefig(filePath2save+"isometric3.jpg", dpi=dpiValue)
        ax.view_init(elev=25., azim=315)
        plt.savefig(filePath2save+"isometric4.jpg", dpi=dpiValue)
        ax.view_init(elev=20., azim=315)
        plt.savefig(filePath2save+"isometric5.jpg", dpi=dpiValue)
        ax.view_init(elev=20., azim=330)
        plt.savefig(filePath2save+"isometric6.jpg", dpi=dpiValue)
        ax.view_init(elev=0., azim=270)
        plt.savefig(filePath2save+"sideXZ.jpg", dpi=dpiValue)
        ax.view_init(elev=0., azim=90)
        plt.savefig(filePath2save+"side2XZ.jpg", dpi=dpiValue)
        ax.view_init(elev=90., azim=270)
        plt.savefig(filePath2save+"topXY.jpg", dpi=dpiValue)
        ax.view_init(elev=0., azim=0)
        plt.savefig(filePath2save+"frontYZ.jpg", dpi=dpiValue)

    plt.close()

def draw3Dshape_videoFrame(positions, voxelStrainEnergy, filePath2save, view_type, dpiValue = 50):

    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111, projection='3d')

    cMap = voxelStrainEnergy/max(voxelStrainEnergy)

    positions = np.vstack((positions, np.zeros((1,3))))
    cMap = np.vstack((cMap, np.zeros((1,1))))

    ax.scatter(positions[:,0], positions[:,1], positions[:,2], c=cMap, cmap = 'plasma',  marker= "o", s=200, alpha = 1)

    ax.set_box_aspect([1,1,1]) # IMPORTANT - this is the new, key line
    set_axes_equal(ax) # IMPORTANT - this is also required

    # Hide grid lines
    ax.grid(False)
    # Hide axes
    ax.axis('off')

    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

    frame_path = filePath2save+"_" + view_type+".jpg"
    if view_type == "sideXZ":
        ax.view_init(elev=0., azim=270)
        plt.savefig(frame_path, dpi=dpiValue)
    elif view_type == "isometric":
        ax.view_init(elev=30., azim=300)
        plt.savefig(frame_path, dpi=dpiValue)
    elif view_type == "topXY":
        ax.view_init(elev=90., azim=180)
        plt.savefig(frame_path, dpi=dpiValue)
    elif view_type == "frontYZ":
        ax.view_init(elev=0., azim=180)
        plt.savefig(frame_path, dpi=dpiValue)
    else:
        raise NotImplementedError

    plt.close()
    return frame_path

def draw3DshapeWOargs(positions, filePath2save, highQuality = 0):

    fig = plt.figure(figsize=(20,20))
    ax = fig.add_subplot(111, projection='3d')

    cMap = positions[:,0]/max(positions[:,0])
    distance = LA.norm(positions, axis=1)

    cMap = distance/max(distance)

    ax.scatter(positions[:,0], positions[:,1], positions[:,2], c=cMap, cmap = 'plasma',  marker= "o", s=200, alpha = 1)

    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    # plt.axis('square')
    ax.set_box_aspect([1,1,1]) # IMPORTANT - this is the new, key line
    set_axes_equal(ax) # IMPORTANT - this is also required

    # Hide grid lines
    ax.grid(False)

    # Hide axes ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 1.0))

    dpiValue = 50
    if highQuality:
        dpiValue = 300

    if (filePath2save[-4]) =='.':
        ax.view_init(elev=30., azim=300)
        plt.savefig(filePath2save, dpi=dpiValue)
    else:
        ax.view_init(elev=20., azim=250)
        plt.savefig(filePath2save+"isometric.jpg", dpi=dpiValue)
        ax.view_init(elev=20., azim=235)
        plt.savefig(filePath2save+"isometric2.jpg", dpi=dpiValue)
        ax.view_init(elev=20., azim=245)
        plt.savefig(filePath2save+"isometric3.jpg", dpi=dpiValue)
        ax.view_init(elev=20., azim=265)
        plt.savefig(filePath2save+"isometric4.jpg", dpi=dpiValue)
        ax.view_init(elev=0., azim=270)
        plt.savefig(filePath2save+"sideXZ.jpg", dpi=dpiValue)
        ax.view_init(elev=90., azim=180)
        plt.savefig(filePath2save+"topXY.jpg", dpi=dpiValue)
        ax.view_init(elev=0., azim=180)
        plt.savefig(filePath2save+"topYZ.jpg", dpi=dpiValue)

    # plt.show()
    plt.close()



def generateDesiredShape(args, shape_type, draw_3Dshape = 1):
    #  voxel num and sizes for the experimental side
    voxelNum = args.ind_size[0]
    voxelSize = args.lattice_dim
    beamLengthOrg = voxelSize * voxelNum*1e3
    numVox = args.ind_size[0]*args.ind_size[1]*args.ind_size[2]
    voxelStrainEnergy = np.ones((numVox, 1))


    # triangleWave  -- fig1
    if shape_type == 1:

        voxelNum = args.ind_size[0]
        beamLengthOrg = voxelSize * voxelNum*1e3

        # antenna points in space
        pts=np.array([[0, voxelSize/2.*1e3, 0],
                      [1, voxelSize/2.*1e3, -1],
                      [3, voxelSize/2.*1e3, 1],
                      [4, voxelSize/2.*1e3, 0]])

        num_of_equidistant = 20
        x=np.zeros((20*(pts.shape[0]-1)))
        y=np.zeros((20*(pts.shape[0]-1)))
        z=np.zeros((20*(pts.shape[0]-1)))

        for index in range(pts.shape[0]-1):
            x[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,0], pts[index+1,0], num_of_equidistant)
            y[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,1], pts[index+1,1], num_of_equidistant)
            z[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,2], pts[index+1,2], num_of_equidistant)


        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((x.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = voxelSize/2.*1e3*np.ones((voxelNum,))
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        xn = xn-xn[0]
        # yn = yn-yn[0]
        zn = zn-zn[0]

        voxelNums = np.linspace(0, args.ind_size[1]*args.ind_size[0]-1, args.ind_size[1]*args.ind_size[0])

        xa = []
        ya = []
        za = []
        for i in range(args.ind_size[1]):
            xa.append(xn)
            ya.append(yn+voxelSize*1e3*i)
            za.append(zn)
        xnFinal = np.concatenate((xa))
        ynFinal = np.concatenate((ya))
        znFinal = np.concatenate((za))

        if  args.isCPUenabled:
            xnFinal = 0.1 + xnFinal
            znFinal = 0.1 + znFinal

        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "TriangleWave_"
    
    # Heartbeat -- fig 2A
    if shape_type == 2:

        # make a helix in 3D
        t = np.linspace(0, 3*math.pi, 5*voxelNum)
        f = np.linspace(1.5, 1, 5*voxelNum)
        amp = np.linspace(0.4, 2, 5*voxelNum)

        tf = np.multiply(t,f)
        # amptf = np.multiply(amp, tf)

        x = t
        y = voxelSize/2.*1e3*np.ones((t.shape[0],))

        z = np.multiply(amp, np.sin(tf))
        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((t.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = voxelSize/2.*1e3*np.ones((voxelNum,))
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        voxelNums = np.linspace(0, args.ind_size[1]*args.ind_size[0]-1, args.ind_size[1]*args.ind_size[0])

        xa = []
        ya = []
        za = []
        for i in range(args.ind_size[1]):
            xa.append(xn)
            ya.append(yn+voxelSize*1e3*i)
            za.append(zn)
        xnFinal = np.concatenate((xa))
        ynFinal = np.concatenate((ya))
        znFinal = np.concatenate((za))

        if args.isCPUenabled:
            xnFinal = 0.1 + xnFinal
            znFinal = 0.1 + znFinal

        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "varyingSine"

    # Stepv2 -- fig 2B
    if shape_type == 3:

        # make a step function
        voxelRegion_num = voxelNum/5
        regionLen = voxelRegion_num * voxelSize

        y = voxelSize/2.*1e3*np.ones((voxelNum,))


        x = np.hstack((np.linspace(0, regionLen, int(voxelRegion_num)),
                       regionLen * np.ones(int(voxelRegion_num)),
                       np.linspace(regionLen, 2*regionLen, int(voxelRegion_num)),
                       2*regionLen * np.ones(int(voxelRegion_num)),
                       np.linspace(2*regionLen, 3*regionLen, int(voxelRegion_num))
                       ))

        z = np.hstack((np.zeros(int(voxelRegion_num)),
                       np.linspace(0, 1*regionLen, int(voxelRegion_num)),
                       regionLen * np.ones(int(voxelRegion_num)),
                       np.linspace(1*regionLen, 0*regionLen, int(voxelRegion_num)),
                       np.zeros(int(voxelRegion_num))
                       ))

        positions = np.vstack((x,y,z))

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((x.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = voxelSize/2.*1e3*np.ones((voxelNum,))
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        xn = xn-xn[0]
        # yn = yn-yn[0]
        zn = zn-zn[0]

        voxelNums = np.linspace(0, args.ind_size[1]*args.ind_size[0]-1, args.ind_size[1]*args.ind_size[0])

        xa = []
        ya = []
        za = []
        for i in range(args.ind_size[1]):
            xa.append(xn)
            ya.append(yn+voxelSize*1e3*i)
            za.append(zn)
        xnFinal = np.concatenate((xa))
        ynFinal = np.concatenate((ya))
        znFinal = np.concatenate((za))

        if args.isCPUenabled:
            xnFinal = 0.1 + xnFinal
            znFinal = 0.1 + znFinal


        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "Stepv2_"

    # diamond -- fig 2C
    if shape_type == 4:

        voxelNum = args.ind_size[0]
        beamLengthOrg = voxelSize * voxelNum*1e3

        # antenna points in space
        pts=np.array([[0, voxelSize/2.*1e3, 0],
                      [1, voxelSize/2.*1e3, 1],
                      [2, voxelSize/2.*1e3, 0],
                      [1, voxelSize/2.*1e3, -1],
                      [0.5, voxelSize/2.*1e3, -0.5]])

        num_of_equidistant = 20
        x=np.zeros((20*(pts.shape[0]-1)))
        y=np.zeros((20*(pts.shape[0]-1)))
        z=np.zeros((20*(pts.shape[0]-1)))

        for index in range(pts.shape[0]-1):
            x[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,0], pts[index+1,0], num_of_equidistant)
            y[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,1], pts[index+1,1], num_of_equidistant)
            z[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,2], pts[index+1,2], num_of_equidistant)


        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((x.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = voxelSize/2.*1e3*np.ones((voxelNum,))
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        xn = xn-xn[0]
        zn = zn-zn[0]

        voxelNums = np.linspace(0, args.ind_size[1]*args.ind_size[0]-1, args.ind_size[1]*args.ind_size[0])

        xa = []
        ya = []
        za = []
        for i in range(args.ind_size[1]):
            xa.append(xn)
            ya.append(yn+voxelSize*1e3*i)
            za.append(zn)
        xnFinal = np.concatenate((xa))
        ynFinal = np.concatenate((ya))
        znFinal = np.concatenate((za))

        if args.isCPUenabled:
            xnFinal = 0.1 + xnFinal
            znFinal = 0.1 + znFinal

        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "diamond_"

    # Stepv1 -- fig S7A
    if shape_type == 5:

        # make a step function
        voxelRegion_num = voxelNum/3
        regionLen = voxelRegion_num * voxelSize

        y = voxelSize/2.*1e3*np.ones((voxelNum,))
        x = np.hstack((np.linspace(0, regionLen, int(voxelRegion_num)), regionLen * np.ones(int(voxelRegion_num)), np.linspace(regionLen, 2*regionLen, int(voxelRegion_num))))
        z = np.hstack((np.zeros(int(voxelRegion_num)), np.linspace(0, 1*regionLen, int(voxelRegion_num)), regionLen * np.ones(int(voxelRegion_num))))

        positions = np.vstack((x,y,z))

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((x.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])

        yn = voxelSize/2.*1e3*np.ones((voxelNum,))
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        xn = xn-xn[0]
        zn = zn-zn[0]

        voxelNums = np.linspace(0, args.ind_size[1]*args.ind_size[0]-1, args.ind_size[1]*args.ind_size[0])

        xa = []
        ya = []
        za = []
        for i in range(args.ind_size[1]):
            xa.append(xn)
            ya.append(yn+voxelSize*1e3*i)
            za.append(zn)
        xnFinal = np.concatenate((xa))
        ynFinal = np.concatenate((ya))
        znFinal = np.concatenate((za))

        if args.isCPUenabled:
            xnFinal = 0.1 + xnFinal
            znFinal = 0.1 + znFinal


        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "Stepv1_"

    # Fibonacci -- fig S7B
    if shape_type == 6:

        # make a spiral
        i = np.linspace(0, 360, voxelNum*5)
        a = 10
        b = 0.3063489
        t = i / 180. * math.pi
        x = np.multiply((a + b * np.exp(t)), np.cos(t))
        z = np.multiply((a + b * np.exp(t)), np.sin(t))
        positions = np.array([x, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((i.shape[0],))

        for i in range(positions.shape[1]):
            positionsRotated[:,i] = rotate_via_numpy(positions[:,i] , 180*math.pi/180)
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        zn = np.interp(finalDistStep, absLength, positionsRotated[1,:])
        yn = voxelSize/2.*1e3*np.ones((voxelNum,))

        voxelNums = np.linspace(0, args.ind_size[1]*args.ind_size[0]-1, args.ind_size[1]*args.ind_size[0])
        xa = []
        ya = []
        za = []
        for i in range(args.ind_size[1]):
            xa.append(xn)
            ya.append(yn+voxelSize*1e3*i)
            za.append(zn)
        xnFinal = np.concatenate((xa))
        ynFinal = np.concatenate((ya))
        znFinal = np.concatenate((za))

        xnFinal = 0.1 + xnFinal - min(xnFinal)
        znFinal = 0.1 + znFinal - znFinal[0]

        xnFinal = np.flip(xnFinal)
        znFinal = np.flip(-znFinal)

        if args.isCPUenabled:
            znFinal = znFinal+0.2

        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)

        file2Save = args.run_dir_main + "/desired_shape/" + "Fibonacci"

    #3D
    # SeaShell -- fig 2D
    if shape_type == 7:

        # make a helix in 3D
        t = np.linspace(1*math.pi, 2.8*math.pi, voxelNum*5)
        f = np.linspace(1.5, 0.75, 5*voxelNum)

        a = 5
        b = 5

        a=np.multiply(f, np.flip(t))

        x = np.multiply(b, t)
        y = np.multiply(a, np.sin(t))
        z = np.multiply(a, np.cos(t))
        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((t.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = np.interp(finalDistStep, absLength, positionsRotated[1,:])
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        voxelNums = np.linspace(0, args.ind_size[0]-1, args.ind_size[0])

        xn = xn-xn[0]
        yn = yn-yn[0]
        zn = zn-zn[0]

        if args.ind_size[1]%2==0:  # even y voxel num
            yn=yn+args.ind_size[1]/2*voxelSize*1e3
        elif args.ind_size[1]%2==1:  # odd y voxel num
            yn=yn+(args.ind_size[1]-1)/2*voxelSize*1e3+voxelSize/2*1e3

        xnFinal = xn
        ynFinal = yn
        znFinal = zn

        if args.isCPUenabled:
            xnFinal = voxelSize/2*1e3 + xnFinal
            znFinal = voxelSize/2*1e3 + znFinal

        voxelStrainEnergy = np.ones((voxelNum, 1))
        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "SeaShell"

    # step3D -- fig 2E
    if shape_type == 8:

        voxelNum = args.ind_size[0]
        beamLengthOrg = voxelSize * voxelNum*1e3

        # antenna points in space
        pts=np.array([[0, 0, 0],
                    [0.5, 0, 0],
                    [0.5, 1, 0],
                    [1.5, 1, 0],
                    [1.5, 1, 1],
                    [1.5, 0, 1]])

        num_of_equidistant = 20
        x=np.zeros((20*(pts.shape[0]-1)))
        y=np.zeros((20*(pts.shape[0]-1)))
        z=np.zeros((20*(pts.shape[0]-1)))

        for index in range(pts.shape[0]-1):
            x[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,0], pts[index+1,0], num_of_equidistant)
            y[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,1], pts[index+1,1], num_of_equidistant)
            z[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,2], pts[index+1,2], num_of_equidistant)

        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((x.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = np.interp(finalDistStep, absLength, positionsRotated[1,:])
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        voxelNums = np.linspace(0, voxelNum-1, voxelNum)

        xn = xn-xn[0]
        yn = yn-yn[0]
        zn = zn-zn[0]

        if args.ind_size[1]%2==0:  # even y voxel num
            yn=yn+args.ind_size[1]/2*voxelSize*1e3
        elif args.ind_size[1]%2==1:  # odd y voxel num
            yn=yn+(args.ind_size[1]-1)/2*voxelSize*1e3+voxelSize/2*1e3

        xnFinal = xn
        ynFinal = yn
        znFinal = zn

        if args.isCPUenabled:
            xnFinal = voxelSize/2*1e3 + xnFinal
            znFinal = voxelSize/2*1e3 + znFinal

        voxelStrainEnergy = np.ones((voxelNum, 1))
        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "step3D"

    # Helix -- Fig S7C
    if shape_type == 9:

        # make a helix in 3D
        t = np.linspace(0, 2*math.pi, voxelNum*5)

        a = 5
        b = 5

        x = np.multiply(b, t)
        y = np.multiply(a, np.sin(t))
        z = np.multiply(a, np.cos(t))
        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((t.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = np.interp(finalDistStep, absLength, positionsRotated[1,:])
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        voxelNums = np.linspace(0, args.ind_size[0]-1, args.ind_size[0])

        xn = xn-xn[0]
        yn = yn-yn[0]
        zn = zn-zn[0]

        if args.ind_size[1]%2==0:  # even y voxel num
            yn=yn+args.ind_size[1]/2*voxelSize*1e3
        elif args.ind_size[1]%2==1:  # odd y voxel num
            yn=yn+(args.ind_size[1]-1)/2*voxelSize*1e3+voxelSize/2*1e3

        xnFinal = xn
        ynFinal = yn
        znFinal = zn

        if args.isCPUenabled:
            xnFinal = voxelSize/2*1e3 + xnFinal
            znFinal = voxelSize/2*1e3 + znFinal

        voxelStrainEnergy = np.ones((voxelNum, 1))
        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "Helix"

    # step3Dv2 -- fig S7D
    if shape_type == 10:  

        voxelNum = args.ind_size[0]
        beamLengthOrg = voxelSize * voxelNum*1e3

        # antenna points in space
        pts=np.array([[0, 0, 0],
                    [1, 0, 0],
                    [1, 1, 0],
                    [1, 1, -1],
                    [2, 1, -1]])

        num_of_equidistant = 20
        x=np.zeros((20*(pts.shape[0]-1)))
        y=np.zeros((20*(pts.shape[0]-1)))
        z=np.zeros((20*(pts.shape[0]-1)))

        for index in range(pts.shape[0]-1):
            x[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,0], pts[index+1,0], num_of_equidistant)
            y[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,1], pts[index+1,1], num_of_equidistant)
            z[index*num_of_equidistant:(index+1)*num_of_equidistant]=np.linspace(pts[index,2], pts[index+1,2], num_of_equidistant)
        positions = np.array([x, y, z])

        positionsRotated  = copy.deepcopy(positions)
        beamLength = 0.
        absLength = np.zeros((x.shape[0],))

        for i in range(positions.shape[1]):
            if not i == 0:
                beamLength = beamLength + np.linalg.norm(positionsRotated[:,i]-positionsRotated[:,(i-1)])
                absLength[i] = copy.deepcopy(beamLength)

        scale = beamLengthOrg / beamLength
        positionsRotated = positionsRotated*scale
        absLength = absLength * scale

        finalDistStep = np.linspace(0,absLength[-1], voxelNum)
        xn = np.interp(finalDistStep, absLength, positionsRotated[0,:])
        yn = np.interp(finalDistStep, absLength, positionsRotated[1,:])
        zn = np.interp(finalDistStep, absLength, positionsRotated[2,:])

        voxelNums = np.linspace(0, voxelNum-1, voxelNum)

        xn = xn-xn[0]
        yn = yn-yn[0]
        zn = zn-zn[0]

        if args.ind_size[1]%2==0:  # even y voxel num
            yn=yn+args.ind_size[1]/2*voxelSize*1e3
        elif args.ind_size[1]%2==1:  # odd y voxel num
            yn=yn+(args.ind_size[1]-1)/2*voxelSize*1e3+voxelSize/2*1e3

        xnFinal = xn
        ynFinal = yn
        znFinal = zn

        if args.isCPUenabled:
            xnFinal = voxelSize/2*1e3 + xnFinal
            znFinal = voxelSize/2*1e3 + znFinal

        voxelStrainEnergy = np.ones((voxelNum, 1))
        desShape = np.stack((voxelNums, xnFinal, ynFinal, znFinal), axis=-1)
        positions = np.stack((xnFinal, ynFinal, znFinal), axis=-1)
        file2Save = args.run_dir_main + "/desired_shape/" + "step3Dv2"


    # sheet_maximize_midSegment --maximmize the mid segment position -- fig. S9B
    if shape_type == 11:
        # returns the voxels that should be maximized in z position
        voxels_to_maximize=[]
        for i in range(args.ind_size[0]):
            for j in range(args.ind_size[1]):
                if i>23 and i<28 and j>23 and j<28:
                    voxels_to_maximize.append(i-1+args.ind_size[0]*(j-1))

        return np.asarray(voxels_to_maximize)

    if draw_3Dshape:
        draw3Dshape(args, positions, voxelStrainEnergy, file2Save)

    return(desShape)

def getDesiredShape(args, drawShape=1):
    "desired shape/task/goal"
    if args.desired_shape == "triangleWave":
        desPos = generateDesiredShape(args, 1, drawShape)
        return desPos
    
    if args.desired_shape == "Heartbeat":
        desPos = generateDesiredShape(args, 2,drawShape)
        return desPos
    
    if args.desired_shape == "Stepv2":
        desPos = generateDesiredShape(args, 3,drawShape)
        return desPos

    if args.desired_shape == "diamond":
        desPos = generateDesiredShape(args, 4, drawShape)
        return desPos
    
    if args.desired_shape == "Stepv1":
        desPos = generateDesiredShape(args, 5, drawShape)
        return desPos
    
    if args.desired_shape == "Fibonacci":
        desPos = generateDesiredShape(args, 6,drawShape)
        return desPos
    
    #3D
    if args.desired_shape == "SeaShell":
        desPos = generateDesiredShape(args, 7, drawShape)
        return desPos
    
    if args.desired_shape == "step3D":
        desPos = generateDesiredShape(args, 8, drawShape)
        return desPos
    
    if args.desired_shape == "Helix":
        desPos = generateDesiredShape(args, 9, drawShape)
        return desPos

    if args.desired_shape == "step3Dv2":
        desPos = generateDesiredShape(args, 10, drawShape)
        return desPos
    
    #other demos
    if args.desired_shape == "beam_max_turn":
        desPos = []
        return desPos

    # sheet
    if args.desired_shape == "sheet_maximize_midSegment":
        desPos = generateDesiredShape(args, 11, drawShape)
        return desPos


    if args.desired_shape == "sheet_min_volume":
        desPos = []
        return desPos


    # dynamic
    if args.desired_shape == "max_COM_z":
        desPos = []
        return desPos
    
    if args.desired_shape == "max_COM_x":
        desPos = []
        return desPos
    

    if args.desired_shape == "multiM_maxForce":
        desPos = []
        return desPos

    if args.desired_shape == "multi_func_walkNjump":
        desPos = []
        return desPos



def plot_progress(args, logbook, dirName):
    gen = logbook.select("gen")
    fit_mins = logbook.chapters["fitness"].select("min")
    fit_mins2 = [item[0] for item in fit_mins]
    fit_avgs = logbook.chapters["fitness"].select("avg")
    fit_avgs2 = [item[0] for item in fit_avgs]
    age_mins = logbook.chapters["age"].select("min")
    age_avgs = logbook.chapters["age"].select("avg")

    fig, ax1 = plt.subplots()
    line1 = ax1.plot(gen, fit_avgs2, "b-", label="Average Fitness")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Average Fitness", color="b")
    for tl in ax1.get_yticklabels():
        tl.set_color("b")

    ax2 = ax1.twinx()
    line2 = ax2.plot(gen, fit_mins2, "r-", label="Minimum Fitness")
    ax2.set_ylabel("Minimum Fitness", color="r")
    for tl in ax2.get_yticklabels():
        tl.set_color("r")

    lns = line1 + line2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="upper right")

    plot_file = dirName + "/Fitness_VS_Gen.png"
    fig.savefig(plot_file)
    plt.close()

    fig, ax1 = plt.subplots()
    line1 = ax1.plot(gen, age_avgs, "b-", label="Average age")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Average Age", color="b")
    for tl in ax1.get_yticklabels():
        tl.set_color("b")

    ax2 = ax1.twinx()
    line2 = ax2.plot(gen, fit_avgs2, "r-", label="Average Fitness")
    ax2.set_ylabel("Average Fitness", color="r")
    for tl in ax2.get_yticklabels():
        tl.set_color("r")

    lns = line1 + line2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="upper right")

    plot_file = dirName + "/age_VS_Gen.png"
    fig.savefig(plot_file)
    plt.close()

""" utils math"""

def identity(x):
    return x

def step(x,x_min=0,x_max=1):
    if x>0:
        return x_max
    else:
        return x_min

def sigmoid(x):
    return 2.0 / (1.0 + np.exp(-x)) - 1.0

def positive_sigmoid(x):
    return (1 + sigmoid(x)) * 0.5

def rescaled_positive_sigmoid(x, x_min=0, x_max=1):
    return (x_max - x_min) * positive_sigmoid(x) + x_min

def inverted_sigmoid(x):
    return sigmoid(x) ** -1

def neg_abs(x):
    return -np.abs(x)

def neg_square(x):
    return -np.square(x)

def sqrt_abs(x):
    return np.sqrt(np.abs(x))

def neg_sqrt_abs(x):
    return -sqrt_abs(x)

def sin_square_x_plus_x(x):
    return np.square(np.sin(x))+x

def gaussian_e(x):
    return np.power(math.e, -np.square(x))

def triangle_wave(x):
    return 2/math.pi*np.arcsin(np.sin(x))

def sawtooth_wave(x):
    # ignoring the division by zero error, arctan takes care of the inf cases
    with np.errstate(divide='ignore',invalid='ignore'):
        return_value=-2/math.pi*np.arctan(1./np.tan(x/2))
    return return_value

def square_wave(x):
    return np.sign(np.sin(x))

def relu(x):
    return np.maximum(x,0)

def elu(x):
    return np.maximum(x,0.3*(np.power(math.e, np.minimum(x,0))-1))

def tanh(x):
	return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))

def swish(x):
    return 2*x*(1.0 + np.exp(-x))-1


def mean_abs(x):
    return np.mean(np.abs(x))

def std_abs(x):
    return np.std(np.abs(x))

def count_positive(x):
    return np.sum(np.greater(x, 0))

def count_negative(x):
    return np.sum(np.less(x, 0))

def proportion_equal_to(x, keys):
    return np.mean(count_occurrences(x, keys))

def normalize(x):
    x -= np.min(x)
    # ignoring the division by zero error, it is handled in the next step
    with np.errstate(divide='ignore',invalid='ignore'):
        x /= np.max(x)
    x = np.nan_to_num(x)
    x *= 2
    x -= 1
    return x

def xml_format(tag):
    """Ensures that tag is encapsulated inside angle brackets."""
    if tag[0] != "<":
        tag = "<" + tag
    if tag[-1:] != ">":
        tag += ">"
    return tag

def natural_sort(l, reverse):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key, reverse=reverse)

def find_between(string, start, end):
    start = string.index(start) + len(start)
    end = string.index(end, start)
    return string[start:end]

def replace_text_in_file(filename, replacements_dict):
    lines = []
    with open(filename) as infile:
        for line in infile:
            for original, target in replacements_dict.iteritems():
                line = line.replace(original, target)
            lines.append(line)
    with open(filename, 'w') as outfile:
        for line in lines:
            outfile.write(line)

def dominates(ind1, ind2, attribute_name, maximize):
    """Returns True if ind1 dominates ind2 in a shared attribute."""
    if maximize:
        return getattr(ind1, attribute_name) > getattr(ind2, attribute_name)
    else:
        return getattr(ind1, attribute_name) < getattr(ind2, attribute_name)

def count_occurrences(x, keys):
    """Count the total occurrences of any keys in x."""
    if not isinstance(x, np.ndarray):
        x = np.asarray(x)
    active = np.zeros_like(x, dtype=np.bool)
    for a in keys:
        active = np.logical_or(active, x == a)
    return active.sum()

def two_muscles(output_state):
    return np.greater(output_state, 0) + 3

def continuous_material(output_state, *args, **kwargs):
    return make_one_shape_only(output_state) * output_state

def discretize_material(output_state, num_materials=4, *args, **kwargs):
    """Discretize outputs into bins, one for each material."""
    bins = np.linspace(-1, 1, num=num_materials)
    # print(make_one_shape_only(output_state) * np.digitize(output_state, bins))
    # print("***\n**\n\n\n\n")

    for key, value in kwargs.items():
        if key == "desired_behaviour":
            if value  == "max_vol_3D":

                orig_size_xyz = np.shape(output_state)
                side_thickness = 2
                _k = orig_size_xyz[1]-2*side_thickness
                empty_segment  = np.zeros((orig_size_xyz[0], _k, _k))

                design_mask = np.pad(empty_segment, ((0,0), (side_thickness, side_thickness), (side_thickness, side_thickness)), 'constant', constant_values=(1, 1))

                output_state = np.multiply(output_state, design_mask)

                return make_one_shape_only(output_state) * np.digitize(output_state, bins)

            elif value == "SMP_gripper":

                # make the top layer magnetic and bot layer smp
                output_state = np.digitize(output_state, bins)

                bottom_layer = np.where(output_state[0,:,:] == 1, 2, output_state[0,:,:])
                top_layer = np.where(output_state[1,:,:] == 2, 1, output_state[1,:,:])

                def convert_to_3d_array(array_2d):
                    array_3d = np.reshape(array_2d, (1, array_2d.shape[0], array_2d.shape[1]))
                    return array_3d

                top_layer = convert_to_3d_array(top_layer)
                bottom_layer = convert_to_3d_array(bottom_layer)
                top_layer = make_one_shape_only(top_layer) * top_layer
                bottom_layer = make_one_shape_only(bottom_layer) * bottom_layer

                modified_output_state = np.stack((bottom_layer[0], top_layer[0]), axis = 0)

                return make_one_shape_only(modified_output_state) * modified_output_state

            else:
                raise NotImplementedError

    # otherwise default
    return make_one_shape_only(output_state) * np.digitize(output_state, bins)

def make_material_tree(this_softbot, *args, **kwargs):

    mapping = this_softbot.to_phenotype_mapping
    material = mapping["material"]

    if material["dependency_order"] is not None:
        for dependency_name in material["dependency_order"]:
            for network in this_softbot:
                if dependency_name in network.graph.nodes():
                    mapping.dependencies[dependency_name]["state"] = \
                        network.graph.nodes[dependency_name]["state"] > 0

    if material["dependency_order"] is not None:
        for dependency_name in reversed(material["dependency_order"]):
            if mapping.dependencies[dependency_name]["material_if_true"] is not None:
                material["state"][mapping.get_dependency(dependency_name, True)] = \
                    mapping.dependencies[dependency_name]["material_if_true"]

            if mapping.dependencies[dependency_name]["material_if_false"] is not None:
                material["state"][mapping.get_dependency(dependency_name, False)] = \
                    mapping.dependencies[dependency_name]["material_if_false"]

    return make_one_shape_only(material["state"]) * material["state"]

def make_Mtheta_tree(this_softbot, *args, **kwargs):

    mapping = this_softbot.to_phenotype_mapping
    Mtheta = mapping["Mtheta"]

    if Mtheta["dependency_order"] is not None:
        for dependency_name in Mtheta["dependency_order"]:
            for network in this_softbot:
                if dependency_name in network.graph.nodes():
                    mapping.dependencies[dependency_name]["state"] = \
                        network.graph.nodes[dependency_name]["state"] > 0

    if Mtheta["dependency_order"] is not None:
        for dependency_name in reversed(Mtheta["dependency_order"]):
            if mapping.dependencies[dependency_name]["material_if_true"] is not None:
                Mtheta["state"][mapping.get_dependency(dependency_name, True)] = \
                    mapping.dependencies[dependency_name]["material_if_true"]

            if mapping.dependencies[dependency_name]["material_if_false"] is not None:
                Mtheta["state"][mapping.get_dependency(dependency_name, False)] = \
                    mapping.dependencies[dependency_name]["material_if_false"]


    return make_one_shape_only(Mtheta["state"]) * Mtheta["state"]


def make_material_tree_single_muscle_patches(this_softbot, *args, **kwargs):

    mapping = this_softbot.to_phenotype_mapping
    material = mapping["material"]

    # for name, details in mapping.items():
    #     if details["dependency_order"] is not None:
    for dependency_name in material["dependency_order"]:
        for network in this_softbot:
            if dependency_name in network.graph.nodes():
                mapping.dependencies[dependency_name]["state"] = \
                    network.graph.nodes[dependency_name]["state"] > 0

    # for name, details in mapping.items():
    #     if details["dependency_order"] is not None:
    for dependency_name in reversed(material["dependency_order"]):
        if mapping.dependencies[dependency_name]["material_if_true"] is not None:
            tmpState = mapping.get_dependency(dependency_name, True)
            if dependency_name == "muscleType":
                tmpState = make_one_shape_only(tmpState)
            material["state"][tmpState] = mapping.dependencies[dependency_name]["material_if_true"]

        if mapping.dependencies[dependency_name]["material_if_false"] is not None:
            tmpState = mapping.get_dependency(dependency_name, False)
            if dependency_name == "muscleType":
                tmpState = make_one_shape_only(tmpState)
                material["state"][ndimage.morphology.binary_dilation(tmpState)] = "1"
                # # print "tmpState:"
                # # print tmpState
                # # print "dilated:"
                # # print ndimage.morphology.binary_dilation(tmpState)
            material["state"][tmpState] = mapping.dependencies[dependency_name]["material_if_false"]

    # return details["state"]
    return make_one_shape_only(material["state"]) * material["state"]

def make_one_shape_only(output_state, mask=None):
    """Find the largest continuous arrangement of True elements after applying boolean mask.

    Avoids multiple disconnected softbots in simulation counted as a single individual.

    Parameters
    ----------
    output_state : numpy.ndarray
        Network output

    mask : bool mask
        Threshold function applied to output_state

    Returns
    -------
    part_of_ind : bool
        True if component of individual

    """
    if mask is None:
        def mask(u): return np.greater(u, 0)

    # # print output_state
    # sys.exit(0)

    one_shape = np.zeros(output_state.shape, dtype=np.int32)


    if np.sum(mask(output_state)) < 2:
        one_shape[np.where(mask(output_state))] = 1
        return one_shape

    else:
        not_yet_checked = []
        for x in range(output_state.shape[0]):
            for y in range(output_state.shape[1]):
                for z in range(output_state.shape[2]):
                    not_yet_checked.append((x, y, z))

        largest_shape = []
        queue_to_check = []
        while len(not_yet_checked) > len(largest_shape):
            queue_to_check.append(not_yet_checked.pop(0))
            this_shape = []
            if mask(output_state[queue_to_check[0]]):
                this_shape.append(queue_to_check[0])

            while len(queue_to_check) > 0:
                this_voxel = queue_to_check.pop(0)
                x = this_voxel[0]
                y = this_voxel[1]
                z = this_voxel[2]
                for neighbor in [(x+1, y, z), (x-1, y, z), (x, y+1, z), (x, y-1, z), (x, y, z+1), (x, y, z-1)]:
                    if neighbor in not_yet_checked:
                        not_yet_checked.remove(neighbor)
                        if mask(output_state[neighbor]):
                            queue_to_check.append(neighbor)
                            this_shape.append(neighbor)

            if len(this_shape) > len(largest_shape):
                largest_shape = this_shape

        for loc in largest_shape:
            one_shape[loc] = 1

        return one_shape

def count_neighbors(output_state, mask=None):
    """Count neighbors of each 3D element after applying boolean mask.

    Parameters
    ----------
    output_state : numpy.ndarray
        Network output

    mask : bool mask
        Threshold function applied to output_state

    Returns
    -------
    num_of_neighbors : list
        Count of True elements surrounding an individual in 3D space.

    """
    if mask is None:
        def mask(u): return np.greater(u, 0)

    presence = mask(output_state)
    voxels = list(itertools.product(*[range(x) for x in output_state.shape]))
    num_neighbors = [0 for _ in voxels]

    for idx, (x, y, z) in enumerate(voxels):
        for neighbor in [(x+1, y, z), (x-1, y, z), (x, y+1, z), (x, y-1, z), (x, y, z+1), (x, y, z-1)]:
            if neighbor in voxels:
                num_neighbors[idx] += presence[neighbor]

    return num_neighbors



# multi-material
def create_mat_color_palette(args, SNScolor_palette):
    mat_color_folder = args.run_directory + "/finalData/mat_color_palette"
    sub.call("mkdir " + mat_color_folder + "/" + " 2>/dev/null", shell=True)

    for mat_num in range(args.material_num):
            mat_id = mat_num+1
            mat_name = args.material_names[mat_num]
            mat_color = SNScolor_palette[mat_num]

            blank_mat_image = np.zeros((600,600,3))
            blank_mat_image[:,:] = mat_color


            save_path = mat_color_folder  + "/mat_name_"+  mat_name + "_matID_" + str(mat_id) + ".png"
            matplotlib.image.imsave(save_path, blank_mat_image)


# file copying

def verify_file_integrity(original_file, copied_file):
    # Calculate checksums for both files
    original_checksum = calculate_checksum(original_file)
    copied_checksum = calculate_checksum(copied_file)

    # Compare checksums
    return original_checksum == copied_checksum

def calculate_checksum(file_path):
    # Open the file in binary mode
    with open(file_path, "rb") as f:
        # Read the content of the file in chunks
        checksum = hashlib.sha256()
        for chunk in iter(lambda: f.read(4096), b""):
            checksum.update(chunk)
    return checksum.hexdigest()

def copy_file_with_subprocess(source, destination, delete_source_afterwards = 0):


    is_copying_succesful = False

    while is_copying_succesful == False:

        copy_result = sub.call("cp "+ source + " " + destination, shell=True)

        if copy_result == 0:
            if verify_file_integrity(source, destination):
                is_copying_succesful = True

                if delete_source_afterwards:
                    copy_result = sub.call("rm "+ source, shell=True)
            else:
                print("Error with copied file:", destination)
        else:
            print("Error copying file:", source)
