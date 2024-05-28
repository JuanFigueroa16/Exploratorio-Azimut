import pandas as pd
import altair as alt

from utils.ETL import range_selector



# -------------------- Daily energy consumption -------------------
def plot_diary_energy_altair(data, column, session_state=None):
    # delete NaN values of data[column]
    data = data.dropna(subset=[column])

    # Convert 'fecha' column to datetime if it's not already
    data['fecha'] = pd.to_datetime(data['fecha'])
    # ensure fecha is ISO 8601 format

    data = range_selector(data, min_date=session_state.min_date, max_date=session_state.max_date)

    # Set 'fecha' as the index
    data = data.set_index('fecha')
    data.index = pd.to_datetime(data.index)

    # Resample the data to daily frequency and sum the values
    daily_data = data.resample('D').sum()[[column]]
    
    # Reset the index to ensure 'fecha' becomes a column again
    data = data.reset_index()
    daily_data = daily_data.reset_index()
 
    # Calculate median of the selected period
    median_value = daily_data[column].median()
    daily_data['fecha'] = daily_data['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    # Create an Altair chart
    bars = alt.Chart(daily_data).mark_bar().encode(
        x='fecha:T',  # Treat 'fecha' as a temporal field
        y=alt.Y(column, title=f'Consumo [{column}] [kWh]', axis=alt.Axis(titleFontSize=14)).scale(zero=False),  # Set the y-axis title
        color=alt.value('#2d667a'),  # Set the color of the bars
        opacity=alt.value(0.9),  # Set the opacity of the bars
        stroke = alt.value('black'),  # Set the color of the boxplot
        strokeWidth=alt.value(0.5),  # Set the width of the boxplot

    )
    # Add horizontal line for median value
    median_line = alt.Chart(pd.DataFrame({'y': [median_value]})
                            ).mark_rule(color='red').encode(y='y' )

    # create a layer with the bars and the median line
    chart = alt.layer(bars, median_line).resolve_scale(y='shared').properties(
        width=600,  # Set the width of the chart
        height=400,  # Set the height of the chart
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
        # strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    ).configure_title(
        fontSize=16  # Set the font size of the chart title
    )
    # data = original_data
    return chart
