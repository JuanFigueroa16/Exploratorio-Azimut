import streamlit as st
import time
import numpy as np

from utils.ETL import *
from utils.plots.Consumo_Ultimos_Meses import *
from utils.session_state import *

# filter by location_id session_state.meters_location by location_id
def filter_location_id(df, location_id):
    return df[df['location_id'] == location_id]

st.set_page_config(page_title="Consumo Historico mensual", page_icon="../favicon.ico")

# Get the session state
session_state = get_session_state()


# sidebar checkbox to show or hide zero values
sidebar(session_state)


if session_state.energy_df is None:
    st.warning('No se han cargado los datos de potencia, por favor vuelve a la pagina de inicio', icon="⚠️")
    st.stop()
else:

    st.markdown(f"# Consumo Historico mensual del cliente{session_state.organization_select}")
    st.sidebar.header("Consumo Historico mensual")
    st.write(
        """Consumo Historico mensual del cliente seleccionado."""
    )
    # plot the histogram
    for key, value in session_state.systems.items():

        filter_df = filter_location_id(session_state.meters_location, value)
        filter_df['meter_name'] = filter_df['meter_name'].str.replace('.', '')
        num_meters = len(filter_df['meter_name'])

        for meter in filter_df['meter_name']:

            fig = plot_monthly_energy(session_state.energy_df, meter, session_state= session_state)
            # Display the plot using Streamlit's plotting function
            st.pyplot(fig)
            # Close the plot
            plt.close()
