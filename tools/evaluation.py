import time
import random
import numpy as np
import subprocess as sub
import math
import os
import multiprocessing
import statistics
import miniball



from tools.read_write_voxelyze import write_voxelyze_file, xml2npArray, write_obj_BC_results, read_objective_results, read_BC_results, write_magnetic_profile, write_magnetic_field
from tools.read_write_voxelyze import write_NN_raw_data
from tools.control_fields import get_magnetic_control_field
from tools.utils import draw3Dshape, drawInitShape, copy_file_with_subprocess
from tools.logger import pickle_thisData_at



def updateVoxelMapping(args, pop):
    """ updates the mapping between global number frame to voxel number frame """
    for ind in pop:
        if not ind.id in pop.all_evaluated_individuals_ids:
            for name, details in ind.genotype.to_phenotype_mapping.items():
                if name == "material":
                    indexGlobal = 0
                    indexVox = 0

                    for z in range(ind.genotype.orig_size_xyz[2]):
                        for y in range(ind.genotype.orig_size_xyz[1]):
                            for x in range(ind.genotype.orig_size_xyz[0]):
                                state = details["output_type"](details["state"][x, y, z])
                                # map the global to Vox frame
                                if state > 0:  # fixed for multi-materials -Alp
                                    ind.mappingGlobal2Voxelyze[indexGlobal] = indexVox
                                    indexVox +=1
                                elif state == 0:
                                    ind.mappingGlobal2Voxelyze[indexGlobal] = -1 # meaning no voxel at that spot
                                ind.isVoxelMap[indexGlobal]=state
                                indexGlobal += 1
    return pop

def segmentMprofile(args, pop):
    """segments the M profile, by average pooling using structure shape as a kernel"""

    for ind in pop:
        if not ind.id in pop.all_evaluated_individuals_ids:

            if args.encoding_type=="same_CPPN" or args.encoding_type=="seperate_CPPN":

                # get the current network output for Material --isVoxel, and M profile --Mtheta nd Mphi
                for name, details in ind.genotype.to_phenotype_mapping.items():
                    designParam = np.zeros((ind.genotype.orig_size_xyz[0], ind.genotype.orig_size_xyz[1], ind.genotype.orig_size_xyz[2]))
                    # TODO : get rid of the loop
                    for z in range(ind.genotype.orig_size_xyz[2]):
                        for y in range(ind.genotype.orig_size_xyz[1]):
                            for x in range(ind.genotype.orig_size_xyz[0]):
                                designParam[x,y,z] = details["output_type"](details["state"][x, y, z])

                    ind.designParameters.update({name: designParam})

                # get the segmented M profile via average pooling with the material structure for each segment as a kernel
                for name, details in ind.segmentedMprofile.items():
                    segmentParam = np.zeros((details.shape))
                    for z in range(details.shape[2]):
                        for y in range(details.shape[1]):
                            for x in range(details.shape[0]):
                                a = ind.designParameters[name][(x*ind.genotype.segment_size_xyz[0]):((x+1)*ind.genotype.segment_size_xyz[0]),
                                                                    (y*ind.genotype.segment_size_xyz[1]):((y+1)*ind.genotype.segment_size_xyz[1]),
                                                                    (z*ind.genotype.segment_size_xyz[2]):((z+1)*ind.genotype.segment_size_xyz[2])]
                                kernel = ind.designParameters["material"][(x*ind.genotype.segment_size_xyz[0]):((x+1)*ind.genotype.segment_size_xyz[0]),
                                                                            (y*ind.genotype.segment_size_xyz[1]):((y+1)*ind.genotype.segment_size_xyz[1]),
                                                                            (z*ind.genotype.segment_size_xyz[2]):((z+1)*ind.genotype.segment_size_xyz[2])]

                                filtered = np.multiply(a, kernel)
                                segmentParam[x,y,z] = np.sum(filtered)/np.sum(kernel)
                    if name=="Mtheta" and args.magnetization_direction =="2D":
                        segmentParam[segmentParam>0]=math.pi
                    segmentParam = np.nan_to_num(segmentParam, nan = -999)
                    ind.segmentedMprofile.update({name: segmentParam})

            elif args.encoding_type=="morph_CPPN_mag_direct" or args.encoding_type=="multi_material":
                # get the current network output for Material --isVoxel
                for name, details in ind.genotype.to_phenotype_mapping.items():
                    if name=="material":
                        designParam = np.zeros((ind.genotype.orig_size_xyz[0], ind.genotype.orig_size_xyz[1], ind.genotype.orig_size_xyz[2]))

                        if details["output_type"] == float:
                            designParam = details["state"]
                        else:
                            for z in range(ind.genotype.orig_size_xyz[2]):
                                for y in range(ind.genotype.orig_size_xyz[1]):
                                    for x in range(ind.genotype.orig_size_xyz[0]):
                                        designParam[x,y,z] = details["output_type"](details["state"][x, y, z])

                        ind.designParameters.update({name: designParam})

                # get the segmented M profile via average pooling with the material structure for each segment as a kernel
                for name, details in ind.genotype.to_phenotype_mapping.items():
                    if not name=="material":
                        segmentParam = np.zeros((ind.segmentedMprofile[name].shape))

                        if details["output_type"] == float:
                            segmentParam = details["state"]
                        else:
                            for z in range(ind.segmentedMprofile[name].shape[2]):
                                for y in range(ind.segmentedMprofile[name].shape[1]):
                                    for x in range(ind.segmentedMprofile[name].shape[0]):
                                        segmentParam[x,y,z] = details["output_type"](details["state"][x, y, z])

                        if name=="Mtheta" and args.magnetization_direction == "2D":
                            segmentParam[segmentParam>0]=math.pi
                            segmentParam[segmentParam<0]=0
                        if name=="Mtheta" and args.magnetization_direction == "3D" and args.magnetization_simplified and args.encoding_type == "multi_material" :
                            segmentParam[segmentParam >= math.pi/4*3] = math.pi
                            segmentParam[segmentParam <= -math.pi/4*3] = -math.pi
                            segmentParam[(segmentParam < math.pi/4*3) & (segmentParam >= math.pi/4)] = math.pi/2
                            segmentParam[(segmentParam > -math.pi/4*3) & (segmentParam <= -math.pi/4)] = -math.pi/2
                            segmentParam[(segmentParam > -math.pi/4) & (segmentParam < math.pi/4)] = 0

                        if args.magnetization_simplified and args.encoding_type == "multi_material" and name == "Mphi":
                            segmentParam[segmentParam>=math.pi/3*2]=math.pi
                            segmentParam[segmentParam<=math.pi/3]=0
                            segmentParam[(segmentParam>math.pi/3) & (segmentParam<math.pi/3*2)]=math.pi/2


                        segmentParam = np.nan_to_num(segmentParam, nan = -999)
                        ind.segmentedMprofile.update({name: segmentParam})

            else:
                raise NotImplementedError

            # map the segmented M profile to the voxel M profile
            for name, details in ind.segmentedMprofile.items():
                designParam = np.zeros((ind.genotype.orig_size_xyz[0], ind.genotype.orig_size_xyz[1], ind.genotype.orig_size_xyz[2]))
                for z in range(ind.genotype.orig_size_xyz[2]):
                    for y in range(ind.genotype.orig_size_xyz[1]):
                        for x in range(ind.genotype.orig_size_xyz[0]):
                            xSegment = x//ind.genotype.segment_size_xyz[0]
                            ySegment = y//ind.genotype.segment_size_xyz[1]
                            zSegment = z//ind.genotype.segment_size_xyz[2]
                            designParam[x,y,z] = details[xSegment, ySegment, zSegment]

                ind.designParameters.update({name: designParam})


    return pop

