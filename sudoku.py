import sys
import logic
import logic_extra
import string
import time

def tryOr(a, b):
    if not a:
        return b
    return a | b
def tryAnd(a, b):
    if not a:
        return b
    return a & b

def atLeastOne(expressions) :
    r = None
    for e in expressions:
        r = tryOr(r, e)
    return r

def atMostOne(expressions) :
    r = None
    for e1 in expressions:
        for e2 in expressions:
            if e1 is e2:
                continue
            r = tryAnd(r, ~e1 | ~e2)
    return r

def exactlyOne(expressions) :
    return atMostOne(expressions) & atLeastOne(expressions)

symbols = [[[logic.Expr("C[{0},{1},{2}]".format(i, j, n)) for n in xrange(9)] for j in xrange(9)] for i in xrange(9)]

def rules():
    s = set()
    # Exclusion in each small square
    for i in xrange(9):
        for j in xrange(9):
            s.add(exactlyOne(symbols[i][j]))
    # All numbers must present in each big square
    for li in xrange(3):
        for lj in xrange(3):
            for n in xrange(9):
                e = None
                for si in xrange(3):
                    for sj in xrange(3):
                        e = tryOr(e, symbols[li * 3 + si][lj * 3 + sj][n])
                s.add(e)
    # All numbers must present in each row / col
    for i in xrange(9):
        for n in xrange(9):
            row = None
            col = None
            for j in xrange(9):
                row = tryOr(row, symbols[i][j][n])
                col = tryOr(col, symbols[j][i][n])
            s.add(row)
            s.add(col)
    return s

def print_sudoku(symbol_dict):
    print_str = ""
    row_breaker = "------+-" * 3
    row_breaker = row_breaker[:-3] + "\n"
    for i in xrange(9):
        if i == 3 or i == 6:
            print_str += row_breaker
        for j in xrange(9):
            if j == 3 or j == 6:
                print_str += "| "
            is_num = False
            for n in xrange(9):
                if symbols[i][j][n] in symbol_dict and symbol_dict[symbols[i][j][n]]:
                    print_str += "{0} ".format(n + 1)
                    is_num = True
                    break
            if not is_num:
                print_str += ". "
        print_str = print_str[:-1] + "\n"
    print print_str

def solve(sudoku_str):
    sudoku_str = sudoku_str.translate(None, "\n")
    assert len(sudoku_str) == 81, "Invalid problem"
    t_0 = time.clock()
    s = rules()
    problem_dict = dict()
    row = 0
    col = 0
    for c in sudoku_str:
        if c in string.digits[1:]:
            problem_dict[symbols[row][col][int(c) - 1]] = True
            s.add(symbols[row][col][int(c) - 1])
        col += 1
        if col == 9:
            col = 0
            row += 1
    print "Problem:"
    print_sudoku(problem_dict)
    for e in s:
        assert logic_extra.is_valid_cnf(e)
    t_prep_done = time.clock()
    solution_dict = logic.pycoSAT(s)
    t_solve_done = time.clock()
    assert solution_dict, "No valid solution"
    print "Solution:"
    print_sudoku(solution_dict)
    print "Expression Build + Sanity Check: {0:.2f}s\nSolving: {1:.2f}s\n{2}\nTotal: {3:.2f}s".format(t_prep_done - t_0, t_solve_done - t_prep_done, "-" * 15, t_solve_done - t_0)

