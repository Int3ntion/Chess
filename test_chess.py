import pytest
import tkinter as tk
from unittest.mock import Mock, MagicMock, call
from chess import Chess, PieceNotOnBoard

def test_path():
    chess = Chess('pc')
    assert chess.path == 'pc'

def test_default_time():
    chess = Chess()
    assert chess.time_limit == 600

def test_init_board():
    chess = Chess()
    chess._initialize_board()
    assert chess.board[0][1] == "n_black"
    assert chess.board[7][2] == "b_white"

def test_setting():
    mock_tk = MagicMock()
    mock_label_1 = MagicMock()
    mock_label_2 = MagicMock()
    mock_entry = MagicMock()
    mock_button = MagicMock()

    tk.Tk = MagicMock(return_value=mock_tk)
    tk.Label = MagicMock(side_effect=[mock_label_1, mock_label_2])
    tk.Entry = MagicMock(return_value=mock_entry)
    tk.Button = MagicMock(return_value=mock_button)

    app = Chess()
    app._setting()

    assert tk.Tk.called
    root = mock_tk

    assert root.title.call_args == call("Шахматы")
    assert root.geometry.call_args == call("400x200")
    assert root.resizable.call_args == call(False, False)

    assert tk.Label.call_count == 2
    first_label = tk.Label.call_args_list[0][1]
    assert first_label['text'] == "Добро пожаловать в шахматы!"
    assert first_label['font'] == ("Arial", 16, "bold")
    assert first_label['pady'] == 10
    assert mock_label_1.pack.call_count == 1

    second_label = tk.Label.call_args_list[1][1]
    assert second_label['text'] == "Введите время на игрока (в минутах)"
    assert second_label['font'] == ("Arial", 12, "italic")
    assert mock_label_2.pack.call_count == 1

    assert tk.Entry.called
    entry = tk.Entry.call_args[1]
    assert entry['width'] == 20
    assert entry['font'] == ("Arial", 12)
    assert entry['justify'] == "center"
    assert mock_entry.pack.call_args == call(pady=10)

    assert tk.Button.called
    button = tk.Button.call_args[1]
    assert button['text'] == "Начать игру"
    assert button['font'] == ("Arial", 12)
    assert button['bg'] == "#4CAF50"
    assert button['fg'] == "white"
    assert button['padx'] == 20
    assert button['pady'] == 5
    assert button['command'] == app._start_game
    assert mock_button.pack.call_args == call(pady=10)

def test_valid_rook_move_err():
    """Тест: координаты вне доски → исключение."""
    chess = Chess()
    with pytest.raises(PieceNotOnBoard):
        chess._valid_rook_move(-1, 0, "w")
    with pytest.raises(PieceNotOnBoard):
        chess._valid_rook_move(8, 0, "w")
    with pytest.raises(PieceNotOnBoard):
        chess._valid_rook_move(0, -1, "w")
    with pytest.raises(PieceNotOnBoard):
        chess._valid_rook_move(0, 8, "w")

def test_valid_bishop_move_err():
    chess = Chess()
    with pytest.raises(PieceNotOnBoard):
        chess._valid_bishop_move(-1, 0, "w")
    with pytest.raises(PieceNotOnBoard):
        chess._valid_bishop_move(0, -1, "w")
    with pytest.raises(PieceNotOnBoard):
        chess._valid_bishop_move(0, 8, "w")
    with pytest.raises(PieceNotOnBoard):
        chess._valid_bishop_move(8, 0, "w")

def test_valid_moves_err():
    chess = Chess()
    chess._initialize_board()
    chess._valid_moves()
    assert chess.valid_moves[0][1] == [(2, 2), (2, 0)]
    assert chess.valid_moves[1][1] == [(2, 1), (3, 1)]

def test_make_move_err():
    chess = Chess()
    chess._initialize_board()
    chess.selected_piece_pos = (0, 0)
    with pytest.raises(PieceNotOnBoard):
        chess._make_move(-1, 0)
    with pytest.raises(PieceNotOnBoard):
        chess._make_move(0, 8)
    with pytest.raises(PieceNotOnBoard):
        chess.selected_piece_pos = (-1, 0)
        chess._make_move(0, 0)
    with pytest.raises(PieceNotOnBoard):
        chess.selected_piece_pos = (0, 8)
        chess._make_move(0, 0)

