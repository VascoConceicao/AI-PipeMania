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


import copy
import random
from search import (
    hill_climbing,
    simulated_annealing
)

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

it = 0

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
                    s += ""
                s += symbols[self.board[i][j]]
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
        for line in sys.stdin:
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

        res = []
        for row in range(state.board.dimension()):
            for col in range(state.board.dimension()):
                piece = state.board.get_value(row, col)
                ok = True
                for delta_row, delta_col in flow_delta[piece]:
                    new_row = col + delta_row
                    new_col = col + delta_col
                    if not (0 <= new_row < state.board.dimension() and 0 <= new_col < state.board.dimension()):
                        ok = False
                    else:
                        found = False
                        for new_delta_row, new_delta_col in flow_delta[state.board.get_value(new_row, new_col)]:
                            new_new_row = new_row + new_delta_row
                            new_new_col = new_col + new_delta_col
                            if row == new_new_row and col == new_new_col:
                                found = True
                        if not found:
                            ok = False
                if not ok:
                    for direction in directions[piece[0]]:
                        if direction != piece[1]:
                            global visited_boards
                            action = [row, col, piece[0] + direction]
                            string = str(self.result(state, action).board)
                            if string not in visited_boards:
                                res += [action]
                                visited_boards += [string]

        return res

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        new_state = copy.deepcopy(state)
        new_state.board.set_value(action[0], action[1], action[2])
        new_state.visited[action[0]][action[1]] = 1
        return new_state

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        global it
        it += 1
        print("\n")
        print(it)
        print(state.board)

        i = 0
        to_check = [[0, 0]]
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
        """Função que a procura hill climbing maximiza."""

        res = 1
        checked = []
        to_check = [[0, 0]]
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

    p = PipeMania(Board.parse_instance())
    goal_node = greedy_search(p)
    print(goal_node.state.board)
    