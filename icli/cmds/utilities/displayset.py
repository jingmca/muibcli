"""Command: display, cols

Category: Utilities

Configure display settings for positions and quotes.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from loguru import logger
from mutil.dispatch import DArg

from icli.cmds.base import IOp, command
from icli.display_config import (
    display_config,
    get_available_presets,
    validate_columns,
    POSITION_COLUMN_ALIASES,
)

if TYPE_CHECKING:
    pass


@command(names=["display", "cols"])
@dataclass
class IOpDisplay(IOp):
    """Configure display settings.

    Usage:
        display                                  # Show all current settings
        display positions.preset compact         # Set position preset
        display positions.columns type,sym,PNL   # Set custom columns
        display positions.autowidth true         # Enable auto-width detection
        display quotes.preset trading            # Set quote preset

    Available position presets:
        minimal, compact, trading, analysis, spread, full, auto

    Available quote presets:
        minimal, compact, trading, options, full
    """

    args: list[str] = field(init=False)

    def argmap(self):
        return [
            DArg(
                "*args",
                desc="Setting key and value (e.g., 'positions.preset compact')"
            )
        ]

    async def run(self):
        # No arguments: show all settings
        if not self.args:
            return self.show_all_settings()

        # One argument: show specific setting
        if len(self.args) == 1:
            return self.show_setting(self.args[0])

        # Two+ arguments: set value
        key = self.args[0]
        value = " ".join(self.args[1:])
        return self.set_setting(key, value)

    def show_all_settings(self):
        """Show all current display settings."""
        logger.info("📊 Current Display Settings:")
        logger.info("")
        logger.info("🔹 Positions:")
        logger.info("   preset:      {}", display_config.position_preset)
        logger.info("   columns:     {}", display_config.position_columns or "auto")
        logger.info("   auto_width:  {}", display_config.position_auto_width)
        logger.info("   threshold:   {}", display_config.position_width_threshold)
        logger.info("")
        logger.info("🔹 Quotes:")
        logger.info("   preset:      {}", display_config.quote_preset)
        logger.info("   columns:     {}", display_config.quote_columns or "auto")
        logger.info("")
        logger.info("Available presets:")
        logger.info("   Positions: {}", ", ".join(get_available_presets("position").keys()))
        logger.info("   Quotes:    {}", ", ".join(get_available_presets("quote").keys()))
        logger.info("")
        logger.info("💡 Usage: display <key> <value>")
        logger.info("   Examples:")
        logger.info("     display positions.preset compact")
        logger.info("     display positions.columns type,sym,position,PNL,%")
        logger.info("     display quotes.preset trading")

    def show_setting(self, key: str):
        """Show a specific setting."""
        parts = key.split(".")
        if len(parts) != 2:
            logger.error("❌ Invalid key format. Use: category.setting")
            logger.info("   Examples: positions.preset, quotes.columns")
            return False

        category, setting = parts

        if category == "positions" or category == "pos":
            if setting == "preset":
                logger.info("positions.preset = {}", display_config.position_preset)
            elif setting == "columns" or setting == "cols":
                logger.info("positions.columns = {}", display_config.position_columns or "auto")
            elif setting == "autowidth" or setting == "auto":
                logger.info("positions.auto_width = {}", display_config.position_auto_width)
            else:
                logger.error("❌ Unknown setting: {}", setting)
                logger.info("   Available: preset, columns, autowidth")
                return False
        elif category == "quotes" or category == "quote":
            if setting == "preset":
                logger.info("quotes.preset = {}", display_config.quote_preset)
            elif setting == "columns" or setting == "cols":
                logger.info("quotes.columns = {}", display_config.quote_columns or "auto")
            else:
                logger.error("❌ Unknown setting: {}", setting)
                logger.info("   Available: preset, columns")
                return False
        else:
            logger.error("❌ Unknown category: {}", category)
            logger.info("   Available: positions, quotes")
            return False

        return True

    def set_setting(self, key: str, value: str) -> bool:
        """Set a specific setting."""
        parts = key.split(".")
        if len(parts) != 2:
            logger.error("❌ Invalid key format. Use: category.setting")
            return False

        category, setting = parts

        # Handle positions settings
        if category in ("positions", "pos"):
            if setting == "preset":
                if display_config.set_position_preset(value):
                    logger.info("✅ Set positions.preset = {}", value)
                    return True
                else:
                    logger.error("❌ Invalid preset: {}", value)
                    logger.info("   Available: {}", ", ".join(get_available_presets("position").keys()))
                    return False

            elif setting in ("columns", "cols"):
                columns = [c.strip() for c in value.split(",")]
                valid, invalid = validate_columns(columns, "position")

                if not valid:
                    logger.error("❌ Invalid column names: {}", invalid)
                    logger.info("   Hint: Use column aliases like 'PNL' instead of 'unrealizedPNL'")
                    logger.info("   Available aliases: {}", ", ".join(POSITION_COLUMN_ALIASES.keys()))
                    return False

                display_config.set_position_columns(columns)
                logger.info("✅ Set positions.columns = {}", columns)
                return True

            elif setting in ("autowidth", "auto"):
                auto = value.lower() in ("true", "1", "yes", "on")
                display_config.position_auto_width = auto
                logger.info("✅ Set positions.auto_width = {}", auto)
                return True

            else:
                logger.error("❌ Unknown setting: {}", setting)
                return False

        # Handle quotes settings
        elif category in ("quotes", "quote"):
            if setting == "preset":
                if value in get_available_presets("quote"):
                    display_config.quote_preset = value
                    logger.info("✅ Set quotes.preset = {}", value)
                    return True
                else:
                    logger.error("❌ Invalid preset: {}", value)
                    logger.info("   Available: {}", ", ".join(get_available_presets("quote").keys()))
                    return False

            elif setting in ("columns", "cols"):
                columns = [c.strip() for c in value.split(",")]
                display_config.set_quote_columns(columns)
                logger.info("✅ Set quotes.columns = {}", columns)
                return True

            else:
                logger.error("❌ Unknown setting: {}", setting)
                return False

        else:
            logger.error("❌ Unknown category: {}", category)
            return False
