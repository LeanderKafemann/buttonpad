import sys
from typing import List, Optional, Tuple

# Enable local import of ButtonPad when running from repo
sys.path.insert(0, __file__.split('/examples/')[0])
from ButtonPad import ButtonPad, BPButton  # noqa: E402

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


def main() -> None:
    layout = build_layout()

    peg_count_initial = sum(1 for y in range(ROWS) for x in range(COLS) if is_valid_cell(x, y)) - 1

    # New Game callback placeholder; will be rebound after bp is created
    def noop_new_game():
        pass

    bp = ButtonPad(
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
        status_bar=f"Pegs: {peg_count_initial}",
        menu={
            "Game": {
                "New Game": (lambda: noop_new_game(), "Cmd+N"),
            }
        },
    )

    # --- game state ---
    board: List[List[int]] = [[-1] * COLS for _ in range(ROWS)]
    selected: Optional[Tuple[int, int]] = None

    def init_board() -> None:
        nonlocal board, selected
        selected = None
        for y in range(ROWS):
            for x in range(COLS):
                if is_valid_cell(x, y):
                    board[y][x] = 1
                else:
                    board[y][x] = -1
        # center empty
        board[3][3] = 0

    def peg_count() -> int:
        return sum(1 for y in range(ROWS) for x in range(COLS) if board[y][x] == 1)

    def update_status() -> None:
        bp.status_bar = f"Pegs: {peg_count()}"

    def apply_cell_style(x: int, y: int) -> None:
        el = bp[x, y]
        val = board[y][x]
        if val == -1:
            # invalid label area (no change needed except background blending)
            el.text = ""
            try:
                el.background_color = WINDOW_BG
            except Exception:
                pass
            return
        # Valid button cell
        if val == 1:
            # Peg present
            el.text = "●"
            el.text_color = PEG_TEXT
            base_bg = PEG_BG
        else:
            # Empty hole
            el.text = ""
            base_bg = HOLE_BG
        # Selection highlight
        if selected == (x, y) and val == 1:
            el.background_color = SELECT_BG
        else:
            el.background_color = base_bg
        # Slightly larger font for visibility
        try:
            el.font_size = 20
        except Exception:
            pass

    def update_all_cells() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                apply_cell_style(x, y)

    def in_bounds(x: int, y: int) -> bool:
        return 0 <= x < COLS and 0 <= y < ROWS

    def can_jump(sx: int, sy: int, dx: int, dy: int) -> bool:
        # Destination must be exactly two steps away in a cardinal direction
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
        # Update only affected cells
        apply_cell_style(sx, sy)
        apply_cell_style(mx, my)
        apply_cell_style(dx, dy)
        update_status()

    def on_cell_click(_: BPButton, x: int, y: int) -> None:
        nonlocal selected
        if not is_valid_cell(x, y):
            return
        val = board[y][x]
        if val == 1:
            # Select or unselect this peg
            if selected == (x, y):
                selected = None
                apply_cell_style(x, y)
                return
            # Change previous selection back to normal if any
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
        # Otherwise ignore

    def new_game() -> None:
        init_board()
        update_all_cells()
        update_status()

    # Wire menu now that new_game exists
    def rebind_menu() -> None:
        bp.menu = {
            "Game": {
                "New Game": (new_game, "Cmd+N"),
            }
        }

    # Initialize board, UI, and callbacks
    init_board()
    update_all_cells()
    update_status()

    # Attach click handlers to valid cells
    for y in range(ROWS):
        for x in range(COLS):
            if is_valid_cell(x, y):
                el = bp[x, y]
                el.on_click = lambda _el, xx=x, yy=y: on_cell_click(_el, xx, yy)

    rebind_menu()

    bp.run()


if __name__ == "__main__":
    main()
