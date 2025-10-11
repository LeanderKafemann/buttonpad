# Introducing ButtonPad: Rapid GUI Prototyping with a Simple Grid

TODO - SCREENSHOT

ButtonPad is a tiny Python library for throwing together GUI apps in minutes. You describe your interface as a compact multi‑line, CSV‑style string and attach Python functions as callbacks. No widget subclassing, no designer files, no sprawling boilerplate—just a layout string and code.

It targets two audiences:
- Beginners: Learn GUI programming without wrestling with verbose frameworks.
- Experienced developers: Crank out interactive prototypes, internal tools, game ideas, or teaching demos fast.

Everything runs on the Python standard library’s Tkinter (so no extra dependency needed for core usage). On macOS it can optionally use `tkmacosx` to give buttons true background colors. A growing suite of demo mini‑apps and games ships with the project and is launchable from a built‑in launcher.

## Highlights

- CSV-like layout string (mergable cells form bigger widgets automatically)
- Buttons, labels, text boxes, and images (IMG_ tokens) today
- One-line window creation; per-row/column sizing, gaps, margins, resizable windows
- Automatic merging of adjacent identical tokens into spanning widgets
- Backtick prefix (`` ` ``) to opt a single cell out of merging
- Per-widget callbacks: click, hover enter, hover exit
- Tooltips (just set `element.tooltip = "Help text"`)
- Global pre/post click hooks for instrumentation
- Keyboard activation: global `map_key()` and per-button/label `.hotkey` property
- Optional status bar (assign `pad.status_bar`)
- Optional nested menubar definition with automatic accelerator binding
- Image widget (token prefix `IMG_`) with automatic file lookup + optional Pillow scaling
- Re-exported dialog helpers: `alert`, `confirm`, `prompt`, `password`
- Pure Python; no code generation phase or hidden threads

TODO - SCREENSHOT (Launcher UI)

## Running the Built‑In Launcher

Once installed or cloned, run:

```bash
python -m buttonpad
```

You’ll see a launcher listing all included example programs. Click one to run it in the same process.

### Included Example Programs & Demos

These showcase different mechanics, layouts, and ButtonPad features:

- Calculator – Basic grid of buttons performing arithmetic.
- TicTacToe / TicTacToeVsCPU – Turn-based game with simple AI in CPU version.
- ConnectFour – Classic vertical alignment game.
- Gomoku – Five-in-a-row strategy board.
- Othello / OthelloVsCPU – Disc-flipping area control with optional AI.
- LightsOut – Toggle puzzle demonstrating merged regions.
- Simon – Memory pattern game.
- MemoryPuzzle – Card matching concentration game.
- SlidePuzzle – 15-puzzle style sliding tile demo.
- PegSolitaire – Jump-based board reduction puzzle.
- SameGame – Group elimination color puzzle.
- FloodIt – Region flooding color puzzle.
- Conway’sGameOfLife – Cellular automaton simulation.
- EightQueens – Chess queens placement solver with a checkerboard layout.
- FishTank – Animated style demo.
- PixelEditor – Simple pixel painting grid using buttons.
- Stopwatch – Timing utility with start/stop/reset.
- Magic8Ball – Random fortune response demo.
- EmojiCopyPad – Click to copy emojis (labels & tooltips example).
- TwentyFortyEight – The 2048 sliding tile game.
- Simon – Pattern memory reproduction (sound optional).
- DodgeRRace (if present) – Movement/keyboard control demo.
- DemoPhoneKeypad / DemoPhoneKeypad2 – Phone keypad showcase variants.
- DemoEnterExit – Hover enter/exit plus tooltip demonstration.
- KeyboardMove – Shows mapping arrow keys or hotkeys to actions.

(Names may evolve; open the launcher to see current list.)

TODO - SCREENSHOT (Example game running)

## The Core Idea: Layout as Data

You describe the UI using a multi-line string. Rows are lines. Columns are comma-separated values. Identical adjacent cells (horizontally and vertically) merge into a single widget.

Example layout:

```
Play,Play,Play
"Status",[Enter name]
`Play,Play,`Play
```

Meaning:
- First row becomes one large merged button spanning columns 0–2 (three identical tokens).
- Second row: a label (quoted) and a text box (square brackets).
- Third row: three independent buttons (backticks prevent merging on left and right).

### Token Types

- Button: any unquoted token (`A`, `OK`, `Start`)
- Label: text in single or double quotes (`"Score"` or `'Ready'`)
- Text Box: text inside square brackets (`[Name]`)
- Image: token starting with `IMG_` (e.g. `IMG_logo.png`) – loads that file if found
- Empty token: `, ,` (blank between commas) gives an empty button
- No-merge: prefix with backtick (`` `X``) to force a single-cell widget

## Quick Start: Build a Tiny App

```python
import buttonpad

layout = """7,8,9\n4,5,6\n1,2,3\n0,=,C"""

pad = buttonpad.ButtonPad(
    layout,
    cell_width=70,
    cell_height=70,
    h_gap=8,
    v_gap=8,
    title="Mini Pad",
)

# Add a click handler to print the button pressed
for y in range(4):
    for x in range(3):
        try:
            el = pad[x, y]
            el.on_click = lambda e, xx=x, yy=y: print(e.text)
        except Exception:
            pass

pad.run()
```

