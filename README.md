# CSIRO-Project-Code
Extract and process solar photovoltaic (PV) and panel data.

## Scripts Overview
### APVI
#### APVI Output 
Capacity: 
- Total installed capacity of PV systems in each two digit postcode region (all postcodes beginning with the same two digit). 

Performance: 
- The average performance (output as a percentage of rated capacity) of all PV systems contributing into the database, for each 2-digit postcode in each 15 min interval. 

Output:
- The estimated total output (MW) of PV systems installed in each 2-digit postcode region in each 15 minute interval. 

#### 'today_apvi_data.py'
Extracts the latest 15min (real-time) data on solar pv system. 
Currently, it does not generate a graphical output due to complexities with creating a coropleth map, which ideally would display different regions' solar output, capacity, and performance metrics.

#### 'historical_apvi_data.py'
Produces a time-series graph representing historical data on solar PV system output, performance, and capacity. Although data availability is announced starting from 2001.04.01 on the website, in practice, the accessible data begins on 2015.02.01. Users can select different time ranges for the data (Yearly, Year to Start, Weekly, Daily), but an increase in the data points can lead to longer processing times.

### 'solar_chart.py'
Extracting solar panel price data. 
It returns a tabular dataset that lists the prices for solar panels of different power outputs. 
It also computes a single value representing the average commercial cost per watt for solar panels.
