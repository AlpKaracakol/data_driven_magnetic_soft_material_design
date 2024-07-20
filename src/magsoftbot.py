import operator
import numpy as np
from copy import deepcopy
import math
import logging
import pickle
import os
import time
import tarfile
import subprocess as sub
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from functools import partial

from src.networks import Network
from tools.utils import sigmoid, xml_format, dominates, getDesiredShape
from src.networks import CPPN, DirectEncoding
from tools.utils import discretize_material, make_material_tree, rescaled_positive_sigmoid, make_Mtheta_tree, identity, step

logger = logging.getLogger(__name__)

class Genotype(object):
    """A container for multiple networks, 'genetic code' copied with modification to produce offspring."""

    def __init__(self, orig_size_xyz=(6, 6, 6), segment_size_xyz= (10,8,1)):

        """
        Parameters
        ----------
        orig_size_xyz : 3-tuple (x, y, z)
            Defines the original 3 dimensions for the cube of voxels corresponding to possible networks outputs. The
            maximum number of SofBot voxel components is x*y*z, a full cube.

        """
        self.networks = []
        self.all_networks_outputs = []
        self.to_phenotype_mapping = GenotypeToPhenotypeMap()
        self.orig_size_xyz = orig_size_xyz
        self.segment_size_xyz = segment_size_xyz

    def __iter__(self):
        """Iterate over the networks. Use the expression 'for n in network'."""
        return iter(self.networks)

    def __len__(self):
        """Return the number of networks in the genotype. Use the expression 'len(network)'."""
        return len(self.networks)

    def __getitem__(self, n):
        """Return network n.  Use the expression 'network[n]'."""
        return self.networks[n]

    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def add_network(self, network, freeze=False, num_consecutive_mutations=1):
        """Append a new network to this list of networks.

        Parameters
        ----------
        freeze : bool
            This indicator is used to prevent mutations to a network while freeze == True

        num_consecutive_mutations : int
            Uses this many (random) steps per mutation.

        """
        assert isinstance(network, Network)
        network.freeze = freeze
        network.num_consecutive_mutations = num_consecutive_mutations
        self.networks += [network]
        self.all_networks_outputs.extend(network.output_node_names)

    def express(self):
        """Calculate the genome networks outputs, the physical properties of each voxel for simulation"""

        for network in self:
            if not network.direct_encoding:
                for name in network.graph.nodes():
                    network.graph.nodes[name]["evaluated"] = False  # flag all nodes as unevaluated

                network.set_input_node_states(self.orig_size_xyz, self.segment_size_xyz)  # reset the inputs

                for name in network.output_node_names:
                    network.graph.nodes[name]["state"] = np.zeros(self.orig_size_xyz)  # clear old outputs
                    network.graph.nodes[name]["state"] = self.calc_node_state(network, name)  # calculate new outputs

        for network in self:
            for name in network.output_node_names:
                if name in self.to_phenotype_mapping:
                    if not network.direct_encoding:
                        self.to_phenotype_mapping[name]["state"] = network.graph.nodes[name]["state"]
                    else:
                        self.to_phenotype_mapping[name]["state"] = network.values

        for name, details in self.to_phenotype_mapping.items():
            if name not in self.all_networks_outputs:
                details["state"] = np.ones(self.orig_size_xyz, dtype=details["output_type"]) * -999
                if details["dependency_order"] is not None:
                    for dependency_name in details["dependency_order"]:
                        self.to_phenotype_mapping.dependencies[dependency_name]["state"] = None

        for name, details in self.to_phenotype_mapping.items():
            if details["dependency_order"] is not None:
                details["state"] = details["func"](self)

    def calc_node_state(self, network, node_name):
        """Propagate input values through the network"""
        if network.graph.nodes[node_name]["evaluated"]:
            return network.graph.nodes[node_name]["state"]

        network.graph.nodes[node_name]["evaluated"] = True
        input_edges = network.graph.in_edges(nbunch=[node_name])
        new_state = np.zeros(self.orig_size_xyz)

        for edge in input_edges:
            node1, node2 = edge
            new_state += self.calc_node_state(network, node1) * network.graph.edges[node1, node2]["weight"]

        network.graph.nodes[node_name]["state"] = new_state

        if node_name in self.to_phenotype_mapping:
            if self.to_phenotype_mapping[node_name]["dependency_order"] is None:
                return self.to_phenotype_mapping[node_name]["func"](new_state)

        return network.graph.nodes[node_name]["function"](new_state)


class GenotypeToPhenotypeMap(object):
    """A mapping of the relationship from genotype (networks) to phenotype (VoxCad simulation)."""

    def __init__(self):
        self.mapping = dict()
        self.dependencies = dict()

    def items(self):
        """to_phenotype_mapping.items() -> list of (key, value) pairs in mapping"""
        return [(key, self.mapping[key]) for key in self.mapping]

    def __contains__(self, key):
        """Return True if key is a key str in the mapping, False otherwise. Use the expression 'key in mapping'."""
        try:
            return key in self.mapping
        except TypeError:
            return False

    def __len__(self):
        """Return the number of mappings. Use the expression 'len(mapping)'."""
        return len(self.mapping)

    def __getitem__(self, key):
        """Return mapping for node with name 'key'.  Use the expression 'mapping[key]'."""
        return self.mapping[key]

    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def add_map(self, name, tag, func=sigmoid, output_type=float, dependency_order=None, params=None, param_tags=None,
                env_kws=None, logging_stats=np.mean):
        """Add an association between a genotype output and a VoxCad parameter.

        Parameters
        ----------
        name : str
            A network output node name from the genotype.

        tag : str
            The tag used in parsing the resulting output from a VoxCad simulation.
            If this is None then the attribute is calculated outside of VoxCad (in Python only).

        func : func
            Specifies relationship between attributes and xml tag.

        output_type : type
            The output type

        dependency_order : list
            Order of operations

        params : list
            Constants dictating parameters of the mapping

        param_tags : list
            Tags for any constants associated with the mapping

        env_kws : dict
            Specifies which function of the output state to use (on top of func) to set an Env attribute

        logging_stats : func or list
            One or more functions (statistics) of the output to be logged as additional column(s) in logging

        """
        if (dependency_order is not None) and not isinstance(dependency_order, list):
            dependency_order = [dependency_order]

        if params is not None:
            assert (param_tags is not None)
            if not isinstance(params, list):
                params = [params]

        if param_tags is not None:
            assert (params is not None)
            if not isinstance(param_tags, list):
                param_tags = [param_tags]
            param_tags = [xml_format(t) for t in param_tags]

        if (env_kws is not None) and not isinstance(env_kws, dict):
            env_kws = {env_kws: np.mean}

        if (logging_stats is not None) and not isinstance(logging_stats, list):
            logging_stats = [logging_stats]

        if tag is not None:
            tag = xml_format(tag)

        self.mapping[name] = {"tag": tag,
                              "func": func,
                              "dependency_order": dependency_order,
                              "state": None,
                              "old_state": None,
                              "output_type": output_type,
                              "params": params,
                              "param_tags": param_tags,
                              "env_kws": env_kws,
                              "logging_stats": logging_stats}

    def add_output_dependency(self, name, dependency_name, requirement, material_if_true=None, material_if_false=None):
        """Add a dependency between two genotype outputs.

        Parameters
        ----------
        name : str
            A network output node name from the genotype.

        dependency_name : str
            Another network output node name.

        requirement : bool
            Dependency must be this

        material_if_true : int
            The material if dependency meets pre-requisite

        material_if_false : int
            The material otherwise

        """
        self.dependencies[name] = {"depends_on": dependency_name,
                                   "requirement": requirement,
                                   "material_if_true": material_if_true,
                                   "material_if_false": material_if_false,
                                   "state": None}

    def get_dependency(self, name, output_bool):
        """Checks recursively if all boolean requirements were met in dependent outputs."""
        if self.dependencies[name]["depends_on"] is not None:
            dependency = self.dependencies[name]["depends_on"]
            requirement = self.dependencies[name]["requirement"]
            return np.logical_and(self.get_dependency(dependency, True) == requirement,
                                  self.dependencies[name]["state"] == output_bool)
        else:
            return self.dependencies[name]["state"] == output_bool


