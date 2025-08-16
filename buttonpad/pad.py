
from __future__ import annotations
import tkinter as tk
from tkinter import font as tkfont
from dataclasses import dataclass
from typing import Callable, List, Tuple, Dict, Optional

LabelMatrix = List[List[str]]
Coord = Tuple[int, int]

@dataclass
class Button:
    caption: str
    widget: tk.Button
    on_click: Optional[Callable[["Button"], None]] = None
    on_enter: Optional[Callable[["Button"], None]] = None
    on_exit: Optional[Callable[["Button"], None]] = None

    def __post_init__(self):
        self.widget.configure(command=self._handle_click)
        self.widget.bind("<Enter>", self._handle_enter)
        self.widget.bind("<Leave>", self._handle_exit)

    @property
    def bg(self): return self.widget.cget("bg")
    @bg.setter
    def bg(self, val): self.widget.configure(bg=val, activebackground=val)

    @property
    def fg(self): return self.widget.cget("fg")
    @fg.setter
    def fg(self, val): self.widget.configure(fg=val, activeforeground=val)

    @property
    def text(self): return self.widget.cget("text")
    @text.setter
    def text(self, val): self.caption = val; self.widget.configure(text=val)

    def _handle_click(self): self.on_click and self.on_click(self)
    def _handle_enter(self, _): self.on_enter and self.on_enter(self)
    def _handle_exit(self, _): self.on_exit and self.on_exit(self)

class TextField:
    def undo(self): self.widget.edit_undo()
    def redo(self): self.widget.edit_redo()
    def __init__(self, label: str, widget: tk.Text, frame: tk.Frame):
        self.label = label
        self.widget = widget
        self.frame = frame

    @property
    def text(self): return self.widget.get("1.0", "end-1c")
    @text.setter
    def text(self, val): self.widget.delete("1.0", "end"); self.widget.insert("1.0", val)

    @property
    def bg(self): return self.widget.cget("bg")
    @bg.setter
    def bg(self, val): self.widget.configure(bg=val)

    @property
    def fg(self): return self.widget.cget("fg")
    @fg.setter
    def fg(self, val): self.widget.configure(fg=val)

    @property
    def font(self): return self.widget.cget("font")
    @font.setter
    def font(self, val): self.widget.configure(font=val)

    @property
    def wrap(self): return self.widget.cget("wrap")
    @wrap.setter
    def wrap(self, val): self.widget.configure(wrap=val)

def _parse_labels(label_text: Optional[str]) -> LabelMatrix:
    default = """1,2,3\n4,5,6\n7,8,9\n*,0,#"""
    label_text = label_text or default
    lines = label_text.strip().splitlines()
    rows = [[cell.strip() for cell in line.split(",")] for line in lines]
    width = len(rows[0])
    for r in rows:
        if len(r) != width:
            raise ValueError("All rows must have the same number of columns.")
    return rows

