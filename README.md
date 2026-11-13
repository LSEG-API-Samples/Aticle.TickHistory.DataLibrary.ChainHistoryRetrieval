# Getting Historical Chain Constituents with LSEG Tick History REST API and LSEG Data Library for Python

The [LSEG Data Library for Python](https://developers.lseg.com/en/api-catalog/lseg-data-platform/lseg-data-library-for-python) `Chain` object returns a chain's constituents, which you can then use with `get_data` and `get_history`. But some bonds chains change its constituent over time because exchanges periodically update which bonds meet the  maturity and coupon criteria for delivery. For instance, newly issued Treasuries are added while older bonds that have fallen below the minimum remaining maturity are removed. 

Examples:
- **0#TYc1=DLV**: CBoT 10-Year US Treasury Note
- **0#FGBMc1=DLV**: Eurex Euro-Bobl (5-year German Govt Bond)
- **0#JGBc1=DLV**: Osaka Exchange 10-Year Japanese Government Bond

See [README.md](./README.md) for more about these chain rules.

The `Chain` object returns **current constituents** because it gets data from the Real-Time platform. To resolve constituents for a specific time, use the [LSEG Tick History REST API](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api), which supports current and past constituents, including inactive, historical-only instruments. 

Once you get the constituents of that specific time from the Tick History, you can then retrieve their historical data with Tick History, the Data Library, or another LSEG API such as [Data Platform APIs (RDP)](https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/refinitiv-data-platform-apis).

#### Note

You can also use the Tick History REST API for the entire workflow. See the [Tick History REST API tutorials](https://developers.lseg.com/en/api-catalog/refinitiv-tick-history/refinitiv-tick-history-rth-rest-api/tutorials#rest-api-tutorials-introduction) for details. This example is for developers who use the Data Library as their primary API.

[tbd]