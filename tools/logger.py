import copy
import time
import sys
import networkx as nx
import subprocess as sub
import numpy as np
from glob import glob
import pickle
import matplotlib.pyplot as plt
import os
import csv

from tools.utils import find_between


def time_stamp():
    # return time.strftime("[%Y/%m/%d-%H:%M:%S]")
    return ""


class PrintLog(object):
    def __init__(self):
        self.timers = {"start": time.time(), "last_call": time.time()}

    def add_timer(self, name):
        assert name not in self.timers
        self.timers[name] = time.time()

    def reset_timer(self, name):
        assert name in self.timers
        if name != "start":
            self.timers[name] = time.time()

    def seconds_from(self, timer_name):
        return time.time() - self.timers[timer_name]

    def message(self, content, timer_name=None, reset=True):
        if timer_name is None:
            print(time_stamp() + ' ' + content)
        else:
            s = self.seconds_from(timer_name)
            m, h = s / 60.0, s / 3600.0
            print(time_stamp() + ' ' + content + ' \t (time from ' + timer_name + ': %0.2fs %0.2fm %0.2fh)' % (s, m, h))
            if reset:
                self.reset_timer(timer_name)
        sys.stdout.flush()
        sys.stderr.flush()


def make_header(population, path):
    _file = open(path, 'w')
    # header_string = "gen\t\tid\t\tage\t\ttype"

    header_string = "gen\t\tid\t\tdom\t\tparent_id\t\tvariation_type"

    # columns for objectives
    for rank in range(len(population.objective_dict)):
        objective = population.objective_dict[rank]
        header_string += "\t\t{}".format(objective["name"]) + "\t\t{}".format("parent_"+objective["name"])

    # columns for network outputs
    ind = population[0]
    output_names = ind.genotype.all_networks_outputs
    output_names.sort()
    # for name in output_names:
    for name, details in ind.genotype.to_phenotype_mapping.items():
        # details = ind.genotype.to_phenotype_mapping[name]
        if details["logging_stats"] is not None:
            header_string += "\t\t" + name + "_different_from_parent"
            for stat in details["logging_stats"]:
                header_string += "\t\t" + stat.__name__ + "_" + name
                header_string += "\t\t" + stat.__name__ + "_parent_" + name
                header_string += "\t\t" + stat.__name__ + "_parent_diff_" + name

    _file.write(header_string + "\n")
    _file.close()


def record_individuals_data(pop, path, num_inds_to_save=None, print_to_terminal=False):

    if num_inds_to_save is None:
        num_inds_to_save = len(pop)

    pop.sort_by_objectives()

    header_list = []
    if print_to_terminal:
        header_list.append('gen')
        header_list.append('id')
        header_list.append('dom')

        # columns for objectives
        for rank in range(len(pop.objective_dict)):
            objective = pop.objective_dict[rank]
            header_list.append(format(objective["name"]))
            header_list.append(format("parent_"+objective["name"]))
        header_list.append('parent_id')
        header_list.append('variation_type')

        header = f""
        for i in range(len(header_list)):
            header+=f"{header_list[i]:^20}|"
        print(header)

    output_names = pop[0].genotype.all_networks_outputs
    output_names.sort()

    recording_file = open(path, 'a')
    n = 0
    while n < num_inds_to_save and n < len(pop):
        ind = pop[n]

        objectives_string = ""

        obj_str_list = []
        obj_str_list.append(str(pop.gen))
        obj_str_list.append(str(ind.id))
        obj_str_list.append(str(len(ind.dominated_by)))

        # objectives
        for rank in range(len(pop.objective_dict)):
            objective = pop.objective_dict[rank]
            objectives_string += "{}\t\t".format(getattr(ind, objective["name"])) + \
                                 "{}\t\t".format(getattr(ind, "parent_{}".format(objective["name"])))
            obj_str_list.append(format(str(getattr(ind, objective["name"]))))
            obj_str_list.append(format(str(getattr(ind, "parent_{}".format(objective["name"])))))

        # network outputs
        for name, details in ind.genotype.to_phenotype_mapping.items():
            if details["logging_stats"] is not None:
                for network, parent_network in zip(ind.genotype, ind.parent_genotype):
                    if name in network.output_node_names:
                        if not network.direct_encoding:
                            state = network.graph.nodes[name]["state"]
                            parent_state = parent_network.graph.nodes[name]["state"]
                        else:
                            state = network.values
                            parent_state = parent_network.values
                        diff = state - parent_state
                        any_changes = np.any(state != parent_state)
                        objectives_string += "{}\t\t".format(any_changes)
                        for stat in details["logging_stats"]:
                            objectives_string += "{}\t\t".format(stat(state))
                            objectives_string += "{}\t\t".format(stat(parent_state))
                            objectives_string += "{}\t\t".format(stat(diff))

        recording_file.write("{}\t\t".format(int(pop.gen)) +
                             "{}\t\t".format(int(ind.id)) +
                             "{}\t\t".format(int(len(ind.dominated_by))) +
                             "{}\t\t".format(int(ind.parent_id)) +
                             ind.variation_type + "\t\t" +
                             objectives_string + "\n")

        if print_to_terminal:
            obj_str_list.append(str(ind.parent_id))
            obj_str_list.append(str(ind.variation_type))

            obj_fstr = f""
            for i in range(len(obj_str_list)):
                obj_fstr+=f"{obj_str_list[i]:^20}|"
            print(obj_fstr)

        n += 1

    recording_file.close()


