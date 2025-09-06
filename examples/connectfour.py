from __future__ import annotations

# Connect Four using ButtonPad
# - 7 columns x 6 rows of play cells (standard Connect Four)
# - Top row (y=0) has 7 buttons to drop a piece in a column
# - Play area is y=1..6 (labels). Labels background becomes red/black per player.
# - On win, the whole board flashes in the winner's color, then auto-resets.

from typing import List, Optional

from buttonpad import ButtonPad, BPButton, BPLabel, alert


COLS = 7  # columns (top row has 7 buttons)
ROWS = 6  # play rows beneath buttons; total grid rows = 1 + ROWS = 7

# UI tuning
BORDER = 10
TITLE = "Connect Four (ButtonPad)"

# Colors
EMPTY_COLOR = "white"
RED = "red"
BLACK = "black"
BTN_BG = "#e0e0e0"
BTN_FG = "black"


pad: ButtonPad  # initialized in main()
board: List[List[int]]
current: int
game_over: bool
buttons: List[BPButton]
cells: List[List[BPLabel]]


def color_for(player: int) -> str:
    return RED if player == 1 else BLACK


def lowest_empty_row(col: int) -> Optional[int]:
    for r in range(ROWS - 1, -1, -1):
        if board[col][r] == 0:
            return r
    return None


def count_line(c: int, r: int, dc: int, dr: int, player: int) -> int:
    count = 1
    cc, rr = c + dc, r + dr
    while 0 <= cc < COLS and 0 <= rr < ROWS and board[cc][rr] == player:
        count += 1
        cc += dc
        rr += dr
    cc, rr = c - dc, r - dr
    while 0 <= cc < COLS and 0 <= rr < ROWS and board[cc][rr] == player:
        count += 1
        cc -= dc
        rr -= dr
    return count


def check_win(c: int, r: int, player: int) -> bool:
    return (
        count_line(c, r, 1, 0, player) >= 4 or
        count_line(c, r, 0, 1, player) >= 4 or
        count_line(c, r, 1, 1, player) >= 4 or
        count_line(c, r, 1, -1, player) >= 4
    )


def new_game() -> None:
    global current, game_over
    for c in range(COLS):
        for r in range(ROWS):
            board[c][r] = 0
            cell = cells[c][r]
            cell.background_color = EMPTY_COLOR
    for btn in buttons:
        btn.background_color = BTN_BG
        btn.text_color = BTN_FG
    current = 1
    game_over = False


def drop(col: int) -> None:
    global current, game_over
    if game_over:
        return
    row = lowest_empty_row(col)
    if row is None:
        return
    player = current
    board[col][row] = player
    cells[col][row].background_color = color_for(player)
    if check_win(col, row, player):
        game_over = True
        try:
            alert(f"{'Red' if player == 1 else 'Black'} player wins!", title="Connect Four")
        except Exception:
            pass
        new_game()
        return
    # Tie detection: if no empty (0) cells remain
    if all(board[c][r] != 0 for c in range(COLS) for r in range(ROWS)):
        game_over = True
        try:
            alert("It's a tie!", title="Connect Four")
        except Exception:
            pass
        new_game()
        return
    current = 2 if current == 1 else 1


def make_drop_handler(col: int):
    def handler(el, x, y):  # ButtonPad callback signature
        drop(col)
    return handler


def main() -> None:
    global pad, board, current, game_over, buttons, cells
    top_buttons = ",".join(str(i + 1) for i in range(COLS))
    label_row = ",".join("`''" for _ in range(COLS))
    layout = "\n".join([top_buttons] + [label_row for _ in range(ROWS)])
    pad = ButtonPad(
        layout,
        cell_width=60,
        cell_height=60,
        h_gap=4,
        v_gap=4,
        default_bg_color=BTN_BG,
        default_text_color=BTN_FG,
        title=TITLE,
        border=BORDER,
    )
    board = [[0 for _ in range(ROWS)] for _ in range(COLS)]
    current = 1
    game_over = False
    buttons = [pad[c, 0] for c in range(COLS)]  # type: ignore[assignment]
    cells = [[pad[c, r + 1] for r in range(ROWS)] for c in range(COLS)]  # type: ignore[list-item]
    for c in range(COLS):
        btn = buttons[c]
        btn.on_click = make_drop_handler(c)
        btn.text = "Drop\nHere"
    new_game()
    pad.run()


if __name__ == "__main__":
    main()
