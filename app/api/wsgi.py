import re

from flask import Flask, request, jsonify
from functools import wraps
from ..solver.solver import Solver, SolverIO

app = Flask(__name__)


def bad_request(msg):
    return jsonify(code=400, error=msg), 400


def require_header(route):
    @wraps(route)
    def check_header(*args, **kwargs):
        if request.headers.get('Content-Type') == 'application/json':
            return route(*args, **kwargs)
        return bad_request("missing header: 'Content-Type: application/json'")

    return check_header


def validate_data(route):
    @wraps(route)
    def check_data(*args, **kwargs):
        base_msg = 'invalid request body'

        if not isinstance(request.json, list):
            return bad_request('{}: not a list'.format(base_msg))

        if len(request.json) != 81:
            return bad_request('{}: expected 81 list items, found {}'.format(base_msg, len(request.json)))

        for i in range(len(request.json)):
            if not (isinstance(request.json[i], str) and re.search('^$|^[1-9]$', request.json[i])):
                return bad_request('{}: bad list item: {}'.format(base_msg, request.json[i]))

        return route(*args, **kwargs)

    return check_data


@app.route('/', methods=['POST'])
@require_header
@validate_data
def solve():
    puzzle = SolverIO.from_list(request.json)
    solver = Solver(puzzle)

    if not solver.solve():
        return jsonify(code=200, result='no solution')

    solution = SolverIO.to_list(solver.get_board())
    return jsonify(code=200, result=solution)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