def compare_fitness(args, best_fitness, new_fitness):
    if args.fitness_maximize:  # maximizing the fitness
        if new_fitness>best_fitness:
            return True
    elif not args.fitness_maximize:  # minimizing the fitness
        if new_fitness<best_fitness:
            return True
    else:
        raise NotImplementedError

    return False

def getFitness(args, ind, desiredVoxPos, vox_dict):
    currentVoxPos=vox_dict["position"]

    def get_COM_position(args, ind, VoxPos):
        COM = 0.
        for globalIndex in range(args.ind_size[0]*args.ind_size[1]*args.ind_size[2]):
            voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
            if voxIndex != -1:
                COM = COM + 1e3*VoxPos[voxIndex]
        isFilled_state = np.where(ind.isVoxelMap != 0, 1, 0)
        COM_final = COM/np.sum(isFilled_state)
        return COM_final


    if args.fitness_calc_type == "positionMSE":  # used for 2D desired shape mathing dmeonstrations
        mse = 0.
        for globalIndex in range(np.shape(desiredVoxPos)[0]):
            voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
            if voxIndex != -1:
                mse = mse + np.sqrt((np.square(desiredVoxPos[globalIndex,1:4] - 1e3*currentVoxPos[voxIndex])).sum(axis=None))

        mse = mse/np.sum(ind.isVoxelMap)

    elif args.fitness_calc_type == "nposMSE_Yavg":  # used for the 3D desired shape mathing dmeonstrations
        if args.ind_size[0]>args.ind_size[2]:
            voxel_num=args.ind_size[0]
            mse = 0.
            for index in range(voxel_num):
                counterY=0
                avg_pos=np.zeros((3))
                for indexY in range(args.ind_size[1]):
                    globalIndex=index+indexY*voxel_num
                    voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
                    if voxIndex != -1:
                        avg_pos=avg_pos+1e3*currentVoxPos[voxIndex]
                        counterY+=1

                if not counterY==0:
                    avg_pos=avg_pos/counterY
                    mse = mse + np.sqrt((np.square(desiredVoxPos[index,1:4] - avg_pos)).sum(axis=None))
        else:
            voxel_num=args.ind_size[2]

            mse = 0.
            for index in range(voxel_num):
                counterY=0
                avg_pos=np.zeros((3))
                for indexY in range(args.ind_size[1]):
                    globalIndex=index*args.ind_size[1]+indexY
                    voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
                    if voxIndex != -1:
                        avg_pos=avg_pos+1e3*currentVoxPos[voxIndex]
                        counterY+=1

                if not counterY==0:
                    avg_pos=avg_pos/counterY
                    mse = mse + np.sqrt((np.square(desiredVoxPos[index,1:4] - avg_pos)).sum(axis=None))

        mse = mse/voxel_num

    elif args.fitness_calc_type == "beam_maximize_turn":   # used for the maximizing beam rotation demonstration
        currentVoxOrient=vox_dict["orientation"]
        if args.ind_size[0]>args.ind_size[2]:
            voxel_num=args.ind_size[0]
            mse = 0.
            avg_orients = np.zeros((voxel_num))
            for index in range(voxel_num):
                counterY=0
                avg_orient=np.zeros((1))
                for indexY in range(args.ind_size[1]):
                    globalIndex=index+indexY*voxel_num
                    voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
                    if voxIndex != -1:
                        avg_orient=avg_orient+currentVoxOrient[voxIndex][0]
                        counterY+=1
                avg_orient=avg_orient/counterY
                avg_orients[index] = avg_orient + math.pi  # shift it by pi

            turn_num = 0
            # get the turn number
            for index in range(voxel_num-1):
                orient1 = avg_orients[index]
                orient2 = avg_orients[index+1]

                # all the cases,
                if (orient1 >= 0 and orient2 >= 0 ) or (orient1 < 0 and orient2 < 0):
                    ang_diff = orient2 - orient1
                elif (orient1 > 0 and orient2 < 0) or (orient1 < 0 and orient2 > 0):
                    ang_diff = abs(orient2 - orient1)
                    if ang_diff > math.pi:
                        ang_diff = 2*math.pi - ang_diff
                else:
                    ang_diff = orient2 - orient1
                turn_num = turn_num + ang_diff

            turn_num = turn_num/(2*math.pi)

            mse = turn_num

    elif args.fitness_calc_type == "maximize_mid_segment": # used for sheet max mid pt demo
        mse = 0.
        counter=0
        for globalIndex in desiredVoxPos:
            voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
            if voxIndex != -1:
                mse = mse + 1e3*currentVoxPos[voxIndex,2]
                counter=counter+1

        if counter==0:
            mse = 0.
        else:
            mse = mse/counter

    elif args.fitness_calc_type == "minimize_enclosing_sphere_volume":  # used for the sheet minimize volume demo
        voxIndices = []
        counter=0
        voxel_num=args.ind_size[0]*args.ind_size[1]*args.ind_size[2]
        for globalIndex in range(voxel_num):
            voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
            if voxIndex != -1:
                voxIndices.append(voxIndex)
                counter=counter+1


        C, r2 = miniball.get_bounding_ball(currentVoxPos[voxIndices], epsilon=1e-9)
        radius = math.sqrt(r2)*1e3  # in mm

        mse = radius

    elif args.fitness_calc_type == "max_velZ_beam":   # beam 2D
        voxCOMvel_maxvelZ=vox_dict["COMvelMaxVelZ"]
        velZ = voxCOMvel_maxvelZ[0,2]
        velCOM = np.linalg.norm(voxCOMvel_maxvelZ)
        COMmaxZ=vox_dict["COMmaxZ"]

        jumpTime=vox_dict["jumpTotTime"]

        COM_reward = COMmaxZ[0,2]*1e3
        floor_touching_penalty = vox_dict["voxTouchingFloor"]

        reward = 10*jumpTime + COM_reward
        penalty = floor_touching_penalty + abs(COMmaxZ[0,0]-args.ind_size[0]*args.lattice_dim)*1e3 + abs(COMmaxZ[0,1]-args.ind_size[1]*args.lattice_dim)*1e3


        if jumpTime > 0 :  # jumped
            mse =  reward - penalty
        else:
            mse = - penalty - 900

    elif args.fitness_calc_type == "max_velZ":  # sheet jumping, 2d and 3D Multi-material jumper as well
        voxCOMvel_maxvelZ=vox_dict["COMvelMaxVelZ"]
        velZ = voxCOMvel_maxvelZ[0,2]
        velCOM = np.linalg.norm(voxCOMvel_maxvelZ)
        COMmaxZ=vox_dict["COMmaxZ"]

        jumpTime=vox_dict["jumpTotTime"]


        COM_reward = COMmaxZ[0,2]*1e3
        floor_touching_penalty = vox_dict["voxTouchingFloor"]

        reward = 10*jumpTime
        penalty = floor_touching_penalty


        if jumpTime > 0 :  # jumped
            mse =  reward - penalty
        else:
            mse = - penalty - 900

    elif args.fitness_calc_type == "max_broad_jump":    # MM directional jumping

        floor_touching_penalty = vox_dict["voxTouchingFloor"]
        # jumping time
        jumpTime=vox_dict["jumpTotTime"]

        ### distance calculations ###
        # get initial COM position
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_-1.xml"
        pre_vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        PreJumpVoxPos=pre_vox_dict["position"]

        COM_initial = get_COM_position(args, ind, PreJumpVoxPos)

        # get final COM position
        FinalVoxPos=vox_dict["position"]
        COM_final = get_COM_position(args, ind, FinalVoxPos)

        COM_X_distFinal = COM_final[0]-COM_initial[0]  #  in mm


        ### jumping height max min position of the robot ###
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_-3.xml"
        MaxMinPosZ_vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        MaxMinPosZ=MaxMinPosZ_vox_dict["MaxMinPosZ"]
        MaxMinZ_heigth = MaxMinPosZ[0][2]*1e3 # in mm

        reward = 100*jumpTime + COM_X_distFinal + MaxMinZ_heigth
        penalty = floor_touching_penalty


        if jumpTime > 0 :  # jumped
            mse =  reward - penalty
        else:
            mse = - penalty - 900

    elif args.fitness_calc_type == "max_dist_move":   # MM traversing robot

        currentVoxPos=vox_dict["position"]
        COM_X = 0.
        for globalIndex in range(args.ind_size[0]*args.ind_size[1]*args.ind_size[2]):
            voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
            if voxIndex != -1:
                COM_X = COM_X + 1e3*currentVoxPos[voxIndex][0]

        COM_X = COM_X/np.sum(ind.isVoxelMap)
        COM_X_initial = args.ind_size[0]*args.lattice_dim*1e3/2  #  in mm
        if args.run_name == "MMSimpContMMxv1" or args.run_name == "MMSimpContMMxv2":
            COM_X_distFinal = COM_X-COM_X_initial  #  in mm
        else:
            COM_X_distFinal = COM_X  #  in mm


        # get the position before the disturbance is occured
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_-1.xml"
        pre_vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        PreDistVoxPos=pre_vox_dict["position"]

        COM_X = 0.
        for globalIndex in range(args.ind_size[0]*args.ind_size[1]*args.ind_size[2]):
            voxIndex = ind.mappingGlobal2Voxelyze[globalIndex]
            if voxIndex != -1:
                COM_X = COM_X + 1e3*PreDistVoxPos[voxIndex][0]

        COM_X = COM_X/np.sum(ind.isVoxelMap)
        COM_X_start = COM_X  #  in mm


        reward = COM_X_distFinal - COM_X_start

        mse =  reward

    elif args.fitness_calc_type == "multi_func_walkNjump":

        ## walk part
        ##########################################3
        args.desired_shape = "max_COM_x"
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + ".xml"
        vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        rewards_walking  = []

        # reward or penatly from difference each step
        WalkerCOMXs = vox_dict["WalkerCOMXs"]
        WalkerCOMXs_diff = [1e3*(WalkerCOMXs[i] - WalkerCOMXs[i - 1]) for i in range(1, len(WalkerCOMXs))]

        WalkerCOMXs_diff_reward = [(WalkerCOMXs_diff[i]*i*i) for i in range(0, len(WalkerCOMXs_diff))]
        rewards_walking.append(np.sum(WalkerCOMXs_diff_reward))

        # reward or penatly from difference each step
        steps_std = np.std(WalkerCOMXs_diff)
        rewards_walking.append(-3*steps_std)


        # penalty if jumped
        jumpTime_walking=vox_dict["jumpTotTime"]

        if jumpTime_walking > 0 :  # jumped
            penalty_walking = 20
        else:
            penalty_walking = 0


        reward_walk = np.sum(rewards_walking) - penalty_walking

        ##### jumping during heated time ############
        ##########################################3
        args.desired_shape = "max_COM_z"
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_heated.xml"
        vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        floor_touching_penalty = vox_dict["voxTouchingFloor"]
        # jumping time
        jumpTime=vox_dict["jumpTotTime"]

        ### distance calculations ###
        # get initial COM position
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_-1_heated.xml"
        pre_vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        PreJumpVoxPos=pre_vox_dict["position"]

        COM_initial = get_COM_position(args, ind, PreJumpVoxPos)

        # get final COM position
        FinalVoxPos=vox_dict["position"]
        COM_final = get_COM_position(args, ind, FinalVoxPos)

        COM_X_distFinal = COM_final[0]-COM_initial[0]  #  in mm


        ### jumping height max min position of the robot ###
        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_-3_heated.xml"
        MaxMinPosZ_vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
        MaxMinPosZ=MaxMinPosZ_vox_dict["MaxMinPosZ"]
        MaxMinZ_heigth = MaxMinPosZ[0][2]*1e3 # in mm



        reward = 100*jumpTime + COM_X_distFinal + MaxMinZ_heigth
        penalty = floor_touching_penalty

        if jumpTime > 0 :  # jumped
            reward_jumping =  reward
        else:
            reward_jumping = - penalty - 200

        # penalty for drastically different performances for jumping and walking --> encouraging similar performances levels for both sides
        walker_distance = (WalkerCOMXs[-1] - WalkerCOMXs[0])*1e3
        jumper_distance = COM_X_distFinal
        distance_penalty = np.sqrt((walker_distance - jumper_distance)**2)


        mse =  reward_walk + reward_jumping - distance_penalty

    elif args.fitness_calc_type == "multiM_maxForce":

        ## get the forces
        currentVoxForce=vox_dict["force"]

        # for slices in x-y plane
        # get the total force applied at the ends
        def get_slice_indices(args, _slice_num):
            width = args.ind_size[0]
            depth = args.ind_size[1]
            height = args.ind_size[2]


            slice_indices = []

            for _y in range(depth):
                for _x in range(width):
                    _indx = _x + _y * width + _slice_num * (width*depth)
                    slice_indices.append(_indx)

            return slice_indices


        slices = [1]
        forces = []
        total_force = 0
        force_avg = 0
        for _slice in slices:

            # get the hull for the final shape
            slice_indices_global = get_slice_indices(args, _slice)
            slice_indices_vox = ind.mappingGlobal2Voxelyze[slice_indices_global]

            slice_forces = currentVoxForce[slice_indices_vox]
            slice_forces_cleaned = slice_forces[~np.isnan(slice_forces).any(axis=1)]

            forces.append(slice_forces_cleaned)

            # slice_forces_cleaned
            _force = np.sum(slice_forces_cleaned, axis=0)


            force_strength = np.linalg.norm(slice_forces_cleaned, axis=1)
            # _force = np.sum(force_strength)
            _force_avg = _force/np.shape(force_strength)[0]
            total_force = _force + total_force
            force_avg = _force_avg + force_avg

        mse = total_force[2] * 1e6  # multi-material max force

    else:
        raise NotImplementedError

    return mse

