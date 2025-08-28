import cv2
import re
import os
import sys
import pytesseract
from dotenv import load_dotenv
from imutils import grab_contours
from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
from time import time
from numpy import ones_like,where, ndarray
from solver import solve


# Alternatively replace this with your own path
load_dotenv()
tesseract_path = os.getenv("TESSERACT_PATH")
if not tesseract_path:
    raise ValueError("TESSERACT_PATH is not set in the .env file")

# loading pytesseract
pytesseract.pytesseract.tesseract_cmd = tesseract_path

def showImage(title: str, img: ndarray, wait: bool = True) -> None:
    """Helper to show an image with OpenCV."""
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.imshow(title, img)
    if wait:
        cv2.waitKey(0)

def findPuzzle(image: ndarray, debug: bool = False) -> tuple[ndarray, ndarray, ndarray]:
    '''
    Finds the puzzle in an image. 
    '''
    # blurs the image
    blurred = cv2.GaussianBlur(image, (5, 5), cv2.BORDER_DEFAULT)
    if debug:
        cv2.namedWindow('img', cv2.WINDOW_NORMAL)
        cv2.imshow('img',blurred)
        cv2.waitKey(0)

    # applies a thresholding function to the image
    # this makes eveything black or white based on certain criteria
    
    thresh = cv2.adaptiveThreshold(blurred.copy(), 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 195, 5)
    thresh = cv2.bitwise_not(thresh)

    if debug:
        cv2.namedWindow('img',cv2.WINDOW_NORMAL)
        cv2.imshow('img',thresh)
        cv2.waitKey(0)
    
    # finds contours in the image
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours = grab_contours(contours)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    if debug:
        print(f"{len(contours)} contours found")

    puzzleContour = None
	# loop over the contours
    for c in contours:
		# approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		# if our approximated contour has four points, then we can
		# assume we have found the outline of the puzzle
        if len(approx) == 4:
            puzzleContour = approx
            break

    if debug:
        output = image.copy()
        cv2.drawContours(output, [puzzleContour], -1, (255, 0, 0), 10)
        cv2.namedWindow('Puzzle Outline',cv2.WINDOW_NORMAL)
        cv2.imshow("Puzzle Outline", output)
        cv2.waitKey(0)

    # applies a four point transform to all versions of image
    # this tries to correct for any error induced by taking
    # photos at an angle. It transforms image to how it might
    # look when looking straight down

    puzzle = four_point_transform(image, puzzleContour.reshape(4, 2))
    warped = four_point_transform(blurred, puzzleContour.reshape(4, 2))

    if puzzle.shape[0] > 800:
        thresh = four_point_transform(thresh, puzzleContour.reshape(4, 2))
    else:
        newThresh = cv2.adaptiveThreshold(image.copy(), 255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 195, 5)
        newThresh = cv2.bitwise_not(newThresh)
        thresh = four_point_transform(newThresh, puzzleContour.reshape(4, 2))

    if debug:
        cv2.namedWindow('Warped Puzzle',cv2.WINDOW_NORMAL)
        cv2.imshow("Warped Puzzle", warped)

        cv2.namedWindow('Warped Thresh',cv2.WINDOW_NORMAL)
        cv2.imshow("Warped Thresh", thresh)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    return puzzle, warped, thresh

