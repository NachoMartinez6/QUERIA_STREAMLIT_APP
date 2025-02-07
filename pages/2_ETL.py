import streamlit as st


st.sidebar.success("Select a page above.")
image_folder = "images/ETL_images"

############################## 1. Extracción de nuestra DATA


st.markdown('<h1>Quer<span style="color:dodgerblue">IA</span> - ETL ', unsafe_allow_html=True)
st.markdown("""
## 1. Extracción de nuestra DATA

**Paso previo:** Recogida por parte de nuestro analista de los registros correspondientes a datos de electricidad, gas y otros aspectos del panorama energetico dentro de la Unión europea.

**Objetivo:** En este apartado se pretende subir los 3 datasets crudos, concatenarlos en un unico dataset final energy_dataset y transformar los datos, ya que el energy_dataset se cargará al servidor en la nube y tiene que ser facilmente interpretable por la IA para transformar nuestra consulta a lenguaje SQL y devolver una respuesta clara y precisa.""")

    
code = """ 
# Import our libraries
import pandas as pd
import warnings

warnings.filterwarnings(
    'ignore',
    '.*',
    UserWarning,
    'warnings_filter',
)
"""

st.code(code, language="python")


code = """ 
# Dataset 1: precios de electricidad
electricity_dataset=pd.read_csv('data/Electricity_prices_eu.csv')

# Cambiamos el nombre de la columna de OBS_VALUE para diferenciarla de cada dataset 
# Esto es debido a que representan valores distintos aunque compartan el mismo nombre
electricity_dataset.rename(columns={'OBS_VALUE': 'electricity_price_eur/kWh'}, inplace=True)
electricity_dataset
"""
st.code(code, language="python")
st.image(f"{image_folder}/1_ETL.png")



code = """ 
# Dataset 2: precios del gas
gas_dataset=pd.read_csv('data/Gas_prices_eu.csv', sep=';')

# cambiamos el nombre de la columna de OBS_VALUE para diferenciarla para cada dataset
gas_dataset.rename(columns={'OBS_VALUE': 'gas_price_eur/GJ'}, inplace=True)
gas_dataset
"""
st.code(code, language="python")
st.image(f"{image_folder}/2_ETL.png")


code = """ 
# Dataset 3: balance energético
balance_dataset=pd.read_csv('data/Energy_balance_eu.csv', sep=';')

# cambiamos el nombre de la columna de OBS_VALUE para diferenciarla para cada dataset
balance_dataset.rename(columns={'OBS_VALUE': 'energy_GWh'}, inplace=True)
balance_dataset
"""
st.code(code, language="python")
st.image(f"{image_folder}/3_ETL.png")



############################## 2. Tranformación de nuestra DATA

st.markdown("""## 2. Tranformación de nuestra DATA

Como en muchos casos de un proyecto de analitica de datos, los datos iniciales vienen con formatos distintos, por los que será necesario una transformación de los datos para que estos tengan el mismo formato y nos sean de utilidad.

**Tarea:** Para unir los 3 datasets en uno único (energy_dataset) tenemos que igualar el numero de columnas y completar los datos con Nulos
""")





