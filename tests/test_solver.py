import copy

import pytest

import solver
from solver import (
    boxFinder,
    bruteForce,
    checkValue,
    columnFinder,
    findEmpty,
    makeList,
    rowFinder,
    solve,
    startLogicalSolve,
    string2List,
)

PUZZLES = {
    "easy": solver.easyPractise,
    "medium": solver.mediumPractise,
    "hard": solver.hardPractise,
    "expert": solver.expertPractise,
    "evil": solver.evilPractise,
    "sparse": solver.testPractise,
    "empty": ["0" * 9 for _ in range(9)],
}

DIGITS = set("123456789")


def assertValidSolution(grid: list[list[str]], puzzle: list[str]) -> None:
    '''
    Checks every row, column and box contains 1-9 exactly once and that
    the solution keeps all of the puzzle's given digits.
    '''
    assert len(grid) == 9 and all(len(row) == 9 for row in grid)

    for i in range(9):
        assert set(grid[i]) == DIGITS, f"row {i} invalid: {grid[i]}"
        assert {grid[r][i] for r in range(9)} == DIGITS, f"column {i} invalid"

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = {grid[br + r][bc + c] for r in range(3) for c in range(3)}
            assert box == DIGITS, f"box at ({br}, {bc}) invalid"

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != "0":
                assert grid[r][c] == puzzle[r][c], f"given at ({r}, {c}) changed"


def candidatesFromPuzzle(puzzle: list[str]) -> dict[int, set[int]]:
    squares = {i: {1, 2, 3, 4, 5, 6, 7, 8, 9} for i in range(81)}
    for r, line in enumerate(puzzle):
        for c, ch in enumerate(line):
            if ch != "0":
                squares[r * 9 + c] = {int(ch)}
    return squares


###### GRID CONVERSION ######

def testString2ListSplitsRowsIntoCharacters():
    grid = string2List(solver.easyPractise)
    assert len(grid) == 9
    assert grid[1] == list("913000000")


def testMakeListSplitsFlatStringIntoRows():
    flat = "".join(solver.hardPractise)
    assert makeList(flat) == solver.hardPractise


###### CELL LOOKUPS ######

def testRowFinder():
    assert rowFinder(0) == list(range(9))
    assert rowFinder(40) == list(range(36, 45))


def testColumnFinder():
    assert columnFinder(0) == list(range(0, 81, 9))
    assert columnFinder(40) == list(range(4, 81, 9))


def testBoxFinder():
    assert boxFinder(0) == [0, 1, 2, 9, 10, 11, 18, 19, 20]
    assert boxFinder(40) == [30, 31, 32, 39, 40, 41, 48, 49, 50]
    assert boxFinder(80) == [60, 61, 62, 69, 70, 71, 78, 79, 80]


@pytest.mark.parametrize("cell", range(81))
def testEveryCellLookupContainsItself(cell):
    assert cell in rowFinder(cell)
    assert cell in columnFinder(cell)
    assert cell in boxFinder(cell)


###### FIND EMPTY / CHECK VALUE ######

def testFindEmptyReturnsFirstEmptyCell():
    grid = string2List(solver.easyPractise)
    assert findEmpty(grid) == (0, 0)
    grid[0][:3] = ["1", "2", "3"]
    assert findEmpty(grid) == (0, 3)


def testFindEmptyReturnsNoneWhenFull():
    assert findEmpty(solve(solver.easyPractise)) is None


def testCheckValueRejectsRowConflict():
    grid = string2List(solver.easyPractise)
    # row 1 is "913000000"
    assert not checkValue(grid, 1, 5, "9")


def testCheckValueRejectsColumnConflict():
    grid = string2List(solver.easyPractise)
    # column 0 contains 9 (row 1), 5 (row 2), 1 (row 4)
    assert not checkValue(grid, 0, 0, "5")


def testCheckValueRejectsBoxConflict():
    grid = string2List(solver.easyPractise)
    # top-left box contains 9, 1, 3, 5 - 3 is not in row 0 or column 2
    assert not checkValue(grid, 0, 2, "3")


def testCheckValueAllowsValidPlacement():
    grid = string2List(solver.easyPractise)
    assert checkValue(grid, 0, 0, "2")


###### LOGICAL SOLVE ######

@pytest.mark.parametrize("name", PUZZLES)
def testLogicalSolveOnlyNarrowsCandidates(name):
    '''
    The logical solve must never remove the correct value from a cell,
    so the known solution must still be a candidate everywhere.
    '''
    puzzle = PUZZLES[name]
    solution = solve(puzzle)
    squares = startLogicalSolve(candidatesFromPuzzle(puzzle))

    for cell, candidates in squares.items():
        assert candidates, f"cell {cell} has no candidates"
        assert int(solution[cell // 9][cell % 9]) in candidates


def testLogicalSolveFullySolvesEasyPuzzle():
    squares = startLogicalSolve(candidatesFromPuzzle(solver.easyPractise))
    assert all(len(candidates) == 1 for candidates in squares.values())


###### BRUTE FORCE ######

def testBruteForceSolvesInPlace():
    grid = string2List(solver.hardPractise)
    assert bruteForce(grid) is True
    assertValidSolution(grid, solver.hardPractise)


def testBruteForceReturnsFalseForUnsolvableGrid():
    # the last cell of row 0 can only be 9, but column 8 already has a 9
    puzzle = ["123456780", "000000009"] + ["0" * 9] * 7
    grid = string2List(puzzle)
    original = copy.deepcopy(grid)

    assert bruteForce(grid) is False
    assert grid == original


###### FULL SOLVE ######

@pytest.mark.parametrize("name", PUZZLES)
def testSolveProducesValidSolution(name):
    puzzle = PUZZLES[name]
    assertValidSolution(solve(puzzle), puzzle)


def testSolveDoesNotMutateInput():
    puzzle = list(solver.mediumPractise)
    solve(puzzle)
    assert puzzle == solver.mediumPractise