class Phenotype(object):
    """Physical manifestation of the genotype - determines the physiology of an individual."""

    def __init__(self, genotype):

        """
        Parameters
        ----------
        genotype : Genotype()
            Defines particular networks (the genome).

        """
        self.genotype = genotype
        self.genotype.express()

    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def is_valid(self):
        """Ensures a randomly generated phenotype is valid (checked before adding individual to a population).

        Returns
        -------
        is_valid : bool
        True if self is valid, False otherwise.

        """
        for network in self.genotype:
            for output_node_name in network.output_node_names:
                if not network.direct_encoding and np.isnan(network.graph.nodes[output_node_name]["state"]).any():
                    return False
                elif network.direct_encoding and np.isnan(network.values).any():
                    return False

        return True


""" Voxelyze handlers"""
# Defining a custom genotype, inheriting from base class Genotype
class MyGenotype(Genotype):
    def __init__(self, orig_size_xyz=(60, 8, 1), segment_size_xyz=(10,8,1), args=None):
        # We instantiate a new genotype for each individual which must have the following properties
        Genotype.__init__(self, orig_size_xyz=orig_size_xyz, segment_size_xyz=segment_size_xyz)
        # The genotype consists of a single Compositional Pattern Producing Network (CPPN),
        # with multiple inter-dependent outputs determining the material and Magnetizaiton profile constituting each voxel

        if args.encoding_type=="same_CPPN": # utilization of same CPPN (monolithic) for both the structural design and magnetic profile -- for testing purposes
            # Add a CPPN, with three outputs.
            # "isVoxel" the geometry of the robot
            # (i.e. whether a particular voxel is empty or full),
            # if full, Mtheta and Mphi determines the magnetizaiton direction
            self.add_network(CPPN(args, output_node_names=["isVoxel", "whichDirection", "Mphi"], input_node_names=['x', 'y', 'z', 'd', 'b']))

            # The mapping for materials depends on "isVoxel"
            # Basically, if "isVoxel" is false (cppn output < 0), the material with id "0" is assigned (-> empty voxel).
            # If, instead, "isVoxel" is true (cppn output > 0), the material with id "1" is assigned (-> full voxel).
            # The magnetizaiton profile is decided from the Mtheta and Mphi values
            self.to_phenotype_mapping.add_map(name="material", tag="<Data>", func=make_material_tree,
                                            dependency_order=["isVoxel"], output_type=int)

            self.to_phenotype_mapping.add_output_dependency(name="isVoxel", dependency_name=None, requirement=None,
                                                            material_if_true="1", material_if_false="0")

            # Once remapped from [-1,1] to [min_Mtheta, max_Mtheta] through "func",
            # "Mtheta" and "Mphi" output goes directly to the vxa tag --<Mtheta>&<Mphi> as a continuous property.
            if args is None or args.magnetization_direction =="3D":  # 3D magnetization directions for the magnetic profile
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>",
                                                func=partial(rescaled_positive_sigmoid, x_min=-math.pi, x_max=math.pi))
            elif args.magnetization_direction =="2D": # 2D magnetization directions for the magnetic profile
                # create a discrete Mtheta either 0 or 180 degrees
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>", func=make_Mtheta_tree,
                                            dependency_order=["whichDirection"], output_type=float)

                self.to_phenotype_mapping.add_output_dependency(name="whichDirection", dependency_name=None, requirement=None,
                                                            material_if_true="0", material_if_false=str(math.pi))
            else:
                raise NotImplementedError

            self.to_phenotype_mapping.add_map(name="Mphi", tag="<Mphi>",
                                            func=partial(rescaled_positive_sigmoid, x_min=0, x_max=math.pi))
        elif args.encoding_type=="seperate_CPPN": # utilization of distinct two CPPNs (monolithic) for both the structural design and magnetic profile -- for testing purposes
            # Create seperate CPPNs for morpholgoy and magnetization profile
            # "isVoxel" the geometry of the robot
            # (i.e. whether a particular voxel is empty or full),
            # if full, Mtheta and Mphi determines the magnetizaiton direction
            self.add_network(CPPN(args, output_node_names=["isVoxel"], input_node_names=['x', 'y', 'z', 'd', 'b']))

            # The mapping for materials depends on "isVoxel"
            # Basically, if "isVoxel" is false (cppn output < 0), the material with id "0" is assigned (-> empty voxel).
            # If, instead, "isVoxel" is true (cppn output > 0), the material with id "1" is assigned (-> full voxel).
            # The magnetizaiton profile is decided from the Mtheta and Mphi values
            self.to_phenotype_mapping.add_map(name="material", tag="<Data>", func=make_material_tree,
                                            dependency_order=["isVoxel"], output_type=int)

            self.to_phenotype_mapping.add_output_dependency(name="isVoxel", dependency_name=None, requirement=None,
                                                            material_if_true="1", material_if_false="0")


            self.add_network(CPPN(args, output_node_names=["whichDirection", "Mphi"], input_node_names=['x', 'y', 'z', 'd', 'b']))
            # Once remapped from [-1,1] to [min_Mtheta, max_Mtheta] through "func",
            # "Mtheta" and "Mphi" output goes directly to the vxa tag --<Mtheta>&<Mphi> as a continuous property.
            if args is None or args.magnetization_direction =="3D":  # 3D magnetization directions for the magnetic profile
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>",
                                                func=partial(rescaled_positive_sigmoid, x_min=-math.pi, x_max=math.pi))
            elif args.magnetization_direction =="2D": # 2D magnetization directions for the magnetic profile
                # create a discrete Mtheta either 0 or 180 degrees
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>", func=make_Mtheta_tree,
                                            dependency_order=["whichDirection"], output_type=float)

                self.to_phenotype_mapping.add_output_dependency(name="whichDirection", dependency_name=None, requirement=None,
                                                            material_if_true="0", material_if_false=str(math.pi))
            else:
                raise NotImplementedError

            self.to_phenotype_mapping.add_map(name="Mphi", tag="<Mphi>",
                                            func=partial(rescaled_positive_sigmoid, x_min=0, x_max=math.pi))
        elif args.encoding_type=="morph_CPPN_mag_direct": # CPPN for structural design and direct encoding for magnetic profile
            # Create a CPPN for structural design
            # "isVoxel" the geometry of the robot
            # (i.e. whether a particular voxel is empty or full),
            # if full, Mtheta and Mphi determines the magnetization direction
            self.add_network(CPPN(args, output_node_names=["isVoxel"], input_node_names=['x', 'y', 'z', 'd', 'b']))

            # The mapping for materials depends on "isVoxel"
            # Basically, if "isVoxel" is false (cppn output < 0), the material with id "0" is assigned (-> empty voxel).
            # If, instead, "isVoxel" is true (cppn output > 0), the material with id "1" is assigned (-> full voxel).
            # The magnetizaiton profile is decided from the Mtheta and Mphi values
            self.to_phenotype_mapping.add_map(name="material", tag="<Data>", func=make_material_tree,
                                            dependency_order=["isVoxel"], output_type=int)

            self.to_phenotype_mapping.add_output_dependency(name="isVoxel", dependency_name=None, requirement=None,
                                                            material_if_true="1", material_if_false="0")


            segmented_size_xyz = (int(orig_size_xyz[0]/segment_size_xyz[0]),
                                    int(orig_size_xyz[1]/segment_size_xyz[1]),
                                    int(orig_size_xyz[2]/segment_size_xyz[2]))

            # add direct encoding for the magnetization profile
            self.add_network(DirectEncoding(output_node_name="Mtheta", orig_size_xyz=segmented_size_xyz, lower_bound=-math.pi, upper_bound=math.pi, func=None, symmetric=False,
                 p=None, scale=1, start_val=None, mutate_start_val=False))
            # Once remapped from [-1,1] to [min_Mtheta, max_Mtheta] through "func",
            # "Mtheta" and "Mphi" output goes directly to the vxa tag --<Mtheta>&<Mphi> as a continuous property.
            if args is None or args.magnetization_direction =="3D":  # 3D magnetization directions for the magnetic profile
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>",
                                                func=partial(identity, x_min=-math.pi, x_max=math.pi))
            elif args.magnetization_direction =="2D": # 2D magnetization directions for the magnetic profile
                # create a discrete Mtheta either 0 or 180 degrees

                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>",
                                                func=partial(step, x_min=0, x_max=math.pi))
            else:
                raise NotImplementedError

            self.add_network(DirectEncoding(output_node_name="Mphi", orig_size_xyz=segmented_size_xyz, lower_bound=0, upper_bound=math.pi, func=None, symmetric=False,
                 p=None, scale=0.5, start_val=None, mutate_start_val=False))

            self.to_phenotype_mapping.add_map(name="Mphi", tag="<Mphi>",
                                                func=partial(identity, x_min=0, x_max=math.pi))
        elif args.encoding_type=="multi_material":
            # Create a CPPN for structural design
            # "isVoxel" the geometry of the robot
            # (i.e. whether a particular voxel is empty or full),
            # if full, Mtheta and Mphi determines the magnetization direction
            self.add_network(CPPN(args, output_node_names=["material"], input_node_names=['x', 'y', 'z', 'd', 'b']))

            # The mapping for materials depends on "isVoxel"
            # The magnetizaiton profile is decided from the Mtheta and Mphi values
            if not args.desired_shape == "max_vol_3D" and not args.desired_shape == "SMP_gripper":
                self.to_phenotype_mapping.add_map(name="material", tag="<Data>",
                                                    func=partial(discretize_material, num_materials=args.material_num))
            else:
                self.to_phenotype_mapping.add_map(name="material", tag="<Data>",
                                                    func=partial(discretize_material, num_materials=args.material_num, desired_behaviour = args.desired_shape))


            segmented_size_xyz = (int(orig_size_xyz[0]/segment_size_xyz[0]),
                                    int(orig_size_xyz[1]/segment_size_xyz[1]),
                                    int(orig_size_xyz[2]/segment_size_xyz[2]))

            # add direct encoding for the magnetization profile
            self.add_network(DirectEncoding(output_node_name="Mtheta", orig_size_xyz=segmented_size_xyz, lower_bound=-math.pi, upper_bound=math.pi, func=None, symmetric=False,
                 p=None, scale=1, start_val=None, mutate_start_val=False))
            # Once remapped from [-1,1] to [min_Mtheta, max_Mtheta] through "func",
            # "Mtheta" and "Mphi" output goes directly to the vxa tag --<Mtheta>&<Mphi> as a continuous property.
            if args is None or args.magnetization_direction =="3D":  # 3D magnetization directions for the magnetic profile
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>",
                                                func=partial(identity, x_min=-math.pi, x_max=math.pi))
            elif args.magnetization_direction =="2D": # 2D magnetization directions for the magnetic profile
                # create a discrete Mtheta either 0 or 180 degrees
                self.to_phenotype_mapping.add_map(name="Mtheta", tag="<Mtheta>",
                                                func=partial(step, x_min=0, x_max=math.pi))
            else:
                raise NotImplementedError

            self.add_network(DirectEncoding(output_node_name="Mphi", orig_size_xyz=segmented_size_xyz, lower_bound=0, upper_bound=math.pi, func=None, symmetric=False,
                 p=None, scale=0.5, start_val=None, mutate_start_val=False))

            self.to_phenotype_mapping.add_map(name="Mphi", tag="<Mphi>",
                                                func=partial(identity, x_min=0, x_max=math.pi))
        else:
            if args.debug: print("encoding_type %d is not defined", args.encoding_type)
            raise NotImplementedError

