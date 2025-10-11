# Sphinx configuration for ButtonPad documentation
import os
import sys
from datetime import datetime

# Add project root to sys.path so autodoc can import ButtonPad
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

project = 'ButtonPad'
author = 'asweigart'
copyright = f"{datetime.now().year}, {author}"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'
html_static_path = ['_static']

# Autodoc settings
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
html_show_sourcelink = True
