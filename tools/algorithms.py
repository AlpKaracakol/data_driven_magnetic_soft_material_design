import random
import time
import pickle
import numpy as np
import subprocess as sub
import copy


from src.base import ObjectiveDict
from tools.evaluation import evaluate_in_parallel, update_pop_obj_BC, evaluate_on_surrogate_model, update_pop_obj_BC_onNN
from tools.selection import pareto_selection
from tools.mutation import create_new_children_through_mutation
from tools.logger import save_progress_stats, plot_progress, PrintLog, initialize_folders, make_gen_directories, write_gen_stats, save_current_run_settings, copy_progress_files, logging_this_gen
from tools.utils import getDesiredShape
from tools.control_fields import get_magnetic_control_field

class Optimizer(object):
    def __init__(self, sim, env, evaluation_func=evaluate_in_parallel):
        self.sim = sim
        self.env = env
        if not isinstance(env, list):
            self.env = [env]
        self.evaluate = evaluation_func
        self.curr_env_idx = 0
        self.start_time = None

    def elapsed_time(self, units="s"):
        if self.start_time is None:
            self.start_time = time.time()
        s = time.time() - self.start_time
        if units == "s":
            return s
        elif units == "m":
            return s / 60.0
        elif units == "h":
            return s / 3600.0

    def save_checkpoint(self, directory, gen):
        random_state = random.getstate()
        numpy_random_state = np.random.get_state()

        data = [self, random_state, numpy_random_state]
        with open('{0}/pickledPops/Gen_{1}.pickle'.format(directory, gen), 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def run(self, *args, **kwargs):
        raise NotImplementedError




class PopulationBasedOptimizer(Optimizer):
    def __init__(self, args, sim, env, pop, selection_func, mutation_func):
        Optimizer.__init__(self, sim, env)
        self.pop = pop
        self.select = selection_func
        self.mutate = mutation_func
        self.num_env_cycles = 0
        self.autosuspended = False
        self.max_gens = None
        self.directory = None
        self.name = None
        self.num_random_inds = args.num_random_inds
        self.args = args

        self.desiredShape_VoxPos  = getDesiredShape(args)

    def update_env(self):
        if self.num_env_cycles > 0:
            switch_every = self.max_gens / float(self.num_env_cycles)
            self.curr_env_idx = int(self.pop.gen / switch_every % len(self.env))
            print (" Using environment {0} of {1}".format(self.curr_env_idx+1, len(self.env)))

    def run(self, max_hours_runtime=29, max_gens=3000, num_random_individuals=1, num_env_cycles=0,
            directory="tests_data", name="TestRun",
            max_eval_time=60, time_to_try_again=10, checkpoint_every=100, save_vxa_every=100, save_pareto=False,
            save_nets=False, save_lineages=False, continued_from_checkpoint=False):

        if self.autosuspended:
            sub.call("rm %s/AUTOSUSPENDED" % directory, shell=True)

        self.autosuspended = False
        self.max_gens = max_gens  # can add additional gens through checkpointing

        print_log = PrintLog()
        print_log.add_timer("evaluation")
        print_log.add_timer("statistics")

        self.start_time = print_log.timers["start"]  # sync start time with logging

        # sub.call("clear", shell=True)
        if not continued_from_checkpoint:  # generation zero
            self.directory = directory
            self.name = name
            self.num_random_inds = num_random_individuals
            self.num_env_cycles = num_env_cycles

            # set-up the folders
            initialize_folders(self.args, self.pop, self.directory, self.name, save_nets, save_lineages=save_lineages)
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)
            save_current_run_settings(self.args)


            # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # get the objectives for the ind selection
            self.pop = update_pop_obj_BC(self.args, self.pop)

            # select/sort the population
            self.select(self.pop)  # only produces dominated_by stats, no selection happening (population not replaced)
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                            save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)

        while self.pop.gen < max_gens:

            if self.pop.gen % checkpoint_every == 0:
                print_log.message("Saving checkpoint at generation {0}".format(self.pop.gen+1), timer_name="start")
                self.save_checkpoint(self.directory, self.pop.gen)

            if self.elapsed_time(units="h") > max_hours_runtime:
                self.autosuspended = True
                print_log.message("Autosuspending at generation {0}".format(self.pop.gen+1), timer_name="start")
                self.save_checkpoint(self.directory, self.pop.gen)
                sub.call("touch {0}/AUTOSUSPENDED && rm {0}/RUNNING".format(self.directory), shell=True)
                break

            self.pop.gen += 1
            print_log.message("Creating folders structure for this generation")
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)

            # update ages
            self.pop.update_ages()

            # mutation
            print_log.message("Mutation starts")
            new_children = self.mutate(self.pop, print_log=print_log)
            print_log.message("Mutation ends: successfully generated %d new children." % (len(new_children)))

            # combine children and parents for selection
            print_log.message("Now creating new population")
            self.pop.append(new_children)
            for _ in range(self.num_random_inds):
                print_log.message("Random individual added to population")
                self.pop.add_random_individual()
            print_log.message("New population size is %d" % len(self.pop))

            # evaluate fitness
            print_log.message("Starting fitness evaluation", timer_name="start")
            print_log.reset_timer("evaluation")
            self.update_env()

            # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # get the objectives for the ind selection
            self.pop = update_pop_obj_BC(self.args, self.pop)

            print_log.message("Fitness evaluation finished\n", timer_name="evaluation")  # record total eval time in log

            # perform selection by pareto fronts
            new_population = self.select(self.pop)

            # print population to stdout and save all individual data
            print_log.message("\nSaving statistics", timer_name="start")
            print_log.reset_timer("statistics")
            logging_this_gen(self.pop, self.directory)
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                            save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)
            plot_progress(self.args, self.pop, saveFolderName = self.args.run_directory + "/finalData")

            print_log.message("Saving statistics finished", timer_name="statistics")  # record total eval time in log

            # replace population with selection
            self.pop.individuals = new_population
            print_log.message("Population size reduced to %d" % len(self.pop))

        # save the statistics object seperately
        save_progress_stats(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

        if not self.autosuspended:  # print end of run stats
            print_log.message("Finished {0} generations".format(self.pop.gen + 1))
            print_log.message("DONE!", timer_name="start")
            # sub.call("touch {0}/RUN_FINISHED && rm {0}/RUNNING".format(self.directory), shell=True)


class AFPO(PopulationBasedOptimizer):
    def __init__(self, args, sim, env, pop):
        PopulationBasedOptimizer.__init__(self, args, sim, env, pop, pareto_selection, create_new_children_through_mutation)



# MAP-elites + NN running on the simulation implementation
class ArchiveBasedOptimizer(Optimizer):
    def __init__(self, args, sim, env, pop, archive, mutation_func):
        Optimizer.__init__(self, sim, env)
        self.pop = pop
        self.mutate = mutation_func
        self.num_env_cycles = 0
        self.autosuspended = False
        self.max_gens = None
        self.directory = None
        self.name = None
        self.num_random_inds = args.num_random_inds
        self.args = args
        self.BC_archive = archive

        self.desiredShape_VoxPos  = getDesiredShape(args)

        self.control_field  = None
        if self.args.controller_type != "quasi-static":
            self.args, self.control_field = get_magnetic_control_field(args)

    def update_env(self):
        if self.num_env_cycles > 0:
            switch_every = self.max_gens / float(self.num_env_cycles)
            self.curr_env_idx = int(self.pop.gen / switch_every % len(self.env))
            if self.args.debug: print (" Using environment {0} of {1}".format(self.curr_env_idx+1, len(self.env)))

    def save_checkpoint(self, directory, gen):
        func_start_t = time.time()

        random_state = random.getstate()
        numpy_random_state = np.random.get_state()

        # save the NN
        if self.args.use_NN:
            assert self.pop.NN is not None, "NN is None for this pop, NN is somehow not created?"
            self.pop.NN.save_at_checkpoint(generation=gen)

        # save the BC archive
        self.BC_archive.save_at_checkpoint(self.args, gen)

        # save the optimizer
        data = [self, random_state, numpy_random_state]
        with open('{0}/pickledPops/Gen_{1}.pickle'.format(directory, gen), 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if self.args.use_NN:
            self.pop.NN.load_after_saving_at_checkpoint()

        func_end_t = time.time() - func_start_t
        if self.args.debug: print("Total time to checkpoint: ", func_end_t)


    def return_exit_code(self):
        if self.autosuspended:  # checkpointed , to be continued
            exit_code = 3
        else:                   # done
            exit_code = 0
        return exit_code

    def run(self, max_hours_runtime=29, max_gens=3000, num_random_individuals=1, num_env_cycles=0,
            directory="tests_data", name="TestRun",
            max_eval_time=60, time_to_try_again=10, checkpoint_every=100, save_vxa_every=100, save_pareto=False,
            save_nets=False, save_lineages=False, continued_from_checkpoint=False):

        if self.autosuspended:
            sub.call("rm %s/AUTOSUSPENDED" % directory, shell=True)

        self.autosuspended = False
        self.max_gens = max_gens  # can add additional gens through checkpointing

        # timers
        print_log = PrintLog()
        print_log.add_timer("generation_total_time")
        print_log.add_timer("generation_evaluation")
        print_log.add_timer("generation_mutation")
        print_log.add_timer("generation_objective_update")
        print_log.add_timer("generation_archive_handling")
        print_log.add_timer("statistics")

        self.start_time = print_log.timers["start"]  # sync start time with logging

        if not continued_from_checkpoint:  # generation zero
            self.directory = directory
            self.name = name
            self.num_random_inds = num_random_individuals
            self.num_env_cycles = num_env_cycles

            if self.args.cluster_debug: print("\n\ngeneration zero\n\n")

            # set-up the folders
            initialize_folders(self.args, self.pop, self.directory, self.name, save_nets, save_lineages=save_lineages)
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)
            save_current_run_settings(self.args)

            # if the NN is warm started
            if self.args.NN_warm_start:
                self.pop.NN.load_warm_start(warm_start_file=self.args.NN_warm_start_file)

            # evaluate the initial pop
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos, self.control_field)

            # get the objectives & the behavioural characterizaitons (BCs) for the ind selection
            self.pop = update_pop_obj_BC(self.args, self.pop)

            # print population to stdout and save all individual data
            logging_this_gen(self.pop, self.directory)
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)

            # update the ME archive
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)

            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # end of gen 0
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )


            # select from ME archive
            self.pop.individuals = self.BC_archive.select_pop(self.pop.explore)


        while self.pop.gen < max_gens:

            if self.pop.gen % checkpoint_every == 0:
                if self.args.cluster_debug: print("saving a checkpoint")
                if self.args.debug:  print_log.message("Saving checkpoint at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Saving checkpoint at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                if self.args.cluster_debug: print("checkpoint saved")

            if self.elapsed_time(units="h") > max_hours_runtime:
                if self.args.cluster_debug: print("autosuspending")
                self.autosuspended = True
                if self.args.debug:  print_log.message("Autosuspending at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Autosuspending at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                sub.call("touch {0}/AUTOSUSPENDED && rm {0}/RUNNING".format(self.directory), shell=True)
                if self.args.cluster_debug: print("autosuspended")
                break


            self.pop.gen += 1
            if self.args.cluster_debug: print("\n*\n*\n*\n*\n*\n*Generation: "+str(self.pop.gen)+ "\n*\n*\n*")
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)

            # update ages
            self.pop.update_ages()

            # mutation
            # if self.args.debug:print_log.message("Mutation starts")
            print_log.reset_timer("generation_mutation" )
            new_children = self.mutate(self.pop, print_log=print_log)
            self.pop.gen_mut_time = print_log.seconds_from("generation_mutation" )

            # fill any remaining slots by random individuals
            self.pop.individuals = new_children

            rndm_ind_num = 0
            while (self.args.pop_size + self.args.num_random_inds) > len(self.pop):
                self.pop.add_random_individual()
                rndm_ind_num += 1

            random.shuffle(self.pop.individuals)

            if self.pop.start_NN_predictions:
                for ind in self.pop:
                    if ind.fitness_prediction is None:
                        X_predict = self.pop.NN.convert_robot_params_to_x_predict(ind)
                        Y_predict = self.pop.NN.get_y_predicted(X_predict)
                        ind.fitness_prediction = self.pop.NN.process_y_predict_to_fitness(Y_predict)

            # evaluate fitness
            self.update_env()
            print_log.reset_timer("generation_evaluation")
            # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos, self.control_field)
            self.pop.gen_eval_time = print_log.seconds_from("generation_evaluation")



            # get the objectives for the ind selection
            print_log.reset_timer("generation_objective_update")
            self.pop = update_pop_obj_BC(self.args, self.pop)
            self.pop.gen_obj_update_time = print_log.seconds_from("generation_objective_update")


            # update the ME archive
            # if self.args.debug:print_log.message("BC archive handling started\n", timer_name="start")
            print_log.reset_timer("generation_archive_handling")
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)
            self.pop.gen_novelty_calc_time = self.BC_archive.novelty_time
            self.pop.gen_arch_handle_time = print_log.seconds_from("generation_archive_handling")


            # update the NN prediction error on the evaluations
            if self.pop.start_NN_predictions:
                if self.args.cluster_debug: print("updating the prediction error")
                if self.args.cluster_debug: print("pop robot num: " + str(len(self.pop.individuals)))
                self.pop.NN.update_prediction_error(self.pop)

            # print population to stdout and save all individual data
            print_log.reset_timer("statistics")
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                            save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)
            plot_progress(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            copy_progress_files(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

            # end of pop.gen   N
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            logging_this_gen(self.pop, self.directory)

            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )

            # next generation starts here
            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # update if mutations are guided by NN
            self.pop.update_NN_mutations()

            # select from ME archive
            if self.args.explore_strategy == "novelty_bias":
                if self.pop.gen>self.args.novelty_top_gen:
                    self.args.explore_strategy = "uniform"
                    self.BC_archive.args.explore_strategy = "uniform"
                    self.BC_archive.mees_strategy_explore = "uniform"
            new_population = self.BC_archive.select_pop(self.pop.explore)

            # replace population with selection
            self.pop.individuals = new_population


        # save the statistics object seperately
        save_progress_stats(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

        # save the archive
        self.BC_archive.save_archive(self.args, self.BC_archive, archive_file=None)


        if not self.autosuspended:  # print end of run stats
            if self.args.debug:print_log.message("Finished {0} generations".format(self.pop.gen + 1))
            if self.args.debug:print_log.message("DONE!", timer_name="start")
            
        # return the exit code
        return self.return_exit_code()


class MAP_Elites(ArchiveBasedOptimizer):
    def __init__(self, args, sim, env, pop, archive):
        ArchiveBasedOptimizer.__init__(self, args, sim, env, pop, archive, create_new_children_through_mutation)



# Random Optimizer implementation
class RandomOptimizer(Optimizer):
    def __init__(self, args, sim, env, pop, archive, mutation_func):
        Optimizer.__init__(self, sim, env)
        self.pop = pop
        self.mutate = mutation_func
        self.num_env_cycles = 0
        self.autosuspended = False
        self.max_gens = None
        self.directory = None
        self.name = None
        self.num_random_inds = args.num_random_inds
        self.args = args
        self.BC_archive = archive

        self.desiredShape_VoxPos  = getDesiredShape(args)

    def update_env(self):
        if self.num_env_cycles > 0:
            switch_every = self.max_gens / float(self.num_env_cycles)
            self.curr_env_idx = int(self.pop.gen / switch_every % len(self.env))
            if self.args.debug: print (" Using environment {0} of {1}".format(self.curr_env_idx+1, len(self.env)))

    def save_checkpoint(self, directory, gen):
        func_start_t = time.time()

        random_state = random.getstate()
        numpy_random_state = np.random.get_state()

        # save the NN
        if self.args.use_NN:
            assert self.pop.NN is not None, "NN is None for this pop, NN is somehow not created?"
            self.pop.NN.save_at_checkpoint(generation=gen)

        # save the BC archive
        self.BC_archive.save_at_checkpoint(self.args, gen)

        # save the optimizer
        data = [self, random_state, numpy_random_state]
        with open('{0}/pickledPops/Gen_{1}.pickle'.format(directory, gen), 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if self.args.use_NN:
            self.pop.NN.load_after_saving_at_checkpoint()

        func_end_t = time.time() - func_start_t
        if self.args.debug: print("Total time to checkpoint: ", func_end_t)

    def return_exit_code(self):
        if self.autosuspended:  # checkpointed , to be continued
            exit_code = 3
        else:                   # done
            exit_code = 0
        return exit_code

    def run(self, max_hours_runtime=29, max_gens=3000, num_random_individuals=1, num_env_cycles=0,
            directory="tests_data", name="TestRun",
            max_eval_time=60, time_to_try_again=10, checkpoint_every=100, save_vxa_every=100, save_pareto=False,
            save_nets=False, save_lineages=False, continued_from_checkpoint=False):

        if self.autosuspended:
            sub.call("rm %s/AUTOSUSPENDED" % directory, shell=True)

        self.autosuspended = False
        self.max_gens = max_gens  # can add additional gens through checkpointing

        # timers
        print_log = PrintLog()
        print_log.add_timer("generation_total_time")
        print_log.add_timer("generation_evaluation")
        print_log.add_timer("generation_mutation")
        print_log.add_timer("generation_objective_update")
        print_log.add_timer("generation_archive_handling")
        print_log.add_timer("statistics")

        self.start_time = print_log.timers["start"]  # sync start time with logging

        # sub.call("clear", shell=True)
        if not continued_from_checkpoint:  # generation zero
            self.directory = directory
            self.name = name
            self.num_random_inds = num_random_individuals
            self.num_env_cycles = num_env_cycles

            if self.args.cluster_debug: print("\n\ngeneration zero\n\n")

            # set-up the folders
            initialize_folders(self.args, self.pop, self.directory, self.name, save_nets, save_lineages=save_lineages)
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)
            save_current_run_settings(self.args)

            # if the NN is warm started
            if self.args.NN_warm_start:
                self.pop.NN.load_warm_start(warm_start_file=self.args.NN_warm_start_file)

            # evaluate the initial pop
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # get the objectives & the behavioural characterizaitons (BCs) for the ind selection
            self.pop = update_pop_obj_BC(self.args, self.pop)

            # print population to stdout and save all individual data
            logging_this_gen(self.pop, self.directory)
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)

            # update the ME archive
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)

            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # end of gen 0
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )


            # select from ME archive
            # self.pop.individuals = self.BC_archive.select_pop(self.pop.explore)

            # select/sort the population
            # self.select(self.pop)  # only produces dominated_by stats, no selection happening (population not replaced)

        ## debug case delete later!

        # print("setting the debugging flags")
        # self.pop.args.cluster_debug = 1
        # self.pop.NN.args.cluster_debug = 1
        # self.BC_archive.args.cluster_debug =1
        # self.args.cluster_debug =1
        if self.args.cluster_debug: print("debugging flags are set")

        if self.args.cluster_debug: print("pop generation starting from:"  +str(self.pop.gen))
        if self.args.cluster_debug: print("max generaton set at: " +str(max_gens))

        ## debug case delete later!



        while self.pop.gen < max_gens:

            if self.pop.gen % checkpoint_every == 0:
                if self.args.cluster_debug: print("saving a checkpoint")
                if self.args.debug:  print_log.message("Saving checkpoint at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Saving checkpoint at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                if self.args.cluster_debug: print("checkpoint saved")

            if self.elapsed_time(units="h") > max_hours_runtime:
                if self.args.cluster_debug: print("autosuspending")
                self.autosuspended = True
                if self.args.debug:  print_log.message("Autosuspending at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Autosuspending at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                sub.call("touch {0}/AUTOSUSPENDED && rm {0}/RUNNING".format(self.directory), shell=True)
                if self.args.cluster_debug: print("autosuspended")
                break


            self.pop.gen += 1
            if self.args.cluster_debug: print("\n*\n*\n*\n*\n*\n*Generation: "+str(self.pop.gen)+ "\n*\n*\n*")
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)

            # update ages
            self.pop.update_ages()

            # mutation
            # if self.args.debug:print_log.message("Mutation starts")
            print_log.reset_timer("generation_mutation" )
            # new_children = self.mutate(self.pop, print_log=print_log)
            self.pop.gen_mut_time = print_log.seconds_from("generation_mutation" )

            # fill any remaining slots by random individuals
            # if self.args.debug:print_log.message("Now creating new population")
            # self.pop.individuals = new_children

            self.pop.individuals = []
            rndm_ind_num = 0
            while (self.args.pop_size + self.args.num_random_inds) > len(self.pop):
                self.pop.add_random_individual()
                rndm_ind_num += 1
            # if self.args.debug: print("%d random individual(s) added to population"% rndm_ind_num)
            # if self.args.debug: print_log.message("New population size is %d" % len(self.pop))

            # if self.pop.start_NN_predictions:
            #     for ind in self.pop:
            #         if ind.fitness_prediction is None:
            #             X_predict = self.pop.NN.convert_robot_params_to_x_predict(ind)
            #             Y_predict = self.pop.NN.get_y_predicted(X_predict)
            #             ind.fitness_prediction = self.pop.NN.process_y_predict_to_fitness(Y_predict)
            #             # ind.fitness_prediction = self.pop.compute_NN_prediction(ind)

            # evaluate fitness
            self.update_env()
            print_log.reset_timer("generation_evaluation")
            # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)
            self.pop.gen_eval_time = print_log.seconds_from("generation_evaluation")



            # get the objectives for the ind selection
            print_log.reset_timer("generation_objective_update")
            self.pop = update_pop_obj_BC(self.args, self.pop)
            self.pop.gen_obj_update_time = print_log.seconds_from("generation_objective_update")


            # update the ME archive
            # if self.args.debug:print_log.message("BC archive handling started\n", timer_name="start")
            print_log.reset_timer("generation_archive_handling")
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)
            self.pop.gen_novelty_calc_time = self.BC_archive.novelty_time
            self.pop.gen_arch_handle_time = print_log.seconds_from("generation_archive_handling")


            # update the NN prediction error on the evaluations
            # if self.pop.start_NN_predictions:
            #     if self.args.cluster_debug: print("updating the prediction error")
            #     if self.args.cluster_debug: print("pop robot num: " + str(len(self.pop.individuals)))
            #     self.pop.NN.update_prediction_error(self.pop)

            # print population to stdout and save all individual data
            # if self.args.debug:print_log.message("\nSaving statistics", timer_name="start")
            print_log.reset_timer("statistics")
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                            save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)
            plot_progress(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            copy_progress_files(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            # if self.args.debug:print_log.message("Saving statistics finished\n", timer_name="statistics")  # record total eval time in log

            # end of pop.gen   N
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            logging_this_gen(self.pop, self.directory)

            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )

            # next generation starts here
            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # update if mutations are guided by NN
            # self.pop.update_NN_mutations()

            # select from ME archive
            # if self.args.explore_strategy == "novelty_bias":
            #     if self.pop.gen>self.args.novelty_top_gen:
            #         self.args.explore_strategy = "uniform"
            #         self.BC_archive.args.explore_strategy = "uniform"
            #         self.BC_archive.mees_strategy_explore = "uniform"
            # new_population = self.BC_archive.select_pop(self.pop.explore)

            # replace population with selection
            # self.pop.individuals = new_population
            # if self.args.debug:print_log.message("Population size reduced to %d" % len(self.pop))



        # save the statistics object seperately
        save_progress_stats(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

        # save the archive
        self.BC_archive.save_archive(self.args, self.BC_archive, archive_file=None)


        if not self.autosuspended:  # print end of run stats
            if self.args.debug:print_log.message("Finished {0} generations".format(self.pop.gen + 1))
            if self.args.debug:print_log.message("DONE!", timer_name="start")
            # sub.call("touch {0}/RUN_FINISHED && rm {0}/RUNNING".format(self.directory), shell=True)

        # return the exit code
        return self.return_exit_code()


class RandomOpt(RandomOptimizer):
    def __init__(self, args, sim, env, pop, archive):
        ArchiveBasedOptimizer.__init__(self, args, sim, env, pop, archive, create_new_children_through_mutation)


## MAP-elites on a pre-trained NN-surrogate model --optimizer implementation
class NNsurrogateBasedOptimizer(Optimizer):
    def __init__(self, args, sim, env, pop, archive, mutation_func):
        Optimizer.__init__(self, sim, env, evaluation_func=evaluate_on_surrogate_model)
        self.pop = pop
        self.mutate = mutation_func
        self.num_env_cycles = 0
        self.autosuspended = False
        self.max_gens = None
        self.directory = None
        self.name = None
        self.num_random_inds = args.num_random_inds
        self.args = args
        self.BC_archive = archive

        self.desiredShape_VoxPos  = getDesiredShape(args)

    def update_env(self):
        if self.num_env_cycles > 0:
            switch_every = self.max_gens / float(self.num_env_cycles)
            self.curr_env_idx = int(self.pop.gen / switch_every % len(self.env))
            if self.args.debug: print (" Using environment {0} of {1}".format(self.curr_env_idx+1, len(self.env)))

    def save_checkpoint(self, directory, gen):
        func_start_t = time.time()

        random_state = random.getstate()
        numpy_random_state = np.random.get_state()

        # save the NN
        if self.args.use_NN:
            assert self.pop.NN is not None, "NN is None for this pop, NN is somehow not created?"
            self.pop.NN.save_at_checkpoint(generation=gen)

        # save the BC archive
        self.BC_archive.save_at_checkpoint(self.args, gen)

        # save the optimizer
        data = [self, random_state, numpy_random_state]
        with open('{0}/pickledPops/Gen_{1}.pickle'.format(directory, gen), 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if self.args.use_NN:
            self.pop.NN.load_after_saving_at_checkpoint()

        func_end_t = time.time() - func_start_t
        if self.args.debug: print("Total time to checkpoint: ", func_end_t)


    def return_exit_code(self):
        if self.autosuspended:  # checkpointed , to be continued
            exit_code = 3
        else:                   # done
            exit_code = 0
        return exit_code

    def run(self, max_hours_runtime=29, max_gens=3000, num_random_individuals=1, num_env_cycles=0,
            directory="tests_data", name="TestRun",
            max_eval_time=60, time_to_try_again=10, checkpoint_every=100, save_vxa_every=100, save_pareto=False,
            save_nets=False, save_lineages=False, continued_from_checkpoint=False):

        if self.autosuspended:
            sub.call("rm %s/AUTOSUSPENDED" % directory, shell=True)

        self.autosuspended = False
        self.max_gens = max_gens  # can add additional gens through checkpointing

        # timers
        print_log = PrintLog()
        print_log.add_timer("generation_total_time")
        print_log.add_timer("generation_evaluation")
        print_log.add_timer("generation_mutation")
        print_log.add_timer("generation_objective_update")
        print_log.add_timer("generation_archive_handling")
        print_log.add_timer("statistics")

        self.start_time = print_log.timers["start"]  # sync start time with logging

        # sub.call("clear", shell=True)
        if not continued_from_checkpoint:  # generation zero
            self.directory = directory
            self.name = name
            self.num_random_inds = num_random_individuals
            self.num_env_cycles = num_env_cycles

            if self.args.cluster_debug: print("\n\ngeneration zero\n\n")

            # set-up the folders
            initialize_folders(self.args, self.pop, self.directory, self.name, save_nets, save_lineages=save_lineages)
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)
            save_current_run_settings(self.args)

            # if the NN is warm started
            if self.args.NN_warm_start:
                self.pop.NN.load_warm_start(warm_start_file=self.args.NN_warm_start_file)

            # evaluate the initial pop on surrogate model
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # get the objectives & the behavioural characterizaitons (BCs) for the ind selection
            self.pop = update_pop_obj_BC_onNN(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # print population to stdout and save all individual data
            logging_this_gen(self.pop, self.directory)
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)

            # update the ME archive
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)

            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # end of gen 0
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )


            # select from ME archive
            self.pop.individuals = self.BC_archive.select_pop(self.pop.explore)

            # select/sort the population
            # self.select(self.pop)  # only produces dominated_by stats, no selection happening (population not replaced)

        ## debug case delete later!

        # print("setting the debugging flags")
        # self.pop.args.cluster_debug = 1
        # self.pop.NN.args.cluster_debug = 1
        # self.BC_archive.args.cluster_debug =1
        # self.args.cluster_debug =1
        if self.args.cluster_debug: print("debugging flags are set")

        if self.args.cluster_debug: print("pop generation starting from:"  +str(self.pop.gen))
        if self.args.cluster_debug: print("max generaton set at: " +str(max_gens))

        ## debug case delete later!

        while self.pop.gen < max_gens:

            if self.pop.gen % checkpoint_every == 0:
                if self.args.cluster_debug: print("saving a checkpoint")
                if self.args.debug:  print_log.message("Saving checkpoint at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Saving checkpoint at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                if self.args.cluster_debug: print("checkpoint saved")

            if self.elapsed_time(units="h") > max_hours_runtime:
                if self.args.cluster_debug: print("autosuspending")
                self.autosuspended = True
                if self.args.debug:  print_log.message("Autosuspending at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Autosuspending at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                sub.call("touch {0}/AUTOSUSPENDED && rm {0}/RUNNING".format(self.directory), shell=True)
                if self.args.cluster_debug: print("autosuspended")
                break


            self.pop.gen += 1
            if self.args.cluster_debug: print("\n*\n*\n*\n*\n*\n*Generation: "+str(self.pop.gen)+ "\n*\n*\n*")
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)

            # update ages
            self.pop.update_ages()

            # mutation
            # if self.args.debug:print_log.message("Mutation starts")
            print_log.reset_timer("generation_mutation" )
            new_children = self.mutate(self.pop, print_log=print_log)
            self.pop.gen_mut_time = print_log.seconds_from("generation_mutation" )

            # fill any remaining slots by random individuals
            # if self.args.debug:print_log.message("Now creating new population")
            self.pop.individuals = new_children

            rndm_ind_num = 0
            while (self.args.pop_size + self.args.num_random_inds) > len(self.pop):
                self.pop.add_random_individual()
                rndm_ind_num += 1
            # if self.args.debug: print("%d random individual(s) added to population"% rndm_ind_num)
            # if self.args.debug: print_log.message("New population size is %d" % len(self.pop))

            if self.pop.start_NN_predictions:
                for ind in self.pop:
                    if ind.fitness_prediction is None:
                        X_predict = self.pop.NN.convert_robot_params_to_x_predict(ind)
                        Y_predict = self.pop.NN.get_y_predicted(X_predict)
                        ind.fitness_prediction = self.pop.NN.process_y_predict_to_fitness(Y_predict)
                        # ind.fitness_prediction = self.pop.compute_NN_prediction(ind)

            # evaluate fitness
            self.update_env()
            print_log.reset_timer("generation_evaluation")
            # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
            self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)
            self.pop.gen_eval_time = print_log.seconds_from("generation_evaluation")



            # get the objectives for the ind selection
            print_log.reset_timer("generation_objective_update")
            self.pop = update_pop_obj_BC_onNN(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)
            self.pop.gen_obj_update_time = print_log.seconds_from("generation_objective_update")


            # update the ME archive
            # if self.args.debug:print_log.message("BC archive handling started\n", timer_name="start")
            print_log.reset_timer("generation_archive_handling")
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)
            self.pop.gen_novelty_calc_time = self.BC_archive.novelty_time
            self.pop.gen_arch_handle_time = print_log.seconds_from("generation_archive_handling")


            # update the NN prediction error on the evaluations
            if self.pop.start_NN_predictions:
                if self.args.cluster_debug: print("updating the prediction error")
                if self.args.cluster_debug: print("pop robot num: " + str(len(self.pop.individuals)))
                self.pop.NN.update_prediction_error(self.pop)

            # print population to stdout and save all individual data
            # if self.args.debug:print_log.message("\nSaving statistics", timer_name="start")
            print_log.reset_timer("statistics")
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                            save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)
            plot_progress(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            copy_progress_files(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            # if self.args.debug:print_log.message("Saving statistics finished\n", timer_name="statistics")  # record total eval time in log

            # end of pop.gen   N
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            logging_this_gen(self.pop, self.directory)

            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )

            # next generation starts here
            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # update if mutations are guided by NN
            self.pop.update_NN_mutations()

            # select from ME archive
            if self.args.explore_strategy == "novelty_bias":
                if self.pop.gen>self.args.novelty_top_gen:
                    self.args.explore_strategy = "uniform"
                    self.BC_archive.args.explore_strategy = "uniform"
                    self.BC_archive.mees_strategy_explore = "uniform"
            new_population = self.BC_archive.select_pop(self.pop.explore)

            # replace population with selection
            self.pop.individuals = new_population
            # if self.args.debug:print_log.message("Population size reduced to %d" % len(self.pop))



        # save the statistics object seperately
        save_progress_stats(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

        # save the archive
        self.BC_archive.save_archive(self.args, self.BC_archive, archive_file=None)


        if not self.autosuspended:  # print end of run stats
            if self.args.debug:print_log.message("Finished {0} generations".format(self.pop.gen + 1))
            if self.args.debug:print_log.message("DONE!", timer_name="start")
            # sub.call("touch {0}/RUN_FINISHED && rm {0}/RUNNING".format(self.directory), shell=True)

        # return the exit code
        return self.return_exit_code()


class MAP_elites_on_NNmodel(NNsurrogateBasedOptimizer):
    def __init__(self, args, sim, env, pop, archive):
        NNsurrogateBasedOptimizer.__init__(self, args, sim, env, pop, archive, create_new_children_through_mutation)


# DSA-ME implementation, Deep Surrogate Assisted MAP-Elites
class DSA_ME_Optimizer(Optimizer):
    def __init__(self, args, sim, env, pop, archive, mutation_func):
        Optimizer.__init__(self, sim, env, evaluation_func=evaluate_on_surrogate_model)
        self.pop = pop
        self.mutate = mutation_func
        self.num_env_cycles = 0
        self.autosuspended = False
        self.max_gens = None
        self.directory = None
        self.name = None
        self.num_random_inds = args.num_random_inds
        self.args = args
        self.BC_archive = archive
        self.BC_archive_Surrogate = copy.deepcopy(archive)

        self.desiredShape_VoxPos  = getDesiredShape(args)

    def update_env(self):
        if self.num_env_cycles > 0:
            switch_every = self.max_gens / float(self.num_env_cycles)
            self.curr_env_idx = int(self.pop.gen / switch_every % len(self.env))
            if self.args.debug: print (" Using environment {0} of {1}".format(self.curr_env_idx+1, len(self.env)))

    def save_checkpoint(self, directory, gen):
        func_start_t = time.time()

        random_state = random.getstate()
        numpy_random_state = np.random.get_state()

        # save the NN
        if self.args.use_NN:
            assert self.pop.NN is not None, "NN is None for this pop, NN is somehow not created?"
            self.pop.NN.save_at_checkpoint(generation=gen)

        # save the BC archive
        self.BC_archive.save_at_checkpoint(self.args, gen)
        self.BC_archive_Surrogate.save_at_checkpoint(self.args, gen, file_path = self.BC_archive_Surrogate.checkpoint_folder + "/archiveSurrogateElites_gen" +str(gen)+".tar.gz")

        # save the optimizer
        data = [self, random_state, numpy_random_state]
        with open('{0}/pickledPops/Gen_{1}.pickle'.format(directory, gen), 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        if self.args.use_NN:
            self.pop.NN.load_after_saving_at_checkpoint()

        func_end_t = time.time() - func_start_t
        if self.args.debug: print("Total time to checkpoint: ", func_end_t)


    def return_exit_code(self):
        if self.autosuspended:  # checkpointed , to be continued
            exit_code = 3
        else:                   # done
            exit_code = 0
        return exit_code

    def run(self, max_hours_runtime=29, max_gens=3000, num_random_individuals=1, num_env_cycles=0,
            directory="tests_data", name="TestRun",
            max_eval_time=60, time_to_try_again=10, checkpoint_every=100, save_vxa_every=100, save_pareto=False,
            save_nets=False, save_lineages=False, continued_from_checkpoint=False):

        if self.autosuspended:
            sub.call("rm %s/AUTOSUSPENDED" % directory, shell=True)

        self.autosuspended = False
        self.max_gens = max_gens  # can add additional gens through checkpointing

        # timers
        print_log = PrintLog()
        print_log.add_timer("generation_total_time")
        print_log.add_timer("generation_evaluation")
        print_log.add_timer("generation_mutation")
        print_log.add_timer("generation_objective_update")
        print_log.add_timer("generation_archive_handling")
        print_log.add_timer("statistics")

        self.start_time = print_log.timers["start"]  # sync start time with logging

        # 1st generation
        if not continued_from_checkpoint:  # generation zero
            self.directory = directory
            self.name = name
            self.num_random_inds = num_random_individuals
            self.num_env_cycles = num_env_cycles

            if self.args.cluster_debug: print("\n\ngeneration zero\n\n")

            # set-up the folders
            initialize_folders(self.args, self.pop, self.directory, self.name, save_nets, save_lineages=save_lineages)
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)
            save_current_run_settings(self.args)

            # if the NN is warm started
            if self.args.NN_warm_start:
                self.pop.NN.load_warm_start(warm_start_file=self.args.NN_warm_start_file)


            # # evaluate the initial pop on surrogate model
            # self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # # get the objectives & the behavioural characterizaitons (BCs) for the ind selection
            # self.pop = update_pop_obj_BC_onNN(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)


            # evaluate the initial pop on simulation
            self.pop = evaluate_in_parallel(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)

            # get the objectives for the ind selection
            self.pop = update_pop_obj_BC(self.args, self.pop)

            # end of pop.gen   N
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            logging_this_gen(self.pop, self.directory)


            # print population to stdout and save all individual data
            logging_this_gen(self.pop, self.directory)
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)
            plot_progress(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            copy_progress_files(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

            # update the ME archive
            self.BC_archive_Surrogate.add_population(self.args, self.pop, self.pop.explore)
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)

            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # end of gen 0
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )

            # select from ME archive
            self.pop.individuals = self.BC_archive_Surrogate.select_pop(self.pop.explore)

            # self.pop.NN.evaluation_time_per_generation = self.pop.gen_tot_time/5

        if self.args.cluster_debug: print("debugging flags are set")
        if self.args.cluster_debug: print("pop generation starting from:"  +str(self.pop.gen))
        if self.args.cluster_debug: print("max generaton set at: " +str(max_gens))

        ## debug case delete later!
        while self.pop.gen < max_gens:

            if self.pop.gen % checkpoint_every == 0:
                if self.args.cluster_debug: print("saving a checkpoint")
                if self.args.debug:  print_log.message("Saving checkpoint at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Saving checkpoint at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                if self.args.cluster_debug: print("checkpoint saved")

            if self.elapsed_time(units="h") > max_hours_runtime:
                if self.args.cluster_debug: print("autosuspending")
                self.autosuspended = True
                if self.args.debug:  print_log.message("Autosuspending at generation {0}".format(self.pop.gen+1), timer_name="start")
                if self.args.cluster_debug: print("Autosuspending at generation {0}".format(self.pop.gen+1))
                self.save_checkpoint(self.directory, self.pop.gen)
                sub.call("touch {0}/AUTOSUSPENDED && rm {0}/RUNNING".format(self.directory), shell=True)
                if self.args.cluster_debug: print("autosuspended")
                break


            self.pop.gen += 1
            if self.args.cluster_debug: print("\n*\n*\n*\n*\n*\n*Generation: "+str(self.pop.gen)+ "\n*\n*\n*")
            make_gen_directories(self.pop, self.directory, save_vxa_every, save_nets)

            # update ages
            self.pop.update_ages()

            ##
            ###
            "## Do a ME inner loop, ME on Surrogate model##"
            ###
            ##
            for ME_inner_idx in range(self.args.DSA_ME_innerLoop_num):

                # mutation
                # if self.args.debug:print_log.message("Mutation starts")
                print_log.reset_timer("generation_mutation" )
                new_children = self.mutate(self.pop, print_log=print_log)
                self.pop.gen_mut_time = print_log.seconds_from("generation_mutation" )

                # fill any remaining slots by random individuals
                # if self.args.debug:print_log.message("Now creating new population")
                self.pop.individuals = new_children

                rndm_ind_num = 0
                while (self.args.pop_size + self.args.num_random_inds) > len(self.pop):
                    self.pop.add_random_individual()
                    rndm_ind_num += 1
                # if self.args.debug: print("%d random individual(s) added to population"% rndm_ind_num)
                # if self.args.debug: print_log.message("New population size is %d" % len(self.pop))

                if self.pop.start_NN_predictions:
                    for ind in self.pop:
                        if ind.fitness_prediction is None:
                            X_predict = self.pop.NN.convert_robot_params_to_x_predict(ind)
                            Y_predict = self.pop.NN.get_y_predicted(X_predict)
                            ind.fitness_prediction = self.pop.NN.process_y_predict_to_fitness(Y_predict)
                            # ind.fitness_prediction = self.pop.compute_NN_prediction(ind)

                # evaluate fitness
                self.update_env()
                print_log.reset_timer("generation_evaluation")
                ## this is on surrogate model
                # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
                self.pop = self.evaluate(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)
                self.pop.gen_eval_time = print_log.seconds_from("generation_evaluation")



                # get the objectives for the ind selection
                print_log.reset_timer("generation_objective_update")
                self.pop = update_pop_obj_BC_onNN(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)
                self.pop.gen_obj_update_time = print_log.seconds_from("generation_objective_update")


                # update the ME archive
                # if self.args.debug:print_log.message("BC archive handling started\n", timer_name="start")
                print_log.reset_timer("generation_archive_handling")
                self.BC_archive_Surrogate.add_population(self.args, self.pop, self.pop.explore)
                self.pop.gen_novelty_calc_time = self.BC_archive_Surrogate.novelty_time
                self.pop.gen_arch_handle_time = print_log.seconds_from("generation_archive_handling")


                self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
                logging_this_gen(self.pop, self.directory)

                # new gen calculation starts
                print_log.reset_timer("generation_total_time" )

                # next generation starts here
                # decide if explore mode on
                self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

                # select from ME archive
                if self.args.explore_strategy == "novelty_bias":
                    if self.pop.gen>self.args.novelty_top_gen:
                        self.args.explore_strategy = "uniform"
                        self.BC_archive_Surrogate.args.explore_strategy = "uniform"
                        self.BC_archive_Surrogate.mees_strategy_explore = "uniform"
                new_population = self.BC_archive_Surrogate.select_pop(self.pop.explore)

                # replace population with selection
                self.pop.individuals = new_population
                # if self.args.debug:print_log.message("Population size reduced to %d" % len(self.pop))

            ##
            ###
            "## Do a ME outer loop, ME on Sim, selecting the best only ##"
            ###
            ##
            # pop selection should be the bests from the MAP-Elites
            self.pop.explore = 0 # exploit, select the bests only
            new_population = self.BC_archive_Surrogate.select_pop(self.pop.explore)

            # replace population with selection
            self.pop.individuals = new_population

            # mutate
            new_children = self.mutate(self.pop, print_log=print_log)
            self.pop.gen_mut_time = print_log.seconds_from("generation_mutation" )

            # fill any remaining slots by random individuals
            # if self.args.debug:print_log.message("Now creating new population")
            self.pop.individuals = new_children

            rndm_ind_num = 0
            while (self.args.pop_size + self.args.num_random_inds) > len(self.pop):
                self.pop.add_random_individual()
                rndm_ind_num += 1
            # if self.args.debug: print("%d random individual(s) added to population"% rndm_ind_num)
            # if self.args.debug: print_log.message("New population size is %d" % len(self.pop))

            if self.pop.start_NN_predictions:
                for ind in self.pop:
                    if ind.fitness_prediction is None:
                        X_predict = self.pop.NN.convert_robot_params_to_x_predict(ind)
                        Y_predict = self.pop.NN.get_y_predicted(X_predict)
                        ind.fitness_prediction = self.pop.NN.process_y_predict_to_fitness(Y_predict)
                        # ind.fitness_prediction = self.pop.compute_NN_prediction(ind)

            # evaluate fitness
            self.update_env()
            print_log.reset_timer("generation_evaluation")
            # evaluate the pop, run it at voxelyze, run it in parallel, make an evaluate all function to make this part neater
            self.pop = evaluate_in_parallel(self.args, self.pop, self.sim, self.env[self.curr_env_idx], self.desiredShape_VoxPos)
            self.pop.gen_eval_time = print_log.seconds_from("generation_evaluation")

            # get the objectives for the ind selection
            print_log.reset_timer("generation_objective_update")
            self.pop = update_pop_obj_BC(self.args, self.pop)
            self.pop.gen_obj_update_time = print_log.seconds_from("generation_objective_update")


            # update the ME archive
            # if self.args.debug:print_log.message("BC archive handling started\n", timer_name="start")
            print_log.reset_timer("generation_archive_handling")
            self.BC_archive.add_population(self.args, self.pop, self.pop.explore)
            self.pop.gen_novelty_calc_time = self.BC_archive.novelty_time
            self.pop.gen_arch_handle_time = print_log.seconds_from("generation_archive_handling")


            # update the surrogate ME archive with the ground truth data
            self.BC_archive_Surrogate.update_archive(self.args, self.pop, self.pop.explore)


            # update the NN prediction error on the evaluations
            if self.pop.start_NN_predictions:
                if self.args.cluster_debug: print("updating the prediction error")
                if self.args.cluster_debug: print("pop robot num: " + str(len(self.pop.individuals)))
                self.pop.NN.update_prediction_error(self.pop)

            # print population to stdout and save all individual data
            # if self.args.debug:print_log.message("\nSaving statistics", timer_name="start")
            print_log.reset_timer("statistics")
            write_gen_stats(self.pop, self.directory, self.name, save_vxa_every, save_pareto, save_nets,
                            save_all_individual_data = self.pop.gen % save_vxa_every == 0, save_lineages=save_lineages)
            plot_progress(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            copy_progress_files(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")
            # if self.args.debug:print_log.message("Saving statistics finished\n", timer_name="statistics")  # record total eval time in log

            # end of pop.gen   N
            self.pop.gen_tot_time = print_log.seconds_from("generation_total_time" )
            logging_this_gen(self.pop, self.directory)

            # new gen calculation starts
            print_log.reset_timer("generation_total_time" )

            # next generation starts here
            # decide if explore mode on
            self.pop.explore=True if np.random.random()<self.args.ME_exploit_ratio else False

            # update if mutations are guided by NN
            self.pop.update_NN_mutations()

            # select from surrogate ME archive
            if self.args.explore_strategy == "novelty_bias":
                if self.pop.gen>self.args.novelty_top_gen:
                    self.args.explore_strategy = "uniform"
                    self.BC_archive_Surrogate.args.explore_strategy = "uniform"
                    self.BC_archive_Surrogate.mees_strategy_explore = "uniform"
            new_population = self.BC_archive_Surrogate.select_pop(self.pop.explore)

            # replace population with selection
            self.pop.individuals = new_population
            # if self.args.debug:print_log.message("Population size reduced to %d" % len(self.pop))

            ##
            ###
            "#### Train the NN model befeore the next inner loop starts"
            ###
            ##

            self.pop.NN.train_NN(self.args, epoch_num=self.args.DSA_ME_outerLoop_NNepoch)



        # save the statistics object seperately
        save_progress_stats(self.args, self.pop, save_directory = self.args.run_directory + "/finalData")

        # save the archive
        self.BC_archive.save_archive(self.args, self.BC_archive, archive_file=None)
        self.BC_archive_Surrogate.save_archive(self.args, self.BC_archive_Surrogate, archive_file=self.BC_archive_Surrogate.archive_folder + '/final_archive_surrogate.pickle')




        if not self.autosuspended:  # print end of run stats
            if self.args.debug:print_log.message("Finished {0} generations".format(self.pop.gen + 1))
            if self.args.debug:print_log.message("DONE!", timer_name="start")
            # sub.call("touch {0}/RUN_FINISHED && rm {0}/RUNNING".format(self.directory), shell=True)

        # return the exit code
        return self.return_exit_code()


class DSA_ME(DSA_ME_Optimizer):
    def __init__(self, args, sim, env, pop, archive):
        DSA_ME_Optimizer.__init__(self, args, sim, env, pop, archive, create_new_children_through_mutation)