def compute_obj_BC(args, ind, des_VoxPos, vox_dict=None):

    # update the fitness
    for rank, details in ind.objective_dict.items():
        objectiveName = details["name"]
        if objectiveName == "fitness":
            idNum = ind.id

            if args.isCPUenabled: # CPU run
                indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(idNum).zfill(args.max_ind_1ex)+"/id_" + str(idNum).zfill(args.max_ind_1ex) + ".xml"
                vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)
            else:
                raise NotImplementedError

            ind.voxel_dict=vox_dict

            voxelPositions=vox_dict["position"]
            voxelStrainEnergy=vox_dict["strainEnergy"]
            fitnessValue = getFitness(args, ind, des_VoxPos, vox_dict)
            ind.fitness = fitnessValue

        elif objectiveName == "novelty":
            raise NotImplementedError

    # update the BC's
    if ind.BC_dict is not None:
        detail = []
        for rank, details in ind.BC_dict.items():
            detail.append(details)
        for details in detail:
            BC_name = details["name"]
            if BC_name == "volume":
                setattr(ind, BC_name, np.sum(ind.isVoxelMap>0)/ind.voxelNum)
            elif BC_name == "MthetaAvg":
                if args.magnetization_direction=="3D":
                    setattr(ind, BC_name, np.average(ind.segmentedMprofile["Mtheta"]))
                else:
                    xyz=ind.segmentedMprofile["Mtheta"].shape
                    theta_zx_plane=[]
                    for x in range(xyz[0]):
                        for y in range(xyz[1]):
                            for z in range(xyz[2]):
                                theta = ind.segmentedMprofile["Mtheta"][x,y,z]
                                phi = ind.segmentedMprofile["Mphi"][x,y,z]
                                if not theta==0:
                                    phi = -phi
                                theta_zx_plane.append(phi)
                    setattr(ind, BC_name, sum(theta_zx_plane)/len(theta_zx_plane))
            elif BC_name == "MphiAvg":
                setattr(ind, BC_name, np.average(ind.segmentedMprofile["Mphi"]))
            elif BC_name == "COM":
                COM_average = np.sum(1e3*voxelPositions, axis=0)/np.sum(ind.isVoxelMap>0)
                COM_distance = np.sqrt(np.square(COM_average).sum(axis=None))
                setattr(ind, BC_name, COM_distance)
            elif BC_name == "CPPN": # total number of edges and nodes on the network
                CPPN_complexity = len(ind.genotype.networks[0].graph.nodes())+len(ind.genotype.networks[0].graph.edges())
                setattr(ind, BC_name, CPPN_complexity)
            elif BC_name == "CPPN_node_num": # total number of nodes on the network
                setattr(ind, BC_name, len(ind.genotype.networks[0].graph.nodes()))
            elif BC_name == "CPPN_edge_num": # total number of edges on the network
                setattr(ind, BC_name, len(ind.genotype.networks[0].graph.edges()))
            elif BC_name == "StrainEnergyAvg": # Avg strain energy of the voxels
                setattr(ind, BC_name, np.mean(voxelStrainEnergy))
            else:
                raise NotImplementedError

    # pickle the ind
    ind.save_ind(args, ind)

    # clean up
    if args.isCPUenabled: # CPU run
        # delete the unneccesary files
        dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)

        sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+"*.vxa", shell=True)
        sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+"_M.xml", shell=True)
        sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+".xml", shell=True)

        if args.controller_type != "quasi-static":
            sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+"_B.xml", shell=True)
        # if args.desired_shape == "max_COM_z" or args.desired_shape == "max_COM_x":
        #     sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+"-1.xml", shell=True)
        if args.isSMP_used:
            sub.call("rm "+ dirName +  "/id_*_heated.xml", shell=True)

    else:
        raise NotImplementedError

    "write the resulting  profile of Voxels on xml file"
    write_obj_BC_results(args, ind)

