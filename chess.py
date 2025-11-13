import tkinter as tk
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
        self.selected_piece = None
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
        time_input = self.time_entry.get().strip()

        if not time_input:
            self.time_limit = 180
            self.root.destroy()
            self._draw_board()
            return

        try:
            time_per_player = float(time_input)
            if time_per_player <= 0:
                messagebox.showerror("Ошибка", "Время должно быть положительным числом!")
                return

            self.time_limit = time_per_player
            self.root.destroy()
            self._draw_board()

        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Пожалуйста, введите корректное число (например, 30)!"
            )

    def _draw_board(self):
        board_window = tk.Tk()
        board_window.title("Шахматы")
        board_window.resizable(False, False)

        cell_size = 60

        canvas_width = 8 * cell_size
        canvas_height = 8 * cell_size

        canvas = tk.Canvas(
            board_window,
            width = canvas_width,
            height = canvas_height,
            bg = "white"
        )
        canvas.pack()

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

                canvas.create_rectangle(x1, y1, x2, y2, fill = cell_color, outline = cell_color)

                if row == 7:
                    letter = chr(ord('a') + col)
                    text_x = x1 + 3
                    text_y = y1 + cell_size
                    canvas.create_text(
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
                    canvas.create_text(
                        text_x,
                        text_y,
                        text = str(digit),
                        font = ("Arial", 9),
                        fill = text_color,
                        anchor = 'ne'
                    )

        self._load_piece_images()
        self._draw_pieces(canvas, cell_size)
        board_window.mainloop()

    def _load_piece_images(self):
        piece_names = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']

        images = {}
        for color in colors:
            for piece in piece_names:
                img_path = f"pieces/{color}_{piece}.png"
                img = Image.open(img_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                images[f"{color}_{piece}"] = ImageTk.PhotoImage(img)
        self.piece_images = images

    def _draw_pieces(self, canvas, cell_size):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None:
                    x = col * cell_size + 5
                    y = row * cell_size + 5

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
                    else:
                        raise ValueError(f"Неизвестная фигура: {piece}")

                    canvas.create_image(x, y, image = self.piece_images[img_key], anchor = 'nw')

a = Chess()
a._setting()