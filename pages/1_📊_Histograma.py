import streamlit as st

from utils.ETL import *
from utils.plots.Histograma import *
from utils.session_state import *

# filter by location_id session_state.meters_location by location_id
def filter_location_id(df, location_id):
    return df[df['location_id'] == location_id]

st.set_page_config(page_title="Histogramas de demanda de potencia", page_icon="../favicon.ico")

# Get the session state
session_state = get_session_state()

# sidebar checkbox to show or hide zero values
sidebar(session_state)


if session_state.energy_df is None:
    st.warning('No se han cargado los datos de potencia, por favor vuelve a la pagina de inicio', icon="⚠️")
    st.stop()

else:
    st.markdown(f"# Histogramas de demanda de potencia del cliente{session_state.organization_select}")
    st.sidebar.header("Histogramas de demanda de potencia")
    st.write(
        """Histogramas de demanda de potencia del cliente seleccionado."""
    )    
    # plot the histogram
    for key, value in session_state.systems.items():

        filter_df = filter_location_id(session_state.meters_location, value)
        # for meter in filter_df['meter_name'] if the column name has point/dots replace them with nothing
        filter_df['meter_name'] = filter_df['meter_name'].str.replace('.', '')
        num_meters = len(filter_df['meter_name'])
        for meter in filter_df['meter_name']:
            try:
                fig = plot_histogram_altair(session_state.power_df, meter, session_state= session_state)
                st.altair_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"El medidor {meter} no tiene datos de potencia")
                print(e)
                pass

            