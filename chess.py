import tkinter as tk
from copy import deepcopy
from tkinter import messagebox
from PIL import ImageTk, Image


class UnknownPiece(Exception):
    '''
    Вызывается, если на доске возникает неизвестная фигура (не входящая в стандартный набор фигур в шахматах)
    '''
    pass


class PieceNotOnBoard(Exception):
    '''
    Вызывается, если фигура, с которой пытаются работать, находится на доске, или выполняемый ход приводит к выходу за пределы доски
    '''
    pass


class CantFindImages(Exception):
    '''
    Вызывается, если не получилось найти изображение фигуры во введённой директории
    '''
    pass


class Chess:
    '''
    Класс, реализующий логику и визуализацию игры "Шахматы"
    '''

    def __init__(self, pth='pieces'):
        '''
        :param pth: Название директории, в которой находятся изображения фигур
        '''
        self.path = pth
        self.time_entry = None
        self.piece_images = {}
        self.current_player = "white"
        self.selected_piece_pos = None
        self.board = self._initialize_board()
        self.king_moved = [False, False]
        self.rook_moved = [[False, False], [False, False]]
        self.en_passant_target = None
        self.timer_labels = {}
        self.timer_running = False
        self.after_id = None

    def _initialize_board(self) -> list[list[str]]:
        '''
        Инициализация расстановки фигур в начале партии

        :return: None
        '''
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
        '''
        Вывод окна приветствия и настройки времени на игрока

        :return: None
        '''
        self.root = tk.Tk()
        self.root.title("Шахматы")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        title_label = tk.Label(
            self.root,
            text="Добро пожаловать в шахматы!",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()

        instruction_label = tk.Label(
            self.root,
            text="Введите время на игрока (в минутах)",
            font=("Arial", 12, "italic")
        )
        instruction_label.pack()

        self.time_entry = tk.Entry(
            self.root,
            width=20,
            font=("Arial", 12),
            justify="center"
        )
        self.time_entry.pack(pady=10)

        start_button = tk.Button(
            self.root,
            text="Начать игру",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=5,
            command=self._start_game
        )
        start_button.pack(pady=10)

        self.root.mainloop()

    def _start_game(self):
        '''
        Закрывает окно настройки при успешном вводе времени и запускает окно с доской

        :return: None
        '''
        time_input = self.time_entry.get().strip().replace(',', '.')

        if not time_input:
            self.time_limit = 600
        else:
            try:
                time_in_minutes = float(time_input)
                if time_in_minutes <= 0:
                    messagebox.showerror("Ошибка", "Время должно быть положительным числом!")
                    return
                self.time_limit = int(time_in_minutes * 60)

            except ValueError:
                messagebox.showerror(
                    "Ошибка",
                    "Пожалуйста, введите корректное число (например, 10, 5,5, 15)!"
                )
                return
        self.player_time = {"white": self.time_limit, "black": self.time_limit}
        try:
            self.root.destroy()
            self._setup_board()
        except tk.TclError:
            pass
        except CantFindImages:
            print("Не удалось загрузить изображения фигур")

    def _setup_board(self):
        '''
        Открывает окно доски, в котором выводит время на игрока, пустой холст для отрисовки доски и кнопку перезапуска игры

        :return: None
        '''
        try:
            self.board_window = tk.Tk()
            self.board_window.title("Шахматы")
            self.board_window.resizable(False, False)
            while True:
                try:
                    self._load_piece_images()
                    break
                except CantFindImages:
                    self.path = input("Не получилось загрузить изображения\n"
                                      "Пожалуйста, введите правильный путь к папке с изображениями фигур\n-> ").strip(
                        '/')
                    self.path = 'pieces' if self.path == '' else self.path

            cell_size = 80

            canvas_width = 8 * cell_size
            canvas_height = 8 * cell_size

            timer_frame = tk.Frame(self.board_window)
            timer_frame.pack(pady=5)

            tk.Label(timer_frame, text="Белые", font=("Arial", 12)).pack(side='left', padx=10)
            self.timer_labels["white"] = tk.Label(
                timer_frame, text=self._format_time(self.player_time["white"]), font=("Arial", 12, "bold"), fg="black"
            )
            self.timer_labels["white"].pack(side='left', padx=5)

            tk.Label(timer_frame, text="Чёрные", font=("Arial", 12)).pack(side='right', padx=10)
            self.timer_labels["black"] = tk.Label(
                timer_frame, text=self._format_time(self.player_time["black"]), font=("Arial", 12, "bold"), fg="black"
            )
            self.timer_labels["black"].pack(side='right', padx=5)

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
            self._start_timer()

            tk.Button(
                self.board_window,
                text="Начать заново",
                font=("Arial", 10),
                bg="#4CAF50",
                fg="white",
                padx=10,
                pady=5,
                command=lambda: self._restart_game(self.board_window)
            ).pack(pady=10)
        except tk.TclError:
            print("Failed to load board window")

    def _draw_board(self, cell_size=80):
        '''
        Рисует на созданном холсте клетки, координаты, вызывает рисование фигур

        :param cell_size: размер клетки шахматной доски
        :return: None
        '''
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

                try:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=cell_color, outline=cell_color)
                except tk.TclError:
                    print("No canvas to draw a board")

                if row == 7:
                    letter = chr(ord('a') + col)
                    text_x = x1 + 3
                    text_y = y1 + cell_size
                    self.canvas.create_text(
                        text_x,
                        text_y,
                        text=letter,
                        font=("Arial", 9),
                        fill=text_color,
                        anchor='sw'
                    )
                if col == 7:
                    digit = 8 - row
                    text_x = x1 - 3 + cell_size
                    text_y = y1 + 3
                    self.canvas.create_text(
                        text_x,
                        text_y,
                        text=str(digit),
                        font=("Arial", 9),
                        fill=text_color,
                        anchor='ne'
                    )
                try:
                    self._draw_piece(row, col)
                except UnknownPiece:
                    self.board[row][col] = "No_piece"

    def _load_piece_images(self):
        '''
        Загружает изображения фигур из директории, введённой пользователем

        :return: None
        :raises CantFindImages: Если не удалось загрузить изображения фигур
        '''
        piece_names = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']

        images = {}
        try:
            for color in colors:
                for piece in piece_names:
                    img_path = f"{self.path}/{color}_{piece}.png"
                    img = Image.open(img_path)
                    img = img.resize((80, 80), Image.Resampling.LANCZOS)
                    images[f"{color}_{piece}"] = ImageTk.PhotoImage(img)
        except FileNotFoundError:
            raise CantFindImages
        self.piece_images = images

    def _draw_piece(self, row, col, cell_size=80):
        '''
        Рисует фигуру в заданной клетке

        :param row: Ряд, в котором необходимо нарисовать фигуру
        :param col: Столбец, в котором необходимо нарисовать фигуру
        :param cell_size: Размер клетки доски
        :return: None
        :raises UnknownPiece: Если для рисования на доске находится неизвестная фигура
        '''
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
            try:
                self.canvas.create_image(x, y, image=self.piece_images[img_key], anchor='nw')
            except KeyError:
                raise UnknownPiece

    def _valid_rook_move(self, row, col, color) -> list:
        '''
        Перебор всех возможных ходов ладьёй

        :param row: Ряд, в котором находится фигура
        :param col: Столбец, в который находится фигура
        :param color: Цвет фигуры
        :return: Возможные ходы ладьёй
        :raises PieceNotOnBoard: Если фигура, для которой выполняется подбор, находится не в пределах доски
        '''
        if 0 <= row < 8 and 0 <= col < 8:
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
        else:
            raise PieceNotOnBoard

        return piece

    def _valid_bishop_move(self, row, col, color) -> list:
        '''
        Перебор всех возможных ходов слоном

        :param row: Ряд, в котором находится фигура
        :param col: Столбец, в который находится фигура
        :param color: Цвет фигуры
        :return: Возможные ходы слоном
        :raises PieceNotOnBoard: Если фигура, для которой выполняется подбор, находится не в пределах доски
        '''
        if 0 <= row < 8 and 0 <= col < 8:
            piece = []
            nw, sw, se, ne = True, True, True, True
            for ch in range(1, 7):
                if nw:
                    if row - ch >= 0 and col - ch >= 0 and (
                            self.board[row - ch][col - ch] == "No_piece" or self.board[row - ch][col - ch][0] == "s"):
                        piece.append((row - ch, col - ch))
                    elif row - ch >= 0 and col - ch >= 0 and self.board[row - ch][col - ch][2] != color:
                        piece.append((row - ch, col - ch))
                        nw = False
                    else:
                        nw = False
                if ne:
                    if row - ch >= 0 and col + ch <= 7 and (
                            self.board[row - ch][col + ch] == "No_piece" or self.board[row - ch][col + ch][0] == "s"):
                        piece.append((row - ch, col + ch))
                    elif row - ch >= 0 and col + ch <= 7 and self.board[row - ch][col + ch][2] != color:
                        piece.append((row - ch, col + ch))
                        ne = False
                    else:
                        ne = False
                if se:
                    if row + ch <= 7 and col + ch <= 7 and (
                            self.board[row + ch][col + ch] == "No_piece" or self.board[row + ch][col + ch][0] == "s"):
                        piece.append((row + ch, col + ch))
                    elif row + ch <= 7 and col + ch <= 7 and self.board[row + ch][col + ch][2] != color:
                        piece.append((row + ch, col + ch))
                        se = False
                    else:
                        se = False
                if sw:
                    if row + ch <= 7 and col - ch >= 0 and (
                            self.board[row + ch][col - ch] == "No_piece" or self.board[row + ch][col - ch][0] == "s"):
                        piece.append((row + ch, col - ch))
                    elif row + ch <= 7 and col - ch >= 0 and self.board[row + ch][col - ch][2] != color:
                        piece.append((row + ch, col - ch))
                        sw = False
                    else:
                        sw = False
        else:
            raise PieceNotOnBoard
        return piece

    def _valid_moves(self) -> list[list]:
        '''
        Перебирает возможные ходы всех фигур на доске

        :return: Матрица из возможных ходов
        '''
        self.valid_moves = deepcopy(self.board)
        for row in range(8):
            for col in range(8):
                piece = self.valid_moves[row][col]
                if piece == 'No_piece' or piece[0] == "s":
                    self.valid_moves[row][col] = []
                elif piece == "p_white":
                    piece = []
                    if row - 1 >= 0 and self.board[row - 1][col] == "No_piece":
                        piece.append((row - 1, col))
                    if col + 1 <= 7 and row - 1 >= 0 and (self.board[row - 1][col + 1][2] == "b"):
                        piece.append((row - 1, col + 1))
                    if col - 1 >= 0 and row - 1 >= 0 and self.board[row - 1][col - 1][2] == "b":
                        piece.append((row - 1, col - 1))
                    if row == 6 and self.board[row - 1][col] == "No_piece" and self.board[row - 2][col] == "No_piece":
                        piece.append((row - 2, col))
                    self.valid_moves[row][col] = piece
                elif piece == "p_black":
                    piece = []
                    if row + 1 <= 7 and self.board[row + 1][col] == "No_piece":
                        piece.append((row + 1, col))
                    if col - 1 >= 0 and row + 1 <= 7 and self.board[row + 1][col - 1][2] == "w":
                        piece.append((row + 1, col - 1))
                    if col + 1 <= 7 and row + 1 <= 7 and self.board[row + 1][col + 1][2] == "w":
                        piece.append((row + 1, col + 1))
                    if row == 1 and self.board[row + 1][col] == "No_piece" and self.board[row + 2][col] == "No_piece":
                        piece.append((row + 2, col))
                    self.valid_moves[row][col] = piece
                elif piece[0] == "n":
                    color = piece[2]
                    piece = []
                    for ch_r in 1, -1, 2, -2:
                        ch_col = [1, -1] if abs(ch_r) == 2 else [2, -2]
                        for ch_c in ch_col:
                            if 0 <= row + ch_r <= 7 and 0 <= col + ch_c <= 7 and self.board[row + ch_r][col + ch_c][
                                2] != color:
                                piece.append((row + ch_r, col + ch_c))
                    self.valid_moves[row][col] = piece
                elif piece[0] == "r":
                    color = piece[2]
                    try:
                        self.valid_moves[row][col] = self._valid_rook_move(row, col, color)
                    except PieceNotOnBoard:
                        self.board[row][col] = 'No_piece'
                elif piece[0] == "b":
                    color = piece[2]
                    try:
                        self.valid_moves[row][col] = self._valid_bishop_move(row, col, color)
                    except PieceNotOnBoard:
                        self.board[row][col] = 'No_piece'
                elif piece[0] == "q":
                    color = piece[2]
                    try:
                        self.valid_moves[row][col] = self._valid_rook_move(row, col, color) + self._valid_bishop_move(
                            row, col, color)
                    except PieceNotOnBoard:
                        self.board[row][col] = 'No_piece'
                else:
                    color = piece[2]
                    piece = []
                    for ch_r in -1, 0, 1:
                        for ch_c in -1, 0, 1:
                            if 0 <= row + ch_r <= 7 and 0 <= col + ch_c <= 7 and self.board[row + ch_r][col + ch_c][
                                2] != color:
                                piece.append((row + ch_r, col + ch_c))
                    self.valid_moves[row][col] = piece
        return self.valid_moves

    def _draw_pos_moves(self, row, col):
        '''
        Во время хода рисует возможные ходы выбранной фигуры на доске

        :param row: Ряд выбранной фигуры
        :param col: Столбец выбранной фигуры
        :return: None
        '''
        for (pos_c, pos_r) in self.valid_moves[row][col]:
            if 0 <= pos_r <= 7 and 0 <= pos_c <= 7:
                if self.board[pos_c][pos_r] == "No_piece" or \
                        (self.board[pos_c][pos_r][0] == "s" and
                         self.board[self.selected_piece_pos[0]][self.selected_piece_pos[1]][0] != "p"):
                    self.canvas.create_oval(pos_r * 80 + 30, pos_c * 80 + 30, pos_r * 80 + 50, pos_c * 80 + 50,
                                            fill="#829769", outline="#829769")
                else:
                    c = 18
                    self.canvas.create_polygon(pos_r * 80, pos_c * 80, pos_r * 80 + c, pos_c * 80, pos_r * 80,
                                               pos_c * 80 + c, fill="#829769", outline="#829769")
                    self.canvas.create_polygon(pos_r * 80, (pos_c + 1) * 80, pos_r * 80, (pos_c + 1) * 80 - c,
                                               pos_r * 80 + c, (pos_c + 1) * 80, fill="#829769", outline="#829769")
                    self.canvas.create_polygon((pos_r + 1) * 80, (pos_c + 1) * 80, (pos_r + 1) * 80,
                                               (pos_c + 1) * 80 - c,
                                               (pos_r + 1) * 80 - c, (pos_c + 1) * 80, fill="#829769",
                                               outline="#829769")
                    self.canvas.create_polygon((pos_r + 1) * 80, pos_c * 80, (pos_r + 1) * 80 - c, pos_c * 80,
                                               (pos_r + 1) * 80, pos_c * 80 + c, fill="#829769", outline="#829769")

    def _on_click(self, event):
        '''
        Обрабатывает событие клика кнопкой мыши по доске

        :param event: Координаты события клика
        :return: None
        '''
        col = event.x // 80
        row = event.y // 80

        if not (0 <= row < 8 and 0 <= col < 8):
            return

        piece = self.board[row][col]
        if self.selected_piece_pos is not None and piece[2] != self.current_player[0] and \
                (row, col) in self.valid_moves[self.selected_piece_pos[0]][self.selected_piece_pos[1]]:
            try:
                self._make_move(row, col)
            except PieceNotOnBoard:
                return
        else:
            if self.selected_piece_pos is None:
                if piece != "No_piece" and piece[2] == self.current_player[0]:
                    self.selected_piece_pos = (row, col)
                    self.canvas.delete("all")
                    self._draw_board()
                    self.canvas.create_rectangle(col * 80, row * 80, (col + 1) * 80, (row + 1) * 80, fill="#829769",
                                                 outline="#829769")
                    self._draw_piece(row, col)
                    self._draw_pos_moves(row, col)

            elif self.selected_piece_pos == (row, col):
                self.canvas.delete("all")
                self._draw_board()
                self.selected_piece_pos = None
            elif piece[2] == self.current_player[0]:
                self.canvas.delete("all")
                self._draw_board()
                self.canvas.create_rectangle(col * 80, row * 80, (col + 1) * 80, (row + 1) * 80, fill="#829769",
                                             outline="#829769")
                try:
                    self._draw_piece(row, col)
                except UnknownPiece:
                    self.board[row][col] = "No_piece"
                self.selected_piece_pos = (row, col)
                self._draw_pos_moves(row, col)
                try:
                    self._highlight_checked_king()
                except PieceNotOnBoard:
                    w_king_found, b_king_found = False, False
                    for r in range(8):
                        for c in range(8):
                            if self.board[r][c] == "k_white":
                                self.w_king_pos = (r, c)
                                w_king_found = True
                            elif self.board[r][c] == "k_black":
                                self.b_king_pos = (r, c)
                                b_king_found = True
                    if w_king_found and b_king_found:
                        self._highlight_checked_king()
                    else:
                        print("No king on board")

    def _make_move(self, row, col):
        '''
        Выполняет ход выбранной фигурой на выбранную клетку, проверяет на условия завершения игры и обновляет доску

        :param row: Ряд, в который перемещается выбранная фигура
        :param col: Столбец, в который перемещается выбранная фигура
        :return: None
        :raises PieceNotOnBoard: Если выбранная фигура или конечная клетка за пределами доски
        '''
        if 0 <= self.selected_piece_pos[0] < 8 and 0 <= self.selected_piece_pos[
            1] < 8 and 0 <= row < 8 and 0 <= col < 8:
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
                self.en_passant_target = (piece_pos[0] + 2, piece_pos[1]) if self.board[piece_pos[0]][piece_pos[1]][
                                                                                 2] == "b" \
                    else (piece_pos[0] - 2, piece_pos[1])
            if self.board[row][col][0] == "s" and piece[0] == "p":
                self.board[self.en_passant_target[0]][self.en_passant_target[1]] = "No_piece"
            if self.selected_piece_pos == self.w_king_pos:
                if col - self.w_king_pos[1] == 2:
                    self.w_king_pos = (row, col)
                    self.board[row][col - 1] = "r_white"
                    self.board[row][7] = "No_piece"
                elif col - self.w_king_pos[1] == -2:
                    self.w_king_pos = (row, col)
                    self.board[row][col + 1] = "r_white"
                    self.board[row][0] = "No_piece"
                self.w_king_pos = (row, col)
                self.king_moved[1] = True
            elif self.selected_piece_pos == self.b_king_pos:
                if col - self.b_king_pos[1] == 2:
                    self.b_king_pos = (row, col)
                    self.board[row][col - 1] = "r_black"
                    self.board[row][7] = "No_piece"
                elif col - self.b_king_pos[1] == -2:
                    self.b_king_pos = (row, col)
                    self.board[row][col + 1] = "r_black"
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
                self._highlight_checked_king()
                if self.current_player == "white":
                    self.current_player = "black"
                else:
                    self.current_player = "white"
                self._stop_timer()
                self._start_timer()
                self._simulate("b" if self.current_player == "black" else "w")
                self._castle()
                self._is_mate()
                self._is_stalemate()
        else:
            raise PieceNotOnBoard

    def _highlight_checked_king(self):
        '''
        Выделяет короля, который находится под шахом

        :return: None
        :raises PieceNotOnBoard: Если король находится за пределами доски
        '''
        king_on_check = (0, 0)
        if self._is_square_under_attack(self.w_king_pos[0], self.w_king_pos[1], 'w'):
            king_on_check = self.w_king_pos
        elif self._is_square_under_attack(self.b_king_pos[0], self.b_king_pos[1], 'b'):
            king_on_check = self.b_king_pos
        if 0 <= king_on_check[0] < 8 and 0 <= king_on_check[1] < 8:
            if self._is_square_under_attack(self.w_king_pos[0], self.w_king_pos[1], 'w') or \
                    self._is_square_under_attack(self.b_king_pos[0], self.b_king_pos[1], 'b'):
                self.canvas.create_rectangle(king_on_check[1] * 80, king_on_check[0] * 80, (king_on_check[1] + 1) * 80,
                                             (king_on_check[0] + 1) * 80, outline='red', width=4)
        else:
            raise PieceNotOnBoard

    def _is_square_under_attack(self, row, col, color) -> bool:
        '''
        Проверяет, находится ли клетка под атакой фигуры противника

        :param row: Ряд клетки для проверки
        :param col: Столбец клетки для проверки
        :param color: Цвет фигуры на проверяемой клетке
        :return: Находится ли фигура под атакой
        '''
        opp_col = "b" if color == "w" else "w"
        for brd_r in range(8):
            for brd_c in range(8):
                if self.board[brd_r][brd_c][2] == opp_col and (row, col) in self.valid_moves[brd_r][brd_c] and \
                        self.board[row][col] != "No_piece":
                    return True
        return False

    def _simulate(self, player):
        '''
        Исключает ходы, приводящие к шаху собственного короля

        :param player: Цвет игрока для проверки
        :return: None
        '''
        if player == "w" or player == "b":
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
                        self.board[row][col], self.board[row_move][col_move] = self.board[row_move][
                            col_move], on_cell_piece
                        self._valid_moves()
            self.valid_moves = valid_after_simulate

    def _no_moves(self) -> bool:
        '''
        Проверяет, может ли игрок сделать ход

        :return: True если игрок не может сделать ход
        '''
        for row in range(8):
            for col in range(8):
                if self.board[row][col][2] == self.current_player[0] and self.valid_moves[row][col] != []:
                    return False
        return True

    def _is_mate(self) -> bool:
        '''
        Проверяет, получил ли ходящий игрок мат

        :return: True если игрок получил мат
        '''
        king = self.w_king_pos if self.current_player == "white" else self.b_king_pos
        if self._is_square_under_attack(king[0], king[1], self.current_player[0]) and self._no_moves():
            self._stop_timer()
            self._show_end_game_dialog("Мат! Победили " + ("Чёрные" if self.current_player == "white" else "Белые"))
            return True
        return False

    def _is_stalemate(self) -> bool:
        '''
        Проверяет, является ли позиция игрока патовой

        :return: True если позиция патовая
        '''
        king = self.w_king_pos if self.current_player == "white" else self.b_king_pos
        if not self._is_square_under_attack(king[0], king[1], self.current_player[0]) and self._no_moves():
            self._stop_timer()
            self._show_end_game_dialog("Пат! Ничья")
            return True
        return False

    def _show_end_game_dialog(self, message):
        '''
        Создаёт окно завершения игры, останавливает таймеры игроков

        :param message: Сообщение, которое необходимо вывести в окне завершения игры
        :return: None
        '''
        self._stop_timer()
        end_window = tk.Toplevel(self.board_window)
        end_window.title("Игра окончена")
        end_window.geometry("300x150")
        end_window.resizable(False, False)

        end_window.update_idletasks()
        board_window = self.board_window

        win_width = end_window.winfo_width()
        win_height = end_window.winfo_height()

        board_x = board_window.winfo_x()
        board_y = board_window.winfo_y()
        board_width = board_window.winfo_width()
        board_height = board_window.winfo_height()
        end_window.protocol("WM_DELETE_WINDOW", lambda: None)

        x = board_x + (board_width - win_width) // 2
        y = board_y + (board_height - win_height) // 2

        end_window.geometry(f"{win_width}x{win_height}+{x}+{y}")

        end_window.grab_set()  #Не даёт взаимодействовать с доской

        tk.Label(
            end_window,
            text=message,
            font=("Arial", 12),
            pady=20
        ).pack()

        tk.Button(
            end_window,
            text="Начать заново",
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self._restart_game(end_window)
        ).pack(pady=10)

        end_window.focus_set()

    def _restart_game(self, end_window):
        '''
        Перезапускает игру (возвращает к окну настройки)

        :param end_window: окно, которое необходимо закрыть вместе с доской
        :return: None
        '''
        self._stop_timer()
        end_window.destroy()
        self.board_window.destroy() if end_window != self.board_window else None

        self.__init__()
        self._setting()

    def _format_time(self, seconds) -> str:
        '''
        Форматирует время (формат ММ:СС)

        :param seconds: Количество секунд
        :return: Отформатированное время
        '''
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def _update_timer(self):
        '''
        Каждую секунду обновляет таймер игроков

        :return: None
        '''
        if self.player_time[self.current_player] > 0:
            self.player_time[self.current_player] -= 1
            self.timer_labels[self.current_player].config(text=self._format_time(self.player_time[self.current_player]))
            if self.player_time[self.current_player] == 0:
                winner = "Чёрные" if self.current_player == "white" else "Белые"
                self._stop_timer()
                self._show_end_game_dialog(f"Время вышло! Победили {winner}")
                return

        self.after_id = self.board_window.after(1000, self._update_timer)

    def _start_timer(self):
        '''
        Запускает таймер для текущего игрока

        :return: None
        '''
        if not self.timer_running:
            self.timer_running = True
            self._update_timer()

    def _stop_timer(self):
        '''
        Останавливает таймер (при переходе хода или окончании игры)

        :return: None
        '''
        if self.timer_running and self.after_id is not None:
            self.board_window.after_cancel(self.after_id)
            self.after_id = None
            self.timer_running = False

    def _castle(self):
        '''
        Проверяет на возможность выполнения рокировки

        :return: None
        '''
        for c in 0, 1:
            color = "w" if c == 1 else "b"
            if not (self.rook_moved[c][0] or self.king_moved[c]) and \
                    all(x == "No_piece" for x in self.board[c * 7][1:4]) and \
                    all(not (self._is_square_under_attack(c * 7, x, color)) for x in (2, 3, 4)):
                self.valid_moves[c * 7][4].append((c * 7, 2))
            if not (self.rook_moved[c][1] or self.king_moved[c]) and \
                    all(x == "No_piece" for x in self.board[c * 7][5:7]) and \
                    all(not (self._is_square_under_attack(c * 7, x, color)) for x in (4, 5, 6)):
                self.valid_moves[c * 7][4].append((c * 7, 6))

    def _promote(self, row, col):
        '''
        Выполняет превращение пешки при достижении последней горизонтали

        :param row: Ряд клетки с пешкой
        :param col: Столбец клетки с пешкой
        :return: None
        '''
        def select_piece(piece_type):
            '''
            Заменяет пешку на выбранную фигуру и проводит все необходимые проверки

            :param piece_type: Выбранная фигура
            :return: None
            '''
            new_piece = f"{piece_type[0] if piece_type != "knight" else "n"}_{color}"
            self.board[row][col] = new_piece
            self._valid_moves()
            opponent_king = self.b_king_pos if color == "white" else self.w_king_pos
            is_check = self._is_square_under_attack(opponent_king[0], opponent_king[1],
                                                    "b" if color == "white" else "w")
            self.canvas.delete("all")
            self._draw_board()

            if is_check:
                self._highlight_checked_king()
            self.current_player = "black" if self.current_player == "white" else "white"
            self._simulate("b" if self.current_player == "black" else "w")
            self._castle()
            self._is_mate()
            self._is_stalemate()
            promote_window.destroy()

        if (self.current_player == "white" and row == 0) or (self.current_player == "black" and row == 7):
            promote_window = tk.Toplevel(self.board_window)
            promote_window.title("Превращение пешки")
            promote_window.geometry("370x90")
            promote_window.resizable(False, False)
            promote_window.protocol("WM_DELETE_WINDOW", lambda: None)

            color = self.current_player
            pieces = ['queen', 'rook', 'bishop', 'knight']

            for i, piece in enumerate(pieces):
                img_key = f"{color}_{piece}"
                btn = tk.Button(
                    promote_window,
                    image=self.piece_images[img_key],
                    command=lambda pt=piece: select_piece(pt),
                    bd=0
                )
                btn.grid(row=0, column=i, padx=5, pady=5)
            promote_window.grab_set()
            promote_window.focus_set()

    def run(self):
        '''
        Запускает игру и главный цикл

        :return: None
        '''
        self._setting()


if __name__ == "__main__":
    paths = input('Введите относительный путь папки, где находятся фигуры\nПо умолчанию папка называется "pieces"\n-> ')
    paths = paths.strip('/')
    chess = Chess(pth=paths if paths else "pieces")
    chess.run()
