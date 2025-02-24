import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="PharmaTrend Analyzer", layout="wide")

# Título de la aplicación
st.title("PharmaTrend Analyzer")
st.subheader("Analiza tendencias de mercado para la industria farmacéutica")

# --- Manejo de la API Key con Streamlit Secrets ---
# Para usar esto, debes agregar tu API Key en un archivo `.streamlit/secrets.toml` con el formato:
# [secrets]
# API_KEY = "tu_clave_aqui"
API_KEY = st.secrets["API_KEY"]

# --- Función para llamar a la API de Gemini ---
def call_gemini_api(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 1,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
            "responseMimeType": "text/plain"
        }
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.text
    else:
        st.error(f"Error al conectar con la API: {response.status_code}")
        return None

# --- Sección de carga de datos ---
st.sidebar.header("Carga tus datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV con datos de ventas", type=["csv"])

if uploaded_file is not None:
    # Leer el archivo CSV
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("Datos cargados exitosamente")
    
    # Mostrar una vista previa de los datos
    st.write("Vista previa de los datos:")
    st.dataframe(data.head())

    # Suponiendo que el CSV tiene columnas como "Fecha", "Medicamento", "Ventas"
    if "Fecha" in data.columns and "Ventas" in data.columns:
        # Gráfico de tendencias
        fig = px.line(data, x="Fecha", y="Ventas", title="Tendencias de Ventas", 
                      labels={"Ventas": "Ventas (unidades)", "Fecha": "Fecha"})
        st.plotly_chart(fig, use_container_width=True)

# --- Sección de análisis de tendencias con la API ---
st.header("Análisis de tendencias")
medicamento = st.text_input("Ingresa el nombre de un medicamento para analizar tendencias", "Ibuprofeno")

if st.button("Analizar"):
    prompt = f"Proporciona un análisis breve de las tendencias actuales del medicamento '{medicamento}' en la industria farmacéutica."
    resultado = call_gemini_api(prompt)
    
    if resultado:
        st.write("Resultado del análisis:")
        st.write(resultado)

# --- Footer ---
st.markdown("---")
st.write("PharmaTrend Analyzer © 2025 - Desarrollado para la industria farmacéutica.")
