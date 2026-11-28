
import os
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from stocks import STOCKS 
from main import get_stock_data, API_KEY
import time

stock_cache = {
    "prices": {},
    "last_updated": 0
}

CACHE_DURATION = 60

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


oauth = OAuth(app)

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)
#This will route the user to the Google authentication page when they access the /auth/google URL. It checks for a valid authentication mode (signup or login) and stores it in the session before redirecting the user to Google's authentication page.
@app.route("/auth/google")
def google_login():
    mode = request.args.get("mode")

    if mode not in ["signup", "login"]:
        return "Invalid authentication mode", 400

    session["auth_mode"] = mode

    redirect_uri = url_for("google_callback", _external=True)

    return oauth.google.authorize_redirect(redirect_uri)

#This will route the user to the Google authentication callback URL after they have authenticated with Google. It retrieves the access token and user information, checks for required account information, and stores the user information in the session.
@app.route("/auth/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()

    userinfo = token.get("userinfo")

    if not userinfo:
        return "Google authentication failed", 400

    if not userinfo.get("sub") or not userinfo.get("email"):
        return "Google did not return the required account information", 400

    if userinfo.get("email_verified") is not True:
        return "Google email is not verified", 403

    mode = session.pop("auth_mode", None)

    if mode not in ["signup", "login"]:
        return "Invalid authentication session", 400

    session["google_user"] = {
        "sub": userinfo["sub"],
        "email": userinfo["email"],
        "name": userinfo.get("name")
    }

    return redirect(url_for("macrovania"))

#This will route the user to the signup page when they access the /signup URL. It renders the signup.html template.
@app.route("/signup")
def signup():
    return render_template("signup.html")

#This route will route the user to the login page when they access the /login URL. It renders the login.html template.
@app.route("/login")
def login():
    return render_template("login.html")


#This route is the home page of the application. It returns a welcome message when accessed.
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/macrovania")
def macrovania():
    return render_template("macrovania.html")

@app.route("/api/stocks")
def stock_catalog():
    return jsonify(STOCKS)

@app.route("/api/stock-prices")
def stock_prices():
    current_time = time.time()

    # Check whether cached prices are still fresh
    if current_time - stock_cache["last_updated"] < CACHE_DURATION:
        return jsonify(stock_cache["prices"])

    prices = {}

    for ticker in STOCKS:
        stock_data = get_stock_data(ticker, API_KEY)
        time.sleep(1.2)

        if stock_data is None:
            continue

        current_price, quote = stock_data
        previous_close = quote.get("previous_close")
        change = None
        change_percent = None

        if previous_close is not None:
            change = current_price - previous_close
            if previous_close != 0:
                change_percent = (change / previous_close) * 100

        prices[ticker] = {
            "price": current_price,
            "previous_close": previous_close,
            "change": change,
            "change_percent": change_percent,
            "latest_trading_day": quote.get("07. latest trading day")
        }

    # Save the newly retrieved prices
    stock_cache["prices"] = prices
    stock_cache["last_updated"] = time.time()

    return jsonify(prices)

if __name__ == "__main__":
    app.run(debug=True)
