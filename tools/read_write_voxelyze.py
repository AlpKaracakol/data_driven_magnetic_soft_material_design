import os
import time
import math
import numpy as np
from glob import glob
import xml.etree.ElementTree as ET

from tools.utils import natural_sort


def read_voxlyze_results(population, print_log, filename="softbotsOutput.xml"):
    i = 0
    max_attempts = 60
    file_size = 0
    this_file = ""

    while (i < max_attempts) and (file_size == 0):
        try:
            file_size = os.stat(filename).st_size
            this_file = open(filename)
            this_file.close()
        except ImportError:
            file_size = 0
        i += 1
        time.sleep(1)

    if file_size == 0:
        print_log.message("ERROR: Cannot find a non-empty fitness file in %d attempts: abort" % max_attempts)
        exit(1)

    results = {rank: None for rank in range(len(population.objective_dict))}
    for rank, details in population.objective_dict.items():
        this_file = open(filename) 
        tag = details["tag"]
        if tag is not None:
            for line in this_file:
                if tag in line:
                    results[rank] = float(line[line.find(tag) + len(tag):line.find("</" + tag[1:])])
        this_file.close()

    return results

"Voxelyze handlers"
def write_voxelyze_file(args, sim, env, individual, run_directory, run_name):

    # hot fix for previous version compability
    try:
        if args.isFixedFromTop is None:
            args.isFixedFromTop = 0
        if args.isFixedFromBottom is None:
            args.isFixedFromBottom = 0
        if args.isFixedFromBothTopBottom is None:
            args.isFixedFromBothTopBottom = 0
        
    except: 
        args.isFixedFromTop = 0
        args.isFixedFromBottom = 0
        args.isFixedFromBothTopBottom = 0

    if args.desired_shape == "max_COM_z_symmetry":
        individual.genotype.orig_size_xyz = (args.ind_size[0]*2, individual.genotype.orig_size_xyz[1], individual.genotype.orig_size_xyz[2])
        
        name = "material"
        morphology = individual.designParameters[name]
        morphology_sym = np.flip(morphology, axis=0)
        individual.designParameters[name] = np.concatenate((morphology,morphology_sym), axis=0)


        name = "Mtheta"
        a = individual.designParameters[name]
        a_sym = np.flip(a, axis=0)
        b = a_sym.copy()
        shape_ind = a_sym.shape
        for k in range(shape_ind[2]):
            for j in range(shape_ind[1]):
                for i in range(shape_ind[0]):
                    if b[i,j,k] == 0:
                        b[i,j,k] = math.pi
                    else:
                        b[i,j,k] = 0        

        individual.designParameters[name] = np.concatenate((a,b), axis=0)

        name = "Mphi"
        a = individual.designParameters[name]
        a_sym = np.flip(a, axis=0)
        individual.designParameters[name] = np.concatenate((a,a_sym), axis=0)

    # update any env variables based on outputs instead of writing outputs in
    for name, details in individual.genotype.to_phenotype_mapping.items():
        if details["env_kws"] is not None:
            for env_key, env_func in details["env_kws"].items():
                setattr(env, env_key, env_func(details["state"]))  # currently only used when evolving frequency

    voxelyze_file = open(run_directory + "/voxelyzeFiles/" + run_name + "--id_" + str(individual.id).zfill(args.max_ind_1ex) + ".vxa" , "w")

    voxelyze_file.write(
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
        <VXA Version=\"1.0\">\n\
        <Simulator>\n")

    # Sim
    for name, tag in sim.new_param_tag_dict.items():
        voxelyze_file.write(tag + str(getattr(sim, name)) + "</" + tag[1:] + "\n")

    voxelyze_file.write(
        "<Integration>\n\
        <Integrator>0</Integrator>\n\
        <DtFrac>" + str(args.dt_frac) + "</DtFrac>\n\
        </Integration>\n\
        <Damping>\n\
        <BondDampingZ>"+ str(args.DampingBondZ) +"</BondDampingZ>\n\
        <ColDampingZ>" + str(args.ColBondZ) + "</ColDampingZ>\n\
        <SlowDampingZ>" + str(args.SlowBondZ) + "</SlowDampingZ>\n\
        </Damping>\n\
        <Collisions>\n\
        <SelfColEnabled>" + str(int(sim.self_collisions_enabled)) + "</SelfColEnabled>\n\
        <ColSystem>3</ColSystem>\n\
        <CollisionHorizon>2</CollisionHorizon>\n\
        </Collisions>\n\
        <Features>\n\
        <FluidDampEnabled>0</FluidDampEnabled>\n\
        <PoissonKickBackEnabled>0</PoissonKickBackEnabled>\n\
        <EnforceLatticeEnabled>0</EnforceLatticeEnabled>\n\
        </Features>\n\
        <SurfMesh>\n\
        <CMesh>\n\
        <DrawSmooth>1</DrawSmooth>\n\
        <Vertices/>\n\
        <Facets/>\n\
        <Lines/>\n\
        </CMesh>\n\
        </SurfMesh>\n\
        <StopCondition>\n\
        <StopConditionType>" + str(int(sim.stop_condition)) + "</StopConditionType>\n\
        <StopConditionValue>" + str(args.sim_time) + "</StopConditionValue>\n\
        <AfterlifeTime>" + str(sim.afterlife_time) + "</AfterlifeTime>\n\
        <MidLifeFreezeTime>" + str(sim.mid_life_freeze_time) + "</MidLifeFreezeTime>\n\
        <InitCmTime>" + str(sim.fitness_eval_init_time) + "</InitCmTime>\n\
        </StopCondition>\n\
        <EquilibriumMode>\n\
        <EquilibriumModeEnabled>" + str(sim.equilibrium_mode) + "</EquilibriumModeEnabled>\n\
        </EquilibriumMode>\n\
        <GA>\n\
        <WriteFitnessFile>1</WriteFitnessFile>\n\
        <FitnessFileName>" + run_directory + "/fitnessFiles/softbotsOutput--id_%05i.xml" % individual.id +
        "</FitnessFileName>\n\
        <QhullTmpFile>" + run_directory + "/tempFiles/qhullInput--id_%05i.txt" % individual.id + "</QhullTmpFile>\n\
        <CurvaturesTmpFile>" + run_directory + "/tempFiles/curvatures--id_%05i.txt" % individual.id +
        "</CurvaturesTmpFile>\n\
        </GA>\n\
        <MinTempFact>" + str(sim.min_temp_fact) + "</MinTempFact>\n\
        <MaxTempFactChange>" + str(sim.max_temp_fact_change) + "</MaxTempFactChange>\n\
        <MaxStiffnessChange>" + str(sim.max_stiffness_change) + "</MaxStiffnessChange>\n\
        <MinElasticMod>" + str(sim.min_elastic_mod) + "</MinElasticMod>\n\
        <MaxElasticMod>" + str(sim.max_elastic_mod) + "</MaxElasticMod>\n\
        <ErrorThreshold>" + str(0) + "</ErrorThreshold>\n\
        <ThresholdTime>" + str(0) + "</ThresholdTime>\n\
        <MaxKP>" + str(0) + "</MaxKP>\n\
        <MaxKI>" + str(0) + "</MaxKI>\n\
        <MaxANTIWINDUP>" + str(0) + "</MaxANTIWINDUP>\n")

    if hasattr(individual, "parent_lifetime"):
        if individual.parent_lifetime > 0:
            voxelyze_file.write("<ParentLifetime>" + str(individual.parent_lifetime) + "</ParentLifetime>\n")
        elif individual.lifetime > 0:
            voxelyze_file.write("<ParentLifetime>" + str(individual.lifetime) + "</ParentLifetime>\n")

    voxelyze_file.write("</Simulator>\n")

    # Env
    voxelyze_file.write("<Environment>\n")
    for name, tag in env.new_param_tag_dict.items():
        voxelyze_file.write(tag + str(getattr(env, name)) + "</" + tag[1:] + "\n")

    voxelyze_file.write(
        "<Fixed_Regions>\n\
        <NumFixed>0</NumFixed>\n\
        </Fixed_Regions>\n\
        <Forced_Regions>\n\
        <NumForced>0</NumForced>\n\
        </Forced_Regions>\n")

    fixedFrom = [args.isFixedFromOneEnd, args.isFixedFromTop, args.isFixedFromBottom, args.isFixedFromBothEnd, args.isFixedFromBothTopBottom]
    if sum(fixedFrom)>1:
        print("\n*\n**\nCheck the fixed end? Something is wrong!\n**\n*\n")
        raise NotImplementedError

    if args.isFixedFromOneEnd:
        voxelyze_file.write(
            "<Boundary_Conditions>\n\
              <NumBCs>1</NumBCs>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0</X>\n\
                <Y>0</Y>\n\
                <Z>0</Z>\n\
                <dX>0.01</dX>\n\
                <dY>1</dY>\n\
                <dZ>1</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
            </Boundary_Conditions>\n")
    
    if args.isFixedFromBothEnd:
        voxelyze_file.write(
            "<Boundary_Conditions>\n\
              <NumBCs>2</NumBCs>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0</X>\n\
                <Y>0</Y>\n\
                <Z>0</Z>\n\
                <dX>0.01</dX>\n\
                <dY>1</dY>\n\
                <dZ>1</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0.99</X>\n\
                <Y>0</Y>\n\
                <Z>0</Z>\n\
                <dX>0.01</dX>\n\
                <dY>1</dY>\n\
                <dZ>1</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
            </Boundary_Conditions>\n")

    if args.isFixedFromTop:
        voxelyze_file.write(
            "<Boundary_Conditions>\n\
              <NumBCs>1</NumBCs>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0</X>\n\
                <Y>0</Y>\n\
                <Z>0.99</Z>\n\
                <dX>1</dX>\n\
                <dY>1</dY>\n\
                <dZ>0.01</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
            </Boundary_Conditions>\n")

    if args.isFixedFromBottom:
        voxelyze_file.write(
            "<Boundary_Conditions>\n\
              <NumBCs>1</NumBCs>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0</X>\n\
                <Y>0</Y>\n\
                <Z>0</Z>\n\
                <dX>1</dX>\n\
                <dY>1</dY>\n\
                <dZ>0.01</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
            </Boundary_Conditions>\n")

    if args.isFixedFromBothTopBottom:
        voxelyze_file.write(
            "<Boundary_Conditions>\n\
              <NumBCs>2</NumBCs>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0</X>\n\
                <Y>0</Y>\n\
                <Z>0</Z>\n\
                <dX>1</dX>\n\
                <dY>1</dY>\n\
                <dZ>0.01</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
              <FRegion>\n\
                <PrimType>0</PrimType>\n\
                <X>0</X>\n\
                <Y>0</Y>\n\
                <Z>0.99</Z>\n\
                <dX>1</dX>\n\
                <dY>1</dY>\n\
                <dZ>0.01</dZ>\n\
                <Radius>0</Radius>\n\
                <R>0.4</R>\n\
                <G>0.6</G>\n\
                <B>0.4</B>\n\
                <alpha>1</alpha>\n\
                <DofFixed>63</DofFixed>\n\
                <ForceX>0</ForceX>\n\
                <ForceY>0</ForceY>\n\
                <ForceZ>0</ForceZ>\n\
                <TorqueX>0</TorqueX>\n\
                <TorqueY>0</TorqueY>\n\
                <TorqueZ>0</TorqueZ>\n\
                <DisplaceX>0</DisplaceX>\n\
                <DisplaceY>0</DisplaceY>\n\
                <DisplaceZ>0</DisplaceZ>\n\
                <AngDisplaceX>0</AngDisplaceX>\n\
                <AngDisplaceY>0</AngDisplaceY>\n\
                <AngDisplaceZ>0</AngDisplaceZ>\n\
              </FRegion>\n\
            </Boundary_Conditions>\n")



    voxelyze_file.write(
        "<Gravity>\n\
        <GravEnabled>" + str(env.gravity_enabled) + "</GravEnabled>\n\
        <GravAcc>-9.81</GravAcc>\n\
        <FloorEnabled>" + str(args.isFloorEnabled) + "</FloorEnabled>\n\
        <FloorSlope>" + str(args.FloorSlope) + "</FloorSlope>\n\
        </Gravity>\n\
        <Thermal>\n\
        <TempEnabled>" + str(env.temp_enabled) + "</TempEnabled>\n\
        <TempAmp>" + str(env.temp_amp) + "</TempAmp>\n\
        <TempBase>25</TempBase>\n\
        <VaryTempEnabled>1</VaryTempEnabled>\n\
        <TempPeriod>" + str(1.0 / env.frequency) + "</TempPeriod>\n\
        </Thermal>\n\
        <TimeBetweenTraces>" + str(env.time_between_traces) + "</TimeBetweenTraces>\n\
        <StickyFloor>" + str(env.sticky_floor) + "</StickyFloor>\n\
        </Environment>\n")

    voxelyze_file.write(
        "<VXC Version=\"0.93\">\n\
        <Lattice>\n\
        <Lattice_Dim>" + str(args.lattice_dim) + "</Lattice_Dim>\n\
        <X_Dim_Adj>1</X_Dim_Adj>\n\
        <Y_Dim_Adj>1</Y_Dim_Adj>\n\
        <Z_Dim_Adj>1</Z_Dim_Adj>\n\
        <X_Line_Offset>0</X_Line_Offset>\n\
        <Y_Line_Offset>0</Y_Line_Offset>\n\
        <X_Layer_Offset>0</X_Layer_Offset>\n\
        <Y_Layer_Offset>0</Y_Layer_Offset>\n\
        </Lattice>\n\
        <Voxel>\n\
        <Vox_Name>BOX</Vox_Name>\n\
        <X_Squeeze>1</X_Squeeze>\n\
        <Y_Squeeze>1</Y_Squeeze>\n\
        <Z_Squeeze>1</Z_Squeeze>\n\
        </Voxel>\n")

    if not args.encoding_type=="multi_material":
        voxelyze_file.write(
            "<Palette>\n\
                <Material ID=\"1\">\n\
                <MatType>0</MatType>\n\
                <Name>MagSoElas</Name>\n\
                <Display>\n\
                <Red>" + str(args.voxel_color[0]) + "</Red>\n\
                <Green>" + str(args.voxel_color[1]) + "</Green>\n\
                <Blue>" + str(args.voxel_color[2]) + "</Blue>\n\
                <Alpha>" + str(args.voxel_color[3]) + "</Alpha>\n\
                </Display>\n\
                <Mechanical>\n\
                <MatModel>0</MatModel>\n\
                <Elastic_Mod>" + str(args.modulus) + "</Elastic_Mod>\n\
                <Plastic_Mod>0</Plastic_Mod>\n\
                <Yield_Stress>0</Yield_Stress>\n\
                <FailModel>0</FailModel>\n\
                <Fail_Stress>0</Fail_Stress>\n\
                <Fail_Strain>0</Fail_Strain>\n\
                <Density>" + str(args.density)+  "</Density>\n\
                <Poissons_Ratio>" + str(args.poissons)+ "</Poissons_Ratio>\n\
                <CTE>0</CTE>\n\
                <uStatic>" + str(args.FrictionStatic)+ "</uStatic>\n\
                <uDynamic>" + str(args.FrictionDynamic)+ "</uDynamic>\n\
                </Mechanical>\n\
                <Magnetic>\n\
                <M_per_vol>" + str(args.M_pervol) + "</M_per_vol>\n\
                </Magnetic>\n\
            </Material>\n\
            </Palette>\n")
    elif args.encoding_type=="multi_material":

        voxelyze_file.write(
            "<Palette>\n")


        def get_color_map(material_names):
            # mat_color_map = {
            #         0: "#FFFFFF",   # White
            #         1: "#000000",   # Black
            #         2: "#808080",    # Gray
            #         3: "#40E0D0",    # Turquoise
            #         4: "#FFD700"    # Golden yellow
            #         5: "#5F021F",    # Red
            #         6: "#228c22"    # Froest Green
            #     }

            mat_color_map = {0: "#FFFFFF"}
            mat_color_map[material_names.index("E30")+1] = "#FFD700"
            mat_color_map[material_names.index("N108E30")+1] = "#000000"
            mat_color_map[material_names.index("N157DS30")+1] = "#808080"
            mat_color_map[material_names.index("SS960")+1] = "#40E0D0"
            try:
                mat_color_map[material_names.index("smpMAG")+1] = "#5F021F"
                mat_color_map[material_names.index("smpPAS")+1] = "#228c22"
                return mat_color_map
            except:
                return mat_color_map


        mat_color_map = get_color_map(args.material_names)

        for mat_num in range(args.material_num):
            mat_id = mat_num+1
            mat_color = mat_color_map[mat_id]

            def hex_to_rgb(hex_color):
                # Remove the '#' symbol if it's present
                hex_color = hex_color.lstrip('#')
                
                # Convert the hex color code to an integer
                value = int(hex_color, 16)
                
                # Extract the red, green, and blue components
                red = (value >> 16) & 255
                green = (value >> 8) & 255
                blue = value & 255
                
                return (red, green, blue)
            
            def rgb_0_to_1(rgb_color):
                # Ensure that the RGB values are in the 0-255 range
                red, green, blue = rgb_color
                red = min(255, max(0, red))
                green = min(255, max(0, green))
                blue = min(255, max(0, blue))
                
                # Convert to the 0-1 range
                red_normalized = red / 255.0
                green_normalized = green / 255.0
                blue_normalized = blue / 255.0
                
                return (red_normalized, green_normalized, blue_normalized)
        
            hex_color = mat_color
            rgb_color = hex_to_rgb(hex_color)
            rgb_normalized = rgb_0_to_1(rgb_color)

            
            if args.isSMP_used and args.SMP_flag[mat_num]==1:
                if args.SMP_flag[mat_num]:
                    if args.material_names.index("smpPAS") == mat_num:
                        _Emoduli = args.SMP_moduli_passive[1] if args.isSMP_heated else args.SMP_moduli_passive[0] 
                    elif args.material_names.index("smpMAG") == mat_num:
                        _Emoduli = args.SMP_moduli_responsive[1] if args.isSMP_heated else args.SMP_moduli_responsive[0] 
            else:
                _Emoduli = args.moduli[mat_num]

                
            voxelyze_file.write("\
            <Material ID=\""+ str(mat_id) +"\">\n\
                <MatType>"+str(0)+"</MatType>\n\
                <Name>"+str(args.material_names[mat_num])+"</Name>\n\
                <Display>\n\
                <Red>" + str(rgb_normalized[0]) + "</Red>\n\
                <Green>" + str(rgb_normalized[1]) + "</Green>\n\
                <Blue>" + str(rgb_normalized[2]) + "</Blue>\n\
                <Alpha>" + str(args.voxel_color[3]) + "</Alpha>\n\
                </Display>\n\
                <Mechanical>\n\
                <MatModel>0</MatModel>\n\
                <Elastic_Mod>" + str(_Emoduli) + "</Elastic_Mod>\n\
                <Plastic_Mod>0</Plastic_Mod>\n\
                <Yield_Stress>0</Yield_Stress>\n\
                <FailModel>0</FailModel>\n\
                <Fail_Stress>0</Fail_Stress>\n\
                <Fail_Strain>0</Fail_Strain>\n\
                <Density>" + str(args.densities[mat_num])+  "</Density>\n\
                <Poissons_Ratio>" + str(args.poissonsS[mat_num])+ "</Poissons_Ratio>\n\
                <CTE>0</CTE>\n\
                <uStatic>" + str(args.FrictionStatic)+ "</uStatic>\n\
                <uDynamic>" + str(args.FrictionDynamic)+ "</uDynamic>\n\
                </Mechanical>\n\
                <Magnetic>\n\
                <M_per_vol>" + str(args.M_pervols[mat_num]) + "</M_per_vol>\n\
                </Magnetic>\n\
            </Material>\n")

        voxelyze_file.write(
            "   </Palette>\n")


    voxelyze_file.write(
        "   <Structure Compression=\"ASCII_READABLE\">\n\
        <X_Voxels>" + str(individual.genotype.orig_size_xyz[0]) + "</X_Voxels>\n\
        <Y_Voxels>" + str(individual.genotype.orig_size_xyz[1]) + "</Y_Voxels>\n\
        <Z_Voxels>" + str(individual.genotype.orig_size_xyz[2]) + "</Z_Voxels>\n")

    all_tags = [details["tag"] for name, details in individual.genotype.to_phenotype_mapping.items()]
    if "<Data>" not in all_tags:  # not evolving topology -- fixed presence/absence of voxels
        voxelyze_file.write("<Data>\n")
        for z in range(individual.genotype.orig_size_xyz[2]):
            voxelyze_file.write("<Layer><![CDATA[")
            for y in range(individual.genotype.orig_size_xyz[1]):
                for x in range(individual.genotype.orig_size_xyz[0]):
                    voxelyze_file.write("3")
            voxelyze_file.write("]]></Layer>\n")
        voxelyze_file.write("</Data>\n")

    # append custom parameters
    string_for_md5 = ""
        

    for name, details in individual.genotype.to_phenotype_mapping.items():

        # start tag
        if details["env_kws"] is None:
            voxelyze_file.write(details["tag"]+"\n")

        # record any additional params associated with the output
        if details["params"] is not None:
            for param_tag, param in zip(details["param_tags"], details["params"]):
                voxelyze_file.write(param_tag + str(param) + "</" + param_tag[1:] + "\n")

        if details["env_kws"] is None:
            # write the output state matrix to file
            for z in range(individual.genotype.orig_size_xyz[2]):
                voxelyze_file.write("<Layer><![CDATA[")
                for y in range(individual.genotype.orig_size_xyz[1]):
                    for x in range(individual.genotype.orig_size_xyz[0]):
                        
                        state = individual.designParameters[name][x, y, z]
                        if name == "material":
                            state = int(state)

                        voxelyze_file.write(str(state))
                        if details["tag"] != "<Data>":
                            voxelyze_file.write(", ")
                        string_for_md5 += str(state)

                voxelyze_file.write("]]></Layer>\n")

        # end tag
        if details["env_kws"] is None:
            voxelyze_file.write("</" + details["tag"][1:] + "\n")

    voxelyze_file.write(
        "</Structure>\n\
        </VXC>\n\
        </VXA>")
    voxelyze_file.close()


def write_magnetic_profile(args, individual, run_directory, run_name):
    "write the M profile of Voxels on xml file"
    
    CaseMaxCOMZPos = 0
    # special cases
    if args.desired_shape == "max_COM_z" or args.desired_shape == "max_COM_z_symmetry":
        CaseMaxCOMZPos = 1
        # CaseMaxMinPosZ = 1
    if args.fitness_calc_type == "max_broad_jump":
        CaseMaxMinPosZ = 1
        args.CaseMaxMinPosZ = 1
    
    if args.magnetization_direction == "2D":
        Is3D = 0
    else: 
        Is3D = 1


    Mxml_File = open(args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(individual.id).zfill(args.max_ind_1ex) + "_M.xml", "w")
    Mxml_File.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
                    <VoxelMProfile Version=\"1.0\">\n\
                    <ControllerType>" + str(args.controller_type) + "</ControllerType>\n\
                    <StaticBMag>" + str(args.quasi_static_B_magnitude) + "</StaticBMag>\n\
                    <MperVol>" + str(args.M_pervol) + "</MperVol>\n\
                    <KinEThreshold>" + str(args.KinEThreshold) + "</KinEThreshold>\n\
                    <IsMagForceOn>" + str(args.IsMagForceOn) + "</IsMagForceOn>\n\
                    <SavePosition>" + str(args.save_position) + "</SavePosition>\n\
                    <SaveOrientation>" + str(args.save_orientation) + "</SaveOrientation>\n\
                    <SaveVelocity>" + str(args.save_velocity) + "</SaveVelocity>\n\
                    <SaveAngVel>" + str(args.save_angular_velocity) + "</SaveAngVel>\n\
                    <SaveStrainEnergy>" + str(args.save_strain_energy) + "</SaveStrainEnergy>\n\
                    <SaveKineticEnergy>" + str(args.save_kinetic_energy) + "</SaveKineticEnergy>\n\
                    <SavePressure>" + str(args.save_pressure) + "</SavePressure>\n\
                    <SaveForce>" + str(args.save_force) + "</SaveForce>\n\
                    <CaseMaxCOMZPos>" + str(CaseMaxCOMZPos) + "</CaseMaxCOMZPos>\n\
                    <CaseMaxMinPosZ>" + str(args.CaseMaxMinPosZ) + "</CaseMaxMinPosZ>\n\
                    <Is3D>" + str(Is3D) + "</Is3D>\n\
                    <IsRecordVideo>" + str(args.record_video) + "</IsRecordVideo>\n\
                    <IsCreateHistory>" + str(args.create_history) + "</IsCreateHistory>\n\
                    <HistoryBW>" + str(args.history_bandwidth) + "</HistoryBW>\n\
                    <VideoBW>" + str(args.video_bandwidth) + "</VideoBW>\n")
    
    
    Mxml_File.write("<VoxelMagnetizations>\n")


    if args.desired_shape == "max_COM_z_symmetry":
        individual.genotype.orig_size_xyz = (args.ind_size[0]*2, individual.genotype.orig_size_xyz[1], individual.genotype.orig_size_xyz[2])
        a = individual.mappingGlobal2Voxelyze.copy()
        a_sym = np.flip(a.copy(), axis=0)
        
        vox_num = np.max(a)
        for i in range(a.shape[0]):
            if not a_sym[i] == -1:
                vox_num = vox_num + 1
                a_sym[i] = vox_num

        
        individual.mappingGlobal2Voxelyze = np.concatenate((a,a_sym), axis=0)
        
    for name, details in individual.designParameters.items():
        if name == "Mtheta":
            Mtheta_details = details
        elif name == "Mphi":
            Mphi_details = details
        elif name == "material":
            materials_details = details

    vox_counter = 0
    # write the M profile for each voxel to a xml file
    for z in range(individual.genotype.orig_size_xyz[2]):
        for y in range(individual.genotype.orig_size_xyz[1]):
            for x in range(individual.genotype.orig_size_xyz[0]):

                # get the Mtheta and Mphi values, basically discretized into 1 degree angles
                Mtheta = Mtheta_details[x, y, z]
                Mphi = Mphi_details[x, y, z]
                mat_type = materials_details[x, y, z]
                M = np.array([math.cos(Mtheta) * math.sin(Mphi), math.sin(Mtheta) * math.sin(Mphi), math.cos(Mphi)])

                if not args.encoding_type =="multi_material":  # all the other cases
                    M_pervol = args.M_pervol
                else:    # multi=material case, where there could be several different magnetic &non-magnetic materials
                    M_pervol = 0
                    if mat_type > 0:                    
                        M_pervol = args.M_pervols[int(mat_type)-1]

                if individual.mappingGlobal2Voxelyze[vox_counter] != -1:
                    Mxml_File.write("<VoxelNum" +  str(individual.mappingGlobal2Voxelyze[vox_counter]) +">\n\
                            <VoxelMpervol>" +  str(M_pervol) + "</VoxelMpervol>\n\
                            <VoxelMx>" +  str(M[0]) + "</VoxelMx>\n\
                            <VoxelMy>" +  str(M[1]) + "</VoxelMy>\n\
                            <VoxelMz>" +  str(M[2]) + "</VoxelMz>\n\
                            </VoxelNum" + str(individual.mappingGlobal2Voxelyze[vox_counter]) +">\n")
                vox_counter += 1

    Mxml_File.write("</VoxelMagnetizations>\n")
    Mxml_File.write("</VoxelMProfile>\n")
    Mxml_File.close()

def write_magnetic_field(args, individual, run_directory, run_name, controller_settings):
    "write the external B field on xml file"

    if args.controller_type == "open-loop":
        Mxml_File = open(args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(individual.id).zfill(args.max_ind_1ex) +"_B.xml", "w")
        Mxml_File.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
                    <MagneticField Version=\"1.0\">\n\
                    <ControllerType>" + str(args.controller_type) + "</ControllerType>\n")
        
        Mxml_File.write("<B_period>" + str(controller_settings["B_period"]) + "</B_period>\n\
                        <isPrintEveryStep>" + str(args.isPrintEveryStep) + "</isPrintEveryStep>\n\
                        <B_controller_bandwidth>" + str(controller_settings["B_controller_bandwidth"])  + "</B_controller_bandwidth>\n")
        Mxml_File.write("<BStreamNum>" + str(controller_settings["B_orientation"].size) + "</BStreamNum>\n")
        Mxml_File.write("<BStream>\n")

        for i in range(controller_settings["B_orientation"].size):
            
            direction = controller_settings["B_orientation"][i]
            magnitude = controller_settings["B_magnitude"][i]
            B = magnitude * np.array([math.cos(direction), 0 , math.sin(direction)])

            Mxml_File.write("<BNum" +  str(i) +">\n\
                            <Bx>" +  str(B[0]) + "</Bx>\n\
                            <By>" +  str(B[1]) + "</By>\n\
                            <Bz>" +  str(B[2]) + "</Bz>\n\
                            </BNum" + str(i) +">\n")
        
        Mxml_File.write("</BStream>\n")

    elif args.controller_type == "closed-loop":
        Mxml_File = open(args.run_directory + "/voxelyzeFiles/" + args.run_name + "--id_" + str(individual.id).zfill(args.max_ind_1ex) +"_Bstep_" + str(controller_settings["B_step"])  +".xml", "w")
        Mxml_File.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
                    <MagneticField Version=\"1.0\">\n\
                    <ControllerType>" + str(args.controller_type) + "</ControllerType>\n")

        Mxml_File.write("<B_controller_bandwidth>" + str(controller_settings["B_controller_bandwidth"])  + "</B_controller_bandwidth>\n")

        direction = controller_settings["B_orientation"]
        magnitude = controller_settings["B_magnitude"]
        B = magnitude * np.array([math.cos(direction), 0 , math.sin(direction)])

        Mxml_File.write("<BNum" +  str(0) +">\n\
                        <Bx>" +  str(B[0]) + "</Bx>\n\
                        <By>" +  str(B[1]) + "</By>\n\
                        <Bz>" +  str(B[2]) + "</Bz>\n\
                        </BNum" + str(0) +">\n")
        
    Mxml_File.write("</MagneticField>\n")
    Mxml_File.close()


def read_objective_results(args, ind):
    "read objective_results of individual on xml file"
    ObjValxml_File = open(args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_" + str(ind.id).zfill(args.max_ind_1ex) + "/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_objVal.xml")    
    
    results = {rank: None for rank in range(len(ind.objective_dict))}

    for line in ObjValxml_File:
        for rank, details in ind.objective_dict.items():
            tag = details["tag"]
            if tag is not None:
                if tag in line:
                    results[rank] = float(line[line.find(tag) + len(tag):line.find("</" + tag[1:])])
    ObjValxml_File.close()

    return results

def read_BC_results(args, ind):
    "read BC results of individual on xml file"
    ObjValxml_File = open(args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_" + str(ind.id).zfill(args.max_ind_1ex) + "/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_objVal.xml")    
    
    results = {rank: None for rank in range(len(ind.BC_dict))}

    for line in ObjValxml_File:
        for rank, details in ind.BC_dict.items():
            tag = details["tag"]
            if tag is not None:
                if tag in line:
                    results[rank] = float(line[line.find(tag) + len(tag):line.find("</" + tag[1:])])
    ObjValxml_File.close()

    return results

def write_obj_BC_results(args, ind):
    
    "write_objective_results of individual on xml file"
    ObjValxml_File = open(args.run_directory + "/allIndividualsData/" + args.run_name + "/Ind--id_" + str(ind.id).zfill(args.max_ind_1ex) + "/id_" + str(ind.id).zfill(args.max_ind_1ex) + "_objVal.xml", "w")
    ObjValxml_File.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
                    <ObjVal Version=\"1.0\">\n")
    
    for rank, details in ind.objective_dict.items():
        ObjValxml_File.write(details["tag"] + str(getattr(ind, details["name"])) + "</" + details["tag"][1:] + "\n")
        
    ObjValxml_File.write("</ObjVal>\n")

    ObjValxml_File.write("<BCVal>\n")
    if ind.BC_dict is not None:
        for rank, details in ind.BC_dict.items():
            ObjValxml_File.write(details["tag"] + str(getattr(ind, details["name"])) + "</" + details["tag"][1:] + "\n")
    ObjValxml_File.write("</BCVal>\n")

    ObjValxml_File.close()


def xml2npArray(filename, ind_size, saveAs_xlsx = 0, args=None):

    current_time = 0

    numVox = ind_size[0]*ind_size[1]*ind_size[2]

    robotKineticE = np.full((6), np.nan)

    if args is None:
        voxPos= np.full((numVox, 3), np.nan)
        voxOrientation= np.full((numVox, 4), np.nan)
        voxVel= np.full((numVox, 3), np.nan)
        voxAngVel= np.full((numVox, 3), np.nan)
        voxStrainE= np.full((numVox, 1), np.nan)
        voxKineticE= np.full((numVox, 1), np.nan)
        voxPressure= np.full((numVox, 1), np.nan)
        voxForce= np.full((numVox, 3), np.nan)     
        voxCOMmaxZ = None
        voxCOMvel_maxvelZ = None
        voxCOMmaxY = None
        voxNumTouchingFloor = None
        jumpTime = None
        MaxMinPosZ = None
        WalkerCOMXs = None
    else:
        if args.desired_shape == "max_COM_z_symmetry":
            numVox = args.ind_size[0]*2* args.ind_size[1]* args.ind_size[2]
        voxPos= None
        voxStrainE= None
        voxOrientation= None
        voxVel= None
        voxAngVel= None
        voxForce= None
        voxKineticE= None
        voxPressure= None
        if args.save_position:
            voxPos= np.full((numVox, 3), np.nan)
        if args.save_orientation:
            voxOrientation= np.full((numVox, 4), np.nan)
        if args.save_velocity:
            voxVel= np.full((numVox, 3), np.nan)
        if args.save_angular_velocity:
            voxAngVel= np.full((numVox, 3), np.nan)
        if args.save_strain_energy:
            voxStrainE= np.full((numVox, 1), np.nan)
        if args.save_kinetic_energy:
            voxKineticE= np.full((numVox, 1), np.nan)
        if args.save_pressure:
            voxPressure= np.full((numVox, 1), np.nan)
        if args.save_force:
            voxForce= np.full((numVox, 3), np.nan)
        # special cases
        voxCOMmaxZ = None
        voxCOMvel_maxvelZ = None
        voxCOMmaxY = None
        voxNumTouchingFloor = None
        jumpTime = None
        MaxMinPosZ = None
        Fz_limit = None
        WalkerCOMXs = None
        if args.desired_shape == "max_COM_z" or args.desired_shape == "max_COM_z_symmetry":
            voxCOMmaxZ = np.zeros((1, 3))
            voxCOMvel_maxvelZ = np.zeros((1, 3))
            voxNumTouchingFloor = 99999
            jumpTime = 0
            WalkerCOMXs = None
            if args.CaseMaxMinPosZ:
                MaxMinPosZ = np.zeros((1, 3))
        
    
    retry_counter = 0   # try to read again in case something went wrong at the cluster
    retry_max = 3       # max number of trials before giving up on the run

    if not os.path.isfile(filename):
        print("Result file does not exist, waiting for a sec")
        time.sleep(1)

    while retry_counter < retry_max:
        retry_counter +=1
        try:
            this_file = open(filename)

            tag = "<Voxel "
            tagnum = tag + "num: >"
            tagX = tag + "x: >"
            tagY = tag + "y: >"
            tagZ = tag + "z: >"
            tagStrainE = tag + "StrainEnergy: >"

            tagOrientAngle = tag + "Angle: >"
            tagOrientX = tag + "Orientx: >"
            tagOrientY = tag + "Orienty: >"
            tagOrientZ = tag + "Orientz: >"
            tagVelX = tag + "Velx: >"
            tagVelY = tag + "Vely: >"
            tagVelZ = tag + "Velz: >"
            tagAngVelX = tag + "AngVelx: >"
            tagAngVelY = tag + "AngVely: >"
            tagAngVelZ = tag + "AngVelz: >"
            tagKineticE = tag + "KineticEnergy: >"
            tagPressure = tag + "Pressure: >"
            tagForceX = tag + "Forcex: >"
            tagForceY = tag + "Forcey: >"
            tagForceZ = tag + "Forcez: >"

            tagCOMx = "<COMx: >"
            tagCOMy = "<COMy: >"
            tagCOMz = "<COMz: >"

            tagCOMvelx = "<COMvelx: >"
            tagCOMvely = "<COMvely: >"
            tagCOMvelz = "<COMvelz: >"

            tagVoxNumTouchingFloor = "<voxNumTouchingFloor: >"


            tagMaxMinPosZx = "<MaxMinPosZx: >"
            tagMaxMinPosZy = "<MaxMinPosZy: >"
            tagMaxMinPosZz = "<MaxMinPosZz: >"

            tagTime = "<CurTime(s)>"

            tagKinE = "<KinEavg_t"
            tagKinEt = "<KinEavg_t" + ": >"
            tagKinEt_1 = "<KinEavg_t" + "-1: >"
            tagKinEt_2 = "<KinEavg_t" + "-2: >"
            tagKinEt_3 = "<KinEavg_t" + "-3: >"
            tagKinEt_4 = "<KinEavg_t" + "-4: >"
            tagKinEt_5 = "<KinEavg_t" + "-5: >"

            tagJumpTime = "<sampleAirTotTime: >"


            tagF_limitz = "<Fz_limit: >"

            tagWalkerCOMXs = "<WalkerCOMXsArray: >"


            voxNum = None
            voxelCounter = 0
            for line in this_file:
                if tagTime in line:
                    current_time = float(line[line.find(tagTime) + len(tagTime) : line.find("</" + tagTime[1:])])
                elif tagnum in line:
                    voxelCounter +=1
                    voxNum = int(line[line.find(tagnum) + len(tagnum):line.find("</" + tagnum[1:])])
                elif tagX in line:
                    voxPos[voxNum, 0] = float(line[line.find(tagX) + len(tagX) : line.find("</" + tagX[1:])])
                elif tagY in line:
                    voxPos[voxNum, 1] = float(line[line.find(tagY) + len(tagY) : line.find("</" + tagY[1:])])
                elif tagZ in line:
                    voxPos[voxNum, 2] = float(line[line.find(tagZ) + len(tagZ) : line.find("</" + tagZ[1:])])
                elif tagStrainE in line:
                    voxStrainE[voxNum, 0] = float(line[line.find(tagStrainE) + len(tagStrainE) : line.find("</" + tagStrainE[1:])])
                elif tagOrientAngle in line:
                    voxOrientation[voxNum, 0] = float(line[line.find(tagOrientAngle) + len(tagOrientAngle) : line.find("</" + tagOrientAngle[1:])])
                elif tagOrientX in line:
                    voxOrientation[voxNum, 1] = float(line[line.find(tagOrientX) + len(tagOrientX) : line.find("</" + tagOrientX[1:])])
                elif tagOrientY in line:
                    voxOrientation[voxNum, 2] = float(line[line.find(tagOrientY) + len(tagOrientY) : line.find("</" + tagOrientY[1:])])
                elif tagOrientZ in line:
                    voxOrientation[voxNum, 3] = float(line[line.find(tagOrientZ) + len(tagOrientZ) : line.find("</" + tagOrientZ[1:])])
                elif tagVelX in line:
                    voxVel[voxNum, 0] = float(line[line.find(tagVelX) + len(tagVelX) : line.find("</" + tagVelX[1:])])
                elif tagVelY in line:
                    voxVel[voxNum, 1] = float(line[line.find(tagVelY) + len(tagVelY) : line.find("</" + tagVelY[1:])])
                elif tagVelZ in line:
                    voxVel[voxNum, 2] = float(line[line.find(tagVelZ) + len(tagVelZ) : line.find("</" + tagVelZ[1:])])
                elif tagAngVelX in line:
                    voxAngVel[voxNum, 0] = float(line[line.find(tagAngVelX) + len(tagAngVelX) : line.find("</" + tagAngVelX[1:])])
                elif tagAngVelY in line:
                    voxAngVel[voxNum, 1] = float(line[line.find(tagAngVelY) + len(tagAngVelY) : line.find("</" + tagAngVelY[1:])])
                elif tagAngVelZ in line:
                    voxAngVel[voxNum, 2] = float(line[line.find(tagAngVelZ) + len(tagAngVelZ) : line.find("</" + tagAngVelZ[1:])])
                elif tagKineticE in line:
                    voxKineticE[voxNum, 0] = float(line[line.find(tagKineticE) + len(tagKineticE) : line.find("</" + tagKineticE[1:])])
                elif tagPressure in line:
                    voxPressure[voxNum, 0] = float(line[line.find(tagPressure) + len(tagPressure) : line.find("</" + tagPressure[1:])])        
                elif tagForceX in line:
                    voxForce[voxNum, 0] = float(line[line.find(tagForceX) + len(tagForceX) : line.find("</" + tagForceX[1:])])
                elif tagForceY in line:
                    voxForce[voxNum, 1] = float(line[line.find(tagForceY) + len(tagForceY) : line.find("</" + tagForceY[1:])])
                elif tagForceZ in line:
                    voxForce[voxNum, 2] = float(line[line.find(tagForceZ) + len(tagForceZ) : line.find("</" + tagForceZ[1:])])
                elif tagJumpTime in line:
                    jumpTime = float(line[line.find(tagJumpTime) + len(tagJumpTime) : line.find("</" + tagJumpTime[1:])]) 
            this_file.close()
            
            this_file = open(filename)
            if args is not None and (args.desired_shape == "max_COM_z" or args.desired_shape == "max_COM_z_symmetry" or args.desired_shape == "max_COM_x" ):
                for line in this_file:
                    if tagCOMx in line:
                        voxCOMmaxZ[0, 0] = float(line[line.find(tagCOMx) + len(tagCOMx) : line.find("</" + tagCOMx[1:])])
                    elif tagCOMy in line:
                        voxCOMmaxZ[0, 1] = float(line[line.find(tagCOMy) + len(tagCOMy) : line.find("</" + tagCOMy[1:])])
                    elif tagCOMz in line:
                        voxCOMmaxZ[0, 2] = float(line[line.find(tagCOMz) + len(tagCOMz) : line.find("</" + tagCOMz[1:])])
                    elif tagCOMvelx in line:
                        voxCOMvel_maxvelZ[0, 0] = float(line[line.find(tagCOMvelx) + len(tagCOMvelx) : line.find("</" + tagCOMvelx[1:])])
                    elif tagCOMvely in line:
                        voxCOMvel_maxvelZ[0, 1] = float(line[line.find(tagCOMvely) + len(tagCOMvely) : line.find("</" + tagCOMvely[1:])])
                    elif tagCOMvelz in line:
                        voxCOMvel_maxvelZ[0, 2] = float(line[line.find(tagCOMvelz) + len(tagCOMvelz) : line.find("</" + tagCOMvelz[1:])])
                    elif tagVoxNumTouchingFloor in line:
                        voxNumTouchingFloor = float(line[line.find(tagVoxNumTouchingFloor) + len(tagVoxNumTouchingFloor) : line.find("</" + tagVoxNumTouchingFloor[1:])])
                    elif tagJumpTime in line:
                        jumpTime = float(line[line.find(tagJumpTime) + len(tagJumpTime) : line.find("</" + tagJumpTime[1:])]) 
                    elif tagWalkerCOMXs in line:
                        WalkerCOMXs_str = line[line.find(tagWalkerCOMXs) + len(tagWalkerCOMXs) : line.find("</" + tagWalkerCOMXs[1:])]
                        WalkerCOMXs_str_seperated = WalkerCOMXs_str.split(',')
                        WalkerCOMXs_str_seperated = [part for part in WalkerCOMXs_str.split(',') if part]
                        WalkerCOMXs = [float(part.split(":")[-1]) for part in WalkerCOMXs_str_seperated]
                    elif tagMaxMinPosZx in line:
                        MaxMinPosZ[0, 0] = float(line[line.find(tagMaxMinPosZx) + len(tagMaxMinPosZx) : line.find("</" + tagMaxMinPosZx[1:])])
                    elif tagMaxMinPosZy in line:
                        MaxMinPosZ[0, 1] = float(line[line.find(tagMaxMinPosZy) + len(tagMaxMinPosZy) : line.find("</" + tagMaxMinPosZy[1:])])
                    elif tagMaxMinPosZz in line:
                        MaxMinPosZ[0, 2] = float(line[line.find(tagMaxMinPosZz) + len(tagMaxMinPosZz) : line.find("</" + tagMaxMinPosZz[1:])])
                        break
                    
            this_file.close()


            vox_dict=dict(time=current_time,
                        position=voxPos,
                        strainEnergy=voxStrainE,
                        orientation=voxOrientation,
                        velocity=voxVel,
                        angularVelocity=voxAngVel,
                        kineticEnergy=voxKineticE,
                        pressure=voxPressure,
                        force=voxForce,
                        COMmaxZ=voxCOMmaxZ,
                        COMvelMaxVelZ=voxCOMvel_maxvelZ,
                        voxTouchingFloor = voxNumTouchingFloor,
                        jumpTotTime = jumpTime,
                        COMmaxY=voxCOMmaxY,
                        MaxMinPosZ = MaxMinPosZ,
                        Fz_limit = Fz_limit,
                        WalkerCOMXs = WalkerCOMXs
                        )

            return vox_dict

        except: 
            print("could not read the result file, trying again")
            time.sleep(0.3)
            
    print("Could not read the result file, throwing an error for file", filename)
    
    raise ValueError("Could not read the result file, throwing an error")

"NN handlers"
def write_NN_raw_data(args, pop, txt_file=None):
    "record the raw data for later usage to a txt file"

    if txt_file is None:
        txt_file=args.run_directory+"/NNData/"+"NN_raw_dataset_structure_"+\
                    str(args.ind_size[0])+"_" + str(args.ind_size[1])+"_" +str(args.ind_size[2])+".txt"
        
    if not os.path.isfile(txt_file):
        fileTXT = open(txt_file, "w")
        # write the first line with the info column
        # write it into .txt file
        fileTXT.write("id"+";")
        fileTXT.write("voxel map;")
        fileTXT.write("Mtheta;")
        fileTXT.write("Mphi;")
        fileTXT.write("fitness;")
        fileTXT.write("Bext(mT);")
        fileTXT.write("MperVol(A/m);")
        fileTXT.write("time(sec);")
        fileTXT.write("posX(mm);")
        fileTXT.write("posY(mm);")
        fileTXT.write("posZ(mm);\n")
    elif os.path.isfile(txt_file):
        fileTXT = open(txt_file, "a")
    else:
        raise NotImplementedError
        

    for ind in pop:
        
        # get the design data
        id = ind.id
        voxel_map = ind.designParameters["material"]
        Mtheta = ind.segmentedMprofile["Mtheta"]
        Mphi = ind.segmentedMprofile["Mphi"]
        fitness = ind.fitness

        voxel_map1D = voxel_map.flatten()
        Mtheta1D = Mtheta.flatten()
        Mphi1D= Mphi.flatten()

        # get the details
        bext=args.quasi_static_B_magnitude
        MperVol=args.M_pervol

        vox_dict = ind.load_ind(ind.id, args).voxel_dict
        pos=vox_dict["position"]
        t=vox_dict["time"]

        posX=pos[:,0].flatten()*1e3
        posY=pos[:,1].flatten()*1e3
        posZ=pos[:,1].flatten()*1e3

        # write it into .txt file
        fileTXT.write(str(id)+";")
        np.savetxt(fileTXT, [voxel_map1D], delimiter=',', fmt='%-2.0f', newline="")
        fileTXT.write(";")
        np.savetxt(fileTXT, [Mtheta1D], delimiter=',', fmt='%-2.5f',newline="")
        fileTXT.write(";")
        np.savetxt(fileTXT, [Mphi1D], delimiter=',', fmt='%-2.5f',newline="")
        fileTXT.write(";")
        fileTXT.write(str(fitness)+";")
        fileTXT.write(str(bext)+";")
        fileTXT.write(str(MperVol)+";")
        fileTXT.write(str(t)+";")
        np.savetxt(fileTXT, [posX], delimiter=',', fmt='%-2.3f',newline="")
        fileTXT.write(";")
        np.savetxt(fileTXT, [posY], delimiter=',', fmt='%-2.3f',newline="")
        fileTXT.write(";")
        np.savetxt(fileTXT, [posZ], delimiter=',', fmt='%-2.3f',newline="")
        fileTXT.write(";\n")

    fileTXT.close()
