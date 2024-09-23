from pysat.solvers import Solver
import math
# position number at row i and column j from left to right and top to bottom
def position(i, j, N):
    return i*N+j+1
# cnf formula for at most one queen
def coordinates(pos,column_count):
    y = math.floor(pos/column_count)
    x = pos % column_count
    return x,y

def at_most_one(list,vars):
    clauses = []
    row_count=math.ceil(math.sqrt(len(list)))
    column_count=math.ceil(len(list)/row_count)
    row_vars = [i for i in range (len(vars)+1,len(vars)+1+row_count)]
    vars.extend(row_vars)
    column_vars = [i for i in range (len(vars)+1,len(vars)+1+column_count)]
    vars.extend(column_vars)
    for i,x in enumerate(row_vars):
        for y in row_vars[i+1:]:
            clauses.append([-x,-y])
    for i,x in enumerate(column_vars):
        for y in column_vars[i+1:]:
            clauses.append([-x,-y])
    for i in range (len(list)):
        x,y=coordinates(i,column_count)
        clauses.append([-list[i],row_vars[y]])
        clauses.append([-list[i],column_vars[x]])

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