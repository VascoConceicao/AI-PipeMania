from PIL import Image, ImageGrab, ImageOps
from functools import partial
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
import numpy as np
from skimage.metrics import structural_similarity as ssim
import pyautogui
import time

size = 25
how_many = 100

inner = 1
pixels = 0

x1_box = 2524
y1_box = 228
x2_box = 3224
y2_box = 928
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
        score = compare_images_ssim("C:\\Users\\vasco\\OneDrive - Universidade de Lisboa\\Universidade\\2ºAno\\2ºSemestre\\InteligênciaArtificial\\Projeto\\gerador\\pieces\\" + pieces[i] + ".png", cell)

        if score == 1:
            return pieces[i]
        
        if score > max:
            max = score
            res = i

    return pieces[res]

def get_board(image_path, rows, cols, output_folder):
    img = Image.open(image_path)
    img_width, img_height = img.size

    cell_width = img_width // cols
    cell_height = img_height // rows

    board = []
    for row in range(rows):
        for col in range(cols):
            box = (col * cell_width + inner, row * cell_height + inner, (col + 1) * cell_width - inner, (row + 1) * cell_height - inner)
            
            cell = ImageOps.expand(img.crop(box), border=pixels, fill='white')
            # cell.save(fr"{output_folder}\img_{row}_{col}.png")
            piece = compare(cell)
            board.append(piece)

    return board

pyautogui.moveTo(3015, 986)
for k in range(how_many):
    print("\n######## TEST %d ########" %(k+1))
    pyautogui.scroll(-300)

    save = "25x25" + "_" + str(k+1)

    time.sleep(1)
    ImageGrab.grab().crop((x1_box, y1_box, x2_box, y2_box)).save(r"C:\Users\vasco\OneDrive - Universidade de Lisboa\Universidade\2ºAno\2ºSemestre\InteligênciaArtificial\Projeto\gerador\Board.png")

    board = get_board(r"C:\Users\vasco\OneDrive - Universidade de Lisboa\Universidade\2ºAno\2ºSemestre\InteligênciaArtificial\Projeto\gerador\Board.png", size, size, r"C:\Users\vasco\OneDrive - Universidade de Lisboa\Universidade\2ºAno\2ºSemestre\InteligênciaArtificial\Projeto\gerador\pieces\slices")

    board = np.reshape(board, (size, size))

    with open("C:\\Users\\vasco\\OneDrive - Universidade de Lisboa\\Universidade\\2ºAno\\2ºSemestre\\InteligênciaArtificial\\Projeto\\gerador\\tests\\" + save + ".txt", 'w') as f:
        for i in range(size):
            if i != 0:
                f.write("\n")
                print("\n")
            for j in range(size):
                print(symbols[board[i][j]], end=' ')
                f.write(board[i][j])
                f.write("\t")
    print("\n")

    pyautogui.scroll(-100)
    pyautogui.moveTo(3015, 986)
    pyautogui.click()
    time.sleep(1)