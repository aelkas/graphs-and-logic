import os
import sys
sys.path[0] = os.path.abspath(os.path.join(sys.path[0], '..'))
from modules.adders import adders
from modules.bool_circ import *
import random 
import numpy as np

def find_bigger_2_pow(n):
    acc = 1
    i = 0
    while acc < n:
        acc *=2
        i+=1
    return acc,i


def add_registre_naive(a,b, size=8):
    """
        b is added to a using an adder

        Parameters:
        -----------
        b (int)
        a (int)
        size (int): size of max(a,b)

        Returns:
        --------
        sum of a and b
    """
    reg_size , n = find_bigger_2_pow(size)
    a_str = bool_circ.convert_to_binary_string(a,size=reg_size)
    b_str = bool_circ.convert_to_binary_string(b,size=reg_size)
    res = ""
    for i in range(reg_size):
        res +=   b_str[i]+a_str[i]
    res = res + "0" # adding 0 carry bit
    
    g = adders.adder(n)
    registre = bool_circ.create_registre(int(res , 2),size=2*reg_size+1)
    g.icompose(registre)
    return g.calculate()

def add_registre_naive_half(a,b, size=8):
    """
        b is added to a using a half_adder

        Parameters:
        -----------
        b (int)
        a (int)
        size (int): size of max(a,b)

        Returns:
        --------
        sum of a and b
    """
    reg_size , n = find_bigger_2_pow(size)
    a_str = bool_circ.convert_to_binary_string(a,size=reg_size)
    b_str = bool_circ.convert_to_binary_string(b,size=reg_size)
    res = ""
    for i in range(reg_size):
        res +=   b_str[i]+a_str[i]
    res = res
    res = res[::-1]
    

    g,cin = adders.half_adder(n)
    g.get_inputs_ids().remove(cin)
    #We remove the carry bit so that it wont be affected by icompose
    registre = bool_circ.create_registre(int(res , 2),size=2*reg_size)
    n = g.icompose(registre)
    g.display_graph("test2",verbose=True)
    g.get_inputs_ids().append(cin+n) #we put him back in for evaluatio
    return g.calculate()

def add_naive(a,b):
    """
        b is added to a with adder without needing to specify size
    """
    size = max(a.bit_length(),b.bit_length())
    return add_registre_naive(a,b,size = size)

def add_registre_CLA(a,b, size=8):
    """
        b is added to a using a CLA_adder

        Parameters:
        -----------
        b (int)
        a (int)
        size (int): size of max(a,b)

        Returns:
        --------
        sum of a and b
    """
    a_str = bool_circ.convert_to_binary_string(a,size=size)
    b_str = bool_circ.convert_to_binary_string(b,size=size)
    #bits must be added 4 by 4
    quotient, remainder = divmod(size, 4)
    res = ""
    for i in range(quotient-1,-1,-1):
        for c in [a_str,b_str]:
            for j in range(3,-1,-1):
                res += c[i*4+j]
    for c in [a_str,b_str]:
        for i in range(size-1,size-remainder-1,-1):
            res+= c[i]
    res = "0"+res  # adding 0 carry bit"
    g = adders.CLA_adder(quotient-1)
    registre = bool_circ.create_registre(int(res , 2),size=(quotient)*8+1)
    g.icompose(registre)
    return g.calculate()
    
def add_CLA(a,b):
    """
        b is added to a without needing to specify size by CLA method
    """
    size = 0
    quotient,mod = divmod(max(a.bit_length(),b.bit_length()),4)
    size = (quotient+1) * 4
    return add_registre_CLA(a,b,size = size)


def check_invarients():
    '''
        Prints information about our encoding and decoding functions

        Parameters:
        -----------
        None

        Returns:
        --------
        None
    '''
    #Initialize our circuits
    enc = bool_circ.encodeur_4bits()
    dec = bool_circ.decodeur_7bits()
    
    for i in range(-1,4): #-1 -> no error is introduced
        noise = adders.perturbe_bit(7,[i])  
        g = bool_circ.compose(noise,enc)  #adding perturbations
        g2 = bool_circ.compose(dec,g)
        
        for i in range(0,16):
            reg = bool_circ.create_registre(i,size=4)
            g3 = bool_circ(bool_circ.compose(g2,reg))
            assert (i==g3.calculate())
    
    print("Hamming property verfied when introducing one error at most.")
    
    mistakes = 0
    for i in range(0,4): 
        for j in range(i+1,4):
            noise = bool_circ.perturbe_bit(7,[i,j]) 
            g = bool_circ.compose(noise,enc)
            g2 = bool_circ.compose(dec,g)
            for k in range(0,16):
                reg = bool_circ.create_registre(k,size=4)
                g3 = bool_circ(bool_circ.compose(g2,reg))
                mistakes += (i!=g3.calculate())
    print(f"Number of time that the original signal couldn't be retreived when introducing 2 errors: {mistakes} out of {6*16} attempts.")
    
    
def count_edges(circuit):
    """
    Counts the number of edges in a graph , with their multiplicity
    """
    s = 0
    for node in circuit.get_nodes():
        s += sum(list(node.get_children().values()))
    return s

def print_stats():
    '''
        prints the statistics involving transformation

        Parameters:
        -----------
        None

        Return:
        -------
        None
    '''
    diff_nodes = 0
    diff_edges = 0
    vn = 0
    ve = 0
    number_trials = 1000

    for i in range(number_trials):
        inputs = random.choice([8,16,32,64])
        outputs = random.choice([8,16,32,64])
        node_number = inputs + outputs + random.randint(32, 128)
        circuit = bool_circ.random_circ_bool(node_number, inputs, outputs)
        node_number = len(circuit.get_nodes())
        edges_number = count_edges(circuit)
        
        circuit.transform_circuit()
        
        number_left_nodes = len(circuit.get_nodes())
        edges_left = count_edges(circuit)
        
        diff_nodes += node_number - number_left_nodes
        diff_edges += edges_number - edges_left
        
        vn += (node_number - number_left_nodes)**2
        ve += (edges_number - edges_left)**2

    moy_n = diff_nodes / number_trials
    moy_e = diff_edges / number_trials

    var_n = vn / number_trials - moy_n**2
    var_e = ve / number_trials - moy_e**2

    print(f"Average number of removed gates : {moy_n}")
    print(f"Variance : {var_n}, deviation : {np.sqrt(var_n)}")
    print(f"Average number of removed edges : {moy_e}")
    print(f"Variance : {var_e}, deviation : {np.sqrt(var_e)}")


## smallest of smallest paths between inputs and outputs of half_adder:
def shortest_path_input_output(n, half_):
    '''
        gets the smallest distance between an input and an output of either a half_adder or a CLA_adder

        Parameters:
        -----------
        half_ (boolean): specifies if we want a half_adder or a CLA_adder
        n (int): Level of adder (half/CLA _adder(n))

        Returns:
        --------
        minimal distance and input_id, output_id which have the shortest path from one to another
    '''
    if (half_):
        g = adders.half_adder(n)[0]
    else :
        g = adders.CLA_adder(n)
    
    smallest_dist = sys.maxsize
    input_id = -1
    output_id = -1
    for i in g.get_inputs_ids():
        for j in g.get_outputs_ids():
            dist = g.shortest_path(i,j)
            if dist<smallest_dist:
                smallest_dist = dist
                input_id = i
                output_id = j
    return smallest_dist,input_id,output_id


check_invarients()
print_stats()
