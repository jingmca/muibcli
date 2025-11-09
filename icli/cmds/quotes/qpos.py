"""Command: qpos

Category: Live Market Quotes
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger
from mutil.dispatch import DArg

from icli.cmds.base import IOp, command

if TYPE_CHECKING:
    pass


@command(names=["qpos"])
@dataclass
class IOpQuotePositions(IOp):
    """Add all current positions to the quote watch list"""

    def argmap(self):
        return []

    async def run(self):
        """Add symbols from current positions to live quote display."""

        # Get all position symbols
        position_symbols = []

        # Get portfolio positions
        positions = self.ib.portfolio()

        # Iterate through all positions
        for position in positions:
                contract = position.contract

                # Get the appropriate symbol for adding to quotes
                if contract.secType == "STK":
                    # For stocks, use the symbol directly
                    symbol = contract.symbol
                elif contract.secType in {"OPT", "FOP"}:
                    # For options, use the contract ID instead to avoid parsing issues
                    symbol = str(contract.conId)
                elif contract.secType == "FUT":
                    # For futures, use the contract ID
                    symbol = str(contract.conId)
                else:
                    # For other types, use contract ID
                    symbol = str(contract.conId)

                # Avoid duplicates
                if symbol and symbol not in position_symbols:
                    position_symbols.append(symbol)

        if not position_symbols:
            logger.warning("No positions found to add to quotes")
            return

        # Sort symbols for consistent display
        position_symbols.sort()

        logger.info("Adding {} position symbols to quotes: {}",
                   len(position_symbols), ", ".join(position_symbols[:5]) + "..." if len(position_symbols) > 5 else ", ".join(position_symbols))

        # Add quotes using the existing add command
        # Quote symbols with spaces need to be quoted
        quoted_symbols = [f'"{sym}"' if " " in sym else sym for sym in position_symbols]

        await self.runoplive("add", " ".join(quoted_symbols))

        logger.info("Successfully added {} position symbols to live quotes", len(position_symbols))
        return True