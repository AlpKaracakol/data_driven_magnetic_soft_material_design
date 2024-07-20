import numpy as np
import random
import copy
import inspect


import multiprocessing as mp
from multiprocessing import get_context


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

def _mutate_in_serial(ind, BC_dict, objective_dict, args, mutations_NN_guided, pop_max_id, print_log, mutate_network_probs, max_mutation_attempts, popNN):


    if mutations_NN_guided:
        candidates=[]
        X_predict=None


    clone = copy.deepcopy(ind)


    # get the required number of networks
    if mutate_network_probs is None:
        required = 1
    else:
        required = args.ME_mutate_max_network_num

    # select which network to mutate
    selection = []
    while np.sum(selection) < required or np.sum(selection) > required:
        if mutate_network_probs is None:
            # uniformly select networks
            selection = np.random.random(len(clone.genotype)) < 1 / float(len(clone.genotype))
        else:
            # use probability distribution
            selection = np.random.random(len(clone.genotype)) < mutate_network_probs

        # don't select any frozen networks (used to freeze aspects of genotype during evolution)
        for idx in range(len(selection)):
            if clone.genotype[idx].freeze:
                selection[idx] = False

    selected_networks = np.arange(len(clone.genotype))[selection].tolist()

    # record current genes as a parent gene for tracking
    for rank, goal in objective_dict.items():
        setattr(clone, "parent_{}".format(goal["name"]), getattr(clone, goal["name"]))

    if BC_dict is not None:
        for rank, BC in BC_dict.items():
            setattr(clone, "parent_{}".format(BC["name"]), getattr(clone, BC["name"]))

    clone.parent_genotype = ind.genotype
    clone.parent_id = clone.id

    for name, details in clone.genotype.to_phenotype_mapping.items():
        details["old_state"] = copy.deepcopy(details["state"])


    # mutate
    while len(selected_networks)>0:

        selected_net_idx=selected_networks[0]
        mutation_counter = 0
        done = False
        while not done:
            mutation_counter += 1
            candidate = copy.deepcopy(clone)

            # perform mutation(s)
            for _ in range(candidate.genotype[selected_net_idx].num_consecutive_mutations):
                if not clone.genotype[selected_net_idx].direct_encoding:
                    # using CPPNs
                    mut_func_args = inspect.getargspec(candidate.genotype[selected_net_idx].mutate)
                    mut_func_args = [0 for _ in range(1, len(mut_func_args.args))]
                    choice = random.choice(range(len(mut_func_args)))
                    mut_func_args[choice] = 1
                    variation_type, variation_degree = candidate.genotype[selected_net_idx].mutate(*mut_func_args)
                else:
                    # direct encoding with possibility of evolving mutation rate
                    rate = None
                    for net in clone.genotype:
                        if "mutation_rate" in net.output_node_names:
                            rate = net.values  # evolved mutation rates, one for each voxel
                    if "mutation_rate" not in candidate.genotype[selected_net_idx].output_node_names:
                        # use evolved mutation rates
                        variation_type, variation_degree = candidate.genotype[selected_net_idx].mutate(rate)
                    else:
                        # this is the mutation rate itself (use predefined meta-mutation rate)
                        variation_type, variation_degree = candidate.genotype[selected_net_idx].mutate()

            if variation_degree != "":
                candidate.variation_type = "{0}({1})".format(variation_type, variation_degree)
            else:
                candidate.variation_type = str(variation_type)
            candidate.genotype.express()

            if candidate.genotype[selected_net_idx].allow_neutral_mutations:
                done = True
                clone = copy.deepcopy(candidate)
                break
            else:
                isChanged=False
                voxel_map = ind.designParameters["material"]
                Mtheta = ind.segmentedMprofile["Mtheta"]
                Mphi = ind.segmentedMprofile["Mphi"]
                fitness = None

                # check if the mutation changed the parameters
                for name, details in candidate.genotype.to_phenotype_mapping.items():

                    new = details["state"]
                    old = details["old_state"]
                    changes = np.array(new != old, dtype=bool)
                    if not isChanged:
                        isChanged=np.any(changes)

                    if mutations_NN_guided:
                        if name=="material":
                            voxel_map=new
                        if name=="Mtheta":
                            Mtheta=new
                        if name=="Mphi":
                            Mphi=new

                # save the mutated individual
                if isChanged and (selected_net_idx!=0 or candidate.phenotype.is_valid(min_percent_full = args.min_volume_ratio, desired_behavior = args.desired_shape, mat_num = args.material_num, max_percent_full = args.max_volume_ratio )):
                    done = True

                    # if it is exploit mode and NN guided mode --> get a list of candidates
                    if mutations_NN_guided:
                        done = False   #  --> force more mutations to predict with NN
                        voxel_map1D = voxel_map.flatten()
                        Mtheta1D = Mtheta.flatten()
                        Mphi1D = Mphi.flatten()
                        x = np.concatenate((voxel_map1D,Mtheta1D, Mphi1D))
                        X = x.reshape(1, x.size)

                        X_processed = popNN.process_X(args, X)   # normalization

                        if X_predict is not None:
                            X_predict = np.concatenate((X_predict,X_processed), axis=0)
                        else:
                            X_predict = (X_processed)

                        if not candidate.genotype[selected_net_idx].direct_encoding:
                            for output_node in candidate.genotype[selected_net_idx].output_node_names:
                                candidate.genotype[selected_net_idx].graph.nodes[output_node]["old_state"] = ""

                        candidate.id = pop_max_id
                        candidates.append(candidate)

                        if (mutation_counter > max_mutation_attempts) or (len(candidates)>args.NN_mutation_number):
                            done = True
                            list_candidates = [X_predict, candidates]
                            return list_candidates

                    # mutation is done, if not NN guided
                    if done:
                        clone = copy.deepcopy(candidate)
                        break

            if mutation_counter > max_mutation_attempts:
                # return the candidates if it exists for NN prediction
                if mutations_NN_guided and len(candidates)>0:
                    done = True
                    list_candidates = [X_predict, candidates]
                    return list_candidates


                if args.debug: print_log.message("Couldn't find a successful mutation in {} attempts! "
                                    "Skipping this network id: {}".format(max_mutation_attempts, selected_net_idx))
                num_edges = len(clone.genotype[selected_net_idx].graph.edges())
                num_nodes = len(clone.genotype[selected_net_idx].graph.nodes())
                if args.debug: print_log.message("num edges: {0}; num nodes {1}".format(num_edges, num_nodes))

                # select a new network to mutate
                new_selected_net_idx = None
                new_selection = []
                while new_selected_net_idx == selected_net_idx or new_selected_net_idx is None:
                    while np.sum(new_selection) != required or new_selected_net_idx == 0:
                        new_selection = np.random.random(len(clone.genotype)) < mutate_network_probs
                        new_selected_net_idx= None
                    new_selected_net_idx=np.arange(len(clone.genotype))[new_selection].tolist()[0]
                selected_networks.append(new_selected_net_idx)
                break

        # end while for mutation

        # mutation while loop is completed --> selected_network iteration is completed
        selected_networks.pop(0)

        # if mutation is succesfull, erase old state
        if done and not clone.genotype[selected_net_idx].direct_encoding:
            for output_node in clone.genotype[selected_net_idx].output_node_names:
                clone.genotype[selected_net_idx].graph.nodes[output_node]["old_state"] = ""

    # end while for selected networks

    # reset all objectives we calculate in sim to unevaluated values
    for rank, goal in objective_dict.items():
        if goal["tag"] is not None:
            if not goal["name"] == "age":
                setattr(clone, goal["name"], goal["worst_value"])

    # reset all the BC to unevaluated values
    if BC_dict is not None:
        for rank, BC in BC_dict.items():
            setattr(clone, BC["name"], BC["worst_value"])


    clone.id = pop_max_id

    # queue.put(clone)
    return clone


