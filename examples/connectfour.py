from __future__ import annotations

# Connect Four using ButtonPad
# - 7 columns x 6 rows of play cells (standard Connect Four)
# - Top row (y=0) has 7 buttons to drop a piece in a column
# - Play area is y=1..6 (labels). Labels background becomes red/black per player.
# - On win, the whole board flashes in the winner's color, then auto-resets.

from typing import List, Optional, Tuple

from buttonpad import ButtonPad, BPButton, BPLabel


COLS = 7  # columns (top row has 7 buttons)
ROWS = 6  # play rows beneath buttons; total grid rows = 1 + ROWS = 7

# UI tuning
CELL_W = 64
CELL_H = 64
HGAP = 6
VGAP = 6
BORDER = 10
TITLE = "Connect Four (ButtonPad)"

# Colors
EMPTY_COLOR = "white"
P1_COLOR = "red"
P2_COLOR = "black"
BTN_BG = "#e0e0e0"
BTN_FG = "black"


class ConnectFour:
    def __init__(self) -> None:
        # Build layout: one button row + 6 label rows
        top_buttons = ",".join(str(i + 1) for i in range(COLS))
        # Use backtick to prevent merge of identical empty labels
        label_row = ",".join("`''" for _ in range(COLS))
        layout = "\n".join([top_buttons] + [label_row for _ in range(ROWS)])

        self.pad = ButtonPad(
            layout,
            cell_width=CELL_W,
            cell_height=CELL_H,
            h_gap=HGAP,
            v_gap=VGAP,
            default_bg_color=BTN_BG,
            default_text_color=BTN_FG,
            title=TITLE,
            border=BORDER,
        )

        # State
        # board[c][r] -> 0 empty, 1 red, 2 black
        self.board: List[List[int]] = [[0 for _ in range(ROWS)] for _ in range(COLS)]
        self.current: int = 1  # 1 = red, 2 = black
        self.game_over: bool = False
        self.flashing: bool = False

        # Cache elements
        self.buttons: List[BPButton] = [self.pad[c, 0] for c in range(COLS)]  # type: ignore[assignment]
        self.cells: List[List[BPLabel]] = [[self.pad[c, r + 1] for r in range(ROWS)] for c in range(COLS)]  # type: ignore[list-item]

        # Wire button handlers
        for c in range(COLS):
            btn = self.buttons[c]
            btn.on_click = self._make_drop_handler(c)
            # Set two-line caption on the selector buttons
            btn.text = "Drop\nHere"

        self._new_game()

    # ----- UI helpers -----
    def _make_drop_handler(self, col: int):
        def handler(el, x, y):  # signature required by ButtonPad
            self.drop(col)
        return handler

    def _new_game(self) -> None:
        for c in range(COLS):
            for r in range(ROWS):
                self.board[c][r] = 0
                cell = self.cells[c][r]
                cell.background_color = EMPTY_COLOR
        # Reset buttons too (visual)
        for btn in self.buttons:
            btn.background_color = BTN_BG
            btn.text_color = BTN_FG
        self.current = 1
        self.game_over = False
        self.flashing = False

    def _color_for(self, player: int) -> str:
        return P1_COLOR if player == 1 else P2_COLOR

    # ----- Game actions -----
    def drop(self, col: int) -> None:
        if self.game_over or self.flashing:
            return
        # find lowest empty row
        row = self._lowest_empty_row(col)
        if row is None:
            return  # column full
        player = self.current
        self.board[col][row] = player
        self.cells[col][row].background_color = self._color_for(player)

        if self._check_win(col, row, player):
            self.game_over = True
            self._flash_winner(player)
            return

        # Switch player
        self.current = 2 if self.current == 1 else 1

    def _lowest_empty_row(self, col: int) -> Optional[int]:
        for r in range(ROWS - 1, -1, -1):
            if self.board[col][r] == 0:
                return r
        return None

    # ----- Win detection -----
    def _check_win(self, c: int, r: int, player: int) -> bool:
        # Check 4 directions: horiz, vert, diag1 (/), diag2 (\)
        return (
            self._count_line(c, r, 1, 0, player) >= 4 or
            self._count_line(c, r, 0, 1, player) >= 4 or
            self._count_line(c, r, 1, 1, player) >= 4 or
            self._count_line(c, r, 1, -1, player) >= 4
        )

    def _count_line(self, c: int, r: int, dc: int, dr: int, player: int) -> int:
        count = 1  # include (c,r)
        # forward
        cc, rr = c + dc, r + dr
        while 0 <= cc < COLS and 0 <= rr < ROWS and self.board[cc][rr] == player:
            count += 1
            cc += dc
            rr += dr
        # backward
        cc, rr = c - dc, r - dr
        while 0 <= cc < COLS and 0 <= rr < ROWS and self.board[cc][rr] == player:
            count += 1
            cc -= dc
            rr -= dr
        return count

    # ----- Flash + reset -----
    def _flash_winner(self, player: int) -> None:
        color = self._color_for(player)
        self.flashing = True
        total_steps = 8  # even number: on/off pairs
        self._flash_step(color, step=0, total=total_steps)

    def _all_elements(self):
        # flatten labels + buttons
        for btn in self.buttons:
            yield btn
        for c in range(COLS):
            for r in range(ROWS):
                yield self.cells[c][r]

    def _flash_step(self, color: str, step: int, total: int) -> None:
        on = (step % 2 == 0)
        for el in self._all_elements():
            try:
                el.background_color = color if on else EMPTY_COLOR
                el.text_color = "white" if on and color == P2_COLOR else BTN_FG
            except Exception:
                pass
        if step + 1 < total:
            # schedule next toggle
            self.pad.root.after(250, lambda: self._flash_step(color, step + 1, total))
        else:
            # Reset to new game
            self.pad.root.after(150, self._new_game)

    # ----- Entrypoint -----
    def run(self) -> None:
        self.pad.run()


if __name__ == "__main__":
    ConnectFour().run()
