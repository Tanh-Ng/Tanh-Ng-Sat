from pysat.solvers import Glucose3
from pysat.formula import CNF
import math
import time

global n, k, wx, wb ,t, noc,nov
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

def encode_sc_for_each_block(cnf, n, k, wx, wb):
    """
    Encode the constraints for R variables in each block.
    """
    num_block = get_num_block(n, wb)

    def get_bi_in_block(i, j):
        """
        Get variable for B_{i,j,s} in block i
        """
        if(i == 1):
            return wb - j + 1
        if (i==2):
            return wb + j
        if(i % 2== 1):
            return get_bi_in_block(1, j) + wb*(i-1)/2
        return get_bi_in_block(2, j) + wb*(i-2)/2
    
    #Bi_wx_s -> R_i,j,s
    for i in range(1, num_block + 1):
        for j in range(1, wb+1):
            for s in range(1, min(wx, k+1)+1):
                bi = get_bi_in_block(i, j)
                Bbi_wx_s= get_b_var(bi, wx, s)
                Rijs = get_r_var(i, j, s)
                cnf.append([-Bbi_wx_s, Rijs])
        
    #R_i,j-1,s -> R_i,j,s
        for j in range(2, wb+1):
            for s in range(2, min(wx*(j-1), k+1)+1):
                Rij_prev_s = get_r_var(i, j-1, s)
                Rijs = get_r_var(i, j, s)
                cnf.append([-Rij_prev_s, Rijs])

    #Bi_wx_sb ∧ R_i,j-1,sr → R_i,j,sb+sr
        for j in range(2, wb+1):
            for sb in range(1, min(wx, k+1)+1):
                    for sr in range(1, min((j-1)*wx, k+1)+1):
                        if(sb+sr <= k+1 and sb + sr <= j*wx):
                            bi = get_bi_in_block(i, j)
                            Bbi_wx_sb = get_b_var(bi, wx, sb)
                            Rij_prev_sr = get_r_var(i, j-1, sr)
                            Rijs = get_r_var(i, j, sb + sr)
                            cnf.append([-Bbi_wx_sb, -Rij_prev_sr, Rijs])
        if(i%2==0 or i==1):
            cnf.append([-get_r_var(i, wb, k+1)])  # Forbid having k+1 ones in the last position of even blocks
        
def block_connection(cnf, n, k, wx, wb):
    num_block = get_num_block(n, wb)
    for i in range(1, num_block):  # nối block i với i+1
        for j1 in range(1, wb+1):
            j2 = wb - j1 + 1
            for s1 in range(1, min(j1*wx, k+1) + 1):
                for s2 in range(1, min(j2*wx, k+1) + 1):
                    if s1 + s2 > k:
                        cnf.append([
                            -get_r_var(i, j1, s1),
                            -get_r_var(i+1, j2, s2)
                        ])



def get_input():
    global n, k, wx, wb
    print("Enter n, k, wx, wb:")
    n, k, wx ,wb = map(int, input().split())
    if(n < 1 or k < 0 or wx < 1 or wb < 1):
        raise ValueError("Invalid input values. Ensure n >= 1, k >= 0, wx >= 1, and wb >= 1.")
    return n, k, wx, wb

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
    global t, noc, nov
    t = 0
    cnf = CNF()
    encode_sc_for_b(cnf, n, k, wx)
    encode_sc_for_each_block(cnf, n, k, wx, wb)
    block_connection(cnf, n, k, wx, wb)
    check()
    if(wb ==1 and n == 1):
        cnf.append([-get_b_var(1,wx,k+1)])
    solutions = []
    solver = Glucose3()
    
    # Add all clauses to solver
    for clause in cnf.clauses:
        print(f"Adding clause: {clause}")
        solver.add_clause(clause)
        print(f"Số biến (vars): {solver.nof_vars()}")
        print(f"Số mệnh đề (clauses): {solver.nof_clauses()}")

        
    # Find all solutions iteratively
    start_time = time.perf_counter()
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
    end_time = time.perf_counter()
    t = end_time - start_time
    noc = solver.nof_clauses()
    nov = solver.nof_vars()
    
    solver.delete()
    return solutions


def main():
    get_input()
    solutions = find_all_solutions(n, k, wx, wb)
    for i,sol in enumerate(solutions):
        print(f"Solution {i+1}: {sol}")

        print(f"Total time: {t:.4f} seconds")
        print(f"Number of clauses: {noc}") 
        print(f"Number of variables: {nov}")

main()
