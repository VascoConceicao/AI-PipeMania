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
import time
import openpyxl
import pandas as pd

directions = {'F': ['C', 'D', 'B', 'E'],
              'B': ['C', 'D', 'B', 'E'],
              'V': ['C', 'D', 'B', 'E'],
              'L': ['H', 'V']}

delta_flow = {'FC': [[-1, 0]],
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

    def get_value(self, row, col):
        return self.board[row][col]

    def dimension(self):
        return len(self.board)

    @staticmethod
    def parse_instance(test):
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        
        board = Board()
        board.board = []
        with open("/mnt/c/Users/vasco/OneDrive - Universidade de Lisboa/Universidade/2ºAno/2ºSemestre/InteligênciaArtificial/Projeto/gerador/tests/" + "25x25_" + str(test+1) + ".txt", 'r') as f:
            for line in f:
                row = []
                for piece in line.split():
                    row += [piece[0]]
                board.board += [row]
        return board

    # TODO: outros metodos da classe


def update_domains(row, col, domains):

    to_update = [[row, col]]
    while to_update:
        row, col = to_update[0]
        to_update = to_update[1:]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0 and j != 0) or (i != 0 and j == 0):
                    new_row = row + i
                    new_col = col + j
                    if 0 <= new_row < len(domains) and 0 <= new_col < len(domains[0]):
                        
                        found = False
                        for piece in domains[row][col]:
                            if [i, j] not in delta_flow[piece]:
                                found = True

                        if not found:
                            # se todas as peças enviam fluxo para este vizinho, ele precisa de o receber
                            new_domain = []
                            for piece in domains[new_row][new_col]:
                                found = False
                                for delta_row, delta_col in delta_flow[piece]:
                                    new_new_row = new_row + delta_row
                                    new_new_col = new_col + delta_col
                                    if row == new_new_row and col == new_new_col:
                                        found = True
                                if found:
                                    new_domain += [piece]
                        else:
                            # se nenhuma peça envia fluxo para o vizinho, ele não o pode receber
                            new_domain = []
                            for piece in domains[new_row][new_col]:
                                found = False
                                for delta_row, delta_col in delta_flow[piece]:
                                    new_new_row = new_row + delta_row
                                    new_new_col = new_col + delta_col
                                    if row == new_new_row and col == new_new_col:
                                        found = True      
                                if found:
                                    found = False
                                    for new_piece in domains[row][col]:
                                        for delta_row, delta_col in delta_flow[new_piece]:
                                            new_new_row = row + delta_row
                                            new_new_col = col + delta_col
                                            if new_row == new_new_row and new_col == new_new_col:
                                                found = True
                                    if found:
                                        new_domain += [piece]
                                else:
                                    new_domain += [piece]

                        if domains[new_row][new_col] != new_domain:
                            domains[new_row][new_col] = new_domain
                            to_update += [[new_row, new_col]]
    return domains


class PipeManiaState:
    state_id = 0

    def __init__(self, board: Board):
        self.board = board
        domains = []
        for row in range(board.dimension()):
            domain_row = []
            for col in range(board.dimension()):
                piece_type = board.get_value(row, col)
                domain = []
                for direction in directions[piece_type]:
                    domain += [piece_type + direction]
                domain_row += [domain]
            domains += [domain_row]
        
        for row in range(board.dimension()):
            for col in range(board.dimension()):
                new_domain = []
                for piece in domains[row][col]:
                    ok = True
                    for delta_row, delta_col in delta_flow[piece]:
                        new_row = row + delta_row
                        new_col = col + delta_col
                        if 0 <= new_row < board.dimension() and 0 <= new_col < board.dimension():
                            found = False
                            for new_piece in domains[new_row][new_col]:
                                for new_delta_row, new_delta_col in delta_flow[new_piece]:
                                    new_new_row = new_row + new_delta_row
                                    new_new_col = new_col + new_delta_col
                                    if row == new_new_row and col == new_new_col:
                                        found = True
                            if not found:
                                ok = False
                        else:
                            ok = False
                    if ok:
                        new_domain += [piece]
                if domains[row][col] != new_domain:
                    domains[row][col] = new_domain
                    domains = update_domains(row, col, domains)

        self.domains = domains
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    def __str__(self):
        """Representação em string de uma instância da classe PipeManiaState.
        Representa visualmente as posições com apenas uma peça possível, quer por
        escolha, quer por restrição de outras escolhas."""

        s = ""
        domains = self.domains
        if not mooshak:
            for domain_row in domains:
                for domain in domain_row:
                    if len(domain) == 1:
                        s += symbols[domain[0]]
                    else:
                        s += " "
                s += "\n"
        else:
            for i in range(len(domains)):
                for j in range(len(domains)):
                    if j != 0:
                        s += "\t"
                    s += domains[i][j][0]
                s += "\n"
        return s[:-1]

    # TODO: outros metodos da classe


