from urllib.error import URLError
import streamlit as st
from utils.ETL import * # Load all the Extract, Transform, Load functions
from utils.session_state import *

@st.cache_data
def get_organizations():
    t_medidores = obtener_t_medidores()
    organizations = t_medidores[['ID Cliente', 'Nombre Cliente']].drop_duplicates()
    organizations = organizations.dropna(subset=['ID Cliente'])
    organizations.sort_values(by='ID Cliente', inplace=True)
    organizations_list = [name for name in organizations['Nombre Cliente'] if name is not None]
    organizations_list.sort()
    return organizations, organizations_list

def get_organization_id(organization_select, organizations):
    organization_id = organizations[organizations['Nombre Cliente'] == organization_select]['ID Cliente'].values[0]
    return organization_id

@st.cache_data
def get_inmuebles(organization_id):
    t_medidores = obtener_t_medidores()
    t_medidores = t_medidores[t_medidores['ID Cliente'] == organization_id]
    with st.spinner("Cargando inmuebles de la organización..."):
        organization_data = get_organization_data(organization_id)
        consulta = combinacion_consultas(organization_data, t_medidores)
        inmuebles = conocer_id_inmuebles(consulta)
    return inmuebles

def get_inmueble_id(inmueble_select, inmuebles):
    inmueble_id = inmuebles[inmuebles['Nombre Inmueble'] == inmueble_select]['ID Inmueble'].values[0]
    return inmueble_id

def main():
    st.set_page_config(
        page_title="Analisis exploratorio",
        page_icon="favicon.ico"
    )

    st.sidebar.header("Analisis exploratorio")
    st.write("# Analisis Exploratorio Azimut 📊")

    st.markdown(
        """
        Herramienta para realizar analisis exploratorios de los datos de energía, potencia u otra variable medida
        en un cliente.
    """
    )

    st.markdown("# Selección del cliente")

    st.write(
        """Selección del cliente a analizar."""
    )

    # Get session state
    session_state = get_session_state()

    # Get unique organizations
    organizations, organizations_list = get_organizations()

    # If organization is not selected, show organization selectbox

    if session_state["organization_select"] is None:
        organization_select = st.selectbox(
            "Lista de organizaciones", organizations_list, index=None, placeholder="Seleccione una organización"
        )
        if organization_select:
            session_state.organization_select = organization_select
    else:
        organization_select = session_state.organization_select

    # If organization is selected, proceed with the rest of the logic
    if organization_select:

        # get organization_id from the organizations list
        organization_id = organizations[organizations['Nombre Cliente'] == organization_select]['ID Cliente'].values[0]
        st.write("### Organización seleccionada", organization_select)
        # st.write("### ID Cliente", organization_id)

        inmuebles = get_inmuebles(organization_id)
        inmuebles_list = [name for name in inmuebles['Nombre Inmueble'] if name is not None]
        inmuebles_list.sort()
        
        # If inmueble is not selected, show inmueble selectbox
        if session_state["inmueble_select"] is None:
            inmueble_select = st.selectbox(
                "Lista de inmuebles", inmuebles_list, index=None, placeholder="Seleccione un inmueble"
            )
            if inmueble_select:
                session_state.inmueble_select = inmueble_select
        else:
            inmueble_select = session_state.inmueble_select

        # If inmueble is selected, proceed with the rest of the logic
        if inmueble_select:

            inmueble_id = int(get_inmueble_id(inmueble_select, inmuebles))
            # st.write("### ID Inmueble", inmueble_id)
            st.write("### Inmueble seleccionado", inmueble_select)
            
            # spinner to wait for the data to load
            with st.spinner("Cargando datos de energía y potencia..."):

                meters = get_meters(organization_id)
                hierarchy = build_hierarchy(meters)

                # IDs of the parent entities
                parent_ids = meters[meters['parent_id'].isnull()]['id']
                parent_ids_list = parent_ids.tolist()

                # Getting descendants
                descendants = get_descendants(hierarchy, parent_ids_list)
                meters_location = get_meters_names(inmueble_id, descendants)
                
                # get unique location_id of meters_location as a list
                unique_location_ids = meters_location['location_id'].unique().tolist()
                
                # for id in meters
                # check if id in unique_location_ids, if so add to dictionary systems with key name and value id
                systems = {}
                for index, row in meters.iterrows():
                    if row['id'] in unique_location_ids:
                        systems[row['name']] = row['id']

                interval = get_interval(organization_id)
                min_date = interval['min_date'][0]
                max_date = interval['max_date'][0]

                
                power_df = get_power_data(meters_location, organization_id, min_date, max_date)
                energy_df = get_ener_data(meters_location, organization_id, min_date, max_date)

                # for each column in power_df and energy_df, if there are points/dots on the column name, replace them nothing
                power_df.columns = power_df.columns.str.replace(".", "")
                energy_df.columns = energy_df.columns.str.replace(".", "")
                # Save the data to the session state
                st.write("## Datos de Potencia")
                power_df
                st.write("## Datos de Energía")
                energy_df
                session_state.meters_location = meters_location
                session_state.systems = systems
                session_state.power_df = power_df
                session_state.energy_df = energy_df
                session_state.min_date = min_date
                session_state.max_date = max_date
                
if __name__ == "__main__":
    main()