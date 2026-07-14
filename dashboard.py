import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración visual de la página
st.set_page_config(
    page_title="NEXO Commerce - Panel de Control", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título Principal del Dashboard
st.title("📊 Panel de Control - NEXO Commerce")
st.markdown("Bienvenido al análisis inteligente de ventas y rendimiento comercial.")

# 1. Cargar el dataset de manera segura
@st.cache_data # Cacheamos los datos para que el dashboard cargue volando ⚡
def cargar_datos():
    df = pd.read_csv("dataset_limpio.csv")
    # Limpiamos posibles espacios en blanco en los nombres de las columnas
    df.columns = df.columns.str.strip()
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'dataset_limpio.csv' en tu repositorio. Por favor, asegúrate de subirlo.")
    st.stop()

# 2. CONFIGURACIÓN DE FILTROS (Barra Lateral / Sidebar)
st.sidebar.header("🎯 Filtros de Análisis")

# Filtro 1: Selección de Países (country)
paises_disponibles = sorted(df['country'].dropna().unique())
paises_seleccionados = st.sidebar.multiselect(
    "Filtrar por País",
    options=paises_disponibles,
    default=paises_disponibles # Seleccionados todos por defecto
)

# Filtro 2: Selección de Categorías (category)
categorias_disponibles = sorted(df['category'].dropna().unique())
categorias_seleccionadas = st.sidebar.multiselect(
    "Filtrar por Categoría",
    options=categorias_disponibles,
    default=categorias_disponibles
)

# Filtro 3: Método de Pago (payment_method)
pagos_disponibles = sorted(df['payment_method'].dropna().unique())
pagos_seleccionados = st.sidebar.multiselect(
    "Método de Pago",
    options=pagos_disponibles,
    default=pagos_disponibles
)

# Aplicar todos los filtros en cascada sobre los datos originales
df_filtered = df[
    (df['country'].isin(paises_seleccionados)) &
    (df['category'].isin(categorias_seleccionadas)) &
    (df['payment_method'].isin(pagos_seleccionados))
]

# Mensaje de advertencia si los filtros dejan la tabla vacía
if df_filtered.empty:
    st.warning("⚠️ No hay registros que coincidan con la combinación de filtros seleccionada. Intenta seleccionar más opciones.")
    st.stop()


# 3. TARJETAS DE MÉTRICAS PRINCIPALES (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_ventas = df_filtered['revenue'].sum()
    st.metric(
        label="💰 Ventas Totales", 
        value=f"${total_ventas:,.2f}"
    )

with col2:
    total_ganancias = df_filtered['profit'].sum()
    # Cambiar color si las ganancias son negativas (pérdidas) o positivas
    delta_val = "Ganancia neta" if total_ganancias >= 0 else "Pérdida neta"
    st.metric(
        label="📈 Ganancia Total", 
        value=f"${total_ganancias:,.2f}",
        delta=delta_val,
        delta_color="normal" if total_ganancias >= 0 else "inverse"
    )

with col3:
    total_ordenes = len(df_filtered)
    st.metric(
        label="📦 Órdenes Realizadas", 
        value=f"{total_ordenes:,}"
    )

with col4:
    total_unidades = int(df_filtered['quantity'].sum())
    st.metric(
        label="🛒 Unidades Vendidas", 
        value=f"{total_unidades:,}"
    )

st.markdown("---")


# 4. GRÁFICOS INTERACTIVOS (Distribución en dos columnas)
col_g1, col_g2 = st.columns(2)

# Gráfico Izquierdo: Ventas por Categoría (Donut Chart)
with col_g1:
    st.subheader("🛍️ Distribución de Ventas por Categoría")
    df_cat = df_filtered.groupby('category')['revenue'].sum().reset_index()
    fig_donut = px.pie(
        df_cat, 
        values='revenue', 
        names='category', 
        hole=0.4, # Hace que sea un gráfico de dona
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="seaborn"
    )
    # Mejorar el diseño del gráfico
    fig_donut.update_layout(margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig_donut, use_container_width=True)

# Gráfico Derecho: Top 10 Productos Más Vendidos
with col_g2:
    st.subheader("🏆 Top 10 Productos más Vendidos")
    df_prod = (
        df_filtered.groupby('product_name')['revenue']
        .sum()
        .reset_index()
        .sort_values(by='revenue', ascending=True) # Ascendente para que la barra más larga quede arriba en horizontal
        .tail(10)
    )
    fig_bar = px.bar(
        df_prod, 
        x='revenue', 
        y='product_name', 
        orientation='h', # Barra horizontal
        labels={'revenue': 'Ingresos ($)', 'product_name': 'Producto'},
        color='revenue',
        color_continuous_scale=px.colors.sequential.Viridis,
        template="seaborn"
    )
    fig_bar.update_layout(margin=dict(t=20, b=20, l=10, r=10), showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")


# 5. GRÁFICO DE DISPERSIÓN (Análisis de rentabilidad)
st.subheader("🔍 Análisis de Rentabilidad: Ventas vs. Ganancias por País")
fig_scatter = px.scatter(
    df_filtered,
    x='revenue',
    y='profit',
    color='country',
    size='quantity', # El tamaño del punto depende de la cantidad de unidades vendidas
    hover_name='product_name',
    labels={'revenue': 'Ingreso de la Orden ($)', 'profit': 'Ganancia de la Orden ($)', 'country': 'País'},
    color_discrete_map={'MX': '#1f77b4', 'CO': '#ff7f0e', 'PE': '#2ca02c'}, # Colores personalizados por país
    title="Cada círculo representa una orden (Tamaño = Unidades vendidas)",
    template="seaborn"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")


# 6. TABLA DE DATOS DETALLADA (Al fondo)
st.subheader("📋 Vista Previa de Transacciones Filtradas")
st.markdown("Mostrando las primeras 100 transacciones según los filtros seleccionados arriba.")

# Columnas seleccionadas para mostrar en la tabla (para que no sea gigantesca con 32 columnas)
columnas_vista = [
    'order_date', 'country', 'city', 'product_name', 'category', 
    'quantity', 'revenue', 'profit', 'payment_method', 'order_status'
]
st.dataframe(df_filtered[columnas_vista].head(100), use_container_width=True)
