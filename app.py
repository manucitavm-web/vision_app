import os
import streamlit as st
import base64
from openai import OpenAI

# Función para convertir la imagen a base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")


# Configuración de la página
st.set_page_config(
    page_title="Análisis de Imagen",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Análisis de Imágenes")

# Input de API Key (oculta)
ke = st.text_input("Ingresa tu Clave", type="password")

# Validar API key
api_key = ke.strip() if ke else None

# Crear cliente solo si hay API key
client = None
if api_key:
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Error al inicializar OpenAI: {e}")

# Subir imagen
uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    with st.expander("Imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Opción de pregunta adicional
show_details = st.toggle("Pregunta algo específico sobre la imagen", value=False)

additional_details = ""
if show_details:
    additional_details = st.text_area("Añade contexto o pregunta sobre la imagen:")

# Botón de análisis
analyze_button = st.button("Analizar imagen")

# Lógica principal
if analyze_button:

    if not api_key:
        st.warning("Por favor ingresa tu API key.")
    
    elif not uploaded_file:
        st.warning("Por favor sube una imagen.")
    
    else:
        with st.spinner("Analizando imagen..."):

            try:
                # Convertir imagen
                base64_image = encode_image(uploaded_file)

                # Prompt base
                prompt_text = "Describe lo que ves en la imagen en español."

                if additional_details:
                    prompt_text += f"\n\nContexto adicional del usuario:\n{additional_details}"

                # Mensaje para la API
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ]

                # Streaming de respuesta
                full_response = ""
                message_placeholder = st.empty()

                for chunk in client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=1200,
                    stream=True
                ):
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

            except Exception as e:
                import traceback
                st.error(f"Error: {e}")
                st.text(traceback.format_exc())
