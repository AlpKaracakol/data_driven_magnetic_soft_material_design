#!/usr/bin/env python
"""

ToDo:

explanation for the what this code does?

"""

# External imports
import random
import numpy as np
import subprocess as sub
import os
import sys
import argparse
from glob import glob


# import main classes
from src.base import Sim, Env, ObjectiveDict, BehavioralCharacterizationDict
from src.magsoftbot import MyGenotype, MyPhenotype, Population, BCArchive
from src.config import setup_BC_config
from src.nn import NeuralNetwork
from tools.algorithms import AFPO, MAP_Elites, RandomOpt, MAP_elites_on_NNmodel, DSA_ME
from tools.checkpointing import continue_from_checkpoint
from tools.utils import natural_sort


# Appending repo's root dir in the python path to enable subsequent imports
sys.path.append(os.getcwd() + "/..")

# CPU Making sure to have the most up-to-date version of the Voxelyze physics engine CPU
VOXELYZE_VERSION = '_voxcad'
sub.call("cp ../" + VOXELYZE_VERSION + "/voxelyzeMain/voxelyze .", shell=True)
sub.call("cp " + VOXELYZE_VERSION + "/voxelyzeMain/voxelyze .", shell=True)


def parse_arguments():
    """
    All-almost- the arguments/parameters/configurations for
        - optimizer
        - simulation
        - controller
        - ...(check the desriptions below for details)

    Also check the config.py @/src for MAP-elites specific configurations

    -Alp
    """
    parser = argparse.ArgumentParser(description='trial', fromfile_prefix_chars="@")

    # new ones, place them at the approprate place later
    parser.add_argument('--post_process_at_the_end', type=int, default=0, help="arrange/organize the data, draw the final graphs etc.")
    parser.add_argument('--max_ind_1ex', type=int, default=7, help="what is the maximum number of individuals that are going to be evaluated? 1e5?1e6?1e7?")
    parser.add_argument('--run_on_cluster', type=int, default=0, help='is it going to run on cluster?')
    parser.add_argument('--run_abs_path', type=str, default="..", help='absolute path for the results, relative path in default')
    parser.add_argument('--results_folder_name', type=str, default="results", help='absolute path for the results, relative path in default')

    parser.add_argument('--isCPUenabled', type=int, default=1, help='is CPU enabled, for potential GPU extension in future')

    # parser.add_argument('--multi_process', type=bool, default=True, help='multi-process setting, bool  -- deprecited')
    parser.add_argument('--available_thread_num', type=int, default=50, help='INT, available thread number for parallel processing')
    parser.add_argument('--mutate_in_parallel', type=int, default=1)
    parser.add_argument('--process_in_parallel', type=int, default=1)

    parser.add_argument('--max_run_time', type=float, default=24, help='float, (hours) max run time before autosuspending the session')
    parser.add_argument('--checkpoint', type=str, default=None)
    parser.add_argument('--max_gen2load', type=int, default=0)


    # Quasi-static desired shape/behaviour optimization
    parser.add_argument('--desired_shape', type=str, default=None)
    parser.add_argument('--run_directory', type=str, default='demoTrial')
    parser.add_argument('--run_name', type=str, default='demo')
    parser.add_argument('--run_dir_main', type=str, default='demoTrial')
    parser.add_argument('--run_main', type=str, default=None)
    parser.add_argument('--seed', type=int, default=11)
    parser.add_argument('--seeds', nargs="+", type=int, default=None)
    parser.add_argument('--num_random_inds', type=int, default=1)
    parser.add_argument('--max_gens', type=int, default=30)
    parser.add_argument('--pop_size', type=int, default=10)
    parser.add_argument('--checkpoint_every', type=int, default=5)
    parser.add_argument('--save_pop_every', type=int, default=5)
    parser.add_argument('--save_lineages', type=int, default=0)
    parser.add_argument('--save_nets', type=int, default=0)
    parser.add_argument('--save_finals_as_data', type=int, default=0)
    parser.add_argument('--min_volume_ratio', type=float, default=0.5)
    parser.add_argument('--max_volume_ratio', type=float, default=1)
    parser.add_argument('--magnetization_direction', type=str, default="3D")
    parser.add_argument('--magnetization_simplified', type=int, default=0)

    parser.add_argument('--encoding_type', type=str, default="morph_CPPN_mag_direct")

    # CPPN params
    parser.add_argument('--cppn_sample_from_normal_dist', type=int, default=0)
    parser.add_argument('--num_random_node_adds', type=int, default=5)
    parser.add_argument('--num_random_node_removals', type=int, default=0)
    parser.add_argument('--num_random_link_adds', type=int, default=10)
    parser.add_argument('--num_random_link_removals', type=int, default=5)
    parser.add_argument('--num_random_activation_functions', type=int, default=100)
    parser.add_argument('--num_random_weight_changes', type=int, default=100)


    # optimizer type
    parser.add_argument('--optimizer_type', type=str, default="MAP_Elites_CPPN")
    parser.add_argument('--ME_strategy', type=str, default="explore_exploit")
    parser.add_argument('--ME_exploit_ratio', type=float, default=0.5)
    parser.add_argument('--ME_mutation_ratio_magnetization_vs_morphology', type=float, default=0.66)
    parser.add_argument('--ME_mutate_max_network_num', type=float, default=1)
    parser.add_argument('--ME_cx_ratio', type=float, default=0.05)
    parser.add_argument('--explore_strategy', type=str, default="uniform", help="uniform/novelty_bias")
    parser.add_argument('--novelty_top_gen', type=int, default=500)
    parser.add_argument('--exploit_strategy', type=str, default="bests")
    parser.add_argument('--BC_type', type=str, default="vol_mag_3D", help="str, specifies the map-elites BCs, and gneral BCs, check config.py for options")

    parser.add_argument('--fitness_calc_type', type=str, default="positionMSE", help="str, (fitness calculation methods) Implemented ones: \npositionMSE \nposMSE_lengthMSE \nposMSE_Yavg")
    parser.add_argument('--fitness_maximize', type=int, default=0, help="maximize, 1 or minimize, 0 the fitness")
    parser.add_argument('--bruteForceSet', type=bool, default=False)
    parser.add_argument('--max_optimizer_iteration', type=int, default=1)



    # Map-elites + CPPN params
    parser.add_argument('--number_cells_per_BC', type=int, default=20)


    # Neural Network(NN) settings -- it is used as a pseudo simulation tool
    parser.add_argument('--save_NN_raw_data', type=int, default=1, help="gather, organize and save the robots for general NN use, positions included")
    parser.add_argument('--use_NN', type=int, default=0, help="use neural network as a pseudo simulation if 1")
    parser.add_argument('--NN_when_to_use', type=float, default=1e5, help="after how many evaluations, start using the NN guided mutations")
    parser.add_argument('--NN_mutation_number', type=float, default=1e2, help="after how many evaluations, start using the NN guided mutations")
    parser.add_argument('--NN_run_on', type=str, default="CPU", help="run NN on CPU or GPU")
    parser.add_argument('--NN_input_type', type=str, default="1D_direct_morph_mag", help="input of the NN")
    parser.add_argument('--NN_layers', nargs="+", type=int, default=None, help="NN layers with node numbers")
    parser.add_argument('--NN_activation_function', type=str, default='tanh', help="NN activation function for the nodes")
        # for possible deep NN cases
    parser.add_argument('--NN_layer_num', type=int, default=6, help="NN layer number, set NN_layers to None")
    parser.add_argument('--NN_node_num', type=int, default=128, help="NN node number, set NN_layers to None")
    parser.add_argument('--NN_dropout_ratio', type=float, default=0.1, help="dropout ratio for the dropout layers")
    parser.add_argument('--NN_tensorBoard_callback', type=int, default=1, help="tensorboard logs enabled for visualization of the NN learning")
    parser.add_argument('--NN_modelCheckpoint_callback', type=int, default=1, help="modelCheckpoint enabled for saving the best validaiton model over the time of NN learning")
    parser.add_argument('--NN_batch_size', type=int, default=512, help="batch size for NN training")
    parser.add_argument('--NN_epochs_num', type=int, default=1, help="epoch num for NN training")
    parser.add_argument('--NN_adaptive_epoch_num', type=int, default=1, help="Adaptively selects the epoch number per evaluation run")
    parser.add_argument('--NN_validation_split', type=float, default=-1, help="validation split for the data")
    parser.add_argument('--NN_pop_test_split', type=float, default=0.1, help="population test split for data")
    parser.add_argument('--NN_shuffle', type=int, default=1, help="shuffle the data before training?")
    parser.add_argument('--NN_verbose', type=int, default=0, help="write down the NN results during training, for debugging purposes")
    parser.add_argument('--NN_loss', type=str, default="mean_squared_error", help="loss, mse")
    parser.add_argument('--NN_optimizer', type=str, default="adam", help="loss, mse")
    parser.add_argument('--NN_metrics', type=str, default="mean_squared_error", help="metrics, mse")
    parser.add_argument('--NN_sample_weights', type=int, default=1, help="set to 0 if no weights")
    parser.add_argument('--NN_sample_weights_method', type=str, default="inverse_clip", help="sample_weights method, set to None if no weights")
    parser.add_argument('--NN_save_raw_txt', type=int, default=0, help="gather, organize and save the robots for warm starts")
    parser.add_argument('--NN_save_raw_pickle', type=int, default=0, help="gather, organize and save the robots for warm starts")
    parser.add_argument('--NN_data_process_type', type=str, default="beam", help="process/normalization for the data type")
    parser.add_argument('--NN_warm_start', type=int, default=0, help="NN using the data generated before")
    parser.add_argument('--NN_warm_start_file', type=str, default="../results/NN", help="NN using the data generated before")
    parser.add_argument('--NN_warm_start_processedPrior', type=int, default=0, help="Does the provided data processed already?")
    parser.add_argument('--NN_warm_start_train_epoch', type=int, default=100, help="train number if warm started and model is not trained before-hand")
    parser.add_argument('--NN_use_best_model', type=int, default=0, help="use the best model for testing, defaulted to 0, due to the best model is getting stuck at the beginning via overfitting")


    # DSA-ME, Deep Surrogate Assisted MAP-Elites params
    parser.add_argument('--DSA_ME_outerLoop_NNepoch', type=int, default=20, help="epoch number for DSA-ME outer loop NN train")
    parser.add_argument('--DSA_ME_innerLoop_num', type=int, default=1e2, help="epoch number for DSA-ME outer loop NN train")


    # debug and saving settings
    parser.add_argument('--debug', type=int, default=1)
    parser.add_argument('--cluster_debug', type=int, default=1)
    parser.add_argument('--onlyGenerateShape', type=int, default=0)
    parser.add_argument('--backupALL', type=int, default=0)
    parser.add_argument('--isSaveAllOn', type=bool, default=False)
    parser.add_argument('--morphStacking_size', nargs="+", type=int, default=(15,15))
    parser.add_argument('--only_stack_morphs', type=int, default=0)


    # checkpointing params
    parser.add_argument('--continue_from_checkPoint', type=int, default=0)
    parser.add_argument('--extra_gen_after_max_gen', type=int, default=0, help="extra generations after the max # of gen reached")


    # novelty params
    parser.add_argument('--novelty_k', type=int, default=15, help="number of neighbors for knn novelty score")


    # controller params
    parser.add_argument('--controller_type', type=str, default="quasi-static", help="string, controller type, selec from, quasi-static, open-loop, closed-loop")
    parser.add_argument('--controller_loop_bandwidth', type=int, default=60, help="int in Hz, control loop bandwidth")
        # Quasi-static
    parser.add_argument('--quasi_static_B_magnitude', type=float, default=10e-3, help="float, magnetic field strength of the control signal in z direction")
        # open_loop (OL)
    parser.add_argument('--OL_frequency', type=float, default=2, help="float, frequency of the open loop control signal")
        # closed-loop (CL)
    parser.add_argument('--max_controller_iteration', type=int, default=60, help="int, controller iteration for single run")
    parser.add_argument('--isPrintEveryStep', type=int, default=0, help="int, printing position of the robot every step")


    # sim params
    parser.add_argument('--dt_frac', type=float, default=0.9)
    parser.add_argument('--sim_time', type=float, default=1e-1)
    parser.add_argument('--init_time', type=float, default=5e-3)
    parser.add_argument('--time_to_try_again', type=int, default=600, help="Int, (seconds) wait this long before assuming simulation crashed and resending")
    parser.add_argument('--max_eval_time', type=int, default=1200)
        # mostly for quasi-static
    parser.add_argument('--KinEThreshold', type=float, default=1e-15)
    parser.add_argument('--equilibrium_mode', type=int, default=1)
        # mostly for open-loop
        # damping
    parser.add_argument('--DampingBondZ', type=float, default=1)
    parser.add_argument('--ColBondZ', type=float, default=0.8)
    parser.add_argument('--SlowBondZ', type=float, default=0.01)


    # environment params
    parser.add_argument('--isFloorEnabled', type=int, default=0)
    parser.add_argument('--FloorSlope', type=float, default=0.0)
    parser.add_argument('--FrictionStatic', type=float, default=1.0)
    parser.add_argument('--FrictionDynamic', type=float, default=0.5)


    # robot params
    parser.add_argument('--isFixedFromOneEnd', type=int, default=0)
    parser.add_argument('--isFixedFromBothEnd', type=int, default=0)
    parser.add_argument('--isFixedFromBothTopBottom', type=int, default=0)
    parser.add_argument('--isFixedFromTop', type=int, default=0)
    parser.add_argument('--isFixedFromBottom', type=int, default=0)
    parser.add_argument('--lattice_dim', type=float, default=200e-6)
    parser.add_argument('--ind_size', nargs="+", type=int, default=(60, 7, 1))
    parser.add_argument('--segment_size', nargs="+", type=int, default=(5, 7, 1))

        # 0 if uniform or 1 if non-uniform magnetic field, NOTICE: 1 is only implemented for a 7cm diameter magnet
    parser.add_argument('--IsMagForceOn', type=int, default=0)
    
        # material properties
    parser.add_argument('--M_pervol', type=float, default=20e3, help="exp=32k, fitted 20k")
    parser.add_argument('--density', type=float, default=2.41e3)
    parser.add_argument('--modulus', type=float, default=150e3, help="exp=200k, fitted 150k")
    parser.add_argument('--poissons', type=float, default=0.49)

    # if multi-material
    # combination of hard/softish/soft, Active/passive, light/heavy
    parser.add_argument('--material_num', type=int, default=6, help="")
    parser.add_argument('--material_names', nargs="+", type=str, default=("N108E30",   "N157DS30",   "E30",   "SS960",   "smpMAG",   "smpPAS"), help="")
    parser.add_argument('--M_pervols', nargs="+", type=float,    default=(84e3,         62e3,         0.0,     0.0,       60e3,       0.0),     help="")
    parser.add_argument('--densities', nargs="+", type=float,    default=(2.41e3,       1.86e3,       1.07e3,  1.45e3,    2e3,        1.2e3))
    parser.add_argument('--moduli', nargs="+", type=float,       default=(150e3,        710e3,        69e3,    1.93e6,    1e6,        2e6),  help="")
    parser.add_argument('--poissonsS', nargs="+", type=float,    default=(0.49,         0.49,         0.49,    0.49,      0.49,       0.49))
    parser.add_argument('--SMP_flag', nargs="+", type=int,       default=(0,            0,            0,       0,         1,          1))
    parser.add_argument('--isSMP_used', type=int, default=0)
    parser.add_argument('--isSMP_heated', type=int, default=0)


    parser.add_argument('--SMP_moduli_passive', nargs="+", type=float,          default=(1e6, 50e3),  help="")
    parser.add_argument('--SMP_moduli_responsive', nargs="+", type=float,       default=(2e6, 100e3),  help="")


    # params to save on simulation side
    parser.add_argument('--save_position', type=int, default=1)
    parser.add_argument('--save_orientation', type=int, default=0)
    parser.add_argument('--save_velocity', type=int, default=0)
    parser.add_argument('--save_angular_velocity', type=int, default=0)
    parser.add_argument('--save_strain_energy', type=int, default=1)
    parser.add_argument('--save_kinetic_energy', type=int, default=0)
    parser.add_argument('--save_pressure', type=int, default=0)
    parser.add_argument('--save_force', type=int, default=0, help="you have to set the force as a param on the c++ side1st")


    # drawer params for fitness vs inds histogram
    parser.add_argument('--only_draw_ind_hist', type=int, default=0)
    parser.add_argument('--path_to_files', type=str, default="/../results")
    parser.add_argument('--path_to_save', type=str, default="/../data")
    parser.add_argument('--ind_start', type=int, default=0)
    parser.add_argument('--ind_final', type=int, default=-1)

    #demo max/min vol
    parser.add_argument('--slices2max', nargs="+", type=int, default=(1,2,3,4,5,6) , help="which slices to max volume")
    parser.add_argument('--slices2min', nargs="+", type=int, default=(7,8,9,10,11,12) , help="which slices to min volume")

    # demo jumping params
    parser.add_argument('--CaseMaxMinPosZ', type=int, default=0, help="writing the max minimum Z position of the robot")
    # video params for the sim
    parser.add_argument('--record_video', type=int, default=0, help="int, flag to record a video from the simulation, save the positons of the robot at a given BW")
    parser.add_argument('--video_bandwidth', type=int, default=60, help="int in Hz, video bandwidth, ")
    parser.add_argument('--video_speed_wrt_RT', type=float, default=0.5, help="video speed wrt wall clock")
    parser.add_argument('--video_sim_time', type=float, default=3, help="total video time wrt wall clock")
    parser.add_argument('--video_quality', type=int, default=0, help="video quality, 0 --> 50 dpi, other number N --> 300*N dpi")
    parser.add_argument('--view_type', nargs="+", type=str, default="isometric", help="video viewing side, options: isometric, sideXZ, topXY, frontYZ, all")


    # post-process params
    parser.add_argument('--create_history', type=int, default=0, help="int, flag to create a history file that will be used in unity")
    parser.add_argument('--history_bandwidth', type=int, default=120, help="int in Hz, video bandwidth ")
    parser.add_argument('--history_sim_time', type=int, default=3, help="int in Secs, total history tim")
    parser.add_argument('--voxel_color', nargs="+", type=float, default=(0.,0.,0.,0.9) , help="voxel color code in RGBA, default is black")


    return parser.parse_args()

