"""Command: qcopypos

Category: Quote Management
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from loguru import logger
from mutil.dispatch import DArg

from icli.cmds.base import IOp, command
from icli.helpers import *

if TYPE_CHECKING:
    pass


@command(names=["qcopypos"])
@dataclass
class IOpQuoteCopyPositions(IOp):
    """Copy another client's positions to your watchlist.

    This command will:
    1. Load another client's saved portfolio snapshot
    2. Extract the symbols from their positions
    3. Add those symbols to your current watchlist

    Usage:
        qcopypos 1    # Copy client 1's positions to your watchlist
        qcopypos 2    # Copy client 2's positions to your watchlist
    """

    otherClientId: int = field(init=False)

    def argmap(self):
        return [
            DArg(
                "otherClientId",
                convert=int,
                desc="Client ID of the account whose positions you want to copy",
            )
        ]

    async def run(self):
        # The approach of reading portfolio cache snapshot won't work because:
        # 1. positions command doesn't save snapshots
        # 2. Even if it did, portfolio data is live and changes frequently

        # Instead, we need to look for another approach:
        # Option 1: Look for quote groups that might contain position symbols
        # Option 2: Ask the user to run a command that saves positions to cache

        # For now, let's try to find quote groups that might contain the other client's symbols
        quoteKey = ("quotes", f"client-{self.otherClientId}")
        quoteData = self.cache.get(quoteKey)

        if not quoteData:
            logger.warning(
                "⚠️  No quote snapshot found for client {}. "
                "To copy positions from client {}, please:\n"
                "  1. Switch to client {} window\n"
                "  2. Run 'positions' to see their holdings\n"
                "  3. Manually add the symbols to your watchlist using 'add' command",
                self.otherClientId,
                self.otherClientId,
                self.otherClientId
            )
            return False

        # Extract symbols from quote data (contract objects)
        symbols_added = 0
        symbols_failed = 0

        try:
            contracts = quoteData.get("contracts", [])
            symbols_to_add = set()

            for contract in contracts:
                if hasattr(contract, 'localSymbol'):
                    symbol = contract.localSymbol
                    # Skip option symbols for now (they have complex formats)
                    if ' ' in symbol or len(symbol) > 10:
                        continue
                    symbols_to_add.add(symbol)
                elif hasattr(contract, 'symbol'):
                    symbol = contract.symbol
                    if symbol and len(symbol) <= 10:  # Skip complex option symbols
                        symbols_to_add.add(symbol)

            # Add symbols to current watchlist
            for symbol in symbols_to_add:
                try:
                    # Use the add command to subscribe to the symbol
                    result = await self.runoplive("add", symbol)
                    if result:
                        symbols_added += 1
                        logger.info("✅ Added {} to watchlist", symbol)
                    else:
                        symbols_failed += 1
                        logger.warning("⚠️  Failed to add {}", symbol)
                except Exception as e:
                    symbols_failed += 1
                    logger.warning("⚠️  Error adding {}: {}", symbol, e)

        except Exception as e:
            logger.error("❌ Error processing quote data: {}", e)
            return False

        if symbols_added == 0:
            logger.warning(
                "⚠️  No symbols found to add. "
                "For better results, ask client {} to run 'qsnapshot' first.",
                self.otherClientId
            )
            return False

        logger.info(
            "✅ Successfully added {} symbols to watchlist ({} failed)",
            symbols_added,
            symbols_failed
        )

        return symbols_added > 0