# Define a custom phenotype, inheriting from the Phenotype class
class MyPhenotype(Phenotype):
    def is_valid(self, min_percent_full=0.5, min_percent_muscle=0.1, desired_behavior = None, mat_num = 1, max_percent_full = 0.9):
        # override super class function to redefine what constitutes a valid individuals
        for name, details in self.genotype.to_phenotype_mapping.items():
            if np.isnan(details["state"]).any():
                return False
            if name == "material":
                state = details["state"]
                # Discarding the robot if it doesn't have at least a given percentage of non-empty voxels
                if np.sum(state>0) < np.product(self.genotype.orig_size_xyz) * min_percent_full or np.sum(state>0) > np.product(self.genotype.orig_size_xyz) * max_percent_full:
                    return False

                isFilled_state = np.where(state != 0, 1, 0)

                if desired_behavior == "max_vol_3D":
                    # check if the corners are located
                    empty_segment  = np.zeros((self.genotype.orig_size_xyz[0], self.genotype.orig_size_xyz[1], self.genotype.orig_size_xyz[2]))
                    empty_segment[0,                                   0,                                 0] = 1
                    empty_segment[0,                                   self.genotype.orig_size_xyz[1]-1,  0] = 1
                    empty_segment[0,                                   self.genotype.orig_size_xyz[1]-1,  self.genotype.orig_size_xyz[2]-1] = 1
                    empty_segment[self.genotype.orig_size_xyz[0]-1   , self.genotype.orig_size_xyz[1]-1,  self.genotype.orig_size_xyz[2]-1] = 1
                    empty_segment[self.genotype.orig_size_xyz[0]-1   , self.genotype.orig_size_xyz[1]-1,  0] = 1
                    empty_segment[self.genotype.orig_size_xyz[0]-1   , 0,                                 self.genotype.orig_size_xyz[2]-1] = 1
                    empty_segment[0,                                   0,                                 self.genotype.orig_size_xyz[2]-1] = 1
                    empty_segment[self.genotype.orig_size_xyz[0]-1,    0,                                 0] = 1

                    design_mask = empty_segment

                    if np.sum(np.multiply(isFilled_state, design_mask)) != 8:
                        return False

                    if desired_behavior == "max_vol_3D":
                        # check if each axis is filled
                        _axis0 = np.sum(isFilled_state, axis=0)
                        _axis1 = np.sum(isFilled_state, axis=1)
                        _axis2 = np.sum(isFilled_state, axis=2)

                        _axis0 = np.where(_axis0 < 2, 1, 0)
                        _axis1 = np.where(_axis1 < 2, 1, 0)
                        _axis2 = np.where(_axis2 < 2, 1, 0)
                        if np.any(_axis1) or np.any(_axis2):
                            return False
                        if np.any(_axis0[0:2]) or np.any(_axis0[5:7]) or np.any(_axis0[:,0:2]) or np.any(_axis0[:,5:7]):
                            return False

                else:
                    # check if its 3D or 2D case
                    _is3Ddemo =  np.all([1 if _x>1 else 0 for _x in list(self.genotype.orig_size_xyz)])
                    if not _is3Ddemo:  # 2D demo case

                        for z in range(int(self.genotype.orig_size_xyz[2]/self.genotype.segment_size_xyz[2])):
                            for y in range(int(self.genotype.orig_size_xyz[1]/self.genotype.segment_size_xyz[1])):
                                for x in range(int(self.genotype.orig_size_xyz[0]/self.genotype.segment_size_xyz[0])):
                                    kernel = state[(x*self.genotype.segment_size_xyz[0]):((x+1)*self.genotype.segment_size_xyz[0]),
                                                    (y*self.genotype.segment_size_xyz[1]):((y+1)*self.genotype.segment_size_xyz[1]),
                                                    (z*self.genotype.segment_size_xyz[2]):((z+1)*self.genotype.segment_size_xyz[2])]
                                    if np.sum(kernel>0) < np.product(self.genotype.segment_size_xyz) * min_percent_full:
                                        return False

                        # discard the robot if it does not have at least one voxel at each direction
                        voxelMap = isFilled_state[:,:,0]
                        sum0 = np.sum(voxelMap, axis=0)
                        sum1 = np.sum(voxelMap, axis=1)
                        if not np.all(sum0) or not np.all(sum1):
                            return False

                    else:  # 3D demo case

                        _axis0 = np.sum(isFilled_state, axis=0)
                        _axis1 = np.sum(isFilled_state, axis=1)
                        _axis2 = np.sum(isFilled_state, axis=2)

                        _axis0 = np.where(_axis0 == self.genotype.orig_size_xyz[0], 1, 0)
                        _axis1 = np.where(_axis1 == self.genotype.orig_size_xyz[1], 1, 0)
                        _axis2 = np.where(_axis2 == self.genotype.orig_size_xyz[2], 1, 0)

                        if not np.any(_axis0) and not np.any(_axis1) and not np.any(_axis2):
                            return False

                        if desired_behavior == "multiM_maxForce":
                            # make sure fixed ends are not set loose
                            if not (np.sum(isFilled_state[:,:,0]) and np.sum(isFilled_state[:,:,(self.genotype.orig_size_xyz[2]-1)])):
                                return False

                # check if at least one of each material type is included
                if mat_num>1:  # confirming it is multi-material case
                    mat_exist_counter = 0
                    for mat_type in range(mat_num+1):
                        if np.any(np.array(state) == mat_type):
                            mat_exist_counter +=1
                    if mat_num > 4:
                        if mat_exist_counter<(mat_num-2): # ensuring at least mat_num types are used
                            return False
                    elif mat_exist_counter<mat_num: # ensuring at least mat_num types are used
                        return False
        return True


