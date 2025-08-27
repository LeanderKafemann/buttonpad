"""
ButtonPad: declare tkinter button/label/entry grids from a configuration string.

Public classes:
- ButtonPad
- BPButton
- BPLabel
- BPTextBox
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union
import tkinter as tk

__all__ = ["ButtonPad", "BPButton", "BPLabel", "BPTextBox"]

# ---------- element wrappers ----------

Callback = Optional[Callable[[tk.Widget], None]]


@dataclass
class _FontSpec:
    name: str = "TkDefaultFont"
    size: int = 12


class _BaseElement:
    def __init__(self, widget: tk.Widget, text: str = ""):
        self.widget = widget
        self._font = _FontSpec()

        # Unified text state across all widget types via StringVar
        self._textvar = tk.StringVar(value=text)
        self._text = self._textvar.get()
        try:
            # Button, Label, Entry all support 'textvariable'
            self.widget.configure(textvariable=self._textvar)
        except tk.TclError:
            # If a specific widget did not support it, we silently ignore.
            pass

        try:
            self._background_color = widget.cget("bg")
        except tk.TclError:
            self._background_color = "SystemButtonFace"

        try:
            self._text_color = widget.cget("fg")
        except tk.TclError:
            self._text_color = "black"

        # Unified, opt-in callbacks (ButtonPad dispatches clicks)
        self._on_click: Callback = None
        self.on_enter: Callback = None
        self.on_exit: Callback = None

        # Hover bindings available by default
        self.widget.bind("<Enter>", lambda e: self.on_enter(self.widget) if self.on_enter else None)
        self.widget.bind("<Leave>", lambda e: self.on_exit(self.widget) if self.on_exit else None)

    # ----- text (now centralized) -----
    @property
    def text(self) -> str:
        # Always reflect the live UI value
        try:
            self._text = self._textvar.get()
        except Exception:
            pass
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        try:
            self._textvar.set(value)
        except Exception:
            pass

    # ----- colors -----
    @property
    def background_color(self) -> str:
        return self._background_color

    @background_color.setter
    def background_color(self, value: str) -> None:
        self._background_color = value
        try:
            self.widget.configure(bg=value)
        except tk.TclError:
            pass

    @property
    def text_color(self) -> str:
        return self._text_color

    @text_color.setter
    def text_color(self, value: str) -> None:
        self._text_color = value
        try:
            self.widget.configure(fg=value)
        except tk.TclError:
            pass

    # ----- font -----
    @property
    def font_name(self) -> str:
        return self._font.name

    @font_name.setter
    def font_name(self, value: str) -> None:
        self._font.name = value
        self._apply_font()

    @property
    def font_size(self) -> int:
        return self._font.size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font.size = int(value)
        self._apply_font()

    def _apply_font(self) -> None:
        try:
            self.widget.configure(font=(self._font.name, self._font.size))
        except tk.TclError:
            pass

    # ----- unified click handler (set by user; fired by ButtonPad) -----
    @property
    def on_click(self) -> Callback:
        return self._on_click

    @on_click.setter
    def on_click(self, func: Callback) -> None:
        self._on_click = func


class BPButton(_BaseElement):
    def __init__(self, widget: tk.Button, text: str):
        super().__init__(widget, text=text)
        # default click prints text (ButtonPad calls via dispatcher)
        self.on_click = lambda w: print(self.text)


class BPLabel(_BaseElement):
    def __init__(self, widget: tk.Label, text: str, anchor: str = "center"):
        super().__init__(widget, text=text)
        self._anchor = anchor
        widget.configure(anchor=anchor)

    @property
    def anchor(self) -> str:
        return self._anchor

    @anchor.setter
    def anchor(self, value: str) -> None:
        self._anchor = value
        self.widget.configure(anchor=value)


class BPTextBox(_BaseElement):
    def __init__(self, widget: tk.Entry, text: str):
        # Entry works with textvariable too; no special handling needed.
        super().__init__(widget, text=text)


# ---------- layout & parsing ----------

@dataclass
class _Spec:
    kind: str  # "button" | "label" | "entry"
    text: str  # for entry, this is initial text
    anchor: Optional[str] = None
    no_merge: bool = False


class ButtonPad:
    """
    ButtonPad(
        configuration: str,
        cell_width: int | Sequence[int] = 60,
        cell_height: int | Sequence[int] = 60,
        horizontal_gap: int = 0,
        vertical_gap: int = 0,
        window_background_color: str = '#f0f0f0',
        default_button_background_color: str = '#f0f0f0',
        default_button_text_color: str = 'black',
        title: str = 'ButtonPad App',
        resizable: bool = True,
        border: int = 0,
    )

    - Column widths / row heights are owned by the GRID:
        * If an int is given, all columns (or rows) get that size.
        * If a sequence of ints is given, its length must match the number of
          columns (or rows) parsed from the configuration).
    - `horizontal_gap` / `vertical_gap` are internal spacing between cells.
    - `border` is the outer margin between the grid and the window edges.
    - Global hooks:
        * on_pre_click(element)
        * on_post_click(element)
      …fired around every click (mouse or keyboard).
    - Keyboard mapping:
        * map_key("1", 0, 0)  # pressing key "1" triggers cell at (x=0, y=0)
    - Indexing:
        * Access elements with Cartesian order: pad[x, y]
          (x is the column, y is the row).
    """
    def __init__(
        self,
        layout: str,
        cell_width: Union[int, Sequence[int]] = 60,
        cell_height: Union[int, Sequence[int]] = 60,
        h_gap: int = 0,
        v_gap: int = 0,
        window_color: str = '#f0f0f0',
        default_bg_color: str = '#f0f0f0',
        default_text_color: str = 'black',
        title: str = 'ButtonPad App',
        resizable: bool = True,
        border: int = 0,
    ):
        self._original_configuration = layout

        self._cell_width_input = cell_width
        self._cell_height_input = cell_height
        self.h_gap = int(h_gap)
        self.v_gap = int(v_gap)
        self.window_bg = window_color
        self.default_background_color = default_bg_color
        self.default_text_color = default_text_color
        self.border = int(border)

        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg=self.window_bg)
        self.root.resizable(resizable, resizable)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Outer container; border controls padding to window edges
        self._container = tk.Frame(self.root, bg=self.window_bg)
        self._container.pack(padx=self.border, pady=self.border, fill="both", expand=True)

        # storage: now keyed by (x, y) == (col, row)
        self._cell_to_element: Dict[Tuple[int, int], Union[BPButton, BPLabel, BPTextBox]] = {}
        self._widgets: List[tk.Widget] = []
        self._destroyed = False

        # global click hooks (user sets these)
        self.on_pre_click: Optional[Callable[[Union[BPButton, BPLabel, BPTextBox]], None]] = None
        self.on_post_click: Optional[Callable[[Union[BPButton, BPLabel, BPTextBox]], None]] = None

        # keyboard mapping: keysym(lowercased) -> (x, y)
        self._keymap: Dict[str, Tuple[int, int]] = {}
        # Bind globally so focus doesn't matter; handle both forms for robustness
        self.root.bind_all("<Key>", self._on_key)
        self.root.bind_all("<KeyPress>", self._on_key)

        # Build initial grid
        self._build_from_config(layout)

    # ----- public API -----
    def run(self) -> None:
        self.root.mainloop()

    def quit(self) -> None:
        """Quit the application and destroy the window (idempotent)."""
        if self._destroyed:
            return
        try:
            self.root.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass
        self._destroyed = True

    def update(self, new_configuration: str) -> None:
        """Rebuild the layout with a new configuration string."""
        self._original_configuration = new_configuration
        # destroy old widgets except the container/root
        for w in self._widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._widgets.clear()
        self._cell_to_element.clear()

        self._build_from_config(new_configuration)

    # Public accessor uses Cartesian order: [x, y]
    def __getitem__(self, key: Tuple[int, int]) -> Union[BPButton, BPLabel, BPTextBox]:
        return self._cell_to_element[tuple(key)]

    def map_key(self, key: str, x: int, y: int) -> None:
        """
        Map a keyboard key to trigger the element at (x, y).
        `key` should be a Tk keysym (e.g., "1", "a", "Escape", "space", "Return").
        """
        if not isinstance(key, str) or not key:
            raise ValueError("key must be a non-empty string (Tk keysym).")
        self._keymap[key.lower()] = (int(x), int(y))

    # ----- internals -----
    def _on_key(self, event) -> None:
        # Some Tk builds omit keysym for synthetic events; fall back to char.
        ks = ""
        if getattr(event, "keysym", None):
            ks = event.keysym
        elif getattr(event, "char", None):
            ks = event.char
        ks = (ks or "").lower()
        if not ks:
            return
        pos = self._keymap.get(ks)  # (x, y)
        if pos is None:
            return
        element = self._cell_to_element.get(pos)  # keyed by (x, y)
        if element is not None:
            self._fire_click(element)

    def _fire_click(self, element: Union[BPButton, BPLabel, BPTextBox]) -> None:
        """Invoke pre->on_click->post sequence safely."""
        try:
            if self.on_pre_click:
                self.on_pre_click(element)
        except Exception:
            pass
        try:
            if element.on_click:
                element.on_click(element.widget)
        except Exception:
            pass
        try:
            if self.on_post_click:
                self.on_post_click(element)
        except Exception:
            pass

    def _build_from_config(self, configuration: str) -> None:
        grid_specs = self._parse_configuration(configuration)

        rows = len(grid_specs)
        cols = max((len(r) for r in grid_specs), default=0)

        # Resolve column widths / row heights from input (int or sequence)
        self.column_widths = self._resolve_sizes(self._cell_width_input, cols, "cell_width/columns")
        self.row_heights = self._resolve_sizes(self._cell_height_input, rows, "cell_height/rows")

        # Configure the grid geometry manager with per-row/col sizes
        for r in range(rows):
            self._container.rowconfigure(r, minsize=self.row_heights[r], weight=1)
        for c in range(cols):
            self._container.columnconfigure(c, minsize=self.column_widths[c], weight=1)

        # Determine merged rectangles
        assigned = [[False] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(len(grid_specs[r])):
                if assigned[r][c]:
                    continue
                spec = grid_specs[r][c]
                if spec is None:
                    continue

                if spec.no_merge:
                    self._place_widget(r, c, 1, 1, spec)
                    assigned[r][c] = True
                else:
                    r2, c2 = self._max_rectangle(grid_specs, r, c)
                    self._place_widget(r, c, r2 - r + 1, c2 - c + 1, spec)
                    for rr in range(r, r2 + 1):
                        for cc in range(c, c2 + 1):
                            assigned[rr][cc] = True

        # Ensure a deterministic focus target so Key events route consistently
        try:
            self._container.focus_set()
        except Exception:
            pass

    @staticmethod
    def _resolve_sizes(val: Union[int, Sequence[int]], n: int, what: str) -> List[int]:
        if n <= 0:
            return []
        # int => uniform sizes
        if isinstance(val, int):
            return [int(val)] * n
        # sequence => must match length n
        try:
            seq = list(val)  # type: ignore[arg-type]
        except Exception as e:
            raise TypeError(f"{what} must be int or sequence of ints") from e
        if len(seq) != n:
            raise ValueError(f"Length of {what} sequence must match {n}; got {len(seq)}")
        sizes: List[int] = []
        for x in seq:
            if not isinstance(x, int):
                raise TypeError(f"{what} sequence must contain ints; got {type(x).__name__}")
            sizes.append(int(x))
        return sizes

    def _max_rectangle(self, grid: List[List[Optional[_Spec]]], r: int, c: int) -> Tuple[int, int]:
        rows = len(grid)
        base = grid[r][c]
        if base is None:
            return (r, c)

        # grow rightwards while same spec and within row length
        max_c = c
        while True:
            nc = max_c + 1
            if nc >= len(grid[r]):
                break
            cell = grid[r][nc]
            if not self._merge_compatible(base, cell):
                break
            max_c = nc

        # grow downward ensuring each new row has the whole horizontal run identical
        max_r = r
        while True:
            nr = max_r + 1
            if nr >= rows:
                break
            if len(grid[nr]) <= max_c:
                break
            row_ok = True
            for cc in range(c, max_c + 1):
                if not self._merge_compatible(base, grid[nr][cc]):
                    row_ok = False
                    break
            if not row_ok:
                break
            max_r = nr

        return (max_r, max_c)

    @staticmethod
    def _merge_compatible(a: Optional[_Spec], b: Optional[_Spec]) -> bool:
        if a is None or b is None:
            return False
        if a.no_merge or b.no_merge:
            return False
        return (a.kind == b.kind) and (a.text == b.text) and (a.anchor == b.anchor)

    def _place_widget(self, r: int, c: int, rowspan: int, colspan: int, spec: _Spec) -> None:
        # Compute fixed pixel size of the merged cell from per-row/col sizes
        width = sum(self.column_widths[c: c + colspan])
        height = sum(self.row_heights[r: r + rowspan])

        # Each cell/merged region gets a frame; gaps apply here
        frame = tk.Frame(
            self._container,
            width=width,
            height=height,
            bg=self.window_bg,
            highlightthickness=0,
            bd=0,
        )
        frame.grid(
            row=r,
            column=c,
            rowspan=rowspan,
            columnspan=colspan,
            padx=self.h_gap // 2,
            pady=self.v_gap // 2,
            sticky="nsew",
        )
        frame.grid_propagate(False)

        # Create the actual widget and make it fill the frame (no internal margins)
        if spec.kind == "button":
            w = tk.Button(
                frame,
                text=spec.text,
                bg=self.default_background_color,
                fg=self.default_text_color,
                relief="raised",
                padx=0,
                pady=0,
                highlightthickness=0,
            )
            w.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            element = BPButton(w, text=spec.text)
            # Fire ONCE on release via ButtonPad dispatcher
            w.configure(command=lambda e=element: self._fire_click(e))

        elif spec.kind == "label":
            w = tk.Label(
                frame,
                text=spec.text,
                bg=self.window_bg,
                fg="black",
                anchor=spec.anchor or "center",
                padx=0,
                pady=0,
                highlightthickness=0,
            )
            w.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            element = BPLabel(w, text=spec.text, anchor=spec.anchor or "center")
            # Fire ONCE on release via ButtonPad dispatcher
            w.bind("<ButtonRelease-1>", lambda evt, e=element: self._fire_click(e))

        elif spec.kind == "entry":
            w = tk.Entry(frame, relief="sunken", highlightthickness=0)
            w.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            element = BPTextBox(w, text=spec.text)
            # Fire ONCE on release via ButtonPad dispatcher (optional for entries)
            w.bind("<ButtonRelease-1>", lambda evt, e=element: self._fire_click(e))

        else:
            raise ValueError(f"Unknown spec kind: {spec.kind}")

        # Map every cell in this rectangle to the created element
        # NOTE: storage uses (x, y) == (column, row)
        for rr in range(r, r + rowspan):
            for cc in range(c, c + colspan):
                self._cell_to_element[(cc, rr)] = element

        # keep references for later destruction
        self._widgets.append(frame)
        self._widgets.append(element.widget)

    # ----- config parsing -----
    def _parse_configuration(self, configuration: str) -> List[List[Optional[_Spec]]]:
        rows: List[List[Optional[_Spec]]] = []
        for rline in configuration.strip("\n").splitlines():
            raw_items = rline.split(",")
            row: List[Optional[_Spec]] = []
            for token in raw_items:
                tok = token.strip()
                if tok == "":
                    # treat as an empty button to preserve a cell
                    row.append(_Spec(kind="button", text="", no_merge=False))
                    continue

                no_merge = tok.startswith("`")
                if no_merge:
                    tok = tok[1:].lstrip()

                # label?
                if (len(tok) >= 2) and ((tok[0] == tok[-1]) and tok[0] in ("'", '"')):
                    text = tok[1:-1]
                    row.append(_Spec(kind="label", text=text, anchor="center", no_merge=no_merge))
                    continue

                # text box?
                if tok.startswith("[") and tok.endswith("]"):
                    text = tok[1:-1]
                    row.append(_Spec(kind="entry", text=text, no_merge=no_merge))
                    continue

                # plain button
                row.append(_Spec(kind="button", text=tok, no_merge=no_merge))
            rows.append(row)
        return rows
