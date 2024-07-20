python3.10 ../run.py \
--run_on_cluster 1 \
--run_abs_path  "/your/path/to/this/repo/data_driven_magnetic_soft_material_design" \
--isCPUenabled 1 \
--debug 0 \
--cluster_debug 0 \
--isSaveAllOn True \
--backupALL 0 \
--save_NN_raw_data 1 \
--max_run_time 4 \
--checkpoint_every 50 \
--save_finals_as_data 1 \
--optimizer_type "MAP_Elites_CPPN" \
--explore_strategy "novelty_bias" \
--results_folder_name "results" \
--seed 11 \
--run_main "Step3Dv2" \
--run_directory "Step3Dv2" \
--run_name "Step3Dv2" \
--desired_shape "step3Dv2" \
--isFixedFromTop 0 \
--isFixedFromOneEnd 1 \
--isFloorEnabled 0 \
--fitness_calc_type "nposMSE_Yavg" \
--fitness_maximize 0 \
--BC_type "vol_mag_3D" \
--magnetization_direction "3D" \
--encoding_type "morph_CPPN_mag_direct" \
--ind_size 60 5 1 \
--segment_size 3 5 1 \
--morphStacking_size 60 5 \
--max_gens 5000 \
--pop_size 49 \
--num_random_inds 1 \
--min_volume_ratio 0.6 \
--number_cells_per_BC 50 \
--ME_cx_ratio 0.05 \
--quasi_static_B_magnitude 30e-3 \
--IsMagForceOn 1 \
--M_pervol 20e3 \
--modulus 150e3 \
--sim_time 1 \
--init_time 5e-3 \
--KinEThreshold 1e-15 \
--use_NN 1 \
--NN_mutation_number 250 \
--NN_when_to_use 1e5 \
--NN_data_process_type "beam" \
--NN_sample_weights 0 \
--NN_sample_weights_method "no_weight" \
--mutate_in_parallel 0 \
--material_num  1 \
--isSMP_used  0 \
--SMP_flag 0 0 \