def setDebuggingSettings(args): # hard-coded debugging settings
    """hard-coded debugging settings"""
    if args.debug: print("\nDebug mode is selected\n")
    args.isSaveAllOn = True

    # example demo

    args.run_directory = "example_demo"
    args.isCPUenabled =1
    args.debug = 1
    args.isSaveAllOn  = True
    args.backupALL = 0
    args.save_NN_raw_data =  True
    args.max_run_time = 1
    args.checkpoint_every = 5
    args.save_finals_as_data = 1
    args.seed = 97
    args.optimizer_type = "MAP_Elites_CPPN"
    args.explore_strategy = "novelty_bias"
    args.results_folder_name ="results"


    args.desired_shape ="triangleWave"
    args.isFixedFromTop =0
    args.isFixedFromOneEnd =1
    args.isFloorEnabled =0
    args.fitness_calc_type ="positionMSE"
    args.fitness_maximize =0
    args.BC_type ="vol_mag_2D"
    args.magnetization_direction ="2D"
    args.encoding_type ="morph_CPPN_mag_direct"
    args.ind_size= ( 5, 2, 1 )
    args.segment_size = (1, 2, 1)

    args.max_gens= 250
    args.pop_size =7
    args.num_random_inds= 1
    args.min_volume_ratio =0.6
    args.number_cells_per_BC =50
    args.ME_cx_ratio =0.05
    args.quasi_static_B_magnitude= 30e-3
    args.IsMagForceOn =1
    args.M_pervol =20e3
    args.modulus =150e3
    args.sim_time =1
    args.init_time =5e-3
    args.KinEThreshold= 1e-15
    args.use_NN =1
    args.NN_mutation_number =25
    args.NN_when_to_use= 1e5
    args.NN_data_process_type ="beam"
    args.NN_sample_weights =0
    args.NN_sample_weights_method ="no_weight"
    args.mutate_in_parallel =0
    args.material_num = 1
    args.isSMP_used = 0
    args.SMP_flag = (0,)

    return args

