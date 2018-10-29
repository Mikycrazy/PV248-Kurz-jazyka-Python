import sys
import numpy as np
import re
import math

def parse_equation(test_str):
    parts = test_str.split(' = ')
    if len(parts) != 2:
        return {}

    constant = int(parts[1])

    left = parts[0]
    regex = r"([+-]?)\s*([\d]*)([a-z])"
    matches = re.finditer(regex, left)
    variables = {'':constant}
    for match in matches:
        sign = match.group(1)
        coeficient = int(match.group(2)) if match.group(2).isdigit() else 1
        variable = match.group(3)
        if sign == '-':
            coeficient *= -1

        if len(variable.strip()) > 0:
            variables[variable] = coeficient

    return variables

def side_values(num_list):
    results_list = sorted(num_list)
    return results_list[0], results_list[-1]  


if len(sys.argv) < 2:
    exit("Too less arguments calling script")

input_file = sys.argv[1]

lines = []
with open(input_file, mode='r') as f:
    lines = [line.strip() for line in f.readlines()]

equations = [parse_equation(line) for line in lines]
variables = list()
for eq in equations:
    variables_chars_numbers = [ ord(key) for key in eq.keys() if len(key) > 0]
    variables = list(set(variables) | set(variables_chars_numbers))

""" min, max = side_values(merged)

variables = [chr(x) for x in range(min, max + 1)] """
variables = [chr(x) for x in sorted(variables)]

coeficient = [[(eq[x] if x in eq.keys() else 0) for x in variables] for eq in equations]
constant = [eq[''] for eq in equations]
a = np.array(coeficient)
b = np.array(constant)

m = np.asmatrix(a)
c = np.column_stack((m, b))
rank_a = np.linalg.matrix_rank(np.asmatrix(a))
rank_c = np.linalg.matrix_rank(c)

for line in lines:
    print(line)
    
if rank_a == rank_c:
    if rank_a == len(variables):
        solutions = np.linalg.solve(a, b)
        solutions_str = [variable + " = " + str(solutions[idx]) for idx, variable in enumerate(variables)]
        print("solution: " + ', '.join(solutions_str))
    elif rank_a < len(variables):
        print("solution space dimension: " + str(len(variables) - rank_a))
else:
    print("no solution")