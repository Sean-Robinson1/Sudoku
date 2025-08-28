from flask import Flask, render_template, request, send_file
import io
import cv2
import numpy as np
from solver import string2List, startLogicalSolve, bruteForce
from sudoku_image_solver import getDigits, findPuzzle


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return "No file uploaded", 400

    file = request.files["photo"]
    if file.filename == "":
        return "No selected file", 400

    # Read uploaded file into memory as numpy array
    file_bytes = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)

    # Resize if very large
    h, w = image.shape[:2]
    if w > 2000:
        image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)

    # Sudoku processing 
    warpedPuzzle, warpedBlurred, thresh = findPuzzle(image, False)
    sudoku = getDigits(warpedBlurred, thresh, debug=False)

    # Solving
    newSquares = string2List(["0"*9 for _ in range(9)])
    squares = {i: {1,2,3,4,5,6,7,8,9} for i in range(81)}

    for i in range(9):
        for j, digit in enumerate(sudoku[i]):
            if digit != '0':
                idx = i * 9 + j
                squares[idx] = {int(digit)}

    squares = startLogicalSolve(squares)
    filled = bruteForce(newSquares)

    # Drawing solution back onto puzzle
    xInc = warpedBlurred.shape[1] // 9
    yInc = warpedBlurred.shape[0] // 9
    warpedBlurred = cv2.cvtColor(warpedBlurred, cv2.COLOR_GRAY2BGR)

    for row in range(9):
        for col in range(9):
            if sudoku[row][col] == '0':
                cv2.putText(
                    warpedBlurred,
                    str(newSquares[row][col]),
                    (int(xInc * col + xInc * 0.25), int((row + 1) * yInc - yInc * 0.2)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (50, 50, 50),
                    4,
                )

    _, buffer = cv2.imencode(".jpg", warpedBlurred)
    io_buf = io.BytesIO(buffer)

    return send_file(io_buf, mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
