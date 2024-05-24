import os
import sys
sys.path[0] = os.path.abspath(os.path.join(sys.path[0], '..'))

class bool_circ_gates_mx:
    def copy_gate(self, copy_node_id, input_node_id):
        """
        Replaces the copy gate node with a new set of nodes copying the input signal.

        Parameters:
        ----------
        copy_node_id : int
            The node ID of the copy gate to replace.
        input_node_id : int
            The node ID of the input signal to copy, labeled as '1' or '0'.

        Returns:
        -------
        list
            A list of newly created nodes that represent the copied input signal.
        """
        inp = self.get_node_by_id(input_node_id).get_label()
        assert inp == "1" or inp == "0"
        
        children = list(self.get_node_by_id(copy_node_id).get_children())
        self.remove_node_by_id(copy_node_id)
        self.remove_node_by_id(input_node_id)
        res = []
        for child in children:
            copied_input = self.add_node(inp)
            self.add_edge(copied_input, child)
            res.append(copied_input)
        return res

    def not_gate(self, not_node_id, input_node_id):
        """
        Inverts the input signal at the NOT gate.

        Parameters:
        ----------
        not_node_id : int
            The node ID of the NOT gate.
        input_node_id : int
            The node ID of the input signal to invert, labeled as '1' or '0'.

        Returns:
        -------
        list
            A list containing the ID of the NOT gate node after inversion.
        """
        inp = self.get_node_by_id(input_node_id).get_label()
        assert inp == "1" or inp == "0"
        
        not_node = self.get_node_by_id(not_node_id)
        self.remove_node_by_id(input_node_id)
        if inp == "1":
            not_node.set_label("0")
        else:
            not_node.set_label("1")
        
        return [not_node_id]

    def and_gate(self, and_node_id, input_node_id):
        """
        Updates the AND gate output based on the given input.

        Parameters:
        ----------
        and_node_id : int
            The node ID of the AND gate.
        input_node_id : int
            The node ID of the input signal, labeled as '1' or '0'.

        Returns:
        -------
        list
            A list containing the ID of the AND gate node after updates.
        """
        inp = self.get_node_by_id(input_node_id).get_label()
        assert inp == "1" or inp == "0"
        
        self.remove_node_by_id(input_node_id)
        and_node = self.get_node_by_id(and_node_id)
        if inp == "0":
            and_node.set_label("0")
            parents = list(and_node.get_parents()).copy()
            for p in parents:
                self.remove_parallel_edges(p, and_node_id)
                nullifier = self.add_copy_node()
                self.add_edge(p, nullifier)
            return [and_node_id]
        
        if len(and_node.get_parents()) == 0:
            self.neutral_element(and_node_id)
            return [and_node_id]

        return []

    def or_gate(self, or_node_id, input_node_id):
        """
        Updates the OR gate output based on the given input.

        Parameters:
        ----------
        or_node_id : int The node ID of the OR gate.
        input_node_id : int The node ID of the input signal, labeled as '1' or '0'.

        Returns:
        -------
        list
            A list containing the ID of the OR gate node after updates.
        """
        inp = self.get_node_by_id(input_node_id).get_label()
        assert inp == "1" or inp == "0"
        
        self.remove_node_by_id(input_node_id)
        or_node = self.get_node_by_id(or_node_id)
        if inp == "1":
            or_node.set_label("1")
            parents = list(or_node.get_parents()).copy()
            for p in parents:
                self.remove_parallel_edges(p, or_node_id)
                nullifier = self.add_copy_node()
                self.add_edge(p, nullifier)
            return [or_node_id]
        
        if len(or_node.get_parents()) == 0:
            self.neutral_element(or_node_id)
            return [or_node_id]

        return []

    def xor_gate(self, xor_node_id, input_node_id):
        """
        Adjusts the XOR gate operation based on the given input.

        Parameters:
        ----------
        xor_node_id : int The node ID of the XOR gate.
        input_node_id : int The node ID of the input signal, labeled as '1' or '0'.

        Returns:
        -------
        list
            A list containing the XOR gate or its transformed form after updates.
        """
        inp = self.get_node_by_id(input_node_id).get_label()
        assert inp == "1" or inp == "0"
        
        self.remove_node_by_id(input_node_id)
        xor_node = self.get_node_by_id(xor_node_id)
        new_xor = None
        if inp == "1":
            xor_node.set_label("~")
            parents = list(xor_node.get_parents()).copy()
            
            new_xor = self.add_node(label="^")
            self.add_edge(new_xor, xor_node_id)
            for p in parents:
                self.remove_parallel_edges(p, xor_node_id)
                self.add_edge(p, new_xor)
        
        if len(xor_node.get_parents()) == 0 and xor_node.get_label() == "^":
            self.neutral_element(xor_node_id)
            return [xor_node_id]
        elif new_xor is not None and len(self.get_node_by_id(new_xor).get_parents()) == 0:
            self.neutral_element(new_xor)
            return [new_xor]

        return []

    def neutral_element(self, binary_gate):
        """
        Neutralizes a binary gate node, setting its neutral value.

        Parameters:
        ----------
        binary_gate : int The node ID of the binary gate to neutralize.

        Returns:
        -------
        None
        """
        node = self.get_node_by_id(binary_gate)
        if node.is_or() or node.is_xor():
            node.set_label("0")
            self.convert_node(node)
        elif node.is_and():
            node.set_label("1")
            self.convert_node(node)

    def assoc_xor(self, parent_xor, child_xor):
        """
        Applies the associative property to two XOR gates.

        Parameters:
        ----------
        parent_xor : int The node ID of the parent XOR gate.
        child_xor : int The node ID of the child XOR gate.

        Returns:
        -------
        bool
            True if the association was successful, otherwise False.
        """
        parent_node = self.get_node_by_id(parent_xor)
        child_node = self.get_node_by_id(child_xor)
        assert parent_node.is_xor() and child_node.is_xor()
        
        parents_of_parent = list(parent_node.get_parents())
        self.remove_node_by_id(parent_xor)
        
        for p in parents_of_parent:
            self.add_edge(p, child_xor)
        return True

    def assoc_and(self, parent_and, child_and):
        """
        Bonus transformation

        Applies the associative property to two AND gates.

        Parameters:
        ----------
        parent_and : int The node ID of the parent AND gate.
        child_and : int The node ID of the child AND gate.

        Returns:
        -------
        bool
            True if the association was successful, otherwise False.
        """
        parent_node = self.get_node_by_id(parent_and)
        child_node = self.get_node_by_id(child_and)
        assert parent_node.is_and() and child_node.is_and()
        
        parents_of_parent = list(parent_node.get_parents())
        self.remove_node_by_id(parent_and)
        
        for p in parents_of_parent:
            self.add_edge(p, child_and)
        return True

            
    def assoc_or(self, parent_or, child_or):
        """

        Bonus transformation
        
        Applies the associative property to two OR gates.

        Parameters:
        ----------
        parent_or : int The node ID of the parent OR gate.
        child_or : int The node ID of the child OR gate.

        Returns:
        -------
        bool
            True if the association was successful, otherwise False.
        """
        parent_node = self.get_node_by_id(parent_or)
        child_node = self.get_node_by_id(child_or)
        assert parent_node.is_or() and child_node.is_or()
        
        parents_of_parent = list(parent_node.get_parents())
        self.remove_node_by_id(parent_or)
        
        for p in parents_of_parent:
            self.add_edge(p, child_or)
        return True

    def assoc_copy(self, parent_copy, child_copy):
        """
        Applies the associative property to two copy nodes.

        Parameters:
        ----------
        parent_copy : int The node ID of the parent copy node.
        child_copy : int The node ID of the child copy node.

        Returns:
        -------
        bool
            True if the association was successful, otherwise False.
        """
        parent_node = self.get_node_by_id(parent_copy)
        child_node = self.get_node_by_id(child_copy)
        assert parent_node.is_copy() and child_node.is_copy()
        
        if child_copy in self.get_outputs_ids() or parent_copy in self.get_inputs_ids():
            return False
        
        children_of_child = list(child_node.get_children())
        self.remove_node_by_id(child_copy)
        
        for c in children_of_child:
            self.add_edge(parent_copy, c)
        return True

    def involution_xor(self, xor_id, copy_id):
        """
        Resolves XOR involution based on the copy node multiplicity.

        Parameters:
        ----------
        xor_id : int The node ID of the XOR gate.
        copy_id : int The node ID of the copy node.
        
        Returns:
        -------
        bool
            True if the involution was successful, otherwise False.
        """
        xor_node = self.get_node_by_id(xor_id)
        copy_node = self.get_node_by_id(copy_id)
        assert xor_node.is_xor() and copy_node.is_copy()
        nb_arretes = (copy_node.get_children())[xor_id]
        
        if nb_arretes >= 2:
            self.remove_parallel_edges(copy_id, xor_id)
            
            if nb_arretes % 2 == 1:
                self.add_edge(copy_id, xor_id)
            
            return True
        else:
            return False

    def effacement(self, op_id, child_id):
        """
        Replaces an operation node with a neutral copy node.

        Parameters:
        ----------
        op_id : int The node ID of the operation node to be removed.
        child_id : int The node ID of the child node to be replaced.

        Returns:
        -------
        bool
            True if the effacement was successful, otherwise False.
        """
        if child_id in self.get_outputs_ids():
            return False
        
        parents = list(self.get_node_by_id(op_id).get_parents())
        self.remove_node_by_id(op_id)
        self.remove_node_by_id(child_id)
        
        for p in parents:
            nullifier = self.add_copy_node()
            self.add_edge(p, nullifier)
            
        return True

    def not_xor(self, not_id, xor_id):
        """
        Applies a NOT gate to an XOR operation.

        Parameters:
        ----------
        not_id : int The node ID of the NOT gate.
        xor_id : int The node ID of the XOR gate.

        Returns:
        -------
        bool
            True if the operation was successful, otherwise False.
        """
        xor_node = self.get_node_by_id(xor_id)
        not_node = self.get_node_by_id(not_id)
        assert xor_node.is_xor() and not_node.is_not()
        
        parent_of_not = list(not_node.get_parents())[0]
        child_of_xor = list(xor_node.get_children())[0]
        
        self.remove_parallel_edges(xor_id, child_of_xor)
        self.remove_parallel_edges(parent_of_not, not_id)
        self.remove_parallel_edges(not_id, xor_id)
        self.add_edge(xor_id, not_id)
        self.add_edge(not_id, child_of_xor)
        self.add_edge(parent_of_not, xor_id)
        return True
    
    def not_copy(self, not_id, copy_id):
        """
        Applies a NOT gate to a copy operation.

        Parameters:
        ----------
        not_id : int The node ID of the NOT gate.
        copy_id : int The node ID of the copy node.

        Returns:
        -------
        bool
            True if the NOT operation was successfully applied to all child nodes, otherwise False.
        """
        copy_node = self.get_node_by_id(copy_id)
        not_node = self.get_node_by_id(not_id)
        assert copy_node.is_copy() and not_node.is_not()
        if copy_id in self.get_outputs_ids():
            return False

        parent_of_not = list(not_node.get_parents())[0]
        self.remove_node_by_id(not_id)
        self.add_edge(parent_of_not, copy_id)

        children_of_copy = list(self.get_node_by_id(copy_id).get_children())
        for c in children_of_copy:
            new_not = self.add_not_node()
            self.remove_edge(copy_id, c)
            self.add_edge(copy_id, new_not)
            self.add_edge(new_not, c)
        return True

    def involution_not(self, not1, not2):
        """
        Resolves the involution of two NOT gates.

        Parameters:
        ----------
        not1 : int The node ID of the first NOT gate.
        not2 : int The node ID of the second NOT gate.

        Returns:
        -------
        bool
            True if the two NOT gates were successfully removed and replaced with a direct connection.
        """
        node1 = self.get_node_by_id(not1)
        node2 = self.get_node_by_id(not2)
        assert node1.is_not() and node2.is_not()

        parent_of_node1 = list(node1.get_parents())[0]
        child_of_node2 = list(node2.get_children())[0]

        self.remove_node_by_id(not1)
        self.remove_node_by_id(not2)
        self.add_edge(parent_of_node1, child_of_node2)
        return True

    def idempotance_and(self, and_id, copy_id):
        """
        Bonus transformation
        
        Applies the idempotence property to an AND gate.

        Parameters:
        ----------
        and_id : int The node ID of the AND gate.
        copy_id : int The node ID of the copy node.

        Returns:
        -------
        bool
            True if the idempotence was successfully applied to the AND gate, otherwise False.
        """
        and_node = self.get_node_by_id(and_id)
        copy_node = self.get_node_by_id(copy_id)
        assert and_node.is_and() and copy_node.is_copy()
        nb_arretes = (copy_node.get_children())[and_id]
        if nb_arretes > 1:
            self.remove_parallel_edges(copy_id, and_id)
            self.add_edge(copy_id, and_id)
            return True
        else:
            return False
        
    def idempotance_or(self, or_id, copy_id):
        """
        Bonus transformtion

        Applies the idempotence property to an OR gate.

        Parameters:
        ----------
        or_id : int The node ID of the OR gate.
        copy_id : int The node ID of the copy node.

        Returns:
        -------
        bool
            True if the idempotence property was successfully applied to the OR gate, otherwise False.
        """
        or_node = self.get_node_by_id(or_id)
        copy_node = self.get_node_by_id(copy_id)
        assert or_node.is_or() and copy_node.is_copy()
        nb_arretes = (copy_node.get_children())[or_id]
        if nb_arretes > 1:
            self.remove_parallel_edges(copy_id, or_id)
            self.add_edge(copy_id, or_id)
            return True
        else:
            return False

    def absoroption_and(self, copy_id, or_id, and_id):
        """
        Bonus transformation

        Resolves an AND gate by absorbing the copy and OR gates.

        Parameters:
        ----------
        copy_id : int The node ID of the copy node.
        or_id : int The node ID of the OR gate.
        and_id : int The node ID of the AND gate.

        Returns:
        -------
        bool True if the absorption process was successful, otherwise False.
        """
        or_node = self.get_node_by_id(or_id)
        copy_node = self.get_node_by_id(copy_id)
        and_node = self.get_node_by_id(and_id)
        assert or_node.is_or() and copy_node.is_copy() and and_node.is_and()

        nullifier = self.add_copy_node()
        self.add_edge(or_node, nullifier)
        self.effacement(or_id, nullifier)
        return True

    def absoroption_or(self, copy_id, or_id, and_id):
        """
        Bonus transformation

        Resolves an OR gate by absorbing the copy and AND gates.

        Parameters:
        ----------
        copy_id : int The node ID of the copy node.
        or_id : int The node ID of the OR gate.
        and_id : int The node ID of the AND gate.

        Returns:
        -------
        bool True if the absorption process was successful, otherwise False.
        """
        or_node = self.get_node_by_id(or_id)
        copy_node = self.get_node_by_id(copy_id)
        and_node = self.get_node_by_id(and_id)
        assert or_node.is_or() and copy_node.is_copy() and and_node.is_and()

        nullifier = self.add_copy_node()
        self.add_edge(and_node, nullifier)
        self.effacement(and_id, nullifier)
        return True