def update_pop_obj_BC(args, pop):
    "updates the robots' objectives and BCs and returns the pop"

    # Calculate the related objectives in parallel
    if args.isCPUenabled: # CPU run

        if args.process_in_parallel:
            processes = []
            if args.cluster_debug: print("robot pop objs are going to be calculated")
            for ind in pop:
                if not ind.id in pop.all_evaluated_individuals_ids:
                    p = multiprocessing.Process(target=compute_obj_BC, args=(args, ind, pop.des_VoxPos,))
                    processes.append(p)
                    p.start()
            if args.cluster_debug: print("calculating robot pop objs")
            for process in processes:
                process.join()
            if args.cluster_debug: print("calculating robot pop objs is completed")

        else:
            if args.cluster_debug: print("robot pop objs are going to be calculated")
            for ind in pop:
                if not ind.id in pop.all_evaluated_individuals_ids:
                    compute_obj_BC(args, ind, pop.des_VoxPos)

            if args.cluster_debug: print("calculating robot pop objs is completed")

    else:
        raise NotImplementedError


    for ind in pop: # read the values and update the pop fitness and BC
        if not ind.id in pop.all_evaluated_individuals_ids:
            objective_values_dict = read_objective_results(args, ind)
            # get the objective/fitness/goal/cost/whateveryou want to call it
            for rank, details in pop.objective_dict.items():
                if objective_values_dict[rank] is not None:
                    setattr(ind, details["name"], objective_values_dict[rank])

            # get the ind BC dict
            if ind.BC_dict is not None:
                BC_dict = read_BC_results(args, ind)
                for rank, details in ind.BC_dict.items():
                    setattr(ind, details["name"], BC_dict[rank])


            dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)

            # update the best ind
            if compare_fitness(args, best_fitness=pop.best_fit_so_far, new_fitness=ind.fitness):
                pop.best_fit_so_far = ind.fitness
                pop.best_fit_ind_id = ind.id
                dirName = args.run_directory + "/bestSoFar/fitOnly"

                # get the positions
                vox_dict = ind.load_ind(ind.id, args).voxel_dict
                voxelPositions=vox_dict["position"]
                voxelStrainEnergy=vox_dict["strainEnergy"]
                ind.voxel_dict=vox_dict

                # draw the initial shape
                plotInitialShapeSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/initShapeTOP"

                if not np.all(_size > 1 for _size in args.ind_size):   # 3D cases are not
                    drawInitShape(args, ind.designParameters["material"], plotInitialShapeSaveFile)

                # draw the shape and save it
                plot3DSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/finalShape3D_"
                draw3Dshape(args, 1e3*voxelPositions, voxelStrainEnergy, plot3DSaveFile)

                if args.desired_shape == "max_COM_z" or args.desired_shape == "max_COM_z_symmetry":
                    COM_file = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+ "/id_"+str(ind.id).zfill(args.max_ind_1ex)+ '_COM.txt'
                    fileTXT = open(COM_file, "w")
                    np.savetxt(fileTXT, [vox_dict["COMmaxZ"][0]], delimiter=',', fmt='%-2.5f',newline="")
                    fileTXT.close()

                sub.call("cp -R "+ args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex) \
                        + " " + dirName, shell=True)

            if args.save_lineages:
                sub.call("cp " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(ind.id).zfill(args.max_ind_1ex)+".vxa" \
                             + " " + args.run_directory + "/ancestors/", shell=True)

            pop.all_evaluated_individuals_ids.append(ind.id)
            pop.already_evaluated[ind.md5] = [getattr(ind, details["name"])
                                                                for rank, details in
                                                                pop.objective_dict.items()]

    if args.cluster_debug: print("pops obj and Bcs are updated")

    # reset possible NaNs to worst values
    for ind in pop:
        if math.isnan(ind.fitness):
            ind.fitness = pop.objective_dict[0]["worst_value"]
            print ("FITNESS WAS NAN, RESETTING IT TO:", pop.objective_dict[0]["worst_value"])
            print ("for ind id: ", ind.id)

    if args.use_NN: # update the train and test data for NN
        if args.cluster_debug: print("updating the train and test data for NN")
        pop.NN.update_dataset(args, pop.individuals)

    if args.save_NN_raw_data: # save the raw data for NN
        if args.cluster_debug: print("saving the raw data for NN")
        write_NN_raw_data(args, pop)

    # update the stats
    if args.cluster_debug: print("updating the stats")
    # create a temporary stat dict of lists
    tempStat = {}
    for rank, details in pop.objective_dict.items():
        tempStat[details["name"]] = []
    tempStat["Ind_IDs_for_gen"] = []
    tempBestFitID = None
    tempBestFitParentID = None
    tempBestFit = None
    tempBestFitAGE = None

    for ind in pop:
        tempStat["Ind_IDs_for_gen"].append(ind.id)
        for rank, details in pop.objective_dict.items():
            tempStat[details["name"]].append(getattr(ind, details["name"]))
            if tempBestFit is None or getattr(ind, details["name"]) <  tempBestFit:
                tempBestFit = getattr(ind, details["name"])
                tempBestFitID = ind.id
                tempBestFitParentID = ind.parent_id
                tempBestFitAGE = ind.age


    # pop.logbook.update({pop.gen: {}})
    for rank, details in pop.objective_dict.items():
        # pop.logbook[details["name"]] = {}
        pop.logbook[details["name"]]["min"].append(min(tempStat[details["name"]]))
        pop.logbook[details["name"]]["max"].append(max(tempStat[details["name"]]))
        pop.logbook[details["name"]]["mean"].append(statistics.mean(tempStat[details["name"]]))
        pop.logbook[details["name"]]["stdev"].append(statistics.stdev(tempStat[details["name"]]))

    for param in pop.record_these_too:
        pop.logbook[param].append(tempStat["Ind_IDs_for_gen"])  # list of individual IDs for each generation
    pop.logbook["best_fit_IDS"].append(tempBestFitID)
    pop.logbook["best_fit_parent_IDS"].append(tempBestFitParentID)
    pop.logbook["best_fit_age"].append(tempBestFitAGE)
    pop.logbook["isExplore"].append(pop.explore)


    # pickle the ind ids for each generation
    dirName = args.run_directory + "/generationsData/Gen_"+str(pop.gen)+"/Ind_IDs_Gen_" +str(pop.gen)+".pickle"
    pickle_thisData_at(tempStat["Ind_IDs_for_gen"],dirName)

    if args.cluster_debug: print("BCs and objs are calculated, returning the updated pop")
    return pop