def degree(row, col, domains):
    res = 0
    for piece in domains[row][col]:
        for delta_row, delta_col in delta_flow[piece]:
            new_row = row + delta_row
            new_col = col + delta_col
            if len(domains[new_row][new_col]) > 1:
                res += 1
    return res


class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        
        super().__init__(PipeManiaState(board))

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        to_check = []
        for row in range(state.board.dimension()):
            for col in range(state.board.dimension()):
                if len(state.domains[row][col]) == 0:
                    # se tem um domínio vazio, valoração impossível
                    return []
                to_check += [[row, col]]
        while to_check:
            # se tem um ciclo, valoração impossível
            row, col = to_check[0]
            to_check = to_check[1:]
            if len(state.domains[row][col]) == 1:
                found = False
                new_to_check = [[row, col]]
                checked = []
                while new_to_check:
                    row, col = new_to_check[0]
                    checked += [new_to_check[0]]
                    if new_to_check[0] in to_check:
                        to_check.remove(new_to_check[0])
                    new_to_check = new_to_check[1:]
                    if len(state.domains[row][col]) == 1:
                        for delta_row, delta_col in delta_flow[state.domains[row][col][0]]:
                            new_row = row + delta_row
                            new_col = col + delta_col
                            if [new_row, new_col] not in checked + new_to_check:
                                new_to_check += [[new_row, new_col]]
                    else:
                        found = True
                if not found:
                    return []

        mrv = 4
        deg = 0
        positions = []
        for row in range(len(state.domains)):
            for col in range(len(state.domains)):
                if 1 < len(state.domains[row][col]) < mrv:
                    mrv = len(state.domains[row][col])
                    deg = degree(row, col, state.domains)
                    positions = [[row, col]]
                elif len(state.domains[row][col]) == mrv and deg == degree(row, col, state.domains):
                    positions += [[row, col]]
        row, col = positions[random.randint(0, len(positions) - 1)]
        possible_actions = []
        for piece in state.domains[row][col]:
            possible_actions += [[row, col, piece]]
        possible_actions_lcv = []
        for action in possible_actions:
            v = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if ((i == 0 and j != 0) or (i != 0 and j == 0)) and [i, j] not in delta_flow[action[2]]:
                        new_row = row + i
                        new_col = col + j
                        if 0 <= new_row < len(state.domains) and 0 <= new_col < len(state.domains):
                            for piece in state.domains[new_row][new_col]:
                                found = False
                                for delta_row, delta_col in delta_flow[piece]:
                                    new_new_row = new_row + delta_row
                                    new_new_col = new_col + delta_col
                                    if row == new_new_row and col == new_new_col:
                                        found = True
                                if found:
                                    v += 1
            possible_actions_lcv += [action + [v]]
        possible_actions_lcv = sorted(possible_actions_lcv, key=lambda x: x[3])
        possible_actions = []
        for action_lcv in possible_actions_lcv:
            possible_actions += [action_lcv[:-1]]
        return possible_actions


    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        
        new_state = copy.deepcopy(state)
        new_state.domains[action[0]][action[1]] = [action[2]]
        new_state.domains = update_domains(action[0], action[1], new_state.domains)

        return new_state


    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        global it
        it += 1

        if not mooshak:
            print("\n")
            print(it)
            print(state)

        checked = []
        to_check = [[random.randint(0, state.board.dimension() - 1), random.randint(0, state.board.dimension() - 1)]]
        while to_check:
            row, col = to_check[0]
            if len(state.domains[row][col]) != 1:
                return False
            piece = state.domains[row][col][0]
            new_to_check = []
            for delta_row, delta_col in delta_flow[piece]:
                new_row = row + delta_row
                new_col = col + delta_col
                if [new_row, new_col] not in checked + to_check + new_to_check:
                    new_to_check += [[new_row, new_col]]
            checked += [to_check[0]]
            to_check = to_check[1:] + new_to_check
        return len(checked) == len(state.domains) ** 2

def auto_adjust_column_width(file_path, sheet_name):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb[sheet_name]
    for column_cells in sheet.columns:
        sheet.column_dimensions[column_cells[0].column_letter].width = max(len(str(cell.value)) for cell in column_cells) + 2
    wb.save(file_path)

if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
    mooshak = 0

    # data = {'Test': [],
    #         'Interactions': [],
    #         'Time': []}

    data = {'Interactions': [],
            'Time': []}

    tests = 100
    for i in range(tests):
        start_time = time.time()

        it = 0
        p = PipeMania(Board.parse_instance(i))
        goal_node = depth_first_tree_search(p)
        if mooshak:
            print(goal_node.state)

        # data['Test'] += [i + 1]
        data['Interactions'] += [it]
        data['Time'] += [time.time() - start_time]

    df = pd.DataFrame(data)
    excel_path = "/mnt/c/Users/vasco/OneDrive - Universidade de Lisboa/Universidade/2ºAno/2ºSemestre/InteligênciaArtificial/Projeto/results/results.xlsx"
    df.to_excel(excel_path, index=False)
    auto_adjust_column_width(excel_path, "Sheet1")