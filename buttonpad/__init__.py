"""
TODO
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Union, Any, TYPE_CHECKING
import tkinter as tk
from pymsgbox import (
    alert as _pymsgbox_alert,
    confirm as _pymsgbox_confirm,
    prompt as _pymsgbox_prompt,
    password as _pymsgbox_password,
)
import warnings

# --- Optional macOS support for colorable buttons ---
try:
    from tkmacosx import Button as MacButton  # type: ignore
except Exception:
    MacButton = None  # fallback to tk.Button when unavailable

__all__ = [
    "ButtonPad",
    "BPButton",
    "BPLabel",
    "BPTextBox",
    # Re-exported pymsgbox helpers
    "alert",
    "confirm",
    "prompt",
    "password",
]

# ---------- element wrappers ----------

# All element callbacks receive: (element_object, x, y)
BPWidgetType = Union["BPButton", "BPLabel", "BPTextBox"]
BPCallback = Optional[Callable[["BPWidgetType", int, int], None]]

# Track the last-created Tk root so we can restore focus after dialogs
_last_root: Optional[tk.Tk] = None

def _refocus_root() -> None:
    """Attempt to bring focus back to the most recent ButtonPad window."""
    try:
        root = globals().get("_last_root")
        if root is not None and hasattr(root, "winfo_exists") and root.winfo_exists():
            try:
                root.lift()
            except Exception:
                pass
            try:
                root.focus_force()
            except Exception:
                pass
    except Exception:
        pass

def alert(text: str = "", title: str = "PyMsgBox", button: str = "OK") -> str:  # type: ignore[override]
    result = _pymsgbox_alert(text=text, title=title, button=button)
    _refocus_root()
    return result

def confirm(text: str = "", title: str = "PyMsgBox", buttons: Union[str, Sequence[str]] = ("OK", "Cancel")) -> str:  # type: ignore[override]
    result = _pymsgbox_confirm(text=text, title=title, buttons=buttons)
    _refocus_root()
    return result

def prompt(text: str = "", title: str = "PyMsgBox", default: Optional[str] = "") -> Optional[str]:  # type: ignore[override]
    result = _pymsgbox_prompt(text=text, title=title, default=default)
    _refocus_root()
    return result

def password(text: str = "", title: str = "PyMsgBox", default: Optional[str] = "", mask: str = "*") -> Optional[str]:  # type: ignore[override]
    result = _pymsgbox_password(text=text, title=title, default=default, mask=mask)
    _refocus_root()
    return result




class _BPBase:
    """
    Base wrapper for a Tk widget. Public attributes:
      - widget: the underlying tkinter widget
      - text:   live UI text (StringVar-backed when supported)
    """

    def __init__(self, widget: tk.Widget, text: str = ""):
        self.widget = widget
        self._font_name = "TkDefaultFont"
        self._font_size = 12

        # Text handling:
        # - Use textvariable only for widgets known to support it reliably (Label/Entry).
        # - For buttons (tk.Button, tkmacosx Button), set text directly to avoid macOS issues.
        self._text = text
        self._textvar = tk.StringVar(value=text)
        self._uses_textvariable = False
        if isinstance(widget, tk.Label) or isinstance(widget, tk.Entry):
            try:
                self.widget.configure(textvariable=self._textvar)
                self._uses_textvariable = True
            except tk.TclError:
                self._uses_textvariable = False
        if not self._uses_textvariable:
            try:
                self.widget.configure(text=text)
            except tk.TclError:
                pass  # some widgets simply don't have text

        try:
            self._background_color = widget.cget("bg")
        except tk.TclError:
            self._background_color = "SystemButtonFace"

        try:
            self._text_color = widget.cget("fg")
        except tk.TclError:
            self._text_color = "black"

        # Callback hooks (ButtonPad will invoke these)
        self._on_click = None
        self.on_enter = None
        self.on_exit = None

        # Filled in by ButtonPad when placed
        self._pos = (0, 0)
        # Tooltip data (managed by ButtonPad on hover)
        self._tooltip_text = None
        self._tooltip_after = None
        self._tooltip_window = None

    # ----- text (robust across tk / tkmacosx) -----
    @property
    def text(self) -> str:
        if self._uses_textvariable:
            try:
                self._text = self._textvar.get()
            except Exception:
                pass
        else:
            # If we can read the live widget text, do so
            try:
                self._text = str(self.widget.cget("text"))
            except Exception:
                pass
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        if self._uses_textvariable:
            try:
                self._textvar.set(value)
                return
            except Exception:
                pass
        # Fallback for widgets without textvariable (e.g., some tkmacosx buttons)
        try:
            self.widget.configure(text=value)
        except tk.TclError:
            pass

    # ----- tooltip -----
    @property
    def tooltip(self) -> Optional[str]:
        """Optional hover tooltip text. Set to a string to enable; None/'' to disable."""
        return self._tooltip_text

    @tooltip.setter
    def tooltip(self, value: Optional[str]) -> None:
        self._tooltip_text = value or None

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
        return self._font_name

    @font_name.setter
    def font_name(self, value: str) -> None:
        self._font_name = value
        self._apply_font()

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font_size = int(value)
        self._apply_font()

    def _apply_font(self) -> None:
        try:
            self.widget.configure(font=(self._font_name, self._font_size))
        except tk.TclError:
            pass

    # ----- unified click handler (set by user; fired by ButtonPad) -----
    @property
    def on_click(self) -> BPCallback:
        return self._on_click

    @on_click.setter
    def on_click(self, func: BPCallback) -> None:
        self._on_click = func



class BPButton(_BPBase):
    def __init__(self, widget: tk.Widget, text: str):
        super().__init__(widget, text=text)
        # default click prints text (ButtonPad calls via dispatcher)
        self.on_click = lambda el, x, y: print(self.text)


class BPLabel(_BPBase):
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


class BPTextBox(_BPBase):
    def __init__(self, widget: tk.Text, text: str):
        # Initialize base without relying on textvariable/text configure
        super().__init__(widget, text=text)
        # Ensure initial text is shown in Text widget
        try:
            widget.delete("1.0", "end")
            if text:
                widget.insert("1.0", text)
        except Exception:
            pass

    # Override text property to work with tk.Text (multiline)
    @property
    def text(self) -> str:  # type: ignore[override]
        try:
            self._text = self.widget.get("1.0", "end-1c")  # omit trailing newline
        except Exception:
            pass
        return self._text

    @text.setter  # type: ignore[override]
    def text(self, value: str) -> None:
        self._text = value or ""
        try:
            self.widget.delete("1.0", "end")
            if self._text:
                self.widget.insert("1.0", self._text)
        except Exception:
            pass


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
    - Callback signatures (user-supplied):
        * element.on_click   -> (element, x, y)
        * element.on_enter   -> (element, x, y)
        * element.on_exit    -> (element, x, y)
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
        status_bar: Optional[str] = None,
    menu: Optional[Dict[str, Any]] = None,
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
        # Remember last root for post-dialog refocus
        try:
            globals()["_last_root"] = self.root
        except Exception:
            pass

        # Optional status bar (created on-demand when status_bar is set)
        self._status_frame = None
        self._status_label = None
        self._status_text = None
        # Defaults: background inherits window background; text inherits default button text color
        self._status_bg_color = self.window_bg
        self._status_text_color = self.default_text_color

        # Menu internals
        self._menubar = None
        self._menu_def = None
        self._menu_bindings = []

        # Optional message if macOS without tkmacosx
        if sys.platform == "darwin" and MacButton is None:
            try:
                warnings.warn(
                    "[ButtonPad] tkmacosx not found; using tk.Button (colors may not update on macOS). "
                    "Install with: pip install tkmacosx",
                    RuntimeWarning,
                )
            except Exception:
                pass

        # Outer container; border controls padding to window edges
        self._container = tk.Frame(self.root, bg=self.window_bg)
        self._container.pack(padx=self.border, pady=self.border, fill="both", expand=True)

        # storage: keyed by (x, y) == (col, row)
        self._cell_to_element = {}
        self._widgets = []
        self._destroyed = False

        # global click hooks (user sets these) — receive the element wrapper
        self.on_pre_click = None
        self.on_post_click = None

        # keyboard mapping: keysym(lowercased) -> (x, y)
        self._keymap = {}
        # Bind globally so focus doesn't matter; handle both forms for robustness
        self.root.bind_all("<Key>", self._on_key)
        self.root.bind_all("<KeyPress>", self._on_key)

        # Build initial grid
        self._build_from_config(layout)

        # Initialize status bar if requested
        if status_bar is not None:
            try:
                self.status_bar = str(status_bar)
            except Exception:
                pass

        # Initialize menu if provided
        if menu:
            try:
                self.menu = menu
            except Exception:
                pass

    # ----- status bar API -----
    @property
    def status_bar(self) -> Optional[str]:
        """Get or set the text shown in a bottom status bar.

        - None (default) means no status bar is shown.
        - Setting to a string shows/updates a bottom status bar with that text.
        - Setting to None removes the status bar widget.
        """
        return self._status_text

    @status_bar.setter
    def status_bar(self, value: Optional[str]) -> None:
        # Normalize: empty string still shows an empty bar; None removes it
        if value is None:
            self._status_text = None
            # Destroy if exists
            if self._status_frame is not None:
                try:
                    self._status_frame.destroy()
                except Exception:
                    pass
            self._status_frame = None
            self._status_label = None
            return

        # Ensure frame/label exist
        self._status_text = str(value)
        if self._status_frame is None or self._status_label is None:
            try:
                frame = tk.Frame(self.root, bg=self._status_bg_color, bd=1, relief="sunken")
                # Place at bottom; allow main container to expand above it
                frame.pack(side="bottom", fill="x")
                label = tk.Label(
                    frame,
                    text=self._status_text,
                    anchor="w",
                    bg=self._status_bg_color,
                    fg=self._status_text_color,
                    padx=6,
                    pady=2,
                )
                label.pack(side="left", fill="x", expand=True)
                self._status_frame = frame
                self._status_label = label
            except Exception:
                # If creation fails, just keep the text state; no hard crash
                self._status_frame = None
                self._status_label = None
                return

        # Update text if already created
        try:
            if self._status_label is not None:
                self._status_label.configure(text=self._status_text)
                # also ensure colors are in sync
                try:
                    self._status_label.configure(bg=self._status_bg_color, fg=self._status_text_color)
                except Exception:
                    pass
            if self._status_frame is not None:
                try:
                    self._status_frame.configure(bg=self._status_bg_color)
                except Exception:
                    pass
        except Exception:
            pass

    @property
    def status_bar_background_color(self) -> str:
        """Background color for the status bar. Defaults to window_background_color."""
        return self._status_bg_color

    @status_bar_background_color.setter
    def status_bar_background_color(self, value: str) -> None:
        self._status_bg_color = str(value)
        # Update live widgets if present
        if self._status_frame is not None:
            try:
                self._status_frame.configure(bg=self._status_bg_color)
            except Exception:
                pass
        if self._status_label is not None:
            try:
                self._status_label.configure(bg=self._status_bg_color)
            except Exception:
                pass

    @property
    def status_bar_text_color(self) -> str:
        """Text color for the status bar. Defaults to default_button_text_color."""
        return self._status_text_color

    @status_bar_text_color.setter
    def status_bar_text_color(self, value: str) -> None:
        self._status_text_color = str(value)
        if self._status_label is not None:
            try:
                self._status_label.configure(fg=self._status_text_color)
            except Exception:
                pass

    # ----- menu API -----
    @property
    def menu(self) -> Optional[Dict[str, Any]]:
        """Get or set the menu definition dict.
        Structure:
          {
            "File": { "Open": func, "Quit": (func, "Ctrl+Q") },
            "Help": { "About": func },
            "Reload": func  # command directly on the menubar
          }
        A value can be:
          - callable -> command
          - (callable, accelerator_str) -> command with displayed accelerator and key binding
          - dict -> submenu (recursively parsed)
        """
        return getattr(self, "_menu_def", None)

    @menu.setter
    def menu(self, value: Optional[Dict[str, Any]]) -> None:
        # Clear existing
        self._menu_clear()
        self._menu_def = None
        if not value:
            return
        # Build new menubar
        try:
            menubar = tk.Menu(self.root)
            self._menu_build_recursive(menubar, value)
            self.root.config(menu=menubar)
            self._menubar = menubar
            self._menu_def = value
        except Exception:
            # Best-effort: leave no menu if building fails
            try:
                self.root.config(menu="")
            except Exception:
                pass
            self._menubar = None
            self._menu_def = None

    # -- menu helpers --
    def _menu_clear(self) -> None:
        # Unbind previous accelerators
        binds = getattr(self, "_menu_bindings", [])
        for seq in binds:
            try:
                self.root.unbind_all(seq)
            except Exception:
                pass
        self._menu_bindings = []
        # Remove existing menubar
        if getattr(self, "_menubar", None) is not None:
            try:
                self.root.config(menu="")
            except Exception:
                pass
            try:
                self._menubar.destroy()
            except Exception:
                pass
        self._menubar = None

    def _menu_build_recursive(self, menu_widget: tk.Menu, definition: Dict[str, Any]) -> None:
        for label, spec in definition.items():
            if isinstance(spec, dict):
                # Submenu
                submenu = tk.Menu(menu_widget, tearoff=0)
                self._menu_build_recursive(submenu, spec)
                menu_widget.add_cascade(label=label, menu=submenu)
            else:
                cmd, accel_text, bind_seq = self._coerce_menu_item(spec)
                if cmd is None:
                    # skip invalid entries silently
                    continue
                if accel_text:
                    try:
                        menu_widget.add_command(label=label, command=cmd, accelerator=accel_text)
                    except Exception:
                        menu_widget.add_command(label=label, command=cmd)
                else:
                    menu_widget.add_command(label=label, command=cmd)
                # Bind accelerator sequence
                if bind_seq:
                    self._menu_bind_accel(bind_seq, cmd)

    def _coerce_menu_item(self, spec: Any) -> Tuple[Optional[Callable[[], None]], Optional[str], Optional[str]]:
        func: Optional[Callable[[], None]] = None
        accel: Optional[str] = None
        if callable(spec):
            func = lambda f=spec: f()
        elif isinstance(spec, tuple) and len(spec) >= 1 and callable(spec[0]):
            func = lambda f=spec[0]: f()
            if len(spec) >= 2 and isinstance(spec[1], str):
                accel = spec[1]
        else:
            return (None, None, None)
        seq = self._parse_accelerator(accel) if accel else None
        return (func, accel, seq)

    def _menu_bind_accel(self, seq: str, func: Callable[[], None]) -> None:
        try:
            self.root.bind_all(seq, lambda e: func())
            self._menu_bindings.append(seq)
            # If Command on non-mac, also bind Control variant for convenience
            if "Command" in seq and sys.platform != "darwin":
                ctrl_seq = seq.replace("Command", "Control")
                self.root.bind_all(ctrl_seq, lambda e: func())
                self._menu_bindings.append(ctrl_seq)
        except Exception:
            pass

    def _parse_accelerator(self, accel: str) -> Optional[str]:
        if not accel:
            return None
        parts = [p.strip() for p in accel.replace("+", "-").split("-") if p.strip()]
        if not parts:
            return None
        mods_map = {
            "ctrl": "Control", "control": "Control",
            "cmd": "Command", "command": "Command",
            "alt": "Alt", "option": "Alt",
            "shift": "Shift",
        }
        key = parts[-1]
        mods = [mods_map.get(p.lower(), None) for p in parts[:-1]]
        mods = [m for m in mods if m]
        # Normalize key
        named = {
            "enter": "Return", "return": "Return",
            "esc": "Escape", "escape": "Escape",
            "space": "space",
            "left": "Left", "right": "Right", "up": "Up", "down": "Down",
            "tab": "Tab", "backspace": "BackSpace", "delete": "Delete",
        }
        if len(key) == 1:
            ksym = key.lower()
        else:
            ksym = named.get(key.lower(), key)
        seq = "<" + ("-".join(mods + [ksym])) + ">" if mods else f"<{ksym}>"
        return seq

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
    def __getitem__(self, key: Tuple[int, int]) -> BPWidgetType:
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

    def _fire_click(self, element: BPWidgetType) -> None:
        """Invoke pre->on_click->post sequence safely, delivering (element, x, y)."""
        x, y = element._pos  # set during placement
        # Hide tooltip upon click
        try:
            self._tooltip_hide(element)
        except Exception:
            pass
        try:
            if self.on_pre_click:
                self.on_pre_click(element)
        except Exception:
            pass
        try:
            if element.on_click:
                element.on_click(element, x, y)
        except Exception:
            pass
        try:
            if self.on_post_click:
                self.on_post_click(element)
        except Exception:
            pass

    def _fire_enter(self, element: BPWidgetType) -> None:
        x, y = element._pos
        # Schedule tooltip show if present
        try:
            self._tooltip_schedule(element)
        except Exception:
            pass
        try:
            if element.on_enter:
                element.on_enter(element, x, y)
        except Exception:
            pass

    def _fire_exit(self, element: BPWidgetType) -> None:
        x, y = element._pos
        # Hide tooltip on exit
        try:
            self._tooltip_hide(element)
        except Exception:
            pass
        try:
            if element.on_exit:
                element.on_exit(element, x, y)
        except Exception:
            pass

    # ----- tooltip helpers (no idlelib) -----
    def _tooltip_schedule(self, element: BPWidgetType) -> None:
        text = getattr(element, "_tooltip_text", None)
        if not text:
            return
        # cancel previous timer
        after_id = getattr(element, "_tooltip_after", None)
        if after_id:
            try:
                self.root.after_cancel(after_id)  # type: ignore[arg-type]
            except Exception:
                pass
        element._tooltip_after = self.root.after(350, lambda e=element: self._tooltip_show(e))

    def _tooltip_show(self, element: BPWidgetType) -> None:
        text = getattr(element, "_tooltip_text", None)
        if not text:
            return
        tw = getattr(element, "_tooltip_window", None)
        if tw is None:
            tw = tk.Toplevel(self.root)
            tw.wm_overrideredirect(True)
            try:
                tw.attributes("-topmost", True)
            except Exception:
                pass
            frame = tk.Frame(tw, bg="#333333", bd=0, highlightthickness=0)
            frame.pack(fill="both", expand=True)
            label = tk.Label(frame, text=text, bg="#333333", fg="white", padx=6, pady=3, justify="left")
            label.pack()
            element._tooltip_window = tw
        else:
            # update text
            try:
                for child in tw.winfo_children():
                    for gc in child.winfo_children():
                        if isinstance(gc, tk.Label):
                            gc.configure(text=text)
            except Exception:
                pass
        # position near mouse pointer
        try:
            x = self.root.winfo_pointerx() + 12
            y = self.root.winfo_pointery() + 16
            tw.wm_geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _tooltip_hide(self, element: BPWidgetType) -> None:
        after_id = getattr(element, "_tooltip_after", None)
        if after_id:
            try:
                self.root.after_cancel(after_id)  # type: ignore[arg-type]
            except Exception:
                pass
        element._tooltip_after = None
        tw = getattr(element, "_tooltip_window", None)
        if tw is not None:
            try:
                tw.destroy()
            except Exception:
                pass
        element._tooltip_window = None

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
            # Choose button class depending on platform and availability
            ButtonCls = MacButton if (sys.platform == "darwin" and MacButton is not None) else tk.Button

            # tkmacosx extras (optional aesthetics)
            extra_kwargs = {}
            if ButtonCls is MacButton:
                extra_kwargs.update({
                    "borderless": 1,
                    "focuscolor": "",
                })

            w = ButtonCls(
                frame,
                text=spec.text,
                bg=self.default_background_color,
                fg=self.default_text_color,
                anchor="center",
                justify="center",
                padx=0,
                pady=0,
                bd=0,
                relief="flat",
                highlightthickness=0,
                **extra_kwargs,
            )
            w.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            element: BPWidgetType = BPButton(w, text=spec.text)
            # Click via ButtonPad dispatcher
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
            # Click dispatch (optional for labels)
            w.bind("<ButtonRelease-1>", lambda evt, e=element: self._fire_click(e))

        elif spec.kind == "entry":
            w = tk.Text(
                frame,
                relief="sunken",
                highlightthickness=0,
                wrap="word",
                bd=1,
            )
            w.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
            element = BPTextBox(w, text=spec.text)
            # Click dispatch (optional for text areas)
            w.bind("<ButtonRelease-1>", lambda evt, e=element: self._fire_click(e))

        else:
            raise ValueError(f"Unknown spec kind: {spec.kind}")

        # Record this element's *top-left* position
        element._pos = (c, r)

        # Hover enter/exit handlers (bind here so we know the element & its coords)
        w.bind("<Enter>", lambda evt, e=element: self._fire_enter(e))
        w.bind("<Leave>", lambda evt, e=element: self._fire_exit(e))

        # Map every cell in this rectangle to the created element (keyed by x,y)
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
