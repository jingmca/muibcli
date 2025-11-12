"""Command: chains

Category: Live Market Quotes
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ib_async import (
    Contract,
    FuturesOption,
    Option,
)
from loguru import logger
from mutil.dispatch import DArg

from icli.cmds.base import IOp, command
from icli.helpers import *

if TYPE_CHECKING:
    pass
import asyncio

import dateutil.parser
import prettyprinter as pp  # type: ignore
import whenever


@command(names=["chains"])
@dataclass
class IOpOptionChain(IOp):
    """Print option chains for symbol with optional price range filter.

    Usage:
        chains SPY                    # All strikes
        chains SPY 600 650           # Only strikes between $600-$650
        chains SPY REFRESH           # Force refresh cache
        chains SPY 600 650 REFRESH   # With price range and refresh
    """

    symbols: list[str] = field(init=False)
    minPrice: float | None = field(init=False, default=None)
    maxPrice: float | None = field(init=False, default=None)

    def argmap(self):
        return [
            DArg(
                "*symbols",
                convert=lambda x: [z.upper() for z in x],
            )
        ]

    def parseArgs(self):
        """Parse symbols and extract price range if provided."""
        filtered_symbols = []
        prices = []

        for s in self.symbols:
            # Check if it's a number (price)
            try:
                price = float(s)
                prices.append(price)
            except ValueError:
                # Not a number, it's a symbol or keyword
                filtered_symbols.append(s)

        # Update symbols to only contain actual symbols
        self.symbols = filtered_symbols

        # Set price range if provided
        if len(prices) >= 2:
            self.minPrice = min(prices[0], prices[1])
            self.maxPrice = max(prices[0], prices[1])
        elif len(prices) == 1:
            # If only one price, use it as center ±20%
            center = prices[0]
            self.minPrice = center * 0.8
            self.maxPrice = center * 1.2

    async def run(self):
        # Parse arguments to extract price range and symbols
        self.parseArgs()

        # Index cache by symbol AND current date because strikes can change
        # every day even for the same expiration if there's high volatility.
        got = {}

        symbol: str | None
        self.symbols: list[str]
        IS_PREVIEW = len(self.symbols) > 0 and self.symbols[-1] == "PREVIEW"
        IS_REFRESH = False
        if len(self.symbols) > 0 and self.symbols[-1] == "REFRESH":
            IS_REFRESH = True
            # remove "REFRESH" from symbols so we don't try to look it up
            self.symbols = self.symbols[:-1]

        for symbol in self.symbols:
            # if asking for weeklies, need to correct symbol for underlying quote...
            if symbol == "SPXW":
                symbol = "SPX"

            # our own symbol hack for printing more detailed output here
            if symbol == "PREVIEW":
                continue

            contractFound: Contract | None = None
            if symbol.startswith(":"):
                symbol, contractFound = self.state.quoteResolve(symbol)
                assert symbol

            cacheKey = ("chains", symbol)
            # logger.info("Looking up {}", cacheKey)

            # if found in cache, don't lookup again!
            if not IS_REFRESH:
                if (found := self.cache.get(cacheKey)) and all(list(found.items())):
                    got[symbol] = found
                    # Display cached chains (unless in PREVIEW mode for Fast command)
                    if not IS_PREVIEW:
                        await self.displayChains(symbol, found)
                    else:
                        logger.info(
                            "[{}] Already cached: {}",
                            symbol,
                            pp.pformat(found.items()),
                        )
                    continue

            # resolve for option chains lookup

            if contractFound:
                contractExact = contractFound
            else:
                contractExact = contractForName(symbol)

            # if we want to request ALL chains, only provide underlying
            # symbol then mock it as "OPT" so the IBKR resolver sees we
            # are requesting option underlying and not just single-stock
            # contract details.
            # NOTE: we DO NOT POPULATE contractId on OPT/FOP lookups or else
            #       it pins the entire lookup to a single ID. We need our
            #       lookups to search more generally without an id.
            if isinstance(contractExact, Stock):
                # hack/edit contract type to be different for OPTION lookup using Stock underlying details
                contractExact.secType = "OPT"
                contractExact.conId = 0
            elif isinstance(contractExact, Future):
                # hack/edit contract type to be different for FUTURES OPTION lookup using Future underlying details
                contractExact.secType = "FOP"
                contractExact.conId = 0
            elif isinstance(contractExact, Index):
                # sure, is fine too
                # we use the different API for index options, so we need an exact contract id
                (contractExact,) = await self.state.qualify(contractExact)
                pass
            else:
                logger.error(
                    "Unknown contract type requested for chain? Got: {}", contractExact
                )

            # note "fetching" here so it doesn't fire if the cache hit passes.
            # (We only want to log the fetching network requests; just cache reading is quiet)
            logger.info("[chains] Fetching for {} using {}", symbol, contractExact)

            # If full option symbol, get all strikes for the date of the symbol
            if isinstance(contractExact, (Option, FuturesOption)):
                contractExact.strike = 0.00
                # if is option already, use exact date of option...
                useDates = set(
                    [dateutil.parser.parse("20" + symbol[-15 : -15 + 6]).date()]
                )  # type: ignore
            else:
                # Actually, even more, we should use the calendar returned from contract details, but, due to IBKR
                # data problems, we change the gateway to only return 2 future days instead of 10+ future days. sigh.
                # Note: the 'tradingDays()' API returns number of market days in the next N CALENDAR DAYS. So if you want
                #       an entire next month of expirations, you need to request "31" trading days ahead.
                # ALSO NOTE: this doesn't work cleanly _across future expiration boundaries_ for generic symbols.
                #            So if you need the next quarter future expiration, you need to use the exact name and not just '/ES + 100 days' etc.
                # TODO: this fetches many redundant dates because not all symbols trade in all days. We should fix the request system.
                useDates = [
                    datetime.date(d.year, d.month, d.day)  # type: ignore
                    for d in self.state.tradingDays(40)
                ]

            # this request takes between 1 second and 60 seconds depending on ???
            # does IBKR rate limit this endpoint? sometimes the same request
            # takes 1-5 seconds, other times it takes 45-65 seconds.
            # Maybe it's rate limited to one "big" call per minute?
            # (UPDATE: yeah, the docs say:
            #  "due to the potentially high amount of data resulting from such
            #   queries this request is subject to pacing. Although a request such
            #   as the above one will be answered immediately, a similar subsequent
            #   one will be kept on hold for one minute.")
            # So this endpoint is a jerk. You may need to rely on an external data
            # provider if you want to gather full chains of multiple underlyings
            # without waiting 1 minute per symbol.
            # Depending on what you ask for with the contract, it can return between
            # one row (one date+strike), dozens of rows (all strikes for a date),
            # or thousands of rows (all strikes at all future dates).

            # complete return value for caller to use if they need it
            got = {}

            # fetch dates by MONTH so IBKR returns all days for all the months requested
            # (so we don't get stuck requesting day-by-day or non-existing days between instruments
            #  trading daily vs weekly vs monthly vs quarterly etc)
            fetchDates = sorted(set([f"{d.year}{d.month:02}" for d in useDates]))
            logger.info("Fetching for dates: {}", fetchDates)

            logger.info("[{}{}] Fetching strikes...", symbol, fetchDates)

            try:
                # Note: we converted this from reqContractDetailsAsync() to use multiple data providers.
                #       If you have a tradier API key in your environment (TRADIER_KEY=key), we use tradier
                #       directly because it fetches chains in less than 100 ms while IBKR sometimes takes minutes
                #       to fetch many chains at once.
                #
                # long timeout here because these get delayed by IBKR "pacing backoff" API limits sometimes.
                #
                # Note: IBKR API docs mention another function called reqSecDefOptParams() but it returns INVALID date+strike details
                #       so its output is completely useless (it returns a list of dates and a list of strikes, but it doesn't combine
                #       strikes-per-date so you have "all strikes for the next 5 years" against "all dates for the next 5 years" which
                #       isn't valid because of things like split-strikes-vs-weekly-vs-opex-vs-LEAP strikes all combined showing for
                #       all dates which isn't applicable at all, so the output from reqSecDefOptParams() is practically useless).
                strikes = await asyncio.wait_for(
                    self.state.fetchContractExpirations(contractExact, fetchDates),
                    timeout=180,
                )

                # only cahce if strikes exist _AND_ all the values exist
                # (because strikes are returned as {key: strikes} so 'strikes' should always exist on its own
                if strikes and all(list(strikes.values())):
                    # TODO: maybe more logically expire strike caches at the next 1615 available
                    # Expire in 10 calendar days at 1700 ET (to prevent these from expiring IN THE MIDDLE OF A LIVE SESSION).
                    now = whenever.ZonedDateTime.now("US/Eastern")
                    expireAt = now.add(days=10, disambiguate="compatible").replace(
                        hour=17, minute=0, disambiguate="compatible"
                    )
                    expireSeconds = (expireAt - now).in_seconds()

                    self.cache.set(cacheKey, strikes, expire=expireSeconds)  # type: ignore

                got[symbol] = strikes

                # Format and display the strikes in horizontal format
                await self.displayChains(symbol, strikes)
            except:
                logger.exception(
                    "[{}] Error while fetching contract details...",
                    symbol,
                )

        return got

    async def displayChains(self, symbol: str, strikes: dict):
        """Display option chains in compact horizontal format with ATM symbols."""
        # Get current price for ATM calculation
        try:
            # Add quote if not already subscribed
            await self.runoplive("add", symbol)

            # Wait briefly for quote to populate
            for _ in range(5):
                if symbol in self.state.quoteState:
                    quote = self.state.quoteState[symbol]
                    if quote.last == quote.last:  # Check not NaN
                        break
                await asyncio.sleep(0.1)

            currentPrice = None
            if symbol in self.state.quoteState:
                quote = self.state.quoteState[symbol]
                # Try last, then close as fallback
                currentPrice = quote.last if quote.last == quote.last else quote.close
        except:
            currentPrice = None

        logger.info("\n" + "=" * 80)
        logger.info(f"[{symbol}] Option Chains" + (f" (Current: ${currentPrice:,.2f})" if currentPrice else ""))

        if self.minPrice or self.maxPrice:
            logger.info(f"Price Range: ${self.minPrice or 0:,.2f} - ${self.maxPrice or 999999:,.2f}")

        logger.info("=" * 80)

        # Sort dates
        sorted_dates = sorted(strikes.keys())

        for date in sorted_dates:
            strike_list = strikes[date]

            # Filter by price range if specified
            if self.minPrice or self.maxPrice:
                strike_list = [
                    s for s in strike_list
                    if (not self.minPrice or s >= self.minPrice) and
                       (not self.maxPrice or s <= self.maxPrice)
                ]

            if not strike_list:
                continue

            # Find ATM strike (closest to current price)
            atm_strike = None
            atm_call = None
            atm_put = None

            if currentPrice and currentPrice == currentPrice:  # Check not NaN
                atm_strike = min(strike_list, key=lambda s: abs(s - currentPrice))
                # Format OCC symbols for ATM options
                # Date format: YYMMDD from full date YYYYMMDD
                date_str = date[2:]  # Remove first 2 digits (20XX -> XX)
                atm_call = f"{symbol}{date_str}C{int(atm_strike * 1000):08d}"
                atm_put = f"{symbol}{date_str}P{int(atm_strike * 1000):08d}"

            # Format date nicely
            try:
                date_obj = dateutil.parser.parse(date)
                date_display = date_obj.strftime("%Y-%m-%d")
            except:
                date_display = date

            # Display in horizontal format
            strike_str = ", ".join([f"{s:.2f}" for s in sorted(strike_list)[:20]])  # Limit to first 20
            if len(strike_list) > 20:
                strike_str += f" ... (+{len(strike_list) - 20} more)"

            logger.info(f"\n[{date_display}] {len(strike_list)} strikes: {strike_str}")

            if atm_call and atm_put:
                logger.info(f"  ATM ${atm_strike:.2f}: Call={atm_call}  Put={atm_put}")

        logger.info("=" * 80 + "\n")
