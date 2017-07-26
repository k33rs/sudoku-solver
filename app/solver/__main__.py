import fileinput

from .solver import Solver, SolverIO

filein = fileinput.input()
cells = SolverIO.from_file(filein)
solver = Solver(cells)

print("puzzle")
print(solver)

if solver.solve():
    print("solution")
    print(solver)
else:
    print("no solution")
