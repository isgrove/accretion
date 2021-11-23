import csv

from app.models import Trade, Profile, Portfolio
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
                        if ex_date > trade_date:
                            units *= to_factor
                            effective_price /= to_factor
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


# Method for getting stock close_data for get_portfolio_data()
def get_price_tasks(session, symbols):
    tasks = []
    for symbol in symbols:
        request_url = f"{IEX_URL}stock/{symbol['symbol']}/previous?token={IEX_KEY}"
        tasks.append(session.get(request_url, ssl=False))
    return tasks


# Gets all of the data for the portfolio page
async def get_portfolio_data(symbols, raw_trade_data):
    start = time.time()
    results = []
    close_data = {}
    open_data = {}

    session = aiohttp.ClientSession()
    tasks = get_price_tasks(session, symbols)
    responses = await asyncio.gather(*tasks)

    for response in responses:
        results.append(await response.json())
    await session.close()

    for x in results:
        close_data[x["symbol"]] = x["close"]
        open_data[x["symbol"]] = x["open"]
    trade_data = {}
    for trade in raw_trade_data:
        if trade.trade_type == "S":
            trade.effective_price = -trade.effective_price 
            trade.units = -trade.units

        if trade.symbol in trade_data:
            trade_data[trade.symbol]["units"] += trade.units
            trade_data[trade.symbol]["value"] += trade.units * trade_data[trade.symbol]["close"]
            trade_data[trade.symbol]["purchase_price"] += trade.units * trade.effective_price
        else:
            close_price = close_data[trade.symbol]
            open_price = open_data[trade.symbol]
            data = {
                "close" : close_price,
                "open" : open_price,
                "purchase_price" : trade.units * trade.effective_price,
                "units" : trade.units,
                "value" : trade.units * close_price,
            }
            trade_data[trade.symbol] = data

    end = time.time()
    total_time = end - start
    #TODO: Send alert (via Telegram?) api call takes >10s
    return trade_data


#https://cloud.iexapis.com/stable/stock/twtr/chart/1y?token=pk_0d4b88face5f434b9f2e25c8d3b65f9e

def get_chart_tasks(session, symbols, range):
    tasks = []
    for symbol in symbols:
        request_url = f"{IEX_URL}stock/{symbol['symbol']}/chart/{range}?token={IEX_KEY}"
        tasks.append(session.get(request_url, ssl=False))
    return tasks


# Gets all of the data for the portfolio page
async def get_portfolio_data_1y(symbols, raw_trade_data):
    start = time.time()
    results = []

    session = aiohttp.ClientSession()
    tasks = get_chart_tasks(session, symbols, "1y")
    responses = await asyncio.gather(*tasks)

    for response in responses:
        results.append(await response.json())
    await session.close()

    trade_data = {}
    for result in results:
        trade_data[result[0]["key"]] = [ele for ele in reversed(result)]

    end = time.time()
    total_time = end - start
    print("Request took " + str(total_time) + " seconds.")
    return trade_data