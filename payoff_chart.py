import streamlit as st
from solarc_chart import calculate_payoff, scrape_solar_prices
import plotly.graph_objects as go


#Define the average performance and electricity cost for each state
performance = {
    'AdelaideSA': 23.98, 
    'BrisbaneQLD': 16.95,
    'CanberraACT': 21.06,
    'DarwinNT': 15.85,
    'HobartTAS': 15.97,
    'MelbourneVIC': 19.57,
    'SydneyNSW': 21.06,
    'PerthWA': 20.50,
}

electricity_cost = {
    'AdelaideSA': 34.84,
    'BrisbaneQLD': 21.69,
    'CanberraACT': 26.56,
    'DarwinNT': 25.74,
    'HobartTAS': 26.67,
    'MelbourneVIC': 27.29,
    'SydneyNSW': 28.72,
    'PerthWA': 27.17,
}     


def display_payoff_time_table(data, headers, color_one, color_two, color_three):
    st.markdown("## Solar Panel Payoff Time (in years)")
    payoff_data = calculate_payoff(data, performance, electricity_cost, headers)
    
    #Create headers for the payoff table
    payoff_headers = [' '] + headers[1:]  # Use the headers from the solar price chart

    #Transpose the payoff data for the table display
    transposed_payoff_data = [list(item) for item in zip(*payoff_data)]

    payoff_fig = go.Figure(data=[go.Table(
        header=dict(
            values=payoff_headers,
            line_color=color_one,
            fill_color=color_one,  
            align='center',
            font=dict(color='black', size=15),
            height=30
        ),
        cells=dict(
            values=transposed_payoff_data,
            line_color=color_one,
            fill=dict(color=[color_two, *([color_three] * (len(payoff_headers) - 1))]),
            align='center',
            font=dict(color='black', size=12.5)
        ))
    ])

    payoff_fig.update_layout(width=1200, height=600, margin=dict(t=10, b=10))
    st.plotly_chart(payoff_fig, use_container_width=True)

if __name__ == "__main__":
    # st.title('Solar Panel Payoff Time')

    color_one = "#FFD700"  # line
    color_two = "#FFFAF0"
    
    url = "https://www.solarchoice.net.au/solar-panels/solar-power-system-prices"
    headers, data = scrape_solar_prices(url)

    # Display the payoff time table
    display_payoff_time_table(data, headers, color_one, color_one, color_two)