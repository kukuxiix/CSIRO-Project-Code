import pandas as pd

#Filter for rows where 'Timestamp' ends with '12:00:00 +1000'
def filter_timestamp(df):
            return df[df['Timestamp'].str.endswith('12:00:00 +1000')]

#Group data from the same state
def categorize_data_by_state(df, column_name='Postcode'):
    categories = {
        #Postcode 
        'NSW': ['02', '1', '2'],  
        'VIC': ['3'],             
        'QLD': ['4', '9'],             
        'SA':  ['5'],             
        'WA':  ['6'],           
        'TAS': ['7'],          
        'NT':  ['08', '8']       
    }

    categorized_dfs = {state: [] for state in categories.keys()}
    str_postcodes = df[column_name].astype(str)
    for state, prefixes in categories.items():
        matching_rows = pd.concat(
            [df[str_postcodes.str.startswith(prefix)] for prefix in prefixes],
            ignore_index=True
        )
        
        if not matching_rows.empty:
            categorized_dfs[state].append(matching_rows)

    for state, data_list in categorized_dfs.items():
        if data_list: 
            categorized_dfs[state] = pd.concat(data_list, ignore_index=True)
        else:
            categorized_dfs[state] = pd.DataFrame(columns=df.columns)

    return categorized_dfs

#Add data from the same state and same time 
def calculate_total(categorized_data, column_name, date_column = 'Date'):
    results = []
    for state, data in categorized_data.items():
        grouped = data.groupby(date_column)
        for date, group in grouped:
            if not group.empty:
                total_value = group[column_name].sum()
                results.append({
                    "State": state,
                    date_column: date,
                    "Total_" + column_name: total_value
                })
            else:
                results.append({
                    "State": state,
                    date_column: date,
                    "Total_" + column_name: 0 
                })

    return pd.DataFrame(results)

#Average data from the same state and date
def calculate_average(categorized_data, column_name, date_column = 'Date'):
    results = []
    for state, data in categorized_data.items():
        grouped = data.groupby(date_column)
        for date, group in grouped:
            if not group.empty:
                average_performance = group[column_name].mean()
                results.append({
                    "State": state,
                    date_column: date,
                    "Average_" + column_name: average_performance
                })
            else:
                results.append({
                    "State": state,
                    date_column: date,
                    "Average_" + column_name: 0 
                })

    return pd.DataFrame(results)
