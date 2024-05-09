import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import altair as alt
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
from utils.ETL import range_selector


# ------------------- Daily energy consumption plot -------------------
def plot_daily_boxplot_altair(data, column, session_state=None):
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

    hourly_data = data[['fecha', column]]

    # Set fecha as index and datetime
    hourly_data.set_index('fecha', inplace=True)
    hourly_data.index = pd.to_datetime(hourly_data.index)

    # Drop NaN values
    hourly_data.dropna(inplace=True)

    # Resample hourly data to daily sum
    daily_data = hourly_data.resample('D').sum()

    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        daily_data = daily_data[daily_data[column] != 0]

    # Extract day of the week from the timestamp
    daily_data['DayOfWeek'] = daily_data.index.dayofweek

    # Convert DayOfWeek to categorical data type
    daily_data['DayOfWeek'] = daily_data['DayOfWeek'].astype('category')

    # Set custom order and mapping for weekday names in Spanish
    weekday_order = [0, 1, 2, 3, 4, 5, 6]  # Sunday, Monday, Tuesday, ..., Saturday
    day_name = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    weekday_names = [day_name[i] for i in weekday_order]

    daily_data['DayOfWeek'] = daily_data['DayOfWeek'].cat.reorder_categories(weekday_order, ordered=True)
    daily_data['DayOfWeek'] = daily_data['DayOfWeek'].cat.rename_categories(weekday_names)

    # reset index to have fecha as a column
    daily_data = daily_data.reset_index()

    daily_data['fecha'] = daily_data['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    print('daily_data', daily_data)
    order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    boxplot = alt.Chart(daily_data).mark_boxplot(
        size = 55, 
        box={'stroke': 'black'},  # Could have used MarkConfig instead
        median=alt.MarkConfig(stroke='red'),  # Could have used a dict instead        
        ).encode(
        x=alt.X('DayOfWeek:N', title='Día de la semana', sort=order),
        y=alt.Y(f'{column}:Q', title='Consumo [kWh/día]').scale(zero=False),
        color=alt.value('#2d667a'),  # Set the color of the bars
        opacity=alt.value(0.9),  # Set the opacity of the bars
        tooltip=[alt.Tooltip('DayOfWeek:N', title='Día de la semana')]  # Customize the tooltip
    )

    chart = (boxplot).properties(
        width=500,  # Set the width of the chart
        height=400,  # Set the height of the chart
        title=(f'Boxplot de consumo diario {column}')  # Remove date from title
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
    )

    return chart  # Enable zooming and panning
