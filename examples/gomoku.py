from __future__ import annotations

# Gomoku: 15x15 grid of buttons. White moves first, then black.
# Click to place a stone: the button background becomes white or black.
# When a player gets five in a row, the board flashes the winner's color, then resets.

import buttonpad
from typing import List, Tuple

TITLE = "Gomoku"
SIZE = 15

# UI tuning
CELL_W = 40
CELL_H = 40
HGAP = 0
VGAP = 0
BORDER = 2
EMPTY_BG = "#e8e8e8"
WHITE_BG = "#ffffff"
BLACK_BG = "#222222"


def build_layout() -> str:
    row = ",".join(["`"] * SIZE)
    return "\n".join([row for _ in range(SIZE)])


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < SIZE and 0 <= y < SIZE


def count_in_direction(board: List[List[int]], x: int, y: int, dx: int, dy: int, who: int) -> int:
    cnt = 0
    cx, cy = x + dx, y + dy
    while in_bounds(cx, cy) and board[cy][cx] == who:
        cnt += 1
        cx += dx
        cy += dy
    return cnt


def has_five(board: List[List[int]], x: int, y: int, who: int) -> bool:
    # Check 4 lines through (x,y)
    for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
        total = 1
        total += count_in_direction(board, x, y, dx, dy, who)
        total += count_in_direction(board, x, y, -dx, -dy, who)
        if total >= 5:
            return True
    return False


def main() -> None:
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=CELL_W,
        cell_height=CELL_H,
        h_gap=HGAP,
        v_gap=VGAP,
        border=BORDER,
        title=TITLE,
        default_bg_color=EMPTY_BG,
        default_text_color="black",
        window_color="#f0f0f0",
        resizable=True,
    )

    # Board state: 0 empty, 1 white, 2 black
    board: List[List[int]] = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    cells = [pad[x, y] for y in range(SIZE) for x in range(SIZE)]  # type: ignore[list-item]

    turn = {"who": 1}  # 1 = white, 2 = black
    game = {"over": False}

    def set_cell_color(x: int, y: int, who: int) -> None:
        el = pad[x, y]  # type: ignore[index]
        if who == 1:
            el.background_color = WHITE_BG
        else:
            el.background_color = BLACK_BG

    def clear_board() -> None:
        for y in range(SIZE):
            for x in range(SIZE):
                board[y][x] = 0
                pad[x, y].background_color = EMPTY_BG  # type: ignore[index]
        turn["who"] = 1
        game["over"] = False

    def flash_winner(who: int, flashes: int = 6, interval_ms: int = 180) -> None:
        game["over"] = True
        target = WHITE_BG if who == 1 else BLACK_BG
        default = EMPTY_BG

        def step(i: int) -> None:
            color = target if (i % 2 == 0) else default
            for el in cells:
                el.background_color = color
            if i + 1 < flashes:
                pad.root.after(interval_ms, lambda: step(i + 1))
            else:
                # Reset after final flash
                pad.root.after(200, clear_board)

        step(0)

    def handle_click(el, x: int, y: int) -> None:
        if game["over"]:
            return
        if board[y][x] != 0:
            return  # occupied
        who = turn["who"]
        board[y][x] = who
        set_cell_color(x, y, who)

        if has_five(board, x, y, who):
            flash_winner(who)
            return

        turn["who"] = 2 if who == 1 else 1

    # Wire handlers
    for y in range(SIZE):
        for x in range(SIZE):
            pad[x, y].on_click = handle_click  # type: ignore[index]

    pad.run()


if __name__ == "__main__":
    main()
