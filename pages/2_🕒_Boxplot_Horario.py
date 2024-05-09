import streamlit as st
import time
import numpy as np

from utils.ETL import *
from utils.plots.Boxplot_Horario import *
from utils.session_state import *

# filter by location_id session_state.meters_location by location_id
def filter_location_id(df, location_id):
    return df[df['location_id'] == location_id]

st.set_page_config(page_title="Boxplot perfil de consumo Horario", page_icon="../favicon.ico")

# Get the session state
session_state = get_session_state()

sidebar(session_state)


if session_state.energy_df is None:
    st.warning('No se han cargado los datos de potencia, por favor vuelve a la pagina de inicio', icon="⚠️")
    st.stop()
else:
    st.markdown(f"# Boxplot perfil de consumo Horario del cliente{session_state.organization_select}")
    st.sidebar.header("Boxplot perfil de consumo Horario")
    st.write(
        """Boxplot perfil de consumo Horario del cliente seleccionado."""
    )            
    # plot the histogram
    for key, value in session_state.systems.items():

        filter_df = filter_location_id(session_state.meters_location, value)
        filter_df['meter_name'] = filter_df['meter_name'].str.replace('.', '')
        num_meters = len(filter_df['meter_name'])

        for meter in filter_df['meter_name']:

            try:
                fig = plot_hourly_boxplot_altair(session_state.power_df, meter, session_state= session_state)
                st.altair_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"El medidor {meter} no tiene datos de potencia")
                print(e)
                pass

            # fig = plot_hourly_boxplot(session_state.power_df, meter, session_state= session_state)
            # # Display the plot using Streamlit's plotting function
            # st.pyplot(fig)
            # # Close the plot
            # plt.close()
