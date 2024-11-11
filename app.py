import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import openpyxl
import googlemaps
from streamlit_folium import st_folium
import streamlit_authenticator as stauth

# Configuración de autenticación
nombres = ["Admin", "Usuario1", "Usuario2"]
nombres_usuarios = ["admin", "usuario1", "usuario2"]
contraseñas = ["MilAdmin", "pass1", "pass2"]

authenticator = stauth.Authenticate(
    nombres,
    nombres_usuarios,
    contraseñas,
    "nombre_cookie",
    "clave_cookie",
    cookie_expiry_days=30
)

nombre, autenticado, nombre_usuario = authenticator.login("Iniciar sesión", "main")

if not autenticado:
    st.error("Usuario o contraseña incorrectos. Intenta de nuevo.")
    st.stop()

st.success(f"Bienvenido, {nombre}!")

# API de Google Maps
API_KEY = "AIzaSyA6Pn2WtV-5L9wZs-yEFEL0De9SY-H25Rs"
gmaps = googlemaps.Client(key=API_KEY)

# Colores para rutas
colores_disponibles = [
    'red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
    'darkblue', 'darkgreen', 'cadetblue', 'pink', 'gray', 'black', 'lightblue'
]
colores_rutas = {}

def asignar_color_fijo(ruta):
    if ruta not in colores_rutas:
        color = colores_disponibles[len(colores_rutas) % len(colores_disponibles)]
        colores_rutas[ruta] = color
    return colores_rutas[ruta]

def procesar_archivo(archivo):
    df = pd.read_excel(archivo)
    df["UBICACIÓN"] = ""
    df["ESTATUS"] = ""
    df["COLONIA"] = ""
    df["MUNICIPIO"] = ""
    df["CP"] = ""

    for i, row in df.iterrows():
        try:
            referencia = row["REFERENCIA"]
            estado = row["ESTADO"]
            municipio_inferido = row["RUTA"]

            if pd.isna(referencia):
                continue

            query = f"{referencia}, {municipio_inferido}, {estado}"
            geocode_result = gmaps.geocode(query)

            if not geocode_result:
                query = f"{referencia}, {estado}"
                geocode_result = gmaps.geocode(query)

            if geocode_result:
                location = geocode_result[0]["geometry"]["location"]
                lat, lng = location["lat"], location["lng"]
                df.at[i, "UBICACIÓN"] = f"{lat}, {lng}"
                df.at[i, "ESTATUS"] = "Correcto"

                for componente in geocode_result[0]["address_components"]:
                    if "sublocality" in componente["types"]:
                        df.at[i, "COLONIA"] = componente["long_name"]
                    elif "locality" in componente["types"]:
                        df.at[i, "MUNICIPIO"] = componente["long_name"]
                    elif "postal_code" in componente["types"]:
                        df.at[i, "CP"] = componente["long_name"]
            else:
                df.at[i, "ESTATUS"] = "No encontrado"
        except Exception as e:
            st.error(f"Error al procesar dirección: {e}")
            df.at[i, "ESTATUS"] = "Error"

    return df

def mostrar_mapa(df):
    mapa = folium.Map(location=[20.6597, -103.3496], zoom_start=12)
    mapa.add_child(folium.LatLngPopup())

    for i, row in df.iterrows():
        try:
            ubicacion = row["UBICACIÓN"]
            if pd.isna(ubicacion) or ubicacion == "":
                continue

            lat, lng = map(float, ubicacion.split(", "))
            referencia = row["REFERENCIA"]
            parada = row["PARADA"]
            ruta = row["RUTA"]
            color = asignar_color_fijo(ruta)

            folium.Marker(
                location=[lat, lng],
                popup=f"Ruta: {ruta}<br>Parada: {parada}<br>Referencia: {referencia}",
                icon=folium.Icon(color=color),
            ).add_to(mapa)
        except Exception as e:
            st.error(f"Error al añadir punto al mapa: {e}")

    return mapa

# Aplicación Streamlit
st.title("Herramienta de Procesamiento de Rutas")
archivo = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if archivo:
    df = procesar_archivo(archivo)
    st.success("Archivo procesado exitosamente")

    # Vista editable de la tabla
    df_editado = st.data_editor(df, height=600)

    # Mostrar mapa
    st.header("Mapa de Rutas")
    mapa = mostrar_mapa(df_editado)
    st_folium(mapa, width=700)

    # Botón para actualizar el mapa
    if st.button("Actualizar Mapa"):
        df_actualizado = procesar_archivo(archivo)
        mapa_actualizado = mostrar_mapa(df_actualizado)
        st_folium(mapa_actualizado, width=700)
        st.success("Mapa actualizado")

    # Botón para descargar archivo final
    if st.button("Descargar Archivo Final"):
        df_editado.to_excel("processed/archivo_final.xlsx", index=False)
        with open("processed/archivo_final.xlsx", "rb") as file:
            st.download_button(
                label="Descargar Archivo",
                data=file,
                file_name="archivo_final.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
