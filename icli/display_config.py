"""Display configuration system for controlling column visibility.

This module provides:
- Column presets for positions and quotes
- Runtime configuration via 'set' command
- Environment variable support
- Command-line flag support
"""

from dataclasses import dataclass, field
from typing import Literal

# ========== Position Display Presets ==========

POSITION_PRESETS = {
    "minimal": ["sym", "position", "avgCost", "mktPrice", "%", "PNL"],
    "compact": ["sym", "position", "avgCost", "mktPrice", "mktValue", "%", "w%", "PNL"],
    "trading": ["sym", "position", "avgCost", "mktPrice", "closeOrder", "%", "w%", "dailyPNL", "PNL"],
    "analysis": ["sym", "position", "marketValue", "totalCost", "%", "w%", "dailyPNL", "unrealizedPNL"],
    "full": None,  # None means show all columns
}

# All available position columns
POSITION_ALL_COLUMNS = [
    "type", "sym", "conId", "PC", "date", "strike", "exch",
    "position", "averageCost", "marketPrice",
    "closeOrder", "closeOrderValue", "closeOrderProfit",
    "marketValue", "totalCost", "unrealizedPNLPer",
    "unrealizedPNL", "dailyPNL", "%", "w%"
]

# Column aliases for shorter names
POSITION_COLUMN_ALIASES = {
    "avgCost": "averageCost",
    "mktPrice": "marketPrice",
    "mktValue": "marketValue",
    "PNL": "unrealizedPNL",
    "pnl": "unrealizedPNL",
    "cost": "averageCost",
    "price": "marketPrice",
    "value": "marketValue",
    "pct": "%",
    "weight": "w%",
}

# ========== Quote Display Presets ==========

# Note: Quote display is currently generated as a formatted string in cli.py formatTicker()
# These presets are placeholders for future refactoring when quote fields become configurable
QUOTE_PRESETS = {
    "minimal": ["sym", "last", "bid", "ask", "change", "%"],
    "compact": ["sym", "last", "bid", "ask", "bidSize", "askSize", "change", "%", "volume"],
    "trading": ["sym", "ema100", "trend", "last", "spread", "bid", "ask", "bidSize", "askSize", "atr", "%"],
    "scalping": ["sym", "ema100", "last", "spread", "bid", "ask", "bidSize", "askSize", "atr", "%"],
    "analysis": ["sym", "ema100", "ema100diff", "trend", "ema300", "last", "high", "low", "vwap", "vwapDiff", "atr", "%", "volume"],
    "options": ["sym", "underlying", "itm", "iv", "delta", "mark", "bid", "ask", "spread", "dte"],
    "full": None,
}

# ========== Display Configuration ==========

@dataclass
class DisplayConfig:
    """Runtime display configuration."""

    # Position settings
    position_columns: list[str] | None = None
    position_preset: str = "auto"  # auto, minimal, compact, trading, analysis, spread, full
    position_auto_width: bool = True  # Automatically adjust based on terminal width
    position_width_threshold: int = 120  # Terminal width threshold for auto mode

    # Quote settings
    quote_columns: list[str] | None = None
    quote_preset: str = "full"  # Changed default from "compact" to "full"
    quote_show_greeks: bool = True

    # Global settings
    terminal_width: int | None = None  # Override terminal width detection
    color_enabled: bool = True

    def get_position_columns(
        self,
        override_preset: str | None = None,
        override_columns: list[str] | None = None,
        current_terminal_width: int | None = None
    ) -> list[str] | None:
        """Get position columns based on current settings and overrides.

        Priority: override_columns > override_preset > config > auto-detect

        Returns:
            List of column names, or None for all columns
        """
        # 1. Command-line column override
        if override_columns:
            return self._resolve_column_aliases(override_columns, POSITION_COLUMN_ALIASES)

        # 2. Command-line preset override
        preset = override_preset or self.position_preset

        # 3. Auto mode: select based on terminal width
        if preset == "auto" and self.position_auto_width:
            width = current_terminal_width or self.terminal_width or 120
            preset = "compact" if width <= self.position_width_threshold else "full"

        # 4. Return preset columns
        if preset in POSITION_PRESETS:
            cols = POSITION_PRESETS[preset]
            if cols is None:
                return None  # Show all
            return self._resolve_column_aliases(cols, POSITION_COLUMN_ALIASES)

        # 5. Fallback to compact
        return POSITION_PRESETS["compact"]

    def get_quote_columns(
        self,
        override_preset: str | None = None,
        override_columns: list[str] | None = None
    ) -> list[str] | None:
        """Get quote columns based on current settings and overrides."""
        if override_columns:
            return override_columns

        preset = override_preset or self.quote_preset
        if preset in QUOTE_PRESETS:
            return QUOTE_PRESETS[preset]

        return QUOTE_PRESETS["compact"]

    def _resolve_column_aliases(
        self,
        columns: list[str],
        aliases: dict[str, str]
    ) -> list[str]:
        """Resolve column aliases to actual column names."""
        return [aliases.get(col, col) for col in columns]

    def set_position_preset(self, preset: str) -> bool:
        """Set position display preset."""
        if preset not in POSITION_PRESETS and preset != "auto":
            return False
        self.position_preset = preset
        return True

    def set_position_columns(self, columns: list[str] | str):
        """Set custom position columns."""
        if isinstance(columns, str):
            columns = [c.strip() for c in columns.split(",")]
        self.position_columns = columns

    def to_env_dict(self) -> dict[str, str]:
        """Convert to environment variable format for saving."""
        return {
            "ICLI_POSITION_PRESET": self.position_preset,
            "ICLI_POSITION_COLUMNS": ",".join(self.position_columns) if self.position_columns else "",
            "ICLI_POSITION_AUTO_WIDTH": str(self.position_auto_width),
            "ICLI_QUOTE_PRESET": self.quote_preset,
            "ICLI_QUOTE_COLUMNS": ",".join(self.quote_columns) if self.quote_columns else "",
        }

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "DisplayConfig":
        """Load from environment variables."""
        config = cls()

        if preset := env.get("ICLI_POSITION_PRESET"):
            config.position_preset = preset

        if cols := env.get("ICLI_POSITION_COLUMNS"):
            config.position_columns = [c.strip() for c in cols.split(",") if c.strip()]

        if auto := env.get("ICLI_POSITION_AUTO_WIDTH"):
            config.position_auto_width = auto.lower() in ("true", "1", "yes")

        if preset := env.get("ICLI_QUOTE_PRESET"):
            config.quote_preset = preset

        if cols := env.get("ICLI_QUOTE_COLUMNS"):
            config.quote_columns = [c.strip() for c in cols.split(",") if c.strip()]

        return config


# Global display configuration instance
display_config = DisplayConfig()


def get_available_presets(category: Literal["position", "quote"] = "position") -> dict[str, list[str] | None]:
    """Get available presets for a category."""
    if category == "position":
        return POSITION_PRESETS.copy()
    elif category == "quote":
        return QUOTE_PRESETS.copy()
    return {}


def validate_columns(columns: list[str], category: Literal["position", "quote"] = "position") -> tuple[bool, list[str]]:
    """Validate column names.

    Returns:
        (is_valid, invalid_columns)
    """
    if category == "position":
        valid = set(POSITION_ALL_COLUMNS) | set(POSITION_COLUMN_ALIASES.keys())
    else:
        valid = set()  # TODO: Define quote columns

    invalid = [c for c in columns if c not in valid]
    return len(invalid) == 0, invalid
