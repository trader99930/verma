import requests
import pandas as pd
import time
import os  # Import os for clearing the console
from tabulate import tabulate

# URL for fetching NIFTY option chain data
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
    "Accept-Language": "en,gu;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
}

# Create a session to persist cookies across requests
session = requests.Session()

# Function to import data from the NSE API
def importdata():
    try:
        # Fetch the data
        request = session.get(url, headers=headers)
        cookies = dict(request.cookies)

        # Fetch data again using the cookies
        response = session.get(url, headers=headers, cookies=cookies).json()

        # Get spot price
        spot_price = response.get("records", {}).get("underlyingValue", None)

        # Extract records of option chain
        records = response.get("records", {}).get("data", [])

        # Get the expiry dates list
        expiry_dates = response.get("records", {}).get("expiryDates", [])

        # Prepare lists for option data
        ce_data = []
        pe_data = []

        for record in records:
            # Always add the strike price; add CE and PE data if available
            strike_price = record.get("strikePrice", None)
            ce = record.get("CE", None)
            pe = record.get("PE", None)

            ce_data.append(
                [
                    record.get("expiryDate"),
                    strike_price,
                    ce.get("openInterest", 0) if ce else 0,
                    ce.get("changeinOpenInterest", 0) if ce else 0,
                    ce.get("totalTradedVolume", 0) if ce else 0,
                    ce.get("lastPrice", 0) if ce else 0,
                    ce.get("impliedVolatility", 0) if ce else 0,
                    ce.get("bidQty", 0) if ce else 0,
                    ce.get("bidprice", 0) if ce else 0,
                    ce.get("askPrice", 0) if ce else 0,
                    ce.get("askQty", 0) if ce else 0,
                ]
            )

            pe_data.append(
                [
                    record.get("expiryDate"),
                    strike_price,
                    pe.get("openInterest", 0) if pe else 0,
                    pe.get("changeinOpenInterest", 0) if pe else 0,
                    pe.get("totalTradedVolume", 0) if pe else 0,
                    pe.get("lastPrice", 0) if pe else 0,
                    pe.get("impliedVolatility", 0) if pe else 0,
                    pe.get("bidQty", 0) if pe else 0,
                    pe.get("bidprice", 0) if pe else 0,
                    pe.get("askPrice", 0) if pe else 0,
                    pe.get("askQty", 0) if pe else 0,
                ]
            )

        # Convert lists to DataFrames with appropriate column names
        ce_df = pd.DataFrame(
            ce_data,
            columns=[
                "Expiry Date",
                "Strike Price",
                "CE OI",
                "CE Change in OI",
                "CE Volume",
                "CE LTP",
                "CE IV",
                "CE Bid Qty",
                "CE Bid Price",
                "CE Ask Price",
                "CE Ask Qty",
            ],
        )

        pe_df = pd.DataFrame(
            pe_data,
            columns=[
                "Expiry Date",
                "Strike Price",
                "PE OI",
                "PE Change in OI",
                "PE Volume",
                "PE LTP",
                "PE IV",
                "PE Bid Qty",
                "PE Bid Price",
                "PE Ask Price",
                "PE Ask Qty",
            ],
        )

        # Merge the DataFrames on 'Expiry Date' and 'Strike Price'
        merged_df = pd.merge(
            ce_df, pe_df, on=["Expiry Date", "Strike Price"], how="outer"
        ).sort_values(by=["Expiry Date", "Strike Price"])

        # Replace NaN with 0
        merged_df = merged_df.fillna(0)

        return merged_df, spot_price, expiry_dates
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None


# Main loop to fetch and display data
print("Fetching NIFTY Option Chain Data...")

while True:
    merged_df, spot_price, expiry_dates = importdata()

    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")  # Clear the console output

    if merged_df is not None:
        print("\nNIFTY OPTION CHAIN DATA")
        print(f"Spot Price: {spot_price}\n")

        if expiry_dates:
            # Use the latest expiry date from the list
            selected_expiry = expiry_dates[0]

            # Filter data for the selected expiry
            selected_df = merged_df[merged_df["Expiry Date"] == selected_expiry]

            # Use pandas to set column width for better readability
            pd.set_option("display.max_columns", None)
            pd.set_option("display.width", 1000)

            # Display filtered data for the selected expiry date
            table = tabulate(selected_df, headers="keys", tablefmt="psql", showindex=False)
            print(f"\nOption Chain Data for Expiry: {selected_expiry}\n")
            print(table)
        else:
            print("No expiry dates available.")

    else:
        print("Failed to fetch data.")

    # Wait for 5 seconds before fetching data again
    time.sleep(5)