class ButtonPad:
    def __init__(
        self,
        labels: Optional[str] = None,
        *,
        button_width_px: int = 100,
        button_height_px: int = 60,
        hgap_px: int = 8,
        vgap_px: int = 8,
        button_bg: str = "#eeeeee",
        button_fg: str = "#000000",
        field_bg: str = "#ffffff",
        field_fg: str = "#000000",
        window_bg: str = "#f0f0f0",
        title: str = "ButtonPad",
        border_px: int = 8,
        resizable: bool = True,
    ):
        self.labels_matrix = _parse_labels(labels)
        self.rows, self.cols = len(self.labels_matrix), len(self.labels_matrix[0])
        self.button_width_px = button_width_px
        self.button_height_px = button_height_px
        self.hgap_px = hgap_px
        self.vgap_px = vgap_px
        self.button_bg = button_bg
        self.button_fg = button_fg
        self.field_bg = field_bg
        self.field_fg = field_fg
        self.window_bg = window_bg
        self.title = title
        self.border_px = border_px
        self.resizable = resizable

        self.root = tk.Tk()
        self.root.title(self.title)
        self.root.configure(bg=self.window_bg)
        self.root.resizable(self.resizable, self.resizable)
        self.grid_frame = tk.Frame(self.root, bg=self.window_bg)
        self.grid_frame.grid(row=0, column=0, sticky="nsew", padx=self.border_px, pady=self.border_px)
        self.root.grid_rowconfigure(0, weight=1 if self.resizable else 0)
        self.root.grid_columnconfigure(0, weight=1 if self.resizable else 0)

        self.buttons: List[Button] = []
        self.fields: List[TextField] = []
        self._owner_for_cell: Dict[Coord, object] = {}

        spans = self._compute_spans(self.labels_matrix)
        self._build_grid(spans)

        total_w = self.cols * self.button_width_px + (self.cols - 1) * self.hgap_px + 2 * self.border_px
        total_h = self.rows * self.button_height_px + (self.rows - 1) * self.vgap_px + 2 * self.border_px
        self.root.geometry(f"{total_w}x{total_h}")

    def run(self): self.root.mainloop()
    def __getitem__(self, rc: Coord): return self._owner_for_cell[rc]

    def _compute_spans(self, labels: LabelMatrix):
        visited = [[False] * self.cols for _ in range(self.rows)]
        spans = []
        for r in range(self.rows):
            for c in range(self.cols):
                if visited[r][c]: continue
                label = labels[r][c]
                w = 1
                while c + w < self.cols and labels[r][c + w] == label: w += 1
                h = 1
                while r + h < self.rows and all(labels[r + h][cc] == label and not visited[r + h][cc] for cc in range(c, c + w)): h += 1
                for rr in range(r, r + h):
                    for cc in range(c, c + w):
                        visited[rr][cc] = True
                spans.append((r, c, h, w, label))
        return spans

    def _build_grid(self, spans):
        for i in range(2 * self.rows - 1):
            size = self.button_height_px if i % 2 == 0 else self.vgap_px
            self.grid_frame.grid_rowconfigure(i, weight=1 if self.resizable and i % 2 == 0 else 0, minsize=size)
        for i in range(2 * self.cols - 1):
            size = self.button_width_px if i % 2 == 0 else self.hgap_px
            self.grid_frame.grid_columnconfigure(i, weight=1 if self.resizable and i % 2 == 0 else 0, minsize=size)

        for r, c, rs, cs, label in spans:
            pr, pc = 2 * r, 2 * c
            prs, pcs = 2 * rs - 1, 2 * cs - 1

            if label.startswith("_"):
                outer = tk.Frame(self.grid_frame)
                txt = tk.Text(
                    outer,
                    wrap="word",
                    bg=self.field_bg,
                    fg=self.field_fg,
                    height=1,
                    undo=True,
                    autoseparators=True,
                    insertwidth=2,
                    insertbackground=self.field_fg
                )

                vbar = tk.Scrollbar(outer, orient="vertical", command=txt.yview)
                hbar = tk.Scrollbar(outer, orient="horizontal", command=txt.xview)
                txt.configure(yscrollcommand=lambda *a: self._scroll_vis(vbar, a),
                              xscrollcommand=lambda *a: self._scroll_vis(hbar, a))
                txt.grid(row=0, column=0, sticky="nsew")
                vbar.grid(row=0, column=1, sticky="ns")
                hbar.grid(row=1, column=0, sticky="ew")
                outer.grid_rowconfigure(0, weight=1)
                outer.grid_columnconfigure(0, weight=1)
                outer.grid(row=pr, column=pc, rowspan=prs, columnspan=pcs, sticky="nsew")

                field = TextField(label=label[1:], widget=txt, frame=outer)
                self.fields.append(field)
                for rr in range(r, r + rs):
                    for cc in range(c, c + cs):
                        self._owner_for_cell[(rr, cc)] = field
            else:
                b = tk.Button(self.grid_frame, text=label, bg=self.button_bg, fg=self.button_fg,
                              activebackground=self.button_bg, activeforeground=self.button_fg)
                b.grid(row=pr, column=pc, rowspan=prs, columnspan=pcs, sticky="nsew")
                btn = Button(caption=label, widget=b)
                self.buttons.append(btn)
                for rr in range(r, r + rs):
                    for cc in range(c, c + cs):
                        self._owner_for_cell[(rr, cc)] = btn

    def _scroll_vis(self, scrollbar, args):
        first, last = float(args[0]), float(args[1])
        if first <= 0.0 and last >= 1.0:
            scrollbar.grid_remove()
        else:
            scrollbar.grid()

