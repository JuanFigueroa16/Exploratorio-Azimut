import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import altair as alt
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
from utils.ETL import range_selector

# ----------- hourly boxplot COST -----------
def plot_hourly_boxplot_cost_altair(data, column, session_state=None):
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
    
    # Multiply the demand by the cost of the demand
    cost = session_state.cost  # COP/kWh
    data[column] = data[column] * cost
    data['fecha'] = data['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S')       
    # Create a boxplot using Altair with x axis as the hour of the day on 24 h format and
    # y axis as the demand that is on the data[column]
    boxplot = alt.Chart(data).mark_boxplot(
        size = 23, 
        box={'stroke': 'black'},  # Could have used MarkConfig instead
        median=alt.MarkConfig(stroke='red'),  # Could have used a dict instead
    ).encode(
        x=alt.X('hours(fecha):N', title='Hora', axis=alt.Axis(format='%H')),
        y=alt.Y(f'{column}:Q', title='Costo [$/kWh]', axis=alt.Axis(format='$,.2f'),sort='ascending').scale(zero=False),
        color=alt.value('#2d667a'),  # Set the color of the bars
        opacity=alt.value(0.9), # set the opacity of the bars
        tooltip=[alt.Tooltip('hours(fecha):N', title='Hora')]  # Customize the tooltip
    )

    chart = (boxplot).properties(
        width=600,  # Set the width of the chart
        height=400,  # Set the height of the chart
        title=(f'Costo horario {column}')  # Remove date from title
    ).configure_axis(
        labelFontSize=12,  # Set the font size of axis labels
        titleFontSize=14,  # Set the font size of axis titles
        grid=True,
        # color of labels of x-axis and y-axis is black
        labelColor='black',
        # x-axis and y-axis titles are bold
        titleFontWeight='bold',
        # color of x-axis and y-axis titles is black
        titleColor='black',
        gridColor='#4C72B0',  # Set the color of grid lines
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    )

    return chart  # Enable zooming and panning
