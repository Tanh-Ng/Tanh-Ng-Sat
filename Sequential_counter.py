from pysat.solvers import Glucose3
from pysat.formula import CNF

def atmost_k_simple_negation(n, k):
    """
    At Most K encoding using simple negation approach:
    Build counter up to k+1, then forbid having k+1 ones with single constraint ¬Rn,k+1
    """
    cnf = CNF()
    
    # Variable mapping: Xi = i (1 to n)
    # Auxiliary variables Ri,j = n + (i-1)*(k+1) + j
    def get_aux_var(i, j):
        return n + (i-1) * (k+1) + j
    
    print(get_aux_var(1,2))
    
    # Formula (1): Xi → Ri,1 for i = 1 to n
    for i in range(1, n+1):
        xi = i
        ri1 = get_aux_var(i, 1)
        cnf.append([-xi, ri1])  # Xi → Ri,1 ≡ ¬Xi ∨ Ri,1
    
    # Formula (2): Ri-1,j → Ri,j for i = 2 to n, j = 1 to min(i-1, k+1)
    for i in range(2, n+1):
        for j in range(1, min(i, k+2)):  # j from 1 to k+1
            ri_prev_j = get_aux_var(i-1, j)
            ri_j = get_aux_var(i, j)
            cnf.append([-ri_prev_j, ri_j])  # Ri-1,j → Ri,j
    
    # Formula (3): Xi ∧ Ri-1,j-1 → Ri,j for i = 2 to n, j = 2 to min(i, k+1)
    for i in range(2, n+1):
        for j in range(2, min(i+1, k+2)):  # j from 2 to k+1
            xi = i
            ri_prev_j_minus_1 = get_aux_var(i-1, j-1)
            ri_j = get_aux_var(i, j)
            # Xi ∧ Ri-1,j-1 → Ri,j ≡ ¬Xi ∨ ¬Ri-1,j-1 ∨ Ri,j
            cnf.append([-xi, -ri_prev_j_minus_1, ri_j])
    
    # Formula (4): Single constraint ¬Rn,k+1 (forbid having k+1 ones)
    if n > k+1:
        r_final_k_plus_1 = get_aux_var(n, k+1)
        cnf.append([-r_final_k_plus_1])  # ¬Rn,k+1
    
    return cnf

def find_all_solutions(n, k):
    """Find all satisfying assignments for At Most K constraint"""
    cnf = atmost_k_simple_negation(n, k)
    
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
        
        for i in range(1, n+1):
            if i in model:
                solution.append('1')
            else:
                solution.append('0')
        
        solution_str = ''.join(solution)
        solutions.append(solution_str)
        
        # Add blocking clause to exclude this solution
        blocking_clause = []
        for i in range(1, n+1):
            if i in model:
                blocking_clause.append(-i)
            else:
                blocking_clause.append(i)
        solver.add_clause(blocking_clause)
    
    solver.delete()
    return sorted(solutions)

def main():
    print("=== At Most K Constraint - Simple Negation Encoding ===")
    print("Finds all binary strings with at most k ones")
    print("Encoding: Build counter to k+1, then add single constraint ¬Rn,k+1")
    print()
    
    try:
        n = int(input("Enter n (string length): "))
        k = int(input("Enter k (max number of 1s): "))
        
        if n <= 0 or k < 0:
            print("Error: n must be positive, k must be non-negative")
            return
            
        if k >= n:
            print(f"Note: k >= n, all {2**n} possible strings satisfy the constraint")
        
        print(f"\nFinding all binary strings of length {n} with at most {k} ones...")
        
        solutions = find_all_solutions(n, k)
        
        print(f"\nFound {len(solutions)} solutions:")
        print("-" * 50)
        
        for i, sol in enumerate(solutions, 1):
            ones_count = sol.count('1')
            print(f"{i:3d}. {sol} ({ones_count} ones)")
        
        print("-" * 50)
        print(f"Total: {len(solutions)} solutions")
        
        # Calculate expected count: C(n,0) + C(n,1) + ... + C(n,k)
        from math import comb
        expected = sum(comb(n, i) for i in range(min(k+1, n+1)))
        print(f"Expected: {expected} solutions")
        
        if len(solutions) == expected:
            print(" Correct number of solutions!")
        else:
            print(" Incorrect solution count!")
            
    except ValueError:
        print("Error: Please enter valid integers")
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()