import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from io import StringIO

# Configuración de la página
st.set_page_config(page_title="Analizador de Farmacias GT", layout="wide")

# Selección de idioma
language = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])
lang_dict = {
    "Español": {
        "title": "Analizador de Farmacias GT",
        "subtitle": "Optimiza las ventas e inventarios para tu cadena de farmacias en Guatemala",
        "instructions": """
        1. **Carga tus datos**: Sube un CSV con columnas `Drug_Name`, `Sales_2024 (USD)`, `Region` y `Generic` (1 para genéricos, 0 para marcas).
        2. **Filtra por ventas y región**: Usa los sliders y el selector para analizar ventas por rango y departamento.
        3. **Selecciona un medicamento**: Elige un medicamento del menú para ver detalles y recomendaciones de inventario.
        4. **Analiza con IA**: Haz clic en "Analizar con IA" para obtener tendencias del medicamento seleccionado.
        5. **Análisis manual**: Ingresa un nombre para analizar cualquier medicamento.
        """,
        "load_data": "Carga tus datos",
        "upload_label": "Sube un CSV con datos de ventas",
        "success": "Datos cargados exitosamente",
        "explore": "Explora los Medicamentos",
        "min_sales": "Ventas mínimas (millones USD)",
        "max_sales": "Ventas máximas (millones USD)",
        "region_filter": "Filtrar por Región",
        "select_med": "Elige un medicamento:",
        "data_med": "Datos del medicamento seleccionado:",
        "inventory": "Inventario mínimo recomendado (unidades):",
        "analyze_btn": "Analizar este medicamento con IA",
        "analyze_title": "Análisis de tendencias manual",
        "input_med": "Ingresa un medicamento para analizar",
        "analyze_manual_btn": "Analizar manualmente",
        "filtered": "Medicamentos filtrados:",
        "error_cols": "El CSV debe contener `Drug_Name`, `Sales_2024 (USD)`, `Region` y `Generic`."
    },
    "English": {
        "title": "Pharmacy Analyzer GT",
        "subtitle": "Optimize sales and inventory for your pharmacy chain in Guatemala",
        "instructions": """
        1. **Load your data**: Upload a CSV with columns `Drug_Name`, `Sales_2024 (USD)`, `Region`, and `Generic` (1 for generics, 0 for brands).
        2. **Filter by sales and region**: Use sliders and selector to analyze sales by range and department.
        3. **Select a medicine**: Choose a medicine from the dropdown to view details and inventory suggestions.
        4. **Analyze with AI**: Click "Analyze with AI" for trends on the selected medicine.
        5. **Manual analysis**: Enter a name to analyze any medicine.
        """,
        "load_data": "Load your data",
        "upload_label": "Upload a CSV with sales data",
        "success": "Data loaded successfully",
        "explore": "Explore Medicines",
        "min_sales": "Minimum Sales (million USD)",
        "max_sales": "Maximum Sales (million USD)",
        "region_filter": "Filter by Region",
        "select_med": "Choose a medicine:",
        "data_med": "Selected medicine data:",
        "inventory": "Recommended minimum inventory (units):",
        "analyze_btn": "Analyze this medicine with AI",
        "analyze_title": "Manual Trend Analysis",
        "input_med": "Enter a medicine to analyze",
        "analyze_manual_btn": "Analyze manually",
        "filtered": "Filtered medicines:",
        "error_cols": "The CSV must contain `Drug_Name`, `Sales_2024 (USD)`, `Region`, and `Generic`."
    }
}

# --- Manejo de la API Key con Streamlit Secrets ---
API_KEY = st.secrets["API_KEY"]

# --- Función para llamar a la API de Gemini ---
def call_gemini_api(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 1, "topK": 40, "topP": 0.95, "maxOutputTokens": 8192, "responseMimeType": "text/plain"}
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.text if response.status_code == 200 else None

# --- Configuración de la interfaz ---
st.title(lang_dict[language]["title"])
st.subheader(lang_dict[language]["subtitle"])

st.sidebar.header("Instrucciones / Instructions")
st.sidebar.markdown(lang_dict[language]["instructions"])

