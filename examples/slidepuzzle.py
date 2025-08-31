from __future__ import annotations

# 15-Tile Slide Puzzle using ButtonPad
# - 4 x 4 grid of buttons (tiles 1..15 and one empty space)
# - Click a tile adjacent to the empty space to slide it
# - Board shuffles to a random solvable state on start

from typing import List, Tuple
import random

try:
    import buttonpad  # local module name
except Exception:
    import ButtonPad as buttonpad  # type: ignore

TITLE = "15-Puzzle"
COLS = 4
ROWS = 4  # puzzle rows (control row added separately)

# UI
CELL_W = 72
CELL_H = 72
HGAP = 6
VGAP = 6
BORDER = 12
WINDOW_BG = "#f5f5f5"
TILE_BG = "#e0e0e0"
EMPTY_BG = "#ffffff"
TEXT_COLOR = "#222222"
FONT_SIZE = 20

Coord = Tuple[int, int]


def build_layout() -> str:
    # Control row at top: New, Solve, (two blanks)
    control = ",".join(["New", "New", "Solve", "Solve"])
    row = ",".join(["`"] * COLS)
    grid = "\n".join([row for _ in range(ROWS)])
    return "\n".join([control, grid])


def flatten(board: List[List[int]]) -> List[int]:
    return [board[y][x] for y in range(ROWS) for x in range(COLS)]


def count_inversions(arr: List[int]) -> int:
    a = [v for v in arr if v != 0]
    inv = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                inv += 1
    return inv


def blank_row_from_bottom(board: List[List[int]]) -> int:
    # 1-based index from bottom
    for y in range(ROWS - 1, -1, -1):
        for x in range(COLS):
            if board[y][x] == 0:
                return (ROWS - y)
    return 1


def is_solved(board: List[List[int]]) -> bool:
    return flatten(board) == list(range(1, COLS * ROWS)) + [0]


def is_solvable(board: List[List[int]]) -> bool:
    arr = flatten(board)
    inv = count_inversions(arr)
    blank_from_bottom = blank_row_from_bottom(board)
    # For even grid width (4): solvable iff (blank_from_bottom is odd and inversions even)
    # or (blank_from_bottom is even and inversions odd)
    if COLS % 2 == 0:
        return (blank_from_bottom % 2 == 1 and inv % 2 == 0) or (blank_from_bottom % 2 == 0 and inv % 2 == 1)
    # For odd width (not used here): inversions must be even
    return inv % 2 == 0


def random_solvable_board() -> List[List[int]]:
    while True:
        nums = list(range(1, COLS * ROWS)) + [0]
        random.shuffle(nums)
        board = [[nums[y * COLS + x] for x in range(COLS)] for y in range(ROWS)]
        if is_solvable(board) and not is_solved(board):
            return board


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
        default_bg_color=TILE_BG,
        default_text_color=TEXT_COLOR,
        window_color=WINDOW_BG,
        resizable=True,
    )

    board: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    solving = {"active": False}
    gen_moves: List[Tuple[int, int]] = []  # sequence of blank moves used to generate board (dx, dy)
    user_moves: List[Tuple[int, int]] = []  # sequence of blank moves the user made since generation

    def update_ui() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                el = pad[x, y + 1]  # type: ignore[index]
                v = board[y][x]
                if v == 0:
                    el.text = ""
                    el.background_color = EMPTY_BG
                else:
                    el.text = str(v)
                    el.background_color = TILE_BG
                el.font_size = FONT_SIZE

    def neighbors(x: int, y: int) -> List[Coord]:
        out: List[Coord] = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                out.append((nx, ny))
        return out

    def find_blank() -> Coord:
        for yy in range(ROWS):
            for xx in range(COLS):
                if board[yy][xx] == 0:
                    return (xx, yy)
        return (0, 0)

    def move_blank(dx: int, dy: int) -> bool:
        bx, by = find_blank()
        nx, ny = bx + dx, by + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            board[by][bx], board[ny][nx] = board[ny][nx], board[by][bx]
            update_ui()
            return True
        return False

    def try_move(x: int, y: int) -> None:
        if solving["active"]:
            return
        # If (x,y) is adjacent to the blank (0), swap and record user move direction (blank displacement)
        bx, by = find_blank()
        for nx, ny in neighbors(x, y):
            if board[ny][nx] == 0:
                # blank moves from (nx,ny) to (x,y)
                dx, dy = x - nx, y - ny
                board[ny][nx], board[y][x] = board[y][x], board[ny][nx]
                user_moves.append((dx, dy))
                update_ui()
                return

    def on_click(_el, x: int, y: int) -> None:
        # Adjust for control row offset
        if y == 0:
            return  # control handled separately
        try_move(x, y - 1)
        # Optional: detect solved
        # if is_solved(board):
        #     pass  # could flash or show a dialog

    # Solve animation: undo user moves then generator moves
    def animate_undo(moves: List[Tuple[int, int]], idx: int, done_cb) -> None:
        if idx < 0:
            done_cb()
            return
        dx, dy = moves[idx]
        # Undo by moving blank opposite direction
        move_blank(-dx, -dy)
        pad.root.after(100, lambda: animate_undo(moves, idx - 1, done_cb))

    def do_solve() -> None:
        if solving["active"]:
            return
        solving["active"] = True

        def after_user():
            animate_undo(gen_moves, len(gen_moves) - 1, finish)

        def finish():
            solving["active"] = False
            user_moves.clear()
            gen_moves.clear()
            # After solve, board is solved and histories cleared

        animate_undo(user_moves, len(user_moves) - 1, after_user)

    # Control handlers
    def new_game() -> None:
        if solving["active"]:
            return
        # Start from solved
        nums = list(range(1, COLS * ROWS)) + [0]
        for y in range(ROWS):
            for x in range(COLS):
                board[y][x] = nums[y * COLS + x]
        gen_moves.clear()
        user_moves.clear()
        update_ui()
        # Perform random blank moves, avoiding immediate backtrack
        last = (0, 0)
        steps = 80
        for _ in range(steps):
            bx, by = find_blank()
            cand: List[Tuple[int, int]] = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = bx + dx, by + dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and (dx, dy) != (-last[0], -last[1]):
                    cand.append((dx, dy))
            if not cand:
                cand = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            dx, dy = random.choice(cand)
            move_blank(dx, dy)
            gen_moves.append((dx, dy))
            last = (dx, dy)
        # Ensure not already solved (unlikely); if solved, reshuffle again once
        if is_solved(board):
            last = (0, 0)
            gen_moves.clear()
            for _ in range(50):
                bx, by = find_blank()
                cand: List[Tuple[int, int]] = []
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = bx + dx, by + dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and (dx, dy) != (-last[0], -last[1]):
                        cand.append((dx, dy))
                if not cand:
                    cand = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                dx, dy = random.choice(cand)
                move_blank(dx, dy)
                gen_moves.append((dx, dy))
                last = (dx, dy)

    # Wire handlers for puzzle grid and control row
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y + 1].on_click = on_click  # type: ignore[index]

    # Control buttons at (0,0) and (1,0)
    pad[0, 0].on_click = lambda _e, _x, _y: new_game()
    pad[0, 0].text = "New"
    pad[2, 0].on_click = lambda _e, _x, _y: do_solve()
    pad[2, 0].text = "Solve"

    update_ui()
    new_game()
    pad.run()


if __name__ == "__main__":
    main()
