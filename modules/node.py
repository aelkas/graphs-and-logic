from abc import ABC, abstractmethod
class node:
    
    ###Constructor
    
    def __init__(self , identity , label , parents , children):
        
        """
        identity: int; its unique id in the graph
        label: string;
        parents: int->int dict; maps a parent nodes id to its multiplicity
        children: int->int dict; maps a child nodes id to its multiplicity 
        """
        
        self.id = identity
        self.label = label
        self.parents = parents
        self.children = children 
    

    def copy(self):
        return node(self.id , self.label , self.parents.copy() , self.children.copy())

    
    
    ### Getters and setters
    def get_id(self):
        return self.id
    
    def get_label(self):
        return self.label
    
    def get_parents(self):
        return self.parents
    
    def get_children(self):
        return self.children   

    def set_id(self , id):
        self.id = id
    
    def set_label(self, label):
        self.label = label
    
    def set_children(self , children):
        self.children = children

    def set_parents(self, parents):
        self.parents = parents
    
    
    ###Adding and removing
    
    def add_parent_id(self, par_id , multiplicity=1):
        """ 
            Adds par_id to the node's parent dictionary with a given multiplicy
        """
        if par_id in self.parents.keys():
            self.parents[par_id] += multiplicity
        else:
            self.parents[par_id] = multiplicity
    
    def add_child_id(self, child_id , multiplicity=1):
        """ 
            Adds child_id to the node's children dictionary with a given multiplicy
        """
        
        if child_id in self.children.keys():
            self.children[child_id] += multiplicity
        else:
            self.children[child_id] = multiplicity


    #Note: if multiplicity == 0 the map to the node is removed
    
    def remove_parent_once(self,id):
        """ 
            removes a parent from the node's parent dictionary (one multiplicity)
        """
        self.parents[id] -=1
        if self.parents[id] == 0:
            del  self.parents[id]
            
    def remove_child_once(self,id):
        """ 
            removes a child from the node's children dictionary (one multiplicity)
        """
        self.children[id] -=1
        if self.children[id] == 0:
            del  self.children[id]
    
    def remove_parent_id(self , id):
        del  self.parents[id]
    
    def remove_child_id(self , id):
        del  self.children[id]
    
    def __str__ (self):
        return f"Node {self.id}: \nLabel : {self.label}\nParents : {self.parents}\nChildren : {self.children}"
        
    def __repr__(self):
        return repr(self.__str__)
    
    def __eq__(self,g):
        if type(self)!=type(g):
            return False
        return self.id == g.get_id() and self.label == g.get_label() and self.children == g.get_children() and self.parents == g.get_parents()
    def __ne__(self,g):
        return not self.__eq__(g)
    
    def indegree(self):
        """
            Returns the number on ingoing edges towards the node
        """
        acc = 0
        p = self.get_parents()
        for i in p:
            acc += p[i]
        return acc
    
    def outdegree(self):
        """
            Returns the number on outgoing edges from the node
        """
        acc = 0
        p = self.get_children()
        for i in p:
            acc += p[i]
        return acc
    
    def degree(self):
        """
            returns the degree of the node
        """
        return self.indegree()+self.outdegree()
    
    def is_copy(self):
        return self.label == ""
    
    def is_or(self):
        return self.label == "|"
    
    def is_and(self):
        return self.label == "&"
    
    def is_not(self):
        return self.label == "~"
    
    def is_xor(self):
        return self.label == "^"
    
    def is_constant(self):
        return self.label == 1 or self.label == 0
    
    
    
    def transform(self, circuit):
        """
            call the appropriate transform method defined in the adequate subclass of node (relatively to self)
            for circuit simplificaion
            This method serves as an interface for the all the code that has been devided between subclasses
            
            Parameters:
            -----------
            
            circuit (bool_circ) : the circuit containing the node self
            
            Returns:
            --------
            
            True if a transformation is performed false otherwise
        """
        
        if self.is_copy():
            return circuit_node.from_node(self).transform(circuit)
        elif self.is_and():
            return circuit_node.from_node(self).transform(circuit)
        elif self.is_or():
            return circuit_node.from_node(self).transform(circuit)
        elif self.is_not():
            return circuit_node.from_node(self).transform(circuit)
        elif self.is_xor():
            return circuit_node.from_node(self).transform(circuit)

    def eval(self,circuit,outputs):
        """
            gets the child of self in circuit and calls the adequate calcul method from it
            Preconditions:
            -------------
            self.label = "1" or self.label = "0" i.e the node is already a constant ready to be propagated
            
            Parameters:
            -----------
            circuit (bool_circ) : the boolean circuit that contains self
            
            outputs (list) : a list of ids representing the outputs that have yet to be calculated in the main evaluate() function
            
            Returns:
            --------
            A list of ids of the nodes (potentially empty) that have turned into a constant and are ready to propagate the signal
            
        """
        
        #Neutral element management
        if (self.is_and() or self.is_or() or self.is_xor()) and len(self.parents)==0:
            circuit.neutral_element(self.id)
            res = [self.id]
        
        else:
            
            assert self.get_label() == "0" or self.get_label() == "1" 
            res = []
            node_id = self.get_id()
            child = list(self.get_children())[0]
            
            if child in circuit.get_outputs_ids(): #if output,copy the value of the parent and remove it from the queue
                circuit.get_node_by_id(child).set_label(self.get_label())
                circuit.remove_node_by_id(node_id)
                outputs.remove(child)
                
            else: #apply calculation accodingly
                
                child_node = circuit.get_node_by_id(child)
                if child_node.is_and():
                    res = circuit.and_gate(child,node_id)
                elif child_node.is_or():
                    res = circuit.or_gate(child,node_id)
                elif child_node.is_xor():
                    res = circuit.xor_gate(child,node_id)
                elif child_node.is_not():
                    res = circuit.not_gate(child,node_id)
                elif child_node.is_copy():
                    res = circuit.copy_gate(child,node_id)
        
        return res


