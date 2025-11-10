"""Command: qshare

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


@command(names=["qshare"])
@dataclass
class IOpQuoteShare(IOp):
    """Load another client's snapshot to share their live quotes.
    
    This is a convenience command that's equivalent to:
    qloadsnapshot <otherClientId>
    
    Usage:
        qshare 1    # Load quotes from client 1
        qshare 2    # Load quotes from client 2
    """

    otherClientId: int = field(init=False)

    def argmap(self):
        return [
            DArg(
                "otherClientId",
                convert=int,
                desc="Client ID of the account whose quotes you want to share",
            )
        ]

    async def run(self):
        # Just call qloadsnapshot with the other client ID
        result = await self.runoplive("qloadsnapshot", str(self.otherClientId))
        
        if result:
            logger.info(
                "✅ Loaded {} quotes from client {}",
                len(self.state.quoteState),
                self.otherClientId
            )
        else:
            logger.warning(
                "⚠️  No snapshot found for client {}. "
                "Make sure that client has saved quotes with 'qsnapshot' command.",
                self.otherClientId
            )
        
        return result
