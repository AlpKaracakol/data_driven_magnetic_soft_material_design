import random
import numpy as np
import networkx as nx
from networkx import DiGraph
from copy import deepcopy
from collections import OrderedDict

from tools.utils import normalize, sigmoid
from tools.utils import neg_abs, neg_square, sqrt_abs, neg_sqrt_abs, gaussian_e, sin_square_x_plus_x, triangle_wave, sawtooth_wave, square_wave, relu, elu, tanh, swish

class OrderedGraph(DiGraph):
    """Create a graph object that tracks the order nodes and their neighbors are added."""
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict


class Network(object):
    """Base class for networks."""

    input_node_names = []

    def __init__(self, output_node_names, input_node_names, ):
        self.output_node_names = output_node_names
        self.input_node_names = input_node_names
        self.graph = OrderedGraph()  # preserving order is necessary for checkpointing
        self.freeze = False
        self.allow_neutral_mutations = False
        self.num_consecutive_mutations = 1
        self.direct_encoding = False

    def __deepcopy__(self, memo):
        """Override deepcopy to apply to class level attributes"""
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(deepcopy(self.__dict__, memo))
        return new

    def set_input_node_states(self, *args, **kwargs):
        raise NotImplementedError

    def mutate(self, *args, **kwargs):
        raise NotImplementedError


