#TODO: Sepeate these methods into different files

import csv

from app.models import Trade, Profile, Portfolio
from accretion.secrets import IEX_KEY
import aiohttp
import asyncio
import time
from datetime import datetime
from pytz import timezone


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


# Check if it is between 4:15pm (Mon - Fri) and 4am (Tue - Sat) ET time.  
# Returns true if it is between that time
# Returns false if its not between that time
def check_time():
    time_valid = False

    tz = timezone('EST')
    time = datetime.now(tz)

    start_time = datetime.strptime("15:15:00", "%H:%M:%S").time()
    end_time = datetime.strptime("03:00:00", "%H:%M:%S").time()
    day = time.today().weekday()

    if (day >= 0 and day <=5):
        if (day == 0 and time.time() <= end_time):
            print("invalid time")
        elif (day == 5 and time.time() >= start_time):
            print("invalid time")
        elif (time.time() >= start_time or time.time() <= end_time):
            time_valid = True
    return day, time.time(), time_valid


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
        results.append(await response.json(content_type=None))
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


def get_ohlc_tasks(session, symbols):
    tasks = []
    for symbol in symbols:
        request_url = f"{IEX_URL}stock/{symbol['symbol']}/ohlc?token={IEX_KEY}"
        tasks.append(session.get(request_url, ssl=False))
    return tasks

# Gets all of the data for the portfolio page
# TODO: Check if chart data contains todays data, if not check OHLC for data. If neither have today's data, ignore.
async def get_portfolio_data_1y(symbols, raw_trade_data):
    start = time.time()
    results = []
    ohlc_results = []

    session = aiohttp.ClientSession()
    tasks = get_chart_tasks(session, symbols, "1y")
    responses = await asyncio.gather(*tasks)

    for response in responses:
        results.append(await response.json(content_type=None))
    await session.close()

    # ohlc_data = {}
    # if time_valid:
    #      for result in ohlc_results:
    #         ohlc_data[result["symbol"]] = result

    # TODO: Get OHLC data if chart data does not contain today's data.
    # tz = timezone('EST')
    # ny_time = datetime.now(tz)
    # data_date = results[0][len(results[0])-1]["date"]
    # if ny_time.time() >= datetime.strptime("15:15:00", "%H:%M:%S").time():
    #     if data_date != ny_time:
    #             print("no data")
    #             session = aiohttp.ClientSession()
    #             tasks = get_ohlc_tasks(session, symbols)
    #             responses = await asyncio.gather(*tasks)

    #             for response in responses:
    #                 ohlc_results.append(await response.json(content_type=None))
    #             await session.close()

    trade_data = {}

    counter = 0
    for result in results:
        trade_data[result[0]["key"]] = [ele for ele in reversed(result)]
        counter += 1

    formatted_trade_data = {}

    for trade in raw_trade_data:
        trade_dict = {
            "symbol" : trade.symbol,
            "purchasePrice" : trade.effective_price,
            "units" : trade.units,
            "date" : trade.trade_date,
            "tradeType" : trade.trade_type
        }

        if trade.symbol in formatted_trade_data:
            formatted_trade_data[trade.symbol].append(trade_dict)
        else:
            formatted_trade_data[trade.symbol] = [trade_dict]

    end = time.time()
    total_time = end - start
    print("Request took " + str(total_time) + " seconds.")
    # trade_data["ohlc"] = ohlc_data
    # trade_data["ohlc_raw"] = ohlc_results
    return {"chartData" : trade_data, "tradeData" : formatted_trade_data}