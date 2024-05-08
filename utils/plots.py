import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import altair as alt
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
from utils.ETL import range_selector

# ------------------- Histogram of demanded power -------------------
def plot_histogram(data, column, session_state = None):
    if not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]
    # if session_state is not None:
    #     # filter the data to just get the date interva of session_state.min_date and session_state.max_date
    #     data = data[(data['fecha'] >= session_state.min_date) & (data['fecha'] <= session_state.max_date)]
    sns.set_theme(style="white")
    fig, ax = plt.subplots()
    sns.histplot(data[column], kde=True, bins=10, stat='probability', ax=ax)
    ax.set_ylabel('Frecuencia')
    ax.set_xlabel('Demanda [kW]')

    # Calculate percentages and set y-axis ticks
    total_samples = len(data[column])
    percentage_ticks = [str(int(val * 100)) + '%' for val in ax.get_yticks()]
    ax.set_yticklabels(percentage_ticks)

    ax.grid(True, linestyle='--', linewidth=0.5, color='gray')  # Add grid

    # Plot median and mean on the histogram
    median = data[column].median()
    mean = data[column].mean()
    # ax.axvline(median, color='r', linestyle='-', linewidth=2)
    # ax.axvline(mean, color='g', linestyle='-', linewidth=2)

    ax.legend(['kde - ' + column])

    # Return the figure
    return fig

# ------------------- Boxplot of hourly energy demand -------------------
def plot_hourly_boxplot(data, column, session_state=None):
    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]

    # Filter out rows where the specified column has NaN values
    data = data.dropna(subset=[column])

    if data.empty:
        print(f"No valid data for column '{column}'.")
        return None

    # Set whitegrid style
    sns.set_style("white")
    fig, ax = plt.subplots()

    sns.boxplot(
        x=data['fecha'].dt.hour,
        y=data[column],
        medianprops=dict(color="red", alpha=1),
        flierprops=dict(markerfacecolor="#707070", marker="."),
        boxprops=dict(facecolor='#4C72B0', alpha=0.57),  # Set box color and transparency
        ax=ax
    )

    # Calculate mean for each hour
    means = data.groupby(data['fecha'].dt.hour)[column].mean()

    if not means.empty:
        # Plot mean as black dots
        ax.plot(means.index, means.values, 'ko', markersize=4)

    ax.set_ylabel('Demanda [kW]')
    ax.set_xlabel('Hora')

    ax.legend([column])
    ax.grid(True, linestyle='--', linewidth=0.2, color='gray')  # Add grid

    # Return the figure object
    return fig

# ------------------- Boxplot of hourly energy cost -------------------
def plot_hourly_boxplot_cost(data, column, session_state=None):
    # Set darkgrid style
    sns.set_style("white")
    
    # Filter out rows where the specified column has 0 or NaN values
    filtered_data = data[data[column] != 0]
    filtered_data = filtered_data.dropna(subset=[column])

    # Multiply the demand by the cost of the demand
    cost = session_state.cost  # COP/kWh
    filtered_data[column] = filtered_data[column] * cost
    
    if filtered_data.empty:
        print(f"No valid data for column '{column}'.")
        return None

    fig, ax = plt.subplots()

    sns.boxplot(
        x=filtered_data['fecha'].dt.hour, 
        y=filtered_data[column],
        medianprops=dict(color="red", alpha=1),
        flierprops=dict(markerfacecolor="#707070", marker="."),
        boxprops=dict(facecolor='#4C72B0', alpha=0.57),  # Set box color and transparency
        ax=ax
    )

    # Calculate mean for each hour
    means = filtered_data.groupby(filtered_data['fecha'].dt.hour)[column].mean()

    if not means.empty:
        # Plot mean as black dots
        ax.plot(means.index, means.values, 'ko', markersize=4)

    ax.set_ylabel('Costo [$ COP]')
    ax.set_xlabel('Hora')

    # Format y-axis labels to display in thousands
    formatter = ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/1000) + 'k')
    ax.yaxis.set_major_formatter(formatter)

    ax.legend([column])
    ax.grid(True, linestyle='--', linewidth=0.2, color='gray')  # Add grid

    # Return the figure object
    return fig

