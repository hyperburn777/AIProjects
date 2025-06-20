import random
import sys
import os
import math
from read import readInput
from write import writeOutput
from host import GO
import time
from collections import deque

class MyPlayer():
    def __init__(self):
        self.TIME_LIMIT = 9.5  # Move in 10 sec (9.5s)
        self.start_time = None
        self.filename = "num_move.txt"
        self.init_num_move(go)
        self.num_move = self.num_moves()

    def init_num_move(self, go):
        ''' Initialize numebr of moves file '''
        move_count = sum(row.count(1) + row.count(2) for row in go.board)

        # Check if number of moves file exists
        if os.path.exists(self.filename):
            # Reset for early game
            if move_count < 2:
                with open(self.filename, "w") as f:
                    f.write(str(move_count))
        else:
            # Initialize number of moves in file
            with open(self.filename, "w") as f:
                f.write(str(move_count))

    def num_moves(self):
        ''' Current number of moves '''
        with open(self.filename, "r") as f:
            return int(f.read().strip())
        
    def update_num_move(self):
        ''' Update number of moves'''
        move_count = self.num_move + 2
        if self.num_move >= 22:
            print("Deleting move number file")
            if os.path.exists(self.filename):
                os.remove(self.filename)
        else:
            print("Updating number of moves to: " + str(move_count))
            with open(self.filename, "w") as f:
                f.write(str(move_count))

    def get_input(self, go, piece_type):
        ''' Get move wiht alpha-beta pruning '''
        self.start_time = time.time()
        
        # Check if first move of game
        if self.num_move <= 1:
            self.start_move()
        
        # Otherwise use alpha-beta search
        return self.run_search()
    
    def start_move(self):
        ''' Opening move for each side '''
        if piece_type == 1:  # Black's first move
            self.update_num_move()
            return (2, 2)  # center
        elif piece_type == 2:  # White's first move
            self.update_num_move()
            if go.board[1][1] == 0:  # (1,1)
                return (1, 1)
            elif go.board[1][3] == 0:  # (1,3)
                return (1, 3)
            elif go.board[3][1] == 0:  # (3,1)
                return (3, 1)
            else:  # (3,3)
                return (3, 3)

    def run_search(self):
        ''' Call alpha-beta search '''
        best_move = None
        max_depth = 4
        depth = 1
        while (time.time() - self.start_time < self.TIME_LIMIT) and (depth <= (max_depth + (max(0, self.num_move - 8) / 4))):
            move = self.alpha_beta_search(go, piece_type, depth)
            if move:
                best_move = move
            print("The depth searched was: " + str(depth))
            depth += 1
        print("This move took: " + str(time.time() - self.start_time))
        self.update_num_move()
        return best_move if best_move else "PASS"

    def alpha_beta_search(self, go, piece_type, depth):
        ''' alpha-beta search at depth '''
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')

        depth = min(max(1, 24 - self.num_move), depth)

        possible_moves = self.get_valid_moves(go, self.num_move, piece_type)
        if not possible_moves:
            return "PASS"

        for move in possible_moves:
            new_go = self.simulate_move(go, move, piece_type)
            value = self.minimax(new_go, depth - 1, self.num_move + 1, alpha, beta, False, piece_type)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
        
        return best_move

    def minimax(self, go, depth, move_num, alpha, beta, maximizing, piece_type):
        ''' Minimax with alpha-beta pruning '''
        if depth == 0 or (time.time() - self.start_time > self.TIME_LIMIT):
            return self.evaluate(go, move_num, piece_type)

        opponent = 3 - piece_type
        possible_moves = self.get_valid_moves(go, move_num, piece_type if maximizing else opponent)

        if not possible_moves:
            return self.evaluate(go, move_num, piece_type)

        if maximizing:
            max_eval = -float('inf')
            for move in possible_moves:
                new_go = self.simulate_move(go, move, piece_type)
                eval = self.minimax(new_go, depth - 1, move_num + 1, alpha, beta, False, piece_type)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                new_go = self.simulate_move(go, move, opponent)
                eval = self.minimax(new_go, depth - 1, move_num + 1, alpha, beta, True, piece_type)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def evaluate(self, go, move_num, piece_type):
        ''' Heuristic function based on the research from the paper: https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=fb0b18e490d1d2d60e53f56b1707d7111299078f '''
        opponent = 3 - piece_type

        # Maximize stones on board
        my_stones = sum(row.count(piece_type) for row in go.board)
        opponent_stones = sum(row.count(opponent) for row in go.board)
        if piece_type == 1: # I'm playing Black
            opponent_stones += 2.5
        elif piece_type == 2: # I'm playing White
            my_stones += 2.5
        stone_score = my_stones - opponent_stones

        # Maximize liberties
        my_liberties = self.calculate_liberties(go, piece_type)
        opponent_liberties = self.calculate_liberties(go, opponent)
        liberty_score = my_liberties - opponent_liberties

        # Avoid moves on edge
        edge_penalty = self.calculate_edge_penalty(go, piece_type)

        # Connect stones & make eyes (Euler number)
        euler_score = self.calculate_euler_score(go, piece_type)

        # Weights (White): 7+3, 1, -3+3, -6 worked
        stone_weight = 7 + (3*move_num/24)
        liberty_weight = 1
        edge_weight = min(0, -3 + (3*move_num/24))
        euler_weight = -6
        
        # Weights (Black): 0+10, 0.5, -2+4, -7 worked
        if piece_type ==  1:
            stone_weight = 0 + (10*move_num/24)
            liberty_weight = 0.5
            edge_weight = min(0, -2 + (4*move_num/24))
            euler_weight = -7
        
        # Weight for end game state
        if move_num >= 23:
            stone_weight = 10000

        evaluation = (
            stone_weight * stone_score +
            liberty_weight * min(max(liberty_score, -20), 20) +
            edge_weight * edge_penalty +
            euler_weight * euler_score
        )

        return evaluation

    def calculate_liberties(self, go, piece_type):
        ''' Calculate liberties '''
        liberties = 0
        visited = set()
        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == piece_type and (i, j) not in visited:
                    queue = deque()
                    queue.append((i, j))
                    liberty = set()
                    while queue:
                        x, y = queue.popleft()
                        if (x, y) in visited:
                            continue
                        visited.add((x, y))
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < go.size and 0 <= ny < go.size:
                                if go.board[nx][ny] == 0:
                                    liberty.add((nx, ny))
                                elif go.board[nx][ny] == piece_type:
                                    queue.append((nx, ny))
                    liberties += len(liberty)
        return liberties

    def calculate_edge_penalty(self, go, piece_type):
        ''' Penalize moves on the edge '''
        edge_penalty = 0
        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == piece_type and (i == 0 or i == go.size - 1 or j == 0 or j == go.size - 1):
                    edge_penalty += 1
        return edge_penalty

    def calculate_euler_score(self, go, piece_type):
        ''' Calculate Euler number using 2x2 quad method, idea based on the paper: https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=fb0b18e490d1d2d60e53f56b1707d7111299078f  '''
        n_Q1 = 0
        n_Q3 = 0
        n_Qd = 0

        # Slide 2x2 window over the board
        for i in range(-1, go.size):
            for j in range(-1, go.size):
                window = [[0, 0], [0, 0]]

                # Fill the window, with out of bounds as 0
                for x in range(2):
                    for y in range(2):
                        if 0 <= i + x < go.size and 0 <= j + y < go.size:
                            window[x][y] = go.board[i + x][j + y]
                        else:
                            window[x][y] = 0

                # Count the number of player's stones in the window
                count = sum(row.count(piece_type) for row in window)

                # Check for Q1, Q3, and Qd
                if count == 1:
                    n_Q1 += 1
                elif count == 3:
                    n_Q3 += 1
                elif count == 2:
                    if (window[0][0] == piece_type and window[1][1] == piece_type) or (window[0][1] == piece_type and window[1][0] == piece_type):
                        n_Qd += 1

        euler_number = (n_Q1 - n_Q3 + 2 * n_Qd) / 4
        return euler_number
    
    def get_valid_moves(self, go, move_nums, piece_type):
        ''' Get ordered possible moves '''
        valid_moves = [(i, j) for i in range(go.size) for j in range(go.size) if go.valid_place_check(i, j, piece_type, test_check=True)]
        scored_moves = [(move, self.score_move(go, move, move_nums, piece_type)) for move in valid_moves]
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]

    def simulate_move(self, go, move, piece_type):
        ''' Simulates move and returns new board '''
        new_go = GO(go.size)
        new_go.board = [row[:] for row in go.board]
        new_go.place_chess(move[0], move[1], piece_type)
        new_go.remove_died_pieces(3 - piece_type)
        return new_go
    
    def score_move(self, go, move, move_nums, piece_type):
        ''' Score move based on potential game state '''
        new_go = self.simulate_move(go, move, piece_type)
        score = self.evaluate(new_go, move_nums, piece_type)
        return score

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)