class circuit_node(node):
    @classmethod
    def from_node(cls,node):
        """
            Given a node, returns the adequate specialization of said node 
        """
        id = node.get_id()
        label = node.get_label()
        parents = node.get_parents().copy()
        children = node.get_children().copy()
        if label == "":
            return copy_node(id,parents,children)
        elif label == "&":
            return and_node(id,parents,children)
        elif label == "|":
            return or_node(id,parents,children)
        elif label == "~":
            return not_node(id,parents,children)
        elif label == "^":
            return xor_node(id,parents,children)
        elif label == "0" or label == "1":
            return constant_node(id,label,parents,children)
        return None
    


    @abstractmethod
    def transform(self,circuit):
        """
        Given the node and the circuit it is in, checks if it can make any transformation
        and calls the adequate method from circuit to apply it
        
        Parameters:
        ----------
        
        circuit (bool_circ) : the circuit containing the given node 
        
        Returns:
        -------
        True if a transformation was made , false otherwise
        """
        pass

class copy_node(circuit_node):
    
    def __init__(self , identity, parents , children):
        super().__init__(identity,"",parents, children)
    
        
    def transform(self,circuit):
        r = False
        parents = list(self.get_parents())
        children = list(self.get_children())
            
        if len(children) == 1:  #gets rid of unecessary copy node forming chains
            circuit.remove_node_by_id(self.get_id())
            circuit.add_edge(parents[0],children[0])
            return True
        else:
            for c in children:
                c_node = circuit.get_node_by_id(c)
                if  c_node.is_copy():
                    r=circuit.assoc_copy(self.get_id(),c)        
                elif c_node.is_xor():
                    r=circuit.involution_xor(c,self.get_id())
                    
                #necessary for absorptions, heavy time-complexity wise
                elif c_node.is_and():
                    r = circuit.idempotance_and(c,self.get_id())
                    for other_node_id in children:
                        if other_node_id in circuit.get_node_ids():
                            other_node = circuit.get_node_by_id(other_node_id)
                            if other_node_id != c and other_node.is_or() and list(other_node.get_children())[0] == c_node:
                                r = circuit.absoroption_and(self.get_id() ,list(other_node.get_children())[0],other_node_id )
                
                elif c_node.is_or():
                    for other_node_id in children:
                        if other_node_id in circuit.get_node_ids():
                            r = circuit.idempotance_or(c,self.get_id())
                            other_node = circuit.get_node_by_id(other_node_id)
                            if other_node_id != c and other_node.is_and() and list(other_node.get_children())[0] == c_node:
                                r = circuit.absoroption_or(self.get_id() ,list(other_node.get_children())[0],other_node_id)
        return r

class and_node(circuit_node):
    
    def __init__(self , identity, parents , children):
        super().__init__(identity,"&",parents, children)
        
    
    def transform(self, circuit):
        r = False
        parents = list(self.get_parents())
        
        for p in parents:
            parent_node = circuit.get_node_by_id(p)
            
            if  parent_node.is_and():
                r=circuit.assoc_and(p,self.get_id())
        return r

class or_node(circuit_node):
    
    def __init__(self , identity, parents , children):
        super().__init__(identity,"|",parents, children)
        
    def transform(self, circuit):
        r = False
        parents = list(self.get_parents())
        for p in parents:
            parent_node = circuit.get_node_by_id(p)
            
            if  parent_node.is_or():
                r = circuit.assoc_or(p,self.get_id())  
        return r 


class not_node(circuit_node):
    
    def __init__(self , identity, parents , children):
        super().__init__(identity,"~",parents, children)
    
    def transform(self, circuit):
        r = False
        node_id = self.id
        parent = list(self.get_parents())[0]
        child = list(self.get_children())[0]
                        
        if circuit.get_node_by_id(parent).is_not() :
            r=circuit.involution_not(parent,self.get_id())
            
        elif circuit.get_node_by_id(child).is_not() :
            r=circuit.involution_not(self.get_id(),child)
                            
        elif circuit.get_node_by_id(child).is_copy():
            r=circuit.not_copy(node_id,child)
        return r
    
class xor_node(circuit_node):
    
    def __init__(self , identity, parents , children):
        super().__init__(identity,"^",parents, children)
        
    
    def transform(self, circuit):
        r = False
        parents = list(self.get_parents())
        
        for p in parents:
            parent_node = circuit.get_node_by_id(p)
            if  parent_node.is_xor():
                r=circuit.assoc_xor(p,self.get_id())
                
            elif parent_node.is_copy():
                r=circuit.involution_xor(self.get_id(),p)
                
            elif parent_node.is_not():
                r=circuit.not_xor(p,self.get_id())
        return r
        


class constant_node(circuit_node):
    def __init__(self , identity,inp, parents , children):
        assert inp == "0" or inp == "1"
        super().__init__(identity,inp,parents, children)
    
    
    def transform(self, circuit):
        #such transformations are taked care of in the eval function
        pass