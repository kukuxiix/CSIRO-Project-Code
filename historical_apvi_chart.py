import requests
import pandas as pd
from datetime import datetime, timedelta
from APVI_helper import (filter_timestamp, categorize_data_by_state,
                         calculate_total, calculate_average)
import plotly.graph_objects as go
import streamlit as st
from concurrent.futures import ThreadPoolExecutor


TOKEN = "42d87a50153"
#Set to yesterday since we extract 12pm's data and today's might be unavaliable 
yesterday = datetime.now() - timedelta(days=1)
END_DATE = yesterday.strftime('%Y-%m-%d')
START_DATE = "2015-02-01"


@st.cache(ttl=3600)  #Cache for 1 hour
def fetch_data_for_date(date, token):
    url = f"https://pv-map.apvi.org.au/api/v2/2-digit/{date}.json"
    params = {'access_token': token}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data for {date}")
        return None

def process_data(data, date, field, postcode):
    df_list = []
    if field in ["all", "capacity"]:
        df_cap = pd.DataFrame.from_dict(data['capacity'], orient='index')
        df_cap.reset_index(inplace=True)
        df_cap['Date'] = date
        df_cap.columns = ['Postcode', 'Capacity_MW', 'Date']
        df_cap = df_cap[['Date', 'Postcode', 'Capacity_MW']]
        if postcode != "all":
            df_cap = df_cap[df_cap['Postcode'].str.startswith(str(postcode))].copy()
        df_list.append(df_cap)

    if field in ["all", "performance"]:
        df_per = pd.DataFrame.from_dict(data['performance'], orient='index')
        df_per.reset_index(inplace=True)
        df_per = pd.melt(df_per, id_vars=['index'])
        df_per.columns = ['Postcode', 'Timestamp', 'Performance']
        df_per = filter_timestamp(df_per)
        df_per['Date'] = pd.to_datetime(df_per['Timestamp']).dt.strftime('%Y-%m-%d')
        df_per.drop('Timestamp', axis=1, inplace=True)
        if postcode != "all":
            df_per = df_per[df_per['Postcode'].str.startswith(str(postcode))].copy()
        df_list.append(df_per)

    if field in ["all", "output"]:
        df_out = pd.DataFrame.from_dict(data['output'], orient='index')
        df_out.reset_index(inplace=True)
        df_out = pd.melt(df_out, id_vars=['index'])
        df_out.columns = ['Postcode', 'Timestamp', 'Output']
        df_out = filter_timestamp(df_out)
        df_out['Date'] = pd.to_datetime(df_out['Timestamp']).dt.strftime('%Y-%m-%d')
        df_out.drop('Timestamp', axis=1, inplace=True)
        if postcode != "all":
            df_out = df_out[df_out['Postcode'].str.startswith(str(postcode))].copy()
        df_list.append(df_out)
    return df_list


def api_data_extractor_historical(start_date, end_date, token, frequency="Y", field="all", postcode="all"):
    date_range = pd.date_range(start=start_date, end=end_date, freq=frequency)
    dates_list = [date.strftime('%Y-%m-%d') for date in date_range]

    #Append 'yesterday' only if frequency is 'Y' and it's not in the list
    if frequency == "Y" and END_DATE not in dates_list:
        dates_list.append(END_DATE)

    df_cap_all = []
    df_per_all = []
    df_out_all = []

    #Fetch data using ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda date: fetch_data_for_date(date, token), dates_list)

    for date, data in zip(dates_list, results):
        if data:
            dfs = process_data(data, date, field, postcode)
            if dfs[0] is not None: df_cap_all.append(dfs[0])  
            if dfs[1] is not None: df_per_all.append(dfs[1])  
            if dfs[2] is not None: df_out_all.append(dfs[2])  

    df_cap_all = pd.concat(df_cap_all, ignore_index=True) if df_cap_all else pd.DataFrame()
    df_per_all = pd.concat(df_per_all, ignore_index=True) if df_per_all else pd.DataFrame()
    df_out_all = pd.concat(df_out_all, ignore_index=True) if df_out_all else pd.DataFrame()

    #Group data from same stae
    cat_cap = categorize_data_by_state(df_cap_all)
    cat_per = categorize_data_by_state(df_per_all)
    cat_out = categorize_data_by_state(df_out_all)

    #Find the total/ average
    total_cap = calculate_total(cat_cap, 'Capacity_MW')
    average_per = calculate_average(cat_per, 'Performance')
    total_out = calculate_total(cat_out, 'Output')
    return [total_cap, average_per, total_out]


def plot_data(df, title, y_col_name):
    fig = go.Figure()
    for state in df['State'].unique():
        subset = df[df['State'] == state]
        dates = subset['Date']
        values = subset[y_col_name]
        fig.add_trace(go.Scatter(x=dates, 
                                 y=values, 
                                 mode='lines', 
                                 name=state))
    fig.update_layout(title=f"{title} Historical Data",
                      xaxis_title='Date',
                      yaxis_title=title)
    # fig.show()
    return fig

# Only displays plots (quicker way)
# def main():
#     # Streamlit UI Elements (can be extended for more interactivity)
#     st.title('APVI Historical Data Visualization')
    
#     # Extract data
#     data = api_data_extractor_historical(START_DATE, END_DATE, TOKEN)
    
#     # Display visualizations in Streamlit
#     st.plotly_chart(plot_data(data[0], 'Capacity', 'Total_Capacity_MW'))
#     st.plotly_chart(plot_data(data[1], 'Performance', 'Average_Performance'))
#     st.plotly_chart(plot_data(data[2], 'Output', 'Total_Output'))

# A more interactive version (but slower)

def main():
    st.markdown("## PV Trend")
    #Define frequencies as a dictionary
    frequencies = {
        'Weekly': 'W',
        'Daily': 'D',
        'Year': 'Y'
    }

    #Ensure start date does not go before 2015 and end date does not go over today
    MIN_START_DATE = datetime.strptime('2015-01-01', '%Y-%m-%d')
    MAX_END_DATE = datetime.now()

    #Set the earliest selectable date
    start_date = st.date_input('Start date', datetime.strptime(START_DATE, '%Y-%m-%d'), min_value=MIN_START_DATE, max_value=MAX_END_DATE)
    end_date = st.date_input('End date', MAX_END_DATE, min_value=MIN_START_DATE, max_value=MAX_END_DATE)

    # The selectbox uses the keys from the frequencies dictionary
    selected_frequency = st.selectbox('Select Frequency', list(frequencies.keys()), index=2)
    

    states = ['ACT', 'NSW', 'NT', 'QLD', 'SA', 'TAS', 'VIC', 'WA']
    selected_states = st.multiselect('Select States', states, default=states)
    metrics = ['Capacity', 'Performance', 'Output']
    selected_metric = st.selectbox('Select Metric', metrics)

    total_cap, average_per, total_out = api_data_extractor_historical(
        start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), TOKEN, frequencies[selected_frequency])

    total_cap = total_cap[total_cap['State'].isin(selected_states)]
    average_per = average_per[average_per['State'].isin(selected_states)]
    total_out = total_out[total_out['State'].isin(selected_states)]

    if selected_metric == 'Capacity':
        st.plotly_chart(plot_data(total_cap, 'Capacity', 'Total_Capacity_MW'))
    elif selected_metric == 'Performance':
        st.plotly_chart(plot_data(average_per, 'Performance', 'Average_Performance'))
    else:
        st.plotly_chart(plot_data(total_out, 'Output', 'Total_Output'))


if __name__ == '__main__':
    main()