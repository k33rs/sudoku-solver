# Sudoku Solver (9x9)

## Run the solver

    $ python3 -m app.solver puzzles/mepham

If no file is given, `stdin` is read:

    $ python3 -m app.solver

The algorithm can be found in the [pdf][1].

## Run the server

with Python (development only):

    $ python3 -m app.api

with Docker (recommended):

    $ docker build -t sudoku-solver .
    $ docker run -d --name sudoku-solver -p 5000:5000 sudoku-solver

[1]:https://github.com/k33rs/sudoku_solver/blob/master/crook.pdf
