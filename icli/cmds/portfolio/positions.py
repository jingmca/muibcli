"""Command: positions, ls

Category: Portfolio
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ib_async import (
    FuturesOption,
    Option,
    Warrant,
)
from loguru import logger
from mutil.dispatch import DArg
from mutil.frame import printFrame
from mutil.numeric import fmtPrice

from icli.cmds.base import IOp, command
from icli.helpers import *
from icli.display_config import display_config

if TYPE_CHECKING:
    pass
import shutil
import dateutil.parser
import pandas as pd


@command(names=["positions", "ls"])
@dataclass
class IOpPositions(IOp):
    """Print datatable of all positions."""

    symbols: set[str] = field(init=False)

    def argmap(self):
        return [DArg("*symbols", convert=lambda x: set([sym.upper() for sym in x]))]

    def totalFrame(self, df, costPrice=False):
        if df.empty:
            return None

        # Add new Total index row as column sum (axis=0 is column sum; axis=1 is row sum)
        totalCols = [
            "position",
            "marketValue",
            "totalCost",
            "unrealizedPNLPer",
            "unrealizedPNL",
            "dailyPNL",
            "%",
        ]

        # For spreads, we want to sum the costs/prices since they
        # are under the same order (hopefully).
        if costPrice:
            totalCols.extend(["averageCost", "marketPrice"])

        df.loc["Total"] = df[totalCols].sum(axis=0)
        t = df.loc["Total"]

        # don't do total maths unless totals actually exist
        # (e.g. if you have no open positions, this math obviously can't work)
        if t.all():
            df.loc["Total", "%"] = (
                (t.marketValue - t.totalCost) / ((t.marketValue + t.totalCost) / 2)
            ) * 100

        # Calculated weighted percentage ownership profit/loss...
        try:
            df["w%"] = df["%"] * (abs(df.totalCost) / df.loc["Total", "totalCost"])
            df.loc["Total", "w%"] = df["w%"].sum()
        except:
            # you probably don't have any positions...
            df["w%"] = 0
            df.loc["Total", "w%"] = 0

        # give actual price columns more detail for sub-penny prices
        # but give aggregate columns just two decimal precision
        detailCols = [
            "marketPrice",
            "averageCost",
            "strike",
        ]
        simpleCols = [
            "%",
            "w%",
            "unrealizedPNLPer",
            "unrealizedPNL",
            "dailyPNL",
            "totalCost",
            "marketValue",
        ]

        # convert columns to all strings because we format them as nice to read money strings, but pandas
        # doesn't like replacing strings over numeric-typed columns anymore.
        df[simpleCols] = df[simpleCols].astype(str)
        df[detailCols] = df[detailCols].astype(str)
        df["conId"] = df["conId"].map(lambda x: f"{int(x) if x and x == x else ''}")

        df.loc[:, detailCols] = (
            df[detailCols]
            .astype(float, errors="ignore")
            .map(
                lambda x: fmtPrice(float(x))
                if (x and (isinstance(x, str) and " " not in x))
                else x
            )
        )
        df.loc[:, simpleCols] = df[simpleCols].astype(float).map(lambda x: f"{x:,.2f}")

        # show fractional shares only if they exist
        defaultG = ["position"]
        df[defaultG] = df[defaultG].astype(str)
        df.loc[:, defaultG] = df[defaultG].astype(float).map(lambda x: f"{x:,.10g}")

        # manually override the string-printed 'nan' from .map() of totalCols
        # for columns we don't want summations of.
        # df.at["Total", "closeOrder"] = ""

        # if not costPrice:
        #     df.at["Total", "marketPrice"] = ""
        #     df.at["Total", "averageCost"] = ""

        return df

    async def run(self):
        ords = self.ib.portfolio()
        # logger.info("port: {}", pp.pformat(ords))

        backQuickRef = []
        populate = []

        for o in ords:
            # Store similar details together for same-symbol spread discovery
            backQuickRef.append((o.contract.secType, o.contract.symbol, o.contract))

            # fetch qualified contract from not completely populated port contract
            # (there's no speed difference fetching them individually vs collectively up front,
            #  so it's simpler just to run them one-by-one here as we iterate the portfolio)
            (contract,) = await self.state.qualify(o.contract)

            # fetch qualified contract metadata so we can use proper decimal rounding for display
            # (otherwise, we get IBKR default 8 digit floats everywhere)
            digits = self.state.decimals(contract)

            # Nice debug output showing full contracts.
            # TODO: enable global debug flags for showing these
            # maybe just enable logger.debug mode via a command?
            # logger.info("{}", o.contract)

            make: dict[str, Any] = {}

            # 't' used for switching on OPT/WAR/STK/FUT types later too.
            t = o.contract.secType

            make["conId"] = o.contract.conId
            make["type"] = t
            make["sym"] = o.contract.symbol

            # allow user input to compare against any of the actual symbols representing the instrument
            checkSymbols = {
                o.contract.symbol,
                o.contract.localSymbol,
                o.contract.localSymbol.replace(" ", ""),
                o.contract.tradingClass,
            }

            # TODO: update this to allow glob matching wtih fnmatch.filter(sourceCollection, targetGlob)
            if self.symbols and not (checkSymbols & self.symbols):
                continue

            # logger.info("contract is: {}", o.contract)
            if isinstance(o.contract, (Option, Warrant, FuturesOption)):
                try:
                    # Keep date as string in YYYYMMDD format for later processing
                    parsed_date = dateutil.parser.parse(
                        o.contract.lastTradeDateOrContractMonth
                    )
                    make["date"] = parsed_date.strftime('%Y%m%d')
                except:
                    logger.error("Row didn't have a good date? {}", o)
                    # If parsing fails, keep original string
                    make["date"] = o.contract.lastTradeDateOrContractMonth or ""

                make["strike"] = o.contract.strike
                make["PC"] = o.contract.right

            make["exch"] = o.contract.primaryExchange[:3]
            make["position"] = o.position

            make["marketPrice"] = round(o.marketPrice, digits + 1)

            close = self.state.orderPriceForContract(o.contract, o.position)

            # if it's a list of tuples, break them by newlines for display
            multiplier = float(o.contract.multiplier or 1)
            isLong = o.position > 0

            # TODO: fix this logic because technically if the close order isn't the entire size
            #       of the current position, we should always report in the list format to show pairs of size+price
            #       since we are only disposing of a sub-quantity of the entire position
            if isinstance(close, list):
                closingSide = " ".join([str(x) for x in close])
                make["closeOrderValue"] = " ".join(
                    [f"{size * price * multiplier:,.2f}" for size, price in close]
                )
                make["closeOrderProfit"] = " ".join(
                    [
                        f"{-((size * price * multiplier) + (o.averageCost * size)):,.2f}"
                        for size, price in close
                    ]
                    if isLong
                    else [
                        f"{(size * o.averageCost) - (size * price * multiplier):,.2f}"
                        for size, price in close
                    ]
                )
            else:
                closingSide = close
                # logger.info("FIELDS HERE: {}", pp.pformat(dict(close=close, pos=o.position, mul=multiplier, avg=o.averageCost, o=o)))
                make["closeOrderValue"] = f"{close * o.position * multiplier:,.2f}"

                # We use addition for the Profit here because the 'close' price is negaive for sales which makes the math work out.
                make["closeOrderProfit"] = (
                    # Longs have NEGATIVE CLOSING PRICE and POSIIVE COST,
                    # so we ADD THE EXIT PRICE to the COST BASIS (-exit + +cost) which is still a negative (credit)
                    # for a profit, but we invert it to show positive for profit here since this is a P&L column.
                    f"{-((close * o.position * multiplier) + (o.averageCost * o.position)):,.2f}"
                    if isLong
                    # Shorts have POSITIVE CLOSING PRICE and NEGATIVE COST
                    # TODO: verify short math works correct where profit is positive and loss is negative
                    else f"{(o.averageCost * o.position) - (close * o.position * multiplier):,.2f}"
                )

            make["closeOrder"] = closingSide
            make["marketValue"] = o.marketValue
            make["totalCost"] = o.averageCost * o.position
            make["unrealizedPNLPer"] = o.unrealizedPNL / abs(o.position)
            make["unrealizedPNL"] = o.unrealizedPNL

            try:
                # Note: dailyPnL per-position is only subscribed on the client where the order
                #       originated, so you may get 'dailyPnL' position errors if you view
                #       positions on a different client than the original.
                make["dailyPNL"] = self.state.pnlSingle[o.contract.conId].dailyPnL

                # API issue where it returns the largest value possible if not populated.
                # same as: sys.float_info.max:
                if not isset(make["dailyPNL"]):
                    make["dailyPNL"] = -1
            except:
                logger.warning(
                    "Subscribing to live PNL updates for: {}",
                    o.contract.localSymbol or o.contract.symbol,
                )

                # if we didn't have a PnL, attempt to subscribe it now anyway...
                # (We can have an unsubscribed PnL if we have live positions created today
                #  on another client or we have some positions just "show up" like getting assigned
                #  long shares from short puts or getting assigned short shares from short calls)
                self.state.pnlSingle[o.contract.conId] = self.ib.reqPnLSingle(
                    self.state.accountId, "", o.contract.conId
                )

                pass

            multiplier = float(o.contract.multiplier or 1)
            if t == "FUT":
                make["averageCost"] = round(o.averageCost / multiplier, digits + 1)
                make["%"] = (
                    (o.marketPrice * multiplier - o.averageCost) / o.averageCost * 100
                )
            elif t == "BAG":
                logger.info("available: {}", o)
            elif t in {"OPT", "FOP"}:
                # For some reason, IBKR reports marketPrice
                # as the contract price, but averageCost as
                # the total cost per contract. shrug.
                make["%"] = (
                    (o.marketPrice * multiplier - o.averageCost) / o.averageCost * 100
                )

                # show average cost per share instead of per contract
                # because the "marketPrice" live quote is the quote
                # per share, not per contract.
                make["averageCost"] = round(o.averageCost / multiplier, digits + 1)
            else:
                make["%"] = (o.marketPrice - o.averageCost) / o.averageCost * 100
                make["averageCost"] = round(o.averageCost, digits + 1)

            # if short, our profit percentage is reversed
            if o.position < 0:
                make["%"] *= -1
                make["averageCost"] *= -1
                make["marketPrice"] *= -1

            populate.append(make)

        # positions() just returns symbol names, share count, and cost basis.
        # portfolio() returns PnL details and current market prices/values
        df = pd.DataFrame(
            data=populate,
            columns=[
                "type",
                "sym",
                "conId",
                "PC",
                "date",
                "strike",
                "exch",
                "position",
                "averageCost",
                "marketPrice",
                "closeOrder",
                "closeOrderValue",
                "closeOrderProfit",
                "marketValue",
                "totalCost",
                "unrealizedPNLPer",
                "unrealizedPNL",
                "dailyPNL",
                "%",
            ],
        )

        df.sort_values(by=["date", "sym", "PC", "strike"], ascending=True, inplace=True)

        # re-number DF according to the new sort order
        df.reset_index(drop=True, inplace=True)

        allPositions = self.totalFrame(df.copy())
        if allPositions is None:
            logger.info("No current positions found!")
            return None

        # Get terminal width for adaptive display
        terminal_width = shutil.get_terminal_size((80, 40)).columns
        logger.info(f"Terminal width detected: {terminal_width}")

        # Calculate portfolio weight percentage for each position
        if "Total" in allPositions.index and "marketValue" in allPositions.columns:
            try:
                # Convert to float, handling both numeric and string types
                total_val = allPositions.loc["Total", "marketValue"]
                if isinstance(total_val, str):
                    # Remove commas and convert to float
                    total_val = float(total_val.replace(',', ''))
                total_value = abs(total_val)

                if total_value > 0:
                    # Calculate weight percentage for each position
                    def calc_weight(x):
                        try:
                            if pd.isna(x) or x == "NaN":
                                return 0.0
                            if isinstance(x, str):
                                # Remove commas from string values
                                val = float(x.replace(',', ''))
                            else:
                                val = float(x)
                            return round(abs(val) / total_value * 100, 2)
                        except:
                            return 0.0

                    allPositions["w%"] = allPositions["marketValue"].apply(calc_weight)
                    allPositions.loc["Total", "w%"] = 100.0
                    # Ensure w% is numeric type
                    allPositions["w%"] = pd.to_numeric(allPositions["w%"], errors='coerce').fillna(0.0)
            except (ValueError, TypeError, Exception) as e:
                # If conversion fails, skip weight calculation
                logger.warning("Could not calculate portfolio weights: {}", e)
                pass

        # Determine if we should use preset-based display or full display
        # Priority: explicit preset > terminal width auto-detection
        use_preset_display = (
            display_config.position_preset != "full" and
            display_config.position_preset != "auto"
        ) or terminal_width <= 120

        # Create compact/preset view
        if use_preset_display:
            # Get columns from display_config
            preset_cols = display_config.get_position_columns()

            if preset_cols is None:
                # Full mode or auto with wide terminal - use default compact
                compact_cols = ["type", "sym", "position", "avgCost", "mktPrice", "mktValue", "PNL", "%", "w%"]
            else:
                # Use preset columns exactly as specified (don't add type)
                # We'll use allPositions to detect options, not compact_df
                compact_cols = preset_cols

            # Map to actual column names
            col_mapping = {
                "avgCost": "averageCost",
                "mktPrice": "marketPrice",
                "mktValue": "marketValue",
                "PNL": "unrealizedPNL"
            }

            # Get available columns with proper names
            available_cols = []
            all_cols_list = list(allPositions.columns)  # Convert to list to avoid pandas type issues
            for col in compact_cols:
                actual_col = col_mapping.get(col, col)
                if actual_col in all_cols_list:
                    available_cols.append(actual_col)

            # Create compact dataframe first
            compact_df = allPositions[available_cols].copy()

            # Format option symbols using OCC standard format
            # For compact/minimal/trading modes: use OCC format (AAPL240816C00220000)
            # For full mode: keep separate columns (handled separately, not in compact_df)
            for idx in compact_df.index:
                if idx != "Total":
                    row = allPositions.loc[idx]
                    if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
                        date_str = str(row.get("date", ""))
                        strike = row.get("strike", 0)
                        pc = row.get("PC", "")
                        symbol = str(row["sym"])

                        # Use OCC format for all non-full modes
                        compact_df.at[idx, "sym"] = format_option_symbol(
                            symbol, date_str, strike, pc, "occ"
                        )

            # Rename columns to shorter names
            rename_map = {v: k for k, v in col_mapping.items()}
            compact_df.rename(columns=rename_map, inplace=True)

            # Format numbers for compact display - convert to numeric first to handle commas
            if "avgCost" in compact_df.columns:
                compact_df["avgCost"] = pd.to_numeric(compact_df["avgCost"].astype(str).str.replace(',', ''), errors='coerce').round(2)
            if "mktPrice" in compact_df.columns:
                compact_df["mktPrice"] = pd.to_numeric(compact_df["mktPrice"].astype(str).str.replace(',', ''), errors='coerce').round(2)
            if "mktValue" in compact_df.columns:
                compact_df["mktValue"] = pd.to_numeric(compact_df["mktValue"].astype(str).str.replace(',', ''), errors='coerce').round(0)
            if "PNL" in compact_df.columns:
                compact_df["PNL"] = pd.to_numeric(compact_df["PNL"].astype(str).str.replace(',', ''), errors='coerce').round(0)
            if "w%" in compact_df.columns:
                compact_df["w%"] = pd.to_numeric(compact_df["w%"], errors='coerce').fillna(0.0).round(2)

            # Truncate symbol names to fit
            if "sym" in compact_df.columns:
                compact_df["sym"] = compact_df["sym"].astype(str).str[:15]

            # Log full details for reference
            logger.info("Compact view for terminal width: {}", terminal_width)

            desc = f"Positions ({len(allPositions)-1})"
            if self.symbols:
                desc += f" for {', '.join(list(self.symbols)[:2])}"

            printFrame(compact_df, desc)

            if terminal_width <= 80:
                print("[Tip: Some columns hidden. Check log for details]")
        else:
            # Wide terminal - show more details but still hide some columns
            drop_cols = ["closeOrder", "closeOrderValue", "closeOrderProfit", "conId", "exch"]
            display_df = allPositions.drop(columns=[col for col in drop_cols if col in allPositions.columns]).copy()

            # Format option symbols to OCC even in full/wide mode
            for idx in display_df.index:
                if idx != "Total":
                    row = allPositions.loc[idx]
                    if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
                        date_str = str(row.get("date", ""))
                        strike = row.get("strike", 0)
                        pc = row.get("PC", "")
                        symbol = str(row["sym"])

                        # Use OCC format for options in wide display too
                        display_df.at[idx, "sym"] = format_option_symbol(
                            symbol, date_str, strike, pc, "occ"
                        )

            desc = "All Positions"
            if self.symbols:
                desc += f" for {', '.join(self.symbols)}"
            printFrame(display_df, desc)

        # attempt to find spreads by locating options with the same symbol
        symbolCounts = df.pivot_table(index=["type", "sym", "date"], aggfunc="size")

        spreadSyms = set()
        postype: str
        sym: str
        date: str
        for (postype, sym, date), symCount in symbolCounts.items():  # type: ignore
            if postype in {"OPT", "FOP"} and symCount > 1:
                spreadSyms.add((sym, date))

        # print individual frames for each spread since the summations
        # will look better (also sort the symbols so the set() is always in the same order across clients)
        # TODO: we would need a real database of trade intent to record spreads because we can't tell the difference
        #       between a single vertical spread or two vertical spreads combined for math purposes.
        for sym, date in sorted(spreadSyms):
            spread = df[
                df.type.isin({"OPT", "FOP"}) & (df.sym == sym) & (df.date == date)
            ]
            spread = self.totalFrame(spread.copy(), costPrice=True)

            # Apply compact view to spread display too (if terminal is narrow)
            logger.debug(f"Spread display - terminal_width: {terminal_width}")
            if terminal_width <= 120:
                # Create compact spread display
                compact_spread_cols = ["type", "PC", "strike", "position", "averageCost", "marketPrice", "marketValue", "unrealizedPNL", "%", "w%"]
                all_spread_cols = list(spread.columns)
                available_spread_cols = [col for col in compact_spread_cols if col in all_spread_cols]
                spread_display = spread[available_spread_cols].copy()

                # Shorten column names
                spread_display.rename(columns={
                    "averageCost": "avgCost",
                    "marketPrice": "mktPrice",
                    "marketValue": "mktValue",
                    "unrealizedPNL": "PNL"
                }, inplace=True)

                # Format numbers
                if "avgCost" in spread_display.columns:
                    spread_display["avgCost"] = pd.to_numeric(spread_display["avgCost"], errors='coerce').round(2)
                if "mktPrice" in spread_display.columns:
                    spread_display["mktPrice"] = pd.to_numeric(spread_display["mktPrice"], errors='coerce').round(2)
                if "mktValue" in spread_display.columns:
                    spread_display["mktValue"] = pd.to_numeric(spread_display["mktValue"], errors='coerce').round(0)
                if "PNL" in spread_display.columns:
                    spread_display["PNL"] = pd.to_numeric(spread_display["PNL"], errors='coerce').round(0)
                if "w%" in spread_display.columns:
                    spread_display["w%"] = pd.to_numeric(spread_display["w%"], errors='coerce').fillna(0.0).round(2)

                # Format date from YYYYMMDD to MM/DD
                date_str = str(date)
                if len(date_str) >= 8:
                    exp_display = f"{date_str[4:6]}/{date_str[6:8]}"
                else:
                    exp_display = date_str

                printFrame(spread_display, f"[{sym} {exp_display}] Spread")
            else:
                # Wide terminal spread display - also format option symbols to OCC
                spread_occ = spread.copy()

                # Format option symbols to OCC format
                for idx in spread_occ.index:
                    if idx != "Total":
                        row = spread.loc[idx]
                        if row["type"] in {"OPT", "FOP"} and pd.notna(row.get("strike")):
                            date_str = str(row.get("date", ""))
                            strike = row.get("strike", 0)
                            pc = row.get("PC", "")
                            symbol = str(row["sym"])

                            # Use OCC format for spread display too
                            spread_occ.at[idx, "sym"] = format_option_symbol(
                                symbol, date_str, strike, pc, "occ"
                            )

                printFrame(spread_occ, f"[{sym}] Potential Spread Identified")

            matchingContracts = [
                contract
                for secType, bqrsym, contract in backQuickRef
                if secType in {"OPT", "FOP"} and bqrsym == sym
            ]

            # transmit the size of the spread only if all are the same
            # TODO: figure out how to do this for butterflies, etc
            equality = 0
            if spread.loc["Total", "position"] == "0":  # yeah, it's a string here
                equality = spread.iloc[0]["position"]

            closeit = self.state.orderPriceForSpread(matchingContracts, equality)
            logger.info("Potential Closing Side: {}", closeit)
