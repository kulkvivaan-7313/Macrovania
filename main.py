
import os
import requests
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

print("Welcome to Macrovania! A world of Wall Street with fake money! For now, this is the beta version of this. To find your ticker and result, please kindly input your stock ticker(eg. NVDA), and then we will return you the result! Thx :) -Vivaan(CEO of Macrovania):)")
print()

ticker = input("Please input your stock ticker(e.g. NVDA): ").upper()

url = "https://www.alphavantage.co/query"

parameters = {
    "function": "GLOBAL_QUOTE",
    "symbol": ticker,
    "apikey": API_KEY
}

#API KEY LOGIC FOR ALPHA VANTAGE API _____________________________________________________________________________________ Helped by ChatGPT! 

try:
    response = requests.get(url, params=parameters, timeout=30)
    response.raise_for_status()
    data = response.json()

    #In this try block, we attempt to make a GET request from the ticker via the API key. If it fails, we will give an error message. Else, we will go to next step. 

except requests.exceptions.RequestException as error:
    print("Unable to retrieve stock data:", error)
    exit() #This is the error message we talked about if the request fails. 

if "Error Message" in data:
    print("Stock ticker not found in our database. More will be available in Developer Beta 2.0! Please try another ticker.")
    exit() #This is a seperate error message, for if the data can't be found in Alpha Vantage's database. 

if "Note" in data or "Information" in data:
    print("Alpha Vantage API message:", data.get("Note") or data.get("Information"))
    exit() #This block will display any notes or information from the Alpha Vantage API.

quote = data.get("Global Quote") #This line will retrieve the global quote data about this ticker. 

if not quote or not quote.get("05. price"):
    print("Stock ticker not found in our database. More will be available in Developer Beta 2.0! Please try another ticker.")
    exit() #If they can't get the quote, it will reveal this error message. 

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
    exit() #If all else fails, then the stock is not in the data base, revealing this error. 

print()
print(f"The current price for a share of {ticker} is ${current_price:,.2f}!") #Prints the stock price for one share of that ticker
print(f"Latest trading day: {quote['07. latest trading day']}") 

# 50-day moving average comparison will be enabled
# after we integrate historical stock data.