def check_previous_checkpoints(args):
    continue_from_checkpoint = False
    # check if there are any previous checkpoints exists
    pickled_pops = glob(args.run_directory + "/seed-" + str(args.seed) + "/pickledPops/*.pickle")

    if len(pickled_pops):
        continue_from_checkpoint = True

    return continue_from_checkpoint

def initialize_main_folders(args):
    # folder for the results
    if not os.path.exists("../results"):
        os.makedirs("../results")

    sub.call("mkdir " + args.run_dir_main + "/" + " 2>/dev/null", shell=True)
    sub.call("rm -rf " + args.run_dir_main + "/* 2>/dev/null", shell=True)

    # folder for drawing the desired shape
    ret = sub.call("mkdir " + args.run_dir_main + "/desired_shape/" + " 2>/dev/null", shell=True)

def delete_obsolute_folders(args):
    sub.call("rm -r " + args.run_dir_main + "/fitnessFiles/ 2>/dev/null", shell=True)
    sub.call("rm -r " + args.run_dir_main + "/tempFiles/ 2>/dev/null", shell=True)
    sub.call("rm -r " + args.run_dir_main + "/voxelyzeFiles/ 2>/dev/null", shell=True)

def main(args):
    try:
        if not args.continue_from_checkPoint:
            # Setting up the simulation object
            my_sim = Sim(dt_frac=args.dt_frac, simulation_time=args.sim_time, fitness_eval_init_time=args.init_time, equilibrium_mode = args.equilibrium_mode)

            # Setting up the environment object
            my_env = Env(lattice_dimension = args.lattice_dim)

            # setting up the optimizer with objectives and population
            if args.optimizer_type == "AFPO_CPPN":  # not used in this work
                # Now specifying the objectives for the optimization.
                # Creating an objectives dictionary
                my_objective_dict = ObjectiveDict()

                # Adding an objective named "fitness", which we want to maximize. This information is returned by Voxelyze
                # in a fitness .xml file, with a tag named "NormFinalDist"
                my_objective_dict.add_objective(name="fitness", maximize=args.fitness_maximize, tag="<normAbsolutePosError>")

                # Add an objective to minimize the age of solutions: promotes diversity
                my_objective_dict.add_objective(name="age", maximize=False, tag="<age>")

                # Initialize a population
                my_pop = Population(args, MyGenotype, MyPhenotype, my_objective_dict)

                my_optimization = AFPO(args, my_sim, my_env, my_pop)

            elif args.optimizer_type == "MAP_Elites_CPPN":
                # Now specifying the objectives for the optimization.
                "objective"
                # Creating an objectives dictionary
                my_objective_dict = ObjectiveDict()

                # Adding an objective named "fitness", which we want to maximize
                my_objective_dict.add_objective(name="fitness", maximize=args.fitness_maximize, tag="<normAbsolutePosError>")

                # Add an objective to minimize the age of solutions: promotes diversity
                my_objective_dict.add_objective(name="age", maximize=False, tag="<age>")


                "BC"
                # Creating a behavioral characterization(BC) dictionary   --aka novelty dictionary
                my_BC_dict = BehavioralCharacterizationDict()

                # get the BC settings
                BC_config = setup_BC_config(args)


                for BC in BC_config:
                    my_BC_dict.add_BC(name=BC_config[BC]["name"], tag=BC_config[BC]["tag"], min=BC_config[BC]["min"], max=BC_config[BC]["max"], nb_cells=BC_config[BC]["nb_cells"], worst_value=BC_config[BC]["worst_value"], logging_only=BC_config[BC]["logging_only"])


                # initialize the NN6
                my_NN=None
                if args.use_NN:
                    my_NN = NeuralNetwork(args)
                    if args.cluster_debug: print("\n*\n*NN initialized \n*\n*")

                # Initialize a population
                my_pop = Population(args, MyGenotype, MyPhenotype, my_objective_dict, my_BC_dict, my_NN)
                if args.cluster_debug: print("\n*\n*POP initialized \n*\n*")

                # Initialize an empty archive
                my_arch  = BCArchive(args, my_objective_dict, my_BC_dict)
                if args.cluster_debug: print("\n*\n*BCArchive initialized \n*\n*")

                my_optimization = MAP_Elites(args, my_sim, my_env, my_pop, my_arch)
                if args.cluster_debug: print("\n*\n*MAP_Elites initialized \n*\n*")

            elif args.optimizer_type == "Random":
                # Now specifying the objectives for the optimization.
                "objective"
                # Creating an objectives dictionary
                my_objective_dict = ObjectiveDict()

                # Adding an objective named "fitness", which we want to maximize
                my_objective_dict.add_objective(name="fitness", maximize=args.fitness_maximize, tag="<normAbsolutePosError>")

                # Add an objective to minimize the age of solutions: promotes diversity
                my_objective_dict.add_objective(name="age", maximize=False, tag="<age>")


                "BC"
                # Creating a behavioral characterization(BC) dictionary   --aka novelty dictionary
                my_BC_dict = BehavioralCharacterizationDict()

                # get the BC settings
                BC_config = setup_BC_config(args)


                for BC in BC_config:
                    my_BC_dict.add_BC(name=BC_config[BC]["name"], tag=BC_config[BC]["tag"], min=BC_config[BC]["min"], max=BC_config[BC]["max"], nb_cells=BC_config[BC]["nb_cells"], worst_value=BC_config[BC]["worst_value"], logging_only=BC_config[BC]["logging_only"])


                # initialize the NN
                my_NN=None
                if args.use_NN:
                    my_NN = NeuralNetwork(args)

                # Initialize a population
                my_pop = Population(args, MyGenotype, MyPhenotype, my_objective_dict, my_BC_dict, my_NN)

                # Initialize an empty archive
                my_arch  = BCArchive(args, my_objective_dict, my_BC_dict)

                my_optimization = RandomOpt(args, my_sim, my_env, my_pop, my_arch)

            elif args.optimizer_type == "MAP_Elites_CPPN_onNN":  # MAP-elites solely runs on a trained NN instead of the simulation environment
                # Now specifying the objectives for the optimization.
                "objective"
                # Creating an objectives dictionary
                my_objective_dict = ObjectiveDict()

                # Adding an objective named "fitness", which we want to maximize
                my_objective_dict.add_objective(name="fitness", maximize=args.fitness_maximize, tag="<normAbsolutePosError>")

                # Add an objective to minimize the age of solutions: promotes diversity
                my_objective_dict.add_objective(name="age", maximize=False, tag="<age>")


                "BC"
                # Creating a behavioral characterization(BC) dictionary   --aka novelty dictionary
                my_BC_dict = BehavioralCharacterizationDict()

                # get the BC settings
                BC_config = setup_BC_config(args)


                for BC in BC_config:
                    my_BC_dict.add_BC(name=BC_config[BC]["name"], tag=BC_config[BC]["tag"], min=BC_config[BC]["min"], max=BC_config[BC]["max"], nb_cells=BC_config[BC]["nb_cells"], worst_value=BC_config[BC]["worst_value"], logging_only=BC_config[BC]["logging_only"])


                # initialize the NN
                my_NN=None
                if args.use_NN:
                    my_NN = NeuralNetwork(args)

                # Initialize a population
                my_pop = Population(args, MyGenotype, MyPhenotype, my_objective_dict, my_BC_dict, my_NN)

                # Initialize an empty archive
                my_arch  = BCArchive(args, my_objective_dict, my_BC_dict)

                my_optimization = MAP_elites_on_NNmodel(args, my_sim, my_env, my_pop, my_arch)

            elif args.optimizer_type == "DSA_ME": # for comparison case, Deep Surrogate Assisted MAP-Elites
                # Now specifying the objectives for the optimization.
                "objective"
                # Creating an objectives dictionary
                my_objective_dict = ObjectiveDict()

                # Adding an objective named "fitness", which we want to maximize
                my_objective_dict.add_objective(name="fitness", maximize=args.fitness_maximize, tag="<normAbsolutePosError>")

                # Add an objective to minimize the age of solutions: promotes diversity
                my_objective_dict.add_objective(name="age", maximize=False, tag="<age>")


                "BC"
                # Creating a behavioral characterization(BC) dictionary   --aka novelty dictionary
                my_BC_dict = BehavioralCharacterizationDict()

                # get the BC settings
                BC_config = setup_BC_config(args)


                for BC in BC_config:
                    my_BC_dict.add_BC(name=BC_config[BC]["name"], tag=BC_config[BC]["tag"], min=BC_config[BC]["min"], max=BC_config[BC]["max"], nb_cells=BC_config[BC]["nb_cells"], worst_value=BC_config[BC]["worst_value"], logging_only=BC_config[BC]["logging_only"])


                # initialize the NN
                my_NN=None
                if args.use_NN:
                    my_NN = NeuralNetwork(args)

                # Initialize a population
                my_pop = Population(args, MyGenotype, MyPhenotype, my_objective_dict, my_BC_dict, my_NN)

                # Initialize an empty archive
                my_arch  = BCArchive(args, my_objective_dict, my_BC_dict)

                my_optimization = DSA_ME(args, my_sim, my_env, my_pop, my_arch)

            # run the optimization
            if args.cluster_debug: print("\n*\n*MAP_Elites starting\n*\n*")
            exit_code = my_optimization.run(max_hours_runtime=args.max_run_time, max_gens=args.max_gens, num_random_individuals=args.num_random_inds,
                                    directory=args.run_directory, name=args.run_name, max_eval_time=args.max_eval_time,
                                    time_to_try_again=args.time_to_try_again, checkpoint_every=args.checkpoint_every,
                                    save_vxa_every=args.save_pop_every, save_nets=args.save_nets, save_lineages=args.save_lineages)

        else:  # load checkpoint
            exit_code = continue_from_checkpoint(directory=args.run_directory, max_gens=args.max_gens, max_hours_runtime=args.max_run_time,
                                    max_eval_time=args.max_eval_time, time_to_try_again=args.time_to_try_again,
                                    checkpoint_every=args.checkpoint_every, save_vxa_every=args.save_pop_every,
                                    save_lineages=args.save_lineages)


        # delete unneccassry files
        delete_obsolute_folders(args)


        if args.save_finals_as_data: # save final results to data folder
            dirName = "../results/data"
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            dirName = dirName + "/" + args.run_main
            if not os.path.exists(dirName):
                os.makedirs(dirName)
            dirName = dirName + "/" + args.run_name
            if not os.path.exists(dirName):
                os.makedirs(dirName)

            sub.call("cp -r "+ args.run_directory + "/finalData/" \
                    + " " + dirName + "/seed-" + str(args.seed) + "/", shell=True)
            # also copy the best ind
            path_to_files = args.run_directory + "/bestSoFar/fitOnly"
            pickled_inds = glob(path_to_files + "/*")
            ordered_pickled_inds = natural_sort(pickled_inds, reverse=True)
            sub.call("cp -r "+ ordered_pickled_inds[0] \
                    + " " + dirName + "/seed-" + str(args.seed) + "/", shell=True)

    except:   # error
        exit_code = 1
    return exit_code

