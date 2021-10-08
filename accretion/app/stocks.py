import csv

from .models import Trade


# Takes user's trade data from csv file and adds it to the database
# TODO: Check data before adding it to the database
def upload_portfolio(data_file, user_id):
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
                        trade_type = row[5],
                        portfolio_id= user_id
                    )
                except Exception as ex:
                    print(f"Error: {ex}")