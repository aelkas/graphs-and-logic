import os
import sys
sys.path[0] = os.path.abspath(os.path.join(sys.path[0], '..'))
from modules.bool_circ import bool_circ

class adders(bool_circ):
    @classmethod
    def adder_helper(cls,n):
        '''
            auxiliary function that helps create the adder recursively

            Parameters:
            -----------
            n (int) : represent which level of adder wanted; Adder_n.
            
            Returns:
            --------
            a tuple of adder_n circuit (adders), carry in id (int), carry out id (int)
        '''
        if n == 0:
            circuit = cls.empty_bool_circ()
            inp1 = circuit.add_copy_node()
            inp2 = circuit.add_copy_node()
            carry_in = circuit.add_copy_node()
            cop1 =  circuit.add_copy_node({inp1:1},{})
            cop2 =  circuit.add_copy_node({inp2:1},{})
            and1 = circuit.add_and_node({cop1:1,cop2:1},{})
            nor1 = circuit.add_xor_node({cop1:1,cop2:1},{})
            cop3 = circuit.add_copy_node({nor1:1},{})
            cop4 = circuit.add_copy_node({carry_in:1},{})
            and2 = circuit.add_and_node({cop3:1,cop4:1},{})
            nor2 = circuit.add_xor_node({cop3:1,cop4:1},{})
            or1 =  circuit.add_or_node({and1:1,and2:1},{})
            carry_out =  circuit.add_copy_node({or1:1},{})
            out2 =  circuit.add_copy_node({nor2:1},{})
            circuit.set_inputs([inp1,inp2,carry_in])
            circuit.set_outputs([carry_out,out2])
            return circuit,carry_in,carry_out
        else:
            adder_1,carry_in1,carry_out1 = cls.adder_helper(n-1)
            adder_2,carry_in2,carry_out2 = cls.adder_helper(n-1)
            n = adder_1.iparallel(adder_2)
            adder_1.add_edge(carry_out1+n,carry_in2)
            adder_1.get_inputs_ids().remove(carry_in2)
            adder_1.get_outputs_ids().remove(carry_out1+n)
            return adder_1,carry_in1+n,carry_out2
    
    @classmethod
    def adder(cls,n):
        '''
            use adder_helper to create adder_n

            Parameters:
            -----------
            n (int) : represent which level of adder wanted; Adder_n.
            
            Returns:
            --------
            adder_n circuit (adders)
        '''
        add,cin,cout = cls.adder_helper(n)
        add.get_inputs_ids().sort()
        add.get_outputs_ids().sort()
        return add

    @classmethod
    def half_adder(cls,n):
        '''
            use adder_helper to create half_adder_n

            Parameters:
            -----------
            n (int) : represent which level of adder wanted; Adder_n.
            
            Returns:
            --------
            half_adder_n circuit (adders)
        '''
        add,cin,cout = cls.adder_helper(n)
        add.get_node_by_id(cin).set_label("0")
        return add,cin
    
    @classmethod
    def CL_4bit(cls):
        '''
            creates the circuit representing the pn gn algebraic expressions

            Parameters:
            -----------
            None

            Returns:
            -------
            the circuit representing the pn gn algebraic expressions
        '''
        return cls.parse_parentheses("((g3)^((p3)&(g2))^((p3)&(p2)&(g1))^((p3)&(p2)&(p1)&(g0))^((p3)&(p2)&(p1)&(p0)&(c0)))",
                                        "((g2)^((p2)&(g1))^((p2)&(p1)&(g0))^((p2)&(p1)&(p0)&(c0)))",
                                        "((g1)^((p1)&(g0))^((p1)&(p0)&(c0)))" , 
                                        "((g0)^((p0)&(c0)))")
    
    @classmethod 
    def CLA_4bit(cls):
        '''
            creates the circuit representing a CLA 4bit adder (CLA_adder(0))

            Parameters:
            -----------
            None
            
            Returns:
            -------
            the circuit representing the CLA 4bit adder (CLA_adder(0))
        '''
        circuit ,inps = cls.CL_4bit()
        dict_inputs = {inps[i]:list(circuit.get_inputs_ids())[i] for i in range(len(inps))}
        
        copies  = [circuit.add_copy_node() for i in range(13)]
        ands = [circuit.add_and_node() for i in range(4)]
        xors = [circuit.add_xor_node() for i in range(8)]
        
        #links for gi pi
        circuit.add_edges(
            [(copies[i],xors[i]) for i in range(4)] + [(copies[i+4],xors[i]) for i in range(4)] +
            [(copies[i],ands[i]) for i in range(4)] + [(copies[i+4],ands[i]) for i in range(4)] +
            [(xors[i],copies[9+i]) for i in range(4)],[]
        )
        
        #linking the "inputs" of CL with the top portion of the circuit
        circuit.add_edge(copies[8] , dict_inputs["c0"])
        for i in range(0,4):
            circuit.add_edge(copies[9+i],dict_inputs["p"+str(i)])
            circuit.add_edge(ands[i],dict_inputs["g"+str(i)])
        
        
        for i in range(4):
            circuit.add_edge(copies[9+i],xors[4+i])
        circuit.add_edge(copies[8], xors[4])
        
        #linking outputs to the bottom portion of the circuit
        circuit.get_outputs_ids().sort()
        for i in range(1,len(circuit.get_outputs_ids())):
            circuit.add_edge(list(circuit.get_outputs_ids())[i] , xors[8-i])
        c_n1 = list(circuit.get_outputs_ids())[0]
        
        
        #resetting the inputs and outputs of the circuit and adding the final ones
        circuit.set_outputs([])
        circuit.set_inputs([])
        
        circuit.add_output_node(c_n1)
        for i in range(3,-1,-1):
            circuit.add_output_node(xors[4+i])
        
        circuit.add_input_node(copies[8])
        for i in range(8):
            circuit.add_input_node(copies[i])
        
        return circuit
    
    @classmethod
    def CLA_helper(cls,n):
        '''
            auxiliary function that helps create the CLA_adder recursively

            Parameters:
            -----------
            n (int) : represent which level of adder wanted; CLA_adder_n.
            
            Returns:
            --------
            a tuple of CLA_adder_n circuit (adders), carry out id (int), carry in id (int)
        '''
        if (n==0):
            g = cls.CLA_4bit()
            return 65,g,70
        else :
            cout1,CLA1,cin1 = cls.CLA_helper(0)
            cout2,CLA2,cin2 = cls.CLA_helper(n-1)
            n = CLA1.iparallel(CLA2)
            CLA1.add_edge(cout1+n,cin2)
            CLA1.get_inputs_ids().remove(cin2)
            CLA1.get_outputs_ids().remove(cout1+n)
            return cout2,CLA1,cin1+n
        
    @classmethod
    def CLA_adder(cls,n):
        '''
            function that creates the CLA_adder

            Parameters:
            -----------
            n (int) : represent which level of adder wanted; CLA_adder_n.
            
            Returns:
            --------
            CLA_adder_n circuit (adders)
        '''
        cout,cla,cin = cls.CLA_helper(n)
        return cla