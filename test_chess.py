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
    chess.initialize_board()
    assert chess.board[0][1] == "n_black"
    assert chess.board[7][2] == "b_white"

def test_setting():
    mock_tk = Mock()
    mock_label_1 = Mock()
    mock_label_2 = Mock()
    mock_entry = Mock()
    mock_button = Mock()

    tk.Tk = Mock(return_value=mock_tk)
    tk.Label = Mock(side_effect=[mock_label_1, mock_label_2])
    tk.Entry = Mock(return_value=mock_entry)
    tk.Button = Mock(return_value=mock_button)

    app = Chess()
    app.setting()

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
    assert button['command'] == app.start_game
    assert mock_button.pack.call_args == call(pady=10)

def test_valid_rook_move_err():
    """Тест: координаты вне доски → исключение."""
    chess = Chess()
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_rook_move(-1, 0, "w")
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_rook_move(8, 0, "w")
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_rook_move(0, -1, "w")
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_rook_move(0, 8, "w")

def test_valid_bishop_move_err():
    chess = Chess()
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_bishop_move(-1, 0, "w")
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_bishop_move(0, -1, "w")
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_bishop_move(0, 8, "w")
    with pytest.raises(PieceNotOnBoard):
        chess.find_valid_bishop_move(8, 0, "w")

def test_valid_moves_err():
    chess = Chess()
    chess.initialize_board()
    chess.find_valid_moves()
    assert chess.valid_moves[0][1] == [(2, 2), (2, 0)]
    assert chess.valid_moves[1][1] == [(2, 1), (3, 1)]

def test_make_move_err():
    chess = Chess()
    chess.initialize_board()
    chess.selected_piece_pos = (0, 0)
    with pytest.raises(PieceNotOnBoard):
        chess.make_move(-1, 0)
    with pytest.raises(PieceNotOnBoard):
        chess.make_move(0, 8)
    with pytest.raises(PieceNotOnBoard):
        chess.selected_piece_pos = (-1, 0)
        chess.make_move(0, 0)
    with pytest.raises(PieceNotOnBoard):
        chess.selected_piece_pos = (0, 8)
        chess.make_move(0, 0)

def test_make_move():
    chess = Chess()
    chess.initialize_board()
    chess.selected_piece_pos = (7, 1)

    chess.canvas = Mock()
    chess.start_timer = Mock()
    chess.is_mate = Mock()
    chess.is_stalemate = Mock()

    chess.make_move(5, 2)
    assert chess.board[7][1] == "No_piece"

def test_highlight_ck_no_king_under_attack():
    chess = Chess()
    chess.canvas = Mock()
    chess.is_square_under_attack = Mock(return_value=False)
    chess.highlight_checked_king()
    assert not chess.canvas.create_rectangle.called

def test_highlight_ck_invalid_king_pos():
    chess = Chess()
    chess.canvas = Mock()
    chess.is_square_under_attack = Mock(return_value=True)
    chess.w_king_pos = (-1, -1)
    with pytest.raises(PieceNotOnBoard):
        chess.highlight_checked_king()
    assert not chess.canvas.create_rectangle.called

def test_square_under_attack_no_piece():
    chess = Chess()
    chess.initialize_board()
    chess.find_valid_moves()
    assert not chess.is_square_under_attack(3, 3, "red")

def test_square_under_attack():
    chess = Chess()
    chess.initialize_board()
    chess.board[4][4] = "q_white"
    chess.find_valid_moves()
    assert chess.is_square_under_attack(1, 4, "b")
    assert not chess.is_square_under_attack(1, 3, "b")
    assert not chess.is_square_under_attack(6, 4, "w")

def test_no_moves():
    chess = Chess()
    chess.board = [["No_piece" for _ in range(8)] for _ in range(8)]
    chess.board[0][0] = "k_white"
    chess.current_player = "black"
    assert chess.no_moves()
    chess.current_player = "white"
    chess.board[0][1] = "q_black"
    chess.board[1][1] = "r_black"
    chess.board[1][0] = "p_black"
    chess.find_valid_moves()
    chess.simulate("w")
    assert chess.no_moves()

def test_is_mate_has_moves():
    chess = Chess()
    chess.current_player = "black"
    chess.b_king_pos = (0, 0)
    chess.is_square_under_attack = Mock(return_value=True)
    chess.no_moves = Mock(return_value=False)
    chess.stop_timer = Mock()
    chess.show_end_game_dialog = Mock()
    assert not chess.is_mate()
    assert not chess.stop_timer.called
    assert not chess.show_end_game_dialog.called

def test_is_mate_not_in_check():
    chess = Chess()
    chess.current_player = "white"
    chess.w_king_pos = (4, 4)
    chess.is_square_under_attack = Mock(return_value=False)
    chess.no_moves = Mock(return_value=True)  # условно, но не важно — шах первоочереден
    chess.stop_timer = Mock()
    chess.show_end_game_dialog = Mock()
    assert not chess.is_mate()
    assert not chess.stop_timer.called
    assert not chess.show_end_game_dialog.called

def test_is_mate():
    chess = Chess()
    chess.w_king_pos = (4, 4)
    chess.b_king_pos = (0, 0)
    chess.is_square_under_attack = Mock(return_value=True)
    chess.no_moves = Mock(return_value=True)
    chess.stop_timer = Mock()
    chess.show_end_game_dialog = Mock()
    assert chess.is_mate()
    assert chess.stop_timer.called
    assert chess.show_end_game_dialog.called
    expected_message = "Мат! Победили Чёрные"
    call_args = chess.show_end_game_dialog.call_args[0]
    assert call_args[0] == expected_message

def test_is_stalemate_in_check():
    chess = Chess()
    chess.current_player = "white"
    chess.w_king_pos = (4, 4)
    chess.is_square_under_attack = Mock(return_value=True)
    chess.no_moves = Mock(return_value=True)  # условно, но не важно — шах первоочереден
    chess.stop_timer = Mock()
    chess.show_end_game_dialog = Mock()
    assert not chess.is_stalemate()
    assert not chess.stop_timer.called
    assert not chess.show_end_game_dialog.called

def test_is_stalemate():
    chess = Chess()
    chess.current_player = "white"
    chess.w_king_pos = (4, 4)
    chess.is_square_under_attack = Mock(return_value=False)
    chess.no_moves = Mock(return_value=True)  # условно, но не важно — шах первоочереден
    chess.stop_timer = Mock()
    chess.show_end_game_dialog = Mock()
    assert chess.is_stalemate()
    assert chess.stop_timer.called
    assert chess.show_end_game_dialog.called