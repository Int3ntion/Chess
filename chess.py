import tkinter as tk

class Chess:
    def __init__(self, time_limit=180):
        self.root = tk.Tk()
        self.root.title("Шахматы")
        self.time_limit = time_limit
        self.player_time = {"white": time_limit, "black": time_limit}
        self.current_player = "white"
        self.selected_piece = None
        self.game_on_run = True
        self.board = self._initialize_board()

    def _initialize_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]

        for col in range(8):
            board[6][col] = "p_white"
        board[7][0], board[7][7] = "r_white", "r_white"
        board[7][1], board[7][6] = "n_white", "n_white"
        board[7][2], board[7][5] = "b_white", "b_white"
        board[7][3] = "q_white"
        board[7][4] = "k_white"

        for col in range(8):
            board[1][col] = "p_black"
        board[0][0], board[0][7] = "r_black", "r_black"
        board[0][1], board[0][6] = "n_black", "n_black"
        board[0][2], board[0][5] = "b_black", "b_black"
        board[0][3] = "q_black"
        board[0][4] = "k_black"

        return board
