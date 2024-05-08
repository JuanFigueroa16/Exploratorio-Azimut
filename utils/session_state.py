import streamlit as st
import datetime

# Define a function to get or create SessionState
def get_session_state():
    session_state = st.session_state
    if 'organization_id' not in session_state:
        session_state.organization_id = None
    if 'min_date' not in session_state:
        session_state.min_date = None
    if 'max_date' not in session_state:
        session_state.max_date = None
    if 't_medidores' not in session_state:
        session_state.t_medidores = None
    if 'organizations' not in session_state:
        session_state.organizations = None
    if 'organization_select' not in session_state:
        session_state.organization_select = None
    if 'inmueble_select' not in session_state:
        session_state.inmueble_select = None
    if 'meters_location' not in session_state:
        session_state.meters_location = None
    if 'systems' not in session_state:
        session_state.systems = None
    if 'power_df' not in session_state:
        session_state.power_df = None
    if 'energy_df' not in session_state:
        session_state.energy_df = None
    if 'cost' not in session_state:
        session_state.cost = 600
    if 'days' not in session_state:
        session_state.days = []  # All days
    if 'min_value' not in session_state:
        session_state.min_value = None
    if 'max_value' not in session_state:
        session_state.max_value = None
        
    return session_state

# Define the sidebar content
def sidebar(session_state):
    st.sidebar.title("Opciones")
    min_date = st.sidebar.date_input("Fecha Inicial", session_state.min_date)
    max_date = st.sidebar.date_input("Fecha Final", session_state.max_date)

    map_days = {'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4, 'Sábado': 5, 'Domingo': 6}

    # Add 7 checks representing the 7 days of the week, default all checked
    # This will allow filtering the data by day of the week
    with st.sidebar.expander("Días de la semana"):
        days = st.multiselect(
            "Seleccionar días", 
            ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'], 
            ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
            placeholder="Días para el informe"
            )
        days = [map_days[day] for day in days]
    zero_values = st.sidebar.checkbox("Mostrar valores en cero", value=True)

    session_state.min_date = min_date
    session_state.max_date = max_date
    session_state.zero_values = zero_values
    session_state.days = days
    return min_date, max_date, zero_values,days