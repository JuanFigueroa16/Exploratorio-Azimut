import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from matplotlib.colors import LinearSegmentedColormap


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
