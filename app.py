import streamlit as st
import pandas as pd
from gtts import gTTS
from io import BytesIO
import random
from collections import defaultdict

# Título de la aplicación
st.title("Torneo de Savate con Narración")

# Texto de bienvenida personalizado
introduccion = (
    "Bienvenidos al Campeonato Nacional Federado de Savate y Escalafón Nacional "
    "Poussins, Benjamins, Junior y Senior Individual. "
    "A continuación, presentamos los enfrentamientos del torneo."
)
st.write(introduccion)

# Sección para subir el archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel con participantes", type=["xlsx"])

if uploaded_file:
    # Leemos el Excel
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error al leer el Excel: {e}")
        st.stop()

    # Verificamos si tiene las columnas mínimas
    columnas_obligatorias = {"Nombre", "Edad", "Peso", "Categoria"}
    if not columnas_obligatorias.issubset(set(df.columns)):
        st.error("El archivo Excel debe contener al menos las columnas: Nombre, Edad, Peso y Categoria.")
        st.stop()

    # Mostramos la tabla para chequear datos
    st.subheader("Datos de participantes cargados:")
    st.write(df)

    # Ordenar o mezclar aleatoriamente
    # (para cada categoría, mezclamos a los participantes)
    narracion_texto = introduccion + "\n\n"
    peleas_por_categoria = defaultdict(list)

    # Agrupar por categoria
    for categoria, grupo in df.groupby('Categoria'):
        # Mezclar participantes
        grupo_mezclado = grupo.sample(frac=1).reset_index(drop=True)
        nombres = grupo_mezclado['Nombre'].tolist()
        pesos = grupo_mezclado['Peso'].tolist()

        # Generar texto inicial por categoría
        texto_categoria = f"\nEn la categoría {categoria}, con un total de {len(nombres)} participantes:\n"
        narracion_texto += texto_categoria
        st.markdown(f"### {texto_categoria}")

        # Emparejar de a dos
        for i in range(0, len(nombres), 2):
            if i + 1 < len(nombres):
                p1 = nombres[i]
                p2 = nombres[i+1]
                peso_promedio = round((pesos[i] + pesos[i+1]) / 2)
                pelea_text = (
                    f"{p1} contra {p2} "
                    f"en la división de aproximadamente {peso_promedio} kilogramos."
                )
            else:
                pelea_text = (
                    f"{nombres[i]} pasa automáticamente "
                    f"a la siguiente ronda (número impar de participantes)."
                )

            peleas_por_categoria[categoria].append(pelea_text)
            narracion_texto += "- " + pelea_text + "\n"

            # Mostrar pelea en la web
            st.write("• " + pelea_text)

    # Al final, mostrar todo el texto de narración
    st.subheader("Narración generada:")
    st.write(narracion_texto)

    # Generar y reproducir el audio
    if st.button("Generar narración de audio"):
        with st.spinner("Generando narración, por favor espera..."):
            tts = gTTS(narracion_texto, lang='es')
            mp3_bytes = BytesIO()
            tts.write_to_fp(mp3_bytes)
            mp3_bytes.seek(0)

            st.success("¡Narración generada con éxito!")
            # Reproducir audio en la app
            st.audio(mp3_bytes, format='audio/mp3')

            # Opción para descargar
            st.download_button(
                label="Descargar audio (MP3)",
                data=mp3_bytes,
                file_name="narracion_torneo_savate.mp3",
                mime="audio/mp3"
            )