def test_make_move():
    chess = Chess()
    chess._initialize_board()
    chess.selected_piece_pos = (7, 1)

    chess.canvas = Mock()
    chess._start_timer = Mock()
    chess._is_mate = Mock()
    chess._is_stalemate = Mock()

    chess._make_move(5, 2)
    assert chess.board[7][1] == "No_piece"

def test_highlight_ck_no_king_under_attack():
    chess = Chess()
    chess.canvas = Mock()
    chess._is_square_under_attack = Mock(return_value=False)
    chess._highlight_checked_king()
    assert not chess.canvas.create_rectangle.called

def test_highlight_ck_invalid_king_pos():
    chess = Chess()
    chess.canvas = Mock()
    chess._is_square_under_attack = Mock(return_value=True)
    chess.w_king_pos = (-1, -1)
    with pytest.raises(PieceNotOnBoard):
        chess._highlight_checked_king()
    assert not chess.canvas.create_rectangle.called

def test_square_under_attack_no_piece():
    chess = Chess()
    chess._initialize_board()
    chess._valid_moves()
    assert not chess._is_square_under_attack(3, 3, "red")

def test_square_under_attack():
    chess = Chess()
    chess._initialize_board()
    chess.board[4][4] = "q_white"
    chess._valid_moves()
    assert chess._is_square_under_attack(1, 4, "b")
    assert not chess._is_square_under_attack(1, 3, "b")
    assert not chess._is_square_under_attack(6, 4, "w")

def test_no_moves():
    chess = Chess()
    chess.board = [["No_piece" for _ in range(8)] for _ in range(8)]
    chess.board[0][0] = "k_white"
    chess.current_player = "black"
    assert chess._no_moves()
    chess.current_player = "white"
    chess.board[0][1] = "q_black"
    chess.board[1][1] = "r_black"
    chess.board[1][0] = "p_black"
    chess._valid_moves()
    chess._simulate("w")
    assert chess._no_moves()

def test_is_mate_has_moves():
    chess = Chess()
    chess.current_player = "black"
    chess.b_king_pos = (0, 0)
    chess._is_square_under_attack = Mock(return_value=True)
    chess._no_moves = Mock(return_value=False)
    chess._stop_timer = Mock()
    chess._show_end_game_dialog = Mock()
    assert not chess._is_mate()
    assert not chess._stop_timer.called
    assert not chess._show_end_game_dialog.called

def test_is_mate_not_in_check():
    chess = Chess()
    chess.current_player = "white"
    chess.w_king_pos = (4, 4)
    chess._is_square_under_attack = Mock(return_value=False)
    chess._no_moves = Mock(return_value=True)  # условно, но не важно — шах первоочереден
    chess._stop_timer = Mock()
    chess._show_end_game_dialog = Mock()
    assert not chess._is_mate()
    assert not chess._stop_timer.called
    assert not chess._show_end_game_dialog.called

def test_is_mate():
    chess = Chess()
    chess.w_king_pos = (4, 4)
    chess.b_king_pos = (0, 0)
    chess._is_square_under_attack = Mock(return_value=True)
    chess._no_moves = Mock(return_value=True)
    chess._stop_timer = Mock()
    chess._show_end_game_dialog = Mock()
    assert chess._is_mate()
    assert chess._stop_timer.called
    assert chess._show_end_game_dialog.called
    expected_message = "Мат! Победили Чёрные"
    call_args = chess._show_end_game_dialog.call_args[0]
    assert call_args[0] == expected_message

def test_is_stalemate_in_check():
    chess = Chess()
    chess.current_player = "white"
    chess.w_king_pos = (4, 4)
    chess._is_square_under_attack = Mock(return_value=True)
    chess._no_moves = Mock(return_value=True)  # условно, но не важно — шах первоочереден
    chess._stop_timer = Mock()
    chess._show_end_game_dialog = Mock()
    assert not chess._is_stalemate()
    assert not chess._stop_timer.called
    assert not chess._show_end_game_dialog.called

def test_is_stalemate():
    chess = Chess()
    chess.current_player = "white"
    chess.w_king_pos = (4, 4)
    chess._is_square_under_attack = Mock(return_value=False)
    chess._no_moves = Mock(return_value=True)  # условно, но не важно — шах первоочереден
    chess._stop_timer = Mock()
    chess._show_end_game_dialog = Mock()
    assert chess._is_stalemate()
    assert chess._stop_timer.called
    assert chess._show_end_game_dialog.called