class MagSoftBot(object):
    """A SoftBot is a 3D creature composed of a continuous arrangement of connected voxels with varying softness."""

    def __init__(self, args, max_id, genotype, phenotype, objective_dict, BC_dict = None):

        """Initialize an individual SoftBot for physical simulation within VoxCad.

        Parameters
        ----------
        max_id : the lowest id tag unused
            An index to keep track of evolutionary history.

        genotype : Genotype cls
            Defines the networks (genome).

        phenotype : Phenotype cls
            The physical manifestation of the genotype which defines an individual in simulation.

        """
        self.genotype = genotype(orig_size_xyz=args.ind_size, segment_size_xyz=args.segment_size, args=args)  # initialize new random genome
        self.phenotype = phenotype(self.genotype)  # calc phenotype from genome

        self.id = max_id
        self.md5 = "none"
        self.dominated_by = []  # other individuals in the population that are superior according to evaluation
        self.pareto_level = 0
        self.selected = 0  # survived selection
        self.variation_type = "newly_generated"  # (from parent)
        self.parent_genotype = self.genotype  # default for randomly generated ind
        self.parent_id = -1
        self.age = 0
        self.generation=0

        self.voxel_dict = {}  # voxel dictionary for all the related data
        self.allIndividualsDataFolder=args.run_directory + "/allIndividualsData/" + args.run_name

        self.boundary_conditions = None

        # set the objectives as attributes of self (and parent)
        self.objective_dict = objective_dict
        for rank, details in objective_dict.items():
            if details["name"] != "age":
                setattr(self, details["name"], details["worst_value"])
            setattr(self, "parent_{}".format(details["name"]), details["worst_value"])

        # M profile, Shape, and Msegmented --by average pooling
        self.designParameters = {}
        for name, details in self.genotype.to_phenotype_mapping.items():
            self.designParameters.update({name: np.zeros((self.genotype.orig_size_xyz[0], self.genotype.orig_size_xyz[1], self.genotype.orig_size_xyz[2]))})

        self.segmentedMprofile = {}  # this part assumes dividable orig_sizes to segment_sizes for each axis, and segment axis long slide for each axis
        for name, details in self.genotype.to_phenotype_mapping.items():
            if name == "Mphi" or name == "Mtheta":
                self.segmentedMprofile.update({name: np.zeros((int(self.genotype.orig_size_xyz[0]/self.genotype.segment_size_xyz[0]),
                                                                int(self.genotype.orig_size_xyz[1]/self.genotype.segment_size_xyz[1]),
                                                                int(self.genotype.orig_size_xyz[2]/self.genotype.segment_size_xyz[2])))})

        # mapping for voxel # from global to voxelyze frame
        self.voxelNum = self.genotype.orig_size_xyz[0]*self.genotype.orig_size_xyz[1]*self.genotype.orig_size_xyz[2]
        self.isVoxelMap = np.zeros(self.voxelNum)
        self.mappingGlobal2Voxelyze = np.arange(self.voxelNum)

        # set the behavioral characterization(BC) as attributes of self (and parent)
        self.BC_dict = BC_dict
        if self.BC_dict is not None:
            for rank, details in BC_dict.items():
                setattr(self, details["name"], details["worst_value"])
                setattr(self, "parent_{}".format(details["name"]), details["worst_value"])

        # fitness prediction from NN
        self.fitness_prediction=None

        # fitness calculated from the simulation result
        self.fitness_sim = None


    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def save_ind(self, args, individual, design_file=None):
        if design_file is None:
            design_file = self.allIndividualsDataFolder + "/Ind--id_"+str(individual.id).zfill(args.max_ind_1ex)+ "/id_"+str(individual.id).zfill(args.max_ind_1ex)+ '.pickle'
            # design_file = self.allIndividualsDataFolder + "/Ind--id_"+str(individual.id)+ "/id_"+str(individual.id)+ '.pickle'
        to_save = dict()
        to_save.update( individual=individual)

        with open(design_file, "wb") as handle:
            pickle.dump(to_save, handle)

    def load_ind(self, ind_id, args):
        design_file = self.allIndividualsDataFolder + "/Ind--id_"+str(ind_id).zfill(args.max_ind_1ex)+ "/id_"+str(ind_id).zfill(args.max_ind_1ex)+ '.pickle'
        with open(design_file, 'rb') as f:
            out = pickle.load(f)
        individual = out['individual']
        assert (individual.id == ind_id)

        return individual


