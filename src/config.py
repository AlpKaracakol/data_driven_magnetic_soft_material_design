# Inspired from 2020 Uber Technologies, Inc.

"""
BC_default_config sets up the BC space. Then,
Depending on the arguments of the optimization, sets the order and logging settings.
"""
import math

def setup_BC_config(args):

    # args_dict = vars(args)
    
    BC_default_config = dict(volume=dict(name="volume", # volume ratio to the defined maximum volume
                                         tag="<volume>",
                                         min=args.min_volume_ratio,
                                         max=1,
                                         nb_cells=int(args.number_cells_per_BC),
                                         worst_value=-999,
                                         logging_only=True),
                             Mtheta=dict(name="MthetaAvg",            # average Mtheta
                                         tag="<MthetaAvg>",
                                         min=-math.pi,
                                         max=math.pi,
                                         nb_cells=int(args.number_cells_per_BC),
                                         worst_value=-999,
                                         logging_only=True),
                             Mphi=dict(name="MphiAvg",                # average Mphi
                                         tag="<MphiAvg>",
                                         min=0,
                                         max=math.pi,
                                         nb_cells=int(args.number_cells_per_BC/2),
                                         worst_value=-999,
                                         logging_only=True),
                             COM=dict(name="COM",                     # COM distance from the origin
                                         tag="<COM>",
                                         min=0,
                                         max=100,
                                         nb_cells=50,
                                         worst_value=-999,
                                         logging_only=True),
                             CPPN=dict(name="CPPN",                   # CPPN complexity--total number of edges and nodes
                                         tag="<CPPN>",
                                         min=0,
                                         max=160,
                                         nb_cells=20,
                                         worst_value=-999,
                                         logging_only=True),
                             CPPN_node=dict(name="CPPN_node_num",      # CPPN total number of nodes
                                         tag="<CPPNnode>",
                                         min=0,
                                         max=40,
                                         nb_cells=20,
                                         worst_value=-999,
                                         logging_only=True),
                             CPPN_edge=dict(name="CPPN_edge_num",      # CPPN total number of edges
                                         tag="<CPPNedge>",
                                         min=0,
                                         max=120,
                                         nb_cells=20,
                                         worst_value=-999,
                                         logging_only=True),
                             StrainEnergy=dict(name="StrainEnergyAvg", # Avg strain energy of the voxels
                                         tag="<StrainEnergy>",
                                         min=0,
                                         max=1e-3,
                                         nb_cells=50,
                                         worst_value=-999,
                                         logging_only=True))

    # hard-coded BC_type configurations
    if args.BC_type == "vol_mag_3D":
        BC_rank=["volume", "Mtheta", "Mphi", "COM", "CPPN", "CPPN_node", "CPPN_edge", "StrainEnergy"]
        BC_logging_only = [False, False, False, True, True, True, True, True ]
    elif args.BC_type == "node_edge":
        BC_rank=["CPPN_node", "CPPN_edge", "volume", "Mtheta", "Mphi", "COM", "CPPN", "StrainEnergy"]
        BC_logging_only = [False, False, True, True, True, True, True, True]
    elif args.BC_type == "vol_cppn":
        BC_rank=["volume", "CPPN", "Mtheta", "Mphi", "COM", "CPPN_node", "CPPN_edge", "StrainEnergy"]
        BC_logging_only = [False, False, True, True, True, True, True, True ]
    elif args.BC_type == "vol_mag_2D":
        BC_rank=["volume", "Mtheta", "Mphi", "COM", "CPPN", "CPPN_node", "CPPN_edge", "StrainEnergy"]
        BC_logging_only = [False, False, True, True, True, True, True, True ]
    else:
        raise NotImplementedError
        
    
    # set BC_config right order and update the logging option
    BC_config = dict()
    BC_index = 0
    for rank in BC_rank:
        BC_config[rank]=BC_default_config[rank]
        BC_config[rank]["logging_only"]=BC_logging_only[BC_index]
        BC_index+=1

    return BC_config
