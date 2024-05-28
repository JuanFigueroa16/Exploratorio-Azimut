import pandas as pd
import altair as alt

from utils.ETL import range_selector

# ----------- Hisotgram Altair-----------
def plot_histogram_altair(data, column, session_state=None):
    # Convert 'fecha' column to datetime format
    data['fecha'] = pd.to_datetime(data['fecha'])
        
    # erase Nan values on data[column]
    data = data.dropna(subset=[column])
    
    if not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]

    # filter the data to just get the date range selected
    data = range_selector(data, min_date=session_state.min_date, max_date=session_state.max_date)

    # filter the data to just get the days of the week selected
    if session_state.days:
        data = data[data['fecha'].dt.dayofweek.isin(session_state.days)]

    # Create a histogram using Altair
    chart = alt.Chart(data).transform_joinaggregate(
            total='count(*)'
        ).transform_calculate(
            pct='1 / datum.total'
        ).mark_bar().encode(
        x=alt.X(f"{column}:Q", bin=alt.Bin(maxbins=10), title='Demanda [kW]').scale(zero=False),
        y=alt.Y('sum(pct):Q', stack=None, axis=alt.Axis(format='%'), title='Frecuencia'),
        color=alt.value('#2D667A'),  # Set the color of the bars
        opacity=alt.value(0.9),  # Set the opacity of the bars 
        stroke = alt.value('black'),  # Set the color of the boxplot
        strokeWidth=alt.value(1),  # Set the width of the boxplot  
    ).properties(
        width=600,  # Set the width of the chart
        height=450,  # Set the height of the chart
        title=f'Histograma de demanda de potencia {column}'  # Set the title of the chart
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
    ).interactive()  # Enable zooming and panning


    # Return the chart
    return chart
