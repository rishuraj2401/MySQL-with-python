# import pandas as pd
# import yfinance as yf

# # Define the ticker symbol of the company
# ticker = "AAPL"  # Replace with the desired ticker symbol

# # Set the start and end dates for the historical data
# start_date = "2023-01-01"
# end_date = "2023-12-31"

# # Fetch the historical stock data using Yahoo Finance API
# data = yf.download(ticker, start=start_date, end=end_date)

# # Save the data to a CSV file
# data.to_csv(f"{ticker}_stock_data.csv")

# # Read the data from a CSV file or modify it accordingly if already in a dataframe
# data = pd.read_csv(f"{ticker}_stock_data.csv")

# # Calculate 50-day Moving Average
# data['50-day MA'] = data['Close'].rolling(window=50).mean()
# print(data['50-day MA'])

# # Calculate RSI (14-day)
# delta = data['Close'].diff()
# gain = delta.where(delta > 0, 0)
# loss = -delta.where(delta < 0, 0)
# avg_gain = gain.rolling(window=14).mean()
# avg_loss = loss.rolling(window=14).mean()
# rs = avg_gain / avg_loss
# data['RSI'] = 100 - (100 / (1 + rs))

# # Calculate MACD (12-day, 26-day, 9-day)
# data['12-day EMA'] = data['Close'].ewm(span=12, adjust=False).mean()
# data['26-day EMA'] = data['Close'].ewm(span=26, adjust=False).mean()
# data['MACD Line'] = data['12-day EMA'] - data['26-day EMA']
# data['Signal Line'] = data['MACD Line'].ewm(span=9, adjust=False).mean()
# data['Histogram'] = data['MACD Line'] - data['Signal Line']

# # Save the modified dataframe to a new CSV file
# data.to_csv('modified_data.csv', index=False)
# data.head()

import yfinance as yf
import mysql.connector
import numpy as np
import config

# Define the ticker symbol of the company
ticker = "AAPL"  # Replace with the desired ticker symbol

# Set the start and end dates for the historical data
start_date = "2023-01-01"
end_date = "2023-12-31"

# Fetch the historical stock data using Yahoo Finance API
data = yf.download(ticker, start=start_date, end=end_date)

data['50-day MA'] = data['Close'].rolling(window=50).mean()

# Calculate RSI (14-day)
delta = data['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
data['RSI'] = 100 - (100 / (1 + rs))

# Calculate MACD (12-day, 26-day, 9-day)
data['12-day EMA'] = data['Close'].ewm(span=12, adjust=False).mean()
data['26-day EMA'] = data['Close'].ewm(span=26, adjust=False).mean()
data['MACD Line'] = data['12-day EMA'] - data['26-day EMA']
data['Signal Line'] = data['MACD Line'].ewm(span=9, adjust=False).mean()
data['Histogram'] = data['MACD Line'] - data['Signal Line']

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=config.password,
    database="stocks"
)

# Create a cursor object to execute SQL queries
cursor = db.cursor()

# Create a table to store the stock data
create_table_query = """
CREATE TABLE IF NOT EXISTS stock_data (
    Date DATE PRIMARY KEY,
    Open FLOAT,
    High FLOAT,
    Low FLOAT,
    Close FLOAT,
    Adj_Close FLOAT,
    Volume INT,
    `50-day MA` FLOAT,
    RSI FLOAT,
    `12-day EMA` FLOAT,
    `26-day EMA` FLOAT,
    `MACD Line` FLOAT,
    `Signal Line` FLOAT,
    Histogram FLOAT
)
"""
cursor.execute(create_table_query)

# Insert the stock data into the MySQL table
for index, row in data.iterrows():
    if np.isnan(row['50-day MA']):
        row['50-day MA'] = 0

    if np.isnan(row['RSI']):
        row['RSI'] = 0

    insert_query = """
    INSERT INTO stock_data (Date, Open, High, Low, Close, Adj_Close, Volume, `50-day MA`, RSI, `12-day EMA`, `26-day EMA`, `MACD Line`, `Signal Line`, Histogram)
    VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)
    """
    values = (index.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'], row['50-day MA'], row['RSI'], row['12-day EMA'], row['26-day EMA'], row['MACD Line'], row['Signal Line'], row['Histogram'])
    cursor.execute(insert_query, values)

# Commit the changes to the database
db.commit()

# Close the cursor and database connection
cursor.close()
db.close()