def _mutate_in_parallel(queue, params):

    ind, BC_dict, objective_dict, args, mutations_NN_guided, pop_max_id, print_log, mutate_network_probs, max_mutation_attempts, popNN = params

    if mutations_NN_guided:
        candidates=[]
        X_predict=None


    clone = copy.deepcopy(ind)


    # get the required number of networks
    if mutate_network_probs is None:
        required = 1
    else:
        required = args.ME_mutate_max_network_num

    # select which network to mutate
    selection = []
    while np.sum(selection) < required or np.sum(selection) > required:
        if mutate_network_probs is None:
            # uniformly select networks
            selection = np.random.random(len(clone.genotype)) < 1 / float(len(clone.genotype))
        else:
            # use probability distribution
            selection = np.random.random(len(clone.genotype)) < mutate_network_probs

        # don't select any frozen networks (used to freeze aspects of genotype during evolution)
        for idx in range(len(selection)):
            if clone.genotype[idx].freeze:
                selection[idx] = False

    selected_networks = np.arange(len(clone.genotype))[selection].tolist()

    # record current genes as a parent gene for tracking
    for rank, goal in objective_dict.items():
        setattr(clone, "parent_{}".format(goal["name"]), getattr(clone, goal["name"]))

    if BC_dict is not None:
        for rank, BC in BC_dict.items():
            setattr(clone, "parent_{}".format(BC["name"]), getattr(clone, BC["name"]))

    clone.parent_genotype = ind.genotype
    clone.parent_id = clone.id

    for name, details in clone.genotype.to_phenotype_mapping.items():
        details["old_state"] = copy.deepcopy(details["state"])


    # mutate
    while len(selected_networks)>0:

        selected_net_idx=selected_networks[0]
        mutation_counter = 0
        done = False
        while not done:
            mutation_counter += 1
            candidate = copy.deepcopy(clone)

            # perform mutation(s)
            for _ in range(candidate.genotype[selected_net_idx].num_consecutive_mutations):
                if not clone.genotype[selected_net_idx].direct_encoding:
                    # using CPPNs
                    mut_func_args = inspect.getargspec(candidate.genotype[selected_net_idx].mutate)
                    mut_func_args = [0 for _ in range(1, len(mut_func_args.args))]
                    choice = random.choice(range(len(mut_func_args)))
                    mut_func_args[choice] = 1
                    variation_type, variation_degree = candidate.genotype[selected_net_idx].mutate(*mut_func_args)
                else:
                    # direct encoding with possibility of evolving mutation rate
                    rate = None
                    for net in clone.genotype:
                        if "mutation_rate" in net.output_node_names:
                            rate = net.values  # evolved mutation rates, one for each voxel
                    if "mutation_rate" not in candidate.genotype[selected_net_idx].output_node_names:
                        # use evolved mutation rates
                        variation_type, variation_degree = candidate.genotype[selected_net_idx].mutate(rate)
                    else:
                        # this is the mutation rate itself (use predefined meta-mutation rate)
                        variation_type, variation_degree = candidate.genotype[selected_net_idx].mutate()

            if variation_degree != "":
                candidate.variation_type = "{0}({1})".format(variation_type, variation_degree)
            else:
                candidate.variation_type = str(variation_type)
            candidate.genotype.express()

            if candidate.genotype[selected_net_idx].allow_neutral_mutations:
                done = True
                clone = copy.deepcopy(candidate)  # SAM: ensures change is made to every net
                break
            else:
                isChanged=False
                voxel_map = ind.designParameters["material"]
                Mtheta = ind.segmentedMprofile["Mtheta"]
                Mphi = ind.segmentedMprofile["Mphi"]
                fitness = None

                # check if the mutation changed the parameters
                for name, details in candidate.genotype.to_phenotype_mapping.items():

                    new = details["state"]
                    old = details["old_state"]
                    changes = np.array(new != old, dtype=bool)
                    if not isChanged:
                        isChanged=np.any(changes)

                    if mutations_NN_guided:
                        if name=="material":
                            voxel_map=new
                        if name=="Mtheta":
                            Mtheta=new
                        if name=="Mphi":
                            Mphi=new

                # save the mutated individual
                if isChanged and (selected_net_idx!=0 or candidate.phenotype.is_valid(min_percent_full = args.min_volume_ratio, desired_behavior = args.desired_shape, mat_num = args.material_num, max_percent_full = args.max_volume_ratio)):
                    done = True

                    # if it is exploit mode and NN guided mode --> get a list of candidates
                    if mutations_NN_guided:
                        done = False   #  --> force more mutations to predict with NN
                        voxel_map1D = voxel_map.flatten()
                        Mtheta1D = Mtheta.flatten()
                        Mphi1D = Mphi.flatten()
                        x = np.concatenate((voxel_map1D,Mtheta1D, Mphi1D))
                        X = x.reshape(1, x.size)

                        X_processed = popNN.process_X(args, X)   # normalization

                        if X_predict is not None:
                            X_predict = np.concatenate((X_predict,X_processed), axis=0)
                        else:
                            X_predict = (X_processed)

                        if not candidate.genotype[selected_net_idx].direct_encoding:
                            for output_node in candidate.genotype[selected_net_idx].output_node_names:
                                candidate.genotype[selected_net_idx].graph.nodes[output_node]["old_state"] = ""

                        candidate.id = pop_max_id
                        candidates.append(candidate)

                        if (mutation_counter > max_mutation_attempts) or (len(candidates)>args.NN_mutation_number):
                            done = True
                            list_candidates = [X_predict, candidates]
                            queue.put(list_candidates)
                            return list_candidates

                    # mutation is done, if not NN guided
                    if done:
                        clone = copy.deepcopy(candidate)
                        break

            if mutation_counter > max_mutation_attempts:
                # return the candidates if it exists for NN prediction
                if mutations_NN_guided and len(candidates)>0:
                    done = True
                    list_candidates = [X_predict, candidates]
                    queue.put(list_candidates)
                    return list_candidates


                if args.debug: print_log.message("Couldn't find a successful mutation in {} attempts! "
                                    "Skipping this network id: {}".format(max_mutation_attempts, selected_net_idx))
                num_edges = len(clone.genotype[selected_net_idx].graph.edges())
                num_nodes = len(clone.genotype[selected_net_idx].graph.nodes())
                if args.debug: print_log.message("num edges: {0}; num nodes {1}".format(num_edges, num_nodes))

                # select a new network to mutate
                new_selected_net_idx = None
                new_selection = []
                while new_selected_net_idx == selected_net_idx or new_selected_net_idx is None:
                    while np.sum(new_selection) != required or new_selected_net_idx == 0:
                        new_selection = np.random.random(len(clone.genotype)) < mutate_network_probs
                        new_selected_net_idx= None
                    new_selected_net_idx=np.arange(len(clone.genotype))[new_selection].tolist()[0]
                selected_networks.append(new_selected_net_idx)
                break

        # end while for mutation

        # mutation while loop is completed --> selected_network iteration is completed
        selected_networks.pop(0)

        # if mutation is succesfull, erase old state
        if done and not clone.genotype[selected_net_idx].direct_encoding:
            for output_node in clone.genotype[selected_net_idx].output_node_names:
                clone.genotype[selected_net_idx].graph.nodes[output_node]["old_state"] = ""

    # end while for selected networks

    # reset all objectives we calculate in sim to unevaluated values
    for rank, goal in objective_dict.items():
        if goal["tag"] is not None:
            if not goal["name"] == "age":
                setattr(clone, goal["name"], goal["worst_value"])

    # reset all the BC to unevaluated values
    if BC_dict is not None:
        for rank, BC in BC_dict.items():
            setattr(clone, BC["name"], BC["worst_value"])


    clone.id = pop_max_id

    queue.put(clone)
    return clone

