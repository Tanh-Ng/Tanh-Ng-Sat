from pysat.solvers import Solver
import math
# position number at row i and column j from left to right and top to bottom
def position(i, j, N):
    return i*N+j+1

# cnf formula for at most one queen
def at_most_one(list,vars):
    clauses = []
    new_var_count=len(list)-1
    encode_list = [i for i in range (len(vars)+1,len(vars)+1+new_var_count)]
    vars.extend(encode_list)
    clauses.append([-list[0],encode_list[0]])
    for i in range (1,new_var_count):
        clauses.append([-encode_list[i-1],encode_list[i]])
        clauses.append([-list[i],encode_list[i]])
        clauses.append([-list[i],-encode_list[i-1]])
    clauses.append([-encode_list[new_var_count-1],-list[new_var_count]])
    return clauses

# cnf formula for exactly one queen
def exactly_one(list,vars):
    clauses = []
    clauses.append(list)
    clauses.extend(at_most_one(list,vars))
    return clauses

def generate_clauses(N):
    clauses = []
    vars = [i for i in range (1,N*N+1)]
# rows and columns
    for row in range(N):
        A = []
        B = []
        for  column in range(N):
            A.append(position(row,column,N))
            B.append(position(column,row,N))
        # number *row row
        print("cnf clause for row number",row+1,"from top to bottom")
        temp = exactly_one(A,vars)
        for clause in temp:
            clauses.append(clause)
            print(clause)
        # number *row column
        print("cnf clause for column number",row+1,"from left to right")
        temp = exactly_one(B,vars)
        for clause in temp:
            clauses.append(clause)
            print(clause)
        
# top left -> mid positive diagonal
    print("cnf clause for positive diagonal from top to bottom")
    for column in range (1,N):
        A= []
        for x in range (column+1):
            A.append(position(x,column-x,N))
        temp = at_most_one(A,vars)
        for clause in temp:
            clauses.append(clause)
            print(clause)
        
# mid+1 -> bottom right positive diagonal
    for row in range (1,N-1):
        A= []
        for x in range (N-row):
            A.append(position(row+x,N-x-1,N))
        temp = at_most_one(A,vars)
        for clause in temp:
            clauses.append(clause)
            print(clause)

# top right -> mid negative diagonal
    print("cnf clause for negative diagonal from top to bottom")
    for column in range (N-2,-1,-1):
        A= []
        for x in range (N-column):
            A.append(position(x,column+x,N))
        temp = at_most_one(A,vars)
        for clause in temp:
            clauses.append(clause)
            print(clause)

# mid+1 -> bottom left negative diagonal
    for row in range(1,N-1):
        A = []
        for x in range (N-row):
            A.append(position(row+x,x,N))
        temp = at_most_one(A,vars)
        for clause in temp:
            clauses.append(clause)
            print(clause)
    return clauses

#add blocking clause generate other solutions
def add_blocking_clause(solver,queens_position):
    blocking_clause = [-pos for pos in queens_position]
    solver.add_clause(blocking_clause)

def solve_n_queens():
    N=int(input('enter the number of queens\n'))
    cnf_clauses = generate_clauses(N)
    solver = Solver(name='g3')
    for clause in cnf_clauses:
        solver.add_clause(clause)
    if solver.solve():
        while solver.solve():
            queens_position = []
            print ("Satisfiable")
            model = solver.get_model()
            print("Solution: ",model)
            for i in model:
                if abs(i)<=N*N:
                    if i>0 :
                        print("Q", end=' ')
                        queens_position.append(i)
                    else: print(".", end=' ')
                    if( abs(i)%N==0):
                        print (" ")
            add_blocking_clause(solver,queens_position)
    else: print ("Unsatisfiable")
solve_n_queens()