def getDigits(warped: ndarray, warpedBinary: ndarray, debug: bool = False, debugCells: list[int] = []) -> list[str]:
    '''
    Extracts the numbers from the grid using pytesseract.
    '''
    # gets the increments for x and y
    xInc = warped.shape[1] // 9
    yInc = warped.shape[0] // 9

    warpedBinary = cv2.bitwise_not(warpedBinary)

    # empty list to store the cells in
    cells = []
    # iterates through all possible cells in the image
    # splits it into 9 rows and columns, and works out
    # the coordinates of their corners.
    for y in range(9):
        row = ''
        for x in range(9):
            cellNum = y*9 + x + 1

            if debug == True or cellNum in debugCells:
                print(f'Cell Num:  {cellNum}')

            # finds the start x and y coords
            startX = x * xInc
            startY = y * yInc

            #finding end x and y coords
            endX = (x + 1) * xInc
            endY = (y + 1) * yInc

            cell = [startX, startY, endX, endY]

            # takes inner bit of the cell to reduce possible noise in the 
            # image from grid lines
            cell = warpedBinary[
                int(round(startY + 0.05 * yInc)):int(round(endY - 0.02 * yInc)),
                int(round(startX + 0.15 * xInc)):int(round(endX - 0.1 * xInc))]
            
            cv2.bitwise_not(cell)

            cell = cv2.threshold(cell, 0, 255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]    

            cell = clear_border(cell)

            # resize it to better fit pytesseract's optimum image size
            cell = cv2.resize(cell, (45, 45), interpolation=cv2.INTER_LINEAR)

            contours = cv2.findContours(cell.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            contours = grab_contours(contours)

            if debug == True:
                print(len(contours))
                print(cell.shape)
                
            if len(contours) > 0:
                contour = max(contours, key = cv2.contourArea)
                
            # flipping colours as pytesseract does better when dealing with black text 
            # on white background
            cell = cv2.bitwise_not(cell)

            (h, w) = cell.shape
            percentfilled = cv2.countNonZero(cell) / float(w * h)

            # if more than 97% of the image is blank then dont even test it
            # causes a 50%+ speedup 
            # I am using 97 to have a very large buffer before errors start
            # happening because it doesnt scan valid cells
            if percentfilled > 0.97:
                row += "0"
                if debug or cellNum in debugCells:
                    print("Fill below threshold value")
                continue

            # reading the number in the cell
            data = pytesseract.image_to_data(cell,config=r'--oem 3 --psm 10 digits')

            if debug:
                cv2.namedWindow('cell',cv2.WINDOW_NORMAL)
                cv2.imshow("cell", cell)

                print(data)

            elif cellNum in debugCells:
                # prints data about a specific cell
                print(data)

            # getting the useful data out of the pytesseract output
            data = data.split('\n')
            data = data[-2]
            data = data.split('\t')

            cellOCRtext = [data[-1],data[-2]]

            # fixing some common mistakes tesseract makes 
            letterToNum = {'g':'8','T':'1','?':'2','a':'2','e':'9'}
            if (cellOCRtext[0] in letterToNum.keys()) and float(cellOCRtext[1]) > 60:
                cellOCRtext[0] = letterToNum[cellOCRtext[0]]

            # if the result is likely to be right and is a number, we set the output
            # to that result
            text = 'N/A'
            if re.sub("[^0-9]","",cellOCRtext[0]) in ['1','2','3','4','5','6','7','8','9',1,2,3,4,5,6,7,8,9]:
                if float(cellOCRtext[1]) > 62:
                    text = re.sub("[^0-9]","",cellOCRtext[0])

            if debug:
                print('Normal Cell: ',data[-2],data[-1])
                if cellOCRtext[0] != data[-1]:
                    print('Normal Cell Adjusted: ',cellOCRtext[0],cellOCRtext[1])

            
            if len(contours) > 0 and text == "N/A": 
                # this code creates a new image using the contours of the original 
                # sometimes this can improve results by further reducing noise

                # we only check this if no previous result was found
                cellContour = cell.copy()
                mask = ones_like(cellContour) * 255  # White background

                # Fill the contour area with black
                cv2.drawContours(mask, [cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)], -1, (0, 0, 0), thickness=cv2.FILLED)

                # Apply mask to the original image
                cellContour = where(mask == 0, cellContour, 255)

                if debug:
                    cv2.namedWindow('cell contour',cv2.WINDOW_NORMAL)
                    cv2.imshow("cell contour", cellContour)

                # extracting data
                data = pytesseract.image_to_data(cellContour,config='--psm 6 -c tessedit_char_whitelist=123456789')

                if debug or cellNum in debugCells:
                    print(data)
                
                data = data.split('\n')
                data = data[-2]
                data = data.split('\t')

                cellContourOCRtext = [data[-1],data[-2]]

                # checking for common mistakes
                letterToNum = {'g':'8','T':'1','?':'2','a':'2','e':'9'}
                if (cellContourOCRtext[0] in letterToNum.keys()) and float(cellContourOCRtext[1]) > 60:
                    cellContourOCRtext[0] = letterToNum[cellContourOCRtext[0]]

                if debug or cellNum in debugCells:
                    print('Cell Contour:  ',data[-2],data[-1])
                    if cellContourOCRtext[0] != data[-1]:
                        print('Contour Cell Adjusted: ',cellContourOCRtext[0],cellContourOCRtext[1])

                if cellContourOCRtext[0].strip().replace('.','').replace(':','').replace("'","").replace("‘","") in ['1','2','3','4','5','6','7','8','9']:
                    if float(cellContourOCRtext[1]) > 62:
                        text = cellContourOCRtext[0]

            if text in ['1','2','3','4','5','6','7','8','9']:
                row += text
            else:
                row += '0'

            if debug:
                print('Final Text: ', text)

                cv2.waitKey(0)
                cv2.destroyAllWindows()
            elif cellNum in debugCells:
                print('Final Text: ', text)

        cells.append(row)

    return cells.copy()

