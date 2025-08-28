# Sudoku Solver Web App

A Python-based Sudoku solver that uses computer vision and OCR to extract Sudoku puzzles from images, then solves them using logical and brute-force techniques. Includes a web interface (Flask), a Tkinter GUI, and command-line tools.

## Features

- Upload or take a photo of a Sudoku puzzle and get the solution overlaid on the image.
- Fast and accurate digit extraction using OpenCV and Tesseract OCR.
- Logical and brute-force solving algorithms.
- Web interface ([Flask](https://flask.palletsprojects.com/)) to upload photos and desktop GUI ([Tkinter](https://docs.python.org/3/library/tkinter.html)).

## Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (set the path in `.env`)
- pip packages: see below

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/sudoku-solver.git
   cd sudoku
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   If `requirements.txt` is missing, install manually:
   ```sh
   pip install flask opencv-python numpy pytesseract python-dotenv imutils scikit-image tk
   ```

3. **Install Tesseract OCR:**
   - Download and install from [here](https://github.com/tesseract-ocr/tesseract).
   - Add the install path to your `.env` file:
     ```
     TESSERACT_PATH=C:/Program Files/Tesseract-OCR/tesseract.exe
     ```

## Usage

### Web App

1. Start the Flask server:
   ```sh
   python flask_app.py
   ```
2. Open your browser at [http://localhost:5000](http://localhost:5000).
3. Upload or take a photo of a Sudoku puzzle and view the solved result.

> **Note:** This webapp will only run locally

### Desktop GUI

Run the Tkinter GUI:
```sh
python solver_gui.py
```
Enter the Sudoku puzzle and press "SOLVE" to solve.
It should highlight issues if you enter an invalid sudoku.

### Command-Line

#### Solve a Sudoku from an image saved on device:

Run the `sudoku_image_solver` followed by the path to the image.
```sh
python sudoku_image_solver.py path/to/image.jpg
```

#### Debugging the OCR:

To troubleshoot OCR (text recognition) issues, pass `True` as the second argument:
```sh
python sudoku_image_solver.py path/to/image.jpg True
```

To debug issues with specifc cells, pass `False` followed by one or more cell indices (1-indexed):
```sh
python sudoku_image_solver.py path/to/image.jpg False 1 2 5 9 ...
```

> **Note:** This works for `.png`, `.jpeg` and `.jpg`. It should work for any file type accepted by OpenCV.

## Project Structure

- `flask_app.py` - Flask web server for image upload and solving.
- `solver.py` - Sudoku solving logic (logical and brute-force).
- `solver_gui.py` - Tkinter desktop GUI.
- `sudoku_image_solver.py` - Image processing and OCR.
- `templates/index.html` - Web interface HTML.


## Environment Variables

Create a `.env` file with:
```
TESSERACT_PATH=path/to/tesseract.exe
PHOTO_PATH=optional_default_image_path
```


> [!NOTE]
> Large parts of this project were written years ago, and as such may not reflect my present coding style or standards.