def initialize_folders(args, population, run_directory, run_name, save_networks, save_all_individual_data=True, save_lineages=True):

    sub.call("mkdir " + run_directory + "/" + " 2>/dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/voxelyzeFiles 2> /dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/tempFiles 2> /dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/fitnessFiles 2> /dev/null", shell=True)

    sub.call("mkdir " + run_directory + "/bestSoFar 2> /dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/bestSoFar/paretoFronts 2> /dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/bestSoFar/fitOnly 2>/dev/null", shell=True)

    sub.call("mkdir " + run_directory + "/pickledPops 2> /dev/null", shell=True)

    sub.call("mkdir " + run_directory + "/generationsData 2> /dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/finalData 2> /dev/null", shell=True)
    sub.call("mkdir " + run_directory + "/NNData 2> /dev/null", shell=True)

    champ_file = run_directory + "/bestSoFar/bestOfGen.txt"
    make_header(population, champ_file)

    if save_all_individual_data:
        sub.call("mkdir " + run_directory + "/allIndividualsData", shell=True)
        sub.call("rm -f " + run_directory + "/allIndividualsData/* 2>/dev/null", shell=True)  # TODO: why clear these

    if save_networks:
        sub.call("mkdir " + run_directory + "/network_gml", shell=True)
        sub.call("rm -rf " + run_directory + "/network_gml/* 2>/dev/null", shell=True)

    if save_lineages:
        sub.call("mkdir " + run_directory + "/ancestors 2> /dev/null", shell=True)



def make_gen_directories(population, run_directory, save_vxa_every, save_networks):

    if population.args.debug or population.args.cluster_debug:
        print("\n\n")
        print ("----------------------------------")
        print ("---------- GENERATION", population.gen, "----------")
        print ("----------------------------------")
        print ("\n")

        # Get the current time in seconds since the epoch
        current_time_seconds = time.time()

        # Convert the time in seconds to a struct_time
        current_struct_time = time.localtime(current_time_seconds)

        # Format the struct_time to a readable string
        formatted_time = time.strftime("%A, %B %d, %Y %I:%M %p", current_struct_time)

        # Print the formatted date and time
        print("Formatted Date and Time:", formatted_time)

    # if population.gen % save_vxa_every == 0 and save_vxa_every > 0:
    sub.call("mkdir " + run_directory + "/generationsData/Gen_" +str(population.gen), shell=True)

    if save_networks:
        sub.call("mkdir " + run_directory + "/network_gml/Gen_%04i" % population.gen, shell=True)

