from __future__ import annotations

"""
Dodger: 20x20 original concept adapted.
- Grid now omits the last visible row for scoring; score & high score shown in status bar.
- Move with Arrow Keys or WASD. No wrap-around.
- Hazards stream in from edges toward the opposite side as red background cells.
- Collision triggers Game Over dialog and restart. High score resets only when program exits.
"""

import random
from typing import Dict, List, Tuple

try:
    import buttonpad
except Exception:  # fallback for local dev
    import ButtonPad as buttonpad  # type: ignore

COLS = 21
ROWS = 20  # removed last row of widgets; scoring now in status bar
TITLE = "Dodger"

# UI sizing/colors
CELL_W = 36
CELL_H = 36
HGAP = 3
VGAP = 3
BORDER = 8
WINDOW_BG = "#f0f0f0"  # keep labels readable (labels default to black text)
PLAYER_BG = "#2b78ff"   # blue highlight for player
HAZARD_BG = "#ff5a5a"   # red background for hazards

TICK_MS = 140  # game tick interval
SPAWN_PROB_PER_TICK = 0.35  # chance to spawn one hazard each tick

CenterBand = range(COLS // 2 - 2, COLS // 2 + 2 + 1)  # 5x5-ish band around center


def build_label_grid(cols: int, rows: int) -> str:
    # Use no-merge quoted-empty labels for every cell: `''
    row = ",".join(["`''"] * cols)
    return "\n".join([row for _ in range(rows)])


def main() -> None:
    layout = build_label_grid(COLS, ROWS)
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=CELL_W,
        cell_height=CELL_H,
        h_gap=HGAP,
        v_gap=VGAP,
        border=BORDER,
        title=TITLE,
        window_color=WINDOW_BG,
        resizable=True,
        status_bar="Score: 0  High: 0",
    )

    state: Dict[str, object] = {
        "player": {"x": 0, "y": 0},
        "hazards": [],  # list of dicts {x,y,dx,dy}
        "hazard_set": set(),  # set of (x,y) for quick collision checks
        "score": 0,
        "high_score": 0,
        "running": False,
        "after_id": None,
    }

    # --- helpers to read/update UI ---
    def set_hazard_bg(x: int, y: int) -> None:
        # Color the cell background to indicate a hazard; leave text empty
        el = pad[x, y]
        el.text = ""
        try:
            el.background_color = HAZARD_BG
        except Exception:
            pass

    def clear_cell_visual(x: int, y: int) -> None:
        el = pad[x, y]
        el.text = ""
        try:
            el.background_color = WINDOW_BG
        except Exception:
            pass

    def draw_player(px: int, py: int) -> None:
        el = pad[px, py]
        el.text = ""
        try:
            el.background_color = PLAYER_BG
        except Exception:
            pass

    def undraw_player(px: int, py: int) -> None:
        # restore to normal background
        clear_cell_visual(px, py)

    def update_status_bar() -> None:
        try:
            pad.status_bar = f"Score: {state['score']}  High: {state['high_score']}"
        except Exception:
            pass

    # --- game control ---
    def reset_board_visuals() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                clear_cell_visual(x, y)
        update_status_bar()

    def start_game() -> None:
        # cancel any prior tick
        after_id = state.get("after_id")
        if after_id:
            try:
                pad.root.after_cancel(after_id)  # type: ignore[arg-type]
            except Exception:
                pass
            state["after_id"] = None

        # reset model
        state["hazards"] = []
        state["hazard_set"] = set()
        state["score"] = 0
        state["running"] = True

        reset_board_visuals()

        # pick a start near center
        while True:
            sx = random.choice(list(CenterBand))
            sy = random.choice(list(CenterBand))
            break  # any center band cell okay now
        state["player"] = {"x": sx, "y": sy}
        draw_player(sx, sy)
        schedule_next_tick()

    def game_over() -> None:
        # stop ticking
        state["running"] = False
        after_id = state.get("after_id")
        if after_id:
            try:
                pad.root.after_cancel(after_id)  # type: ignore[arg-type]
            except Exception:
                pass
            state["after_id"] = None
        try:
            buttonpad.alert("Game Over")
        except Exception:
            pass
        # restart fresh
        start_game()

    # --- hazards ---
    def spawn_hazard() -> None:
        # Decide edge and direction; avoid score cell; avoid spawning atop player.
        side = random.choice(["left", "right", "top", "bottom"])
        px = state["player"]["x"]  # type: ignore[index]
        py = state["player"]["y"]  # type: ignore[index]
        if side == "left":
            x = 0
            y = random.randrange(ROWS)
            dx, dy = 1, 0
        elif side == "right":
            x = COLS - 1
            y = random.randrange(ROWS)
            dx, dy = -1, 0
        elif side == "top":
            x = random.randrange(COLS)
            y = 0
            dx, dy = 0, 1
        else:  # bottom
            x = random.randrange(COLS)
            y = ROWS - 1
            dx, dy = 0, -1

        # avoid spawning atop player
        if (x == px and y == py):
            return

        hazards: List[Dict[str, int]] = state["hazards"]  # type: ignore[assignment]
        hset: set[Tuple[int, int]] = state["hazard_set"]  # type: ignore[assignment]
        if (x, y) in hset:
            return  # cell already occupied; skip
        hazards.append({"x": x, "y": y, "dx": dx, "dy": dy})
        hset.add((x, y))
        set_hazard_bg(x, y)

    def move_hazards() -> bool:
        """Advance hazards one step. Return True if collision occurred."""
        hazards: List[Dict[str, int]] = state["hazards"]  # type: ignore[assignment]
        hset: set[Tuple[int, int]] = state["hazard_set"]  # type: ignore[assignment]
        if not hazards:
            return False

        px = state["player"]["x"]  # type: ignore[index]
        py = state["player"]["y"]  # type: ignore[index]

        # clear current visuals (but not where player stands)
        for h in hazards:
            hx, hy = h["x"], h["y"]
            if not (hx == px and hy == py):
                clear_cell_visual(hx, hy)

        new_list: List[Dict[str, int]] = []
        new_set: set[Tuple[int, int]] = set()
        for h in hazards:
            nx = h["x"] + h["dx"]
            ny = h["y"] + h["dy"]

            # off-grid => drop
            if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
                continue
            # no special reserved cell now
            # collision with player?
            if nx == px and ny == py:
                return True

            # keep and draw
            new_list.append({"x": nx, "y": ny, "dx": h["dx"], "dy": h["dy"]})
            new_set.add((nx, ny))

        # draw new positions
        for (hx, hy) in new_set:
            set_hazard_bg(hx, hy)

        # swap
        state["hazards"] = new_list
        state["hazard_set"] = new_set
        return False

    # --- ticking ---
    def tick() -> None:
        if not state["running"]:
            return
        # score
        state["score"] = int(state["score"]) + 1
        if state["score"] > state["high_score"]:  # type: ignore[operator]
            state["high_score"] = state["score"]
        update_status_bar()

        # maybe spawn
        if random.random() < SPAWN_PROB_PER_TICK:
            spawn_hazard()

        # move hazards and check collision
        if move_hazards():
            game_over()
            return

        schedule_next_tick()

    def schedule_next_tick() -> None:
        try:
            state["after_id"] = pad.root.after(TICK_MS, tick)
        except Exception:
            state["after_id"] = None

    # --- input ---
    def try_move(dx: int, dy: int) -> None:
        if not state["running"]:
            return
        px = state["player"]["x"]  # type: ignore[index]
        py = state["player"]["y"]  # type: ignore[index]
        nx = max(0, min(COLS - 1, px + dx))
        ny = max(0, min(ROWS - 1, py + dy))
        # don't move if clamped to same position
        if nx == px and ny == py:
            return
    # no reserved score cell constraint
        # collision if moving into hazard
        if (nx, ny) in state["hazard_set"]:  # type: ignore[operator]
            game_over()
            return
        # update visuals
        undraw_player(px, py)
        state["player"] = {"x": nx, "y": ny}
        draw_player(nx, ny)

    def on_left(_evt=None):
        try_move(-1, 0)

    def on_right(_evt=None):
        try_move(1, 0)

    def on_up(_evt=None):
        try_move(0, -1)

    def on_down(_evt=None):
        try_move(0, 1)

    # Bind arrows and WASD (both lowercase/uppercase)
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

    # start the first run
    start_game()

    pad.run()


if __name__ == "__main__":
    main()
