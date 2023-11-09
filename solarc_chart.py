import streamlit as st
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import pandas as pd

#Solar panel costs (table)
def scrape_solar_prices(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', id='tablepress-5')
    headers = [th.text for th in table.thead.find_all('th')] #Extract headers
    rows = table.tbody.find_all('tr') #Extract rows 
    data = []
    for row in rows:
        cells = row.find_all(['td', 'th'])
        row_data = [cell.text for cell in cells]
        data.append(row_data)
    return headers, data

#Average commercial solar panel costs per watt (one number)
def scrape_average_price(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', id='tablepress-8')
    average_price = table.tfoot.find('th', class_='column-2').text.strip()
    
    return average_price

def calculate_payoff(data, performance, electricity_cost, headers):
    payoff_data = []
    for row in data:
        region_formatted = row[0].strip()
        region = row[0].strip().replace(',', '').replace(' ', '')
        
        region_performance = performance.get(region)
        region_electricity_cost = electricity_cost.get(region)  # This should be in cents

        if region_performance is None or region_electricity_cost is None:
            st.write(f"Skipping region: {region} due to missing data")
            continue

        # Convert the performance to a fraction and electricity cost to dollars
        region_performance = region_performance / 100
        region_electricity_cost = region_electricity_cost / 100

        # row_payoff = [region]
        row_payoff = [region_formatted] 
        for i, cell in enumerate(row[1:], start=1):  # Skip the region name
            try:
                # The kW size is determined by the header for this column
                kW_size = float(headers[i].replace('kW', ''))
                cost = float(cell.replace(',', '').replace('$', ''))
                savings_per_year = kW_size * region_performance * region_electricity_cost  * 24 * 365 * 0.5
                time_to_payoff = cost / savings_per_year if savings_per_year else float('inf')
                # Format the result to two decimal places
                row_payoff.append(f"{time_to_payoff:.2f}" if time_to_payoff != float('inf') else "∞")
            except ValueError as e:
                st.write(f"Error processing {region}, system size {kW_size}kW: {e}")
                row_payoff.append('Error')
        payoff_data.append(row_payoff)

    return payoff_data


def display_solar_costs(url, header_color, color_one, color_two, color_three):
    #Display average commercial cost per watt
    try:
        average_price = scrape_average_price(url)
        st.markdown(f"### Average Commercial Cost per Watt: <span style='color:{header_color};'>{average_price}</span>",
                    unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

    #Fetch and display solar panel cost table
    try:
        headers, data = scrape_solar_prices(url)
        transposed_data = [list(item) for item in zip(*data)] 

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=headers,
                line_color=color_one,
                fill_color=color_two,
                align='center',
                font=dict(color='black', size=15),
                height=35
            ),
            cells=dict(
                values=transposed_data,
                line_color=color_one,
                fill=dict(color=[color_two, color_three]),
                align='center',
                font=dict(color='black', size=12.5),
            ))
        ])
        fig.update_layout(width=1200, height=600, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred while displaying the solar panel cost table: {e}")

if __name__ == "__main__":
    # st.title('Solar Panel Costs')
    st.markdown("## Solar Panel Costs")
    header_color = "#FF4500" 
    color_one = "#FFD700"
    color_two = "#FFD700"
    color_three = "#FFFAF0"
    url = "https://www.solarchoice.net.au/solar-panels/solar-power-system-prices"
    display_solar_costs(url, header_color, color_one, color_two, color_three)
    