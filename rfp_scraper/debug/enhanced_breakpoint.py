import asyncio
import os
import sys

import nest_asyncio  # pyright: ignore
from IPython.terminal.debugger import TerminalPdb
from rich import pretty, traceback
from rich.console import Console
from rich.theme import Theme

# Define a custom theme with enhanced colors
custom_theme = Theme(
    {
        "info": "bold cyan",
        "warning": "bold yellow",
        "error": "bold red",
        "var_name": "bold green",
        "var_value": "yellow",
        "code": "bold blue",
        "highlight": "reverse bold white on dark_blue",
    }
)

# Create a console with our theme
console = Console(theme=custom_theme)


class RichTerminalPdb(TerminalPdb):
    """An IPython TerminalPdb subclass with rich formatting."""

    def __init__(self, *args, **kwargs):  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
        # Initialize rich hooks before creating the terminal
        pretty.install()
        traceback.install()  # pyright: ignore[reportUnusedCallResult]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, ]

    def displayhook(self, obj):  # pyright: ignore[reportMissingParameterType]
        """Custom displayhook to use rich pretty printing"""
        if obj is not None:
            # Use rich's pretty print for objects
            console.print(obj)

    def do_pp(self, arg):  # pyright: ignore[reportMissingParameterType]
        """pp expression
        Pretty-print the value of the expression using rich.
        """
        try:
            val = self._getval(arg)
            console.print(val)
        except:  # noqa: E722
            pass


def set_trace():
    """Custom breakpoint hook that uses IPython for debugging with rich colors."""
    # Handle async event loops
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            nest_asyncio.apply()  # pyright: ignore[reportUnknownMemberType]
    except RuntimeError:
        pass

    # Get caller's frame
    frame = sys._getframe().f_back  # pyright: ignore[reportPrivateUsage]

    # Set environment variables to configure IPython colors
    # The Linux color scheme has vibrant colors that work well on dark backgrounds
    os.environ["IPYTHON_COLORS"] = "Linux"

    # Set LESS options for proper color interpretation in pagers
    os.environ["PAGER"] = "less"
    os.environ["LESS"] = "-r"

    # Create our custom IPython-powered debugger with rich integration
    debugger = RichTerminalPdb()

    # Start the debugger at caller's frame
    debugger.set_trace(frame=frame)
