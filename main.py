# streamlit_app.py

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy.stats import ttest_ind

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Análisis de Reproducciones de Taylor Swift", layout="wide")

# Estilos de Seaborn
sns.set_style("whitegrid")

# Título de la aplicación
st.title("Análisis de Cambios en las Reproducciones de Taylor Swift Antes y Después de sus Conciertos")

# Sección de introducción
st.write("""
## Introducción

Este análisis examina cómo cambian las reproducciones de Taylor Swift en Spotify un mes antes y después de sus conciertos en diferentes ciudades. Al seleccionar una ciudad, puedes visualizar estos cambios y entender mejor el impacto que tienen los conciertos en el interés de los oyentes.

Utiliza las opciones en la barra lateral para seleccionar una ciudad y ajustar el rango de fechas de análisis.
""")



# Datos de los conciertos
concerts = {
    "Sao Paulo": "Nov 23, 2023",
    "Melbourne": "Feb 16, 2024",
    "Sydney": "Feb 23, 2024",
    "Singapore": "Mar 2, 2024",
    "Stockholm": "May 17, 2024",
    "Manchester": "Jun 13, 2024",
    "Dublin": "Jun 28, 2024",
    "Paris": "Jun 3, 2024",
    "London": "Jun 21, 2024",
}

# Convertir las fechas de los conciertos a formato datetime
concert_dates = {city: datetime.strptime(date, "%b %d, %Y") for city, date in concerts.items()}

# Cargar los datos desde el archivo CSV
@st.cache_data
def load_data():
    data = pd.read_csv('ts_stream_data.csv', parse_dates=['Date'])
    data.set_index('Date', inplace=True)
    return data

try:
    data = load_data()
except FileNotFoundError:
    st.error("El archivo 'ts_stream_data.csv' no se encontró. Asegúrate de que el archivo exista en el directorio actual.")
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

# Definir el rango de fechas predeterminado (un mes antes y después del concierto)
default_start_date = concert_date - timedelta(days=30)
default_end_date = concert_date + timedelta(days=30)

# Añadir controles para el rango de fechas
st.sidebar.subheader("Ajuste del Rango de Fechas")
date_range = st.sidebar.slider(
    "Selecciona el rango de fechas:",
    min_value=data.index.min().date(),
    max_value=data.index.max().date(),
    value=(default_start_date.date(), default_end_date.date())
)

start_date, end_date = [datetime.combine(d, datetime.min.time()) for d in date_range]

# Filtrar los datos dentro del rango de fechas
city_data = data.loc[start_date:end_date, selected_city].dropna()