code = """ 
# Filtramos las columnas de interés para cada dataset
electricity_dataset=electricity_dataset[['TIME_PERIOD','geo','product','indic_en', 'electricity_price_eur/kWh']]
gas_dataset=gas_dataset[['TIME_PERIOD','geo','product','indic_en','gas_price_eur/GJ']]
balance_dataset=balance_dataset[['TIME_PERIOD','geo','nrg_bal','siec','energy_GWh']]

# Creamos columnas extras con valores nulos para cada dataset, para que los 3 dataset contengan las mismas columnas
electricity_dataset['nrg_bal']=None
electricity_dataset['siec']=None
electricity_dataset['gas_price_eur/GJ']=None
electricity_dataset['energy_GWh']=None

gas_dataset['nrg_bal']=None
gas_dataset['siec']=None
gas_dataset['electricity_price_eur/kWh']=None
gas_dataset['energy_GWh']=None

balance_dataset['product']='Energy balance'
balance_dataset['indic_en']=None
balance_dataset['electricity_price_eur/kWh']=None
balance_dataset['gas_price_eur/GJ']=None

# Reordenamos columnas para que todos los df tengan el mismo formato
electricity_dataset=electricity_dataset[
    ['TIME_PERIOD',
     'geo',
     'product',
     'nrg_bal',
     'siec',
     'indic_en',
     'energy_GWh', 
     'electricity_price_eur/kWh', 
     'gas_price_eur/GJ']
]
gas_dataset=gas_dataset[
    ['TIME_PERIOD',
     'geo',
     'product',
     'nrg_bal',
     'siec',
     'indic_en',
     'energy_GWh', 
     'electricity_price_eur/kWh', 
     'gas_price_eur/GJ']
]
balance_dataset=balance_dataset[
    ['TIME_PERIOD',
     'geo',
     'product',
     'nrg_bal',
     'siec',
     'indic_en',
     'energy_GWh', 
     'electricity_price_eur/kWh', 
     'gas_price_eur/GJ']
]

# Unimos los 3 dataset en un solo energy_dataset concatenando los valores (se suma el numero de filas)
energy_dataset = pd.concat([electricity_dataset, gas_dataset, balance_dataset], ignore_index=True)

# Eliminamos los datos de total Europeo del dataset ya que no son de interés en este caso
energy_dataset = energy_dataset[energy_dataset['geo'] != 'EU27_2020']

# Comprobamos que se ha concatenado correctamente
energy_dataset
"""
st.code(code, language="python")
st.image(f"{image_folder}/4_ETL.png")


code = """energy_dataset.rename(columns={
    'TIME_PERIOD': 'time_period',
    'geo': 'country', 
    'product': 'data_type',
    'nrg_bal': 'energy_category', 
    'siec': 'energy_product_class', 
    'indic_en': 'costumer'}, inplace=True)

energy_dataset
"""
st.code(code, language="python")
st.image(f"{image_folder}/5_ETL.png")


code = """
# Traducimos los códigos los valores unicos de cada columna para que sea facilmente comprensible para la IA

# valores de pais
# para consultar valores unicos usamos: energy_dataset['country'].unique()
energy_dataset['country'] = energy_dataset['country'].replace({
    'DE': 'Germany',
    'ES': 'Spain',
    'FR': 'France',
    'IT': 'Italy',
    'PT': 'Portugal'})

# valores de tipo de dato (tipo de dato que mostramos, si es balance energético, precio de gas o de electricidad)
# para consultar valores unicos usamos: energy_dataset['product'].unique()
energy_dataset['data_type'] = energy_dataset['data_type'].replace({
    6000: 'Electricity price',
    4100: 'Gas price'})

# valores de categoría energética
energy_dataset['energy_category']=energy_dataset['energy_category'].replace({
    'EXP': 'Exports',
    'GAE': 'Gross available energy', 
    'GIC': 'Gross inland consumption',
    'IMP': 'Imports',
    'NRGSUP': 'Total energy supply',
    'PPRD': 'Primary production'})

# valores de clase de producto energético
energy_dataset['energy_product_class']=energy_dataset['energy_product_class'].replace({
    'C0000X0350-0370': 'Solid fossil fuels', 
    'G3000': 'Natural gas', 
    'N900H': 'Nuclear heat', 
    'O4000XBIO': 'Oil and petroleum products (excluding biofuel portion)', 
    'RA000': 'Renewables and biofuels',
    'RA420': 'Solar photovoltaic', 
    'TOTAL': 'Total'})

# valores de tipo de cliente
energy_dataset['costumer']=energy_dataset['costumer'].replace({
    'MSHH':'Medium size households',
    'MSIND':'Non-household, medium size consumers'})


# dataframe final limpio:
energy_dataset
"""
st.code(code, language="python")
st.image(f"{image_folder}/6_ETL.png")

st.markdown("""## 3. Carga de la DATA

En esta etapa, guardaremos el dataset final en un fichero .csv dentro del mismo directorio que será cargado en la BBDD para la posterior interacción con la aplicación de IA.
""")

code = """
# Carga de datos
energy_dataset.to_csv('pages/energy_dataset.csv', index=False, sep=';', encoding='utf-8')

# Comprobamos que se guardo y se lee correctamente
df=pd.read_csv('data/energy_dataset.csv', sep=';')
df
"""
st.code(code, language="python")
st.image(f"{image_folder}/7_ETL.png")
