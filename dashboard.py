import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="NEXO Commerce Dashboard", layout="wide")

st.title("📊 Panel de Control - NEXO Commerce")
st.markdown("Bienvenido al análisis de datos de ventas de NEXO Commerce.")

# Intentar cargar el archivo CSV
try:
    df = pd.read_csv("dataset_limpio.csv")
except FileNotFoundError:
    st.error("No se encontró el archivo 'dataset_limpio.csv'. Asegúrate de tenerlo subido en este mismo repositorio de GitHub.")
    st.stop()

# Limpiar espacios en los nombres de las columnas
df.columns = df.columns.str.strip()

# Buscar columnas clave automáticamente (sin importar mayúsculas/minúsculas)
col_pais = next((col for col in df.columns if col.lower() in ['country', 'pais', 'país']), None)
col_ventas = next((col for col in df.columns if col.lower() in ['sales', 'ventas', 'total', 'monto']), None)
col_producto = next((col for col in df.columns if col.lower() in ['product', 'producto', 'item']), None)

# Sidebar para Filtros
st.sidebar.header("Filtros")

if col_pais:
    paises_disponibles = df[col_pais].dropna().unique()
    paises_seleccionados = st.sidebar.multiselect(
        "Filtrar por País",
        options=paises_disponibles,
        default=paises_disponibles[:3] if len(paises_disponibles) >= 3 else paises_disponibles
    )
    # Filtrar datos
    if paises_seleccionados:
        df_filtered = df[df[col_pais].isin(paises_seleccionados)]
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()
    st.sidebar.warning("No se detectó la columna de País en el dataset.")

# --- Tarjetas de KPI's principales en la parte superior ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Registros", f"{len(df_filtered):,}")

with col2:
    if col_ventas:
        total_ventas = df_filtered[col_ventas].sum()
        st.metric("Ventas Totales", f"${total_ventas:,.2f}")
    else:
        st.metric("Ventas Totales", "N/A")

with col3:
    if col_producto:
        total_productos = df_filtered[col_producto].nunique()
        st.metric("Productos Únicos", f"{total_productos:,}")
    else:
        st.metric("Productos Únicos", "N/A")

st.markdown("---")

# --- Gráficos del Dashboard ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Distribución de Ventas")
    if col_ventas and col_producto:
        # Gráfico de barras de ventas por producto
        df_prod = df_filtered.groupby(col_producto)[col_ventas].sum().reset_index().sort_values(by=col_ventas, ascending=False).head(10)
        fig_bar = px.bar(
            df_prod, 
            x=col_producto, 
            y=col_ventas, 
            title="Top 10 Productos más Vendidos",
            labels={col_producto: "Producto", col_ventas: "Ventas ($)"},
            template="seaborn"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sube columnas de Producto y Ventas para visualizar este gráfico.")

with col_g2:
    st.subheader("Análisis de Dispersión")
    if col_ventas and col_pais:
        # Gráfico de dispersión seguro usando el índice en X para evitar fallos
        fig_scatter = px.scatter(
            df_filtered,
            x=df_filtered.index,  
            y=col_ventas,
            color=col_pais,
            title="Distribución de Transacciones por País",
            labels={"index": "Número de Transacción", col_ventas: "Monto de Venta"},
            template="seaborn"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Sube columnas de País y Ventas para visualizar el gráfico de dispersión.")

# Mostrar tabla de datos abajo
st.subheader("Vista Previa de los Datos Filtrados")
st.dataframe(df_filtered.head(100))