# ------------------- weekly energy boxplot -------------------
def plot_daily_boxplot(data, column, session_state=None):
    # Set darkgrid style
    sns.set_style("white")

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

    if daily_data.empty:
        print(f"No valid data for column '{column}'.")
        return None

    # Clean atypical values (outliers) z-score > 3
    z_scores = (daily_data[column] - daily_data[column].mean()) / daily_data[column].std()
    daily_data = daily_data[(z_scores < 3) & (z_scores > -3)]

    # Set style and color palette for Seaborn
    sns.set_theme(style="white")

    # Extract day of the week from the timestamp
    daily_data['DayOfWeek'] = daily_data.index.dayofweek

    # Create boxplot with Seaborn
    sns.boxplot(
        x='DayOfWeek',
        y=column,
        data=daily_data,
        medianprops=dict(color="red", alpha=1),
        flierprops=dict(markerfacecolor="#707070", marker="."),
        boxprops=dict(facecolor='#4C72B0', alpha=0.57)  # Set box color and transparency
    )

    # Calculate mean for each day of the week
    means = daily_data.groupby('DayOfWeek')[column].mean()
    # Plot mean points on the boxplot
    plt.plot(means.index, means.values, 'ko', markersize=5)  # 'ko' means black circle markers

    plt.xlabel('Día', fontsize=14)  # Set x-axis label font size
    plt.ylabel('Consumo [kWh/día]', fontsize=14)  # Set y-axis label font size

    plt.xticks(range(7), ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'], fontsize=12)  # Set x-axis tick labels in Spanish
    plt.yticks(fontsize=12)  # Set y-axis tick font size
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.legend([column])
    plt.grid(True, linestyle='--', linewidth=0.2, color='gray')  # Add grid

    # Return the figure object
    return plt.gcf()

# ------------------- power profile -------------------
def plot_power_profile_daily(data, column, session_state=None):
    # Set darkgrid style
    sns.set_style("white")
    
    data = data[['fecha', column]]

    # Convert 'fecha' column to datetime if it's not already
    data['fecha'] = pd.to_datetime(data['fecha'])

    # Extract hour from datetime
    data['hour'] = data['fecha'].dt.hour

    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]

    if data.empty:
        print(f"No valid data for column '{column}'.")
        return None

    # Group by day and plot
    fig, ax = plt.subplots()

    # Plot power consumption profile for each day in light grey
    for day, group in data.groupby(data['fecha'].dt.date):
        ax.plot(group['hour'], group[f'{column}'], color='grey', alpha=0.14)

    # Plot median of all data
    median_profile = data.groupby(data['hour'])[f'{column}'].median()
    ax.plot(median_profile.index, median_profile.values, linewidth=4,  color='#4C72B0', label='Mediana')

    # Add labels and title
    ax.set_xlabel('Hora')
    ax.set_ylabel('Demanda [kW]')
    ax.set_title(f'Perfil de potencia diario {column}')
    ax.set_xticks(range(24))
    ax.grid(True, linestyle='--', alpha=0.7)

    # Show plot
    plt.tight_layout()
    ax.legend()
    
    # Close the plot
    plt.close()

    # return the figure object
    return fig

