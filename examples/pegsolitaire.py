import sys
from typing import List, Optional, Tuple
import buttonpad

COLS = 7
ROWS = 7

# Theme
WINDOW_BG = "#6d4c41"   # brown
PEG_BG = "#d7ccc8"      # light wood for cells with a peg
HOLE_BG = "#bcaaa4"     # slightly darker wood for empty holes
PEG_TEXT = "#4e342e"    # dark brown peg
SELECT_BG = "#ffe082"   # highlight selected peg (amber)

# Board values: -1 invalid, 0 empty, 1 peg

def is_valid_cell(x: int, y: int) -> bool:
    # English cross board: valid if in central cross (rows/cols 2..4)
    return (2 <= x <= 4) or (2 <= y <= 4)


def build_layout() -> str:
    # Use backtick to disable merge; labels for invalid cells, buttons for valid
    rows: List[str] = []
    for y in range(ROWS):
        tokens: List[str] = []
        for x in range(COLS):
            if is_valid_cell(x, y):
                tokens.append("`o")  # no-merge button; placeholder text (will be updated)
            else:
                tokens.append("`\"\"")  # no-merge blank label
        rows.append(",".join(tokens))
    return "\n".join(rows)


########################
# Global game state
bp = None  # type: ignore
board: List[List[int]] = []
selected: Optional[Tuple[int, int]] = None


def init_board() -> None:
    global board, selected
    selected = None
    if not board:
        board = [[-1] * COLS for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            if is_valid_cell(x, y):
                board[y][x] = 1
            else:
                board[y][x] = -1
    board[3][3] = 0  # center empty


def peg_count() -> int:
    return sum(1 for y in range(ROWS) for x in range(COLS) if board and board[y][x] == 1)


def update_status() -> None:
    if bp is not None:
        try:
            bp.status_bar = f"Pegs: {peg_count()}"
        except Exception:
            pass


def apply_cell_style(x: int, y: int) -> None:
    if bp is None or not board:
        return
    el = bp[x, y]
    val = board[y][x]
    if val == -1:
        el.text = ""
        try:
            el.background_color = WINDOW_BG
        except Exception:
            pass
        return
    if val == 1:
        el.text = "●"
        el.text_color = PEG_TEXT
        base_bg = PEG_BG
    else:
        el.text = ""
        base_bg = HOLE_BG
    if selected == (x, y) and val == 1:
        el.background_color = SELECT_BG
    else:
        el.background_color = base_bg
    try:
        el.font_size = 20
    except Exception:
        pass


def update_all_cells() -> None:
    if not board or bp is None:
        return
    for y in range(ROWS):
        for x in range(COLS):
            apply_cell_style(x, y)


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < COLS and 0 <= y < ROWS


def can_jump(sx: int, sy: int, dx: int, dy: int) -> bool:
    if not (in_bounds(dx, dy) and is_valid_cell(dx, dy)):
        return False
    if board[sy][sx] != 1 or board[dy][dx] != 0:
        return False
    vx, vy = dx - sx, dy - sy
    if (abs(vx), abs(vy)) not in ((2, 0), (0, 2)):
        return False
    mx, my = sx + vx // 2, sy + vy // 2
    if not in_bounds(mx, my) or board[my][mx] != 1:
        return False
    return True


def perform_jump(sx: int, sy: int, dx: int, dy: int) -> None:
    vx, vy = dx - sx, dy - sy
    mx, my = sx + vx // 2, sy + vy // 2
    board[sy][sx] = 0
    board[my][mx] = 0
    board[dy][dx] = 1
    apply_cell_style(sx, sy)
    apply_cell_style(mx, my)
    apply_cell_style(dx, dy)
    update_status()


def on_cell_click(_el, x: int, y: int) -> None:
    global selected
    if not is_valid_cell(x, y):
        return
    val = board[y][x]
    if val == 1:
        if selected == (x, y):
            selected = None
            apply_cell_style(x, y)
            return
        if selected is not None:
            px, py = selected
            apply_cell_style(px, py)
        selected = (x, y)
        apply_cell_style(x, y)
        return
    if val == 0 and selected is not None:
        sx, sy = selected
        if can_jump(sx, sy, x, y):
            perform_jump(sx, sy, x, y)
            selected = None
            return


def new_game() -> None:
    init_board()
    update_all_cells()
    update_status()


def rebind_menu() -> None:
    if bp is not None:
        bp.menu = {"File": {"New Game": (new_game, "Cmd+N")}}


def main() -> None:
    global bp, board, selected
    layout = build_layout()
    peg_count_initial = sum(1 for y in range(ROWS) for x in range(COLS) if is_valid_cell(x, y)) - 1
    bp = buttonpad.ButtonPad(
        layout=layout,
        cell_width=48,
        cell_height=48,
        h_gap=2,
        v_gap=2,
        window_color=WINDOW_BG,
        default_bg_color=PEG_BG,
        default_text_color=PEG_TEXT,
        title="Peg Solitaire",
        resizable=False,
        border=8,
        status_bar=f"Pegs remaining: {peg_count_initial}",
        menu=None,
    )

    bp.status_bar_text_color = "black"
    board = [[-1] * COLS for _ in range(ROWS)]
    selected = None
    init_board()
    update_all_cells()
    update_status()
    for y in range(ROWS):
        for x in range(COLS):
            if is_valid_cell(x, y):
                el = bp[x, y]
                el.on_click = lambda _el, xx=x, yy=y: on_cell_click(_el, xx, yy)
    rebind_menu()
    bp.run()


if __name__ == "__main__":
    main()
