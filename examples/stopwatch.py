import sys
import time
from typing import Optional

# Allow local import when running from repo
sys.path.insert(0, __file__.split('/examples/')[0])
from ButtonPad import ButtonPad, BPButton  # noqa: E402

# Layout: 3 columns
# Row0: time label spans 3 cols (repeat same quoted text to merge)
# Row1: Start | Lap | Reset buttons
# Row2: "Laps:" | [entry spans 2 cols]
LAYOUT = "\n".join([
    "'00:00.00','00:00.00','00:00.00'",
    "Start,Lap,Reset",
    "'Laps:',[],[]",
])


def format_elapsed(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    hundredths = int((seconds - int(seconds)) * 100)
    return f"{minutes:02d}:{secs:02d}.{hundredths:02d}"


def main() -> None:
    bp = ButtonPad(
        layout=LAYOUT,
        cell_width=90,
        cell_height=56,
        h_gap=4,
        v_gap=4,
        title="Stopwatch",
        resizable=False,
        border=8,
    )

    # Elements
    time_label = bp[0, 0]  # merged across 3 cols
    start_btn = bp[0, 1]
    lap_btn = bp[1, 1]
    reset_btn = bp[2, 1]
    laps_entry = bp[1, 2]  # merged across 2 cols

    # Style time label
    try:
        time_label.font_size = 28
    except Exception:
        pass

    # Stopwatch state
    running = False
    start_time: float = 0.0
    base_elapsed: float = 0.0

    def update_display() -> None:
        # Called periodically; reschedule itself when running
        nonlocal running
        now_elapsed = base_elapsed + (time.monotonic() - start_time) if running else base_elapsed
        time_label.text = format_elapsed(now_elapsed)
        if running:
            # refresh about every 50ms
            try:
                bp.root.after(50, update_display)
            except Exception:
                pass

    def set_running(new_state: bool) -> None:
        nonlocal running, start_time
        if new_state == running:
            return
        running = new_state
        if running:
            # start / resume
            start_time = time.monotonic()
            start_btn.text = "Stop"
            update_display()
        else:
            # pause
            elapsed_now = base_elapsed + (time.monotonic() - start_time)
            set_base_elapsed(elapsed_now)
            start_btn.text = "Start"

    def set_base_elapsed(value: float) -> None:
        nonlocal base_elapsed
        base_elapsed = max(0.0, float(value))
        time_label.text = format_elapsed(base_elapsed)

    def on_start_stop(_: BPButton, _x: int, _y: int) -> None:
        set_running(not running)

    def on_lap(_: BPButton, _x: int, _y: int) -> None:
        # Record current displayed time regardless of running state
        stamp = time_label.text
        text = laps_entry.text.strip()
        if not text:
            laps_entry.text = stamp
        else:
            # Append on a new line
            laps_entry.text = f"{text}\n{stamp}"

    def on_reset(_: BPButton, _x: int, _y: int) -> None:
        nonlocal start_time
        if running:
            # Reset while running keeps running from zero
            start_time = time.monotonic()
            set_base_elapsed(0.0)
        else:
            set_base_elapsed(0.0)
        # Clear laps
        laps_entry.text = ""

    # Wire button actions
    start_btn.on_click = on_start_stop
    lap_btn.on_click = on_lap
    reset_btn.on_click = on_reset

    # Optional key bindings: Space toggles, L lap, R reset
    try:
        bp.map_key("space", 0, 1)  # will fire Start button handler
        bp.map_key("l", 1, 1)
        bp.map_key("r", 2, 1)
    except Exception:
        pass

    # Initial display
    set_base_elapsed(0.0)

    bp.run()


if __name__ == "__main__":
    main()
