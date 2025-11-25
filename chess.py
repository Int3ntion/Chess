import tkinter as tk
from copy import deepcopy
from tkinter import messagebox
from PIL import ImageTk, Image

class Chess:
    def __init__(self, time_limit=180):
        self.root = tk.Tk()
        self.root.title("Шахматы")
        self.time_limit = None
        self.time_entry = None
        self.piece_images = {}
        self.player_time = {"white": time_limit, "black": time_limit}
        self.current_player = "w"
        self.selected_piece = None
        self.board = self._initialize_board()

    def _initialize_board(self):
        board = [['No_piece' for _ in range(8)] for _ in range(8)]

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

        self.b_king_pos = (0, 4)
        self.w_king_pos = (7, 4)

        return board

    def _setting(self):
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        title_label = tk.Label(
            self.root,
            text = "Добро пожаловать в шахматы!",
            font = ("Arial", 16, "bold"),
            pady = 10
        )
        title_label.pack()

        instruction_label = tk.Label(
            self.root,
            text = "Введите время на игрока (в секундах)",
            font = ("Arial", 12, "italic")
        )
        instruction_label.pack()

        self.time_entry = tk.Entry(
            self.root,
            width = 20,
            font = ("Arial", 12),
            justify = "center"
        )
        self.time_entry.pack(pady=10)

        start_button = tk.Button(
            self.root,
            text = "Начать игру",
            font = ("Arial", 12),
            bg = "#4CAF50",
            fg = "white",
            padx = 20,
            pady = 5,
            command = self._start_game
        )
        start_button.pack(pady=10)

        self.root.mainloop()

    def _start_game(self):
        time_input = self.time_entry.get().strip().replace(',', '.')

        if not time_input:
            self.time_limit = 180
            self.root.destroy()
            self._setup_board()
            return

        try:
            time_per_player = float(time_input)
            if time_per_player <= 0:
                messagebox.showerror("Ошибка", "Время должно быть положительным числом!")
                return

            self.time_limit = time_per_player
            self.root.destroy()
            self._setup_board()

        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Пожалуйста, введите корректное число (например, 30)!"
            )

    def _setup_board(self):
        self.board_window = tk.Tk()
        self.board_window.title("Шахматы")
        self.board_window.resizable(False, False)
        self._load_piece_images()

        cell_size = 80

        canvas_width = 8 * cell_size
        canvas_height = 8 * cell_size

        canvas = tk.Canvas(
            self.board_window,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )
        self.canvas = canvas
        canvas.pack()
        self.canvas.bind("<Button-1>", self._on_click)
        self._valid_moves()
        self._draw_board()

    def _draw_board(self, cell_size=80):
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    cell_color = "#F0D9B5"
                    text_color = "#B58863"
                else:
                    cell_color = "#B58863"
                    text_color = "#F0D9B5"

                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                self.canvas.create_rectangle(x1, y1, x2, y2, fill = cell_color, outline = cell_color)

                if row == 7:
                    letter = chr(ord('a') + col)
                    text_x = x1 + 3
                    text_y = y1 + cell_size
                    self.canvas.create_text(
                        text_x,
                        text_y,
                        text = letter,
                        font = ("Arial", 9),
                        fill = text_color,
                        anchor = 'sw'
                    )
                if col == 7:
                    digit = 8 - row
                    text_x = x1 - 3 + cell_size
                    text_y = y1 + 3
                    self.canvas.create_text(
                        text_x,
                        text_y,
                        text = str(digit),
                        font = ("Arial", 9),
                        fill = text_color,
                        anchor = 'ne'
                    )
                self._draw_piece(row, col)

    def _load_piece_images(self):
        piece_names = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']

        images = {}
        for color in colors:
            for piece in piece_names:
                img_path = f"pieces/{color}_{piece}.png"
                img = Image.open(img_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                images[f"{color}_{piece}"] = ImageTk.PhotoImage(img)
        self.piece_images = images

    def _draw_piece(self, row, col, cell_size=80):
        piece = self.board[row][col]
        if piece != 'No_piece':
            img_key = ""
            x = col * cell_size
            y = row * cell_size
            if piece[:2] == "p_":
                img_key = f"{piece[2:]}_pawn"
            elif piece[:2] == "r_":
                img_key = f"{piece[2:]}_rook"
            elif piece[:2] == "n_":
                img_key = f"{piece[2:]}_knight"
            elif piece[:2] == "b_":
                img_key = f"{piece[2:]}_bishop"
            elif piece[:2] == "q_":
                img_key = f"{piece[2:]}_queen"
            elif piece[:2] == "k_":
                img_key = f"{piece[2:]}_king"

            self.canvas.create_image(x, y, image=self.piece_images[img_key], anchor='nw')

    def _valid_rook_move(self, row, col, color):
        piece = []
        if row != 0:
            for ch_r in range(1, row + 1):
                if self.board[row - ch_r][col] == "No_piece":
                    piece.append((row - ch_r, col))
                elif self.board[row - ch_r][col][2] != color:
                    piece.append((row - ch_r, col))
                    break
                else:
                    break
        if row != 7:
            for ch_r in range(1, 8 - row):
                if self.board[row + ch_r][col] == "No_piece":
                    piece.append((row + ch_r, col))
                elif self.board[row + ch_r][col][2] != color:
                    piece.append((row + ch_r, col))
                    break
                else:
                    break
        if col != 0:
            for ch_c in range(1, col + 1):
                if self.board[row][col - ch_c] == "No_piece":
                    piece.append((row, col - ch_c))
                elif self.board[row][col - ch_c][2] != color:
                    piece.append((row, col - ch_c))
                    break
                else:
                    break
        if col != 7:
            for ch_c in range(1, 8 - col):
                if self.board[row][col + ch_c] == "No_piece":
                    piece.append((row, col + ch_c))
                elif self.board[row][col + ch_c][2] != color:
                    piece.append((row, col + ch_c))
                    break
                else:
                    break

        return piece

    def _valid_bishop_move(self, row, col, color):
        piece = []
        nw, sw, se, ne = True, True, True, True
        for ch in range(1, 7):
            if nw:
                if row - ch >= 0 and col - ch >= 0 and self.board[row - ch][col - ch] == "No_piece":
                    piece.append((row - ch, col - ch))
                elif row - ch >= 0 and col - ch >= 0 and self.board[row - ch][col - ch][2] != color:
                    piece.append((row - ch, col - ch))
                    nw = False
                else:
                    nw = False
            if ne:
                if row - ch >= 0 and col + ch <= 7 and self.board[row - ch][col + ch] == "No_piece":
                    piece.append((row - ch, col + ch))
                elif row - ch >= 0 and col + ch <= 7 and self.board[row - ch][col + ch][2] != color:
                    piece.append((row - ch, col + ch))
                    ne = False
                else:
                    ne = False
            if se:
                if row + ch <= 7 and col + ch <= 7 and self.board[row + ch][col + ch] == "No_piece":
                    piece.append((row + ch, col + ch))
                elif row + ch <= 7 and col + ch <= 7 and self.board[row + ch][col + ch][2] != color:
                    piece.append((row + ch, col + ch))
                    se = False
                else:
                    se = False
            if sw:
                if row + ch <= 7 and col - ch >= 0 and self.board[row + ch][col - ch] == "No_piece":
                    piece.append((row + ch, col - ch))
                elif row + ch <= 7 and col - ch >= 0 and self.board[row + ch][col - ch][2] != color:
                    piece.append((row + ch, col - ch))
                    sw = False
                else:
                    sw = False
        return piece

    def _valid_moves(self):
        self.valid_moves = deepcopy(self.board)
        for row in range(8):
            for col in range(8):
                piece = self.valid_moves[row][col]
                if piece == 'No_piece':
                    self.valid_moves[row][col] = []
                elif piece == "p_white":
                    piece = []
                    if row-1 >= 0 and self.board[row-1][col] == "No_piece":
                        piece.append((row-1, col))
                    if col+1 <= 7 and row-1 >= 0 and self.board[row-1][col+1][2] == "b":
                        piece.append((row-1, col+1))
                    if col-1 >= 0 and row-1 >= 0 and self.board[row-1][col-1][2] == "b":
                        piece.append((row-1, col-1))
                    if row == 6 and self.board[row-1][col] == "No_piece" and self.board[row-2][col] == "No_piece":
                        piece.append((row-2, col))
                    self.valid_moves[row][col] = piece
                elif piece == "p_black":
                    piece = []
                    if row+1 <= 7 and self.board[row+1][col] == "No_piece":
                        piece.append((row+1, col))
                    if col-1 >= 0 and row+1 <= 7 and self.board[row+1][col-1][2] == "w":
                        piece.append((row+1, col-1))
                    if col+1 <= 7 and row+1 <= 7 and self.board[row+1][col+1][2] == "w":
                        piece.append((row+1, col+1))
                    if row == 1 and self.board[row+1][col] == "No_piece" and self.board[row+2][col] == "No_piece":
                        piece.append((row+2, col))
                    self.valid_moves[row][col] = piece
                elif piece[0] == "n":
                    color = piece[2]
                    piece = []
                    for ch_r in 1, -1, 2, -2:
                        if abs(ch_r) == 2:
                            ch_col = [1, -1]
                        else:
                            ch_col = [2, -2]
                        for ch_c in ch_col:
                            if 0 <= row+ch_r <= 7 and 0 <= col+ch_c <= 7 and self.board[row+ch_r][col+ch_c][2] != color:
                                piece.append((row+ch_r, col+ch_c))
                    self.valid_moves[row][col] = piece
                elif piece[0] == "r":
                    color = piece[2]
                    self.valid_moves[row][col] = self._valid_rook_move(row, col, color)
                elif piece[0] == "b":
                    color = piece[2]
                    self.valid_moves[row][col] = self._valid_bishop_move(row, col, color)
                elif piece[0] == "q":
                    color = piece[2]
                    self.valid_moves[row][col] = self._valid_rook_move(row, col, color) + self._valid_bishop_move(row, col, color)
                else:
                    color = piece[2]
                    piece = []
                    for ch_r in -1, 0, 1:
                        for ch_c in -1, 0, 1:
                            if 0 <= row+ch_r <= 7 and 0 <= col+ch_c <= 7 and self.board[row+ch_r][col+ch_c][2] != color:
                                piece.append((row+ch_r, col+ch_c))
                    self.valid_moves[row][col] = piece
        return self.valid_moves

    def _draw_pos_moves(self, row, col):
        for (pos_c, pos_r) in self.valid_moves[row][col]:
            if self.board[pos_c][pos_r] == "No_piece":
                self.canvas.create_oval(pos_r * 80 + 30, pos_c * 80 + 30, pos_r * 80 + 50, pos_c * 80 + 50,
                                        fill="#829769", outline="#829769")
            else:
                c = 18
                self.canvas.create_polygon(pos_r * 80, pos_c * 80, pos_r * 80 + c, pos_c * 80, pos_r * 80,
                                           pos_c * 80 + c, fill="#829769", outline="#829769")
                self.canvas.create_polygon(pos_r * 80, (pos_c + 1) * 80, pos_r * 80, (pos_c + 1) * 80 - c,
                                           pos_r * 80 + c, (pos_c + 1) * 80, fill="#829769", outline="#829769")
                self.canvas.create_polygon((pos_r + 1) * 80, (pos_c + 1) * 80, (pos_r + 1) * 80, (pos_c + 1) * 80 - c,
                                           (pos_r + 1) * 80 - c, (pos_c + 1) * 80, fill="#829769", outline="#829769")
                self.canvas.create_polygon((pos_r + 1) * 80, pos_c * 80, (pos_r + 1) * 80 - c, pos_c * 80,
                                           (pos_r + 1) * 80, pos_c * 80 + c, fill="#829769", outline="#829769")

    def _on_click(self, event):
        col = event.x // 80
        row = event.y // 80

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        piece = self.board[row][col]
        if self.selected_piece is not None and piece[2] != self.current_player and (row, col) in self.valid_moves[self.selected_piece[0]][self.selected_piece[1]]:
            self._make_move(row, col)
        else:
            if self.selected_piece is None:
                if piece != "No_piece" and piece[2] == self.current_player:
                    self.selected_piece = (row, col)
                    self.canvas.delete("all")
                    self._draw_board()
                    self.canvas.create_rectangle(col*80, row*80, (col+1)*80, (row+1)*80, fill="#829769", outline="#829769")
                    self._draw_piece(row, col)
                    self._draw_pos_moves(row, col)

            elif self.selected_piece == (row, col):
                self.canvas.delete("all")
                self._draw_board()
                self.selected_piece = None
            elif piece[2] == self.current_player:
                self.canvas.delete("all")
                self._draw_board()
                self.canvas.create_rectangle(col*80, row*80, (col+1)*80, (row+1)*80, fill="#829769", outline="#829769")
                self._draw_piece(row, col)
                self.selected_piece = (row, col)
                self._draw_pos_moves(row, col)
            self._checked_king()

    def _make_move(self, row, col):
        if self.selected_piece == self.w_king_pos:
            self.w_king_pos = (row, col)
        elif self.selected_piece == self.b_king_pos:
            self.b_king_pos = (row, col)
        self.board[row][col] = self.board[self.selected_piece[0]][self.selected_piece[1]]
        self.board[self.selected_piece[0]][self.selected_piece[1]] = "No_piece"
        self._valid_moves()
        self.canvas.delete("all")
        self._draw_board()
        self._checked_king()
        if self.current_player == "w":
            self.current_player = "b"
            self._simulate("b")
            return
        self.current_player = "w"
        self._simulate("w")
        self._is_mate()
        self._is_stalemate()

    def _checked_king(self):
        if self._is_check('w'):
            king_on_check = self.w_king_pos
        elif self._is_check('b'):
            king_on_check = self.b_king_pos
        if self._is_check('w') or self._is_check('b'):
            self.canvas.create_rectangle(king_on_check[1] * 80, king_on_check[0] * 80, (king_on_check[1] + 1) * 80,
                                         (king_on_check[0] + 1) * 80, outline='red', width=4)

    def _is_check(self, color):
        if color == "w":
            king = self._find_king("white")
            opp_col = "b"
        else:
            king = self._find_king("black")
            opp_col = "w"
        for row in range(8):
            for col in range(8):
                if self.board[row][col][2] == opp_col and king in self.valid_moves[row][col]:
                    return True
        return False

    def _find_king(self, color):
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == f'k_{color}':
                    return (row, col)

    def _simulate(self, player):
        valid_after_simulate = [[[] for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                moves = self.valid_moves[row][col]
                for move in range(len(moves)):
                    row_move, col_move = moves[move]
                    on_cell_piece = self.board[row_move][col_move]
                    self.board[row][col], self.board[row_move][col_move] = "No_piece", self.board[row][col]
                    self._valid_moves()
                    if player == "w":
                        if not self._is_check("w"):
                            valid_after_simulate[row][col].append(moves[move])
                    else:
                        if not self._is_check("b"):
                            valid_after_simulate[row][col].append(moves[move])
                    self.board[row][col], self.board[row_move][col_move] = self.board[row_move][col_move], on_cell_piece
                    self._valid_moves()
        self.valid_moves = valid_after_simulate

    def _no_moves(self):
        for row in range(8):
            for col in range(8):
                if self.board[row][col][2] == self.current_player and self.valid_moves[row][col] != []:
                    return False
        print("Нет ходов")
        return True

    def _is_mate(self):
        if self._is_check(self.current_player) and self._no_moves():
            print("Мат")
            return True
        return False

    def _is_stalemate(self):
        if not self._is_check(self.current_player) and self._no_moves():
            print("Пат")
            return True
        return False

    def run(self):
        self._setting()

if __name__ == "__main__":
    chess = Chess()
    chess.run()