class Population(object):
    """A population of SoftBots."""

    def __init__(self, args, genotype, phenotype, objective_dict, BC_dict=None, NN=None):

        """Initialize a population of individual SoftBots.

        Parameters
        ----------
        BC_dict:  BehavioralCharacterizationDict()
            Defines the BCs for novelty -- MAP-elites

        objective_dict : ObjectiveDict()
            Defines the objectives to optimize.

        genotype : Genotype
            The genetic code used to create an individual and passed to offspring (with modification).

        phenotype : Phenotype
            The physical manifestation of the genotype which defines an individual in simulation.

        pop_size : int
            The target number of individuals to maintain in the population.

        """
        self.args = args
        self.genotype = genotype
        self.phenotype = phenotype
        self.pop_size = args.pop_size
        self.gen = 0
        self.gen_tot_time = 0
        self.gen_eval_time = 0
        self.gen_mut_time = 0
        self.gen_obj_update_time = 0
        self.gen_arch_handle_time = 0
        self.gen_novelty_calc_time = 0
        self.total_evaluations = 0
        self.already_evaluated = {}
        self.all_evaluated_individuals_ids = []

        self.objective_dict = objective_dict
        self.best_fit_so_far = objective_dict[0]["worst_value"]
        self.best_fit_ind_id = 0

        self.best_fit_so_far_onSim_GT = objective_dict[0]["worst_value"]

        self.des_VoxPos  = getDesiredShape(args)

        self.BC_dict = BC_dict

        self.NN=NN
        self.explore=True
        self.mutations_NN_guided = False
        self.start_NN_predictions = False

        self.individuals = []
        self.lineage_dict = {}
        self.max_id = 0
        self.non_dominated_size = 0

        # Stats to keep track of
        self.logbook = {}
        self.keep_track_of = ["min", "max", "mean", "stdev"]
        self.record_these_too = ["Ind_IDs_for_gen"]

        # initialize the stats, take this as a reference whenever you want to accesss/update the generation stats
        for rank, details in self.objective_dict.items():
            self.logbook[details["name"]] = {}
            for param in self.keep_track_of:
                self.logbook[details["name"]][param] = []
        for param in self.record_these_too:
            self.logbook[param] = []  # list of individual IDs for each generation
        self.logbook["best_fit_IDS"] = []

        self.logbook["best_fit_onSim_GT"] = []


        self.logbook["isExplore"] = []
        self.logbook["best_fit_parent_IDS"] = []
        self.logbook["best_fit_age"] = []


        if self.BC_dict is not None:
            for rank, details in self.BC_dict.items():
                self.logbook[details["name"]] = {}
                for param in self.keep_track_of:
                    self.logbook[details["name"]][param] = []

        while len(self) < args.pop_size:
            self.add_random_individual()
        print("\nInitial population of " + str(args.pop_size) + " individuals is generated\n\n")

    def __iter__(self):
        """Iterate over the individuals. Use the expression 'for n in population'."""
        return iter(self.individuals)

    def __contains__(self, n):
        """Return True if n is a SoftBot in the population, False otherwise. Use the expression 'n in population'."""
        try:
            return n in self.individuals
        except TypeError:
            return False

    def __len__(self):
        """Return the number of individuals in the population. Use the expression 'len(population)'."""
        return len(self.individuals)

    def __getitem__(self, n):
        """Return individual n.  Use the expression 'population[n]'."""
        return self.individuals[n]

    def pop(self, index=None):
        """Remove and return item at index (default last)."""
        return self.individuals.pop(index)

    def append(self, individuals):
        """Append a list of new individuals to the end of the population.

        Parameters
        ----------
        individuals : list of/or MagSoftBot
            A list of individual MagSoftBots to append or a single MagSoftBot to append

        """
        if type(individuals) == list:
            for n in range(len(individuals)):
                if type(individuals[n]) != MagSoftBot:
                    raise TypeError("Non-SoftBot added to the population")
            self.individuals += individuals

        elif type(individuals) == MagSoftBot:
            self.individuals += [individuals]

    def sort(self, key, reverse=False):
        """Sort individuals by their attributes.

        Parameters
        ----------
        key : str
            An individual-level attribute.

        reverse : bool
            True sorts from largest to smallest (useful for maximizing an objective).
            False sorts from smallest to largest (useful for minimizing an objective).

        """
        return self.individuals.sort(reverse=reverse, key=operator.attrgetter(key))

    def add_random_individual(self):
        valid = False
        while not valid:
            ind = MagSoftBot(self.args, self.max_id, self.genotype, self.phenotype, self.objective_dict, self.BC_dict)
            if ind.phenotype.is_valid(min_percent_full = self.args.min_volume_ratio, desired_behavior = self.args.desired_shape, mat_num = self.args.material_num, max_percent_full = self.args.max_volume_ratio):
                ind.generation=self.gen
                self.individuals.append(ind)
                self.max_id += 1
                valid = True

    def update_ages(self):
        """Increment the age of each individual."""
        for ind in self:
            ind.age += 1
            ind.variation_type = "survived"

    def update_lineages(self):
        """Tracks ancestors of the current population."""
        for ind in self:
            if ind.id not in self.lineage_dict:
                if ind.parent_id > -1:
                    # parent already in dictionary
                    self.lineage_dict[ind.id] = [ind.parent_id] + self.lineage_dict[ind.parent_id]
                else:
                    # randomly created ind has no parents
                    self.lineage_dict[ind.id] = []

        current_ids = [ind.id for ind in self]
        keys_to_remove = [key for key in self.lineage_dict if key not in current_ids]
        for key in keys_to_remove:
            del self.lineage_dict[key]

    def update_NN_mutations(self):
        if self.args.cluster_debug: print("updating NN mutations")
        if self.args.use_NN and (self.max_id>self.args.NN_when_to_use or self.args.NN_warm_start):
            self.start_NN_predictions=True
            if not self.explore and (not self.args.optimizer_type == "MAP_Elites_CPPN_onNN" and not self.args.optimizer_type == "DSA_ME" ):
                self.mutations_NN_guided = True
            else:
                self.mutations_NN_guided = False
        if self.args.cluster_debug: print("NN mutations updated")

    def sort_by_objectives(self):
        """Sorts the population multiple times by each objective, from least important to most important."""
        for ind in self:
            if math.isnan(ind.fitness):
                ind.fitness = self.objective_dict[0]["worst_value"]
                print ("FITNESS WAS NAN, RESETTING IT TO:", self.objective_dict[0]["worst_value"])
                print ("for ind id: ", ind.id)

        self.sort(key="id", reverse=True)  # (max) promotes neutral mutation
        self.sort(key="age", reverse=False)  # (min) protects younger, undeveloped solutions

        for rank in reversed(range(len(self.objective_dict))):
            if not self.objective_dict[rank]["logging_only"]:
                goal = self.objective_dict[rank]
                self.sort(key=goal["name"], reverse=goal["maximize"])

        self.sort(key="pareto_level", reverse=False)  # min

        # print "rank in sort_by_objectives:", [len(i.dominated_by) for i in self]
        # print "age in sort_by_objectives:", [i.age for i in self]
        # print "fitness in sort_by_objectives:", [i.fitness for i in self]

    def dominated_in_multiple_objectives(self, ind1, ind2):
        """Calculate if ind1 is dominated by ind2 according to all objectives in objective_dict.

        If ind2 is better or equal to ind1 in all objectives, and strictly better than ind1 in at least one objective.

        """
        # losses = []  # 2 dominates 1
        wins = []  # 1 dominates 2
        for rank in reversed(range(len(self.objective_dict))):
            if not self.objective_dict[rank]["logging_only"]:
                goal = self.objective_dict[rank]
                # losses += [dominates(ind2, ind1, goal["name"], goal["maximize"])]  # ind2 dominates ind1?
                wins += [dominates(ind1, ind2, goal["name"], goal["maximize"])]  # ind1 dominates ind2?
        # return np.any(losses) and not np.any(wins)
        return not np.any(wins)

    def calc_dominance(self):
        """Determine which other individuals in the population dominate each individual."""

        self.sort(key="id", reverse=False)  # if tied on all objectives, give preference to newer individual

        # clear old calculations of dominance
        self.non_dominated_size = 0
        for ind in self:
            ind.dominated_by = []
            ind.pareto_level = 0

        for ind in self:
            for other_ind in self:
                # if (other_ind.fitness >= ind.fitness) and \
                #         self.dominated_in_multiple_objectives(ind, other_ind) and \
                #         (ind.id not in other_ind.dominated_by) and \
                #         (other_ind.id != ind.id):
                if other_ind.id != ind.id:
                    if self.dominated_in_multiple_objectives(ind, other_ind) and (ind.id not in other_ind.dominated_by):
                        ind.dominated_by += [other_ind.id]

            if ind.fitness == self.objective_dict[0]["worst_value"]:  # extra penalty for doing nothing or being invalid
                ind.dominated_by += [ind.id for _ in range(self.pop_size * 2)]

            ind.pareto_level = len(ind.dominated_by)  # update the pareto level

            # update the count of non_dominated individuals
            if ind.pareto_level == 0:
                self.non_dominated_size += 1

    def compute_NN_prediction(self, ind):
        "makes a prediction on the ind design using best trained model so far"
        for name, details in ind.genotype.to_phenotype_mapping.items():
            new = details["state"]
            if name=="material":
                voxel_map=new
            if name=="Mtheta":
                Mtheta=new
            if name=="Mphi":
                Mphi=new
        voxel_map1D = voxel_map.flatten()
        Mtheta1D = Mtheta.flatten()
        Mphi1D= Mphi.flatten()
        x=np.concatenate((voxel_map1D,Mtheta1D, Mphi1D))
        X_predict = x.reshape(1, x.size)
        y_predict=self.NN.NN(X_predict).numpy()
        if self.args.NN_data_process_type == "beam":
            if not self.args.fitness_maximize:
                return y_predict[0]*np.max(self.args.ind_size)*self.args.lattice_dim*1e3*2
            else:
                return y_predict[0]

        elif self.args.NN_data_process_type == "sheet":
            return y_predict[0]
        else:
            raise    NotImplementedError


