# lights_out_5x5.py
from __future__ import annotations

import random
from typing import List, Tuple
from buttonpad import ButtonPad  # adjust if your package/module name differs

# 5x5 grid where each cell is a standalone button (no-merge using backtick `)
LAYOUT = """
`.,`.,`.,`.,`.
`.,`.,`.,`.,`.
`.,`.,`.,`.,`.
`.,`.,`.,`.,`.
`.,`.,`.,`.,`.
""".strip()

GRID_W = GRID_H = 5

# Colors / looks
ON_BG   = "#ffd54f"   # warm yellow
OFF_BG  = "#2b2b2b"   # dark gray
ON_FG   = "black"
OFF_FG  = "#bbbbbb"
FONT    = "TkDefaultFont"
FONT_SZ = 20

FLASH_ON  = "#00e676"  # green flash
FLASH_OFF = "#1e1e1e"
FLASH_COUNT = 6        # total on/off toggles
FLASH_MS    = 120      # ms between flashes

class LightsOut:
    def __init__(self) -> None:
        self.pad = ButtonPad(
            layout=LAYOUT,
            cell_width=70,
            cell_height=70,
            h_gap=6,
            v_gap=6,
            window_color="#121212",
            default_bg_color="#121212",
            default_text_color="white",
            title="Lights Out (5×5)",
            resizable=True,
            border=12,
        )

        # state[y][x] -> bool (True = ON, False = OFF)
        self.state: List[List[bool]] = [[False]*GRID_W for _ in range(GRID_H)]

        # Initialize appearance & handlers
        for y in range(GRID_H):
            for x in range(GRID_W):
                el = self.pad[x, y]
                el.font_name = FONT
                el.font_size = FONT_SZ
                #el.text = "●"  # we’ll dim/brighten with colors
                el.text = ''
                # clicking toggles (element, x, y) signature:
                el.on_click = self.handle_click

        self.new_random_puzzle()
        self.redraw()

    # --- game logic ---
    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < GRID_W and 0 <= y < GRID_H

    def toggle(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.state[y][x] = not self.state[y][x]

    def handle_click(self, _el, x: int, y: int) -> None:
        # toggle clicked + orthogonal neighbors
        self.toggle(x, y)
        self.toggle(x-1, y)
        self.toggle(x+1, y)
        self.toggle(x, y-1)
        self.toggle(x, y+1)
        self.redraw()

        if self.is_solved():
            self.win_flash_then_new()

    def is_solved(self) -> bool:
        # solved when all OFF
        return all(not v for row in self.state for v in row)

    def new_random_puzzle(self, moves: int = 20) -> None:
        # start all-off, then apply N random valid moves to guarantee solvable
        for y in range(GRID_H):
            for x in range(GRID_W):
                self.state[y][x] = False
        for _ in range(moves):
            rx, ry = random.randrange(GRID_W), random.randrange(GRID_H)
            # simulate a click move:
            self.toggle(rx, ry)
            self.toggle(rx-1, ry)
            self.toggle(rx+1, ry)
            self.toggle(rx, ry-1)
            self.toggle(rx, ry+1)

    # --- UI ---
    def redraw(self) -> None:
        for y in range(GRID_H):
            for x in range(GRID_W):
                el = self.pad[x, y]
                if self.state[y][x]:
                    el.background_color = ON_BG
                    el.text_color = ON_FG
                else:
                    el.background_color = OFF_BG
                    el.text_color = OFF_FG

    def win_flash_then_new(self) -> None:
        """
        Flash the whole board, then generate a new puzzle and redraw.
        """
        # capture original colors to restore after flashing
        original: List[List[Tuple[str, str]]] = [
            [(self.pad[x, y].background_color, self.pad[x, y].text_color) for x in range(GRID_W)]
            for y in range(GRID_H)
        ]

        def set_all(bg: str, fg: str) -> None:
            for y in range(GRID_H):
                for x in range(GRID_W):
                    el = self.pad[x, y]
                    el.background_color = bg
                    el.text_color = fg

        def do_flash(step: int = 0) -> None:
            if step >= FLASH_COUNT:
                # done flashing: start a new puzzle and restore normal looks
                self.new_random_puzzle()
                self.redraw()
                return

            if step % 2 == 0:
                set_all(FLASH_ON, "black")
            else:
                set_all(FLASH_OFF, "white")

            self.pad.root.after(FLASH_MS, lambda: do_flash(step + 1))

        do_flash()

    def run(self) -> None:
        self.pad.run()


if __name__ == "__main__":
    LightsOut().run()