TODO - SCREENSHOT (Mini pad app)

## Images (IMG_ Tokens)

If a token starts with `IMG_`, the remainder is treated as a filename. ButtonPad will try to load it from the current working directory, then relative to the module. Example:

```
IMG_cat.png,IMG_cat.png
IMG_cat.png,IMG_cat.png
```

All four cells merge into one image widget if the filenames match exactly.

- With Pillow installed (`pip install Pillow`), images can scale down (and proportionally scale up when stretch=False) to fit the cell region.
- Without Pillow, the library falls back to `tk.PhotoImage` (limited formats, no resizing). A one-time warning is issued.

You can later assign an image path or a Pillow Image object: `pad[0,0].image = "logo.png"`.

## Status Bar

Assign `pad.status_bar = "Ready"` to create/update a bottom status bar. Set it to `None` to remove it. Customize colors via:

```python
pad.status_bar_background_color = "#222222"
pad.status_bar_text_color = "white"
```

## Menus

Define nested dictionaries:

```python
pad.menu = {
    "File": {
        "Quit": (pad.quit, "Ctrl+Q"),
    },
    "Help": {
        "About": lambda: print("ButtonPad Rocks"),
    },
}
```

Accelerators (like `Ctrl+Q`) are auto-bound. On macOS, `Command` can be used. ButtonPad also binds a Control variant for convenience when `Command` is specified on non-mac platforms.

## Keyboard Interaction

Two mechanisms:
1. Global mapping: `pad.map_key("space", 0, 0)` maps Spacebar to cell (0,0).
2. Hotkeys on buttons/labels: `element.hotkey = ("a", "b", "Escape")` sets multiple independent triggers.

Hotkeys and mapped keys fire the same `on_click` callback path (including pre/post hooks and tooltip hiding).

## Tooltips & Hover Events

Set `element.tooltip = "Reset the timer"` to enable a tooltip after a short hover delay. Also available:
- `element.on_enter` — called when mouse enters
- `element.on_exit` — called when mouse leaves

Tooltips hide automatically on click or exit.

## Global Click Hooks

Optional functions:

```python
pad.on_pre_click = lambda e: print("About to click", e.text)
pad.on_post_click = lambda e: print("Clicked", e.text)
```

They run around every element click.

## Accessing Elements Programmatically

Use Cartesian indexing: `pad[x, y]` (column, row). After building the pad you can change properties:

```python
btn = pad[0,0]
btn.text = "Go"
btn.background_color = "#4488ff"
btn.text_color = "white"
btn.tooltip = "Start the process"
btn.on_click = lambda e, x, y: print("GO!")
```

## API Overview

### Constructor

```python
ButtonPad(
    layout: str,
    cell_width: int | Sequence[int] = 60,
    cell_height: int | Sequence[int] = 60,
    h_gap: int = 0,
    v_gap: int = 0,
    window_color: str = '#f0f0f0',
    default_bg_color: str = '#f0f0f0',
    default_text_color: str = 'black',
    title: str = 'ButtonPad App',
    resizable: bool = True,
    border: int = 0,
    status_bar: str | None = None,
    menu: dict | None = None,
)
```

### Methods & Attributes

- `run()` — start event loop
- `quit()` — destroy window (safe to call multiple times)
- `update(new_layout)` — rebuild with a fresh layout string
- `map_key(keysym, x, y)` — map a key to a cell
- `status_bar` (get/set) — string or None
- `menu` (get/set) — nested dict for menubar
- `on_pre_click` / `on_post_click` — global hooks
- Indexing: `pad[x, y]` -> element wrapper

### Element Wrapper (BPButton, BPLabel, BPTextBox, BPImage)

Common:
- `text`
- `background_color`
- `text_color`
- `font_name`, `font_size`
- `tooltip`
- `on_click`, `on_enter`, `on_exit`
- `widget` (raw Tk widget)

Extras:
- `BPLabel.anchor` (e.g., 'w', 'center')
- `BPButton.hotkey`, `BPLabel.hotkey`
- `BPTextBox.text` reflects full content
- `BPImage.image` (path or Pillow Image), `BPImage.stretch` (True = fill frame; False = proportional fit)

## Design Philosophy

- Text-first. Layout describes intent in a plain string—easy to diff, version, and teach.
- Merge-by-sameness beats manual row/colspan.
- Crash avoidance: internal errors are trapped; GUI keeps running (useful for teaching/beginners).
- Minimal surprise: widgets expose intuitive properties; underlying Tk widget still accessible.
- Fast feedback: edit layout string -> instantly different UI.

## Installation

If published to PyPI (placeholder):

```bash
pip install buttonpad
```

Or clone and run in-place. For macOS colored buttons:

```bash
pip install tkmacosx
```

For image scaling:

```bash
pip install Pillow
```

## Roadmap (Aspirational)

- More widget types (dropdowns, sliders)
- Built-in theme support
- Layout validation & linter helpers
- Image caching / async loading
- Optional sound hooks in examples

## Contributing

Open issues or PRs with concise descriptions. Add or improve an example game to showcase a feature.

## Final Notes

ButtonPad aims to shrink the distance between an idea and a clickable GUI. Whether you’re teaching loops and conditionals or mocking a tool for colleagues, it keeps friction low.

TODO - SCREENSHOT (Collage of several example apps)

Happy prototyping!