# ------------------- Monthly energy consumption -------------------
def plot_monthly_energy(data, column, session_state=None):
    # Set darkgrid style
    sns.set_style("white")
    
    # Extract year and month from the timestamp
    data['YearMonth'] = data['fecha'].dt.to_period('M')
    
    # Group by month and sum the energy consumption
    monthly_data = data.groupby('YearMonth')[column].sum()

    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        monthly_data = monthly_data[monthly_data != 0]

    if monthly_data.empty:
        print(f"No valid data for column '{column}'.")
        return None
    
    # Get the last 4 complete months including the current month
    last_4_months = monthly_data.index[-4:]
    
    # Convert PeriodIndex to strings for plotting
    last_4_months_str = last_4_months.astype(str)
    
    # Create a bar plot for the last 4 complete months
    fig, ax = plt.subplots()

    ax.bar(last_4_months_str, monthly_data[last_4_months_str], color='#4C72B0', alpha=0.57)

    # Set the title of the plot
    ax.set_title(f'Consumo mensual {column}')

    # Set the x-axis label
    ax.set_xlabel('Mes')

    # Set the y-axis label
    ax.set_ylabel('Consumo [kWh]')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Show the values on the bars
    # Inside the loop for annotations
    for p in ax.patches:
        value_formatted = '{:,.2f}'.format(p.get_height()).replace(',', ' ').replace('.', ',')  # Format the number
        ax.annotate(value_formatted, (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                    textcoords='offset points')
    # erase column YearMonth
    data.drop(columns=['YearMonth'], inplace=True)
    # Close the plot
    plt.close()

    # return the figure object
    return fig

# ------------------- Weekly energy consumption -------------------
def plot_hourly_matrix(data, column, session_state=None):
    # Define the custom colormap
    colors = ["#00B0F0", "#141A2F"]
    cmap = LinearSegmentedColormap.from_list("custom", colors)

    data = data[['fecha', column]]
    # Convert 'fecha' column to datetime format
    data['fecha'] = pd.to_datetime(data['fecha'])
        
    # erase Nan values on data[column]
    data = data.dropna(subset=[column])
    
    if not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]

    # filter the data to just get the date range selected
    # data = range_selector(data, min_date=session_state.min_date, max_date=session_state.max_date)

    # filter the data to just get the days of the week selected
    if session_state.days:
        data = data[data['fecha'].dt.dayofweek.isin(session_state.days)]

    data['DayOfWeek'] = data['fecha'].dt.dayofweek
    data['Hour'] = data['fecha'].dt.hour
    # Pivot the data to have rows as hour of the day and columns as day of the week
    heatmap_data = data.pivot_table(index='Hour', columns='DayOfWeek', values=f'{column}', aggfunc='mean')

    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        heatmap_data = heatmap_data[heatmap_data != 0]

    if heatmap_data.empty:
        print(f"No valid data for column '{column}'.")
        return None
    
    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, cmap=cmap, ax=ax)  # Use the custom colormap
    ax.set_title(f'Consumo semanal y horario {column} [kWh]', fontsize=16)
    ax.set_xlabel('Día de la semana', fontsize=14)
    ax.set_ylabel('Hora', fontsize=14)

    # Adjust y-axis ticks and labels to separate the hours
    ax.yaxis.set_tick_params(labelsize=12, rotation=0)
    ax.set_yticks(range(0, 24, 2))
    ax.set_yticklabels([f'{hour}:00' for hour in range(0, 24, 2)])

    # Set x-axis tick labels to Spanish names of the week
    ax.xaxis.set_tick_params(labelsize=12, rotation=45)
    ax.set_xticks(range(7))
    ax.set_xticklabels(['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'])

    plt.tight_layout()

    
    plt.show()
    # Return the figure object
    return fig

# ------------------- Daily energy consumption -------------------
def plot_diary_energy(data, column, session_state=None):
    # Set darkgrid style
    sns.set_style("white")
    
    # Create a figure with a rectangular size
    fig, ax = plt.subplots(figsize=(12, 6))

    # Apply zero_values filtering logic if session_state is provided
    if session_state and not session_state.zero_values:
        # Erase 0 values from the data
        data = data[data[column] != 0]

    # Extract year, month, and day from the timestamp
    data['YearMonthDay'] = data['fecha'].dt.to_period('D')
    
    # Group by day and sum the energy consumption
    daily_data = data.groupby('YearMonthDay')[column].sum()
    
    # Order the data by date
    daily_data = daily_data.sort_index()

    # Get the last 4 complete months including the current month
    last_4_months = daily_data.index[-(30*4):]

    # Filter last_4_months to only include dates present in daily_data
    last_4_months = [date for date in last_4_months if date in daily_data.index]
    
    # #days
    days = len(last_4_months)

    # get last day
    last_day = last_4_months[-1]
    
    # copy daily_data to avoid modifying the original data
    median_data = daily_data.copy()
    
    median_data = median_data[last_4_months]
    
    # Apply zero_values filtering logic if session_state is provided
    if session_state and not session_state.zero_values:
        # Drop 0 values
        median_data = median_data[median_data != 0]

    # drop nan values
    median_data.dropna(inplace=True)

    median = median_data.median()

    # Create a bar plot for the last 4 complete months
    sns.barplot(ax=ax, x=range(len(last_4_months)), y=daily_data[last_4_months], color='#4C72B0', alpha=0.57)
    
    # Set the title of the plot
    ax.set_title(f'Consumo diario {column}')
    
    # Set the x-axis label
    ax.set_xlabel('Día')
    
    # Set the y-axis label
    ax.set_ylabel('Consumo [kWh]')
    
    # step size for x-axis to ensure showing the latest and most recent date
    step_size = int(days/9)

    # Set the number of ticks on the x-axis
    ax.xaxis.set_major_locator(plt.MaxNLocator(10))

    # Manually annotate the most recent date on the x-axis
    ticks = range(0, days, step_size)
    labels = last_4_months[0::step_size]

    # Create a new index with the modified last item
    modified_labels = labels[:-1] + [last_day]

    ax.set_xticks(ticks)
    ax.set_xticklabels(modified_labels, rotation=0)

    # Plot median line on the graph
    ax.axhline(y=median, color='r', alpha=1, linestyle='-', label='Mediana')
    
    # Annotate on the left side on top of the median line the text Mediana : median value
    # rounded to 2 decimal places, text(x) can't be 0 because it will be over the y-axis, need to be a little bit to the right
    ax.text(0.1, median*1.02, f'Mediana: {median:.2f}', color='black', fontsize=10)

    # Show the plot
    plt.show()    

    # Return the figure object
    return fig


