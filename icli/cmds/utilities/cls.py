"""Command: cls

Category: Utilities
"""

import os
import platform
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger
from mutil.dispatch import DArg

from icli.cmds.base import IOp, command

if TYPE_CHECKING:
    pass


@command(names=["cls"])
@dataclass
class IOpClearScreen(IOp):
    """Clear the terminal screen"""

    def argmap(self):
        return []

    async def run(self):
        """Clear the terminal screen display."""
        # Detect platform and use appropriate clear command
        system = platform.system()

        if system in ["Linux", "Darwin"]:  # Darwin is macOS
            os.system("clear")
        elif system == "Windows":
            os.system("cls")
        else:
            # Fallback: print many newlines to push content up
            print("\n" * 100)

        logger.info("Terminal screen cleared")
        return True