def log_gen_data(pop, log_file):
    if not os.path.isfile(log_file): # log file is not created yet
        with open(log_file, mode='w') as handle:
            csv_writer = csv.writer(handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # write header
            csv_writer.writerow(["gen_num",
                                 "explore?",
                                 "robot_evaluated",
                                 "best_robot",
                                 "best_fit",
                                 "NN_test",
                                 "NN_prediction",
                                 "total_t",
                                 "mut_t",
                                 "eval_t",
                                 "obj_t",
                                 "arch_t",
                                 "novelty_t"])
            handle.close()

    with open(log_file, mode='a') as handle:
        csv_writer = csv.writer(handle, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if pop.NN is None:
            row_list = [str(pop.gen),
                str(pop.explore), 
                str(pop.max_id), 
                str(pop.best_fit_ind_id), 
                str(pop.best_fit_so_far), 
                str(None), 
                str(None), 
                str(pop.gen_tot_time),
                str(pop.gen_mut_time), 
                str(pop.gen_eval_time), 
                str(pop.gen_obj_update_time), 
                str(pop.gen_arch_handle_time),
                str(pop.gen_novelty_calc_time)]
        else:
            row_list = [str(pop.gen),
                        str(pop.explore), 
                        str(pop.max_id), 
                        str(pop.best_fit_ind_id), 
                        str(pop.best_fit_so_far), 
                        str(pop.NN.test_MSE), 
                        str(pop.NN.prediction_MSE), 
                        str(pop.gen_tot_time),
                        str(pop.gen_mut_time), 
                        str(pop.gen_eval_time), 
                        str(pop.gen_obj_update_time), 
                        str(pop.gen_arch_handle_time),
                        str(pop.gen_novelty_calc_time)]
        csv_writer.writerow(row_list)
        handle.close()

def logging_this_gen(population, run_directory):

    log_file = run_directory + "/finalData/genLogs.csv"
    log_gen_data(population, log_file)

def write_gen_stats(population, run_directory, run_name, save_vxa_every, save_pareto, save_networks,
                    save_all_individual_data=True, num_inds_to_save=None, save_lineages=False):
    if population.args.cluster_debug: print("writing the gen stats")
    write_champ_file(population, run_directory)

    if save_all_individual_data:
        write_gen_individuals_data(population, run_directory, num_inds_to_save)

    if save_lineages:  # must be performed every generation
        # each vxa is saved during evaluation in the ancestors folder
        remove_old_lineages(population, run_directory)

    if population.gen % save_vxa_every == 0 and save_vxa_every > 0 and save_networks:
        write_networks(population, run_directory)

    if population.gen % save_vxa_every == 0 and save_vxa_every > 0 and save_pareto:
        write_pareto_front(population, run_directory, run_name)

    sub.call("rm " + run_directory + "/voxelyzeFiles/* 2>/dev/null", shell=True)  # clear the voxelyzeFiles folder

    if population.args.cluster_debug: print("gen stats are written")

def write_champ_file(population, run_directory):
    champ_file = run_directory + "/bestSoFar/bestOfGen.txt"
    record_individuals_data(population, champ_file, population.args.debug)

def write_gen_individuals_data(population, run_directory, num_inds_to_save):
    gen_file = run_directory + "/generationsData/Gen_" +str(population.gen)+"/Gen_" +str(population.gen)+".txt"
    make_header(population, gen_file)
    record_individuals_data(population, gen_file, num_inds_to_save, print_to_terminal=False)

def remove_old_lineages(population, run_directory):
    population.update_lineages()
    print (" Length of best lineage: {}".format(len(population.lineage_dict[population[0].id])) )

    ancestors_ids = [ind.id for ind in population]  # include current generation
    for child, lineage in population.lineage_dict.items():
        for parent in lineage:
            if parent not in ancestors_ids:
                ancestors_ids += [parent]

    for vxa in glob(run_directory + "/ancestors/*"):
        this_id = int(find_between(vxa, "--id_", ".vxa"))
        if this_id not in ancestors_ids:
            sub.call("rm " + vxa, shell=True)

def write_pareto_front(population, run_directory, run_name):
    """Save the vxa of all individuals with min dominance number (top list)."""
    sub.call("mkdir " + run_directory + "/bestSoFar/paretoFronts/Gen_%04i" % population.gen, shell=True)
    ind = population[0]  # first individual
    for individual in population:
        if len(individual.dominated_by) == 0:
            sub.call("mv " + run_directory + "/voxelyzeFiles/" + run_name + "--id_%05i.vxa" % individual.id +
                     " " + run_directory + "/bestSoFar/paretoFronts/Gen_%04i/" % population.gen + "/" +
                     run_name + "Gen_%04i--Fit_%.08f--id_%05i--dom_%d.vxa" %
                     (population.gen, individual.fitness, individual.id, len(individual.dominated_by)), shell=True)
        else:
            break

def write_networks(population, run_directory):
    for individual in population:
        clone = copy.deepcopy(individual)
        net_idx = 0
        for network in clone.genotype:
            for name in network.graph.nodes():
                network.graph.nodes[name]["state"] = ""  # remove state information to reduce file size
                network.graph.nodes[name]["evaluated"] = 0
            nx.write_gml(network.graph, run_directory +
                         "/network_gml/Gen_%04i/network--%02i--fit_%.08f--id_%05i" %
                         (population.gen, net_idx, clone.fitness, clone.id) + ".txt")
            net_idx += 1

def save_current_run_settings(args):
    txtSaveFile = args.run_directory + "/run_settings.txt"
    with open(txtSaveFile, "w") as txt_file:
        txt_file.write("\nSettings of this run \n\n")
        for arg in vars(args):
            txt_file.write(arg + " is set to: " + str(getattr(args, arg)) + " \n")
        txt_file.close()

    pickle_at=args.run_directory + "/run_settings.pickle"
    pickle_thisData_at(args, pickle_at)
    return True

def compare_fitness(isMaximize, best_fitness, new_fitness):
        if isMaximize:  # maximizing the fitness 
            if new_fitness>best_fitness:
                return True
        elif not isMaximize:  # minimizing the fitness 
            if new_fitness<best_fitness:
                return True
        else:
            raise NotImplementedError
        return False

def plot_progress(args, pop, save_directory, high_quality_figures = 0):
    if args.cluster_debug: print("plotting the progress")
    colors = ['darkorange','blue', 'red', 'green']
    facecolors = ['navajowhite','lightblue', 'lightcoral', 'mediumseagreen']
    dpi_value = 150
    if high_quality_figures:
        dpi_value = 1000

    gen = np.arange(pop.gen+1)
    fit_max = np.transpose(np.array([pop.logbook["fitness"]["max"]])).reshape((pop.gen+1),)
    fit_min = np.transpose(np.array([pop.logbook["fitness"]["min"]])).reshape((pop.gen+1),)
    fit_mean = np.transpose(np.array([pop.logbook["fitness"]["mean"]])).reshape((pop.gen+1),)
    fit_stdev = np.transpose(np.array([pop.logbook["fitness"]["stdev"]])).reshape((pop.gen+1),)
    isExplore = np.transpose(np.array([pop.logbook["isExplore"]])).reshape((pop.gen+1),)

    fit_bestSoFar = []
    fit_bestSoFar_changed = []
    bestSoFar = None

    if args.fitness_maximize:
        fit = fit_max
    else:
        fit = fit_min

    for value in fit:
        if bestSoFar is None or compare_fitness(isMaximize=args.fitness_maximize, best_fitness=bestSoFar, new_fitness=value):
            bestSoFar=value
            fit_bestSoFar.append(bestSoFar)
            fit_bestSoFar_changed.append(True)
        else: 
            fit_bestSoFar.append(bestSoFar)
            fit_bestSoFar_changed.append(False)

    fit_bestSoFar = np.transpose(np.array([fit_bestSoFar])).reshape((pop.gen+1),)
    fit_bestSoFar_changed = np.transpose(np.array([fit_bestSoFar_changed])).reshape((pop.gen+1),)

    plt.rcParams['font.size'] = 15
    plt.tick_params(top=False, bottom=False, left=False, right=False,
                    labelleft=False, labelbottom=True)

    # draw the average fitness with std figure 
    fig = plt.figure(figsize=(10,5))
    ax = plt.subplot(111)
    ax.set_title("Mean fitness")
    ax.set_xlabel('Generation #')
    ax.set_ylabel('Fitness')
    ax.plot(gen, fit_mean, color=colors[2], linewidth=3)
    ax.set_xlim((0, 110/100*np.max(gen)))
    ax.set_ylim((0, 110/100*np.max(fit_max)))
    ax.fill_between(gen, fit_mean+fit_stdev, fit_mean-fit_stdev, facecolor=facecolors[2], alpha=0.3)
    # ax.legend(['$\mu$', '\u00B1 $\sigma$'], loc=1)
    plot_file = save_directory + "/progressPlot_fitVSgen.png"
    fig.savefig(plot_file, dpi=dpi_value)
    plt.close()

    # draw the bestSoFar figure
    fig = plt.figure(figsize=(10,5))
    ax = plt.subplot(111)
    ax.set_title("Best fitness")
    ax.set_xlabel('Generation #')
    ax.set_ylabel('Fitness')
    ax.plot(gen, fit_bestSoFar, color=colors[2], linewidth=3)
    ax.set_xlim((0, 110/100*np.max(gen)))
    ax.set_ylim((0, 110/100*np.max(fit_bestSoFar)))
    plot_file = save_directory + "/progressPlot_bestSoFar.png"
    fig.savefig(plot_file, dpi=dpi_value)
    plt.close()


    # draw the bestSoFar figure with explore vs epxloit information
    fig = plt.figure(figsize=(10,5))
    ax = plt.subplot(111)

    fit_bestSoFar_explore = np.ma.masked_where(~((isExplore==True) & (fit_bestSoFar_changed ==True)), fit_bestSoFar)
    fit_bestSoFar_exploit = np.ma.masked_where(~((isExplore==False) & (fit_bestSoFar_changed ==True)), fit_bestSoFar)

    ax.scatter(gen, fit_bestSoFar_explore, s=10*5*2, marker='^', c=colors[1], label="explore")
    ax.scatter(gen, fit_bestSoFar_exploit, s=10*5*2, marker='o', c=colors[3], label="exploit")

    ax.plot(gen, fit_bestSoFar, color=colors[2], linewidth=3)
    ax.set_title("Best fitness")
    ax.set_xlabel('Generation #')
    ax.set_ylabel('Fitness')
    
    ax.set_xlim((0, 110/100*np.max(gen)))
    ax.set_ylim((0, 110/100*np.max(fit_bestSoFar)))

    ax.legend()

    plot_file = save_directory + "/progressPlot_bestSoFar_wexp.png"
    fig.savefig(plot_file, dpi=dpi_value)
    plt.close()

    if args.optimizer_type == "MAP_Elites_CPPN_onNN":
        # draw the bestSoFar figure with N prediction and Sim fitness
        fit_sim_best_soFar = np.transpose(np.array([pop.logbook["best_fit_onSim_GT"]])).reshape((pop.gen+1),)
        fig = plt.figure(figsize=(10,5))
        ax = plt.subplot(111)
        ax.set_title("Best fitness")
        ax.set_xlabel('Generation #')
        ax.set_ylabel('Fitness')
        
        ax.plot(gen, fit_bestSoFar, color=colors[2], linewidth=3)
        ax.plot(gen, fit_sim_best_soFar, color=colors[3], linewidth=3)

        ax.set_xlim((0, 110/100*np.max(gen)))
        ax.set_ylim((0, 110/100*np.max(fit_sim_best_soFar)))
        plot_file = save_directory + "/progressPlot_bestSoFar_NN_Sim_Comp.png"
        fig.savefig(plot_file, dpi=dpi_value)
        plt.close()
    
    # draw the NN prediction error figure
    if pop.start_NN_predictions:
        if args.cluster_debug: print("plotting the NN prediction error progress")
        gen = pop.NN.prediction_errors["generation_number"]
        if args.cluster_debug: print("plotting the NN prediction error progress, gen number data extracted")
        prediction_error = pop.NN.prediction_errors["prediction_error"]
        if args.cluster_debug: print("plotting the NN prediction error progress, prediction_error data extracted")
        explore_mode = pop.NN.prediction_errors["explore"]
        if args.cluster_debug: print("plotting the NN prediction error progress, explore_mode data extracted")
        explore_mode = np.array(explore_mode)

        if args.cluster_debug: print("plotting the NN prediction error progress, data extraction completed")

        fig = plt.figure(figsize=(10,5))
        ax = plt.subplot(111)
        ax.set_title("Mean fitness")
        ax.set_xlabel('Generation #')
        ax.set_ylabel('Prediction error')

        prediction_error_explore = np.ma.masked_where(explore_mode==True, prediction_error)
        prediction_error_exploit = np.ma.masked_where(explore_mode==False, prediction_error)

        if args.cluster_debug: print("plotting the NN prediction error progress, data masked")

        ax.scatter(gen, prediction_error, s=10*prediction_error_explore, marker='^', c=colors[1], label="explore")
        ax.scatter(gen, prediction_error, s=10*prediction_error_exploit, marker='o', c=colors[3], label="exploit")
        ax.legend()

        if args.cluster_debug: print("plotting the NN prediction error progress, scatter part drawn")

        ax.plot(gen, prediction_error, color=colors[2], linewidth=3)
        if args.cluster_debug: print("plotting the NN prediction error progress, line ise drawn")

        if args.cluster_debug: print("plotting the NN prediction error progress, max gen: " + str(np.max(gen)))
        if args.cluster_debug: print("plotting the NN prediction error progress, max prediction error: " + str(np.nanmax(prediction_error)))
        ax.set_xlim((0, 110/100*np.nanmax(gen)))
        ax.set_ylim((0, 110/100*np.nanmax(prediction_error)))

        if args.cluster_debug: print("plotting the NN prediction error progress, limits are set")

        plot_file = save_directory + "/progressPlot_NN_prediction_error.png"
        fig.savefig(plot_file, dpi=dpi_value)
        if args.cluster_debug: print("plotting the NN prediction error progress, figure is saved")
        plt.close()

    if args.cluster_debug: print("plotted the progress figures")
    """Draws with double axes """


def copy_progress_files(args, pop, save_directory):
    "copy the progress files for easier progress checks for human-beings"
    if args.cluster_debug: print("copying the progress updates to the final data folder")

    file_of_interest="map_total_inds_matrix.png"
    os.popen("cp -R "+ args.run_directory + "/archive/"+file_of_interest \
                        + " " + save_directory+"/"+file_of_interest)

    file_of_interest="map_perf_matrix.png"
    os.popen("cp -R "+ args.run_directory + "/archive/"+file_of_interest \
                        + " " + save_directory+"/"+file_of_interest)

    file_of_interest="finalShape3D_sideXZ.png"
    os.popen("cp -R "+ args.run_directory + "/bestSoFar/fitOnly/Ind--id_"+str(pop.best_fit_ind_id).zfill(args.max_ind_1ex)+"/"+file_of_interest \
                        + " " + save_directory+"/"+file_of_interest)
    
    file_of_interest="finalShape3D_isometric.png"
    os.popen("cp -R "+ args.run_directory + "/bestSoFar/fitOnly/Ind--id_"+str(pop.best_fit_ind_id).zfill(args.max_ind_1ex)+"/"+file_of_interest \
                        + " " + save_directory+"/"+file_of_interest)

    if args.cluster_debug: print("progress updates to the final data folder is done")


def save_progress_stats(args, pop, save_directory):
    if args.use_NN:
        assert pop.NN is not None, "NN is None for this pop, NN is somehow not created?"
        pop.NN.save_at_checkpoint(pop.gen)
    sp = dict(args = args, pop = pop)
    with open(save_directory+ "/stats_gen_" + str(pop.gen) + ".pkl", "wb") as handle:
        pickle.dump(sp, handle)
    if args.use_NN:
        pop.NN.load_after_saving_at_checkpoint()

def pickle_thisData_at(thisData, at):
    with open(at, "wb") as handle:
        pickle.dump(thisData, handle)