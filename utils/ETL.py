from azure.storage.blob import BlobClient #para acceder al blob storage en Azure
import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

@st.cache_data
def obtener_t_medidores(): 
    '''Función que se conecta a la ETL para traer el t_medidores.
       ---------------------------------------------------------------------------------
       Parameters
       None
       ---------------------------------------------------------------------------------
       Return
       tabla_medidores: DF
                  Tabla de azure de t_medidores que esta almacenado en el DWH Analitica.'''
    #Conexion a ACTIVA

    connection = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME")
    )

    # Creacion de un cursor para hacer operaciones sobre la base de datos
    cursor = connection.cursor()
    
    
    # Consulta SQL 
    query = '''(SELECT *
FROM azure_tables.t_medidores); '''

    # Ejecucion de la consulta
    cursor.execute(query)

    #Almacenamiento de los datos
    tabla_medidores = cursor.fetchall()
    
    #convertir datos a dataframe
    tabla_medidores = pd.DataFrame(tabla_medidores, columns = ['ID Medidor',"Nombre Medidor","ID Sistema","Sistema Equipo","ID Inmueble","Nombre Inmueble","ID Cliente","Nombre Cliente","Jerarquía","Parent ID","Nombre Parent","Estado medidor","Nombre DU","ID Línea-Planta-Piso","Nombre Línea-Planta-Piso","Serial","Column1","Agrupación recobro","ID Equipo","Equipos","Servicio","Simular","Jerarquia Simulada"])
    connection.close()
    return tabla_medidores


def obtener_datos_AZURE(): #obtiene Tablas Generales desde Azure
    
    #string de conexion
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    #accede a Tablas Generales
    blob = BlobClient.from_connection_string(conn_str = connection_string , container_name = "gestion-del-uso", blob_name = "Tablas Generales.xlsx")
    #descarga tablas generales
    with open("./Tablas_generales.xlsx", "wb") as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)

def obtener_estilo_AZURE(): #obtiene estilo desde Azure
    
    #string de conexion
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    #accede a el estilo
    blob = BlobClient.from_connection_string(conn_str = connection_string , container_name = "gestion-del-uso", blob_name = "estilo_azimut.mplstyle")
    #descarga el estilo
    with open("./estilo_azimut.mplstyle", "wb") as my_blob:
        blob_data = blob.download_blob()
        blob_data.readinto(my_blob)

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST2"),
        port=os.getenv("DB_PORT2"),
        dbname=os.getenv("DB_NAME2"), 
        user=os.getenv("DB_USER2"), 
        password=os.getenv("DB_PASSWORD2"))
    
    return conn

# get interval
def get_interval(organization_id):
    conn = get_connection()
    query = f"""
    SELECT
        MIN(hh.date) AS Min_Date,
        MAX(hh.date) AS Max_Date
    FROM
        usage_management.history_hourly hh
    INNER JOIN
        usage_management.meters m ON hh.meter_id = m.id
    WHERE
        m.organization_id = {organization_id}
        AND hh.event_code = 'act_pwr';
    """
    interval = pd.read_sql_query(query, conn)
    conn.close()
    return interval


