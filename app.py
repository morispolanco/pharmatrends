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
# [secrets]
# API_KEY = "tu_clave_aqui" en .streamlit/secrets.toml
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

# Variable para almacenar el DataFrame
data = None

if uploaded_file is not None:
    # Leer el archivo CSV
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("Datos cargados exitosamente")
    
    # Mostrar una vista previa de los datos
    st.write("Vista previa de los datos:")
    st.dataframe(data.head())

    # --- Filtros y Menú Desplegable ---
    st.header("Explora los Medicamentos")
    if "Drug_Name" in data.columns and "Sales_2024 (USD)" in data.columns:
        # Filtro por rango de ventas
        min_sales = st.sidebar.slider("Ventas mínimas (millones USD)", 
                                      float(data["Sales_2024 (USD)"].min()), 
                                      float(data["Sales_2024 (USD)"].max()), 
                                      float(data["Sales_2024 (USD)"].min()))
        max_sales = st.sidebar.slider("Ventas máximas (millones USD)", 
                                      float(data["Sales_2024 (USD)"].min()), 
                                      float(data["Sales_2024 (USD)"].max()), 
                                      float(data["Sales_2024 (USD)"].max()))
        
        # Filtrar datos según el rango de ventas
        filtered_data = data[(data["Sales_2024 (USD)"] >= min_sales) & 
                             (data["Sales_2024 (USD)"] <= max_sales)]
        
        st.write(f"Medicamentos filtrados: {len(filtered_data)}")
        st.dataframe(filtered_data)

        # Menú desplegable con los medicamentos filtrados
        medicamentos = filtered_data["Drug_Name"].tolist()
        medicamento_seleccionado = st.selectbox("Elige un medicamento:", medicamentos)
        
        # Mostrar datos del medicamento seleccionado
        if medicamento_seleccionado:
            datos_medicamento = filtered_data[filtered_data["Drug_Name"] == medicamento_seleccionado]
            st.write("Datos del medicamento seleccionado:")
            st.dataframe(datos_medicamento)
            
            # Gráfico de las ventas
            fig = px.bar(
                datos_medicamento, 
                x="Drug_Name", 
                y="Sales_2024 (USD)", 
                title=f"Ventas de {medicamento_seleccionado} en 2024",
                labels={"Sales_2024 (USD)": "Ventas (millones USD)"},
                text=datos_medicamento["Sales_2024 (USD)"].apply(lambda x: f"{x:.2f}")
            )
            fig.update_traces(textposition='auto')  # Mostrar valores en las barras
            st.plotly_chart(fig, use_container_width=True)

            # Botón para analizar con la API de Gemini
            if st.button("Analizar este medicamento con IA"):
                prompt = f"Proporciona un análisis breve de las tendencias actuales del medicamento '{medicamento_seleccionado}' en la industria farmacéutica."
                resultado = call_gemini_api(prompt)
                if resultado:
                    st.write("Análisis de tendencias:")
                    st.write(resultado)
    else:
        st.error("El archivo CSV debe contener las columnas 'Drug_Name' y 'Sales_2024 (USD)'.")

# --- Sección de análisis manual con la API ---
st.header("Análisis de tendencias manual")
medicamento_input = st.text_input("Ingresa el nombre de un medicamento para analizar tendencias", "Ibuprofeno")
if st.button("Analizar manualmente"):
    prompt = f"Proporciona un análisis breve de las tendencias actuales del medicamento '{medicamento_input}' en la industria farmacéutica."
    resultado = call_gemini_api(prompt)
    if resultado:
        st.write("Resultado del análisis:")
        st.write(resultado)

# --- Footer ---
st.markdown("---")
st.write("PharmaTrend Analyzer © 2025 - Desarrollado para la industria farmacéutica.")
