import random
import sys
from typing import Dict, List, Optional, Set, Tuple
import buttonpad

COLS = 16
ROWS = 10
SAND_ROW = ROWS - 1

WATER_COLOR = "#87CEEB"  # skyblue
SAND_COLOR = "#FFD54F"   # warm yellow

# Water creatures (must not overlap)
FISH_EMOJIS = [
    "🐟",  # fish
    "🐠",  # tropical fish
    "🐡",  # blowfish
    "🦈",  # shark
    "🐋",  # whale
    "🐬",  # dolphin
    "🐙",  # octopus
    "🦑",  # squid
]

BOTTOM_EMOJIS = ["🦀", "🦞"]  # crab, lobster


def build_empty_label_layout(cols: int, rows: int) -> str:
    # Use quoted empty strings to create labels
    line = ",".join(["`\"\""] * cols)
    return "\n".join([line for _ in range(rows)])


def main() -> None:
    layout = build_empty_label_layout(COLS, ROWS)

    bp = buttonpad.ButtonPad(
        layout=layout,
        cell_width=40,
        cell_height=40,
        h_gap=1,
        v_gap=1,
        window_color="#000000",  # thin grid lines look nicer against black window bg
        default_bg_color=WATER_COLOR,
        default_text_color="black",
        title="Fish Tank",
        resizable=True,
        border=4,
    )

    # Color water and sand, clear any text
    for y in range(ROWS):
        for x in range(COLS):
            el = bp[x, y]
            if y == SAND_ROW:
                el.background_color = SAND_COLOR
            else:
                el.background_color = WATER_COLOR
            el.text = ""

    # Occupancy of all animated emojis (both water and bottom)
    occupied: Set[Tuple[int, int]] = set()

    # ---- spawn fish in water (rows 0..SAND_ROW-1) ----
    water_cells = [(x, y) for y in range(0, SAND_ROW) for x in range(COLS)]

    # Choose a reasonable count: not too crowded
    fish_count = min(20, max(8, (COLS * (ROWS - 1)) // 12))

    # Build fish list with varying speeds
    fish: List[Dict] = []
    rng = random.Random()

    for i in range(fish_count):
        # Pick emoji cycling through list for variety
        emoji = FISH_EMOJIS[i % len(FISH_EMOJIS)]
        # Find a free starting position
        rng.shuffle(water_cells)
        start: Optional[Tuple[int, int]] = None
        for pos in water_cells:
            if pos not in occupied:
                start = pos
                break
        if start is None:
            break
        occupied.add(start)
        x, y = start
        bp[x, y].text = emoji
        # Half moderate speed (now doubled: 800-1300ms), half slow (now doubled: 1600-2600ms)
        if i % 2 == 0:
            speed = rng.randint(800, 1300)
        else:
            speed = rng.randint(1600, 2600)
        fish.append({"pos": start, "emoji": emoji, "ms": speed})

    # ---- bottom walkers (1-2 across sand) ----
    walkers: List[Dict] = []
    walker_count = rng.randint(1, 2)
    rng.shuffle(BOTTOM_EMOJIS)
    candidates = BOTTOM_EMOJIS[:walker_count]
    for emoji in candidates:
        # choose free x on sand
        xs = list(range(COLS))
        rng.shuffle(xs)
        start_x = None
        for x in xs:
            if (x, SAND_ROW) not in occupied:
                start_x = x
                break
        if start_x is None:
            continue
        occupied.add((start_x, SAND_ROW))
        bp[start_x, SAND_ROW].text = emoji
        dir_ = rng.choice([-1, 1])
    walkers.append({"pos": (start_x, SAND_ROW), "emoji": emoji, "dir": dir_, "ms": rng.randint(1200, 2200)})

    # ---- movement logic ----
    def free(p: Tuple[int, int]) -> bool:
        x, y = p
        return (0 <= x < COLS) and (0 <= y < ROWS) and (p not in occupied)

    def in_water(p: Tuple[int, int]) -> bool:
        return 0 <= p[0] < COLS and 0 <= p[1] < SAND_ROW

    def move_fish_one(idx: int) -> None:
        if idx >= len(fish):
            return
        info = fish[idx]
        x, y = info["pos"]
        emoji = info["emoji"]
        # 4-neighborhood; bias to keep moving horizontally a bit more often
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        rng.shuffle(candidates)
        # With small chance, don't move this tick
        if rng.random() < 0.15:
            bp.root.after(info["ms"], lambda i=idx: move_fish_one(i))
            return
        # Try to move to first free water cell
        for nx, ny in candidates:
            np = (nx, ny)
            if in_water(np) and free(np):
                # Update UI and occupancy
                bp[x, y].text = ""
                occupied.discard((x, y))
                bp[nx, ny].text = emoji
                occupied.add(np)
                info["pos"] = np
                break
        bp.root.after(info["ms"], lambda i=idx: move_fish_one(i))

    def move_walker_one(idx: int) -> None:
        if idx >= len(walkers):
            return
        info = walkers[idx]
        (x, y) = info["pos"]
        emoji = info["emoji"]
        dir_ = info["dir"]
        nx = x + dir_
        np = (nx, SAND_ROW)
        # If blocked or beyond edges, flip direction; otherwise move
        if not (0 <= nx < COLS) or not free(np):
            dir_ = -dir_
            info["dir"] = dir_
            nx = x + dir_
            np = (nx, SAND_ROW)
        if 0 <= nx < COLS and free(np):
            bp[x, y].text = ""
            occupied.discard((x, y))
            bp[nx, SAND_ROW].text = emoji
            occupied.add(np)
            info["pos"] = np
        bp.root.after(info["ms"], lambda i=idx: move_walker_one(i))

    # Kick off animations
    for i in range(len(fish)):
        bp.root.after(random.randint(0, 800), lambda i=i: move_fish_one(i))
    for i in range(len(walkers)):
        bp.root.after(random.randint(0, 600), lambda i=i: move_walker_one(i))

    bp.run()


if __name__ == "__main__":
    main()
