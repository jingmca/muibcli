#!/usr/bin/env python3

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv
from loguru import logger
from prompt_toolkit.patch_stdout import patch_stdout

import icli.cli as cli

# just load our dot files into the environment too
load_dotenv(".env.icli")

# Load display configuration
from icli.display_config import display_config

# Use more efficient coroutine logic if available
# https://docs.python.org/3.12/library/asyncio-task.html#asyncio.eager_task_factory
if sys.version_info >= (3, 12):
    asyncio.get_event_loop().set_task_factory(asyncio.eager_task_factory)

CONFIG_DEFAULT = dict(
    ICLI_IBKR_HOST="127.0.0.1", ICLI_IBKR_PORT=4001, ICLI_REFRESH=3.33
)

# populate config with defaults if they aren't in the environment
CONFIG = {**CONFIG_DEFAULT, **os.environ}

try:
    ACCOUNT_ID: str = CONFIG["ICLI_IBKR_ACCOUNT_ID"]  # type: ignore
except:
    logger.error(
        "Sorry, please provide your IBKR Account ID [U...] in ICLI_IBKR_ACCOUNT_ID"
    )
    sys.exit(0)

HOST: str = CONFIG["ICLI_IBKR_HOST"]  # type: ignore
PORT = int(CONFIG["ICLI_IBKR_PORT"])  # type: ignore
REFRESH = float(CONFIG["ICLI_REFRESH"])  # type: ignore


async def initcli():
    app = cli.IBKRCmdlineApp(
        accountId=ACCOUNT_ID, toolbarUpdateInterval=REFRESH, host=HOST, port=PORT
    )

    await app.setup()

    if sys.stdin.isatty():
        # patch entire application with prompt-toolkit-compatible stdout
        with patch_stdout(raw=True):
            try:
                await app.runall()
            except (SystemExit, EOFError):
                # known-good exit condition
                pass
            except:
                logger.exception("Major uncaught exception?")
    else:
        logger.error("Attached input isn't a console, so we can't do anything!")

    app.stop()


def runit():
    """Entry point for icli script and __main__ for entire package."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='ICLI - Interactive Brokers CLI Trading Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Display Presets:
  Position presets: minimal, compact, trading, analysis, full
  Quote presets: minimal, compact, trading, scalping, analysis, options, full

Examples:
  icli --position-preset compact --quote-preset trading
  icli -p minimal -q scalping
  icli --position-columns sym,position,PNL,%,w%

Environment Variables:
  ICLI_IBKR_ACCOUNT_ID - Your IBKR account ID (required)
  ICLI_IBKR_HOST       - Gateway host (default: 127.0.0.1)
  ICLI_IBKR_PORT       - Gateway port (default: 4001)
  ICLI_CLIENT_ID       - Client ID for this session
  ICLI_REFRESH         - Toolbar refresh rate in seconds (default: 3.33)
        """
    )

    parser.add_argument(
        '--position-preset', '-p',
        choices=['minimal', 'compact', 'trading', 'analysis', 'full', 'auto'],
        help='Position display preset (default: auto)'
    )

    parser.add_argument(
        '--quote-preset', '-q',
        choices=['minimal', 'compact', 'trading', 'scalping', 'analysis', 'options', 'full'],
        help='Quote display preset (default: compact)'
    )

    parser.add_argument(
        '--position-columns',
        type=str,
        metavar='COLUMNS',
        help='Custom position columns (comma-separated). Example: sym,position,PNL,%%,w%%'
    )

    parser.add_argument(
        '--quote-columns',
        type=str,
        metavar='COLUMNS',
        help='Custom quote columns (comma-separated) - for future use'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='ICLI 2.0.0 - Interactive Brokers CLI'
    )

    args = parser.parse_args()

    # Apply command-line display configuration
    if args.position_preset:
        if display_config.set_position_preset(args.position_preset):
            logger.info("Position preset set to: {}", args.position_preset)
        else:
            logger.error("Invalid position preset: {}", args.position_preset)
            sys.exit(1)

    if args.position_columns:
        display_config.set_position_columns(args.position_columns)
        logger.info("Position columns set to: {}", display_config.position_columns)

    if args.quote_preset:
        display_config.quote_preset = args.quote_preset
        logger.info("Quote preset set to: {}", args.quote_preset)

    if args.quote_columns:
        display_config.set_quote_columns(args.quote_columns)
        logger.info("Quote columns set to: {}", display_config.quote_columns)

    # Load environment variable overrides (if not already set by CLI args)
    if not args.position_preset and 'ICLI_POSITION_PRESET' in os.environ:
        display_config.position_preset = os.environ['ICLI_POSITION_PRESET']
        logger.info("Position preset loaded from env: {}", display_config.position_preset)

    if not args.quote_preset and 'ICLI_QUOTE_PRESET' in os.environ:
        display_config.quote_preset = os.environ['ICLI_QUOTE_PRESET']
        logger.info("Quote preset loaded from env: {}", display_config.quote_preset)

    try:
        asyncio.run(initcli())
    except (KeyboardInterrupt, SystemExit):
        # known-good exit condition
        ...
    except:
        logger.exception("bad bad so bad bad")


if __name__ == "__main__":
    runit()
