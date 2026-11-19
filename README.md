# Getting Historical Chain Constituents with LSEG Tick History REST API and LSEG Data Library for Python

- Last Updated: November 2026
- Language: Python
- Prerequisites: DataScope Select credentials and permission for the Tick History REST API; Workspace or Data Platform access for the LSEG Data Library for Python

## Overview

A chain RIC identifies a group of related instrument names, not their values. For example, a chain may contain the constituents of a market index like the Dow Jones or the list of strike prices on a particular option contract. 

Chain membership can change over time as instruments are listed or delisted. Bond chains are one example: exchanges periodically update which bonds meet the maturity and coupon criteria for delivery. Newly issued Treasuries may be added, while bonds that fall below the minimum remaining maturity may be removed.

Examples:
- **0#TYc1=DLV**: CBoT 10-Year US Treasury Note
- **0#FGBMc1=DLV**: Eurex Euro-Bobl (5-year German Govt Bond)
- **0#JGBc1=DLV**: Osaka Exchange 10-Year Japanese Government Bond

The [LSEG Data Library for Python](https://developers.lseg.com/en/api-catalog/lseg-data-platform/lseg-data-library-for-python) offers a convenient way to expand a chain using its `Chain` object. The object returns a chain's *current constituents which you can then use with the library's other methods. 

The question is, how can we get the chain constituents for a specific time?

## The Solution: LSEG Tick History - REST API.

The [LSEG Tick History - REST API](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api) provides access to more than 30 years of historical intraday market data, including trades, quotes and market depth across 580+ venues and contributors through HTTP REST API. Its `/Search/HistoricalChainResolution` endpoint lets developers resolve current and past chain constituents, including inactive, historical-only instruments.

- [Tutorial 15: Historical Chain Constituents Search](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api/tutorials#rest-api-tutorial-15-historical-chain-constituents-search)

Once you have the constituents for the period you need, you can retrieve their historical data using Tick History, the Data Library, or another LSEG API, such as the [Data Platform APIs (RDP)](https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis).

#### Note

The Tick History REST API can also be used for the entire workflow. See the [Tick History REST API tutorials](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api/tutorials#rest-api-tutorials-introduction) for details. This example focuses on developers who use the Data Library as their primary API.

[tbd]