def get_meters(organization_id):
    conn = get_connection()
    query = f"""
    SELECT id, parent_id, name 
    FROM organizations.locations l 
    WHERE organization_id = {organization_id};
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_organization_data(organization_id): #obtiene los datos del organizacion id

    # construct a string with the variables separated by commas and surrounded by single quotes like 'act_pwr', 'act_ene'
    # variables_str = ", ".join([f"'{variable}'" for variable in variables])
    #Conexion a Plataforma
    conn = get_connection()

    # Creacion de un cursor para hacer operaciones sobre la base de datos
    cursor = conn.cursor()
        
    # Consulta SQL 
    query = f'''(SELECT
    organization_id,
    meter_id as "id_medidor",
    name as "nombre_medidor",
    event_code as "variable",
    value as valor,
    date
FROM
    usage_management.history_hourly

LEFT JOIN usage_management.meters
   ON meter_id = usage_management.meters.id

WHERE
    date > (SELECT (TO_CHAR(NOW() - INTERVAL '120 DAY', 'yyyy-mm-01'))::date)
AND (
    event_code = 'act_ene'
)
AND (
    organization_id =)
    ); '''
    
    query = query.replace("organization_id =", "organization_id = " + str(organization_id)) #se añade el organization_id

    # Ejecucion de la consulta
    cursor.execute(query)

    #Almacenamiento de los datos
    datos = cursor.fetchall()
    
    #convertir datos a dataframe
    datos = pd.DataFrame(datos, columns =[ 'organization_id', 'id_medidor', 'nombre del medidor',
                                          'variable', 'valor', 'fecha'])

    conn.close()
    return datos

def combinacion_consultas(organization_data,t_medidores): #combina t_medidores y los datos de activa, ademas de aplicar algunos filtros
    #inner join, es decir que toma la interseccion de los conjuntos
    consulta_combinada = pd.merge(left = organization_data, right = t_medidores, left_on = 'id_medidor', right_on = 'ID Medidor', 
                                 how = "inner") 
    #selecciona las columnas
    #selecciona las columnas
    consulta_combinada = consulta_combinada[['id_medidor', 'variable', 'valor', 'fecha', 
                                             'Nombre DU', 'Jerarquía', 'Nombre Inmueble', 'Sistema Equipo',
                                             'ID Inmueble', 'Nombre Cliente', 'Estado medidor']] 
    #cambiar jerarquía a un str 
    consulta_combinada["Jerarquía"] = consulta_combinada["Jerarquía"].astype(str)
    consulta_combinada = consulta_combinada[consulta_combinada["Jerarquía"] != 'nan'] #elimina los 'nan' de Jerarquía
    consulta_combinada["Jerarquía"] = consulta_combinada["Jerarquía"].astype(float) #convierte a flot 
    consulta_combinada["Jerarquía"] = consulta_combinada["Jerarquía"].astype(int) #eliminar punto decimal
    consulta_combinada["Jerarquía"] = consulta_combinada["Jerarquía"].astype(str) #otra vez str para que sea un factor
    
    ## verificar que ID inmueble es un str
    
    consulta_combinada["ID Inmueble"] = consulta_combinada["ID Inmueble"].astype(str)
    consulta_combinada = consulta_combinada[consulta_combinada["ID Inmueble"] != 'nan'] #elimina los 'nan' de ID Inmueble
    # check if there is a string in the column ID Inmueble that is not a number neither int or float and remove it
    consulta_combinada = consulta_combinada[consulta_combinada["ID Inmueble"].apply(lambda x: x.isnumeric())]
    consulta_combinada["ID Inmueble"] = consulta_combinada["ID Inmueble"].astype(float) #convierte a flot 
    consulta_combinada["ID Inmueble"] = consulta_combinada["ID Inmueble"].astype(int) #eliminar punto decimal
    consulta_combinada["ID Inmueble"] = consulta_combinada["ID Inmueble"].astype(str) #otra vez str para que sea un factor
    
    
    #filtra medidores activos
    consulta_combinada = consulta_combinada[consulta_combinada['Estado medidor'] == 'Activo']
    consulta_combinada = consulta_combinada.fillna(0)
    
    
    #Definir periodo
    fecha_max = consulta_combinada.fecha.max()
    fecha_min = consulta_combinada.fecha.min()

    consulta_combinada['dia'] = consulta_combinada['fecha'].dt.dayofweek
    
    return consulta_combinada

def conocer_id_inmuebles(consulta): #funcion que imprime la lista de inmuebles de la organization_id junto al ID Inmueble
    
    inmuebles = consulta[['Nombre Inmueble', 'ID Inmueble']]
    inmuebles = inmuebles.drop_duplicates()
    return inmuebles

def get_meters_names(parent_id, descendants):
    conn = get_connection()

    # Convert list to comma-separated string
    descendant_ids = ', '.join(map(str, descendants[parent_id]))
    if len(descendant_ids) == 0:
        descendant_ids = 'NULL'
        query = f"""
        SELECT
            ml.location_id,
            ml.meter_id,
            m.name AS meter_name
        FROM
            usage_management.meters_locations ml
        JOIN
            usage_management.meters m ON ml.meter_id = m.id
        """
    else:
            
        query = f"""
        SELECT
            ml.location_id,
            ml.meter_id,
            m.name AS meter_name
        FROM
            usage_management.meters_locations ml
        JOIN
            usage_management.meters m ON ml.meter_id = m.id
        WHERE
            ml.location_id IN ({descendant_ids});
        """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_descendants(data, parent_ids):
    descendants = {}
    for parent_id in parent_ids:
        descendants[parent_id] = []
        if parent_id in data:
            if 'children' in data[parent_id]:
                descendants[parent_id].extend(get_descendants_helper(data[parent_id]['children']))
    return descendants

def get_descendants_helper(node):
    descendants = []
    for child_id, child_data in node.items():
        descendants.append(child_id)
        if 'children' in child_data:
            descendants.extend(get_descendants_helper(child_data['children']))
    return descendants


def build_hierarchy(df, parent_id=None):
    hierarchy = {}
    if pd.isnull(parent_id):
        subset = df[df['parent_id'].isnull()]
    else:
        subset = df[df['parent_id'] == parent_id]
    

    for index, row in subset.iterrows():

        item = {'name': row['name']}
        children = build_hierarchy(df, parent_id=row['id'])
        if children:
            item['children'] = children
            
        hierarchy[row['id']] = item
    return hierarchy

def get_power_data(df, organization_id, start_date, end_date):
    conn = get_connection()

    query = """
    SELECT
      hh.date AS Fecha,"""
    
    # Generate SUM(CASE...) expressions for each meter
    for index, row in df.iterrows():
        query += f"""
      SUM(CASE WHEN m.id = '{row['meter_id']}' THEN hh.value END) AS "{row['meter_name']}", """

    query = query.rstrip(', ')  # Remove trailing comma
    query += f"""
    FROM
        usage_management.history_hourly hh
    INNER JOIN
        usage_management.meters m ON hh.meter_id = m.id
    WHERE
        hh.date BETWEEN '{start_date}' AND '{end_date}'
        AND m.organization_id = {organization_id}
        AND m.id IN ("""
    
    # Add meter IDs to the IN clause
    meter_ids = "', '".join(df['meter_id'])
    query += f"'{meter_ids}')"
    
    query += """
        AND hh.event_code = 'act_pwr'
    GROUP BY
        hh.date
    ORDER BY
        hh.date
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# get energy data
def get_ener_data(df, organization_id, start_date, end_date):
    conn = get_connection()

    query = """
    SELECT
      hh.date AS Fecha,"""
    
    # Generate SUM(CASE...) expressions for each meter
    for index, row in df.iterrows():
        query += f"""
      SUM(CASE WHEN m.id = '{row['meter_id']}' THEN hh.value END) AS "{row['meter_name']}", """

    query = query.rstrip(', ')  # Remove trailing comma
    query += f"""
    FROM
        usage_management.history_hourly hh
    INNER JOIN
        usage_management.meters m ON hh.meter_id = m.id
    WHERE
        hh.date BETWEEN '{start_date}' AND '{end_date}'
        AND m.organization_id = {organization_id}
        AND m.id IN ("""
    
    # Add meter IDs to the IN clause
    meter_ids = "', '".join(df['meter_id'])
    query += f"'{meter_ids}')"
    
    query += """
        AND hh.event_code = 'act_ene'
    GROUP BY
        hh.date
    ORDER BY
        hh.date
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

def range_selector(data, min_date, max_date):
    # Filter data between min_date and max_date
    min_date = pd.to_datetime(min_date)

    # convert max_date to datetime
    max_date = pd.to_datetime(max_date)

    data = data[(data['fecha'] >= min_date) & (data['fecha'] <= max_date)]
    return data