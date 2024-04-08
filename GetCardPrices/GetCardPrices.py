import json
import requests
import psycopg2
from datetime import datetime, timedelta
import time

def GetCardPrices():
    string_to_list = {
        "Unlimited Edition Normal": ["U", "S"],
        "Unlimited Edition Rainbow Foil": ["U", "R"],
        "1st Edition Normal": ["F", "S"],
        "1st Edition Rainbow Foil": ["F", "R"],
        "1st Edition Cold Foil": ["F", "C"],
        "Normal": ["N", "S"],
        "Rainbow Foil": ["N", "R"],
        "Cold Foil": ["N", "C"]
    }

    # Connect to your PostgreSQL database
    conn = psycopg2.connect(
        dbname="FaB_Cards",
        user="",
        password="",
        host="",
        port=""
    )

    # Create a cursor object using the connection
    cursor = conn.cursor()

    # Read all dates from the file
    with open(r"GetCardPrices\recent_dates.txt", "r") as file:
        dates = file.readlines()
        # Remove trailing newline characters and convert strings to datetime objects
        dates = [datetime.strptime(date.strip(), "%Y-%m-%d %H:%M:%S") for date in dates]

    # Get the most recent date
    if dates:
        recent_date = max(dates)
    else:
        # If the file is empty or does not exist, use a default recent date
        recent_date = datetime.now() - timedelta(days=365)

    # Get the current date and time
    current_date = datetime.now()

    # Open the file containing TCGPlayer product IDs
    with open(r"GetCardPrices\tcgplayer_product_ids.txt", "r") as file:
        for tcgID in file:
            tcgID = tcgID.strip()  # Remove leading/trailing whitespace

            # Define the URL for fetching sales data
            url = f'https://mpapi.tcgplayer.com/v2/product/{tcgID}/latestsales'

            offset = 0  # Initialize offset

            while True:
                # Define the post object with initial offset
                post = {
                    'limit': 25,
                    'listingType': 'All',
                    'offset': offset
                }

                # Serialize the post object to JSON
                payload = json.dumps(post)

                # Make the POST request with the correct payload
                response = requests.post(url, data=payload, headers={"Content-Type": "application/json"})

                try:
                    data = response.json()  # Try parsing response as JSON
                except json.decoder.JSONDecodeError:
                    print(f"Error decoding JSON response for tcgID: {tcgID}")
                    print(response.text)  # Print response content for debugging purposes
                    time.sleep(5)  # Wait for 5 seconds
                    # Retry the request for the same tcgID
                    continue

                total_results = data['totalResults']

                for sale in data['data']:
                    #order_date_str = sale['orderDate'].split('.')[0]  # Remove milliseconds
                    order_date_str = sale['orderDate'].split('.')[0].replace("+00:00", "")
                    order_date = datetime.strptime(order_date_str, "%Y-%m-%dT%H:%M:%S")  # Convert to datetime object


                    # Check if order date is after the most recent date
                    if order_date > recent_date:
                        variant = sale['variant']
                        purchase_price = sale['purchasePrice']

                        # Assuming the edition and foiling information is part of the variant string
                        edition, foiling = string_to_list.get(variant, [None, None])

                        # Convert order_date to string with only date (day, month, year)
                        order_date_dateonly_str = order_date.strftime("%Y-%m-%d")

                        # Construct the SQL query to find the card_printing_id
                        query = """
                            SELECT unique_id
                            FROM card_printings
                            WHERE tcgplayer_product_id = %s
                            AND edition = %s
                            AND foiling = %s
                        """

                        # Execute the SQL query
                        cursor.execute(query, (tcgID, edition, foiling))

                        # Fetch the result
                        result = cursor.fetchone()

                        if result:
                            card_printing_id = result[0]  # Retrieve the unique_id

                            # Insert the purchase price into card_prices table
                            insert_price_query = """
                                INSERT INTO card_prices (price, date)
                                VALUES (%s, %s)
                                RETURNING id
                            """
                            cursor.execute(insert_price_query, (purchase_price, order_date_dateonly_str))
                            price_id = cursor.fetchone()[0]

                            # Insert the relationship between card printing and price into card_printing_prices table
                            insert_card_printing_price_query = """
                                INSERT INTO card_printing_prices (card_printing_id, card_price_id)
                                VALUES (%s, %s)
                            """
                            cursor.execute(insert_card_printing_price_query, (card_printing_id, price_id))

                            # Commit the transaction
                            conn.commit()
                    else:
                        # If the order date is not after the most recent date, break the loop
                        break

                # Break the loop if all data has been fetched or if order date not after the most recent date
                if offset >= total_results - 25 or order_date <= recent_date:
                    print(tcgID)
                    break

                # Increment offset by 25 for the next request
                offset += 25

    # Append the current date and time to the file
    with open(r"GetCardPrices\recent_dates.txt", "a") as file:
        file.write(current_date.strftime("%Y-%m-%d %H:%M:%S") + "\n")

    # Close the cursor and connection
    cursor.close()
    conn.close()

GetCardPrices()