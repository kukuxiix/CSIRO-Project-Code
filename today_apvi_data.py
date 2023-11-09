import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
from APVI_helper import categorize_data_by_state, calculate_average

TOKEN = "42d87a50153"

def api_data_extractor(token, date):
    # Get the data from the API for the given date
    url = f"https://pv-map.apvi.org.au/api/v2/2-digit/{date}.json?access_token={token}"
    response = requests.get(url)
    data = response.json()

    # Process performance data
    df_per = pd.DataFrame.from_dict(data['performance'], orient='index')
    df_per = df_per.transpose()  # Transpose the DataFrame so that timestamps are rows
    df_per = df_per.melt(ignore_index=False).reset_index()
    df_per.columns = ['Timestamp', 'Postcode', 'Performance']
    df_per['Timestamp'] = pd.to_datetime(df_per['Timestamp'])
    
    return df_per

def main():
    st.markdown("## Yesterday's PV Performance")

    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date = yesterday.strftime('%Y-%m-%d')

    df_per_all = api_data_extractor(TOKEN, yesterday_date)
    categorized_by_state = categorize_data_by_state(df_per_all)
    df_state_averages = calculate_average(categorized_by_state, 'Performance', 'Timestamp')

    #Get the list of states from the categorized data
    states = list(categorized_by_state.keys())
    selected_state = st.selectbox('Select a State', states)

    #Filter the DataFrame for the selected state's average data
    df_selected = df_state_averages[df_state_averages['State'] == selected_state]

    #Convert Timestamp to just the time part
    df_selected['Time'] = pd.to_datetime(df_selected['Timestamp']).dt.strftime('%H:%M')

    fig = px.line(df_selected, x='Time', y='Average_Performance', title=f'Average Performance over Time in {selected_state}')
    fig.update_xaxes(title='Time of Day')
    fig.update_yaxes(title='Average Performance (%)')
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
