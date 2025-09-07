from __future__ import annotations
import random
from typing import List
import buttonpad

COLS = 2
ROWS = 2

# UI
WINDOW_BG = "#0e1220"  # dark backdrop
TEXT_COLOR = "#ffffff"

# Base and lit colors per quadrant (index: y*2 + x)
BASE_COLORS = [
    "#2ecc71",  # green
    "#e74c3c",  # red
    "#3498db",  # blue
    "#f1c40f",  # yellow
]
LIT_COLORS = [
    "#6ff7a8",  # light green
    "#ff8a73",  # light red
    "#7cbcff",  # light blue
    "#ffe27a",  # light yellow
]

FLASH_MS = 450
GAP_MS = 160
BETWEEN_ROUNDS_MS = 500
CLICK_FLASH_MS = 180


def build_layout() -> str:
    # Two rows of two independent LABELS (blank). Use `"" to create a no-merge blank BPLabel.
    # Backtick prevents auto-merge; "" (quoted empty string) forces label kind instead of button.
    row = ",".join(['`""'] * COLS)
    return "\n".join([row for _ in range(ROWS)])


essential_indices = [0, 1, 2, 3]


def main() -> None:
    layout = build_layout()
    pad = buttonpad.ButtonPad(
        layout=layout,
        cell_width=200,
        cell_height=200,
        h_gap=4,
        v_gap=4,
        border=8,
        title="Simon",
        default_text_color=TEXT_COLOR,
        window_color=WINDOW_BG,
        resizable=True,
    )
    # Initialize status bar (Score tracking)
    try:
        pad.status_bar = "Score: 0  High: 0"
    except Exception:
        pass

    # Apply per-cell base colors, label text (Q W A S), subtle text colors, and hotkeys
    label_chars = ["Q", "W", "A", "S"]  # order: (0,0) (1,0) (0,1) (1,1)
    subtle_text_colors = [
        "#146c3b",  # darker green
        "#82271d",  # darker red
        "#1a5078",  # darker blue
        "#7d6a10",  # muted yellow/brown
    ]
    keysyms = ["q", "w", "a", "s"]
    for y in range(ROWS):
        for x in range(COLS):
            idx = y * COLS + x
            el = pad[x, y]  # type: ignore[index]
            el.background_color = BASE_COLORS[idx]
            el.text = label_chars[idx]
            try:
                el.text_color = subtle_text_colors[idx]
            except Exception:
                pass
            # Assign hotkey directly to label
            try:
                el.hotkey = keysyms[idx]
            except Exception:
                # Fallback to explicit map if property assignment fails
                try:
                    pad.map_key(keysyms[idx], x, y)
                except Exception:
                    pass

    sequence: List[int] = []
    state = {"busy": False, "expect": 0, "accept": False, "timer_id": None, "score": 0, "high_score": 0}

    def set_lit(idx: int, lit: bool) -> None:
        x, y = idx % COLS, idx // COLS
        pad[x, y].background_color = (LIT_COLORS[idx] if lit else BASE_COLORS[idx])  # type: ignore[index]

    def flash_idx(idx: int, on_ms: int, after_cb) -> None:
        set_lit(idx, True)
        pad.root.after(on_ms, lambda: (set_lit(idx, False), after_cb()))

    def playback_sequence() -> None:
        state["busy"] = True
        state["accept"] = False
        state["expect"] = 0
        i = 0

        def next_step():
            nonlocal i
            if i >= len(sequence):
                state["busy"] = False
                state["accept"] = True
                return
            idx = sequence[i]
            def cont():
                pad.root.after(GAP_MS, advance)
            flash_idx(idx, FLASH_MS, cont)

        def advance():
            nonlocal i
            i += 1
            next_step()

        next_step()

    def add_step_and_play() -> None:
        # Append a new random index and play back
        sequence.append(random.choice(essential_indices))
        pad.root.after(BETWEEN_ROUNDS_MS, playback_sequence)

    def _update_status_bar() -> None:
        try:
            pad.status_bar = f"Score: {state['score']}  High: {state['high_score']}"
        except Exception:
            pass
        # Only reschedule while game is active (sequence exists)
        try:
            state["timer_id"] = pad.root.after(500, _update_status_bar)
        except Exception:
            pass

    def game_over() -> None:
        # Report the last fully completed sequence length
        length_achieved = max(0, len(sequence) - 1)
        try:
            buttonpad.alert(f"Game Over\nScore: {length_achieved}")
        except Exception:
            pass
        new_game()

    def on_cell_click(_el, x: int, y: int) -> None:
        if state["busy"] or not state["accept"]:
            return
        idx = y * COLS + x
        # brief click flash
        set_lit(idx, True)
        pad.root.after(CLICK_FLASH_MS, lambda: set_lit(idx, False))

        expected = sequence[state["expect"]]
        if idx == expected:
            state["expect"] += 1
            # completed the whole sequence correctly -> extend
            if state["expect"] == len(sequence):
                state["accept"] = False
                # Completed current sequence -> increment score
                state["score"] += 1
                if state["score"] > state["high_score"]:
                    state["high_score"] = state["score"]
                _update_status_bar()
                add_step_and_play()
        else:
            game_over()

    # Wire clicks
    for y in range(ROWS):
        for x in range(COLS):
            pad[x, y].on_click = on_cell_click  # type: ignore[index]

    def new_game() -> None:
        # Cancel previous timer
        if state.get("timer_id") is not None:
            try:
                pad.root.after_cancel(state["timer_id"])  # type: ignore[arg-type]
            except Exception:
                pass
            state["timer_id"] = None
        sequence.clear()
        state["busy"] = False
        state["accept"] = False
        state["expect"] = 0
        state["score"] = 0  # high_score persists across games in same run
        try:
            pad.status_bar = f"Score: 0  High: {state['high_score']}"
        except Exception:
            pass
        _update_status_bar()  # initial update
        add_step_and_play()

    # Start
    new_game()

    pad.run()


if __name__ == "__main__":
    main()