if not city_data.empty:
    # Crear la figura y los ejes con Seaborn
    fig, ax = plt.subplots(figsize=(12, 6))

    # Graficar los cambios porcentuales
    sns.lineplot(x=city_data.index, y=city_data.values, marker='o', ax=ax, label='Cambios en las reproducciones')

    # Línea vertical para la fecha del concierto con anotación
    ax.axvline(x=concert_date, color='r', linestyle='--')
    ax.text(concert_date, ax.get_ylim()[1]*0.9, 'Fecha del Concierto', rotation=90, color='red', verticalalignment='center')

    # Configurar el gráfico
    ax.set_title(f'Cambios en las reproducciones en {selected_city}', fontsize=16)
    ax.set_xlabel('Fecha', fontsize=14)
    ax.set_ylabel('Cambio porcentual (%)', fontsize=14)
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Mostrar estadísticas adicionales
    st.subheader(f"Análisis Estadístico para {selected_city}")

    # Datos antes y después del concierto
    pre_concert_data = city_data[city_data.index < concert_date]
    post_concert_data = city_data[city_data.index >= concert_date]

    # Calcular estadísticas antes del concierto
    if not pre_concert_data.empty:
        avg_pre_concert = pre_concert_data.mean()
        std_pre_concert = pre_concert_data.std()
        max_pre_concert = pre_concert_data.max()
        min_pre_concert = pre_concert_data.min()
        st.write(f"**Antes del concierto**:")
        st.write(f"- Cambio porcentual promedio: {avg_pre_concert:.2f}%")
        st.write(f"- Desviación estándar: {std_pre_concert:.2f}%")
        st.write(f"- Máximo cambio: {max_pre_concert:.2f}%")
        st.write(f"- Mínimo cambio: {min_pre_concert:.2f}%")
    else:
        st.write("No hay datos disponibles **antes** del concierto.")

    # Calcular estadísticas después del concierto
    if not post_concert_data.empty:
        avg_post_concert = post_concert_data.mean()
        std_post_concert = post_concert_data.std()
        max_post_concert = post_concert_data.max()
        min_post_concert = post_concert_data.min()
        st.write(f"**Después del concierto**:")
        st.write(f"- Cambio porcentual promedio: {avg_post_concert:.2f}%")
        st.write(f"- Desviación estándar: {std_post_concert:.2f}%")
        st.write(f"- Máximo cambio: {max_post_concert:.2f}%")
        st.write(f"- Mínimo cambio: {min_post_concert:.2f}%")
    else:
        st.write("No hay datos disponibles **después** del concierto.")

    # Calcular el cambio total entre los períodos
    if not pre_concert_data.empty and not post_concert_data.empty:
        percent_change = ((avg_post_concert - avg_pre_concert) / abs(avg_pre_concert)) * 100
        st.write(f"**Cambio porcentual total en reproducciones después del concierto:** {percent_change:.2f}%")

        # Prueba t de Student
        t_stat, p_value = ttest_ind(post_concert_data, pre_concert_data, equal_var=False)
        st.write(f"**Prueba t de Student:** estadístico t = {t_stat:.2f}, valor p = {p_value:.4f}")
        if p_value < 0.05:
            st.write("La diferencia en las reproducciones es **estadísticamente significativa**.")
        else:
            st.write("No se encontró una diferencia estadísticamente significativa en las reproducciones.")
    else:
        st.write("No se puede realizar un análisis comparativo completo debido a la falta de datos.")

    # Mostrar la tabla de datos si el usuario lo desea
    if st.sidebar.checkbox("Mostrar datos en tabla"):
        st.subheader("Datos de Reproducciones")
        st.dataframe(city_data)
else:
    st.write(f"No hay datos disponibles para {selected_city} en el rango de fechas especificado.")

# Sección de conclusiones
st.write("""
## Conclusiones

Este análisis proporciona una visión detallada de cómo las reproducciones de Taylor Swift cambian alrededor de las fechas de sus conciertos en diferentes ciudades. Observa las tendencias y considera cómo eventos locales pueden influir en el interés por su música.

Explora diferentes ciudades y ajusta el rango de fechas para descubrir patrones interesantes.
""")

# Sección opcional: Comparación entre ciudades
st.sidebar.subheader("Comparación entre Ciudades")
compare_cities = st.sidebar.multiselect("Selecciona las ciudades para comparar:", city_options, default=[selected_city])

if compare_cities:
    st.subheader("Comparación de Cambios en Reproducciones entre Ciudades")
    comparison_list = []  # Inicializamos una lista vacía

    for city in compare_cities:
        # Obtener datos para cada ciudad
        city_concert_date = concert_dates[city]
        city_start_date = city_concert_date - timedelta(days=30)
        city_end_date = city_concert_date + timedelta(days=30)
        city_series = data.loc[city_start_date:city_end_date, city].dropna()

        if not city_series.empty:
            avg_pre = city_series[city_series.index < city_concert_date].mean()
            avg_post = city_series[city_series.index >= city_concert_date].mean()
            if pd.notnull(avg_pre) and pd.notnull(avg_post):
                percent_change = ((avg_post - avg_pre) / abs(avg_pre)) * 100
                # Agregamos el diccionario a la lista
                comparison_list.append({'Ciudad': city, 'Cambio porcentual': percent_change})

    if comparison_list:
        # Creamos el DataFrame a partir de la lista
        comparison_data = pd.DataFrame(comparison_list)
        # Graficar el cambio porcentual para cada ciudad seleccionada
        fig_comp, ax_comp = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Ciudad', y='Cambio porcentual', data=comparison_data, ax=ax_comp)
        ax_comp.set_title('Cambio Porcentual en Reproducciones Después del Concierto')
        ax_comp.set_ylabel('Cambio porcentual (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig_comp)
    else:
        st.write("No hay suficientes datos para comparar las ciudades seleccionadas.")

st.write("""
##### Este analisis fue hecho por:
Pablo Armando Mac Beath Milián\n
Cristina Sánchez Rivera\n
Oscar Galán Franco\n
Emilio Pineda Tovar """)