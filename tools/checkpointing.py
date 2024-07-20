import random
import pickle
import numpy as np
import subprocess as sub
from glob import glob
from tools.utils import natural_sort


def continue_from_checkpoint(directory="tests_data", max_gens=3000, max_hours_runtime=29,
                             max_eval_time=60, time_to_try_again=10, checkpoint_every=1, save_vxa_every=1,
                             save_pareto=False, save_nets=False, save_lineages=False):

    sub.call("rm -f %s/voxelyzeFiles/*" % directory, shell=True)  # remove partial results

    successful_restart = False
    pickle_idx = 0
    while not successful_restart:
        try:
            pickled_pops = glob(directory + "/pickledPops/*")
            last_gen = natural_sort(pickled_pops, reverse=True)[pickle_idx]
            with open(last_gen, 'rb') as handle:
                [optimizer, random_state, numpy_random_state] = pickle.load(handle)
            if optimizer.args.use_NN:
                optimizer.pop.NN.load_at_checkpoint(optimizer.pop.gen)
            optimizer.BC_archive.load_at_checkpoint(optimizer.args, optimizer.pop.gen)
            if optimizer.args.optimizer_type == "DSA_ME":
                optimizer.BC_archive_Surrogate.load_at_checkpoint(optimizer.args, optimizer.pop.gen, file_path = optimizer.BC_archive_Surrogate.checkpoint_folder + "/archiveSurrogateElites_gen" +str(optimizer.pop.gen)+".tar.gz")
                
            successful_restart = True

        except EOFError:
            # something went wrong writing the checkpoint : use previous checkpoint and redo last generation
            sub.call("touch {}/IO_ERROR_$(date +%F_%R)".format(directory), shell=True)
            pickle_idx += 1
            pass

    random.setstate(random_state)
    np.random.set_state(numpy_random_state)

    
    try:
        print("cluster debug is set to: ", optimizer.args.cluster_debug)
    except:
        optimizer.args.cluster_debug = 0
        optimizer.pop.args.cluster_debug = 0
        optimizer.pop.NN.args.cluster_debug = 0
        optimizer.BC_archive.args.cluster_debug = 0
        
    # if 'a' in vars() or 'a' in globals():
    # better way to handle this instead of try/except block

    if optimizer.pop.gen < max_gens:
        exit_code = optimizer.run(continued_from_checkpoint=True, max_hours_runtime=max_hours_runtime, max_gens=max_gens,
                        max_eval_time=max_eval_time, time_to_try_again=time_to_try_again,
                        checkpoint_every=checkpoint_every, save_vxa_every=save_vxa_every,
                        save_lineages=save_lineages, save_nets=save_nets, save_pareto=save_pareto)

    return exit_code