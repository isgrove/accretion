import csv

from .models import Trade, Profile, Portfolio
from accretion.secrets import IEX_KEY
import aiohttp
import asyncio
import time


IEX_URL = "https://cloud.iexapis.com/stable/"


# Takes user's trade data from csv file and adds it to the database
# TODO: Check for valid data before adding it to the database
def upload_portfolio(data_file, portfolio_id, is_adjusted):
    split_data = {}
    with open("media/" + data_file, newline='' ) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            if row[0] != "":
                symbol = row[3].upper()
                trade_date = row[1]
                effective_price = float(row[6])
                units = float(row[5])

                if not is_adjusted:
                    if symbol not in split_data:
                        splits = asyncio.run(get_splits_basic(symbol))
                        split_data[symbol] = splits
                    for split in split_data[symbol]:
                        ex_date = split["exDate"]
                        to_factor = split["toFactor"]
                        print(f"{ex_date} > {trade_date}")
                        if ex_date > trade_date:
                            print(f"Adjusting {symbol} for stock split...")
                            units *= to_factor
                            effective_price *= to_factor
                try:
                    Trade.objects.create(
                        trade_date = trade_date,
                        symbol = symbol,
                        effective_price = effective_price,
                        units = units,
                        brokerage_fee = row[7],
                        trade_type = row[4],
                        portfolio_id = portfolio_id
                    )
                except Exception as ex:
                    print(f"Error: {ex}")


async def get_price_only(symbol):
    async with aiohttp.ClientSession() as session:
        request_url = f"{IEX_URL}stock/{symbol}/price?token={IEX_KEY}"
        async with session.get(request_url) as resp:
            stock_price = await resp.json()
    return stock_price


async def get_splits_basic(symbol):
    async with aiohttp.ClientSession() as session:
        request_url = f"{IEX_URL}stock/{symbol}/splits?token={IEX_KEY}"
        async with session.get(request_url) as resp:
            stock_splits = await resp.json()
    return stock_splits


# Returns the user's trade data for their dashboard
# TODO: adjust for split and live stock price
def get_display_data(portfolio_id):
    print("Getting display data...")
    start = time.time()
    raw_trade_data = Trade.objects.filter(portfolio_id = portfolio_id)
    trade_data = {}
    for trade in raw_trade_data:
        if trade.trade_type == "S":
            trade.effective_price = -trade.effective_price 
            trade.units = -trade.units

        if trade.symbol in trade_data:
            trade_data[trade.symbol]["units"] += trade.units
            trade_data[trade.symbol]["value"] += trade.units * trade_data[trade.symbol]["current_price"]
        else:
            current_stock_price = asyncio.run(get_price_only(trade.symbol))
            data = {
                "current_price" : current_stock_price,
                "units" : trade.units,
                "value" : trade.units * current_stock_price,
            }
            trade_data[trade.symbol] = data

    end = time.time()
    total_time = end - start
    print(f"It took {total_time}s to get the data for {len(trade_data)} companies.")
    return trade_data