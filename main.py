
import math
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")


def get_stock_data(ticker, api_key):
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": API_SECRET
    }

    if not api_key or not API_SECRET:
        print("Alpaca API key or secret is missing from the environment.")
        return None

    try:
        response = requests.get(
            f"https://data.alpaca.markets/v2/stocks/{ticker}/trades/latest",
            headers=headers,
            params={"feed": "iex"},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as error:
        print("Unable to retrieve stock data:", error)
        return None

    trade = data.get("trade") if isinstance(data, dict) else None
    if not isinstance(trade, dict) or trade.get("p") is None:
        print("Unable to retrieve the latest trade for", ticker)
        return None

    trade_timestamp = trade.get("t")
    if not isinstance(trade_timestamp, str):
        print("Alpaca returned invalid trade data for", ticker)
        return None

    try:
        current_price = float(trade["p"])
        trade_time = datetime.fromisoformat(trade_timestamp.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        print("Alpaca returned invalid trade data for", ticker)
        return None

    if trade_time.tzinfo is None or not math.isfinite(current_price) or current_price < 0:
        print("Alpaca returned invalid trade data for", ticker)
        return None

    trade_date = trade_time.date()
    bars_parameters = {
        "timeframe": "1Day",
        "start": (trade_date - timedelta(days=14)).isoformat() + "T00:00:00Z",
        "end": (trade_date + timedelta(days=1)).isoformat() + "T00:00:00Z",
        "limit": 1000,
        "feed": "iex",
        "adjustment": "raw"
    }

    try:
        bars_response = requests.get(
            f"https://data.alpaca.markets/v2/stocks/{ticker}/bars",
            headers=headers,
            params=bars_parameters,
            timeout=30
        )
        bars_response.raise_for_status()
        bars_data = bars_response.json()
    except requests.exceptions.RequestException as error:
        print("Unable to retrieve previous closing price:", error)
        return None

    bars = bars_data.get("bars") if isinstance(bars_data, dict) else None
    if not isinstance(bars, list):
        print("Alpaca returned invalid daily bars for", ticker)
        bars = []

    parsed_bars = []
    for bar in bars:
        if not isinstance(bar, dict) or not isinstance(bar.get("t"), str):
            continue
        try:
            bar_timestamp = datetime.fromisoformat(bar["t"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if bar_timestamp.tzinfo is not None:
            parsed_bars.append((bar_timestamp, bar))

    trading_day = trade_date.isoformat()
    bar_timestamps = [
        timestamp for timestamp, _ in parsed_bars
        if timestamp <= trade_time
    ]
    if bar_timestamps:
        latest_bar_timestamp = max(bar_timestamps)
        if latest_bar_timestamp.hour in (4, 5):
            trading_day = (
                trade_time + timedelta(hours=-latest_bar_timestamp.hour)
            ).date().isoformat()

    prior_bars = [
        bar for _, bar in parsed_bars
        if bar["t"][:10] < trading_day
    ]
    previous_close = None
    if prior_bars:
        latest_prior_bar = max(prior_bars, key=lambda bar: bar["t"])
        if latest_prior_bar.get("c") is None:
            print("Alpaca did not return the previous close for", ticker)
        else:
            try:
                candidate_close = float(latest_prior_bar["c"])
                if math.isfinite(candidate_close) and candidate_close >= 0:
                    previous_close = candidate_close
                else:
                    print("Alpaca returned an invalid previous close for", ticker)
            except (TypeError, ValueError):
                print("Alpaca returned an invalid previous close for", ticker)

    quote = {
        "07. latest trading day": trading_day,
        "latest trading timestamp": trade_timestamp,
        "previous_close": previous_close
    }

    return current_price, quote

def run_macrovania():
    print("Welcome to Macrovania! A world of Wall Street with fake money! For now, this is the beta version of this. To find your ticker and result, please kindly input your stock ticker(eg. NVDA), and then we will return you the result! Thx :) -Vivaan(CEO of Macrovania):)")
    print()

    database = {} #This is a dictionary that will store the username and password pairs for the sign-up and log-in functionality.
    #For now, this is our temporary in-memory account book, so restarting Macrovania starts fresh.

    logged_in = False

    while True:

        lobby = input("Do you want to sign up or log in? (Type quit to exit): ").lower()

        if lobby == 'sign up':
            username = input("Please enter your desired username: ")

            if username in database:
                print("Username already exists. Please try another username.")
                continue

            password = input("Please enter your desired password: ")

            database[username] = {
                "password": password,
                "balance": 10000.00,
                "starting_balance": 10000.00,
                "holdings": {}
            }

            print(f"Sign up successful! Welcome, {username}! You have been granted a starting balance of $10,000 in paper money to trade with. Please note that this is a beta version. Thanks for your support! Please login to confirm your -Vivaan :D")

            continue

        elif lobby == 'log in':

            while True:
                username = input("Please enter your username: ")
                password = input("Please enter your password: ")

                if username in database and database[username]["password"] == password:
                    print(f"Log in successful! Welcome back, {username}!\n\n\n")
                    logged_in = True #a boolean variable used to track login status of loser. 
                    break

                else:
                    print("Invalid username or password. Please try again.")

            #The inner loop only ends after a successful login, so this break gets us out of the sign-in lobby.
            break

        elif lobby == 'quit':
            print("Thank you for visiting Macrovania!")
            break

        else:
            print("Invalid option. Please type sign up or log in.")
            continue


    #Data Checking Logic
    if logged_in: #Trying to see if the boolean, logged_in is true. 
        while True:

            server = input("What do you want to do? (Type 'check' to check your balance and holdings, 'trade' to trade stocks, 'check portfolio' to check your portfolio, or 'quit' to exit): ").lower()

            if server == 'check':
                balance = database[username]["balance"]
                holdings = database[username]["holdings"]

                print(f"\nYour current balance is: ${balance:,.2f}")
                print("Your current holdings:")
                if not holdings:
                    print("You have no holdings.")
                else:
                    for ticker, stock_info in holdings.items():
                        print(f"{ticker}: {stock_info['shares']} shares")
                print()
                continue

            elif server == 'trade':
                ticker = input("Please input your stock ticker(e.g. NVDA): ").upper()

                stock_data = get_stock_data(ticker, API_KEY)

                if stock_data is None:
                    print("Unable to retrieve stock data. Please try again later.")
                    continue

                current_price, quote = stock_data

                print()
                print(f"The current price for a share of {ticker} is ${current_price:,.2f}!") #Prints the stock price for one share of that ticker
                print(f"Latest trading day: {quote['07. latest trading day']}\n\n")

                # 50-day moving average comparison will be enabled
                # after we integrate historical stock data.

                buysell = input("Do you want to buy or sell this stock? (Type 'buy' or 'sell', or 'skip' to skip): ").lower() #Asks the user if they want to buy or sell
                if buysell == "buy":
                    shares = int(input("How many shares do you want to buy? (choose a number): ")) #Asks for amount of shares
                    new_balance = database[username]["balance"] - (shares * current_price) #Calculates the new balance AFTER the shares are bought
                    if new_balance < 0:
                        print("Insufficient funds to complete the purchase. Please try again with a lower number of shares or check your balance.")
                        continue
                    if new_balance >= 0:
                        #We only change the account after the user confirms, so a cancelled purchase costs nothing.
                        confirmation = input(f"You are being charged ${shares * current_price:,.2f} for {shares} shares of {ticker}. (yes/no): ").lower() #Asks the user to confirm the purchase
                        if confirmation == "yes":
                            database[username]["balance"] = new_balance #Updates the balance in the database

                            if ticker not in database[username]["holdings"]:
                                database[username]["holdings"][ticker] = {
                                    "shares": shares,
                                    "total_cost": shares * current_price
                                }
                            else:
                                database[username]["holdings"][ticker]["shares"] += shares
                                database[username]["holdings"][ticker]["total_cost"] += shares * current_price

                            print(f"You have successfully bought {shares} shares of {ticker}. Your new balance is ${new_balance:,.2f}.") #Prints the new balance after buying shares. ":,.2f" for a float with 2 decimal points.
                            continue
                        else:
                            print("Purchase cancelled.")
                            continue

            elif server == 'check portfolio':
                print(f"\nYour current balance is: ${database[username]['balance']:,.2f}")
                print("You currently hold the following stocks: ")

                portfolio_value = database[username]["balance"]
                total_cost = 0
                portfolio_prices = {}

                #Grab every holding's latest price first, so we don't calculate a portfolio with missing quotes.
                for ticker, stock_info in database[username]["holdings"].items():
                    stock_data = get_stock_data(ticker, API_KEY)

                    if stock_data is None:
                        print("Unable to retrieve all portfolio prices. Please try again later.")
                        break

                    current_price, quote = stock_data
                    portfolio_prices[ticker] = current_price

                #Python's for-else runs this only if the loop finished without a break; no partial portfolio totals!
                else:
                    for ticker, stock_info in database[username]["holdings"].items():
                        shares = stock_info["shares"]
                        purchase_cost = stock_info["total_cost"]
                        #This spreads what we paid across the shares we still hold: our average purchase price.
                        average_purchase_price = purchase_cost / shares
                        current_price = portfolio_prices[ticker]

                        current_market_value = current_price * shares
                        #The gain or loss is still unrealized: it compares today's value with our purchase cost.
                        unrealized_gain_loss = current_market_value - purchase_cost
                        #Turn that dollar change into a percentage of what we paid for this stock.
                        individual_return = (unrealized_gain_loss / purchase_cost) * 100

                        portfolio_value += current_market_value
                        total_cost += purchase_cost

                        print(f"{ticker}:")
                        print(f"* Number of shares: {shares}")
                        print(f"* Average Purchase price: ${average_purchase_price:,.2f}")
                        print(f"* Current market price: ${current_price:,.2f}")
                        print(f"* Current market value: ${current_market_value:,.2f}")
                        print(f"* Unrealized gain/loss: ${unrealized_gain_loss:+,.2f}")
                        #Line 220 calculates the gain/loss by subtracting the current price from the average purchase price, multiplying it by the no. of shares.
                        print(f"* Individual stock return: {individual_return:+.2f}%") #This will calculate the individual stock return of the stock in the portfolio.
                        #In depth summary of line 222: This calculates the individual stock return by subtracting the current market value from the total cost, dividing it by the total cost and multiplying it by 100
                        # * The formula that calculates the percentage of the stock return is current value - average purchase price, divided by the average purchase price, multiplies by 100

                    starting_balance = database[username]["starting_balance"]
                    #Our total includes cash left over plus current holding values; compare it with where we started.
                    overall_gain_loss = portfolio_value - starting_balance
                    overall_return = (overall_gain_loss / starting_balance) * 100

                    print("Total Portfolio Value: ${:,.2f}".format(portfolio_value)) #This will calculate the total portfolio value by adding the balance and the current market value of all holdings.
                    #Summary of line 224: This calculates the total value by adding the remaining balance + the current values of all holdings
                    print(f"Overall portfolio gain/loss: ${overall_gain_loss:+,.2f}")
                    print(f"Overall portfolio return: {overall_return:+.2f}%")
                    #Summary of line 226: This calculates the overall return by subtracting the portfolio value from the starting balance, dividing by the starting balance and multiplying it by 100

                continue

            elif server == 'quit':
                print("Thank you for visiting Macrovania!")
                break

            else:
                print("Invalid option. Please try again.")
                continue

if __name__ == "__main__":
    run_macrovania()