# ------------------ Altair Plots ------------------

# ----------- hourly boxplot -----------
def plot_hourly_boxplot_altair(data, column, session_state=None):
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

    # Create a boxplot using Altair with x axis as the hour of the day on 24 h format and
    # y axis as the demand that is on the data[column]
    data['fecha'] = data['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S') 
          
    boxplot = alt.Chart(data).mark_boxplot(
        size = 23, 
        box={'stroke': 'black'},  # Could have used MarkConfig instead
        median=alt.MarkConfig(stroke='red'),  # Could have used a dict instead
    ).encode(
        x=alt.X('hours(fecha):N', title='Hora', axis=alt.Axis(format='%H'), sort='ascending'),
        y=alt.Y(f'{column}:Q', title='Demanda [kW]'),
        strokeWidth=alt.value(1),  # Set the width of the boxplot
        color=alt.value('#2d667a'),  # Set the color of the bars
        opacity=alt.value(0.9),  # Set the opacity of the bars           
        tooltip=[alt.Tooltip('hours(fecha):N', title='Hora')]  # Customize the tooltip
    )
    chart = (boxplot).properties(
        width=600,  # Set the width of the chart
        height=400,  # Set the height of the chart
        title=(f'Boxplot de demanda de potencia {column}')  # Remove date from title
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
        y=alt.Y(f'{column}:Q', title='Costo [$/kWh]', axis=alt.Axis(format='$,.2f'),sort='ascending'),
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
        gridColor='#4C72B0',  # Set the color of grid lines
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    )

    return chart  # Enable zooming and panning

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
        y=alt.Y(f'{column}:Q', title='Consumo [kWh/día]'),
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
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    )

    return chart  # Enable zooming and panning

# ----------- Hisotgram -----------
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
        x=alt.X(f"{column}:Q", bin=alt.Bin(maxbins=10), title='Demanda [kW]'),
        y=alt.Y('sum(pct):Q', stack=None, axis=alt.Axis(format='%'), title='Frecuencia'),
        color=alt.value('#2D667A'),  # Set the color of the bars
        opacity=alt.value(0.9),  # Set the opacity of the bars 
        stroke = alt.value('black'),  # Set the color of the boxplot
        strokeWidth=alt.value(1),  # Set the width of the boxplot  
    ).properties(
        width=600,  # Set the width of the chart
        height=600,  # Set the height of the chart
        title=f'Histograma de demanda de potencia {column}'  # Set the title of the chart
    ).configure_axis(
        labelFontSize=12,  # Set the font size of axis labels
        titleFontSize=14,  # Set the font size of axis titles
        grid=True,
        gridColor='#4C72B0',  # Set the color of grid lines
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    ).interactive()  # Enable zooming and panning


    # Return the chart
    return chart

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
        color=alt.value('#2d667a'),  # Set the color of the bars
        opacity=alt.value(0.9),  # Set the opacity of the bars
        stroke = alt.value('black'),  # Set the color of the boxplot
        strokeWidth=alt.value(0.5),  # Set the width of the boxplot
        y=alt.Y(column, title=f'Consumo [{column}] [kWh]', axis=alt.Axis(titleFontSize=14)),  # Set the y-axis title

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
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        # strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    ).configure_title(
        fontSize=16  # Set the font size of the chart title
    )
    # data = original_data
    return chart


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
        y=alt.Y(f'{column}:Q', aggregate='median', title=''),
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
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    ).interactive()

    return chart