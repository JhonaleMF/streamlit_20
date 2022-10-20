import pandas as pd
from PIL import Image
import plotly.express as px
import streamlit as st
import pydeck as pdk


def config_page():

    st.set_page_config(page_title = "SUPERSTORE", page_icon=":chart:", layout="wide")

#@st.cache(suppress_st_warning=True) #Esto es para que no ejecute esta función si no cambian los argumentos de entrada. Asi no nos salen los globos cada cargar_datos por tres.
def home():

    st.title("Grupo SuperStore")
    st.subheader("Introducción")

    img = Image.open("foto oficina.jpg")
    st.image(img,use_column_width="auto")

    st.markdown("""SuperStore es el **grupo lider en el sector de tecnología, suministros y equipamiento de oficina** en Estados Unidos. 
    El grupo nació hace más de 30 años en Detroit (EEUU). \n Fue la primera empresa en desarrollar una plataforma B2B de compra online de materiales para el entorno de trabajo en 1999. Su catálogo incluye productos tecnológicos, suministros y equipamiento de oficina. 
    A fecha de hoy disponen de **más de 60.000 empresas clientes** en EEUU.""")

    with st.expander("Sostenibilidad"):
        st.markdown("""SuperStore garantiza que todos los pasos que da para satisfacer a sus clientes se realizan del modo más sostenible posible.\n 
        * Más de la mitad de los productos son ecológicos,
        * El grupo ha reducido en una tercera parte sus emisiones de CO2 (desde 2010).
        * Asimismo, ha reducido al máximo los embalajes.
        * Optimiza sus rutas de transporte.""")
    

def carga_datos():

    
    uploaded_file = st.sidebar.file_uploader("Carga aquí los datos a analizar", type=['xls'])

    if uploaded_file is not None: 

        global dataset   
        dataset = pd.read_excel("Sample-Superstore.xls", header=3, parse_dates=['Order Date', "Ship Date"])
        dataset["Order Date Month"] = dataset["Order Date"].dt.month
        dataset["Order Date Year"] = dataset["Order Date"].dt.year
        dataset["Ship Date Month"] = dataset["Ship Date"].dt.month
        dataset["Ship Date Year"] = dataset["Ship Date"].dt.year
        
        
    if st.sidebar.button("Ver datos"):
        st.dataframe(dataset)
        st.balloons()
        return dataset  


def ventas_cat_tabla():

    #Tabla de venta por categoría

    dataset_sales = pd.DataFrame(dataset.groupby("Category")["Sales"].sum())
    dataset_sales ["Percentage"] = ((dataset_sales ["Sales"] /dataset_sales ["Sales"].sum())*100).round(2)
    dataset_sales ["Percentage"] = dataset_sales ["Percentage"].astype(str) + " %"  
    dataset_sales ["Sales"] = dataset_sales ["Sales"].astype("int")
    
    st.table(dataset_sales)

    
def ventas_cat_barplot():

    df_ventas_año_cat = dataset.groupby(["Order Date Year","Category"])["Sales"].sum().reset_index()
    #Grafica
    
    fig1 = px.bar(df_ventas_año_cat, 
              x="Order Date Year",
              y = "Sales",
             color='Category',
             template="plotly_white",
             labels={"Order Date Yea":''},
             color_discrete_sequence = px.colors.qualitative.Safe,
             height=500, 
             width=600)

    fig1.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1))

    fig1.update_layout(font=dict(size=9),title_text="Ventas de artículos por categoría y año")

    return fig1
   

def ventas_subcat_fig():

    dataset_subcat = dataset.groupby(["Order Date Year", "Category", "Sub-Category"])["Sales"].sum().reset_index()
    
    year = st.slider('Selecciona un año', 2013, 2016)
    
    if year == 2013:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == 2013]
    elif year == 2014:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == 2014]
    elif year == 2015:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == 2015]
    else:
        data = dataset_subcat[dataset_subcat["Order Date Year"] == 2016]
    
    #Grafica

    fig2 = px.bar(data, 
              x="Sub-Category",
              y = "Sales",
             color='Category',
             template="plotly_white",
             labels={"Order Date Year":'',"Sub-Category":" "},
             color_discrete_sequence = px.colors.qualitative.Safe,
             height=500, 
             width=600)

    fig2.update_layout(
        xaxis = dict(
            tickmode = 'linear',
            tick0 = 0,
            dtick = 1))

    fig2.update_layout(font=dict(size=11),title_text="",)

    return fig2


def ventas_subcat_st():
    dataset_order_date_subcat = dataset.groupby(["Order Date Year", "Sub-Category"])["Sales"].sum().reset_index().pivot(index=["Order Date Year"], columns="Sub-Category", values="Sales").fillna(0)
    col1, col2 = st.columns(2)    
    with col1:  
        sub_category = st.multiselect('Escoge la Sub-Categoría', dataset_order_date_subcat.columns.values, dataset_order_date_subcat.columns.values)
         
    with col2:
        year = st.slider('¿Qué years quieres filtrar', 2013, 2016,(2013, 2016))  
       
    if year[0] != year[1]:
        if sub_category != []:                
            st.write("Ventas Sub-Categoría por año")
            df_sub_categ_mask = dataset_order_date_subcat[sub_category]
            st.line_chart(df_sub_categ_mask.loc[year[0]:year[1],:])
        else: 
            st.write("Seleccione la(s) categoria(s) a filtrar")
    else:
        st.write("Seleccione un rango de años a filtrar")

def ventas_estado():
    df_cities = pd.read_csv("statelatlong.csv")
    df_map = dataset.groupby(["State", "Order Date Year"])[["Sales"]].sum().reset_index().merge(df_cities, left_on="State", right_on="City").drop(columns=["State_y", "City"]).rename(columns={"State_x":"State"})

    years =[2013, 2014, 2015, 2016]
    sell_year = st.selectbox('Escoge el año a filtrar', years)
      
    view = pdk.ViewState(latitude=37, longitude=-95, zoom=3,)
    
    tooltip = {
        "html":
            "<b>Estado:</b> {State} <br/>"
            "<b>Ventas:</b> {Sales} <br/>",
        "style": {
            "backgroundColor": "steelblue",
            "color": "black",
        }
    }
    salesLayer = pdk.Layer(
            type= "ScatterplotLayer",
            data=df_map,
            pickable=True,
            opacity=0.3,
            filled=True,
            onClick=True,
            radius_scale=10,
            radius_min_pixels=0,
            radius_max_pixels=30,
            line_width_min_pixels=1,
            get_position=["Longitude", "Latitude"],
            get_radius="Sales",
            get_fill_color=[252, 136, 3],
            get_line_color=[255,0,0],
        )
    layertext = pdk.Layer(
        type="TextLayer",
        data=df_map,
        pickable=True,
        get_position=["Longitude", "Latitude"],
        get_text="Sales",
        get_color=[0, 0, 0],
    )

    r = pdk.Deck(
        layers=[salesLayer, layertext,],
        initial_view_state=view,
        map_style="mapbox://styles/mapbox/light-v10",
        tooltip=tooltip,
    )
    map = st.pydeck_chart(r)
    salesLayer.data = df_map[df_map['Order Date Year'] == sell_year]
    layertext.data = df_map[df_map['Order Date Year'] == sell_year]
  
    r.update()
    map.pydeck_chart(r)
 








