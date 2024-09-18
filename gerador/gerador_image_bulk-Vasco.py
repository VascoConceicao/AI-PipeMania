from PIL import Image, ImageGrab, ImageOps
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
import numpy as np
from skimage.metrics import structural_similarity as ssim
import random
import pyautogui

size = 25
save = "25x25_6"
middle = "BB"

inner = 1
pixels = 0

x1_box = 2524
y1_box = 236
x2_box = 3224
y2_box = 936
pieces = ['FC','FB','FE','FD','BC','BB','BE','BD','VC','VB','VE','VD','LH','LV']

symbols = {'FC': '╽',
           'FB': '╿',
           'FE': '╼',
           'FD': '╾',
           'BC': '┴',
           'BB': '┬',
           'BE': '┤',
           'BD': '├',
           'VC': '┘',
           'VB': '┌',
           'VE': '┐',
           'VD': '└',
           'LH': '─',
           'LV': '│'}

def compare_images_ssim(image_path1, cell):
    img1 = Image.open(image_path1).convert("L")
    img2 = cell.convert("L")
    
    arr1 = np.array(img1)
    arr2 = np.array(img2)

    score, _ = ssim(arr1, arr2, full=True)
    return score

def compare(cell):
    max = 0
    res = 0
    for i in range(len(pieces)):
        score = compare_images_ssim("C:\\Users\\vasco\\OneDrive - Universidade de Lisboa\\Universidade\\2ºAno\\2ºSemestre\\InteligênciaArtificial\\Projeto\\gerador\\Pieces\\" + pieces[i] + ".png", cell)

        if score == 1:
            return pieces[i]
        
        if score > max:
            max = score
            res = i

    return pieces[res]

def get_board(image_path, rows, cols, output_folder):
    img = Image.open(image_path)
    img_width, img_height = img.size

    print(img_width)
    print(img_height)
    cell_width = img_width // cols
    cell_height = img_height // rows
    print(cell_width)
    print(cell_height)

    board = []
    for row in range(rows):
        for col in range(cols):
            box = (col * cell_width + inner, row * cell_height + inner, (col + 1) * cell_width - inner, (row + 1) * cell_height - inner)
            
            if pixels != 0:
                cell = ImageOps.expand(img.crop(box), border=pixels, fill='white')
            cell.save(fr"{output_folder}\img_{row}_{col}.png")
            piece = compare(cell)
            board.append(piece)

    return board

# x = 
# y = 
# pyautogui.moveTo(x, y)
# pyautogui.click()


ImageGrab.grab().crop((x1_box, y1_box, x2_box, y2_box)).save(r"C:\Users\vasco\OneDrive - Universidade de Lisboa\Universidade\2ºAno\2ºSemestre\InteligênciaArtificial\Projeto\gerador\Board.png")

board = get_board(r"C:\Users\vasco\OneDrive - Universidade de Lisboa\Universidade\2ºAno\2ºSemestre\InteligênciaArtificial\Projeto\gerador\Board.png", size, size, r"C:\Users\vasco\OneDrive - Universidade de Lisboa\Universidade\2ºAno\2ºSemestre\InteligênciaArtificial\Projeto\gerador\Pieces\Slices")

board = np.reshape(board, (size, size))
board[int(size/2)][int(size/2)] = middle
print(board[12])

with open("C:\\Users\\vasco\\OneDrive - Universidade de Lisboa\\Universidade\\2ºAno\\2ºSemestre\\InteligênciaArtificial\\Projeto\\gerador\\Tests" + save + ".txt", 'w') as f:
    for i in range(size):
        if i != 0:
            f.write("\n")
            print("\n")
        for j in range(size):
            print(symbols[board[i][j]], end=' ')
            f.write(board[i][j])
            f.write("\t")