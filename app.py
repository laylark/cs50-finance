import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def map_stock(stock):
    """Reformat stocks data"""
    return {
        'symbol': stock["symbol"],
        'stock_name': stock["stock_name"],
        'quantity': stock["quantity"],
        'price': lookup(stock["symbol"])["price"]
    }


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Select all data from database and store in stocks for current user
    stocks = db.execute("SELECT * FROM stocks WHERE user_id = ?", session["user_id"])

    # Update stock data with realtime price
    stocks_with_price = map(map_stock, stocks)

    # Select cash currently available for user
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    total = 0

    # Render index.html
    return render_template("index.html", stocks=stocks_with_price, cash=cash, total=total+cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST
    if request.method == "POST":

        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        # Check if symbol entered
        if not symbol:
            return apology("Missing symbol", 400)
        # Check if shares entered
        if not shares:
            return apology("Missing shares", 400)
        # Check if shares is non-integer
        regex = re.compile("^\d+$")
        if not re.fullmatch(regex, shares):
            return apology("Shares must be an integer", 400)
        # Set shares as int and check if positive value entered
        shares = int(shares)
        if shares <= 0:
            return apology("Value must be greater than or equal to 1.")

        # Lookup stock ticker and check if valid
        stock = lookup(symbol)

        if not stock:
            return apology("Invalid stock symbol", 400)

        # Multiply stock price by number of shares
        price = stock["price"] * shares
        # Select cash currently available for user
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Check if user can afford stock purchase
        if price > cash:
            return apology("Can't afford", 400)

        # Update transaction in database
        cash -= price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
        db.execute("INSERT INTO transactions (amount, symbol, quantity, user_id, unit_price, stock_name) VALUES(?, ?, ? , ?, ?, ?)",
            price, symbol, shares, session["user_id"], stock["price"], stock["name"])

        # Check if stock exists in stock table
        stocks_records = db.execute("SELECT * FROM stocks WHERE symbol = ?", symbol)

        if len(stocks_records) == 0:
            # Insert stock if doesn't exist
            db.execute("INSERT INTO stocks (symbol, stock_name, quantity, user_id) VALUES(?, ?, ?, ?)",
                symbol, stock["name"], shares, session["user_id"])
        else:
            # Otherwise update stock with quantity
            new_shares = stocks_records[0]["quantity"] + shares
            db.execute("UPDATE stocks SET quantity = ? WHERE id = ?", new_shares, stocks_records[0]["id"])

        # Re-direct user to home page
        flash("Bought!")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Select all data from database and store in transactions for current user
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", session["user_id"])

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST
    if request.method == "POST":

        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Missing symbol", 400)

        # Lookup stock ticker and check if valid
        stock = lookup(symbol)

        if not stock:
            return apology("Invalid stock symbol", 400)

        # Re-direct user to "quoted"
        return render_template("quoted.html", stock=stock)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Check for password requirements
        regex = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

        if not username:
            return apology("Provide a username", 400)
        if not password:
            return apology("Provide a password", 400)
        if not re.fullmatch(regex, password):
            return apology("Does not meet requirements", 400)
        if not confirmation:
            return apology("Provide a confirmation", 400)
        if password != confirmation:
            return apology("Passwords do not match!", 400)

        # Ensure username does not exist
        name_check = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Hash the user's password and enter new user in database
        if len(name_check) == 0:
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        else:
            return apology("Username unavailable", 400)

        # Redirect user to login form
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Select all data from database and store in transactions
    stocks = db.execute("SELECT * FROM stocks WHERE user_id = ?", session["user_id"])

    # User reached route via POST
    if request.method == "POST":

        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        # Check if symbol selected
        if not symbol:
            return apology("Missing symbol", 400)
        # Check if shares entered
        if not shares:
            return apology("Missing shares", 400)
        # Set shares to integer and check if positive value
        shares = int(shares)
        if shares <= 0:
            return apology("Value must be greater than or equal to 1.")
        # Select number of shares purchased by user
        shares_owned = db.execute("SELECT quantity, id FROM stocks WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
        # Check if user has enough shares to sell
        if shares > shares_owned[0]["quantity"]:
            return apology("Too many shares", 400)

        # Lookup current stock data at time of transaction
        stock = lookup(symbol)

        # Multiply current stock price by number of shares
        price = stock["price"] * shares
        # Select cash currently available for user
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Increment cash for transaction
        cash += price
        # Check if all shares were sold and update database
        if shares == shares_owned[0]["quantity"]:
            db.execute("DELETE FROM stocks WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
        else:
            # Otherwise update stock with quantity
            new_shares = shares_owned[0]["quantity"] - shares
            db.execute("UPDATE stocks SET quantity = ? WHERE id = ?", new_shares, shares_owned[0]["id"])

        # Update cash amoutn and insert transaction in database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
        db.execute("INSERT INTO transactions (amount, symbol, quantity, user_id, unit_price, stock_name) VALUES(?, ?, ? , ?, ?, ?)",
            price, symbol, (shares * -1), session["user_id"], stock["price"], stock["name"])

        # Re-direct user to home page
        flash("Sold!")
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("sell.html", stocks=stocks)