def evaluate(args, indVox, my_sim, my_env, des_VoxPos, controller = None):

    if args.fitness_calc_type=="multi_func_walkNjump" or args.fitness_calc_type=="multi_func_walkNjumpv2":
        args.desired_shape = "max_COM_x"
        args, controller = get_magnetic_control_field(args)

    # write the phenotype of a magSoftbot to a file so that VoxCad can access for sim.
    write_voxelyze_file(args, my_sim, my_env, indVox, args.run_directory, args.run_name)

    # write the M profile of the magSoftbot
    write_magnetic_profile(args, indVox, args.run_directory, args.run_name)


    if args.controller_type != "quasi-static":
        write_magnetic_field(args, indVox, args.run_directory, args.run_name, controller)

    "evaluate the design"
    sub.Popen("./voxelyze -f " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(indVox.id).zfill(args.max_ind_1ex) + ".vxa" + " -B_ext " + str(args.quasi_static_B_magnitude),shell=True)


    all_done = False
    redo_attempts = 1

    eval_start_time = time.time()

    fileName =  args.run_directory + "/fitnessFiles/" + args.run_name + "--id_" + str(indVox.id).zfill(args.max_ind_1ex) + ".xml"
    while not all_done:

        time_waiting_for_eval = time.time() - eval_start_time

        if time_waiting_for_eval > args.time_to_try_again * redo_attempts:
            # try to redo any simulations that might have crashed
            redo_attempts += 1
            if args.debug: print ("Rerunning voxelyze for individual: ", indVox.id)
            sub.Popen("./voxelyze -f " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+" -B_ext " + str(args.quasi_static_B_magnitude),shell=True)

        # check to see if simulation run is finished
        if os.path.isfile(fileName):
            ls_check = fileName
            ls_check = ls_check.split("/")[-1]
            if (args.run_name + "--id_") in ls_check:
                this_id = int(ls_check.split("_")[1].split(".")[0])

                if this_id == indVox.id:
                    fitnessSaveFile = args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+".xml"
                    try:
                        vox_dict = xml2npArray(fitnessSaveFile, args.ind_size, 0, args)
                        all_done = True
                    except:
                        all_done = False
                        print("could not read the result file!!!")
                        print("for indID: ", indVox.id)

            # wait a second and try again
            else:
                time.sleep(0.2)
        else:
            time.sleep(0.2)


    # copy the voxvad,  profile, and results files for each ind
    # save the individuals
    dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(indVox.id).zfill(args.max_ind_1ex)
    if not os.path.exists(dirName):
        # Create target Directory
        os.makedirs(dirName)
    else:
        if args.debug: print("Directory " , dirName ,  " already exists")


    # pickle the morphology and M profile
    pickle_thisData_at(thisData = dict(args = args, indDesignParams = indVox.designParameters), at = dirName + "/design_parameters.pkl")

    # copy voxcad files, M, results
    source_file = args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+".xml"
    destination_file = dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+".xml"
    copy_file_with_subprocess(source_file, destination_file, delete_source_afterwards = 0)

    sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+".vxa" \
            + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+".vxa", shell=True)
    sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_M.xml" \
            + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_M.xml", shell=True)
    if args.controller_type != "quasi-static":
        sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_B.xml" \
                + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_B.xml", shell=True)

    if args.desired_shape == "max_COM_z":
        sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1.xml" \
            + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1.xml", shell=True)
        sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-2.xml" \
            + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-2.xml", shell=True)
        sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3.xml" \
            + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3.xml", shell=True)

        while not os.path.isfile(dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3.xml"):
            time.sleep(0.1)


    # remove already processed file
    if args.desired_shape == "max_COM_x":
        sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1.xml", shell=True)

    if args.desired_shape == "max_COM_z":
        sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1.xml", shell=True)
        sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-2.xml", shell=True)
        sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3.xml", shell=True)


    if args.isSMP_used or args.SMP_flag.count(1)>0:
        if args.isSMP_used and args.SMP_flag.count(1)>0:
            # SMP is utilized
            args.isSMP_heated = 1
            if args.fitness_calc_type=="multi_func_walkNjump" or args.fitness_calc_type=="multi_func_walkNjumpv2":
                args.desired_shape = "max_COM_z"

                if args.controller_type != "quasi-static":
                    args, controller = get_magnetic_control_field(args)
                    write_magnetic_field(args, indVox, args.run_directory, args.run_name, controller)

                # write the phenotype of a magSoftbot to a file so that VoxCad can access for sim.
                write_voxelyze_file(args, my_sim, my_env, indVox, args.run_directory, args.run_name)

                # write the M profile of the magSoftbot
                write_magnetic_profile(args, indVox, args.run_directory, args.run_name)


                "evaluate the design"
                sub.Popen("./voxelyze -f " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(indVox.id).zfill(args.max_ind_1ex) + ".vxa" + " -B_ext " + str(args.quasi_static_B_magnitude),shell=True)

                all_done = False
                redo_attempts = 1

                eval_start_time = time.time()

                fileName =  args.run_directory + "/fitnessFiles/" + args.run_name + "--id_" + str(indVox.id).zfill(args.max_ind_1ex) + ".xml"
                while not all_done:

                    time_waiting_for_eval = time.time() - eval_start_time

                    if time_waiting_for_eval > args.time_to_try_again * redo_attempts:
                        # try to redo any simulations that might have crashed
                        redo_attempts += 1
                        if args.debug: print ("Rerunning voxelyze for individual: ", indVox.id)
                        sub.Popen("./voxelyze -f " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+" -B_ext " + str(args.quasi_static_B_magnitude),shell=True)

                    # check to see if simulation run is finished
                    if os.path.isfile(fileName):
                        ls_check = fileName
                        ls_check = ls_check.split("/")[-1]
                        if (args.run_name + "--id_") in ls_check:
                            this_id = int(ls_check.split("_")[1].split(".")[0])

                            if this_id == indVox.id:
                                fitnessSaveFile = args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+".xml"
                                try:
                                    vox_dict = xml2npArray(fitnessSaveFile, args.ind_size, 0, args)
                                    voxelPositions=vox_dict["position"]
                                    voxelStrainEnergy=vox_dict["strainEnergy"]
                                    # final_time=vox_dict["time"]
                                    all_done = True
                                except:
                                    all_done = False
                                    print("could not read the result file!!!")
                                    print("for indID: ", indVox.id)

                        # wait a second and try again
                        else:
                            time.sleep(0.2)
                    else:
                        time.sleep(0.2)

                # copy the voxvad,  profile, and results files for each ind
                # save the individuals
                dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(indVox.id).zfill(args.max_ind_1ex)

                # copy voxcad files, M, results
                sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+".xml" \
                    + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_heated.xml", shell=True)
                sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+".vxa" \
                        + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_heated.vxa", shell=True)
                sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_M.xml" \
                        + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_M_heated.xml", shell=True)
                if args.controller_type != "quasi-static":
                    sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_B.xml" \
                            + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_B_heated.xml", shell=True)

                if args.desired_shape == "max_COM_z":
                    sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1.xml" \
                        + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1_heated.xml", shell=True)
                    sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-2.xml" \
                        + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-2_heated.xml", shell=True)
                    sub.call("cp "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3.xml" \
                        + " " + dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3_heated.xml", shell=True)

                    while not os.path.isfile(dirName +  "/id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3_heated.xml"):
                        time.sleep(0.1)


                # remove already processed file
                sub.call("rm " + fitnessSaveFile, shell=True)

                if args.desired_shape == "max_COM_z":
                    sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-1.xml", shell=True)
                    sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-2.xml", shell=True)
                    sub.call("rm "+ args.run_directory + "/fitnessFiles/" + args.run_name + "--id_"+str(indVox.id).zfill(args.max_ind_1ex)+"_-3.xml", shell=True)

            # rerun the heated version
        else:
            print("Something is wrong with you material settings, especially with SMP materials, check it out")
            raise NotImplementedError


