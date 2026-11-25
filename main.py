
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


# ALPHA VANTAGE API FUNCTION
def get_stock_data(ticker, api_key):

    url = "https://www.alphavantage.co/query"

    parameters = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": api_key
    }

    #API KEY LOGIC FOR ALPHA VANTAGE API _____________________________________________________________________________________ Helped by ChatGPT!

    try:
        response = requests.get(url, params=parameters, timeout=30)
        response.raise_for_status()
        data = response.json()

        #In this try block, we attempt to make a GET request from the ticker via the API key. If it fails, we will give an error message. Else, we will go to next step.

    except requests.exceptions.RequestException as error:
        print("Unable to retrieve stock data:", error)
        return None #This is the error message we talked about if the request fails.

    if "Error Message" in data:
        print("Stock ticker not found in our database. More will be available in Developer Beta 2.0! Please try another ticker.")
        return None #This is a seperate error message, for if the data can't be found in Alpha Vantage's database.

    if "Note" in data or "Information" in data:
        print("Alpha Vantage API message:", data.get("Note") or data.get("Information"))
        return None #This block will display any notes or information from the Alpha Vantage API.

    quote = data.get("Global Quote") #This line will retrieve the global quote data about this ticker.

    if not quote or not quote.get("05. price"):
        print("Stock ticker not found in our database. More will be available in Developer Beta 2.0! Please try another ticker.")
        return None #If they can't get the quote, it will reveal this error.

    current_price = float(quote["05. price"]) #current_price will store the current price of one share from that stock.

    stocks = {
        ticker: {
            "price": current_price,
            "50-day moving average": None
        }
    }

    if ticker in stocks: #This is going to ask if the ticker is actually in Alpha Vantage's database.
        current_price = stocks[ticker]["price"] #It will reveal the dictionary of the stock price for one share
        moving_average = stocks[ticker]["50-day moving average"] #It will reveal the dictionary of the stock price in a 50-day average
    else:
        print("Stock ticker not found in our database. More will be available in Developer Beta 2.0! Please try another ticker.")
        return None #If all else fails, then the stock is not in the data base, revealing this error.

    return current_price, quote


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
