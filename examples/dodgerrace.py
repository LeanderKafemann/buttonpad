from __future__ import annotations

"""
Dodgerace: 21x21 grid. Reach the green goal while dodging red hazards.
- Player starts at (10, 3); initial goal at (10, 17). Goal toggles between (10, 17) and (10, 3) on reach.
- Central blocked zone (inclusive) is from (7, 7) to (13, 13); blocks player movement only (hazards can pass through).
- Hazards are red background cells and should appear red even within the black blocked zone.
- Score increases by 1 whenever the player reaches the goal; shown in the status bar.
- Arrow keys or WASD move the player; no wrap-around. Collision with a hazard shows Game Over, then restarts.
"""

import random
from typing import Dict, List, Tuple, Set

try:
    import buttonpad
except Exception:
    import ButtonPad as buttonpad  # type: ignore

# Grid
COLS = 21
ROWS = 21
TITLE = "Dodgerace"

# UI sizing/colors
CELL_W = 34
CELL_H = 34
HGAP = 2
VGAP = 2
BORDER = 8
WINDOW_BG = "#f0f0f0"
PLAYER_BG = "#2b78ff"
HAZARD_BG = "#ff5a5a"
BLOCK_BG = "#000000"
GOAL_BG = "#2ecc71"

TICK_MS = 140
SPAWN_PROB_PER_TICK = 0.35

# Coordinates
START_POS: Tuple[int, int] = (10, 3)
GOAL_A: Tuple[int, int] = (10, 3)
GOAL_B: Tuple[int, int] = (10, 17)
BLOCK_MIN = 7
BLOCK_MAX = 13  # inclusive


def build_label_grid(cols: int, rows: int) -> str:
    # No-merge labels everywhere: `''
    row = ",".join(["`''"] * cols)
    return "\n".join([row for _ in range(rows)])


def is_block(x: int, y: int) -> bool:
    return (BLOCK_MIN <= x <= BLOCK_MAX) and (BLOCK_MIN <= y <= BLOCK_MAX)


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
        status_bar="Score: 0  High score: 0",
    )

    state: Dict[str, object] = {
        "player": {"x": START_POS[0], "y": START_POS[1]},
        "hazards": [],  # list[{x,y,dx,dy}]
        "hazard_set": set(),  # set[(x,y)]
        "goal": GOAL_B,  # initial goal at bottom middle
        "score": 0,
        "high_score": 0,
        "running": False,
        "after_id": None,
    }

    # --- rendering helpers ---
    def draw_cell(x: int, y: int) -> None:
        """Render a single cell based on layered state priority.
        Priority: player > hazard > goal > block > background.
        """
        el = pad[x, y]
        el.text = ""
        px = state["player"]["x"]  # type: ignore[index]
        py = state["player"]["y"]  # type: ignore[index]
        hset: Set[Tuple[int, int]] = state["hazard_set"]  # type: ignore[assignment]
        goal: Tuple[int, int] = state["goal"]  # type: ignore[assignment]

        if x == px and y == py:
            bg = PLAYER_BG
        elif (x, y) in hset:
            bg = HAZARD_BG
        elif (x, y) == goal:
            bg = GOAL_BG
        elif is_block(x, y):
            bg = BLOCK_BG
        else:
            bg = WINDOW_BG
        try:
            el.background_color = bg
        except Exception:
            pass

    def draw_all() -> None:
        for y in range(ROWS):
            for x in range(COLS):
                draw_cell(x, y)

    def update_status() -> None:
        try:
            pad.status_bar = f"Score: {state['score']}  High score: {state['high_score']}"
        except Exception:
            pass

    # --- game control ---
    def start_game() -> None:
        # cancel previous tick
        after_id = state.get("after_id")
        if after_id:
            try:
                pad.root.after_cancel(after_id)  # type: ignore[arg-type]
            except Exception:
                pass
            state["after_id"] = None

        state["hazards"] = []
        state["hazard_set"] = set()
        state["score"] = 0
        state["goal"] = GOAL_B
        state["player"] = {"x": START_POS[0], "y": START_POS[1]}
        state["running"] = True
        update_status()
        draw_all()
        schedule_next_tick()

    def game_over() -> None:
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
        start_game()

    # --- hazards ---
    def spawn_hazard() -> None:
        side = random.choice(["left", "right", "top", "bottom"])
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

        # avoid duplicate spawn in same cell
        hset: Set[Tuple[int, int]] = state["hazard_set"]  # type: ignore[assignment]
        if (x, y) in hset:
            return

        hazards: List[Dict[str, int]] = state["hazards"]  # type: ignore[assignment]
        hazards.append({"x": x, "y": y, "dx": dx, "dy": dy})
        hset.add((x, y))
        draw_cell(x, y)

    def move_hazards() -> bool:
        hazards: List[Dict[str, int]] = state["hazards"]  # type: ignore[assignment]
        hset: Set[Tuple[int, int]] = state["hazard_set"]  # type: ignore[assignment]
        if not hazards:
            return False

        px = state["player"]["x"]  # type: ignore[index]
        py = state["player"]["y"]  # type: ignore[index]

        old_set = set(hset)
        new_list: List[Dict[str, int]] = []
        new_set: Set[Tuple[int, int]] = set()

        for h in hazards:
            nx = h["x"] + h["dx"]
            ny = h["y"] + h["dy"]

            # off-grid => drop
            if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
                continue

            # collision with player?
            if nx == px and ny == py:
                return True

            new_list.append({"x": nx, "y": ny, "dx": h["dx"], "dy": h["dy"]})
            new_set.add((nx, ny))

        # swap sets first, then redraw affected cells (old and new positions)
        state["hazards"] = new_list
        state["hazard_set"] = new_set
        affected = old_set | new_set
        for (ax, ay) in affected:
            draw_cell(ax, ay)
        return False

    # --- ticking ---
    def tick() -> None:
        if not state["running"]:
            return

        # spawn hazards
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

        # if no movement
        if nx == px and ny == py:
            return
        # block player from entering the blocked zone
        if is_block(nx, ny):
            return
        # collision if moving into hazard
        if (nx, ny) in state["hazard_set"]:  # type: ignore[operator]
            game_over()
            return

        # redraw old and new
        state["player"] = {"x": nx, "y": ny}
        draw_cell(px, py)
        draw_cell(nx, ny)

        # check goal
        cur_goal: Tuple[int, int] = state["goal"]  # type: ignore[assignment]
        if (nx, ny) == cur_goal:
            state["score"] = int(state["score"]) + 1
            # update high score
            if state["score"] > state["high_score"]:  # type: ignore[operator]
                state["high_score"] = state["score"]
            update_status()
            # toggle goal to the opposite coordinate
            new_goal = GOAL_A if cur_goal == GOAL_B else GOAL_B
            old_goal = cur_goal
            state["goal"] = new_goal
            # redraw both goal cells to reflect change and layering
            draw_cell(old_goal[0], old_goal[1])
            draw_cell(new_goal[0], new_goal[1])

    def on_left(_evt=None):
        try_move(-1, 0)

    def on_right(_evt=None):
        try_move(1, 0)

    def on_up(_evt=None):
        try_move(0, -1)

    def on_down(_evt=None):
        try_move(0, 1)

    # Bind arrows and WASD
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

    start_game()
    pad.run()


if __name__ == "__main__":
    main()