def evaluate_in_parallel(args, pop, sim, env, desiredShape_VoxPos, controller = None):

    # update the mapping for voxel # from global to voxelyze frame!
    pop = updateVoxelMapping(args, pop)

    # segment the M profile
    pop = segmentMprofile(args, pop)


    if args.isCPUenabled:
        processes = []

        start_time_eval = time.time()

        for ind in pop:
            if not ind.id in pop.all_evaluated_individuals_ids:
                p = multiprocessing.Process(target=evaluate, args=(args, ind, sim, env, desiredShape_VoxPos, controller))
                processes.append(p)
                p.start()
        if args.cluster_debug: print("Robot evaluations are started")

        if args.use_NN and pop.gen !=0 and (pop.max_id > args.NN_batch_size + args.pop_size or args.NN_warm_start):
            random_state = random.getstate()
            numpy_random_state = np.random.get_state()
            pop.NN.train_NN(args)
            random_state2 = random.getstate()
            numpy_random_state2= np.random.get_state()
            random.setstate(random_state)
            np.random.set_state(numpy_random_state)
            if args.cluster_debug:
                if np.array_equal(random_state[1], random_state2[1]): print("random state changed while training NN")
                if np.array_equal(numpy_random_state2[1], numpy_random_state2[1]): print("NP. random state changed while training NN")

        for process in processes:
            process.join()

        if args.cluster_debug: print("Robot evaluations are completed")
        eval_time = time.time() - start_time_eval

        if args.use_NN:
            if not args.isCPUenabled:
                pop.NN.evaluation_time_per_generation=eval_time
            elif args.isCPUenabled and pop.NN.evaluation_time_per_generation==None:   # ensuring the adaptive epoch calculation does not goes out of control
                pop.NN.evaluation_time_per_generation=eval_time
            elif eval_time < pop.NN.evaluation_time_per_generation:
                pop.NN.evaluation_time_per_generation=eval_time
    else:
        raise NotImplementedError

    if args.cluster_debug: print("Evaluated robot pop is returned")
    return pop



