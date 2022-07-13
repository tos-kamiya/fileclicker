import importlib.metadata

__version__ = importlib.metadata.version("fileclicker")

from .file_finder import existing_file_iter, pathlike_iter
from .justpy_with_browser import justpy_with_browser
from .main import main
