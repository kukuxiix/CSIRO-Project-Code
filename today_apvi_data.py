import requests
import json
import pandas as pd
from datetime import datetime
from APVI_helper import (filter_timestamp, categorize_data_by_state,
                         calculate_total, calculate_average)


def api_data_extractor_today(token, field="all", postcode="all"):
    df_cap_all = pd.DataFrame()
    df_per_all = pd.DataFrame()
    df_out_all = pd.DataFrame()

    try:
        #URL specifically for today's data
        url = f"https://pv-map.apvi.org.au/api/v2/2-digit/today.json?access_token={token}"
        response = requests.get(url)
        print("Fetching data for today")
        data = response.json()

        if field in ["all", "capacity"]:  #Daily frequency
            df_cap = pd.DataFrame.from_dict(data['capacity'], orient='index')
            df_cap.reset_index(inplace=True)
            df_cap['Date'] = datetime.now().strftime('%Y-%m-%d')  #Set to today's date
            df_cap.columns = ['Postcode', 'Capacity_MW', 'Date']
            df_cap = df_cap[['Date', 'Postcode', 'Capacity_MW']]
            if postcode != "all":
                df_cap = df_cap[df_cap['Postcode'].str.startswith(str(postcode))].copy()
            df_cap_all = pd.concat([df_cap_all, df_cap], ignore_index=True)

        if field in ["all", "performance"]:  #15min frequency
            df_per = pd.DataFrame.from_dict(data['performance'], orient='index')
            df_per.reset_index(inplace=True)
            df_per = pd.melt(df_per, id_vars=['index'])
            df_per.columns = ['Postcode', 'Timestamp', 'Performance']
            df_per['Timestamp'] = pd.to_datetime(df_per['Timestamp']) 
            latest_timestamp = df_per['Timestamp'].max()
            #Filter to only include the latest timestamp
            df_per = df_per[df_per['Timestamp'] == latest_timestamp]
            df_per_all = pd.concat([df_per_all, df_per], ignore_index=True)

        if field in ["all", "output"]:  # 15min frequency
            df_out = pd.DataFrame.from_dict(data['output'], orient='index')
            df_out.reset_index(inplace=True)
            df_out = pd.melt(df_out, id_vars=['index'])
            df_out.columns = ['Postcode', 'Timestamp', 'Output']
            df_out['Timestamp'] = pd.to_datetime(df_out['Timestamp']) 
            latest_timestamp = df_out['Timestamp'].max()
            # Filter to only include the latest timestamp
            df_out = df_out[df_out['Timestamp'] == latest_timestamp]
            df_out_all = pd.concat([df_out_all, df_out], ignore_index=True)

    except Exception as e:
        print(f"An exception occurred: {e}")

    cat_cap = categorize_data_by_state(df_cap_all)
    cat_per = categorize_data_by_state(df_per_all)
    cat_out = categorize_data_by_state(df_out_all)
    
    total_cap = calculate_total(cat_cap, 'Capacity_MW')
    average_per = calculate_average(cat_per, 'Performance', 'Timestamp')
    total_out = calculate_total(cat_out, 'Output', 'Timestamp')
    return [total_cap, average_per, total_out]

#Usage
token = "42d87a50153" 

#Get all data:
data = api_data_extractor_today(token)
[capacity, performance, output] = api_data_extractor_today(token)
print(data)