st.sidebar.header(lang_dict[language]["load_data"])
uploaded_file = st.sidebar.file_uploader(lang_dict[language]["upload_label"], type=["csv"])

data = None
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.sidebar.success(lang_dict[language]["success"])
    st.write("Vista previa / Preview:")
    st.dataframe(data.head())

    # --- Filtros y Menú ---
    st.header(lang_dict[language]["explore"])
    required_cols = ["Drug_Name", "Sales_2024 (USD)", "Region", "Generic"]
    if all(col in data.columns for col in required_cols):
        # Filtro por rango de ventas
        min_sales = st.sidebar.slider(lang_dict[language]["min_sales"], 
                                      float(data["Sales_2024 (USD)"].min()), 
                                      float(data["Sales_2024 (USD)"].max()), 
                                      float(data["Sales_2024 (USD)"].min()))
        max_sales = st.sidebar.slider(lang_dict[language]["max_sales"], 
                                      float(data["Sales_2024 (USD)"].min()), 
                                      float(data["Sales_2024 (USD)"].max()), 
                                      float(data["Sales_2024 (USD)"].max()))
        
        # Filtro por región (departamentos de Guatemala)
        regiones = data["Region"].unique().tolist()
        region_filter = st.sidebar.multiselect(lang_dict[language]["region_filter"], regiones, default=regiones)

        # Filtrar datos
        filtered_data = data[(data["Sales_2024 (USD)"] >= min_sales) & 
                             (data["Sales_2024 (USD)"] <= max_sales) & 
                             (data["Region"].isin(region_filter))]
        
        st.write(f"{lang_dict[language]['filtered']} {len(filtered_data)}")
        st.dataframe(filtered_data)

        # Menú desplegable
        medicamentos = filtered_data["Drug_Name"].tolist()
        medicamento_seleccionado = st.selectbox(lang_dict[language]["select_med"], medicamentos)
        
        if medicamento_seleccionado:
            datos_medicamento = filtered_data[filtered_data["Drug_Name"] == medicamento_seleccionado]
            st.write(lang_dict[language]["data_med"])
            st.dataframe(datos_medicamento)
            
            # Gráfico
            fig = px.bar(datos_medicamento, x="Drug_Name", y="Sales_2024 (USD)", 
                         title=f"Ventas de {medicamento_seleccionado} en 2024",
                         labels={"Sales_2024 (USD)": "Ventas (millones USD)"},
                         text=datos_medicamento["Sales_2024 (USD)"].apply(lambda x: f"{x:.2f}"))
            fig.update_traces(textposition='auto')
            st.plotly_chart(fig, use_container_width=True)

            # Inventario mínimo recomendado (ejemplo simple: 10% de ventas en unidades asumidas)
            sales = datos_medicamento["Sales_2024 (USD)"].values[0]
            inventory_suggestion = int(sales * 1000 * 0.1)  # Asume $1M USD = 1000 unidades
            st.write(f"{lang_dict[language]['inventory']} {inventory_suggestion}")

            # Botón para análisis con Gemini
            if st.button(lang_dict[language]["analyze_btn"]):
                prompt = f"Proporciona un análisis breve de las tendencias actuales del medicamento '{medicamento_seleccionado}' en Guatemala."
                resultado = call_gemini_api(prompt)
                if resultado:
                    st.write("Análisis de tendencias / Trend Analysis:")
                    st.write(resultado)
    else:
        st.error(lang_dict[language]["error_cols"])

# --- Análisis manual ---
st.header(lang_dict[language]["analyze_title"])
medicamento_input = st.text_input(lang_dict[language]["input_med"], "Ibuprofeno")
if st.button(lang_dict[language]["analyze_manual_btn"]):
    prompt = f"Proporciona un análisis breve de las tendencias actuales del medicamento '{medicamento_input}' en Guatemala."
    resultado = call_gemini_api(prompt)
    if resultado:
        st.write("Resultado del análisis / Analysis Result:")
        st.write(resultado)

# --- Footer ---
st.markdown("---")
st.write("Analizador de Farmacias GT © 2025 - Desarrollado para cadenas de farmacias en Guatemala")
