from time import time
squares={}
squaresFound={}

ROW_LOOKUP = [[r*9 + c for c in range(9)] for r in range(9)]
COL_LOOKUP = [[c + 9*r for r in range(9)] for c in range(9)]
BOX_LOOKUP = []
for br in [0, 3, 6]:
    for bc in [0, 3, 6]:
        box = [ (br + r)*9 + (bc + c) for r in range(3) for c in range(3)]
        BOX_LOOKUP.append(box)


# some test sudokus
easyPractise = ["000004000",
             "913000000",
             "500610000",
             "007400005",
             "190050700",
             "005807600",
             "050906070",
             "041030020",
             "000020460"]

mediumPractise = ['000090060',
                  '000400003',
                  '004030200',
                  '081000000',
                  '970300804',
                  '050070020',
                  '240008600',
                  '008563000',
                  '006040000']

hardPractise = ['000098300',
                '000000010',
                '000700002',
                '005000006',
                '400005890',
                '300016000',
                '700030008',
                '090080063',
                '001400720']

easyPractise = ["000004000",
             "913000000",
             "500610000",
             "007400005",
             "190050700",
             "005807600",
             "050906070",
             "041030020",
             "000020460"]

expertPractise = ['960000100',
                  '080000070',
                  '050046900',
                  '030070005',
                  '000100060',
                  '700064080',
                  '000010036',
                  '093008000',
                  '002000000']

testPractise = ['987000000',
                  '000000000',
                  '000000000',
                  '000000000',
                  '000000000',
                  '000000000',
                  '000000000',
                  '000000000',
                  '000000000']

evilPractise = [  '090807400',
                  '005000060',
                  '000020000',
                  '000090200',
                  '600201040',
                  '010030000',
                  '900000007',
                  '070104800',
                  '000003000']

def string2List(stringList: list[str]) -> list[list]:
    '''
    Converts a list of strings to a list of lists.
    This changes between different ways of representing the grid.
    '''
    newList = []
    for i in range(0, 9):
        rowText = stringList[i]

        rowList = list(rowText)
        newList.append(rowList)
    return newList

###### SUDOKU SOLVING FUNCTIONS  ######

def findEmpty(squares: list[list]) -> tuple[int,int] | None:
    '''
    Finds the first empty cell in the grid.
    '''
    for row in range(9):
        for column in range(9):
            if squares[row][column] == "0":
                return row, column
    return None