class CPPN(Network):
    """A Compositional Pattern Producing Network"""

    # input_node_names = ['x', 'y', 'z', 'd', 'b']
    # activation_functions = [np.sin, np.abs, neg_abs, np.square, neg_square, sqrt_abs, neg_sqrt_abs]
    activation_functions = [np.sin, np.abs, neg_abs, np.square, neg_square, sqrt_abs, neg_sqrt_abs, gaussian_e, sin_square_x_plus_x, triangle_wave, sawtooth_wave, square_wave, relu, elu, tanh, swish]

    def __init__(self, args, output_node_names, input_node_names):
        Network.__init__(self, output_node_names, input_node_names)
        self.set_minimal_graph()
        self.num_random_node_adds=5
        self.num_random_node_removals=0
        self.num_random_link_adds=10
        self.num_random_link_removals=5
        self.num_random_activation_functions=100
        self.num_random_weight_changes=100
        # get the defined params for the cppn structure
        if args is not None:
            self.num_random_node_adds=args.num_random_node_adds
            self.num_random_node_removals=args.num_random_node_removals
            self.num_random_link_adds=args.num_random_link_adds
            self.num_random_link_removals=args.num_random_link_removals
            self.num_random_activation_functions=args.num_random_activation_functions
            self.num_random_weight_changes=args.num_random_weight_changes
            # randomize the nodes and edges from a normal distribution
            if args.cppn_sample_from_normal_dist:
                scale=2
                self.num_random_node_adds= int(np.clip((np.random.normal(scale=scale)+args.num_random_node_adds),a_min=args.num_random_node_removals+1, a_max=None))
                scale=4
                self.num_random_link_adds= int(np.clip(np.random.normal(scale=scale)+args.num_random_link_adds,a_min=args.num_random_link_removals+2, a_max=None))

            if args.optimizer_type == "Random":
                self.num_random_node_adds= np.random.randint(args.num_random_node_adds+1, args.num_random_node_adds*5)
                self.num_random_node_removals=np.random.randint(0, self.num_random_node_adds-1)
                self.num_random_link_adds=np.random.randint(args.num_random_link_adds+1, args.num_random_link_adds*5)
                self.num_random_link_removals=np.random.randint(0, int(self.num_random_link_adds/4)-1)
                self.num_random_activation_functions=np.random.randint(args.num_random_activation_functions+1, args.num_random_activation_functions*5)
                self.num_random_weight_changes=np.random.randint(args.num_random_weight_changes+1, args.num_random_weight_changes*5)


        self.mutate(self.num_random_node_adds, self.num_random_node_removals, self.num_random_link_adds,
               self.num_random_link_removals, self.num_random_activation_functions, self.num_random_weight_changes)


    def set_minimal_graph(self):
        """Create a simple graph with each input attached to each output"""
        for name in self.input_node_names:
            self.graph.add_node(name, type="input", function=None)

        for name in self.output_node_names:
            self.graph.add_node(name, type="output", function=sigmoid)

        for input_node in nx.nodes(self.graph):
            if self.graph.nodes[input_node]["type"] == "input":
                for output_node in nx.nodes(self.graph):
                    if self.graph.nodes[output_node]["type"] == "output":
                        self.graph.add_edge(input_node, output_node, weight=0.0)

    def set_input_node_states(self, orig_size_xyz, segment_size_xyz):
        input_x = np.zeros(orig_size_xyz)
        input_y = np.zeros(orig_size_xyz)
        input_z = np.zeros(orig_size_xyz)

        segment_x = np.zeros(orig_size_xyz)
        segment_y = np.zeros(orig_size_xyz)
        segment_z = np.zeros(orig_size_xyz)

        for x in range(orig_size_xyz[0]):
            for y in range(orig_size_xyz[1]):
                for z in range(orig_size_xyz[2]):
                    input_x[x, y, z] = x
                    input_y[x, y, z] = y
                    input_z[x, y, z] = z

                    segment_x[x, y, z] = x%segment_size_xyz[0]
                    segment_y[x, y, z] = y%segment_size_xyz[1]
                    segment_z[x, y, z] = z%segment_size_xyz[2]

        input_x = normalize(input_x)
        input_y = normalize(input_y)
        input_z = normalize(input_z)

        segment_x = normalize(segment_x)
        segment_y = normalize(segment_y)
        segment_z = normalize(segment_z)


        # TODO: do not forget to change here

        # input_d = normalize(np.power(np.power(input_x, 2) + np.power(input_y, 2) + np.power(input_z, 2), 0.5))
        input_d = normalize(np.power(np.power(segment_x, 2) + np.power(segment_y, 2) + np.power(segment_z, 2), 0.5))

        # input_d = normalize(np.power(np.power(input_x, 2), 0.5))
        input_b = np.ones(orig_size_xyz)  # TODO: check input_d (above): changed pow -> np.power without testing

        for name in self.graph.nodes():
            if name == "x":
                self.graph.nodes[name]["state"] = input_x
                self.graph.nodes[name]["evaluated"] = True
            if name == "y":
                self.graph.nodes[name]["state"] = input_y
                self.graph.nodes[name]["evaluated"] = True
            if name == "z":
                self.graph.nodes[name]["state"] = input_z
                self.graph.nodes[name]["evaluated"] = True
            if name == "d":
                self.graph.nodes[name]["state"] = input_d
                self.graph.nodes[name]["evaluated"] = True
            if name == "b":
                self.graph.nodes[name]["state"] = input_b
                self.graph.nodes[name]["evaluated"] = True

    def mutate(self, num_random_node_adds=5, num_random_node_removals=0, num_random_link_adds=10,
               num_random_link_removals=5, num_random_activation_functions=100, num_random_weight_changes=100):

        variation_degree = None
        variation_type = None

        for _ in range(num_random_node_adds):
            variation_degree = self.add_node()
            variation_type = "add_node"

        for _ in range(num_random_node_removals):
            variation_degree = self.remove_node()
            variation_type = "remove_node"

        for _ in range(num_random_link_adds):
            variation_degree = self.add_link()
            variation_type = "add_link"

        for _ in range(num_random_link_removals):
            variation_degree = self.remove_link()
            variation_type = "remove_link"

        for _ in range(num_random_activation_functions):
            variation_degree = self.mutate_function()
            variation_type = "mutate_function"

        for _ in range(num_random_weight_changes):
            variation_degree = self.mutate_weight()
            variation_type = "mutate_weight"

        self.prune_network()
        return variation_type, variation_degree

    ###############################################
    #   Mutation functions
    ###############################################

    def add_node(self):
        # choose two random nodes (between which a link could exist)
        if len(self.graph.edges()) == 0:
            return "NoEdges"
        this_edge = random.choice(list(self.graph.edges()))
        node1 = this_edge[0]
        node2 = this_edge[1]

        # create a new node hanging from the previous output node
        new_node_index = self.get_max_hidden_node_index()
        self.graph.add_node(new_node_index, type="hidden", function=random.choice(self.activation_functions))
        # random activation function here to solve the problem with admissible mutations in the first generations
        self.graph.add_edge(new_node_index, node2, weight=1.0)

        # if this edge already existed here, remove it
        # but use it's weight to minimize disruption when connecting to the previous input node
        if (node1, node2) in nx.edges(self.graph):
            weight = self.graph.edges[node1, node2]["weight"]
            self.graph.remove_edge(node1, node2)
            self.graph.add_edge(node1, new_node_index, weight=weight)
        else:
            self.graph.add_edge(node1, new_node_index, weight=1.0)
            # weight 0.0 would minimize disruption of new edge
            # but weight 1.0 should help in finding admissible mutations in the first generations
        return ""

    def remove_node(self):
        hidden_nodes = list(set(self.graph.nodes()) - set(self.input_node_names) - set(self.output_node_names))
        if len(hidden_nodes) == 0:
            return "NoHiddenNodes"
        this_node = random.choice(hidden_nodes)

        # if there are edge paths going through this node, keep them connected to minimize disruption
        incoming_edges = self.graph.in_edges(nbunch=[this_node])
        outgoing_edges = self.graph.out_edges(nbunch=[this_node])

        for incoming_edge in incoming_edges:
            for outgoing_edge in outgoing_edges:
                w = self.graph.edges[incoming_edge[0], this_node]["weight"] * \
                    self.graph.edges[this_node, outgoing_edge[1]]["weight"]
                self.graph.add_edge(incoming_edge[0], outgoing_edge[1], weight=w)

        self.graph.remove_node(this_node)
        return ""

    def add_link(self):
        done = False
        attempt = 0
        while not done:
            done = True

            # choose two random nodes (between which a link could exist, *but doesn't*)
            node1 = random.choice(tuple(self.graph.nodes()))
            node2 = random.choice(tuple(self.graph.nodes()))
            while (not self.new_edge_is_valid(node1, node2)) and attempt < 999:
                node1 = random.choice(tuple(self.graph.nodes()))
                node2 = random.choice(tuple(self.graph.nodes()))
                attempt += 1
            if attempt > 999:  # no valid edges to add found in 1000 attempts
                done = True

            # create a link between them
            if random.random() > 0.5:
                self.graph.add_edge(node1, node2, weight=0.1)
            else:
                self.graph.add_edge(node1, node2, weight=-0.1)

            # If the link creates a cyclic graph, erase it and try again
            if self.has_cycles():
                self.graph.remove_edge(node1, node2)
                done = False
                attempt += 1
            if attempt > 999:
                done = True
        return ""

    def remove_link(self):
        if len(self.graph.edges()) == 0:
            return "NoEdges"
        this_link = random.choice(list(self.graph.edges()))
        self.graph.remove_edge(this_link[0], this_link[1])
        return ""

    def mutate_function(self):
        this_node = random.choice(tuple(self.graph.nodes()))
        while this_node in self.input_node_names:
            this_node = random.choice(tuple(self.graph.nodes()))
        old_function = self.graph.nodes[this_node]["function"]
        while self.graph.nodes[this_node]["function"] == old_function:
            self.graph.nodes[this_node]["function"] = random.choice(self.activation_functions)
        return old_function.__name__ + "-to-" + self.graph.nodes[this_node]["function"].__name__

    def mutate_weight(self, mutation_std=0.5):
        if len(self.graph.edges()) == 0:
            return "NoEdges"
        this_edge = random.choice(list(self.graph.edges()))
        node1 = this_edge[0]
        node2 = this_edge[1]
        old_weight = self.graph[node1][node2]["weight"]
        new_weight = old_weight
        while old_weight == new_weight:
            new_weight = random.gauss(old_weight, mutation_std)
            new_weight = max(-1.0, min(new_weight, 1.0))
        self.graph[node1][node2]["weight"] = new_weight
        return float(new_weight - old_weight)

    ###############################################
    #   Helper functions for mutation
    ###############################################

    def prune_network(self):
        """Remove erroneous nodes and edges post mutation."""
        done = False
        while not done:
            done = True
            for node in list(self.graph.nodes()):
                if len(self.graph.in_edges(nbunch=[node])) == 0 and \
                                node not in self.input_node_names and \
                                node not in self.output_node_names:
                    self.graph.remove_node(node)
                    done = False

            for node in list(self.graph.nodes()):
                if len(self.graph.out_edges(nbunch=[node])) == 0 and \
                                node not in self.input_node_names and \
                                node not in self.output_node_names:
                    self.graph.remove_node(node)
                    done = False

    def has_cycles(self):
        """Return True if the graph contains simple cycles (elementary circuits).

        A simple cycle is a closed path where no node appears twice, except that the first and last node are the same.

        """
        return sum(1 for _ in nx.simple_cycles(self.graph)) != 0

    def get_max_hidden_node_index(self):
        max_index = 0
        for input_node in nx.nodes(self.graph):
            if self.graph.nodes[input_node]["type"] == "hidden" and int(input_node) >= max_index:
                max_index = input_node + 1
        return max_index

    def new_edge_is_valid(self, node1, node2):
        if node1 == node2:
            return False
        if self.graph.nodes[node1]['type'] == "output":
            return False
        if self.graph.nodes[node2]['type'] == "input":
            return False
        if (node2, node1) in nx.edges(self.graph):
            return False
        if (node1, node2) in nx.edges(self.graph):
            return False
        return True