## evaluating on the surrogate model

def evaluate_on_NN(args, ind, my_sim, my_env, NN, des_VoxPos):

    # write the phenotype of a magSoftbot to a file so that VoxCad can access for sim.
    write_voxelyze_file(args, my_sim, my_env, ind, args.run_directory, args.run_name)

    # write the M profile of the magSoftbot
    write_magnetic_profile(args, ind, args.run_directory, args.run_name)

    "evaluate the design"
    X_predict = NN.convert_robot_params_to_x_predict(ind)
    Y_predict = NN.get_y_predicted(X_predict)
    ind.fitness_prediction = NN.process_y_predict_to_fitness(Y_predict)[0]
    ind.fitness = ind.fitness_prediction

    # copy the voxvad, profile, and results files for each ind
    # save the individuals
    dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)
    if not os.path.exists(dirName):
        # Create target Directory
        os.makedirs(dirName)
    else:
        if args.debug: print("Directory " , dirName ,  " already exists")

    # copy voxcad files, M, results
    sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(ind.id).zfill(args.max_ind_1ex)+".vxa" \
            + " " + dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+".vxa", shell=True)
    sub.call("cp "+ args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(ind.id).zfill(args.max_ind_1ex)+"_M.xml" \
            + " " + dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+"_M.xml", shell=True)
    time.sleep(0.1)

    # pickle the morphology and M profile
    pickle_thisData_at(thisData = dict(args = args, indDesignParams = ind.designParameters), at = dirName + "/design_parameters.pkl")

    # pickle it for parallel operation
    ind.save_ind(args, ind)
    return ind

def evaluate_on_surrogate_model(args, pop, sim, env, desiredShape_VoxPos):

    # update the mapping for voxel # from global to voxelyze frame!
    pop = updateVoxelMapping(args, pop)

    # segment the M profile
    pop = segmentMprofile(args, pop)


    if args.isCPUenabled:
        start_time_eval = time.time()

        processes = []
        for ind in pop:
            if not ind.id in pop.all_evaluated_individuals_ids:
                p = multiprocessing.Process(target=evaluate_on_NN, args=(args, ind, sim, env, pop.NN, desiredShape_VoxPos,))
                processes.append(p)
                p.start()

        if args.cluster_debug: print("Robot evaluations are started")
        for process in processes:
            process.join()

        if args.cluster_debug: print("Robot evaluations are completed")
        eval_time = time.time() - start_time_eval


        for ind_idx in range(len(pop.individuals)):
            ind = pop.individuals[ind_idx]
            pop.individuals[ind_idx] = ind.load_ind(ind.id, args)

    else:
        raise NotImplementedError

    if args.cluster_debug: print("Evaluated robot pop is returned")
    return pop

def compute_obj_BC_onNN(args, ind, des_VoxPos, vox_dict=None):

    # update the BC's
    if ind.BC_dict is not None:
        detail = []
        for rank, details in ind.BC_dict.items():
            detail.append(details)
        for details in detail:
            BC_name = details["name"]
            if BC_name == "volume":
                setattr(ind, BC_name, np.sum(ind.isVoxelMap>0)/ind.voxelNum)
            elif BC_name == "MthetaAvg":
                if args.magnetization_direction=="3D":
                    setattr(ind, BC_name, np.average(ind.segmentedMprofile["Mtheta"]))
                else:
                    xyz=ind.segmentedMprofile["Mtheta"].shape
                    theta_zx_plane=[]
                    for x in range(xyz[0]):
                        for y in range(xyz[1]):
                            for z in range(xyz[2]):
                                theta = ind.segmentedMprofile["Mtheta"][x,y,z]
                                phi = ind.segmentedMprofile["Mphi"][x,y,z]
                                if not theta==0:
                                    phi = -phi
                                theta_zx_plane.append(phi)
                    setattr(ind, BC_name, sum(theta_zx_plane)/len(theta_zx_plane))
            elif BC_name == "MphiAvg":
                setattr(ind, BC_name, np.average(ind.segmentedMprofile["Mphi"]))
            elif BC_name == "CPPN": # total number of edges and nodes on the network
                CPPN_complexity = len(ind.genotype.networks[0].graph.nodes())+len(ind.genotype.networks[0].graph.edges())
                setattr(ind, BC_name, CPPN_complexity)
            elif BC_name == "CPPN_node_num": # total number of nodes on the network
                setattr(ind, BC_name, len(ind.genotype.networks[0].graph.nodes()))
            elif BC_name == "CPPN_edge_num": # total number of edges on the network
                setattr(ind, BC_name, len(ind.genotype.networks[0].graph.edges()))
            elif BC_name == "StrainEnergyAvg" or BC_name == "COM": # Avg strain energy of the voxels
                pass  # not computed for NN runs
            else:
                raise NotImplementedError

    # pickle the ind
    ind.save_ind(args, ind)

    # clean up
    if args.isCPUenabled: # CPU run
        # delete the unneccesary files
        dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)

        sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+".vxa", shell=True)
        sub.call("rm "+ dirName +  "/id_"+str(ind.id).zfill(args.max_ind_1ex)+"_M.xml", shell=True)

    else:
        raise NotImplementedError

    "write the resulting  profile of Voxels on xml file"
    write_obj_BC_results(args, ind)

