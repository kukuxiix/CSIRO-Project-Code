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

def main():
    st.title('Solar Panel Costs')

    #Change colours 
    color_one = "#FF4500" 
    color_two = "#FFD700"  
    color_three = "#FFFAF0" 
    
    url = "https://www.solarchoice.net.au/solar-panels/solar-power-system-prices"
    
    # Display average commercial cost per watt
    try:
        average_price = scrape_average_price(url)
        st.markdown(f"### **Average Commercial Cost per Watt**", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:32px;color:{color_one};margin-bottom:5px;margin-top:5px;'>{average_price}</p>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Display the table title and adjust spacing
    st.markdown("<h4 style='margin-bottom:5px;margin-top:5px;'>Solar Panel Cost by Region and kW</h4>", unsafe_allow_html=True)

    # Fetch and display table
    try:
        headers, data = scrape_solar_prices(url)
        transposed_data = [list(item) for item in zip(*data)] 
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=headers,
                line_color=color_one,
                fill_color=color_two,
                align='center',
                font=dict(color='black', size=14),
                height=30  # Adjusted height for header
            ),
            cells=dict(
                values=transposed_data,  
                line_color=color_one,
                fill=dict(color=[color_two, color_three]),  # Alternating row colors
                align='center',
                font=dict(color='black', size=13)
            ))
        ])

        fig.update_layout(width=1000, height=600, margin=dict(t=5, b=0, l=0, r=0))
        
        # Using Streamlit to display the chart
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
