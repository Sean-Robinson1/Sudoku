from tkinter import *
from time import time
from solver import *

numbers = ['1','2','3','4','5','6','7','8','9']
squaresTemplate = ["0" * 9 for _ in range(9)]

class SudokuGUI:
    def __init__(self, main: Tk) -> None:
        self.showBruteForce = False
        self.currentBox = 0
        self.boxes = {}
        boxNum = 0
        for column in range(0, 360, 40):
            for row in range(70, 430, 40):
                grid = Button(main,justify = 'center',font = 30,command = lambda num=boxNum: choice.set(num))
                grid.place(x = row, y = column, width=40, height=40)
                self.boxes[boxNum] = grid
                boxNum += 1

        #creating stronger lines to easily show boxes
        for xcoord in [70,190,310,430]:
            vertical = Frame(main, bg='black', height=360,width=1)
            vertical.place(x=xcoord,y=0)

        for ycoord in [0,120,240,360]:
            horizontal = Frame(main, bg='black', height=1,width=360)
            horizontal.place(x=70,y=ycoord)

    def enterData(self,event: Event = None) -> None:
        self.resetBoard()
        newSquares = squaresTemplate
        squares = {}
        squaresFound = {}
        linesString = []
        for i in range(9):
            tempStr = ''
            for ii in range(9):
                box = self.boxes[i*9+ii].cget('text')
                if box not in numbers:
                    tempStr += '0'
                else:
                    tempStr += box
            linesString.append(tempStr)

        for i in range(81):
            squares[i] = {1,2,3,4,5,6,7,8,9}
        
        for i in range (9):
            line = linesString[i]
            for ii in range(len(line)):
                if line[ii] != '0':
                    squares[i * 9 + ii] = {int(line[ii])}
                    squaresFound[i * 9 + ii] = line[ii]

        initalNums = squaresFound
        start = time()
        squares = startLogicalSolve(squares)
        isSolved = True
        counter = 0
        newSquares = string2List(newSquares)
        for key,value in squares.items():
            if len(value) == 1:
                newSquares[counter // 9][counter % 9] = str(list(value)[0])
            else:
                isSolved = False
                
            counter += 1

        if self.checkObviousError(newSquares,squaresFound) == False:
            return

        if not isSolved:
            findSolution(self.boxes, newSquares,start)
            

        end = time()
        for row in newSquares:
            for square in row:
                print(square,' ',end = '')
            print('\n')
        print(f'This took {end-start} seconds')
            
        for i in range (9):
            for ii in range (9):
                self.boxes[i*9+ii].config(text = '')
                boxText = newSquares[i][ii]
                self.boxes[i*9+ii].config(text = boxText)

        for key,value in initalNums.items():
            self.boxes[key].config(fg = 'blue')

    def checkObviousError(self,newSquares: list[list[str]],squaresFound: dict[int, str]) -> bool:
        i = 0
        for row in newSquares:
            for num in range(1,10):
                if row.count(str(num)) > 1:
                    for ii in range(i, i + 9):
                        if newSquares[ii // 9][ii % 9] == str(num):
                            self.boxes[ii].config(bg = 'red')
                            print(ii)
                    main.update()
                    print('INVALID')
                    return False
            i += 9
                
        i = 0
        for column in range(9):
            columnStr = ''
            for row in range(9):
                columnStr += newSquares[row][column]
            for num in range(1,10):
                if columnStr.count(str(num)) > 1:
                    for ii in range(i, i + 73,9):
                        if newSquares[ii // 9][ii % 9] == str(num):
                            self.boxes[ii].config(bg = 'red')
                            print(ii)
                    main.update()
                    print('INVALID')
                    return False
            i += 1

        for key, value in squaresFound.items():
            tempList = boxFinder(key)
            boxValues = []
            for i in tempList:
                boxValues.append(newSquares[i // 9][i % 9])

            if boxValues.count(value) > 1:
                for i in tempList:
                    if newSquares[i // 9][i % 9] == value:
                        self.boxes[i].config(bg = 'red')
                        print(i)
                main.update()
                print('INVALID')
                return False
            
        return True

    def highlightSquares(self, num:int ) -> None:
        self.resetBoard()
        value = self.boxes[num].cget('text')
        for i in rowFinder(num):
            self.boxes[i].config(bg = 'light blue')
        for i in columnFinder(num):
            self.boxes[i].config(bg = 'light blue')
        for i in boxFinder(num):
            self.boxes[i].config(bg = 'light blue')

        self.boxes[num].config(bg = 'light green')

        for i in range(81):
            if self.boxes[i].cget('text') == value:
                self.boxes[i].config(fg = 'blue')

    def resetBoard(self) -> None:
        for i in range(len(self.boxes)):
            self.boxes[i].config(bg = 'white')
            self.boxes[i].config(fg = 'black')

    def moveLeft(self, event: Event) -> None:
        self.resetBoard()
        newBox = (self.currentBox - 1) % 81
        self.highlightSquares(newBox)
        self.currentBox = newBox

    def moveRight(self, event: Event) -> None:
        self.resetBoard()
        newBox = (self.currentBox + 1) % 81
        self.highlightSquares(newBox)
        self.currentBox = newBox

    def moveDown(self, event: Event) -> None:
        self.resetBoard()
        newBox = (self.currentBox + 9) % 81
        self.highlightSquares(newBox)
        self.currentBox = newBox

    def moveUp(self, event: Event) -> None:
        self.resetBoard()
        newBox = (self.currentBox - 9) % 81
        self.highlightSquares(newBox)
        self.currentBox = newBox

    def insertNum(self, event: Event) -> None:
        self.boxes[self.currentBox].config(text = str(event.char))
        self.highlightSquares(self.currentBox)

    def delete(self, event: Event) -> None:
        self.boxes[self.currentBox].config(text = '')

    def deleteAll(self, event: Event) -> None:
        self.resetBoard()
        for i in range(81):
            self.boxes[i].config(text = '')

def findSolution(boxes: list[Button], squares: list[list[str]], start: float, showBruteForce: bool = False) -> list[list[str]] | None:
    if findEmpty(squares) == None:
        end = time()
        print(f'This took {end - start} seconds.')
        for i in range (9):
            for ii in range (9):
                boxes[i*9+ii].config(text = '')
                boxText = squares[i][ii]
                boxes[i*9+ii].config(text =  boxText)

        for i in squares:
            for ii in i:
                print(ii,' ',end = '')
            print('\n')

        return squares
    else:
        row,column = findEmpty(squares)
        
    for i in range (1,10):
        if checkValue(squares,row,column,str(i)) == True:
            squares[row][column] = str(i)
            if showBruteForce == True:
                boxes[row*9+column].config(text = str(i))
            main.update()
            tempVar = findSolution(boxes, squares,start)
            if tempVar == False:
                squares[row][column] = '0'
                if showBruteForce == True:
                    boxes[row*9+column].config(text = '')
                main.update()
            else:
                return squares
    if showBruteForce == True:
        boxes[row*9+column].config(text = '')
    main.update()
    return False   

main = Tk()
main.geometry('500x400')

gui = SudokuGUI(main)
choice = IntVar()

main.bind("<Left>",gui.moveLeft)
main.bind("<Right>",gui.moveRight)
main.bind("<Up>",gui.moveUp)
main.bind("<Down>",gui.moveDown)
main.bind("<Return>",gui.enterData)
main.bind("<BackSpace>",gui.delete)
main.bind("<Escape>",gui.deleteAll)
for i in range(1,10):
    main.bind(str(i),gui.insertNum)

button = Button(text = 'SOLVE', bd = '5',command = gui.enterData)
button.pack(side = 'bottom')
while True:
    main.wait_variable(choice)
    gui.resetBoard()
    box = choice.get()
    gui.highlightSquares(box)
    gui.currentBox = box

main.mainloop()