def create_new_childrens_through_cx(ind1, ind2):

    """Create copies, with modification, of existing individuals in the population.

    Parameters
    ----------
    ind1, ind2

    changes the magnetic networks and morphology networks

    Returns
    -------
    new_childrens : list of two inds
        A list of new individual SoftBots.

    """


    clone1 = copy.deepcopy(ind1)
    clone2 = copy.deepcopy(ind2)

    clone1_nx_Mtheta = clone1.genotype.networks[1]
    clone1_nx_Mphi = clone1.genotype.networks[2]
    clone2_nx_morph = clone2.genotype.networks[0]

    candidate1 =copy.deepcopy(ind1)
    candidate2 =copy.deepcopy(ind2)

    candidate1.genotype.networks[0]= clone2_nx_morph
    candidate2.genotype.networks[1]= clone1_nx_Mtheta
    candidate2.genotype.networks[2]= clone1_nx_Mphi

    new_children=[]

    new_children.append(candidate1)
    new_children.append(candidate2)

    return new_children

def create_new_children_through_mutation(pop, print_log, new_children=None, mutate_network_probs=None, max_mutation_attempts=500):

    """Create copies, with modification, of existing individuals in the population.

    Parameters
    ----------
    pop : Population class
        This provides the individuals to mutate.

    print_log : PrintLog()
        For logging

    new_children : a list of new children created outside this function (may be empty)
        This is useful if creating new children through multiple functions, e.g. Crossover and Mutation.

    mutate_network_probs : probability, float between 0 and 1 (inclusive)
        The probability of mutating each network.

    max_mutation_attempts : int
        Maximum number of invalid mutation attempts to allow before giving up on mutating a particular individual.

    Returns
    -------
    new_children : list
        A list of new individual SoftBots.

    """

    if pop.args.cluster_debug: print("\n***Starting the mutations")

    if new_children is None:
        new_children = []
        candidates_cx = []
        candidates= []


    random.shuffle(pop.individuals)

    # do crossover operation to change magnetization profile vs morphology
    if pop.args.ME_cx_ratio>0:
        if pop.args.cluster_debug: print("Starting the crossover operations")
        assert pop.args.ME_cx_ratio<1,  "CX ratio should be smaller than 1"
        while len(candidates_cx) < pop.pop_size*pop.args.ME_cx_ratio:
            # chose two inds from the pop
            inds=None
            while inds is None or pop[inds[0]].id==pop[inds[1]].id:
                inds = np.random.randint(len(pop), size=2)

            childrens=create_new_childrens_through_cx(pop[inds[0]], pop[inds[1]])

            childrens[0].id =pop.max_id
            childrens[0].variation_type="crossover"
            pop.max_id += 1
            childrens[1].id =pop.max_id
            childrens[1].variation_type="crossover"
            pop.max_id += 1

            candidates_cx.append(childrens[0])
            candidates_cx.append(childrens[1])

        for candidate in candidates_cx:
            if pop.start_NN_predictions:
                X_predict = pop.NN.convert_robot_params_to_x_predict(candidate)
                Y_predict = pop.NN.get_y_predicted(X_predict)
                candidate.fitness_prediction = pop.NN.process_y_predict_to_fitness(Y_predict)

            new_children.append(candidate)

        if pop.args.cluster_debug: print("Crossover operations are finished")


    # adjust the mutation probabilities for the networks
    if pop.args.ME_mutation_ratio_magnetization_vs_morphology > 0. and pop.args.ME_mutation_ratio_magnetization_vs_morphology < 1.0 and (pop.args.encoding_type=="morph_CPPN_mag_direct" or pop.args.encoding_type=="multi_material"):
        mag_prob = pop.args.ME_mutation_ratio_magnetization_vs_morphology/2
        morph_prob=1-mag_prob*2
        mutate_network_probs=[morph_prob, mag_prob, mag_prob]

    # sample the ind numbers to mutate
    n_mutate=pop.pop_size-len(candidates_cx)
    indices = np.random.randint(len(pop), size=n_mutate)

    # mutate!   InParallel or not
    if pop.args.mutate_in_parallel:
        if pop.args.cluster_debug: print("mutating the pop in parallel")
        processes=[]
        if not pop.args.run_on_cluster:
            mpx=get_context("spawn")
            qout = mpx.Queue()
        else:
            qout = mp.Queue()

        for index in indices:
            ind = pop[index]
            if not pop.args.run_on_cluster:
                p = mpx.Process(target = _mutate_in_parallel, args = (qout, (ind, pop.BC_dict, pop.objective_dict, pop.args, pop.mutations_NN_guided, pop.max_id,  print_log, mutate_network_probs, max_mutation_attempts, pop.NN),))
            else:
                p = mp.Process(target = _mutate_in_parallel, args = (qout, (ind, pop.BC_dict, pop.objective_dict, pop.args, pop.mutations_NN_guided, pop.max_id,  print_log, mutate_network_probs, max_mutation_attempts, pop.NN),))

            # eval_list.append((ind, pop.BC_dict, pop.objective_dict, pop.args, pop.mutations_NN_guided, pop.max_id,  print_log, mutate_network_probs, max_mutation_attempts))
            pop.max_id += 1
            processes.append(p)
            p.start()

        candidates = [qout.get() for p in processes]

        for p in processes:
            p.join()

        # new children could be a list of inds or sublists of canditates and their design params
        if not pop.mutations_NN_guided:
            if pop.args.cluster_debug: print("list of candidates lenght: "+ str(len(candidates)))
            for candidate in candidates:

                if pop.start_NN_predictions:
                    X_predict = pop.NN.convert_robot_params_to_x_predict(candidate)
                    Y_predict = pop.NN.get_y_predicted(X_predict)
                    candidate.fitness_prediction = pop.NN.process_y_predict_to_fitness(Y_predict)


                new_children.append(candidate)
        else:
            if pop.args.cluster_debug: print("candidates lenght: "+ str(len(candidates)))
            for candidate in candidates:
                if pop.args.cluster_debug: print("candidate lenght: "+ str(len(candidate)))
                if pop.args.cluster_debug: print("total num of mutated candidates: "+ str(len(candidate[0])))

                X_predicts = candidate[0]
                Y_predict = pop.NN.get_y_predicted(X_predicts)

                if pop.args.fitness_maximize:  # maximizing the fitness
                    best_candidate_index= np.argmax(Y_predict)
                else: # minimizing the fitness
                    best_candidate_index= np.argmin(Y_predict)

                best_candidate=candidate[1][best_candidate_index]
                best_candidate.fitness_prediction = pop.NN.process_y_predict_to_fitness(Y_predict[best_candidate_index])


                if pop.args.cluster_debug: print("best canditate predicted fitness: "+ str(best_candidate.fitness_prediction))
                clone = copy.deepcopy(best_candidate)

                # reset all objectives we calculate in sim to unevaluated values
                for rank, goal in pop.objective_dict.items():
                    if goal["tag"] is not None:
                        if not goal["name"] == "age":
                            setattr(clone, goal["name"], goal["worst_value"])

                # reset all the BC to unevaluated values
                if pop.BC_dict is not None:
                    for rank, BC in pop.BC_dict.items():
                        setattr(clone, BC["name"], BC["worst_value"])

                new_children.append(clone)

    else:
        if pop.args.cluster_debug: print("mutating the pop in serial")
        candidates = []
        for index in indices:
            ind = pop[index]
            clones = _mutate_in_serial(ind, pop.BC_dict, pop.objective_dict, pop.args, pop.mutations_NN_guided, pop.max_id,  print_log, mutate_network_probs, max_mutation_attempts, pop.NN)
            pop.max_id += 1
            candidates.append(clones)

        # new children could be a list of inds or sublists of canditates and their design params
        if not pop.mutations_NN_guided:
            if pop.args.cluster_debug: print("list of candidates lenght: "+ str(len(candidates)))
            for candidate in candidates:

                if pop.start_NN_predictions:
                    X_predict = pop.NN.convert_robot_params_to_x_predict(candidate)
                    Y_predict = pop.NN.get_y_predicted(X_predict)
                    candidate.fitness_prediction = pop.NN.process_y_predict_to_fitness(Y_predict)


                new_children.append(candidate)
        else:
            if pop.args.cluster_debug: print("candidates lenght: "+ str(len(candidates)))
            for candidate in candidates:
                if pop.args.cluster_debug: print("candidate lenght: "+ str(len(candidate)))
                if pop.args.cluster_debug: print("total num of mutated candidates: "+ str(len(candidate[0])))

                X_predicts = candidate[0]
                Y_predict = pop.NN.get_y_predicted(X_predicts)

                if pop.args.fitness_maximize:  # maximizing the fitness
                    best_candidate_index= np.argmax(Y_predict)
                else: # minimizing the fitness
                    best_candidate_index= np.argmin(Y_predict)

                best_candidate=candidate[1][best_candidate_index]
                best_candidate.fitness_prediction = pop.NN.process_y_predict_to_fitness(Y_predict[best_candidate_index])


                if pop.args.cluster_debug: print("best canditate predicted fitness: "+ str(best_candidate.fitness_prediction))
                clone = copy.deepcopy(best_candidate)

                # reset all objectives we calculate in sim to unevaluated values
                for rank, goal in pop.objective_dict.items():
                    if goal["tag"] is not None:
                        if not goal["name"] == "age":
                            setattr(clone, goal["name"], goal["worst_value"])

                # reset all the BC to unevaluated values
                if pop.BC_dict is not None:
                    for rank, BC in pop.BC_dict.items():
                        setattr(clone, BC["name"], BC["worst_value"])

                new_children.append(clone)

    if pop.args.cluster_debug: print("***mutations are completed\n")
    return new_children


def genome_wide_mutation(pop, print_log):
    mutate_network_probs = [1 for _ in range(len(pop[0].genotype))]
    return create_new_children_through_mutation(pop, print_log, mutate_network_probs=mutate_network_probs)
