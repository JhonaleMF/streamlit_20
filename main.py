
import streamlit as st
import functions as ft


## Basic setup and app layout
ft.config_page()

menu = st.sidebar.selectbox("Elige una sección",("Panorámica",  "Carga tus datos","Analiza las ventas"))

if menu == "Panorámica": 

    ft.home()

elif menu == "Carga tus datos": 

    dataset = ft.carga_datos()

elif menu == "Analiza las ventas":

    menu_ventas = st.sidebar.radio("Escoge lo que te interese",options=["Ventas por categoría", "Por subcategoría", "Por estado"])

    if menu_ventas == "Ventas por categoría":

        st.header("Ventas por categoría")

        table =  ft.ventas_cat_tabla()

        fig1 = ft.ventas_cat_barplot()

        st.plotly_chart(fig1,use_container_width=True)
        
    elif menu_ventas == "Por subcategoría":

        st.header("Ventas por subcategoría de producto")
        
        fig2 = ft.ventas_subcat_fig()

        st.plotly_chart(fig2,use_container_width=True)
        
        ft.ventas_subcat_st()
    
    else:
        ft.ventas_estado()

   
   

