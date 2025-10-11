Usage
=====

Quickstart
----------

Create a simple ButtonPad layout and run it:

.. code-block:: py

    from ButtonPad import ButtonPad

    layout = """
    1,2,3
    4,5,6
    7,8,9
    """

    pad = ButtonPad(layout, cell_width=80, cell_height=60, title='Calculator')
    pad.run()

Examples
--------

See the `examples/` directory in the repository for many small programs using ButtonPad (tic-tac-toe, calculator, games, and more).

Image frames
------------

Use tokens prefixed with ``IMG_`` to create image frames. The image path can be absolute or reference a file in the current working directory. If Pillow is installed, ButtonPad will scale images for you; otherwise it will attempt to use ``tk.PhotoImage`` for supported formats.

Anchor/alignment
----------------

- ``BPLabel`` supports the usual Tk anchor values.
- ``BPButton`` uses anchor to control label placement inside the button.
- ``BPTextBox`` only accepts horizontal anchors: ``'w'``, ``'center'``, or ``'e'``.
Layout syntax
-------------

ButtonPad layouts are defined as a simple CSV-like multiline string. Each line is a row, and commas separate cells. Tokens determine the cell type:

- Plain text (unquoted) creates a button. Example: ``OK`` or ``1``.
- Quoted strings (single or double quotes) become labels and are not clickable. Example: ``'Score'`` or ``"Time"``.
- Text boxes use square brackets: ``[initial text]``. These create a multi-line ``tk.Text`` widget.
- Image frames use a token starting with ``IMG_`` followed by a filename: ``IMG_cat.png``. See images below.

Empty tokens (two commas with nothing between) create an empty button cell. Prefix a token with a backtick ```\``` to prevent automatic merging of adjacent identical tokens.

Merging cells
-------------

Adjacent identical tokens are automatically merged into a larger cell. For example:

.. code-block:: py

    A,A,B
    A,A,B

produces a 2x2 merged region for token ``A`` and two 1x2 cells for ``B``. If you want to prevent merging, prefix the token with ```` ` ```` (backtick).

Images (IMG_ tokens)
--------------------

Image tokens take the form ``IMG_<filename>`` where ``<filename>`` can be an absolute path, a path containing ``~`` (expanded to the user home directory), or a relative path (resolved against the current working directory).

If Pillow is installed, ButtonPad will use it to load and scale images with high-quality resampling. If Pillow is not installed, ButtonPad will attempt to load supported formats via ``tk.PhotoImage`` without scaling. When an image is loaded, the wrapper class ``BPImage`` exposes the ``image`` property (accepts string/Path or Pillow Image object) and ``stretch`` (bool) to control scaling behavior.

Anchors and alignment
---------------------

- ``BPLabel``: supports the usual Tk anchor values (e.g., ``'nw'``, ``'n'``, ``'ne'``, ``'w'``, ``'center'``, ``'e'``, ``'sw'``, ``'s'``, ``'se'``).
- ``BPButton``: anchor controls placement of text inside a button and accepts the same Tk anchor set.
- ``BPTextBox``: only horizontal anchors make sense; valid values are ``'w'`` (left), ``'center'``, and ``'e'`` (right).

Callbacks and events
--------------------

Each element wrapper exposes three callback properties that ButtonPad will call when events occur:

- ``on_click`` — called when the widget is clicked (receives ``(element, x, y)``).
- ``on_enter`` — mouse enter (hover) event.
- ``on_exit`` — mouse leave event.

Example:

.. code-block:: py

    pad = ButtonPad("1,2,3")
    btn = pad[0,0]
    def clicked(el, x, y):
        print('Clicked', el.text, x, y)
    btn.on_click = clicked

Hotkeys
-------

Buttons and labels support a ``hotkey`` property that maps a keysym to that element. Hotkeys are specified as a string or a tuple of strings; internally they are stored as lowercased keysyms. Example:

.. code-block:: py

    btn.hotkey = '1'        # pressing '1' will trigger this button
    btn.hotkey = ('a', 'b') # either 'a' or 'b' triggers it

Menus and status bar
--------------------

ButtonPad supports a simple menu definition via the ``menu`` property and a status bar via ``status_bar``. The ``menu`` property accepts a nested dict structure describing menus and commands. Accelerators (e.g., ``'Ctrl+Q'``) can be supplied as part of a tuple alongside a callable.

Example menu definition:

.. code-block:: py

    def say_about():
        print('About')

    menu = {
        'File': {
            'Quit': (lambda: pad.quit(), 'Ctrl+Q')
        },
        'Help': {
            'About': say_about
        }
    }
    pad.menu = menu

Status bar example:

.. code-block:: py

    pad.status_bar = 'Ready'

Advanced notes
--------------

- The package attempts to be resilient on import: optional dependencies are imported only when needed. If you plan to use autodoc on Read the Docs, you may need to add ``Pillow`` and ``tk`` (Tkinter is typically available) to the build environment or configure ``autodoc_mock_imports`` in ``conf.py`` to mock heavy optional imports.
- The package is written to tolerate missing optional libs gracefully (it will warn at runtime when Pillow is missing and fall back to limited functionality).

Further reading
---------------

See the `examples/` directory for small, self-contained programs demonstrating common patterns.