class BCArchive(object):
    """
    The archive is actually two archives:
        - The archive of all past BC. It is used to compute novelty measures
        - The current map-elite population (Behavioral map).
    """

    def __init__(self, args, obj_dict, BC_dict):
        self.args = args
        self.obj_dict = obj_dict
        self.BC_dict = BC_dict

        self.k = args.novelty_k # number of neighbors for knn novelty score

        self.dim_bc = 0 # number of dimensions of the bc
        for rank, details in BC_dict.items():
            if not details["logging_only"]:
                self.dim_bc +=1

        self.nb_cells_per_dimension = np.zeros((self.dim_bc), dtype = int)  # number of cells for each dimension for map discretization
        self.min_max_bcs = np.zeros((self.dim_bc,2), dtype = float)  # min and max values for each dimension of the bc
        for rank, details in BC_dict.items():   # considering the dictionaries keeps the order since py3.6
            if not details["logging_only"]:
                self.nb_cells_per_dimension[rank] = details["nb_cells"]
                self.min_max_bcs[rank,0] = details["min"]
                self.min_max_bcs[rank,1] = details["max"]

        self.algo = self.args.optimizer_type

        self.archive_folder = self.args.run_directory + '/archive'
        os.makedirs(self.archive_folder, exist_ok=True)
        self.design_folder = self.args.run_directory + '/archiveElites'
        os.makedirs(self.design_folder, exist_ok=True)

        self.nn_model = NearestNeighbors(n_neighbors=self.k, algorithm='ball_tree', metric='euclidean')
        self.all_bcs = []  # contains bcs of all individuals seen so far
        self.all_perfs = []  # contains performances of individuals seen so far
        self.empty = True  # whether the archive is empty or not

        # # # # # # #
        # ME archive
        # # # # # # #

        self.mees_strategy_explore = args.explore_strategy  # strategy to sample a cell to start exploration
        self.mees_strategy_exploit = args.exploit_strategy  # strategy to sample a cell to start exploitation
        self.cell_ids = np.arange(int(np.prod(self.nb_cells_per_dimension))).reshape(self.nb_cells_per_dimension)  # array containing all cell ids
        self.filled_cells = []  # list of filled cells, contain cell ids
        self.iteration_filled_cells = []
        self.me_bcs = []  # list of stored individuals bcs
        self.performances = []  # list of stored individuals performances
        # keep tracks of various metrics
        self.stats_novelty = [[]]
        self.stats_best_train = [[]]
        self.stats_archive_performance = dict(mean=[], std=[], median=[], max=[], min=[], cell_count=[])

        # Define boundaries
        self.boundaries = []  # boundaries for each cell
        self.cell_sizes = []  # compute cell size
        for i in range(self.dim_bc):
            bc_min = self.min_max_bcs[i,0]
            bc_max = self.min_max_bcs[i,1]
            boundaries = np.arange(bc_min, bc_max + 1e-5, (bc_max - bc_min) / self.nb_cells_per_dimension[i])
            boundaries[0] = - np.inf
            boundaries[-1] = np.inf
            self.boundaries.append(boundaries)
            self.cell_sizes.append((bc_max - bc_min) / self.nb_cells_per_dimension)

        # log
        self.history = []
        os.makedirs(self.archive_folder, exist_ok=True)
        with open(self.archive_folder + '/cell_ids.pk', 'wb') as f:
            pickle.dump(self.cell_ids, f)
        with open(self.archive_folder + '/cell_boundaries.pk', 'wb') as f:
            pickle.dump(self.boundaries, f)

        "more data for post-processing"
        # counting the number of individuals evaluated at the cells
        self.map_total_inds = np.empty((self.nb_cells_per_dimension))
        self.map_total_inds.fill(np.nan)
        self.map_perf = np.empty((self.nb_cells_per_dimension)) # map of best performances
        self.map_perf.fill(np.nan)

        # checkpoint
        self.checkpoint_folder = self.args.run_directory + '/pickledPops'

        # timing debugging
        self.novelty_time = 0

    def update_novelty(self):
        for index in range(len(self.filled_cells)):
            bc = self.me_bcs[index].reshape(1, -1)
            novelty = self.compute_novelty(bc)[0]
            self.stats_novelty[-1][index] = novelty

    def compute_novelty(self, bc):
        if bc.ndim == 1:
            bc = bc.reshape(1, -1)
        if self.empty:
            distances = (np.ones([bc.shape[0]]) * np.inf).reshape(-1, 1)
        else:
            distances, _ = self.nn_model.kneighbors(bc, n_neighbors=min(self.k, self.size_ns))
            # skip the bc if it is already in the archive.
            if distances.shape[0] == 1 and distances[0, 0] == 0:
                distances = distances[:, 1:]
        return (distances ** 2).mean(axis=1)

    @property
    def size_ns(self):
        return len(self.all_bcs)

    @property
    def size_me(self):
        return len(self.filled_cells)


    def fix_probas(self, probs):
        test_passed = False
        for ii in range(probs.shape[0]):
            if probs.sum() < 1:
                if probs[ii] + (1 - probs.sum()) <= 1:
                    probs[ii] += (1 - probs.sum())
            elif probs.sum() > 1:
                if probs[ii] - (probs.sum() - 1) >= 0:
                    probs[ii] -= (probs.sum() - 1)
            if probs.sum() == 1 and np.all(probs >= 0) and np.all(probs <= 1):
                test_passed = True
                break
        return probs, test_passed

    def select_pop(self, explore):
        if self.args.cluster_debug: print("updating NN mutations")
        # function called to sample the next population to optimize, the method depends on the algorithm
        if not self.empty:
            if self.algo in ['nses', 'nsres', 'nsraes']:
                theta = None
            elif self.algo == "MAP_Elites_CPPN" or self.algo == "MAP_Elites_CPPN_onNN" or self.algo == "DSA_ME":
                offspring = self.sample_mega(explore)
            else:
                raise NotImplementedError

            if self.args.cluster_debug: print("the pop from the archieve is selected")
            return offspring
        else:
            if self.args.cluster_debug: print("The archive is empty")
            raise IndexError('The archive is empty')


        return offspring

    def sample_mega(self, explore):
        # compute probability depending on the explore/exploit state and sampling strategy
        n_offspring = self.args.pop_size   # required number of individuals for the next evaluation
        n_candidates = len(self.filled_cells)
        p_random = 1 / n_candidates
        offspring = []

        if n_offspring > n_candidates:
            for index in range(n_candidates):
                cell_id = self.filled_cells[index]

                # extract corresponding design load from file
                performance = self.performances[index]
                bc = self.me_bcs[index]
                individual = self.load_design(cell_id, performance, bc)
                offspring.append(individual)

            to_log = 'Offspring of {} sampled remaining {} individuals will be randomly chosen'.format(len(offspring), (n_offspring - len(offspring)))
            logger.info(to_log)
            return offspring
        elif (explore and self.mees_strategy_explore == 'uniform'):
            values = None
            method = 'uniform'
        elif explore and self.mees_strategy_explore == 'novelty_bias':
            values = np.array(self.stats_novelty[-1])
            if n_candidates>5*self.args.pop_size:
                method = 'uniform_plus_proportional_x5_best'
            else:
                method = "proportional"

        elif (not explore and self.mees_strategy_exploit == "bests"):
            values = None
            method = "bests"
        else:
            raise NotImplementedError


        if not explore:

            # exploit
            if method =="bests":
                # get certain part of the offspring as exploiting the best inds.
                if not self.args.fitness_maximize:
                    k=int(n_offspring)-1
                    indexes=np.argpartition(self.performances, (k))[:(k)]
                else:
                    k=int(n_offspring)-1
                    indexes=np.argpartition(self.performances, (-k))[-k:]

                for index in range(len(indexes)):
                    # extract corresponding design load from file
                    cell_id = self.filled_cells[indexes[index]]
                    performance = self.performances[indexes[index]]
                    bc = self.me_bcs[indexes[index]]
                    individual = self.load_design(cell_id, performance, bc)
                    offspring.append(individual)

        else:
            # explore
            probs = self.compute_probabilities(args=self.args, n_candidates=n_candidates, values=values, method=method)

            # sample the next cell_id to start from
            # extremely ugly fix to avoid approx errors to ruin the probs.sum() == 1
            probs, test_passed = self.fix_probas(probs)
            while n_offspring > len(offspring):

                if test_passed:
                    index = np.random.choice(range(n_candidates), p=probs)
                else:
                    logger.info('Probs have fucked up' + str(probs))
                    index = np.random.choice(range(n_candidates))

                cell_id = self.filled_cells[index]

                # extract corresponding design load from file
                performance = self.performances[index]
                bc = self.me_bcs[index]
                individual = self.load_design(cell_id, performance, bc)
                offspring.append(individual)

        return offspring

    def compute_probabilities(self, args, n_candidates, values, method='uniform'):
        # method to compute probabilities depending on values
        if method == 'uniform':
            probas = 1 / n_candidates * np.ones([n_candidates])
        else:
            scores = values.copy()
            n_candidates = scores.size
            eps = 0.1
            if method == 'proportional':
                probas = scores / scores.sum()
            elif method == 'uniform_plus_proportional_x5_best':
                except_best_5x = np.argsort(scores)[:-(5*args.pop_size)]
                scores[except_best_5x] = 0
                probas = eps * np.ones(n_candidates) / n_candidates + (1 - eps) * scores / scores.sum()
            elif method == 'argmax':
                probas = np.zeros([n_candidates])
                probas[np.argmax(values)] = 1
            else:
                raise NotImplementedError
        return probas


    def find_cell_id(self, bc):
        """
        Find cell identifier of the BC map corresponding to bc
        """
        coords = []
        for j in range(self.dim_bc):
            inds = np.atleast_1d(np.argwhere(self.boundaries[j] < bc[j]).squeeze())
            coords.append(inds[-1])
        coords = tuple(coords)
        cell_id = self.cell_ids[coords]

        return cell_id, coords

    def compare_fitness(self, isMaximize, best_fitness, new_fitness):
        if isMaximize:  # maximizing the fitness
            if new_fitness>best_fitness:
                return True
        elif not isMaximize:  # minimizing the fitness
            if new_fitness<best_fitness:
                return True
        else:
            raise NotImplementedError
        return False

    def add_individual(self, args, individual, iter, explore = None):
        """
        Attempt to add the new individual to the behavioral map
        """

        # get the performance(fitness) and BCs/novelties
        performance = getattr(individual, "fitness")
        best_train_performance = performance

        new_bc = []
        previous_bc = []

        for rank, details in individual.BC_dict.items():   # considering the dictionaries keeps the order since py3.6, no need to use rank
            if not details["logging_only"]:
                new_bc.append(getattr(individual, details["name"]))
                previous_bc.append(getattr(individual, "parent_{}".format(details["name"])))
        new_bc = np.array(new_bc)
        previous_bc =  np.array(previous_bc)
        starting_bc = previous_bc

        if self.empty:
            self.all_bcs.append(new_bc)
            self.all_perfs.append(performance)
            self.nn_model.fit(np.array(self.all_bcs))

        # update selection scores
        # copy old selection scores for that new generation (need to copy, as cell may be updated)
        if iter > 0 and iter == len(self.stats_best_train):
            self.stats_best_train.append(self.stats_best_train[-1].copy())
            if self.args.explore_strategy == "novelty_bias":
                self.stats_novelty.append(self.stats_novelty[-1].copy())
        #     self.stats_xpos.append(self.stats_xpos[-1].copy())

        # # # # # # # # # #
        # Update ME Archive
        # # # # # # # # # #

        # find cell_id of the new_bc
        cell_id, coords = self.find_cell_id(new_bc)

        # counting the number of individuals evaluated at the cells
        if not np.isnan(self.map_total_inds[coords]):
            self.map_total_inds[coords] += 1
        else:
            self.map_total_inds[coords] = 1

        if iter != 0 and all(item > 0 for (item) in previous_bc) > 0 :
            # if starting from a cell, update the best training performance for that cell, This is used to bias sampling of cell to start exploitation
            previous_cell_id, coords = self.find_cell_id(previous_bc)
            if not np.size(np.argwhere(self.filled_cells == previous_cell_id)) ==0:
                previous_index = np.argwhere(self.filled_cells == previous_cell_id)[0][0]
                if np.all(previous_bc == self.me_bcs[previous_index]):
                    self.stats_best_train[-1][previous_index] = best_train_performance
                    # logger.info('Updating best performance of cell {}, with best perf {}'.format(previous_cell_id, best_train_performance))

        str_history = ''

        # if cell already filled
        if cell_id in self.filled_cells:
            new_cell = False
            index = np.argwhere(self.filled_cells == cell_id)[0][0]

            # check whether performance is better

            maximize = self.obj_dict[0]["maximize"]  # get if we are maximizing or minimizing the objective

            if self.compare_fitness(maximize, best_fitness=self.performances[index], new_fitness=performance):
                update = True
                individual_update = individual
                self.performances[index] = performance
                self.me_bcs[index] = new_bc
                perf_update = performance
                bc_update = new_bc
                str_history += 'perf'
                self.map_perf[coords] = performance  # update the map_perf
            else:
                update = False
                individual_update = None
                bc_update = None
                perf_update = None


        # if new cell
        else:
            new_cell = True
            update = True
            index = -1
            self.filled_cells.append(cell_id)
            self.iteration_filled_cells.append(iter)
            self.stats_best_train[-1].append(0)
            # self.stats_xpos[-1].append(0)
            if self.args.explore_strategy == "novelty_bias":
                self.stats_novelty[-1].append(0)
            self.performances.append(performance)
            self.me_bcs.append(new_bc)
            individual_update = individual
            bc_update = new_bc
            perf_update = performance
            self.map_perf[coords] = performance   # update the map_perf

        if update:
            self.save_design(design_dir=self.design_folder,
                                individual=individual_update,
                                bc=bc_update,
                                performance=perf_update,
                                cell_id=cell_id,
                                iter=iter
                                )

            # log
            if new_cell:
                self.history.append(['add', str_history, bc_update, perf_update, iter, cell_id, starting_bc, explore])
                to_log = 'New individual added to the archive in cell {}, new bc {}! '.format(cell_id, bc_update)
            else:
                self.history.append(['replace', str_history, bc_update, perf_update, iter, cell_id, starting_bc, explore])
                to_log = 'New individual added to the archive in cell {}. '.format(cell_id)
                if str_history == 'perf':
                    to_log += 'Better performance.'
            logger.info(to_log)

            # store best training performance of the previous cell in the newly discovered cell.
            # it will be updated when it is selected as starting cell
            self.stats_best_train[-1][index] = best_train_performance

        else:
            self.history.append(['nothing', str_history, bc_update, perf_update, iter, cell_id, starting_bc, explore])


        if self.args.explore_strategy == "novelty_bias":
            # update novelty scores
            novelty_start = time.time()
            if iter == 0:
                self.stats_novelty[-1][index] = 1e6
            else:
                self.update_novelty()
            self.novelty_time += (time.time()-novelty_start)

        # update novelty archive and knn model
        # add bc and perf to list of all bcs and perfs
        if not self.empty:
            self.all_bcs.append(new_bc)
            self.all_perfs.append(performance)
            if self.args.explore_strategy == "novelty_bias":
                novelty_start = time.time()
                self.nn_model.fit(np.array(self.all_bcs))
                self.novelty_time += (time.time()-novelty_start)
        else:
            self.empty = False

        # track stats about the quality of the archive
        self.stats_archive_performance['mean'].append(np.mean(self.all_perfs))
        self.stats_archive_performance['median'].append(np.median(self.all_perfs))
        self.stats_archive_performance['max'].append(np.max(self.all_perfs))
        self.stats_archive_performance['std'].append(np.std(self.all_perfs))
        self.stats_archive_performance['min'].append(np.min(self.all_perfs))
        self.stats_archive_performance['cell_count'].append(len(self.all_perfs))
        return update

    def add_population(self, args, pop, explore = None):
        if args.cluster_debug: print("adding pop to the archieve")
        # inds = np.flip(np.argsort(perfs).flatten(), axis=0)
        self.novelty_time = 0
        for individual in pop:
            self.add_individual(args, individual, pop.gen, explore)

        # plot the maps
        self.plot_maps(self.map_total_inds, save_dir = self.archive_folder + '/map_total_inds_', highQuality = 1)
        self.plot_maps(self.map_perf, save_dir = self.archive_folder + '/map_perf_',colorBar_limits=[0,1], highQuality = 1)

        if args.cluster_debug: print("pop added to the BC archieve")


    def update_cell(self, args, individual, iter, explore = None):
        """
        Attempt to add the new individual to the behavioral map
        """

        # get the performance(fitness) and BCs/novelties
        performance = getattr(individual, "fitness")
        best_train_performance = performance

        new_bc = []
        previous_bc = []

        for rank, details in individual.BC_dict.items():   # considering the dictionaries keeps the order since py3.6, no need to use rank
            if not details["logging_only"]:
                new_bc.append(getattr(individual, details["name"]))
                previous_bc.append(getattr(individual, "parent_{}".format(details["name"])))
        new_bc = np.array(new_bc)
        previous_bc =  np.array(previous_bc)
        starting_bc = previous_bc

        if self.empty:
            self.all_bcs.append(new_bc)
            self.all_perfs.append(performance)
            self.nn_model.fit(np.array(self.all_bcs))

        # update selection scores
        # copy old selection scores for that new generation (need to copy, as cell may be updated)
        if iter > 0 and iter == len(self.stats_best_train):
            self.stats_best_train.append(self.stats_best_train[-1].copy())
            if self.args.explore_strategy == "novelty_bias":
                self.stats_novelty.append(self.stats_novelty[-1].copy())
        #     self.stats_xpos.append(self.stats_xpos[-1].copy())

        # # # # # # # # # #
        # Update ME Archive
        # # # # # # # # # #

        # find cell_id of the new_bc
        cell_id, coords = self.find_cell_id(new_bc)

        # counting the number of individuals evaluated at the cells
        if not np.isnan(self.map_total_inds[coords]):
            self.map_total_inds[coords] += 1
        else:
            self.map_total_inds[coords] = 1

        if iter != 0 and all(item > 0 for (item) in previous_bc) > 0 :
            # if starting from a cell, update the best training performance for that cell, This is used to bias sampling of cell to start exploitation
            previous_cell_id, coords = self.find_cell_id(previous_bc)
            previous_index = np.argwhere(self.filled_cells == previous_cell_id)[0][0]
            if np.all(previous_bc == self.me_bcs[previous_index]):
                self.stats_best_train[-1][previous_index] = best_train_performance
                # logger.info('Updating best performance of cell {}, with best perf {}'.format(previous_cell_id, best_train_performance))

        str_history = ''

        # if cell already filled
        if cell_id in self.filled_cells:
            new_cell = False
            index = np.argwhere(self.filled_cells == cell_id)[0][0]

            update = True
            individual_update = individual
            self.performances[index] = performance
            self.me_bcs[index] = new_bc
            perf_update = performance
            bc_update = new_bc
            str_history += 'update'
            self.map_perf[coords] = performance  # update the map_perf

        # if new cell
        else:
            new_cell = True
            update = True
            index = -1
            self.filled_cells.append(cell_id)
            self.iteration_filled_cells.append(iter)
            self.stats_best_train[-1].append(0)
            # self.stats_xpos[-1].append(0)
            if self.args.explore_strategy == "novelty_bias":
                self.stats_novelty[-1].append(0)
            self.performances.append(performance)
            self.me_bcs.append(new_bc)
            individual_update = individual
            bc_update = new_bc
            perf_update = performance
            self.map_perf[coords] = performance   # update the map_perf

        if update:
            self.save_design(design_dir=self.design_folder,
                                individual=individual_update,
                                bc=bc_update,
                                performance=perf_update,
                                cell_id=cell_id,
                                iter=iter
                                )

            # log
            if new_cell:
                self.history.append(['add', str_history, bc_update, perf_update, iter, cell_id, starting_bc, explore])
                to_log = 'New individual added to the archive in cell {}, new bc {}! '.format(cell_id, bc_update)
            else:
                self.history.append(['replace', str_history, bc_update, perf_update, iter, cell_id, starting_bc, explore])
                to_log = 'New individual added to the archive in cell {}. '.format(cell_id)
                if str_history == 'perf':
                    to_log += 'Better performance.'
            logger.info(to_log)

            # store best training performance of the previous cell in the newly discovered cell.
            # it will be updated when it is selected as starting cell
            self.stats_best_train[-1][index] = best_train_performance

        else:
            self.history.append(['nothing', str_history, bc_update, perf_update, iter, cell_id, starting_bc, explore])


        if self.args.explore_strategy == "novelty_bias":
            # update novelty scores
            novelty_start = time.time()
            if iter == 0:
                self.stats_novelty[-1][index] = 1e6
            else:
                self.update_novelty()
            self.novelty_time += (time.time()-novelty_start)

        # update novelty archive and knn model
        # add bc and perf to list of all bcs and perfs
        if not self.empty:
            self.all_bcs.append(new_bc)
            self.all_perfs.append(performance)
            if self.args.explore_strategy == "novelty_bias":
                novelty_start = time.time()
                self.nn_model.fit(np.array(self.all_bcs))
                self.novelty_time += (time.time()-novelty_start)
        else:
            self.empty = False

        # track stats about the quality of the archive
        self.stats_archive_performance['mean'].append(np.mean(self.all_perfs))
        self.stats_archive_performance['median'].append(np.median(self.all_perfs))
        self.stats_archive_performance['max'].append(np.max(self.all_perfs))
        self.stats_archive_performance['std'].append(np.std(self.all_perfs))
        self.stats_archive_performance['min'].append(np.min(self.all_perfs))
        self.stats_archive_performance['cell_count'].append(len(self.all_perfs))
        return update

    def update_archive(self, args, pop, explore = None):
        if args.cluster_debug: print("adding pop to the archieve")
        # inds = np.flip(np.argsort(perfs).flatten(), axis=0)
        self.novelty_time = 0
        for individual in pop:
            self.update_cell(args, individual, pop.gen, explore)

        # plot the maps
        self.plot_maps(self.map_total_inds, save_dir = self.archive_folder + '/map_total_inds_', highQuality = 1)
        self.plot_maps(self.map_perf, save_dir = self.archive_folder + '/map_perf_',colorBar_limits=[0,1], highQuality = 1)

        if args.cluster_debug: print("BC archive is updated with new data")


    def save_data(self):

        with open(self.archive_folder + '/history.pk', 'wb') as f:
            pickle.dump(self.history, f)

        with open(self.archive_folder + '/best_train.pk', 'wb') as f:
            pickle.dump(self.stats_best_train, f)

        # with open(self.archive_folder + 'final_xpos.pk', 'wb') as f:
        #     pickle.dump(self.stats_xpos, f)

        with open(self.archive_folder + '/nov.pk', 'wb') as f:
            pickle.dump(self.stats_novelty, f)

        with open(self.archive_folder + '/stat_archive_perfs.pk', 'wb') as f:
            pickle.dump(self.stats_archive_performance, f)

        np.savetxt(self.archive_folder + '/final_me_perfs.txt', np.array(self.performances))
        np.savetxt(self.archive_folder + '/final_ns_bcs.txt', np.array(self.all_bcs))
        np.savetxt(self.archive_folder + '/final_ns_perfs.txt', np.array(self.all_perfs))
        np.savetxt(self.archive_folder + '/final_me_bcs.txt', np.array(self.me_bcs))
        np.savetxt(self.archive_folder + '/final_filled_cells.txt', np.array(self.filled_cells))

        with open(self.archive_folder + '/map_total_inds.pk', 'wb') as f:
            pickle.dump(self.map_total_inds, f)
        with open(self.archive_folder + '/map_perf.pk', 'wb') as f:
            pickle.dump(self.map_perf, f)

    def save_design(self, design_dir, individual, bc, cell_id, performance, iter):
        design_file = design_dir + "/" + str(cell_id) + '.pickle'

        to_save = dict()
        to_save.update( individual=individual,
                        bc=bc,
                        performance=performance,
                        iter=iter,
                        )

        with open(design_file, "wb") as handle:
            pickle.dump(to_save, handle)

    def load_design(self, cell_id, perf, bcTemp):
        design_file = self.design_folder + "/" +str(cell_id) + '.pickle'
        with open(design_file, 'rb') as f:
            out = pickle.load(f)
        individual = out['individual']
        assert np.all(bcTemp == np.array(out['bc']))
        assert perf == out['performance']

        return individual

    def plot_maps(self, map, save_dir, colorBar_limits=[None, None], highQuality = 0):
        dpiValue = 25
        if highQuality:
            dpiValue = 300

        # draw the 2D BCs as a scatter plot
        if self.dim_bc == 2:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            extent=[self.min_max_bcs[0][0],self.min_max_bcs[0][1],self.min_max_bcs[1][0],self.min_max_bcs[1][1]]
            cax= ax.imshow(np.transpose(map),origin='upper', cmap = "plasma", extent=extent, aspect="auto", vmin=colorBar_limits[0], vmax=colorBar_limits[1])
            # ax.set_aspect(1)

            ax.set_xlabel(self.BC_dict[0]["name"])
            ax.set_ylabel(self.BC_dict[1]["name"])

            fig.colorbar(cax)
            plt.savefig(save_dir+"matrix.png", dpi=dpiValue)
            plt.close()

        # draw the 3D BCs as a scatter plot
        elif self.dim_bc == 3:\
            # not implemented
            return

    def save_archive(self, args, archive, archive_file=None):
        if archive_file is None:
            archive_file = self.archive_folder + '/final_archive.pickle'

        to_save = dict()
        to_save.update( archive=archive)

        with open(archive_file, "wb") as handle:
            pickle.dump(to_save, handle)

    def load_archive(self, args, archive_file=None):
        if archive_file is None:
            archive_file = self.archive_folder + '/final_archive.pickle'

        with open(archive_file, 'rb') as f:
            out = pickle.load(f)
        archive = out['archive']

        return archive

    def save_at_checkpoint(self, args, generation ,file_path=None):
        if file_path is None:
            file_path = self.checkpoint_folder + "/archiveElites_gen" +str(generation)+".tar.gz"
        # save the current BC cell information at the self.design folder
        with tarfile.open(file_path, 'w:gz') as archive:
            archive.add(self.design_folder, arcname='.')

    def load_at_checkpoint(self, args, generation, file_path=None, path_to_extract=None):
        # erase the leftover cell info
        sub.call("rm -r "+self.design_folder+"/*", shell=True)

        # erase the archive data at archive
        sub.call("rm -r "+self.archive_folder+"/*", shell=True)

        # load the checkpoint BC cell information at the self.design folder
        if file_path is None:
            file_path = self.checkpoint_folder + "/archiveElites_gen" +str(generation)+".tar.gz"
        if path_to_extract is None:
            path_to_extract = self.design_folder +"/"
        with tarfile.open(file_path, 'r') as archive:
            archive.extractall(path_to_extract)