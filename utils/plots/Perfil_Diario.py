import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import altair as alt
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
from utils.ETL import range_selector

# ------------------- Power Profile Plot -------------------
def plot_power_profile_daily_altair(data, column, session_state=None):
    # Convert 'fecha' column to datetime format
    data['fecha'] = pd.to_datetime(data['fecha'])
    
    # Filter out rows where the specified column has NaN values
    data = data.dropna(subset=[column])

    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]

    # filter the data to just get the date range selected
    data = range_selector(data, min_date=session_state.min_date, max_date=session_state.max_date)

    # filter the data to just get the days of the week selected
    if session_state.days:
        data = data[data['fecha'].dt.dayofweek.isin(session_state.days)]

    if data.empty:
        print(f"No valid data for column '{column}'.")
        return None
    # get a new column of just the date without time 
    data['solo_fecha'] = data['fecha'].dt.date

    daily_data = data[['fecha', column, 'solo_fecha']]
    daily_data['fecha'] = data['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    # plot every day in light grey
    line_chart = alt.Chart(daily_data).mark_line(color='grey', opacity=0.14).encode(
        x=alt.X('hours(fecha):T', title='Hora'),
        y=alt.Y(f'{column}:Q', title='Demanda [kW]'),
        color=alt.Color('solo_fecha:T', legend=None),
    )
    print('dataa', daily_data)
    # Calculate the median of the daily_data
    median_chart = alt.Chart(daily_data).mark_line(color='#4C72B0').encode(
        x=alt.X('hours(fecha):T', title=''),
        # y shows the median of all the daily data
        y=alt.Y(f'{column}:Q', aggregate='median', title='').scale(zero=False),
        strokeWidth=alt.value(5.0)
    )

    # Create a layer with the line chart and the median line
    chart = alt.layer(line_chart, median_chart).properties(
        width=600,  # Set the width of the chart
        height=400,  # Set the height of the chart
        title=(f'Perfil de potencia diario {column}')  # Set the title of the chart
    ).configure_axis(
        labelFontSize=12,  # Set the font size of axis labels
        titleFontSize=14,  # Set the font size of axis titles
        grid=True,
        gridColor='#4C72B0',  # Set the color of grid lines
        # color of labels of x-axis and y-axis is black
        labelColor='black',
        # x-axis and y-axis titles are bold
        titleFontWeight='bold',
        # color of x-axis and y-axis titles is black
        titleColor='black',
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    ).interactive()

    return chart
