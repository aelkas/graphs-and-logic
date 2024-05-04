class open_digraph_composition:
    def min_id(self):
        """
            Returns the id with the smallest value
        """
        m = -1
        for node in self.nodes.values():
            cid = node.get_id() 
            if m==-1:
                m = cid
            elif cid < m:
                m = cid
        return m
    
    def max_id(self):
        """
            Returns the id with the biggest value
        """
        m = -1
        for node in self.nodes.values():
            cid = node.get_id() 
            if cid > m:
                m = cid
        return m

    def shift_indices(self,n):
        """
            Shifts the ids of all nodes in the graph by n
            
            Parameters:
            -----------
            
            n (int) : the value with which the ids will be shifted , can be negative
            
            Output:(inplace)
            -------
            
            The graph (self) with indices shifted by n
        """
        def shift_keys(dictionary, m):
            shifted_dict = {}
            for key, value in dictionary.items():
                new_key = key + m
                shifted_dict[new_key] = value
            return shifted_dict
        
        if n != 0:
            for node in self.nodes.values():
                cid = node.get_id() 
                node.set_id(cid+n)
                node.set_children(shift_keys(node.get_children(),n))
                node.set_parents(shift_keys(node.get_parents(),n))
            for i in range(len(self.inputs)):
                self.inputs[i] += n
            for i in range(len(self.outputs)):
                self.outputs[i] += n
        self.nodes = shift_keys(self.nodes, n)
    
    #6#
    def iparallel(self, g):
        """
            Appends the graph g in parallel to the current graph 
            
            Parameters:
            -----------

            g (open_digraph) : a graph that is going to be added in parallel
            
            Output: (inplace)
            -------
            
            the current graph will now be composed of it's former structure plus the graph g next to it
        """
        minId1 = self.min_id()
        maxId2 = g.max_id()
        
        self.shift_indices(-minId1+maxId2+1)   # avoiding conflicting ids with shift
        for key,nnode in g.get_id_node_map().items():   # adding the nodes of g
            self.nodes[key]= nnode.copy()
        for j in g.get_inputs_ids():
            self.add_input_id(j)
        for i in g.get_outputs_ids():
            self.add_output_id(i)
        #return the the int that shifted the indices to use it elsewhere like in adder functions
        return -minId1+maxId2+1

    #6#
    def parallel(self, g):
        """
            Appends the graph g in parallel to the current graph 
            
            Parameters:
            -----------

            g (open_digraph) : a graph that is going to be added in parallel
            
            Return: 
            -------
            
            A graph that will now be composed of current graph plus the graph g next to it
        """
        c = self.copy()
        c.iparallel(g)
        return c

    #6#
    def icompose(self, f):
        """
            Appends the graph f sequentially to the current graph connecting the inputs of self to the outputs of f
            
            Parameters:
            -----------

            f (open_digraph) : a graph to which self will be added in sequence
            
            Output: (inplace)
            -------
            
            the current graph will now be composed of f followed by the former self in sequence
        """
        assert len(f.get_outputs_ids()) == len(self.get_inputs_ids()) , "error, domains don't match."
        
        self.iparallel(f) 
        
        old_input = [inp for inp in self.get_inputs_ids() if inp not in f.get_inputs_ids()] #inputs that used to belong to self after shift
        
        # merging in sequence
        for k,f_out in enumerate(f.get_outputs_ids()):
            child_dict = self.get_node_by_id(old_input[k]).get_children()
            self.get_node_by_id(f_out).set_children(child_dict)
            self.get_node_by_id(old_input[k]).set_children({})
            for i in child_dict:
                parents_of_child = self.get_node_by_id(i).get_parents()
                multiplicity_of_old_parent = parents_of_child.pop(old_input[k])
                parents_of_child[f_out]=multiplicity_of_old_parent
            self.remove_node_by_id(old_input[k])
        
        
        # updating inputs and outputs lists
        inps = list(self.get_inputs_ids()).copy()
        for inp in inps:
            if inp not in f.get_inputs_ids():
                self.get_inputs_ids().remove(inp)
                
        outs = list(self.get_outputs_ids()).copy()
        for out in outs:
            if out in f.get_outputs_ids():
                self.get_outputs_ids().remove(out)

    #6#
    def compose(self , f):
        """
            Appends the graph f sequentially to the current graph connecting the inputs of self to the outputs of f
            
            Parameters:
            -----------

            f (open_digraph) : a graph to which self will be added in sequence
            
            Return: 
            -------
            
            A graph that will now be composed of f followed by the former self in sequence
        """
        c = self.copy()
        c.icompose(f)
        return c

    #6#
    def connected_components(self):
        """
            Returns the number of connected components as well as a map from each node to the connected component they belong to
            
            Returns:
            --------
            A tuple (int , dict) : the number of connecter components / a dictionary with all the nodes as ids and their respective connected component
        """
        visited = set()
        nb = 0
        component_dict = {}


        def dfs(node):
            if node.get_id() in visited: # i.e if all children explored, add node to the current connected component
                component_dict[node.get_id()] = nb 
            
            else:
                visited.add(node.get_id())
                children = node.get_children()
                parents = node.get_parents()
                for child_id in children:
                    dfs(self.nodes[child_id])
                    component_dict[child_id] = nb 
                for parent_id in parents:
                    dfs(self.nodes[parent_id])
                    component_dict[parent_id] = nb # adds child after exploring the connected component it belongs to

                
        
        for node in self.nodes.values():
            if node.get_id() not in visited:
                dfs(node)
                nb +=1
        return (nb , component_dict)
    
    #component list is part of open_digraph because it uses the constructor

    