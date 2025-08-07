from pysat.solvers import Glucose3
from pysat.formula import CNF
import math

global n, k, wx, wb
def get_x_var(i,j):
    """Get variable for X_i"""
    # i from 1 to n, j from 1 to wx
    return wx*(i-1) + j

def get_b_var(i, j, s):
    """
    Get variable for B_{i,j,s}
    """
    def window_aux_count(wx, k):
        if wx <= k+1:
            return wx*(wx+1)//2
        else:
            return (k+1)*(k+2)//2 + (wx - (k+1))*(k+1)
    
    window_offset = (i-1) * window_aux_count(wx, k)
    

    if j <= k+1:
        pos_offset = j*(j-1)//2
    else:
        pos_offset = (k+1)*k//2 + (j - (k+1))*(k+1)
    
    # Offset cho biến gốc
    return n*wx + window_offset + pos_offset + s
def get_num_block(n, wb):
    """
    Get the number of blocks
    """
    return 2* math.ceil(n / wb)-2

def get_r_var(i, j, s):
    """
    Get variable for R_{i,j,s}
    i: chỉ số block (1-based, 1..num_block)
    j: vị trí trong block (1-based, 1..wb)
    s: số lượng 1 đã đếm được (1..min(k+1, j*wx))
    """
    # Offset cho biến gốc và biến B
    if wx <= k+1:
        offset_r = n * wx + n * (wx*(wx+1)//2)
    else:
        offset_r = n * wx + n * ((k+1)*(k+2)//2 + (wx-k-1)*(k+1))

    # Tổng số biến phụ R trước block i
    total_r_per_block = 0
    for block in range(1, i):
        for jj in range(1, wb+1):
            total_r_per_block += min(k+1, jj*wx)
    block_offset = total_r_per_block

    # Tổng số biến phụ R trước vị trí j trong block hiện tại
    pos_offset = 0
    for jj in range(1, j):
        pos_offset += min(k+1, jj*wx)

    return offset_r + block_offset + pos_offset + s
    
def encode_sc_for_b(cnf, n, k, wx):
    """
    Encode the constraints for B variables.
    """
     # Formula (1): Xi,j → Bi,j,1 for i = 1 to n, j = 1 to wx
    for i in range(1, n+1):
        for j in range(1, wx+1):
            Xij = get_x_var(i, j)
            Bij1 = get_b_var(i, j, 1)
            cnf.append([-Xij, Bij1])
    # Formula (2): Bi,j-1,s → Bi,j,s for i = 1 to n, j = 2 to wx, s = 1 to min(j-1, k+1)
    for i in range(1, n+1):
        for j in range(2, wx+1):
            for s in range(1, min(j-1, k+1)+1):
                Bij_prev_s = get_b_var(i, j-1, s)
                Bij_s = get_b_var(i, j, s)
                cnf.append([-Bij_prev_s, Bij_s])
    # Formula (3): Xi,j ∧ Bi,j-1,s-1 → Bi,j,s for i = 1 to n, j = 2 to wx, s = 2 to min(j, k+1)
    for i in range(1, n+1):
        for j in range(2, wx+1):
            for s in range(2, min(j, k+1)+1):
                Xij = get_x_var(i, j)
                Bij_prev_s_minus_1 = get_b_var(i, j-1, s-1)
                Bij_s = get_b_var(i, j, s)
                cnf.append([-Xij, -Bij_prev_s_minus_1, Bij_s]) 



def check():
    for i in range(1, n+1):
        for j in range(1, wx+1):
            print(f"Checking X_{i},{j} {get_x_var(i,j)}")
    for i in range(1, n+1):
        for j in range(1, wx+1):
            for s in range(1, min(j, k+1)+1):  # s chạy từ 1 đến min(j, k+1)
                print(f"Checking B_{i},{j},{s} {get_b_var(i,j,s)}")
    for i in range (1,get_num_block(n, wb)+1):
        for j in range(1, wb+1):
            for s in range(1, min(j*wx, k+1)+1):
                print(f"Checking R_{i},{j},{s} {get_r_var(i,j,s)}")


def find_all_solutions(n,k,wx,wb):
    cnf = CNF()
    encode_sc_for_b(cnf, n, k, wx)
    check()
    if(wb ==1 and n == 1):
        cnf.append([-get_b_var(1,wx,k+1)])
    solutions = []
    solver = Glucose3()
    
    # Add all clauses to solver
    for clause in cnf.clauses:
        print(f"Adding clause: {clause}")
        solver.add_clause(clause)
    
    # Find all solutions iteratively
    while solver.solve():
        # Get current solution (only original variables X1 to Xn)
        model = solver.get_model()
        solution = []
        
        for i in range(1, wx*n+1):
            if i in model:
                solution.append('1')
            else:
                solution.append('0')
        
        solution_str = ''.join(solution)
        solutions.append(solution_str)
        
        # Add blocking clause to exclude this solution
        blocking_clause = []
        for i in range(1, wx*n+1):
            if i in model:
                blocking_clause.append(-i)
            else:
                blocking_clause.append(i)
        solver.add_clause(blocking_clause)
    
    solver.delete()
    return solutions


def main():
    global n, k, wx, wb
    print("Enter n, k, wx, wb:")
    n, k, wx ,wb = map(int, input().split())
    solutions = find_all_solutions(n, k, wx, wb)
    for i,sol in enumerate(solutions):
        print(f"Solution {i+1}: {sol}")

if __name__ == "__main__":
    main()

