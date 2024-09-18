# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)
from sys import stdin

import random
import copy

directions = {'F': ['C', 'D', 'B', 'E'],
              'B': ['C', 'D', 'B', 'E'],
              'V': ['C', 'D', 'B', 'E'],
              'L': ['H', 'V']}

flow_delta = {'FC': [[-1, 0]],
              'FD': [[0, 1]],
              'FB': [[1, 0]],
              'FE': [[0, -1]],
              'BC': [[0, -1], [-1, 0], [0, 1]],
              'BD': [[-1, 0], [0, 1], [1, 0]],
              'BB': [[0, 1], [1, 0], [0, -1]],
              'BE': [[1, 0], [0, -1], [-1, 0]],
              'VC': [[0, -1], [-1, 0]],
              'VD': [[-1, 0], [0, 1]],
              'VB': [[0, 1], [1, 0]],
              'VE': [[1, 0], [0, -1]],
              'LH': [[0, -1], [0, 1]],
              'LV': [[-1, 0], [1, 0]]}

move_delta = {'C': [-1, 0],
              'D': [0, 1],
              'B': [1, 0],
              'E': [0, -1]}

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

visited_boards = []

first = True

def rot_piece(piece):
    i = 0
    for j in range(len(directions[piece[0]])):
        if directions[piece[0]][j] == piece[1]:
            i = j
    if i == len(directions[piece[0]]) - 1:
        return piece[0] + directions[piece[0]][0]
    else:
        return piece[0] + directions[piece[0]][i + 1]
    
def rot_delta(delta):
    row = delta[0]
    col = delta[1]
    if row != 0:
        new_row = 0
    else:
        new_row = col
    if col != 0:
        new_col = 0
    else:
        new_col = -row
    return [new_row, new_col]

def piece_flow_delta(piece):
    i = 0
    aux = flow_delta[piece[0]]
    while piece != piece[0] + directions[piece[0]][i]:
        i += 1
        new_aux = []
        for j in range(len(aux)):
            new_aux += [rot_delta(aux[j])]
        aux = new_aux
    return aux

