import requests
import json
import pandas as pd
from datetime import datetime
from APVI_helper import (filter_timestamp, categorize_data_by_state,
                         calculate_total, calculate_average)


TOKEN = "add_your_token_here"


def fetch_api_data(url):
    response = requests.get(url)
    response.raise_for_status()  
    return response.json()


def process_data_frame(data, freq, field_name):
    df = pd.DataFrame.from_dict(data[freq], orient='index')
    df.reset_index(inplace=True)

    if freq == 'capacity':
        df['Date'] = datetime.now().strftime('%Y-%m-%d')  # Set to today's date
        df.columns = ['Postcode', 'Capacity_MW', 'Date']
        df = df[['Date', 'Postcode', 'Capacity_MW']]
    else:
        df = pd.melt(df, id_vars=['index'])
        df.columns = ['Postcode', 'Timestamp', field_name]
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        latest_timestamp = df['Timestamp'].max()
        df = df[df['Timestamp'] == latest_timestamp]

    return df


def api_data_extractor_today(token, field="all", postcode="all"):
    df_cap_all, df_per_all, df_out_all = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    try:
        # URL specifically for today's data
        url = f"https://pv-map.apvi.org.au/api/v2/2-digit/today.json?access_token={token}"
        print("Fetching data for today")
        data = fetch_api_data(url)

        if field in ["all", "capacity"]:  # Daily frequency
            df_cap = process_data_frame(data, 'capacity', 'Capacity_MW')
            if postcode != "all":
                df_cap = df_cap[df_cap['Postcode'].str.startswith(str(postcode))].copy()
            df_cap_all = pd.concat([df_cap_all, df_cap], ignore_index=True)

        if field in ["all", "performance"]:  # 15min frequency
            df_per = process_data_frame(data, 'performance', 'Performance')
            df_per_all = pd.concat([df_per_all, df_per], ignore_index=True)

        if field in ["all", "output"]:  # 15min frequency
            df_out = process_data_frame(data, 'output', 'Output')
            df_out_all = pd.concat([df_out_all, df_out], ignore_index=True)

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    cat_cap = categorize_data_by_state(df_cap_all)
    cat_per = categorize_data_by_state(df_per_all)
    cat_out = categorize_data_by_state(df_out_all)

    total_cap = calculate_total(cat_cap, 'Capacity_MW')
    average_per = calculate_average(cat_per, 'Performance', 'Timestamp')
    total_out = calculate_total(cat_out, 'Output', 'Timestamp')

    return [total_cap, average_per, total_out]


def main():
    token = TOKEN 

    try:
        data = api_data_extractor_today(token)
        print(data)
    except Exception as e:
        print(f"An error occurred when fetching and processing data: {e}")


if __name__ == "__main__":
    main()