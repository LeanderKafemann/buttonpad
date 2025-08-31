from __future__ import annotations

# Conway's Game of Life using ButtonPad
# - 32 x 32 clickable cells (buttons)
# - 33rd row: one play/pause button spanning all 32 columns
# - Off color: dark blue; On color: white
# - Starts paused (▶). Click cells to toggle; click the big button to play/pause.

from typing import List, Tuple

try:
	import buttonpad
except Exception:
	import ButtonPad as buttonpad  # type: ignore

TITLE = "Conway's Game of Life"
COLS = 20
ROWS = 20  # cell rows (a control row is added below)

# Ensure there are at least 4 columns so the 4 control buttons can each span >= 1 col
if COLS < 4:
	COLS = 4

# UI
CELL_W = 20
CELL_H = 20
HGAP = 0
VGAP = 0
BORDER = 10
WINDOW_BG = "#0e1220"  # dark backdrop
OFF_BG = "#0b1a3b"     # dark blue (off)
ON_BG = "#ffffff"      # white (on)
TEXT_COLOR = "#ffffff"

PLAY_CHAR = "▶"
PAUSE_CHAR = "⏸"
STEP_INTERVAL_MS = 500

Coord = Tuple[int, int]


def _control_spans(cols: int) -> tuple[list[int], list[int]]:
	"""Return (spans, starts) for 4 controls that split cols as evenly as possible.
	spans: list of 4 integers summing to cols; starts: leftmost x index for each span.
	"""
	base = cols // 4
	rem = cols % 4
	spans = [base + (1 if i < rem else 0) for i in range(4)]
	starts: list[int] = []
	acc = 0
	for s in spans:
		starts.append(acc)
		acc += s
	return spans, starts


def build_layout() -> str:
	# Top grid: no-merge buttons (each cell is independent)
	top_row = ",".join(["`"] * COLS)
	top = "\n".join([top_row for _ in range(ROWS)])
	# Bottom control row: four merged buttons spanning across COLS
	spans, _starts = _control_spans(COLS)
	labels = [PLAY_CHAR, "Clear", "Random", "Invert"]
	control_tokens: list[str] = []
	for label, span in zip(labels, spans):
		control_tokens.extend([label] * span)
	control = ",".join(control_tokens)
	return "\n".join([top, control])


def in_bounds(x: int, y: int) -> bool:
	return 0 <= x < COLS and 0 <= y < ROWS


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
		default_bg_color=OFF_BG,
		default_text_color=TEXT_COLOR,
		window_color=WINDOW_BG,
		resizable=True,
	)

	# Board: 0=off, 1=on
	board: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
	playing = {"value": False}
	after_id = {"id": None}

	def set_cell(x: int, y: int, val: int) -> None:
		board[y][x] = 1 if val else 0
		el = pad[x, y]  # type: ignore[index]
		el.background_color = ON_BG if board[y][x] else OFF_BG
		el.text = ""

	def toggle_cell(_el, x: int, y: int) -> None:
		if not in_bounds(x, y):
			return
		set_cell(x, y, 0 if board[y][x] else 1)

	def update_grid() -> None:
		for y in range(ROWS):
			for x in range(COLS):
				el = pad[x, y]  # type: ignore[index]
				el.background_color = ON_BG if board[y][x] else OFF_BG
				el.text = ""

	def count_neighbors(x: int, y: int) -> int:
		cnt = 0
		for dy in (-1, 0, 1):
			for dx in (-1, 0, 1):
				if dx == 0 and dy == 0:
					continue
				nx, ny = x + dx, y + dy
				if in_bounds(nx, ny) and board[ny][nx]:
					cnt += 1
		return cnt

	def step() -> None:
		nxt = [[0 for _ in range(COLS)] for _ in range(ROWS)]
		for y in range(ROWS):
			for x in range(COLS):
				n = count_neighbors(x, y)
				if board[y][x] == 1:
					nxt[y][x] = 1 if (n == 2 or n == 3) else 0
				else:
					nxt[y][x] = 1 if n == 3 else 0
		# apply differences
		for y in range(ROWS):
			for x in range(COLS):
				if nxt[y][x] != board[y][x]:
					set_cell(x, y, nxt[y][x])
		if playing["value"]:
			after_id["id"] = pad.root.after(STEP_INTERVAL_MS, step)
		else:
			after_id["id"] = None

	def start() -> None:
		if playing["value"]:
			return
		playing["value"] = True
		play_btn = pad[0, ROWS]  # left-most control (merged across 8 cols)
		play_btn.text = PAUSE_CHAR
		after_id["id"] = pad.root.after(STEP_INTERVAL_MS, step)

	def pause() -> None:
		if not playing["value"]:
			return
		playing["value"] = False
		play_btn = pad[0, ROWS]
		play_btn.text = PLAY_CHAR
		if after_id["id"] is not None:
			try:
				pad.root.after_cancel(after_id["id"])  # type: ignore[arg-type]
			except Exception:
				pass
			after_id["id"] = None

	def on_play_pause(_el, _x, _y):
		if playing["value"]:
			pause()
		else:
			start()

	def on_clear(_el, _x, _y):
		# Set all cells to off
		for y in range(ROWS):
			for x in range(COLS):
				board[y][x] = 0
		update_grid()

	def on_random(_el, _x, _y):
		# Randomize board
		for y in range(ROWS):
			for x in range(COLS):
				board[y][x] = 1 if (hash((x, y, id(board))) ^ (x * 1315423911 + y * 2654435761)) & 1 else 0
		update_grid()

	def on_invert(_el, _x, _y):
		# Invert all cells
		for y in range(ROWS):
			for x in range(COLS):
				board[y][x] = 0 if board[y][x] else 1
		update_grid()

	# Wire grid cell toggles
	for y in range(ROWS):
		for x in range(COLS):
			pad[x, y].on_click = toggle_cell  # type: ignore[index]

	# Wire control buttons using dynamic spans across COLS
	_spans, starts = _control_spans(COLS)
	play_x, clear_x, random_x, invert_x = starts
	pad[play_x, ROWS].on_click = on_play_pause  # type: ignore[index]
	pad[play_x, ROWS].text = PLAY_CHAR
	pad[clear_x, ROWS].on_click = on_clear  # type: ignore[index]
	pad[clear_x, ROWS].text = "Clear"
	pad[random_x, ROWS].on_click = on_random  # type: ignore[index]
	pad[random_x, ROWS].text = "Random"
	pad[invert_x, ROWS].on_click = on_invert  # type: ignore[index]
	pad[invert_x, ROWS].text = "Invert"

	# Initialize visuals
	update_grid()
	pad.run()


if __name__ == "__main__":
	main()

