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
import copy
import random
import numpy as np

directions = {'F': np.array(['C', 'D', 'B', 'E']),
              'B': np.array(['C', 'D', 'B', 'E']),
              'V': np.array(['C', 'D', 'B', 'E']),
              'L': np.array(['H', 'V'])}

flow_delta = {'FC': np.array([[-1, 0]]),
              'FD': np.array([[0, 1]]),
              'FB': np.array([[1, 0]]),
              'FE': np.array([[0, -1]]),
              'BC': np.a<rray([[0, -1], [-1, 0], [0, 1]]),
              'BD': np.array([[-1, 0], [0, 1], [1, 0]]),
              'BB': np.array([[0, 1], [1, 0], [0, -1]]),
              'BE': np.array([[1, 0], [0, -1], [-1, 0]]),
              'VC': np.array([[0, -1], [-1, 0]]),
              'VD': np.array([[-1, 0], [0, 1]]),
              'VB': np.array([[0, 1], [1, 0]]),
              'VE': np.array([[1, 0], [0, -1]]),
              'LH': np.array([[0, -1], [0, 1]]),
              'LV': np.array([[-1, 0], [1, 0]])}

move_delta = {'C': np.array([-1, 0]),
              'D': np.array([0, 1]),
              'B': np.array([1, 0]),
              'E': np.array([0, -1])}

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

visited_boards = np.empty((0, 0))

first = True

def not_in_numpy(array, compare):
    for i in range(len(array)):
        if np.array_equal(array[i], compare):
            return False
    return True

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
    return np.array([new_row, new_col])

def piece_flow_delta(piece):
    i = 0
    aux = flow_delta[piece[0]]
    while piece != piece[0] + directions[piece[0]][i]:
        i += 1
        new_aux = np.empty((0, 2))
        for j in range(len(aux)):
            new_aux = np.append(new_aux, np.array([rot_delta(aux[j])]), axis=0)
        aux = new_aux
    return aux

class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.visited = np.array([np.array([0 for _ in range(board.dimension())]) for _ in range(board.dimension())])
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
        
        res = np.empty((0, 2))
        if row != 0:
            res = np.append(res, np.array([self.board[row - 1, col]]), axis=0)
        if row != len(self.board):
            res = np.append(res, np.array([self.board[row + 1, col]]), axis=0)
        return res

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        
        res = np.empty((0, 2))
        if col != 0:
            res = np.append(res, np.array([self.board[row, col - 1]]), axis=0)
        if col != len(self.board):
            res = np.append(res, np.array([self.board[row, col + 1]]), axis=0)
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
        board.board = np.array(board.board)
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

        res = np.empty((0, 3))
        for row in range(state.board.dimension()):
            for col in range(state.board.dimension()):
                if not state.visited[row][col]:
                    piece = state.board.get_value(row, col)
                    for direction in directions[piece[0]]:
                        if direction != piece[1]:
                            ok = True
                            must_flow_delta = np.empty((0, 2))
                            must_not_flow_delta = np.empty((0, 2))
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
                                                    must_flow_delta = np.append(must_flow_delta, np.array([np.array([i, j])]), axis=0).astype(int)
                                                if (new_row == 0 or new_row == state.board.dimension() - 1 or new_col == 0 or new_col == state.board.dimension() - 1) and \
                                                (state.board.get_value(new_row, new_col)[0] == 'L'):
                                                    must_not_flow_delta = np.append(must_not_flow_delta, np.array([np.array([i, j])]), axis=0).astype(int)
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
                                                    must_flow_delta = np.append(must_flow_delta, np.array([np.array([i, j])]), axis=0).astype(int)
                            for delta in must_flow_delta:
                                if not_in_numpy(flow_delta[piece[0] + direction], delta):
                                    ok = False
                            for delta in must_not_flow_delta:
                                if not not_in_numpy(flow_delta[piece[0] + direction], delta):
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
                            if ok and not any(coding == item for item in visited_boards):
                                res = np.append(res, np.array([np.array([row, col, piece[0] + direction])]), axis=0)
                                visited_boards = np.append(visited_boards, np.array(coding))
        return res

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        new_state = copy.deepcopy(state)

        if type(action) == str:
            all_actions = self.actions(state)
            for row in range(state.board.dimension()):
                for col in range(state.board.dimension()):
                    found = False
                    allowed_actions = np.empty((0, 3))
                    for action in all_actions:
                        if row == int(action[0]) and col == int(action[1]) and state.board.get_value(row, col) == action[2]:
                            found = True
                        if row == int(action[0]) and col == int(action[1]):
                            allowed_actions = np.append(allowed_actions, np.array([np.array([row, col, action[2]])]), axis=0)
                    if not found and len(allowed_actions) > 0:
                        new_state.board.set_value(row, col, allowed_actions[random.randint(0, len(allowed_actions) - 1)][2])
                        # new_state.board.set_value(row, col, allowed_actions[0][2])
            return new_state
            
        new_state.board.set_value(int(action[0]), int(action[1]), action[2])
        new_state.visited[int(action[0])][int(action[1])] = 1
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
        print(glo)

        i = 0
        to_check = np.array([[start_point_x, start_point_y]])
        checked = np.empty((0, 2))
        while to_check.size != 0:

            position = to_check[0]
            new_to_check = np.empty((0, 2))

            for delta in flow_delta[state.board.get_value(position[0], position[1])]:

                flow_row = position[0] + delta[0]
                flow_col = position[1] + delta[1]

                if not (0 <= flow_row < state.board.dimension() and 0 <= flow_col < state.board.dimension()):
                    return False

                flow_positions_next = np.empty((0, 2))
                for delta_next in flow_delta[state.board.get_value(flow_row, flow_col)]:
                    flow_positions_next = np.append(flow_positions_next, np.array([np.array([flow_row + delta_next[0], flow_col + delta_next[1]])]), axis=0)

                if not_in_numpy(flow_positions_next, position):
                    return False

                if not_in_numpy(checked, [flow_row, flow_col]) and not_in_numpy(new_to_check, [flow_row, flow_col]) and not_in_numpy(to_check, [flow_row, flow_col]):
                    new_to_check = np.append(new_to_check, np.array([np.array([flow_row, flow_col])]), axis=0).astype(int)
            
            i += 1
            to_check = to_check[1:, :]
            to_check = np.append(to_check, new_to_check, axis = 0).astype(int)
            checked = np.append(checked, np.array([position]), axis=0).astype(int)
        
        return i == state.board.dimension() ** 2

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""

        res = 1
        checked = np.empty((0, 2))
        to_check = np.array([[start_point_x, start_point_y]])
        while to_check.size != 0:
            row, col = to_check[0]
            new_to_check = np.empty((0, 2))
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
                    if found and not_in_numpy(checked, [new_row, new_col]) and not_in_numpy(to_check, [new_row, new_col]) and not_in_numpy(new_to_check, [new_row, new_col]):
                        new_to_check = np.append(new_to_check, np.array([np.array([new_row, new_col])]), axis=0)
                        res += 1
            checked = np.append(checked, np.array([np.array([row, col])]), axis=0)
            to_check = to_check[1:, :]
            to_check = np.append(to_check, new_to_check, axis = 0).astype(int)
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

    res = breadth_first_tree_search(p)
    

    # print(res.solution())
    print(res.state.board)
    # print(glo)