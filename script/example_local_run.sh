python3.10 ../run.py \
--run_on_cluster 1 \
--run_abs_path  "/your/path/to/this/repo/data_driven_magnetic_soft_material_design" \
--isCPUenabled 1 \
--debug 0 \
--cluster_debug 1 \
--isSaveAllOn True \
--backupALL 0 \
--save_NN_raw_data 1 \
--max_run_time 4 \
--checkpoint_every 5 \
--save_finals_as_data 1 \
--optimizer_type "MAP_Elites_CPPN" \
--explore_strategy "novelty_bias" \
--results_folder_name "results" \
--seed 11 \
--run_main "exampleRun" \
--run_directory "exampleRun" \
--run_name "exampleRun" \
--desired_shape "triangleWave" \
--isFixedFromTop 0 \
--isFixedFromOneEnd 1 \
--isFloorEnabled 0 \
--fitness_calc_type "positionMSE" \
--fitness_maximize 0 \
--BC_type "vol_mag_2D" \
--magnetization_direction "2D" \
--encoding_type "morph_CPPN_mag_direct" \
--ind_size 5 2 1 \
--segment_size 1 2 1 \
--morphStacking_size 30 5 \
--max_gens 250 \
--pop_size 14 \
--num_random_inds 1 \
--min_volume_ratio 0.6 \
--number_cells_per_BC 10 \
--ME_cx_ratio 0.05 \
--quasi_static_B_magnitude 30e-3 \
--IsMagForceOn 1 \
--M_pervol 20e3 \
--modulus 150e3 \
--sim_time 1 \
--init_time 5e-3 \
--KinEThreshold 1e-15 \
--use_NN 1 \
--NN_mutation_number 25 \
--NN_when_to_use 1e3 \
--NN_data_process_type "beam" \
--NN_sample_weights 0 \
--NN_sample_weights_method "no_weight" \
--mutate_in_parallel 0 \
--material_num  1 \
--isSMP_used  0 \
--SMP_flag 0 0 \
