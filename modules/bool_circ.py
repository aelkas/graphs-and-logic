import os
import sys
sys.path[0] = os.path.abspath(os.path.join(sys.path[0], '..'))
import random
from modules.node import *
from modules.bool_circ_gates_mx import bool_circ_gates_mx
from modules.open_digraph import open_digraph

class bool_circ(bool_circ_gates_mx,open_digraph):
    
    ###Constructor
    
    def __init__(self, g):
        g.assert_is_well_formed()
        super().__init__(g.get_inputs_ids().copy(), g.get_outputs_ids().copy(), [])
        self.nodes = g.get_id_node_map().copy()
        assert self.is_well_formed()
    
    
    def is_well_formed(self):
        """
            Checks if the boolean circuit is well-formed
        """
        if super().is_acyclic():
            for key,node in self.nodes.items():
                if node.get_label() not in "&|^10~" and node.get_label() != "":
                    return False
                elif (node.get_label() == "" or node.get_label() == "1" or node.get_label() == "0") and node.indegree() > 1 : 
                    return False
                elif (node.get_label() == "&" or node.get_label() == "^" or node.get_label() == "|" or node.get_label() == "1" or node.get_label() == "0") and node.outdegree() > 1:
                    return False
                elif node.get_label() == "~" and (node.outdegree() != 1 or node.indegree()!= 1):
                    return False
                
                
            return True
        return False
    
    def insert_node(self, boolean_circ_node,parents,children):
        """
            Adds a node to the graph
            
            Parameters:
            ----------
            
            boolean_circ_node (node) : a sub-class of node 
            
            Output: (inplace)
            -------
            The graph with the node added to it
        """
        p_ids = list(parents.keys())
        c_ids = list(children.keys())
        r = p_ids + c_ids
        assert r==[] or all(elem in self.nodes.keys() for elem in r)
        self.nodes[boolean_circ_node.get_id()] = boolean_circ_node
        
        
        #Adding the edges from parents and to children
        p = [(par , boolean_circ_node.get_id()) for par in p_ids]
        c = [(boolean_circ_node.get_id(), chi) for chi in c_ids]
        total=p+c
        mult = list(parents.values()) + list(children.values())
        self.add_edges(total,[])

    
    @classmethod   
    def convert_to_binary_string(cls, acc , size=8):
        bin_string = bin(acc)[2:]
        if len(bin_string) <= size:
            bin_string = (size-len(bin_string))*"0" + bin_string   #padding
        else:
            bin_string = bin_string[-1:-size-1:-1]  #bufferOverflow
        return bin_string
    
    def add_copy_node(self,parents={},children={},new_ID = None):
        if new_ID == None:
            new_ID = self.new_id()
        self.insert_node(copy_node(new_ID ,{},{}),parents,children)
        return new_ID
    
    def add_and_node(self,parents={},children={},new_ID = None):
        if new_ID == None:
            new_ID = self.new_id()
        self.insert_node(and_node(new_ID,{}, {}),parents,children)
        return new_ID
    
    def add_or_node(self,parents={},children={},new_ID = None):
        if new_ID == None:
            new_ID = self.new_id()
        self.insert_node(or_node(new_ID,{},{}),parents,children)
        return new_ID
    
    def add_not_node(self,parents={},children={},new_ID = None):
        if new_ID == None:
            new_ID = self.new_id()
        self.insert_node(not_node(new_ID,{} ,{}),parents,children)
        return new_ID
    
    def add_xor_node(self,parents={},children={},new_ID = None):
        if new_ID == None:
            new_ID = self.new_id()
        self.insert_node(xor_node(new_ID,{} , {}),parents,children)
        return new_ID
    
    def add_constant_node(self,inp,parents={},children={},new_ID = None):
        if new_ID == None:
            new_ID = self.new_id()
        self.insert_node(constant_node(new_ID,inp,{} , {}),parents,children)
        return new_ID
    
    
    def convert_node(self,node):
        """
        Converts node to the appropriate boolean circuit component according to its current label
        """
        label = node.get_label()
        if label == "":
            new_node = circuit_node.from_node(node)
        elif label == "&":
            new_node = circuit_node.from_node(node)
        elif label == "|":
            new_node = circuit_node.from_node(node)
        elif label == "^":
            new_node = circuit_node.from_node(node)
        elif label == "~":
            new_node = circuit_node.from_node(node)
        elif label == "1" or label == "0":
            new_node = circuit_node.from_node(node)
        
        parents = node.get_parents().copy()
        children = node.get_children().copy()
        self.remove_node_by_id(node.get_id())
        self.insert_node(new_node, parents, children)
    
    
    
    @classmethod
    def identity(cls,n):
        return cls.perturbe_bit(n,[-1])
    
    @classmethod
    def empty_bool_circ(cls):
        return cls(super().empty())

    @classmethod
    def parse_parentheses(cls,*args):
        """
            Creates the boolean circuit that can be associated to the series of propositional formulas given
            
            Parameters:
            -----------
            *args (str): any number of string representing a propositional formula
            
            Returns:
            --------
            
            A boolean circuit where each output is the output of one formula that is given and the list labels given to every variable
        """
        
        circuit =cls.empty_bool_circ()
        variables = {}
        for arg in args:
            first_node = circuit.add_node()
            circuit.add_output_node(first_node)
            current_node = circuit.get_node_by_id(first_node)
            s2 = ""
            for char in arg:
                if char == "(":
                    label = current_node.get_label()
                    if label == "":
                        current_node.set_label(label+s2)
                    parent_node = circuit.add_node()
                    circuit.add_edge(parent_node,current_node.get_id())
                    current_node = circuit.get_node_by_id(parent_node)
                    s2 = ""
                elif char == ")":
                    current_node.set_label(current_node.get_label()+s2)
                    if s2 != "" and s2 not in variables:
                        variables[s2] = current_node.get_id()
                    current_node = circuit.get_node_by_id(list(current_node.get_children().keys())[0])
                    s2 = ""
                else:
                    s2 += char
                    
                
        
        #Creates appropriate inputs above the copy nodes
        for id in variables.values():
            inp = circuit.add_input_node(id)
            
        
        
        nodes_dict = circuit.get_id_node_map().copy()
        for node_id,n in nodes_dict.items():
            if n.get_label() in variables:
                circuit.merge_nodes(variables[n.get_label()],node_id)
                circuit.get_node_by_id(variables[n.get_label()]).set_label("")
                

        
        assert circuit.is_well_formed() 
        return circuit,list(variables.keys())
    
    @classmethod
    def random_circ_bool(cls, n, nb_inputs,nb_outputs):
        '''
        creates a random circuit with n nodes, then adds nodes according to the 
        number of inputs and outputs wanted.

        Parameters:
        -----------
        n (int) : number of initial nodes
        nb_inputs (int) : number of inputs wanted
        nb_outputs (int) : number of outputs wanted

        Returns:
        --------
        random boolean circuit
        '''

        #step 1
        di = super().random(n,form="DAG")

        #step 2
        d = list(di.get_nodes()).copy()
        for nodess in d:
            if len(nodess.get_parents())==0:
                    inp_id = di.add_node("",{},{nodess.get_id():1})
                    di.add_input_id(inp_id)
            if len(nodess.get_children()) == 0:
                    out_id = di.add_node("",{nodess.get_id():1},{})
                    di.add_output_id(out_id)
        #step 2 bis
        not_out_nor_inp = [id for id in di.get_node_ids() if ((id not in di.get_inputs_ids()) and (id not in di.get_outputs_ids()))]
        random.shuffle(not_out_nor_inp)
        random.shuffle(di.get_inputs_ids())
        random.shuffle(di.get_outputs_ids())
        while(len(di.get_inputs_ids())!=nb_inputs):
            if(len(di.get_inputs_ids())< nb_inputs):
                id = not_out_nor_inp.pop(0)
                new_inp_id = di.add_node("",{},{id:1})
                not_out_nor_inp.append(id)
                di.add_input_id(new_inp_id)
            else:
                inp1 = di.get_inputs_ids().pop(0)
                inp2 = di.get_inputs_ids().pop(0)
                new_inp_id = di.add_node("",{},{inp1:1,inp2:1})
                di.add_input_id(new_inp_id)
                not_out_nor_inp.append(inp1)
                not_out_nor_inp.append(inp2)

        while(len(di.get_outputs_ids())!=nb_outputs):
                if(len(di.get_outputs_ids())< nb_outputs):
                    id = not_out_nor_inp.pop(0)
                    new_out_id = di.add_node("",{id:1},{})
                    not_out_nor_inp.append(id)
                    di.add_output_id(new_out_id)
                else:
                    out1 = di.get_outputs_ids().pop(0)
                    out2 = di.get_outputs_ids().pop(0)
                    new_out_id = di.add_node("",{out1:1,out2:1},{})
                    di.add_output_id(new_out_id)
                    not_out_nor_inp.append(out1)
                    not_out_nor_inp.append(out2)
        #step 3

        d = list(di.get_nodes()).copy()
        for nnodes in d:
            if len(nnodes.get_parents()) ==1 and len(nnodes.get_children()) == 1:
                nnodes.set_label("~")
            elif len(nnodes.get_parents()) >1 and len(nnodes.get_children()) == 1:
                nnodes.set_label(random.choice(["|","^","&"]))
            elif len(nnodes.get_parents()) >1 and len(nnodes.get_children()) > 1:
                bin_node_id = di.add_node(random.choice(["|","^","&"]),{},{})
                #cop_node_id = di.add_node("",{},{})
                for i in list(nnodes.get_parents().keys()).copy():
                    di.add_edge(i,bin_node_id)
                    di.remove_edge(i,nnodes.get_id())
                di.add_edge(bin_node_id,nnodes.get_id())

        circuit = cls(di)
        assert circuit.is_well_formed()
        return circuit
    
    @classmethod
    def create_registre(cls,acc ,size=8):
        bin_string = cls.convert_to_binary_string(acc,size=size)
        registre = cls.empty_bool_circ()
        for i in range(size):
            node_inp = registre.add_constant_node(bin_string[i],{},{})
            registre.add_input_id(node_inp)
            registre.add_output_node(node_inp)
        assert registre.is_well_formed()
        return registre
    
    
    
    ################## ENCODEUR AND DECODEUR ################

    @classmethod
    def encodeur_4bits(cls):
        """
        Creates a circuit that encodes 4bit signals using the Hamming Code
        
        Returns:
        --------
        A boolean circuit with 4 inputs and 7 outputs representing an encoder that uses the Hamming code
        """
        circuit = cls.empty_bool_circ()
        copies = [circuit.add_copy_node() for i in range(4)]
        xors = [circuit.add_xor_node() for i in range(3)]
        circuit.add_edges([(copies[0],xors[0]),(copies[0],xors[1]),(copies[1],xors[0]),
                        (copies[1],xors[2]),(copies[2],xors[1]),(copies[2],xors[2]),
                        (copies[3],xors[0]), (copies[3],xors[1]), (copies[3],xors[2])]
                        ,[])
        for i in range(4):
            circuit.add_input_node(copies[i])
        
        circuit.add_output_node(xors[0])
        circuit.add_output_node(xors[1])
        circuit.add_output_node(copies[0])
        circuit.add_output_node(xors[2])
        
        for i in range(1,4):
            circuit.add_output_node(copies[i])
        
        return circuit
    
    @classmethod
    def decodeur_7bits(cls):
        """
        Creates a circuit that decodes 7bit signals previously encoded using the Hamming code
        
        Returns:
        --------
        A boolean circuit with 7 inputs and 4 outputs representing 
        the original message before encoding
        """
        circuit = cls.empty_bool_circ()
        copies = [circuit.add_copy_node() for i in range(7)]
        xors = [circuit.add_xor_node() for i in range(7)]
        nots = [circuit.add_not_node() for i in range(3)]
        ands = [circuit.add_and_node() for i in range(4)]
        circuit.add_edges([(copies[0],xors[0]),(copies[0],xors[1]),(copies[1],xors[0]),(copies[1],xors[2]),(copies[2],xors[1]),(copies[2],xors[2]), (copies[3],xors[0]), (copies[3],xors[1]), (copies[3],xors[2])]+
                        [(xors[0],copies[4]),(xors[1],copies[5]),(xors[2],copies[6])]
                        +[(copies[4],ands[0]),(copies[4],ands[1]),(copies[4],ands[3])]
                        + [(copies[5],ands[0]),(copies[5],ands[2]),(copies[5],ands[3])]
                        + [(copies[6],ands[1]),(copies[6],ands[2]),(copies[6],ands[3])]
                        + [(copies[4],nots[2]),(copies[5],nots[1]),(copies[6],nots[0])]
                        + [(nots[i],ands[i]) for i in range(3)]
                        + [(copies[i],xors[i+3]) for i in range(4)]
                        + [(ands[i],xors[i+3]) for i in range(4)],[])
        for i in range(3,7):
            circuit.add_output_node(xors[i])
        circuit.add_input_node(xors[0])
        circuit.add_input_node(xors[1])
        circuit.add_input_node(copies[0])
        circuit.add_input_node(xors[2])
        for i in range(1,4):
            circuit.add_input_node(copies[i])
        
        return circuit    
    
    @classmethod
    def perturbe_bit(cls,n,list_pos):
        """
            Creates an identity boolean circuit with certain bits perturbated (inversed)
            mimicking errors in signals
            
            Parameters:
            -----------
            
            n (int): number of bits of the signal
            list_pos (list) : a list of position representing the bits that should be reversed (range {0,...,n-1})
            
            Returns:
            --------
            A bool_circ with n inputs, n outputs either linked directely (no perturbation) or with a not gate 
            in between (addition of perturbation)
        """
        circuit = cls.empty_bool_circ()
        for i in range(n):
            inp = circuit.add_copy_node()
            circuit.add_input_id(inp)
            out = circuit.add_copy_node()
            circuit.add_output_id(out)
            if i in list_pos:
                erreur = circuit.add_not_node()
                circuit.add_edge(inp,erreur)
                circuit.add_edge(erreur , out)
            else:
                circuit.add_edge(inp,out)
                
        return circuit

    #################### EVALUATION OF A CIRCUIT #####################

    def evaluate(self):
        """
            Evaluate the boolean circuit to produce an output.

            The evaluation starts from the input nodes and propagates to the output nodes,
            applying logical operations based on the node labels.
            
            Returns:
            -------
            int that represents the result in binary
        """
        tmp = []
        
        #taking care of neutral gates at the beginning which dont result of transformations
        copy = (self.get_id_node_map().copy()).values()
        for node in copy:
            if (node.is_or() or node.is_not() or node.is_xor() or node.is_and()) and len(node.get_parents())==0 :
                self.neutral_element(node.get_id())
                tmp.append(node.get_id())

        calculated = list(self.get_inputs_ids()) + tmp #constant nodes queue ready to be evaluated
        outputs = list(self.get_outputs_ids()) 
        
        while outputs != [] and calculated != []:
            node_id = calculated[0]
            calculated.remove(node_id)
            node = self.get_node_by_id(node_id)
            calculated += node.eval(self,outputs)  #returns nodes that wait to be evaluated and updates queue
        
        #cleanning up the circuit
        for c in calculated:
            self.remove_node_by_id(c)

        #getting the result
        res = ""
        (self.get_outputs_ids()).sort()
        for out in (self.get_outputs_ids()):
            res+= self.get_node_by_id(out).get_label()
        
        return int(res , 2)
    
    def transform_circuit(self):
        """
        Applies as many simplifications as possible to the boolean circuit using already predefined rules
        
        Result:
        -------
        A simplified version of self that is equivalent to it
        """
        
        def transform_once():
            """
            Runs through all the nodes of a bool_circ and applies as many transformations as possible

            Returns:
            -------
            True if a transformation was successfully applied, false otherwise
            (used as a flag for continuing the iteration of the circuit)
            """
            nodes = list(self.get_node_ids())
            flag = False
            for node_id in nodes:
                r = False
                #if id was erased dureing previous transformation, ignore
                if node_id in self.get_inputs_ids() or node_id in self.get_outputs_ids() or node_id not in self.get_node_ids():
                    continue
                
                node = self.get_node_by_id(node_id)
                label = node.get_label()
                first_child = (self.get_node_by_id((list(node.get_children())[0])))
                
                if first_child.is_copy() and len(first_child.get_children()) == 0:
                        r=self.effacement(node_id ,list(node.get_children())[0] )
                else:  #look for transformation
                    r = node.transform(self)
                    
                if r: # a transformation was made, will iterate again
                    flag = True
            return flag
        
        cont = True
        while cont: 
            cont = transform_once()
    
    def calculate(self):
        """
        A simple method that simplifies the circuit before evaluating it
        """
        self.transform_circuit()
        return self.evaluate()
