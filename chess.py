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
        self.current_player = "white"
        self.selected_piece_pos = None
        self.board = self._initialize_board()
        self.king_moved = [False, False]
        self.rook_moved = [[False, False], [False, False]]
        self.en_passant_target = None

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
            text = "Введите время на игрока (в минутах)",
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
        if piece != 'No_piece' and piece[0] != 's':
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
                if self.board[row - ch_r][col] == "No_piece" or self.board[row - ch_r][col][0] == "s":
                    piece.append((row - ch_r, col))
                elif self.board[row - ch_r][col][2] != color:
                    piece.append((row - ch_r, col))
                    break
                else:
                    break
        if row != 7:
            for ch_r in range(1, 8 - row):
                if self.board[row + ch_r][col] == "No_piece" or self.board[row + ch_r][col][0] == "s":
                    piece.append((row + ch_r, col))
                elif self.board[row + ch_r][col][2] != color:
                    piece.append((row + ch_r, col))
                    break
                else:
                    break
        if col != 0:
            for ch_c in range(1, col + 1):
                if self.board[row][col - ch_c] == "No_piece" or self.board[row][col - ch_c][0] == "s":
                    piece.append((row, col - ch_c))
                elif self.board[row][col - ch_c][2] != color:
                    piece.append((row, col - ch_c))
                    break
                else:
                    break
        if col != 7:
            for ch_c in range(1, 8 - col):
                if self.board[row][col + ch_c] == "No_piece" or self.board[row][col + ch_c][0] == "s":
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
                if row - ch >= 0 and col - ch >= 0 and (self.board[row - ch][col - ch] == "No_piece" or self.board[row - ch][col - ch][0] == "s"):
                    piece.append((row - ch, col - ch))
                elif row - ch >= 0 and col - ch >= 0 and self.board[row - ch][col - ch][2] != color:
                    piece.append((row - ch, col - ch))
                    nw = False
                else:
                    nw = False
            if ne:
                if row - ch >= 0 and col + ch <= 7 and (self.board[row - ch][col + ch] == "No_piece" or self.board[row - ch][col + ch][0] == "s"):
                    piece.append((row - ch, col + ch))
                elif row - ch >= 0 and col + ch <= 7 and self.board[row - ch][col + ch][2] != color:
                    piece.append((row - ch, col + ch))
                    ne = False
                else:
                    ne = False
            if se:
                if row + ch <= 7 and col + ch <= 7 and (self.board[row + ch][col + ch] == "No_piece" or self.board[row + ch][col + ch][0] == "s"):
                    piece.append((row + ch, col + ch))
                elif row + ch <= 7 and col + ch <= 7 and self.board[row + ch][col + ch][2] != color:
                    piece.append((row + ch, col + ch))
                    se = False
                else:
                    se = False
            if sw:
                if row + ch <= 7 and col - ch >= 0 and (self.board[row + ch][col - ch] == "No_piece" or self.board[row + ch][col - ch][0] == "s"):
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
                if piece == 'No_piece' or piece[0] == "s":
                    self.valid_moves[row][col] = []
                elif piece == "p_white":
                    piece = []
                    if row-1 >= 0 and self.board[row-1][col] == "No_piece":
                        piece.append((row-1, col))
                    if col+1 <= 7 and row-1 >= 0 and (self.board[row-1][col+1][2] == "b"):
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
                        ch_col = [1, -1] if abs(ch_r) == 2 else [2, -2]
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
            if self.board[pos_c][pos_r] == "No_piece" or \
                    (self.board[pos_c][pos_r][0] == "s" and self.board[self.selected_piece_pos[0]][self.selected_piece_pos[1]][0] != "p"):
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
        if self.selected_piece_pos is not None and piece[2] != self.current_player[0] and (row, col) in self.valid_moves[self.selected_piece_pos[0]][self.selected_piece_pos[1]]:
            self._make_move(row, col)
        else:
            if self.selected_piece_pos is None:
                if piece != "No_piece" and piece[2] == self.current_player[0]:
                    self.selected_piece_pos = (row, col)
                    self.canvas.delete("all")
                    self._draw_board()
                    self.canvas.create_rectangle(col*80, row*80, (col+1)*80, (row+1)*80, fill="#829769", outline="#829769")
                    self._draw_piece(row, col)
                    self._draw_pos_moves(row, col)

            elif self.selected_piece_pos == (row, col):
                self.canvas.delete("all")
                self._draw_board()
                self.selected_piece_pos = None
            elif piece[2] == self.current_player[0]:
                self.canvas.delete("all")
                self._draw_board()
                self.canvas.create_rectangle(col*80, row*80, (col+1)*80, (row+1)*80, fill="#829769", outline="#829769")
                self._draw_piece(row, col)
                self.selected_piece_pos = (row, col)
                self._draw_pos_moves(row, col)
            self.highlight_checked_king()

    def _make_move(self, row, col):
        piece = self.board[self.selected_piece_pos[0]][self.selected_piece_pos[1]]
        for r in range(8):
            for c in range(8):
                if self.board[r][c][0] == "s" and (r, c) != (row, col):
                    self.board[r][c] = "No_piece"
        if piece[0] == 'p' and abs(self.selected_piece_pos[0] - row) == 2:
            piece_pos = self.selected_piece_pos
            if self.board[piece_pos[0]][piece_pos[1]] == "p_white":
                self.board[piece_pos[0] - 1][piece_pos[1]] = "s_white"
            else:
                self.board[piece_pos[0] + 1][piece_pos[1]] = "s_black"
            self.en_passant_target = (piece_pos[0] + 2, piece_pos[1]) if self.board[piece_pos[0]][piece_pos[1]][2] == "b" \
                else (piece_pos[0] - 2, piece_pos[1])
        if self.board[row][col][0] == "s" and piece[0] == "p":
            self.board[self.en_passant_target[0]][self.en_passant_target[1]] = "No_piece"
        if self.selected_piece_pos == self.w_king_pos:
            if col - self.w_king_pos[1] == 2:
                self.w_king_pos = (row, col)
                self.board[row][col-1] = "r_white"
                self.board[row][7] = "No_piece"
            elif col - self.w_king_pos[1] == -2:
                self.w_king_pos = (row, col)
                self.board[row][col+1] = "r_white"
                self.board[row][0] = "No_piece"
            self.w_king_pos = (row, col)
            self.king_moved[1] = True
        elif self.selected_piece_pos == self.b_king_pos:
            if col - self.b_king_pos[1] == 2:
                self.b_king_pos = (row, col)
                self.board[row][col-1] = "r_black"
                self.board[row][7] = "No_piece"
            elif col - self.b_king_pos[1] == -2:
                self.b_king_pos = (row, col)
                self.board[row][col+1] = "r_black"
                self.board[row][0] = "No_piece"
            self.b_king_pos = (row, col)
            self.king_moved[0] = True
        for x in 0, 1:
            for y in 0, 1:
                if self.selected_piece_pos == (x * 7, y * 7):
                    self.rook_moved[x][y] = True
        self.board[row][col] = piece
        self.board[self.selected_piece_pos[0]][self.selected_piece_pos[1]] = "No_piece"
        if piece == "p_white" and row == 0:
            self._promote(row, col)
        elif piece == "p_black" and row == 7:
            self._promote(row, col)
        else:
            self._valid_moves()
            self.canvas.delete("all")
            self._draw_board()
            self.highlight_checked_king()
            if self.current_player == "white":
                self.current_player = "black"
                self._simulate("b")
            else:
                self.current_player = "white"
                self._simulate("w")
            self.castle()
            self._is_mate()
            self._is_stalemate()

    def highlight_checked_king(self):
        if self._is_square_under_attack(self.w_king_pos[0], self.w_king_pos[1], 'w'):
            king_on_check = self.w_king_pos
        elif self._is_square_under_attack(self.b_king_pos[0], self.b_king_pos[1], 'b'):
            king_on_check = self.b_king_pos
        if self._is_square_under_attack(self.w_king_pos[0], self.w_king_pos[1], 'w') or \
                self._is_square_under_attack(self.b_king_pos[0], self.b_king_pos[1], 'b'):
            self.canvas.create_rectangle(king_on_check[1] * 80, king_on_check[0] * 80, (king_on_check[1] + 1) * 80,
                                         (king_on_check[0] + 1) * 80, outline='red', width=4)

    def _is_square_under_attack(self, row, col, color):
        opp_col = "b" if color == "w" else "w"
        for brd_r in range(8):
            for brd_c in range(8):
                if self.board[brd_r][brd_c][2] == opp_col and (row, col) in self.valid_moves[brd_r][brd_c]:
                    return True
        return False

    def _simulate(self, player):
        valid_after_simulate = [[[] for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                moves = self.valid_moves[row][col]
                for move in moves:
                    row_move, col_move = move
                    on_cell_piece = self.board[row_move][col_move]
                    self.board[row][col], self.board[row_move][col_move] = "No_piece", self.board[row][col]
                    self._valid_moves()
                    if player == "w":
                        if self.board[row_move][col_move] == "k_white":
                            if not self._is_square_under_attack(row_move, col_move, "w"):
                                valid_after_simulate[row][col].append(move)
                        elif not self._is_square_under_attack(self.w_king_pos[0], self.w_king_pos[1], "w"):
                            valid_after_simulate[row][col].append(move)
                    else:
                        if self.board[row_move][col_move] == "k_black":
                            if not self._is_square_under_attack(row_move, col_move, "b"):
                                valid_after_simulate[row][col].append(move)
                        elif not self._is_square_under_attack(self.b_king_pos[0], self.b_king_pos[1], "b"):
                            valid_after_simulate[row][col].append(move)
                    self.board[row][col], self.board[row_move][col_move] = self.board[row_move][col_move], on_cell_piece
                    self._valid_moves()
        self.valid_moves = valid_after_simulate

    def _no_moves(self):
        for row in range(8):
            for col in range(8):
                if self.board[row][col][2] == self.current_player[0] and self.valid_moves[row][col] != []:
                    return False
        print("No valid moves")
        return True

    def _is_mate(self):
        king = self.w_king_pos if self.current_player == "white" else self.b_king_pos
        if self._is_square_under_attack(king[0], king[1], self.current_player[0]) and self._no_moves():
            print("Мат")
            return True
        return False

    def _is_stalemate(self):
        king = self.w_king_pos if self.current_player == "white" else self.b_king_pos
        if not self._is_square_under_attack(king[0], king[1], self.current_player[0]) and self._no_moves():
            print("Пат")
            return True
        return False

    def castle(self):
        for c in 0, 1:
            color = "w" if c == 1 else "b"
            if not(self.rook_moved[c][0] or self.king_moved[c]) and \
                    all(x == "No_piece" for x in self.board[c*7][1:4]) and \
                    all(not(self._is_square_under_attack(c*7, x, color)) for x in (2, 3, 4)):
                self.valid_moves[c*7][4].append((c*7, 2))
            if not(self.rook_moved[c][1] or self.king_moved[c]) and \
                    all(x == "No_piece" for x in self.board[c*7][5:7]) and \
                    all(not(self._is_square_under_attack(c*7, x, color)) for x in (4, 5 ,6)):
                self.valid_moves[c * 7][4].append((c * 7, 6))

    def _promote(self, row, col):
        # Проверяем, что пешка достигла последней горизонтали
        if (self.current_player == "white" and row == 0) or (self.current_player == "black" and row == 7):
            # Создаем новое окно для выбора фигуры
            promote_window = tk.Toplevel(self.board_window)
            promote_window.title("Превращение пешки")
            promote_window.geometry("370x90")
            promote_window.resizable(False, False)

            # Запрещаем закрытие окна через крестик
            promote_window.protocol("WM_DELETE_WINDOW", lambda: None)

            # Определяем цвет пешки
            color = self.current_player

            # Список фигур для превращения (без пешки и короля)
            pieces = ['queen', 'rook', 'bishop', 'knight']

            def select_piece(piece_type):
                # Формируем название новой фигуры
                new_piece = f"{piece_type[0] if piece_type != "knight" else "n"}_{color}"
                # Заменяем пешку на выбранную фигуру
                self.board[row][col] = new_piece

                # Обновляем валидные ходы после превращения
                self._valid_moves()

                # Проверяем, не поставили ли мы шах королю противника
                opponent_king = self.b_king_pos if color == "white" else self.w_king_pos
                is_check = self._is_square_under_attack(opponent_king[0], opponent_king[1],
                                                        "b" if color == "white" else "w")

                # Обновляем отображение
                self.canvas.delete("all")
                self._draw_board()

                if is_check:
                    # Выделяем короля под шахом
                    self.highlight_checked_king()

                # Передаем ход противнику
                self.current_player = "black" if self.current_player == "white" else "white"
                self._simulate("b" if self.current_player == "black" else "w")
                self.castle()
                self._is_mate()
                self._is_stalemate()

                # Закрываем окно выбора
                promote_window.destroy()

            # Размещаем кнопки с изображениями фигур
            for i, piece in enumerate(pieces):
                img_key = f"{color}_{piece}"
                btn = tk.Button(
                    promote_window,
                    image=self.piece_images[img_key],
                    command=lambda pt=piece: select_piece(pt),
                    bd=0
                )
                btn.grid(row=0, column=i, padx=5, pady=5)

            # Делаем окно модальным
            promote_window.grab_set()
            promote_window.focus_set()

    def run(self):
        self._setting()

if __name__ == "__main__":
    chess = Chess()
    chess.run()