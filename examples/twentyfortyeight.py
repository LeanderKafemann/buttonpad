from __future__ import annotations

"""
2048 game using ButtonPad
- 4x4 grid of labels (not buttons)
- Move tiles with Arrow keys or WASD
- Tiles have distinct background colors; text color always white
"""

import random
from typing import List

import buttonpad

COLS = 4
ROWS = 4

# Appearance
WINDOW_BG = "#0e1220"    # dark backdrop
EMPTY_BG = "#1f2640"     # empty cell
TEXT_COLOR = "#ffffff"    # always white text
FONT_SIZE = 24

# Background colors per tile value (fallback used if missing)
TILE_BG = {
    0: EMPTY_BG,
    2: "#3c3f58",
    4: "#4455aa",
    8: "#2b78ff",
    16: "#26a69a",
    32: "#43a047",
    64: "#f57c00",
    128: "#e64a19",
    256: "#d32f2f",
    512: "#8e24aa",
    1024: "#5e35b1",
    2048: "#b8860b",
}
DEFAULT_TILE_BG = "#37474f"


def build_layout() -> str:
    # Labels with no-merge so each cell is independent: tokens like `""
    row = ",".join(['`""'] * COLS)
    return "\n".join([row for _ in range(ROWS)])


def main() -> None:
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=90,
        cell_height=90,
        h_gap=6,
        v_gap=6,
        border=10,
        title="2048",
        default_bg_color=EMPTY_BG,
        default_text_color=TEXT_COLOR,
        window_color=WINDOW_BG,
        resizable=True,
    )

    board: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    # Utility to update a single cell UI
    def set_cell_ui(x: int, y: int, val: int) -> None:
        el = pad[x, y]  # type: ignore[index]
        el.text = str(val) if val else ""
        el.text_color = TEXT_COLOR
        el.font_size = FONT_SIZE
        el.background_color = TILE_BG.get(val, DEFAULT_TILE_BG)

    def update_ui() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                set_cell_ui(x, y, board[y][x])

    def empty_positions() -> list[tuple[int, int]]:
        return [(x, y) for y in range(ROWS) for x in range(COLS) if board[y][x] == 0]

    def add_random_tile() -> bool:
        empties = empty_positions()
        if not empties:
            return False
        x, y = random.choice(empties)
        board[y][x] = 4 if random.random() < 0.1 else 2
        return True

    def new_game() -> None:
        # Reset board, add two tiles, refresh UI
        for y in range(ROWS):
            for x in range(COLS):
                board[y][x] = 0
        add_random_tile()
        add_random_tile()
        update_ui()

    def move_line(line: list[int]) -> tuple[list[int], bool, bool]:
        # Slide non-zeros left, merge pairs once, then slide again
        original = line[:]
        tiles = [v for v in line if v != 0]
        merged: list[int] = []
        skip = False
        i = 0
        made_2048 = False
        while i < len(tiles):
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                nv = tiles[i] * 2
                if nv == 2048:
                    made_2048 = True
                merged.append(nv)
                i += 2
            else:
                merged.append(tiles[i])
                i += 1
        merged += [0] * (len(line) - len(merged))
        moved = merged != original
        return merged, moved, made_2048

    def transpose(mat: List[List[int]]) -> List[List[int]]:
        return [list(row) for row in zip(*mat)]

    def reverse_rows(mat: List[List[int]]) -> List[List[int]]:
        return [list(reversed(row)) for row in mat]

    def apply_move(direction: str) -> bool:
        nonlocal board
        moved_any = False
        won_this_move = False
        new_board: List[List[int]]

        if direction == "left":
            new_board = []
            for row in board:
                nl, moved, made_2048 = move_line(row)
                if moved:
                    moved_any = True
                if made_2048:
                    won_this_move = True
                new_board.append(nl)
        elif direction == "right":
            new_board = []
            for row in board:
                rev = list(reversed(row))
                nl, moved, made_2048 = move_line(rev)
                nl = list(reversed(nl))
                if moved:
                    moved_any = True
                if made_2048:
                    won_this_move = True
                new_board.append(nl)
        elif direction == "up":
            t = transpose(board)
            new_t = []
            for row in t:
                nl, moved, made_2048 = move_line(row)
                if moved:
                    moved_any = True
                if made_2048:
                    won_this_move = True
                new_t.append(nl)
            new_board = transpose(new_t)
        elif direction == "down":
            t = transpose(board)
            new_t = []
            for row in t:
                rev = list(reversed(row))
                nl, moved, made_2048 = move_line(rev)
                nl = list(reversed(nl))
                if moved:
                    moved_any = True
                if made_2048:
                    won_this_move = True
                new_t.append(nl)
            new_board = transpose(new_t)
        else:
            return False

        if moved_any:
            board = new_board
            # Win check: if 2048 created in this move, alert and restart
            if won_this_move or any(v == 2048 for row in board for v in row):
                update_ui()
                try:
                    buttonpad.alert("You win!")
                except Exception:
                    pass
                new_game()
                return True

            # Otherwise add a random tile and update
            add_random_tile()
            update_ui()
            # Lose check: no moves left after the new tile
            if not any_moves_possible():
                try:
                    buttonpad.alert("Game Over")
                except Exception:
                    pass
                new_game()
        return moved_any

    def any_moves_possible() -> bool:
        if empty_positions():
            return True
        # Check for adjacent equal tiles
        for y in range(ROWS):
            for x in range(COLS):
                v = board[y][x]
                if x + 1 < COLS and board[y][x + 1] == v:
                    return True
                if y + 1 < ROWS and board[y + 1][x] == v:
                    return True
        return False

    # Key handlers
    def on_left(_evt=None):
        apply_move("left")

    def on_right(_evt=None):
        apply_move("right")

    def on_up(_evt=None):
        apply_move("up")

    def on_down(_evt=None):
        apply_move("down")

    # Bind keys: arrows and WASD (upper/lower)
    try:
        pad.root.bind_all("<Left>", on_left)
        pad.root.bind_all("<Right>", on_right)
        pad.root.bind_all("<Up>", on_up)
        pad.root.bind_all("<Down>", on_down)
        pad.root.bind_all("<KeyPress-a>", on_left)
        pad.root.bind_all("<KeyPress-A>", on_left)
        pad.root.bind_all("<KeyPress-d>", on_right)
        pad.root.bind_all("<KeyPress-D>", on_right)
        pad.root.bind_all("<KeyPress-w>", on_up)
        pad.root.bind_all("<KeyPress-W>", on_up)
        pad.root.bind_all("<KeyPress-s>", on_down)
        pad.root.bind_all("<KeyPress-S>", on_down)
    except Exception:
        pass

    # Start a new game
    new_game()

    # Ensure all labels start with correct text color & font
    for y in range(ROWS):
        for x in range(COLS):
            el = pad[x, y]  # type: ignore[index]
            el.text_color = TEXT_COLOR
            el.font_size = FONT_SIZE

    pad.run()


if __name__ == "__main__":
    main()