class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.visited = [[0 for _ in range(board.dimension())] for _ in range(board.dimension())]
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de PipeMania."""

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def set_value(self, row: int, col: int, value: str):
        self.board[row][col] = value

    def dimension(self):
        return len(self.board)

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        
        res = []
        if row != 0:
            res += [self.board[row - 1, col]]
        if row != len(self.board):
            res += [self.board[row + 1, col]]
        return res

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        
        res = []
        if col != 0:
            res += [self.board[row, col - 1]]
        if col != len(self.board):
            res += [self.board[row, col + 1]]
        return res

    def __str__(self):
        """Representação em string de uma instância da classe Board."""

        s = ""
        for i in range(len(self.board)):
            if i != 0:
                s += "\n"
            for j in range(len(self.board[i])):
                if j != 0:
                #     s += ""
                # s += symbols[self.board[i][j]]
                    s += "\t"
                s += self.board[i][j]
        return s

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        
        board = Board()
        board.board = []
        for line in stdin:
            board.board += [line.split()]
        return board

    # TODO: outros metodos da classe


class PipeMania(Problem):

    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""

        super().__init__(PipeManiaState(board))

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        global first
        if first:
            first = False
            return ["A"]

        res = []
        for row in range(state.board.dimension()):
            for col in range(state.board.dimension()):
                if not state.visited[row][col]:
                    piece = state.board.get_value(row, col)
                    for direction in directions[piece[0]]:
                        if direction != piece[1]:
                            ok = True
                            must_flow_delta = []
                            must_not_flow_delta = []
                            if (row == 1 or row == state.board.dimension() - 2 or col == 1 or col == state.board.dimension() - 2) and (row != 0 and row != state.board.dimension() - 1 and col != 0 and col != state.board.dimension() - 1):
                                # se está no exterior - 1
                                for i in range(-1, 2):
                                    for j in range(-1, 2):
                                        if (i == 0 and j != 0) or (i != 0 and j == 0):
                                            new_row = row + i
                                            new_col = col + j
                                            if 0 <= new_row < state.board.dimension() and 0 <= new_col < state.board.dimension():
                                                if (new_row == 0 or new_row == state.board.dimension() - 1 or new_col == 0 or new_col == state.board.dimension() - 1) and \
                                                ((state.board.get_value(new_row, new_col)[0] == 'B') or (state.board.get_value(new_row, new_col)[0] == 'V')):
                                                    must_flow_delta += [[i, j]]
                                                if (new_row == 0 or new_row == state.board.dimension() - 1 or new_col == 0 or new_col == state.board.dimension() - 1) and \
                                                (state.board.get_value(new_row, new_col)[0] == 'L'):
                                                    must_not_flow_delta += [[i, j]]
                            if row == 0 or row == state.board.dimension() - 1 or col == 0 or col == state.board.dimension() - 1:
                                # se está no exterior
                                for i in range(-1, 2):
                                    for j in range(-1, 2):
                                        if (i == 0 and j != 0) or (i != 0 and j == 0):
                                            new_row = row + i
                                            new_col = col + j 
                                            if 0 <= new_row < state.board.dimension() and 0 <= new_col < state.board.dimension():
                                                if (new_row == 0 or new_row == state.board.dimension() - 1 or new_col == 0 or new_col == state.board.dimension() - 1) and \
                                                ((state.board.get_value(new_row, new_col)[0] == 'L') or (state.board.get_value(new_row, new_col)[0] == 'B')):
                                                    must_flow_delta += [[i, j]]
                            for delta in must_flow_delta:
                                if delta not in flow_delta[piece[0] + direction]:
                                    ok = False
                            for delta in must_not_flow_delta:
                                if delta in flow_delta[piece[0] + direction]:
                                    ok = False
                            for delta in flow_delta[piece[0] + direction]:
                                new_row = row + delta[0]
                                new_col = col + delta[1]
                                if not (0 <= new_row < state.board.dimension() and 0 <= new_col < state.board.dimension()) or \
                                   (piece[0] == 'F' and state.board.get_value(new_row, new_col)[0] == 'F') or \
                                   ((row != 0 and row != state.board.dimension() - 1 and col != 0 and col != state.board.dimension() - 1) and (new_row == 0 or new_row == state.board.dimension() - 1 or new_col == 0 or new_col == state.board.dimension() - 1) and state.board.get_value(new_row, new_col)[0] == 'L'):
                                    ok = False
                            coding = ""
                            for i in range(state.board.dimension()):
                                for j in range(state.board.dimension()):
                                    if not (i == row and j == col):
                                        coding += state.board.get_value(i, j)
                                    else:
                                        coding += piece[0] + direction
                            global visited_boards
                            if ok and coding not in visited_boards:
                                res += [[row, col, piece[0] + direction]]
                                visited_boards += [coding]
        print(res)
        print("\n")
        return res

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        new_state = copy.deepcopy(state)
        if action == "A":
            all_actions = self.actions(state)
            for row in range(state.board.dimension()):
                for col in range(state.board.dimension()):
                    found = False
                    allowed_actions = []
                    for action in all_actions:
                        if row == action[0] and col == action[1] and state.board.get_value(row, col) == action[2]:
                            found = True
                        if row == action[0] and col == action[1]:
                            allowed_actions += [[row, col, action[2]]]
                    if not found and len(allowed_actions) > 0:
                        new_state.board.set_value(row, col, allowed_actions[random.randint(0, len(allowed_actions) - 1)][2])
                        # new_state.board.set_value(row, col, allowed_actions[0][2])
            return new_state
            
        else:
            new_state.board.set_value(action[0], action[1], action[2])
            new_state.visited[action[0]][action[1]] = 1
            return new_state

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        
        # if first:
        #     print("Inicial")
        # print(state.board)
        # print("\n")

        global glo
        if glo > limit:
            sys.exit()
        glo += 1
        # print(glo)

        i = 0
        to_check = [[start_point_x, start_point_y]]
        checked = []
        while to_check:

            position = to_check[0]
            new_to_check = []

            for delta in flow_delta[state.board.get_value(position[0], position[1])]:

                flow_row = position[0] + delta[0]
                flow_col = position[1] + delta[1]
                if not (0 <= flow_row < state.board.dimension() and 0 <= flow_col < state.board.dimension()):
                    return False

                flow_positions_next = []
                for delta_next in flow_delta[state.board.get_value(flow_row, flow_col)]:
                    flow_positions_next += [[flow_row + delta_next[0], flow_col + delta_next[1]]]

                if position not in flow_positions_next:
                    return False

                if [flow_row, flow_col] not in checked + to_check + new_to_check:
                    new_to_check += [[flow_row, flow_col]]
            
            i += 1
            to_check = to_check[1:] + new_to_check
            checked += [position]

        return i == state.board.dimension() ** 2

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""

        res = 1
        checked = []
        to_check = [[start_point_x, start_point_y]]
        while to_check:
            row, col = to_check[0]
            new_to_check = []
            for delta in flow_delta[node.state.board.get_value(row, col)]:
                new_row = row + delta[0]
                new_col = col + delta[1]
                if 0 <= new_row < node.state.board.dimension() and 0 <= new_col < node.state.board.dimension():
                    found = False
                    for new_delta in flow_delta[node.state.board.get_value(new_row, new_col)]:
                        new_new_row = new_row + new_delta[0]
                        new_new_col = new_col + new_delta[1]
                        if row == new_new_row and col == new_new_col:
                            found = True
                    if found and [new_row, new_col] not in checked + to_check + new_to_check:
                        new_to_check += [[new_row, new_col]]
                        res += 1
            checked += [[row, col]]
            to_check = to_check[1:] + new_to_check
        # print(res)
        return node.state.board.dimension()**2 - res


    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    glo = 0
    limit = 100000
    p = PipeMania(Board.parse_instance())
    start_point_x = random.randint(0, p.initial.board.dimension() - 1)
    start_point_y = random.randint(0, p.initial.board.dimension() - 1)
    # start_point_x = 0
    # start_point_y = 0

    res = depth_first_tree_search(p)

    # print(res.solution())
    print(res.state.board)
    # print(glo)
