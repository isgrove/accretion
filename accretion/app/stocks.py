import csv

from .models import Trade, Profile, Portfolio


# Takes user's trade data from csv file and adds it to the database
# TODO: Check for valid data before adding it to the database
def upload_portfolio(data_file, portfolio_id):
    with open("media/" + data_file, newline='' ) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            if row[0] != "":
                try:
                    Trade.objects.create(
                        trade_date = row[1],
                        symbol = row[3].upper(),
                        effective_price = float(row[6]),
                        units = float(row[5]),
                        brokerage_fee = float(row[7]),
                        trade_type = row[4],
                        portfolio_id = portfolio_id
                    )
                except Exception as ex:
                    print(f"Error: {ex}")


# Returns the user's trade data for their dashboard
# TODO: adjust for split and live stock price
def get_display_data(portfolio_id):
    raw_trade_data = Trade.objects.filter(portfolio_id = portfolio_id)
    trade_data = {}
    for trade in raw_trade_data:
        if trade.trade_type == "S":
            trade.effective_price = -trade.effective_price 
            trade.units = -trade.units

        if trade.symbol in trade_data:
            trade_data[trade.symbol]["units"] += trade.units
            trade_data[trade.symbol]["value"] += trade.units * trade.effective_price
        else:
            data = {
                "units" : trade.units,
                "value" :trade.units * trade.effective_price,
            }
            trade_data[trade.symbol] = data
            
    return trade_data