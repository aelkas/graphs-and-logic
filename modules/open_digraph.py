import random
import os
import sys
sys.path[0] = os.path.abspath(os.path.join(sys.path[0], '..'))
from modules.open_digraph_paths_distance_mx import open_digraph_paths_distance
from modules.open_digraph_composition_mx import open_digraph_composition
from modules.node import *
from modules.matrix_operations import *




class open_digraph(open_digraph_paths_distance,open_digraph_composition): # for open directed graph
    
    
    ###Constructor 
    
    def __init__(self, inputs, outputs, nodes):
        
        """
        inputs: int list; the ids of the input nodes
        outputs: int list; the ids of the output nodes
        nodes: node iter;
        """
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = {node.id:node for node in nodes} 
        self.assert_is_well_formed()

    def __eq__(self, g):
        if len(self.inputs) != len(g.get_inputs_ids()):
            return False
        if len(self.outputs) != len(g.get_outputs_ids()):
            return False
        for i in self.inputs:
            if i not in g.get_inputs_ids():
                return False
        for j in self.outputs:
            if j not in g.get_outputs_ids():
                return False
        # Check if nodes are equal
        if len(self.nodes) != len(g.get_id_node_map()):
            return False
        for node in self.nodes.values():
            if node not in g.get_nodes():
                return False
        return True
    def __ne__(self,g):
        return not self.__eq__(g)


    @classmethod
    def empty(cls):
        return open_digraph([],[],[])


    ### Getters and Setters
    def get_inputs_ids(self):
        return self.inputs

    def get_outputs_ids(self):
        return self.outputs

    def get_id_node_map(self):
        return self.nodes

    def get_nodes(self):
        return self.nodes.values()

    def get_node_ids(self):
        return self.nodes.keys()

    def get_node_by_id(self,id):
        return self.nodes[id]
    
    def get_nodes_by_ids(self , ids):
        return [self.nodes[id] for id in ids]
    
    def set_inputs(self , inputs):
        self.inputs = inputs
    
    def set_outputs(self , outputs):
        self.outputs = outputs

    def add_input_id(self , id):
        """
            Adds id to the list of inputs of the graph
        """
        assert id in self.nodes.keys() , "Input Node doesn't exist in graph"
        self.inputs.append(id)

    def add_output_id(self , id):
        """
            Adds id to the list of outputs of the graph
        """
        assert id in self.nodes.keys(), "Ouput Node doesn't exist in graph"
        self.outputs.append(id)
    
    def new_id(self):
        """
            Generates a new unique id usable in the graph
        """
        id = 0
        while id in self.get_node_ids():
            id+=1
        return id
    
    
    
    ###Adding and removing edges/nodes
    
    def add_edge(self , src , tgt , m=1):
        """
            Adds an edge from a source node to a target node (directed edge) with a certain multiplicity
            
            Parameters:
            -----------
            
            src (int) : id of the source node
            tgt (int) : id of the target node
            m (int) default=1 : the multiplicity of the edge
            
            Output:(inplace)
            -------
            
            the graph with the added edge from the source node to the target node
        """
        assert src in self.nodes.keys()
        assert tgt in self.nodes.keys()
        
        n1 = self.get_node_by_id(tgt)
        n2 = self.get_node_by_id(src)
        n1.add_parent_id(src,m)
        n2.add_child_id(tgt,m)
    
    
    def add_edges(self , edges , m_list):
        """
            Adds several edges with a given multiplicty for each edge
            
            Parameters:
            -----------
            
            edges (list (int,int)) : a list of tuples containing the ids of (src, tgt) between which the edge will be added
            m_list (list int) : the corresponding multiplicity of each edge 
            
            Output:(inplace)
            -------
            
            the graph with the added edges 
        """
        n = len(edges)
        assert (m_list == [] or n == len(m_list))
        for i in range(n):
            if m_list == []:
                self.add_edge(edges[i][0] , edges[i][1])
            else:
                self.add_edge(edges[i][0] , edges[i][1], m=m_list[i])
                
    
    def add_node(self,label="",parents={},children={}):
        """
            Adds a node to the graph
            
            Parameters:
            ----------
            
            Optional:
            label (str) default = "": the label of the added node
            parents ({(int) : (node)}) : the map of all the node's parents
            children ({(int) : (node)}) : the map of all the node's children
            
            Output: (inplace)
            -------
            The graph with the node added to it
        """
        p_ids = list(parents.keys())
        c_ids = list(children.keys())
        r = p_ids + c_ids
        assert r==[] or all(elem in self.nodes.keys() for elem in r)
        new_ID= self.new_id()
        new_node = node(new_ID,label , {} , {})
        self.nodes[new_ID] = new_node
        
        
        #Adding the edges from parents and to children
        p = [(par , new_ID) for par in p_ids]
        c = [(new_ID, chi) for chi in c_ids]
        total=p+c
        mult = list(parents.values()) + list(children.values())
        self.add_edges(total,mult)
        return new_ID
    
    
    def remove_edge(self, src, tgt):
        """
            Removes an edge from a source node to a target node (directed edge) 
            
            Parameters:
            -----------
            
            src (int) : id of the source node
            tgt (int) : id of the target node
            
            Output:(inplace)
            -------
            
            the graph with the removed edge from the source node to the target node
        """
        s = self.get_node_by_id(src)
        t = self.get_node_by_id(tgt)
        
        s.remove_child_once(tgt)
        t.remove_parent_once(src)
    
    def remove_parallel_edges(self, src ,tgt):
        """
            Removes all edges from a source node to a target node (directed edges) 
            
            Parameters:
            -----------
            
            src (int) : id of the source node
            tgt (int) : id of the target node
            
            Output:(inplace)
            -------
            
            the graph with the removed edges from the source node to the target node
        """
        s = self.get_node_by_id(src)
        t = self.get_node_by_id(tgt)
        
        s.remove_child_id(tgt)
        t.remove_parent_id(src)
        
    def remove_node_by_id(self , id):
        """
            Removes a node from the graph given its id
            
            Parameters:
            -----------
            
            id (int) : the id of the node to remove
            
            Output: (inplace)
            -------
            
            The graph with the removed node and updated edges
        """
        all_edges =  [(p,id) for p in self.get_node_by_id(id).get_parents()] + [(id,p) for p in self.get_node_by_id(id).get_children()]
        
        for pair in all_edges:
            self.remove_parallel_edges(pair[0] , pair[1])
        
        del self.nodes[id]
        
    def remove_edges(self , edges):
        """
            Removes a set of edges from pairs of source nodes to target nodes (directed edges) 
            
            Parameters:
            -----------
            
            edges (list (int,int)) : a list of tuples containing the ids of (src, tgt) between which the edge will be removed
            
            Output:(inplace)
            -------
            
            the graph with the removed edges from the source nodes to the target nodes
        """
        for p in edges:
            self.remove_edge(p[0] , p[1])
    
    def remove_several_parallel_edges(self ,edges):
        """
            Removes all edges from pairs of source nodes to target nodes (directed edges) 
            
            Parameters:
            -----------
            
            edges (list (int,int)) : a list of tuples containing the ids of (src, tgt) between which the edges will be removed
            
            Output:(inplace)
            -------
            
            the graph with the removed edges from the source nodes to the target nodes
        """
        for p in edges:
            self.remove_parallel_edges(p[0] , p[1])
            
    def remove_nodes_by_id(self, ids):
        """
            Removes nodes from the graph given their ids
            
            Parameters:
            -----------
            
            ids (list (int)) : the ids of the nodes to remove
            
            Output: (inplace)
            -------
            
            The graph with the removed nodes and updated edges
        """
        for id in ids:
            self.remove_node_by_id(id)


    ### integrity checks
    
    def is_well_formed(self):
        """
            Checks if the graph is well formed 
        """
        
        #checks if all input_ids exist in the graph and if they have only one child
        for i in self.inputs:
            if i not in self.nodes.keys():
                return False          
            if self.get_node_by_id(i).get_parents() != {}:
                return False
            children = list(self.get_node_by_id(i).get_children().values())
            if len(children) !=1 or children[0] != 1:
                return False
        
        #checks if all out_ids exist in the graph and if they have only one parent
        for o in self.outputs:
            if o not in self.nodes.keys():
                return False          
            if self.get_node_by_id(o).get_children() != {}:
                return False
            parents = list(self.get_node_by_id(o).get_parents().values())
            if len(parents) !=1 or parents[0] != 1:
                return False
            
        #checks if every child has the node in question as his parent and vice-versa
        for key , node in self.nodes.items():
            if key != node.get_id():
                return False

            parents = self.get_nodes_by_ids(node.get_parents().keys())
            for p in parents:
                if p.get_children()[key] != node.get_parents()[p.get_id()]:
                    return False
            
            children = self.get_nodes_by_ids(node.get_children().keys())
            for c in children:
                if c.get_parents()[key] != node.get_children()[c.get_id()]:
                    return False
        return True
    
    def assert_is_well_formed(self):
        assert self.is_well_formed() , "The graph is not well formed."
    
    
    def add_input_node(self , child_id):
        """
            Creats an input node that has the node with id child_id as child and adds it to the graph
        """
        assert child_id in self.nodes.keys() , "Node connected to input doesn't exist."
        new_inp = self.add_node(children={child_id: 1})
        self.add_input_id(new_inp)
        return new_inp
    
    def add_output_node(self , par_id):
        """
            Creats an output node that has the node with id parent_id as parent and adds it to the graph
        """
        assert par_id in self.nodes.keys() , "Node connected to output doesn't exist."
        
        new_out = self.add_node(parents={par_id: 1})
        self.add_output_id(new_out)
        return new_out
    
    
    def copy(self):
        """
            Returns a copy of the graph is independant in memory
        """
        new_nodes =[node.copy() for node in self.nodes.values()]
        new_inputs = self.inputs.copy()
        new_outputs = self.outputs.copy()
        return open_digraph(new_inputs, new_outputs , new_nodes)

    def __str__(self):
        s =  f"*********Graph*********\nInputs : {self.inputs}\nOutputs : {self.outputs}\nNodes :\n "
        for n in self.nodes.values():
            s += " \n-------\n"+n.__str__()
        return s
    def __repr__(self):
            return repr(self.__str__)
    
    #3#
    def id_map(self):
        """
            Returns a map from each node_id to a unique integer in [[0,n[[
        """
        d = {}
        
        for k,key in enumerate(self.nodes.keys()):
            d[key] = k
            
        return d
    
    
    #3#
    def adjacency_matrix(self):
        """
            Returns the adjacency matrix associated to the graph
        """
        mat = [[0 for _ in self.nodes] for _ in self.nodes]
        node_ids = self.nodes
        
        for i in node_ids:
            node_i = self.nodes[i]
            children_ids = node_i.get_children()
            
            for j in node_ids:
                node_j = self.nodes[j]
                if node_j.get_id() in children_ids:
                    mat[i][j] = children_ids[node_j.get_id()]      
        return mat
    
    #3#
    @classmethod
    def graph_from_adjacency_matrix(cls,mat , inp = 0 , out = 0,number_generator = 0.5):
        """ 
        Generate a graph from an adjacency matrix with the number input and output nodes.

        Parameters:
        -----------
        mat (list list): A square representing the adjacency matrix of the graph.
        inp (int): Number of input nodes. Default is 0.
        out (int): Number of output nodes. Default is 0.
        number_generator (function): A function that generates random numbers. 
                                    Default is a function generating numbers from a beta distribution.

        Returns:
        --------
        open.diGraph: A directed graph generated from the provided adjacency matrix,
                        with optional input and output nodes.
        """
        assert len(mat[0])==len(mat) , "matrix dimensions not n x n"
        graph = cls.empty()
        nodelistIDS= {i:node(i,"",{},{}) for i in range(len(mat[0]))}
        graph.nodes= nodelistIDS
        N = range(len(mat[0]))
        for i in N:
            for j in N:
                if mat[i][j]!=0:
                    graph.add_edge(i,j,mat[i][j])
        
        ids = list(graph.get_node_ids()).copy()
        for i in range(inp):
            choice = random.choice(ids)
            graph.add_input_id(choice)
            ids.remove(choice)
            
        for i in range(out):
            choice = random.choice(ids)
            graph.add_output_id(choice)
            ids.remove(choice)
        return graph

    #3#
    @classmethod
    def random(cls,n, bound=1, inputs=0, outputs=0, form="free", number_generator=0.5): 
        """
            Returns a graph derived from a randomly generated adjacency matrix
            
            Parameters:
            -----------
            n (int) : size of the adjacency matrix (i.e number of nodes)
            bound (int) : max multiplicity of edges between two nodes
            
            Optional:
            inputs (int) : number of input nodes in the graph
            outputs (int) : number of output nodes in the graph
            form (str) : string specifing constraints on the graph (acyclicity , orientation...)
            number_generator (function): distribution function that generates a seed in [0,1] , must not use an argument

            Rerturn:
            --------
                The graph associated to the adjacency matrix
        """
        if form=="free":
            return cls.graph_from_adjacency_matrix(random_int_matrix(n,bound,False), inp = inputs , out = outputs, number_generator=number_generator) 
        elif form=="DAG":
            return cls.graph_from_adjacency_matrix(random_dag_int_matrix(n,bound), inp = inputs , out = outputs, number_generator=number_generator)
        elif form=="oriented": 
            return cls.graph_from_adjacency_matrix(random_oriented_int_matrix(n,bound,False), inp = inputs , out = outputs, number_generator=number_generator)
        elif form=="loop-free": 
            return cls.graph_from_adjacency_matrix(random_int_matrix(n,bound), inp = inputs , out = outputs, number_generator=number_generator)
        elif form=="undirected":
            return cls.graph_from_adjacency_matrix(random_symetric_int_matrix(n,bound), inp = inputs , out = outputs, number_generator=number_generator)
        elif form=="loop-free undirected":
            return  cls.graph_from_adjacency_matrix(random_symetric_int_matrix(n,bound), inp = inputs , out = outputs, number_generator=number_generator)
        elif form=="loop-free oriented": 
            return cls.graph_from_adjacency_matrix(random_oriented_int_matrix(n,bound), inp = inputs , out = outputs, number_generator=number_generator)
        else : return [[]]

    def save_as_dot_file(self, path, verbose = True):
        """
            Saves the graph in the specified path using the .dot format

            Parameters:
            -----------
            path (str) : the path of the file in which the graph will be saved
            
            
            Optional:
            verbose (bool) default=True : saves the ids of each node as an attribute for debugging puposes

            Return:
            -------
                .dot file representing the graph
        """
        assert path[-4:] == ".dot", "Not the right extension"
        s = "digraph G {\n    rankdir=TB;\n\n"

        # Taking care of inputs
        s += "    {\n        rank = same;\n"
        for iden in self.get_inputs_ids():
            if iden in self.get_node_ids():
                node = self.get_node_by_id(iden)
                s += f'        v{iden} [label="{node.get_label()}'
                if verbose:
                    s+= f'\id={iden}'
                s+='", shape=none, input=True, output=False, color=green];\n'
        s += "    }\n\n"

        # Nodes
        for iden, node in self.nodes.items():
            if iden in self.get_inputs_ids() or iden in self.get_outputs_ids():
                continue
            if node.get_label()=="":
                s += f'    v{iden} [label="'
                if verbose:
                    s+= f'{iden}'
                s+= f'", shape=circle, width=0.4, height=0.4, fixedsize=true, input=False, output=False];\n'
            else:
                s += f'    v{iden} [label="{node.get_label()}'
                if verbose:
                    s+= f'\nid={iden}'
                s+=f'", input=False, output=False];\n'
                

        # Outputs
        s += "\n    {\n        rank = same;\n"
        for iden in self.get_outputs_ids():
            if iden in self.get_node_ids():
                node = self.get_node_by_id(iden)
                s += f'        v{iden} [label="{node.get_label()}'
                if verbose:
                    s+= f'\nid={iden}'
                s+='", shape=none, input=False, output=True, color=red];\n'
        s += "    }\n"

        # Adding edges
        for iden, node in self.get_id_node_map().items():
            for child in node.get_children():
                s += f"    v{iden} -> v{child}"
                if iden in self.get_inputs_ids():
                    s += "[color=green]"
                elif child in self.get_outputs_ids():
                    s += "[color=red]"
                s += ";\n"
            

        s += "}\n"

        with open(path, "w") as f:
            f.write(s)



    def display_graph(self , name="display" ,verbose=False):
        """
            Displays the graph using the .dot format after converting it to pdf
            Both the .dot and pdf file will be stored in the current directory
            
            Parameters:
            -----------
            
            Optional:
            verbose (bool) default=True : displays the ids of each node as an attribute for debugging puposes

            Output:(inplace)
            -------
                Display of the graph's representation in pdf
        """
        self.save_as_dot_file(f"{name}.dot",verbose = verbose)
        os.system(f"dot -Tpdf {name}.dot -o {name}.pdf")
        if sys.platform.startswith('win'):
            os.system(f"icacls {name}  /grant %USERNAME%:F")
        elif sys.platform.startswith('linux'):
            os.system(f"chmod 777 {name}")
        
        os.system(f"explorer.exe {name}")


    @classmethod
    def from_dot_file(cls , path):
        """
            Returns the graph associated to the .dot file located in the specified path 
            
            Parameters:
            -----------
            path (str) : the path of the file from which the graph will be read

            Return:
            -------
                .dot file representing the graph
            
        """
        assert path[-4:] == ".dot" , "Not the right extension"
        f = open(path, "r")
        text  = f.read()
        g = open_digraph([], [] , {})
        st = text.index("{")
        end = text.index("}")
        assert st != -1 and end != -1 , "Invalid File , no {}"
        text = text[st+1 : end]
        elements = text.split(";")
        nodes_dict = {}  # dict from nodes names to their ids in the graph
        for e in elements:
            if "[" in e: #attributs handling
                bracketstart = e.index("[")
                bracketend = e.index("]")
                if bracketstart != -1:
                    node_name = e[:bracketstart].strip()
                    att_val_liste = [(attribute.split("=")[0] ,attribute.split("=")[1].replace("\"" , "") ) for attribute in e[bracketstart+1 : bracketend].split(",")]
                    for pair in att_val_liste:
                        lab = ""
                        inp = out = False
                        if pair[0] == "label":
                            lab = pair[1]
                        elif pair[0] == "input":
                            inp = True
                        elif  pair[0] == "output":
                            out = True
                        assert not (inp and out) , "The node is both an input and output node"
                        nid = g.add_node(label= lab)
                        if inp:
                            g.add_input_id(nid)
                        if out:
                            g.add_input_id(nid)
                        nodes_dict[node_name] = nid
            elif "->" in e:  # edges handling
                chain = e.strip().split(" -> ")
                parent = chain[0]
                children = chain[1:]
                if parent not in nodes_dict.keys():
                    parent_id = g.add_node()
                    nodes_dict[parent] = parent_id
                for child in children:
                    if child not in nodes_dict.keys():
                        child_id = g.add_node()
                        nodes_dict[child] = child_id
                    g.add_edge(nodes_dict[parent],nodes_dict[child])
        return g

    def is_acyclic(self):
        """
            Checks if the graph is acyclic using the Depth-First-Search algorithm
            
            Returns:
            --------
            True if the graph is acyclic, false otherwise
        """
        visited = set()
        stack = set()

        def dfs(node):
            if node.get_id() in stack:   #i.e if the node was encounterd twice before visiting all its children 
                return False
            if node.get_id() in visited:
                return True

            visited.add(node.get_id())
            stack.add(node.get_id())

            children = node.get_children()
            for child_id in children:   # explore children
                if not dfs(self.nodes[child_id]):
                    return False  # Cycle detected

            stack.remove(node.get_id())
            return True

        for id in self.nodes:
            if id not in visited:
                if not dfs(self.nodes[id]):
                    return False  # Cycle detected

        return True  # No cycle found

    #6#
    @classmethod
    def identity(cls , n):
        """
            Returns the identity graph for n entries (n inputs , n outputs)
        """
        g = cls.empty()
        for i in range(n):
            inp = g.add_node()
            out = g.add_node()
            g.add_edge(inp, out)
            g.add_input_id(inp)
            g.add_output_id(out)
        return g
    
    #6#
    def component_list(self):
        """
            Returns the number of connected components as well as a map from each node to the connected component they belong to
            
            Returns:
            --------
            A tuple (int , dict) : the number of connecter components / a dictionary with all the nodes as ids and their respective connected component
        """
        nb , dict_ = self.connected_components()
        componentMat = [[] for i in range(nb)]
        for i in dict_ :
            componentMat[dict_[i]].append(self.nodes[i])    # one row for every connected component
        
        
        for i in range(nb):
            # updating input and output lists for every component
            component_input = [inp for inp in self.get_inputs_ids() if dict_[inp]==i]
            component_output = [out for out in self.get_outputs_ids() if dict_[out]==i]
            componentMat[i] = open_digraph(component_input , component_output , componentMat[i])
        return componentMat
    
    
    def merge_nodes(self,node_id, other_id):
        """
            Merges two nodes into one, the node that is left becomes parent of both input nodes' children and gets the label of node_id
            
            Parameters:
            -----------
            node_id (int): the id in self of the node that will remain
            other_id (int): the id of the node that will be merged
        """
        if node_id != other_id:
            node = self.get_node_by_id(node_id)
            other = self.get_node_by_id(other_id)
            for p,mult in other.get_parents().items():
                if p != node_id:                 #avoids reflexive edges if node is parent of other
                    self.add_edge(p,node_id,m=mult)
            for c,mult in other.get_children().items():
                if c != node_id:                 #avoids reflexive edges if node is child of other
                    self.add_edge(node_id,c,m=mult)
            self.remove_node_by_id(other_id)