if __name__ == "__main__":
    "Parse the arguments"
    args = parse_arguments()
    # hard-coded debugging settings
    if args.debug:
        args = setDebuggingSettings(args)

    # arrange the paths
    if args.run_main is None:
        args.run_main = args.run_directory
    args.run_directory = args.run_abs_path + "/" + args.results_folder_name + "/" + args.run_directory
    args.run_dir_main = args.run_directory
    if args.debug: print("\nArguments parsed\n")

    # check for a previous run, continue from the last checkpoint if possible
    args.continue_from_checkPoint = check_previous_checkpoints(args)

    if not args.continue_from_checkPoint: # initialize the folders
        initialize_main_folders(args)

    if args.seeds is None:  # get the seed if seeds is not defined
        args.seeds = [args.seed]

    for i in range(len(args.seeds)):  # runs for various pre-defined seeds
        args.seed = args.seeds[i]
        if args.debug: print("Run #" + str(i+1) + " out of " + str(len(args.seeds)) + " runs\n\n")
        args.run_directory = args.run_dir_main + "/seed-" + str(args.seed)
        random.seed(args.seed)  # Initializing the random number generator for reproducibility
        np.random.seed(args.seed)

        if args.cluster_debug: print("seed is set!")
        exit_code = main(args)
        if args.cluster_debug: print("main function exit_code: "+ str(exit_code))
        sys.exit(exit_code)

    if args.debug: print("\n\n\n\n\n")
    if args.debug: print("DONE")