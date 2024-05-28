import streamlit as st

from utils.ETL import *
from utils.plots.Comparativo_Medidores import *
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

    st.markdown(f"# Cálculos carga base ")
    st.markdown(f"## {session_state.organization_select}")


    # st.sidebar.header("Boxplot perfil de costos horarios")

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
    # show a selectbox to select the meter on the sidebar
    meter_select = st.sidebar.multiselect("Seleccionar medidor", meters_list, [], placeholder="Selecciona los medidores")
    session_state.meter_select = meter_select
    # add fecha to the meter_select list
    meter_select.insert(0, 'fecha')
    
    base_load_df = session_state.power_df.copy()
    # filter the base_load_df to just keep columns fecha and the meter_select
    base_load_df = base_load_df[meter_select]

    base_load_df['fecha'] = pd.to_datetime(base_load_df['fecha'])
    
    # # Filter out rows where the specified column has NaN values
    # base_load_df = base_load_df.dropna(subset=[meter_select])

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

    # create a altair layer chart with the fecha as x axis and all the meters in meter_select as y axis with
    # common x and y axis

    # --- altair graph logic here ---

    # pivot base load df to have fecha, value and meter_name columns
    base_load_df_pivot = base_load_df.melt(id_vars=['fecha'], var_name='meter_name', value_name='value')
    base_load_df_pivot['fecha'] = base_load_df_pivot['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    # rename meter_name to Medidor
    base_load_df_pivot = base_load_df_pivot.rename(columns={'meter_name': 'Medidor'})

    legend_graph= alt.Chart(base_load_df_pivot).mark_line().encode(
    x=alt.X('fecha:T', title='Fecha', axis=alt.Axis(format='%d/%m/%Y-%H:%M')),  # Specify date format for axis
    y=alt.Y('value:Q', title='Demanda [kW]').scale(zero=False),
    color='Medidor:N',
    tooltip=['fecha:T', 'value:Q', 'Medidor:N']
    ).properties(
        width=900,  # Set the width of the chart
        height=450,  # Set the height of the chart
        title=f'Comparativo Medidores'  # Set the title of the chart
    ).configure_axis(
        labelFontSize=12,  # Set the font size of axis labels
        titleFontSize=14,  # Set the font size of axis titles
        grid=True,
        gridColor='#4C72B0',  # Set the color of grid lines
        labelColor='black', # color of labels of x-axis and y-axis is black        
        titleFontWeight='bold', # x-axis and y-axis titles are bold
        titleColor='black', # color of x-axis and y-axis titles is black
        gridOpacity=0.2  # Set the opacity of grid lines
    ).configure_view(
        strokeWidth=0,  # Remove the border of the chart
        fill='#FFFFFF'  # Set background color to white
    ).interactive()

    # Show the chart
    st.altair_chart(legend_graph, use_container_width=False)    
