#  Generating Random Lists and Matrices  
import random
#3#
def random_int_list(n , bound):
    return [random.randint(0 , bound) for k in range(n)]
#3#
def random_int_matrix(n ,bound , null_diag = True, number_generator=(lambda : random.betavariate(1,5))):
    random.seed(number_generator)
    if not null_diag:
        return [random_int_list(n , bound) for k in range(n)]
    return [random_int_list(k , bound)+[0]+random_int_list(n-k-1 , bound) for k in range(n)]

#3#
def random_symetric_int_matrix(n , bound , null_diag = True, number_generator=(lambda : random.betavariate(1,5))):
    random.seed(number_generator)
    mat = [[0 for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i==j:
                mat[i][j] = int(not null_diag)* random.randint( 0,bound ) 
            else:
                v = random.randint(0,bound)
                mat[i][j] = v
                mat[j][i] = v
    return mat

#3#
def random_oriented_int_matrix(n , bound , null_diag = True, number_generator=(lambda : random.betavariate(1,5))):
    random.seed(number_generator)
    m = random_int_matrix(n , bound , null_diag=null_diag, number_generator=number_generator)
    for i in range(n):
        for j in range(n):
            if i<j and m[i][j] != 0 and m[j][i] != 0:
                if random.randint(0,1):
                    m[i][j] = 0
                else:
                    m[j][i] = 0
    return m

#3#
def random_dag_int_matrix(n,bound,null_diag=True, number_generator=2.5):
    random.seed(number_generator)
    mat = [[0 for j in range(n)] for i in range(n)]
    if random.randint(0,1):
        for i in range(n):
            for j in range(n):
                if i<=j:
                    mat[i][j]= int(not(null_diag and i==j))*random.randint(0,bound)
    else:
        for i in range(n):
            for j in range(n):
                if i<=j:
                    mat[j][i]= int(not(null_diag and i==j))*random.randint(0,bound)
    return mat

def print_m(m):
    print("[")
    for i in range(len(m)):
        print(m[i].__str__() + ",")
    print("]")



def identity_matrix(n):
    identity = [[0] * n for i in range(n)]
    for i in range(n):
        identity[i][i] = 1
    return identity

def copy_matrix(mat):
    return [row[:] for row in mat]

def degree_matrix(mat):
    """ Meant for adjacency matrices """
    res = copy_matrix(mat)
    for i in range(len(mat)):
        deg = 0 
        for j in range(len(mat)):
            deg += res[i][j]
        res[i][i] = deg
    return res

def laplacian(mat):
    return degree_matrix(mat) - mat

#Pivot de Gauss
def swap_rows(mat, row1, row2):
    mat[row1], mat[row2] = mat[row2], mat[row1]

def scale_row(mat, row, scalar):
    mat[row] = [scalar * element for element in mat[row]]

def add_scaled_row(mat, source_row, destination_row, scalar):
    scaled_row = [scalar * element for element in mat[source_row]]
    mat[destination_row] = [sum(pair) for pair in zip(mat[destination_row], scaled_row)]

def gauss(mat):
    n = len(mat)

    for pivot_row in range(n):
        if mat[pivot_row][pivot_row] == 0:
            for row_below in range(pivot_row + 1, n):
                if mat[row_below][pivot_row] != 0:
                    swap_rows(mat, pivot_row, row_below)
                    break
            else:
                continue  

        scale_row(mat, pivot_row, 1.0 / mat[pivot_row][pivot_row])

        for row_below in range(pivot_row + 1, n):
            if mat[row_below][pivot_row] != 0:
                add_scaled_row(mat, pivot_row, row_below, -mat[row_below][pivot_row])

def rank(mat):
    copy = copy_matrix(mat)
    gauss(copy)
    rank = sum(1 for row in copy if any(row))
    return rank

def kernel_dim(mat):
    return len(mat) - rank(mat)