def checkValue(squares: list[list], row:int, column:int, value:int) -> bool:
    '''
    Checks if an item can be placed in a certain cell
    does this by checking if any square in the same
    row, column or box shares the same value, and if
    so returns False. If not returns True.
    '''
    # check items in row
    for i in range(9):
        if squares[row][i] == value:
            return False
        
    # check items in column
    for i in range(9):
        try:
            if squares[i][column] == value:
                return False
        except:
            print(column)
          
    # check items in box
    startRow = (row // 3) * 3
    startColumn = (column // 3) * 3

    # iterating through squares in the box
    for i in range(startRow, startRow + 3):
        for ii in range(startColumn, startColumn + 3):
            if squares[i][ii] == value:
                return False
            
    return True


def bruteForce(squares: list[list]) -> bool:
    '''
    Tries to brute force a solution for the sudoku. Does this
    via backtracking.
    '''
    #checks if the sudoku is solved
    if findEmpty(squares) is None:
        return True

    # finds next empty cell
    try:
        row, column = findEmpty(squares)
    except:
        print(squares)
        print(findEmpty(squares))

    # iterates through all possible values for that cell and 
    # checks to see if they are possible
    for i in range(1, 10):
        if checkValue(squares, row, column, str(i)):
            squares[row][column] = str(i)
            tempVar = bruteForce(squares)
            if tempVar == False:
                squares[row][column] = "0"
            else:
                return True

    return False

def rowFinder(squareNum:int) -> list[int]:
    '''
    Calculates the row from the number of the square.
    Returns a list containing the indexes of the other
    cells in the row.
    '''
    rowNum = squareNum // 9
    return ROW_LOOKUP[rowNum]

def columnFinder(squareNum:int) -> list[int]:
    '''
    Calculates the column from the number of the square.
    Returns a list containing the indexes of the other
    cells in the column.
    '''
    columnNum = squareNum % 9
    return COL_LOOKUP[columnNum]

def boxFinder(squareNum:int) -> list[int]:
    '''
    Calculates the box from the number of the square.
    Returns a list containing the indexes of the other
    cells in the box.
    '''
    r, c = squareNum // 9, squareNum % 9
    boxIndex = (r // 3) * 3 + (c // 3)
    return BOX_LOOKUP[boxIndex]


def updateCell(squareNum:int, squares:dict) -> dict:
    '''
    If a cell becomes solved (you know which value it takes) this function
    updates all cells in that cell's row, column and box, removing the value
    from the values they can take. If that cell then becomes solved it calls
    update on that cell.
    '''
    for x in squares[squareNum]: 
        squareValue = x

    # updating rows
    for i in rowFinder(squareNum):
        if squareValue in squares[i] and len(squares[i]) > 1:
            squares[i].remove(squareValue)
            if len(squares[i]) == 1:
                squares = updateCell(i, squares)

    # updating columns
    for i in columnFinder(squareNum):
        if squareValue in squares[i] and len(squares[i]) > 1:
            squares[i].remove(squareValue)
            if len(squares[i]) == 1:
                squares = updateCell(i, squares)

    # updating boxes
    for i in boxFinder(squareNum):
        if squareValue in squares[i] and len(squares[i]) > 1:
            squares[i].remove(squareValue)
            if len(squares[i]) == 1:
                squares = updateCell(i, squares)

    # calls indirect update
    squares = checkHiddenSingles(squares)

    return squares


def checkHiddenSingles(squares:dict) -> None:
    '''
    Checks for hidden singles in rows, boxes and columns. A hidden
    single is where only one cell in a row, box or column can take
    a specific value.
    '''

    for row in range(9):
        letterCount = {
            1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        
        # finds all cells in the row and counts how many times each number
        # appears
        for squareNum in rowFinder(row * 9):
            for poss in squares[squareNum]:
                letterCount[poss].append(squareNum)

        # if a value only appears once, the cell that contains that value
        # must be set to contain it, if it is not already solved.
        for key, value in letterCount.items():
            if len(value) == 1 and len(squares[value[0]]) != 1:
                squares[value[0]] = {key}
                squares = updateCell(value[0], squares)

    # next two work with exactly the same logic

    for col in range(9):
        letterCount = {
            1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        
        for squareNum in columnFinder(col):
            for poss in squares[squareNum]:
                letterCount[poss].append(squareNum)

        for key, value in letterCount.items():
            if len(value) == 1 and len(squares[value[0]]) != 1:
                squares[value[0]] = {key}
                squares = updateCell(value[0], squares)

    for i in range(9):
        boxStarts = [0, 3, 6, 27, 30, 33, 54, 57, 60]
        box = boxStarts[i]
        letterCount = {
            1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
        
        for squareNum in boxFinder(box):
            for poss in squares[squareNum]:
                letterCount[poss].append(squareNum)

        for key, value in letterCount.items():
            if len(value) == 1 and len(squares[value[0]]) != 1:
                squares[value[0]] = {key}
                squares = updateCell(value[0], squares)

    return squares

# this function was where i planned on adding a lot more 
# of the more niche methods of solving a sudoku (such as 
# X-wing or Y-wing methods) if i ever implemented them
# but after some testing, i found that to a large extent
# it was faster to just brute force than it was to test
# a huge amount of very uncommon edge cases.
def checkNicheMethods(squares:dict) -> dict:
    '''
    Tries to solve the sudoku using more niche methods.
    This might include techniques such as checking for
    two squares with values making a pair, or only one
    value appearing in a row, box or column.
    '''
    # checking hidden singles
    checkHiddenSingles(squares)

    return squares


def startLogicalSolve(squares:dict) -> dict:
    '''
    Begins solve by attempting to solve the sudoku like a human might
    (no brute force, just logical methods). This is not advanced enough
    to actually solve harder sudokus, but can usually get enough to 
    make the brute force much faster, by reducing the number of possible
    branches.
    '''

    #calls update on all known starting cells
    for squareSet in squares:
        if len(squares[squareSet]) == 1:
            result = updateCell(squareSet, squares)
            if result:
                squares = result 

    return squares

def makeList(x):
    output = []
    for i in range (0,81,9):
        output.append(x[i:i+9])
    return output

def solve(sudoku):
    squares = {i: {1,2,3,4,5,6,7,8,9} for i in range(81)}

    squaresFound={}

    for i, line in enumerate(sudoku):
        for j, ch in enumerate(line):
            if ch != '0':
                squares[i*9 + j] = {int(ch)}
                squaresFound[i*9 + j] = ch

    squares = startLogicalSolve(squares)

    solved = True
    counter = 0
    newSquares = string2List(["0"*9 for _ in range(9)])

    for value in squares.values():
        if len(value) == 1:
            newSquares[counter // 9][counter % 9] = str(list(value)[0])
        else:
            solved = False
            
        counter += 1

    if solved:
        return newSquares

    bruteForce(newSquares)
            
    return newSquares


if __name__ == "__main__":
    difficulty = input('Would you like to run: [e]asy, [m]edium, [h]ard or [v]ery hard? ')
    if difficulty[0].lower() == 'e':
        linesString = easyPractise
    elif difficulty[0].lower() == 'm':
        linesString = mediumPractise
    elif difficulty[0].lower() == 'h':
        linesString = hardPractise
    elif difficulty[0].lower() == 'v':
        linesString = expertPractise
    elif difficulty[0].lower() == 's':
        linesString = evilPractise
    else:
        linesString = makeList(difficulty)

    start = time()
    
    solved = solve(linesString)

    end = time()
    for row in solved:
        for square in row:
            print(square,' ',end = '')
        print('\n')
    print(f'This took {end-start} seconds')
    
            


