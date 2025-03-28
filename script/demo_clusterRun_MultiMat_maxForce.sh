python3.10 ../run.py \
--run_on_cluster 1 \
--run_abs_path  "/your/path/to/this/repo/data_driven_magnetic_soft_material_design" \
--isCPUenabled 1 \
--debug 0 \
--isSaveAllOn True \
--backupALL 0 \
--save_NN_raw_data 1 \
--max_run_time 4 \
--checkpoint_every 50 \
--save_finals_as_data 1 \
--seed 11 \
--optimizer_type "MAP_Elites_CPPN" \
--explore_strategy "novelty_bias" \
--results_folder_name "results" \
--run_main "multiMat3DMaxForce" \
--run_directory "multiMat3DMaxForce" \
--run_name "multiMat3DMaxForce" \
--desired_shape "multiM_maxForce" \
--CaseMaxMinPosZ 1 \
--isFixedFromTop 0 \
--isFixedFromOneEnd 0 \
--isFixedFromBothEnd 0 \
--isFixedFromBothTopBottom 1 \
--isFloorEnabled 0 \
--save_force 1 \
--fitness_calc_type "multiM_maxForce" \
--controller_type "quasi-static" \
--fitness_maximize 1 \
--BC_type "vol_mag_3D" \
--magnetization_direction "3D" \
--magnetization_simplified 1 \
--encoding_type "morph_CPPN_mag_direct" \
--ind_size 7 3 30 \
--segment_size 1 1 1 \
--lattice_dim 2e-3 \
--morphStacking_size 10 10 \
--max_gens 5000 \
--pop_size 49 \
--num_random_inds 1 \
--min_volume_ratio 0.2 \
--number_cells_per_BC 50 \
--ME_cx_ratio 0.05 \
--quasi_static_B_magnitude 10e-3 \
--IsMagForceOn 0 \
--M_pervol 20e3 \
--modulus 150e3 \
--sim_time 1 \
--init_time 5e-3 \
--KinEThreshold 1e-15 \
--use_NN 1 \
--NN_mutation_number 250 \
--NN_when_to_use 1e5 \
--novelty_top_gen 500 \
--NN_data_process_type "sheet" \
--NN_sample_weights_method "no_weight" \
--encoding_type "multi_material" \
--DampingBondZ 1 \
--ColBondZ 0.01 \
--SlowBondZ 0.001 \
--isSMP_used 0 \
--material_num 4 \
--material_names "E30" "SS960"  "N108E30"  "N157DS30" \
--M_pervols      0.0    0.0     84e3        62e3      \
--densities      1.07e3 1.45e3  2.41e3       1.86e3    \
--moduli         69e3   1.93e6  150e3        710e3     \
--SMP_flag       0      0       0            0         \
--mutate_in_parallel 0 \