class DirectEncoding(Network):
    def __init__(self, output_node_name, orig_size_xyz, lower_bound=-1, upper_bound=1, func=None, symmetric=False,
                 p=None, scale=None, start_val=None, mutate_start_val=False):

        Network.__init__(self, [output_node_name], [])

        self.direct_encoding = True
        self.allow_neutral_mutations = False
        self.size = orig_size_xyz
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        if p is None:
            p = 1/np.product(self.size, dtype='f')
        self.p = p
        self.scale = scale
        self.func = func
        self.symmetric = symmetric
        self.start_value = start_val

        if start_val is None:
            self.values = np.random.uniform(lower_bound, upper_bound, size=orig_size_xyz)
        else:
            self.values = np.ones(shape=orig_size_xyz) * start_val
            if mutate_start_val:
                self.mutate()

        self.enforce_symmetry()

        if self.func is not None:
            self.values = self.func(self.values)

        self.values = np.clip(self.values, self.lower_bound, self.upper_bound)

    # @property
    # def values(self):
    #     return self._values
    #
    # @values.setter
    # def values(self, values):
    #     if self.func is None:
    #         self._values = values
    #     else:
    #         self._values = self.func(values)

    def set_input_node_states(self, *args, **kwargs):
        pass

    def mutate(self, rate=None):
        if rate is None:
            rate = self.p

        scale = self.scale
        if self.scale is None:
            scale = np.clip(self.values**0.5, self.start_value**0.5, self.upper_bound)
            # right not the only time this occurs is for meta mutations
            # assuming values are less than 1, ow this should be 1/val

        tmp = self.values
        while np.array_equal(tmp, self.values):
            selection = np.random.random(self.size) < rate
            change = np.random.normal(scale=scale, size=self.size)
            self.values[selection] += change[selection]
            self.values = np.clip(self.values, self.lower_bound, self.upper_bound)
            self.enforce_symmetry()
            if self.func is not None:
                self.values = self.func(self.values)

        return "gaussian", self.scale

    def enforce_symmetry(self):
        if self.symmetric:
            reversed_array = self.values[::-1, :, :]
            self.values[:int(self.size[0]/2.0), :, :] = reversed_array[:int(self.size[0]/2.0), :, :]