def displayGrid(grid):
    for i in grid:
        print(i)


if __name__ == "__main__":
    showFinal = True

    # extracting path to the image to process
    if len(sys.argv) > 1:
        photoPath = sys.argv[1]
    elif os.getenv("PHOTO_PATH"): 
        photoPath = os.getenv("PHOTO_PATH")
    else:
        raise ValueError("No valid path found on input")
    
    debug = len(sys.argv) > 2 and sys.argv[2].lower() == "true"
    debugCells = list(map(int, sys.argv[3:]))
    
    print("Path to Image:", photoPath)

    # opens image as greyscale
    image = cv2.imread(photoPath, cv2.IMREAD_GRAYSCALE)
                
    if debug:
        showImage("Original", image)

    h, w = image.shape[:2]

    # Displaying the height and width
    print("Height = {},  Width = {}".format(h, w))

    # resizing if needed
    if w > 2000:
        image = cv2.resize(image.copy(), (0, 0), fx = 0.5, fy = 0.5)

        h, w = image.shape[:2]
        # Displaying the height and width
        print("Height = {},  Width = {}".format(h, w))
        if debug:
            cv2.namedWindow('img', cv2.WINDOW_NORMAL)
            cv2.imshow('img',image)
            cv2.waitKey()
        cv2.destroyAllWindows()

    warpedPuzzle, warpedBlurred, thresh = findPuzzle(image, debug)

    start = time()
    sudoku = getDigits(warpedBlurred, thresh, debug, debugCells)
    print(f"Digit extraction took {time() - start:.2f} seconds")

    start = time()
    solved = solve(sudoku)
    print(f"Solve took {time() - start:.2f} seconds")

    for row in solved:
        for square in row:
            print(square,' ',end = '')
        print('\n')

    print(sudoku)
    xInc = warpedBlurred.shape[1] // 9
    yInc = warpedBlurred.shape[0] // 9
    print(solved)
    warpedBlurred = cv2.cvtColor(warpedBlurred, cv2.COLOR_GRAY2BGR)
    cv2.resize(warpedBlurred, (800, 800), interpolation=cv2.INTER_LINEAR)
    for row in range(9):
        for value in range(9):
            if sudoku[row][value] == '0':
                cv2.putText(warpedBlurred, str(solved[row][value]), (int(round(xInc * value + xInc * 0.25)), int(round((row + 1) * yInc - yInc * 0.2))),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=2,color=(50,50,50),thickness=7)

    if showFinal:
        cv2.namedWindow('Solution', cv2.WINDOW_NORMAL)
        cv2.imshow('Solution', warpedBlurred)
        cv2.waitKey(0)