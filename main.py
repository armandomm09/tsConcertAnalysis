# streamlit_app.py

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Análisis de Reproducciones de Taylor Swift", layout="wide")

st.title("Análisis de Cambios en las Reproducciones de Taylor Swift Antes y Después de sus Conciertos")

# Datos de los conciertos
concerts = {
    "Tokyo": "Feb 7, 2024",
    "Melbourne": "Feb 16, 2024",
    "Sydney": "Feb 23, 2024",
    "Singapore": "Mar 2, 2024",
    "Stockholm": "May 17, 2024",
    "Dublin": "Jun 28, 2024",
    "Paris": "Jun 3, 2024",
    "London": "Jun 21, 2024",
    "Orlando": "Oct 18, 2024",
    "Rio de Janeiro": "Nov 17, 2024"
}

# Convertir las fechas de los conciertos a formato datetime
concert_dates = {city: datetime.strptime(date, "%b %d, %Y") for city, date in concerts.items()}

# Cargar los datos desde el archivo CSV
try:
    # Asegúrate de que 'ts_stream_data.csv' esté en el mismo directorio que este script,
    # o proporciona la ruta completa al archivo.
    data = pd.read_csv('ts_stream_data.csv', parse_dates=['Date'])
    data.set_index('Date', inplace=True)
except FileNotFoundError:
    st.error("El archivo 'ts_stream_data.csv' no se encontró. Por favor, asegúrate de que el archivo exista en el directorio actual.")
    st.stop()

# Asegurarse de que las columnas numéricas estén en el tipo correcto
for city in concerts.keys():
    if city in data.columns:
        data[city] = pd.to_numeric(data[city], errors='coerce')

# Interfaz de usuario en Streamlit
st.sidebar.title("Opciones de Visualización")
city_options = list(concert_dates.keys())
selected_city = st.sidebar.selectbox("Selecciona una ciudad:", city_options)

# Obtener la fecha del concierto
concert_date = concert_dates[selected_city]

# Definir el rango de fechas (un mes antes y después del concierto)
start_date = concert_date - timedelta(days=30)
end_date = concert_date + timedelta(days=30)

# Filtrar los datos dentro del rango de fechas
city_data = data.loc[start_date:end_date, selected_city].dropna()

if not city_data.empty:
    # Crear la figura y los ejes
    fig, ax = plt.subplots(figsize=(12, 6))

    # Gráficar los cambios porcentuales
    ax.plot(city_data.index, city_data.values, marker='o', label='Cambios en las reproducciones')

    # Línea vertical para la fecha del concierto
    ax.axvline(x=concert_date, color='r', linestyle='--', label='Fecha del concierto')

    # Configurar el gráfico
    ax.set_title(f'Cambios en las reproducciones en {selected_city}', fontsize=16)
    ax.set_xlabel('Fecha', fontsize=14)
    ax.set_ylabel('Cambio porcentual (%)', fontsize=14)
    ax.legend()
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Mostrar estadísticas adicionales
    st.subheader(f"Análisis Estadístico para {selected_city}")

    # Datos antes y después del concierto
    pre_concert_data = city_data[city_data.index < concert_date]
    post_concert_data = city_data[city_data.index >= concert_date]

    # Calcular el cambio porcentual promedio antes y después del concierto
    if not pre_concert_data.empty:
        avg_pre_concert = pre_concert_data.mean()
        st.write(f"Cambio porcentual promedio **antes** del concierto: {avg_pre_concert:.2f}%")
    else:
        st.write("No hay datos disponibles **antes** del concierto.")

    if not post_concert_data.empty:
        avg_post_concert = post_concert_data.mean()
        st.write(f"Cambio porcentual promedio **después** del concierto: {avg_post_concert:.2f}%")
    else:
        st.write("No hay datos disponibles **después** del concierto.")

    # Calcular el cambio total entre los períodos
    if not pre_concert_data.empty and not post_concert_data.empty:
        percent_change = ((avg_post_concert - avg_pre_concert) / abs(avg_pre_concert)) * 100
        st.write(f"Cambio porcentual total en reproducciones después del concierto: {percent_change:.2f}%")
else:
    st.write(f"No hay datos disponibles para {selected_city} en el rango de fechas especificado.")

# Mostrar la tabla de datos si el usuario lo desea
if st.sidebar.checkbox("Mostrar datos en tabla"):
    st.subheader("Datos de Reproducciones")
    st.dataframe(city_data)
