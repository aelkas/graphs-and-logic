import sys
class open_digraph_paths_distance:
        
    def dijkstra(self, src_node , direction = 0,tgt = None):
        """
            dijkstra's algorithm to find the shortest path from a node to any other node

            Parameters:
            -----------
            src_node, the node source.
            direction: an int representing direction of the search 
                direction = 0: bidirectional graph (both directions).
                direction = 1: search only children.
                direction = -1: search only parents.

            Returns:
            --------
            dict,dict {node:int}{node:node} :
            the first indicating the length of the path to each node from the source node.
            the seconf indicating the previous node before arriving to the wanted node.
        """
        Q = [src_node]
        dist = {src_node:0}
        prev = {}
        while Q != []:
            shortest = sys.maxsize
            u = None
            for node in Q:
                if dist[node] <= shortest:
                    shortest = dist[node]
                    u = node
            if u == tgt:  #Early stoppage if min dist to tgt has been calculated
                return dist,prev
            Q.remove(u)
            if direction == 1:
                neighbours = u.get_children()
            elif direction == -1:
                neighbours = u.get_parents()
            else :
                new_dict = u.get_children().copy()
                neighbours = new_dict.update(u.get_parents())
            for nei in neighbours:
                v= self.get_node_by_id(nei)
                if v not in dist:
                    Q.append(v)
                if v not in dist or dist[v]> dist[u]+1:
                    dist[v] = dist[u]+1
                    prev[v] = u
        return dist,prev
    
    
    def shortest_path(self , u , v):
        return self.dijkstra( u , direction = 0,tgt = v)[0][v]  #dist[v] with u as source node
    
    def distances_from_common_ancestors(self , u ,v):
        distu , prevu = self.dijkstra( u , direction = -1)
        distv ,prevv = self.dijkstra( v , direction = -1)
        
        result = {}   #Ancestors are not strict here
        for key in distu:
            if key in distv:
                result[key] = (distu[key] , distv[key])
        return result
    
    def topological_sort(self):
        '''
        topological sorting of a graph

        contents:
        ----------
        function get_coleave which gets a curretn coleaf from a graph and adds it to a semi_visited node
        once we get all the current coleafs, we add all the semi_visited elements to visited
        '''
        visited =set(self.get_inputs_ids())
        stack = []
        def get_coleave(semi_visit,node_ID,nnode,sub_stack):
            flag = True
            for parent in nnode.get_parents():
                if not (parent in visited):  
                    flag = False
            
            if flag:
                sub_stack.append(node_ID)
                semi_visit.append(node_ID)
                return True
            return False
                
        flag_isthere_coleaf = True
        while flag_isthere_coleaf and len(visited)<len(self.get_node_ids()):
            flag_isthere_coleaf = False
            sub_stack = []
            semi_visit = []
            for node_ID in self.get_id_node_map():
                if node_ID not in visited:
                    if get_coleave(semi_visit,node_ID,self.get_node_by_id(node_ID),sub_stack):
                        flag_isthere_coleaf= True
            stack.append(sub_stack)
            visited.update(semi_visit)
        assert (not len(visited)<len(self.get_node_ids())), "graph is cyclic"
        return stack 
    
    def depth_node_acyclic_knowing_Topological_sort(self,node,stack):
        '''
        assuming we know a topological sorting, this returns
        the depth of a node
        
        Parameters:
        -----------  
        node : the node we want to know the depth of
        stack :list of list, the result of the topological sorting

        Returns:
        -------
        int depth of a node
        '''
        assert node in self.get_nodes(), "node isn't in graph"
        i = 0
        while node.get_id() not in stack[i]:
            i+=1
        
        return (i+1)
    
    def depth_node_acyclic(self,node):
        assert node in self.get_nodes(), "node isn't in graph"
        stack = self.topological_sort()
        i = 0
        while node.get_id() not in stack[i]:
            i+=1
        return i+1

    def depth_acyclic(self):
        return len(self.topological_sort())
    
    def longest_path(self,u,v):
        dist = {u:0}
        prev = {u:u}
        stack = self.topological_sort()
        u_depth = self.depth_node_acyclic_knowing_Topological_sort(self.get_node_by_id(u),stack)
        graph_depth = len(stack)
        for i in range(u_depth,graph_depth):
            for j in range(0,len(stack[i])):
                w = stack[i][j]
                dist[w]= -1
                for parent in self.get_node_by_id(w).get_parents():
                    if parent in dist.keys():
                        if dist[parent]+1> dist[w]: 
                            dist[w]= dist[parent]+1
                            prev[w]=parent
                if w == v: 
                    return dist[w],prev
        return dist[v],prev

