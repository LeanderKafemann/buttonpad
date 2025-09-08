# ButtonPad

ButtonPad lets you declare a grid of buttons, labels, and text boxes using a compact, CSV-like layout string and control it with simple Python callbacks. It’s built on the Tkinter standard library and works on Windows, macOS, and Linux. On macOS, it can optionally use tkmacosx for better button color support.

(THIS CODE AND DOCUMENTATION IS STILL UNDER REVIEW AND CAN CHANGE AT ANY TIME.)

Key features:
• Pure-Python, no custom widget subclasses you must learn — just layout + callbacks
• CSV-like layout string with auto-merge of identical adjacent cells
• Per-cell click handlers plus hover enter/exit callbacks and tooltips
• Global key mapping AND per-button / per-label hotkeys (BPButton.hotkey / BPLabel.hotkey)
• Optional status bar (set/get via pad.status_bar) with color customization
• Optional menubar definition with automatic accelerator binding
• Adjustable per-column/row sizing, gaps, margin, and resizable windows
• PyMsgBox dialog boxes: `alert()`, `confirm()`, `prompt()`, `password()`


## Quick Start with the Launcher

Run `python -m buttonpad` to run the launcher program to view several demo programs and games made with Buttonpad.

## Example Code

```python
# Phone keypad example
import buttonpad

# Multi-line string defines 4 rows of 3 cells each (a 3x4 grid).
bp = buttonpad.ButtonPad(
	"""1,2,3
	4,5,6
	7,8,9
	*,0,#""",
	cell_width=70,
	cell_height=100,
	h_gap=20,
	v_gap=10,
	border=40,
	default_bg_color='#ff4444',
	default_text_color='darkblue',
	window_color='green',	
	title="Telephone Keypad Demo",
)

bp.run()
```


## Layout string reference

The grid is described by a CSV-like string: commas separate columns, newlines separate rows.

Token types:
- Button (default): any unquoted text, e.g. `A`, `Click`, `7`
- Label: text wrapped in single or double quotes, e.g. `'Hello'` or `"Ready"`
- Text box (editable): text wrapped in square brackets, e.g. `[Name]`
- No-merge: prefix a token with a backtick to prevent merging, e.g. `` `X``
- Empty token: an empty cell becomes an empty button

Merging rules:
- Adjacent identical tokens merge into one larger element (row/column spanning).
- Merging is rectangular: a block of identical tokens forms a single widget.
- Prefixing a token with a backtick ` prevents merging for that cell only.

Examples:

```
# 1x3 row, then a 3-wide merged button row, then a label+entry row
A,B,C
Play,Play,Play
"Status",[Name]

# Prevent the center from merging with neighbors
`Play,Play,`Play
```


## API

### ButtonPad

Constructor:

```python
ButtonPad(
	layout: str,
	cell_width: int | Sequence[int] = 60,
	cell_height: int | Sequence[int] = 60,
	h_gap: int = 0,
	v_gap: int = 0,
	window_color: str = "#f0f0f0",
	default_bg_color: str = "#f0f0f0",
	default_text_color: str = "black",
	title: str = "ButtonPad App",
	resizable: bool = True,
	border: int = 0,
)
```

Notes:
- `cell_width`/`cell_height` can be a single int (uniform) or a list matching the number of columns/rows.
- `h_gap`/`v_gap` set the internal spacing between cells; `border` is outer margin.
- The window is resizable by default.

Instance methods and properties:
- `run()` — start the Tkinter event loop.
- `quit()` — close the window (idempotent).
- `update(new_layout: str)` — rebuild the grid from a new layout string.
- `pad[x, y]` — index into the grid to get an element wrapper at column x, row y.
- `map_key(keysym: str, x: int, y: int)` — press a key to trigger a cell (e.g., `"1"`, `"a"`, `"Escape"`).
- Status bar: `status_bar` (string or None) plus `status_bar_background_color`, `status_bar_text_color`.
- Menu: assign a nested dict to `menu` to build a menubar with optional accelerators.
- Global hooks: `on_pre_click(element)`, `on_post_click(element)` called around every click.

Re-exported dialogs (from pymsgbox): `alert`, `confirm`, `prompt`, `password`.


### Widgets

All wrappers expose:
- `text: str` — get/set the visible text.
- `background_color: str` — get/set background color.
- `text_color: str` — get/set text/foreground color.
- `font_name: str` and `font_size: int` — change font.
- `tooltip: Optional[str]` — small hover tooltip; set to a string to enable, `None`/`""` to disable.
- `on_click: Callable[[element, x, y], None] | None` — click handler.
- `on_enter` / `on_exit` — hover handlers with the same signature.
- `widget` — the underlying Tk widget, for advanced customization.
Specific additions:
- `BPButton.hotkey` / `BPLabel.hotkey` properties: assign a string (keysym) or tuple of strings to create independent hotkeys (case-insensitive). Reassigning replaces prior hotkeys.

Specifics:
- `BPButton` — click-focused element; created for unquoted tokens.
- `BPLabel` — static text; has `anchor` property (e.g., `"w"`, `"center"`, `"e"`) and optional `hotkey` like buttons.
- `BPTextBox` — editable single-line entry; `text` reflects its content.


## Keyboard mapping

Map keys to cells with `map_key`. Keys are Tk keysyms (case-insensitive): `"1"`, `"a"`, `"space"`, `"Return"`, `"Escape"`, etc.

```python
pad.map_key("1", 0, 0)
pad.map_key("space", 1, 0)
```


## Merging and no-merge cells

Adjacent identical tokens automatically merge into a single widget, spanning a rectangular area. To opt out for a specific cell, prefix it with a backtick to mark it as “no-merge”:

```
Play,Play,Play
`Play,Play,`Play   # left and right don't merge with the middle
```


## Platform notes

- macOS: For fully colorable buttons, install `tkmacosx`. When unavailable, ButtonPad falls back to the system `tk.Button` (colors may not update on some macOS builds). You’ll see a console message suggesting: `pip install tkmacosx`.
- Dialog helpers use `pymsgbox` and are re-exported for convenience.

