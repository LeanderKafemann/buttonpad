from __future__ import annotations

from typing import List, Optional, Tuple
import random
import buttonpad

COLS = 15
ROWS = 10

# UI
WINDOW_BG = "#f5f5f5"
EMPTY_BG = "#e8e8e8"

# Palette
GREEN = "#2ecc71"
RED = "#e74c3c"
BLUE = "#3498db"
YELLOW = "#f1c40f"
PURPLE = "#9b59b6"
PALETTE: List[str] = [GREEN, RED, BLUE, YELLOW, PURPLE]

Coord = Tuple[int, int]


def build_layout() -> str:
    row = ",".join(["`"] * COLS)
    return "\n".join([row for _ in range(ROWS)])


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < COLS and 0 <= y < ROWS


def main() -> None:
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=40,
        cell_height=40,
        h_gap=2,
        v_gap=2,
        border=10,
        title="SameGame",
        default_bg_color=EMPTY_BG,
        default_text_color="black",
        window_color=WINDOW_BG,
        resizable=False,
    )

    # Board stores palette indices or None for empty
    board: List[List[Optional[int]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def new_game() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                board[y][x] = random.randrange(len(PALETTE))
        update_ui()

    def update_ui() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                el = pad[x, y]  # type: ignore[index]
                idx = board[y][x]
                el.text = ""
                el.background_color = EMPTY_BG if idx is None else PALETTE[idx]

    def cluster_at(x0: int, y0: int) -> List[Coord]:
        if not in_bounds(x0, y0):
            return []
        color = board[y0][x0]
        if color is None:
            return []
        visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
        stack = [(x0, y0)]
        out: List[Coord] = []
        while stack:
            x, y = stack.pop()
            if not in_bounds(x, y) or visited[y][x]:
                continue
            if board[y][x] != color:
                continue
            visited[y][x] = True
            out.append((x, y))
            # 4-dir neighbors
            stack.extend([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)])
        return out

    def remove_cells(cells: List[Coord]) -> None:
        for x, y in cells:
            board[y][x] = None

    def apply_gravity() -> None:
        # Cells fall down within each column
        for x in range(COLS):
            col_vals = [board[y][x] for y in range(ROWS) if board[y][x] is not None]
            # stack at bottom
            new_col: List[Optional[int]] = [None] * (ROWS - len(col_vals)) + col_vals  # type: ignore[operator]
            for y in range(ROWS):
                board[y][x] = new_col[y]

    def shift_columns_left() -> None:
        # Gather non-empty columns in order
        nonempty_xs = [x for x in range(COLS) if any(board[y][x] is not None for y in range(ROWS))]
        new_board: List[List[Optional[int]]] = [[None for _ in range(COLS)] for _ in range(ROWS)]
        for newx, x in enumerate(nonempty_xs):
            for y in range(ROWS):
                new_board[y][newx] = board[y][x]
        for y in range(ROWS):
            for x in range(COLS):
                board[y][x] = new_board[y][x]

    def has_moves() -> bool:
        # If any cluster of size >= 2 exists
        seen = [[False for _ in range(COLS)] for _ in range(ROWS)]
        for y in range(ROWS):
            for x in range(COLS):
                if seen[y][x] or board[y][x] is None:
                    continue
                cells = cluster_at(x, y)
                for cx, cy in cells:
                    seen[cy][cx] = True
                if len(cells) >= 2:
                    return True
        return False

    def on_click(_el, x: int, y: int) -> None:
        cells = cluster_at(x, y)
        if len(cells) < 2:
            return
        remove_cells(cells)
        apply_gravity()
        shift_columns_left()
        update_ui()
        # End-of-game: show remaining blocks and restart
        if not has_moves():
            remaining = sum(1 for yy in range(ROWS) for xx in range(COLS) if board[yy][xx] is not None)
            msg = f"{remaining} out of {COLS * ROWS} blocks remaining."
            if remaining == 0:
                msg += " PERFECT GAME!"
            try:
                buttonpad.alert(msg)
            except Exception:
                # Fallback: print if alert unavailable
                print(msg)
            new_game()

    # Wire handlers
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y].on_click = on_click  # type: ignore[index]

    new_game()
    pad.run()


if __name__ == "__main__":
    main()