def update_pop_obj_BC_onNN(args, pop, my_sim, my_env, des_VoxPos):
    "updates the robots' objectives and BCs and returns the pop"

    # Calculate the related objectives in parallel
    if args.isCPUenabled: # CPU run

        processes = []
        if args.cluster_debug: print("robot pop objs are going to be calculated")
        for ind in pop:
            if not ind.id in pop.all_evaluated_individuals_ids:
                p = multiprocessing.Process(target=compute_obj_BC_onNN, args=(args, ind, pop.des_VoxPos,))
                processes.append(p)
                p.start()
        if args.cluster_debug: print("calculating robot pop objs")

        for process in processes:
            process.join()

        if args.cluster_debug: print("calculating robot pop objs is completed")

    else:
        raise NotImplementedError


    for ind in pop: # read the values and update the pop fitness and BC
        if not ind.id in pop.all_evaluated_individuals_ids:
            objective_values_dict = read_objective_results(args, ind)
            
            for rank, details in pop.objective_dict.items():
                if objective_values_dict[rank] is not None:
                    setattr(ind, details["name"], objective_values_dict[rank])

            # get the ind BC dict
            if ind.BC_dict is not None:
                BC_dict = read_BC_results(args, ind)
                for rank, details in ind.BC_dict.items():
                    setattr(ind, details["name"], BC_dict[rank])


            dirName = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)

            # update the best ind
            if not args.optimizer_type == "DSA_ME":
                if compare_fitness(args, best_fitness=pop.best_fit_so_far, new_fitness=ind.fitness):
                    pop.best_fit_so_far = ind.fitness
                    pop.best_fit_ind_id = ind.id
                    dirName = args.run_directory + "/bestSoFar/fitOnly"

                    # evaluate the best designs found on simulation
                    evaluate(args, ind, my_sim, my_env, des_VoxPos)

                    # get the positions
                    if args.isCPUenabled: # CPU run
                        indResultSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/id_" + str(ind.id).zfill(args.max_ind_1ex) + ".xml"
                        vox_dict = xml2npArray(indResultSaveFile, args.ind_size, 0, args)

                    voxelPositions=vox_dict["position"]
                    voxelStrainEnergy=vox_dict["strainEnergy"]
                    ind.voxel_dict=vox_dict


                    fitnessValue = getFitness(args, ind, des_VoxPos, vox_dict)
                    ind.fitness_sim = fitnessValue
                    pop.best_fit_so_far_onSim_GT = ind.fitness_sim

                    # draw the initial shape
                    plotInitialShapeSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/initShapeTOP"

                    if not np.all(_size > 1 for _size in args.ind_size):   # 3D cases are not
                        drawInitShape(args, ind.designParameters["material"], plotInitialShapeSaveFile)
                    # draw the shape and save it
                    plot3DSaveFile = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+"/finalShape3D_"
                    draw3Dshape(args, 1e3*voxelPositions, voxelStrainEnergy, plot3DSaveFile)

                    if args.desired_shape == "max_COM_z" or args.desired_shape == "max_COM_z_symmetry":
                        COM_file = args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex)+ "/id_"+str(ind.id).zfill(args.max_ind_1ex)+ '_COM.txt'
                        fileTXT = open(COM_file, "w")
                        np.savetxt(fileTXT, [vox_dict["COMmaxZ"][0]], delimiter=',', fmt='%-2.5f',newline="")
                        fileTXT.close()

                    sub.call("cp -R "+ args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex) \
                            + " " + dirName, shell=True)

            if args.save_lineages:
                sub.call("cp " + args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_"+str(ind.id).zfill(args.max_ind_1ex)+".vxa" \
                             + " " + args.run_directory + "/ancestors/", shell=True)

            pop.all_evaluated_individuals_ids.append(ind.id)
            pop.already_evaluated[ind.md5] = [getattr(ind, details["name"])
                                                                for rank, details in
                                                                pop.objective_dict.items()]

    if args.cluster_debug: print("pops obj and Bcs are updated")

    # reset possible NaNs to worst values
    for ind in pop:
        if math.isnan(ind.fitness):
            ind.fitness = pop.objective_dict[0]["worst_value"]
            print ("FITNESS WAS NAN, RESETTING IT TO:", pop.objective_dict[0]["worst_value"])
            print ("for ind id: ", ind.id)
        if args.optimizer_type == "DSA_ME":
            sub.call("rm -r " + args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_"+str(ind.id).zfill(args.max_ind_1ex), shell=True)


    if not args.optimizer_type == "DSA_ME":
        # update the stats
        if args.cluster_debug: print("updating the stats")
        # create a temporary stat dict of lists
        tempStat = {}
        for rank, details in pop.objective_dict.items():
            tempStat[details["name"]] = []
        tempStat["Ind_IDs_for_gen"] = []
        tempBestFitID = None
        tempBestFit = None

        for ind in pop:
            tempStat["Ind_IDs_for_gen"].append(ind.id)
            for rank, details in pop.objective_dict.items():
                tempStat[details["name"]].append(getattr(ind, details["name"]))
                if tempBestFit is None or getattr(ind, details["name"]) <  tempBestFit:
                    tempBestFit = getattr(ind, details["name"])
                    tempBestFitID = ind.id

        # pop.logbook.update({pop.gen: {}})
        for rank, details in pop.objective_dict.items():
            # pop.logbook[details["name"]] = {}
            pop.logbook[details["name"]]["min"].append(min(tempStat[details["name"]]))
            pop.logbook[details["name"]]["max"].append(max(tempStat[details["name"]]))
            pop.logbook[details["name"]]["mean"].append(statistics.mean(tempStat[details["name"]]))
            pop.logbook[details["name"]]["stdev"].append(statistics.stdev(tempStat[details["name"]]))

        for param in pop.record_these_too:
            pop.logbook[param].append(tempStat["Ind_IDs_for_gen"])  # list of individual IDs for each generation
        pop.logbook["best_fit_IDS"].append(tempBestFitID)


        ## record the ground truth as well
        pop.logbook["best_fit_onSim_GT"].append(pop.best_fit_so_far_onSim_GT)


        # pickle the ind ids for each generation
        dirName = args.run_directory + "/generationsData/Gen_"+str(pop.gen)+"/Ind_IDs_Gen_" +str(pop.gen)+".pickle"
        pickle_thisData_at(tempStat["Ind_IDs_for_gen"],dirName)

    if args.cluster_debug: print("BCs and objs are calculated, returning the updated pop")
    return pop