import streamlit as st
import time
import numpy as np

from utils.ETL import *
from utils.plots import *
from utils.session_state import *

# filter by location_id session_state.meters_location by location_id
def filter_location_id(df, location_id):
    return df[df['location_id'] == location_id]

st.set_page_config(page_title="Cálculo de carga base", page_icon="../favicon.ico")

# Get the session state
session_state = get_session_state()

# sidebar checkbox to show or hide zero values
sidebar(session_state)


if session_state.energy_df is None:
    st.warning('No se han cargado los datos de potencia, por favor vuelve a la pagina de inicio', icon="⚠️")
    st.stop()
else:

    st.markdown(f"# Cálculos carga base {session_state.organization_select}")
    # st.sidebar.header("Boxplot perfil de costos horarios")
    st.write(
        """Cálculo de costo carga base."""
    )
    # add a input to SIDEBAR to input the cost of energy
    cost = st.sidebar.number_input("Costo de la energía", value= 1.0)
    session_state.cost = cost


    # get the list of meters
    meters_list=[]
    for key, value in session_state.systems.items():
        filter_df = filter_location_id(session_state.meters_location, value)
        filter_df['meter_name'] = filter_df['meter_name'].str.replace('.', '')
        num_meters = len(filter_df['meter_name'])
        # get a list of meters
        for meter in filter_df['meter_name']:
            try:
                meters_list.append(meter)
            except Exception as e:
                st.warning(f"El medidor {meter} no tiene datos de potencia")
                print(e)
                pass    
    # shoe a selectbox to select the meter on the sidebar
    meter_select = st.sidebar.selectbox("Seleccionar medidor", meters_list)
    session_state.meter_select = meter_select

    base_load_df = session_state.energy_df.copy()

    # just keep fecha and meter_select columns
    base_load_df = base_load_df[['fecha', meter_select]]

    base_load_df['fecha'] = pd.to_datetime(base_load_df['fecha'])
    
    # Filter out rows where the specified column has NaN values
    base_load_df = base_load_df.dropna(subset=[meter_select])

    if session_state and not session_state.zero_values:
        # Erase 0 values from the base_load_df
        base_load_df = base_load_df[base_load_df[meter_select] != 0]

    # filter the base_load_df to just get the date range selected
    base_load_df = range_selector(base_load_df, min_date=session_state.min_date, max_date=session_state.max_date)

    # filter the base_load_df to just get the days of the week selected
    if session_state.days:
        base_load_df = base_load_df[base_load_df['fecha'].dt.dayofweek.isin(session_state.days)]

    if base_load_df.empty:
        print(f"No valid data for meter_select '{meter_select}'.")
        pass

    # get the max and min values of the column selected
    max_value = base_load_df[meter_select].max()
    # min_value = base_load_df[meter_select].min()

    # set a range selector on the sidebar to get the max and min values of the column selected
    # min_value could be 0 and must be at begining 
    min_value = st.sidebar.number_input("Valor mínimo", 0.0, float(max_value), 0.0)
    max_value = st.sidebar.number_input("Valor máximo", min_value, max_value, max_value)

    # set the min and max values to the session_state
    session_state.min_value = min_value
    session_state.max_value = max_value

    # filter the base_load_df to just get the values between min_value and max_value
    base_load_df = base_load_df[(base_load_df[meter_select] >= min_value) & (base_load_df[meter_select] <= max_value)]

    # calculate a new column cost that is the product of the column selected and the cost of energy
    base_load_df['cost'] = base_load_df[meter_select] * cost
    # get the total cost on the date range selected
    total_cost = base_load_df['cost'].sum()
    total_kwh = base_load_df[meter_select].sum()

    # show to user the base load
    st.write(f"## Costo total carga base: ${total_cost:,.2f}")
    st.write(f"## Consumo total carga base [kWh]: {total_kwh:,.2f} kWh")