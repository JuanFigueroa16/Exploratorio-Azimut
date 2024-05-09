import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import altair as alt
from matplotlib import ticker
from matplotlib.colors import LinearSegmentedColormap
from utils.ETL import range_selector

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
