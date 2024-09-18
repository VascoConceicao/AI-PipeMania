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

visited_states = []

class Board:
    """Representação interna de um tabuleiro de PipeMania."""

    def __str__(self):
        """Representação em string de uma instância da classe Board."""

        s = ""
        for i in range(len(self.board)):
            if i != 0:
                s += "\n"
            for j in range(len(self.board[i])):
                if j != 0:
                    s += ""
                if (len(self.board[i][j]) == 1):
                    s += " "
                else:
                    s += symbols[self.board[i][j]]
                #     s += "\t"
                # s += self.board[i][j]
        return s

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
        # TODO
        pass

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        # TODO
        pass

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
            row = []
            for piece in line.split():
                row += [piece[0]]
            board.board += [row]
        global start_row
        global start_col
        start_row = random.randint(0, board.dimension() - 1)
        start_col = random.randint(0, board.dimension() - 1)
        return board

    # TODO: outros metodos da classe


class PipeManiaState:
    state_id = 0

    def __init__(self, board: Board):
        self.board = board
        self.overflow = [[start_row, start_col]]
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        
        super().__init__(PipeManiaState(board))

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        
        res = []
        for row, col in state.overflow:
            available_directions = 0
            piece_type = state.board.get_value(row, col)
            for piece_direction in directions[piece_type]:
                piece = piece_type + piece_direction
                ok = True
                for delta_row, delta_col in flow_delta[piece]:
                    new_row = row + delta_row
                    new_col = col + delta_col
                    if not (0 <= new_row <= state.board.dimension() - 1 and 0 <= new_col <= state.board.dimension() - 1):
                        ok = False
                    elif len(state.board.get_value(new_row, new_col)) == 2:
                        found = False
                        for next_delta_row, next_delta_col in flow_delta[state.board.get_value(new_row, new_col)]:
                            next_row = new_row + next_delta_row
                            next_col = new_col + next_delta_col
                            if row == next_row and col == next_col:
                                found = True
                        if not found:
                            ok = False
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if ((i == 0 and j != 0) or (i != 0 and j == 0)) and (0 <= row + i <= state.board.dimension() - 1 and 0 <= col + j <= state.board.dimension() - 1):
                            if len(state.board.get_value(row + i, col + j)) == 2:
                                found = False
                                for delta_row, delta_col in flow_delta[state.board.get_value(row + i, col + j)]:
                                    if row == row + i + delta_row and col == col + j + delta_col:
                                        found = True
                                if found and [i, j] not in flow_delta[piece]:
                                    ok = False
                global visited_states
                board_str = str(self.result(state, [row, col, piece]).board)
                if ok and board_str not in visited_states:
                    visited_states += [board_str]
                    res += [[row, col, piece]]
                    available_directions += 1
            if not available_directions:
                return []
        return res

    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        
        new_row = action[0]
        new_col = action[1]
        new_piece = action[2]
        new_state = copy.deepcopy(state)
        new_state.board.set_value(new_row, new_col, new_piece)
        new_overflow = []
        for row in range(new_state.board.dimension()):
            for col in range(new_state.board.dimension()):
                if len(new_state.board.get_value(row, col)) == 2:
                    for delta_row, delta_col in flow_delta[new_state.board.get_value(row, col)]:
                        new_row = row + delta_row
                        new_col = col + delta_col
                        if (0 <= new_row <= new_state.board.dimension() - 1 and 0 <= new_col <= new_state.board.dimension() - 1) and \
                           [new_row, new_col] not in new_overflow and \
                           len(new_state.board.get_value(new_row, new_col)) == 1:
                            new_overflow += [[new_row, new_col]]
        new_state.overflow = new_overflow
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
        
        for row in range(state.board.dimension()):
            for col in range(state.board.dimension()):
                if len(state.board.get_value(row, col)) == 1:
                    return False
        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        
        possible = 0
        connected = 0
        for row in range(node.state.board.dimension()):
            for col in range(node.state.board.dimension()):
                piece_type = node.state.board.get_value(row, col)[0]
                piece_direction = directions[piece_type][0]
                piece = piece_type + piece_direction
                possible += len(flow_delta[piece])
                if len(node.state.board.get_value(row, col)) == 2:
                    connected += len(flow_delta[piece])
        return possible - connected

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    it = 0
    start_row = 0
    start_col = 0
    p = PipeMania(Board.parse_instance())
    res1 = depth_first_tree_search(p)
    # print(res1.state.board)